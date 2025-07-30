import logging
import shutil
import traceback
from pathlib import Path

import torch
from argconf import argconf_parse
from tqdm import tqdm
from wai import get_frame, get_scene_frame_names, load_data, set_frame, store_data
from wai.camera import CAMERA_KEYS
from wai.io import set_processing_state
from wai.semantics import INVALID_ID, load_semantic_color_mapping
from wai_processing import WAI_PROC_CONFIG_PATH

## Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def majority_voting(frame_semantics):
    """
    Perform majority voting on semantic labels for each pixel. Requires a GPU.
    Args:
        frame_semantics: Array of shape [num_pixels, k] where k is the number of vertices
                         associated with each pixel
    Returns:
        Array of shape [num_pixels] containing the most common semantic label for each pixel
    """
    pixels_tensor = torch.from_numpy(frame_semantics).cuda()
    # Mask invalid values
    valid_mask = pixels_tensor != INVALID_ID
    pixels_tensor_valid = pixels_tensor.clone()
    pixels_tensor_valid[~valid_mask] = 0
    # Determine the maximum valid label value
    max_val = int(pixels_tensor_valid.max().item())
    # Create a one-hot encoding for each value in the tensor
    one_hot = torch.zeros(
        pixels_tensor_valid.shape[0], max_val + 1, device="cuda", dtype=torch.int32
    )
    # Convert indices to int64 for scatter_add_
    indices = pixels_tensor_valid.long()
    # Use scatter_add_ to count occurrences
    one_hot.scatter_add_(1, indices, valid_mask.int())
    # Get the index of the maximum count for each row
    result = one_hot.argmax(dim=1)
    # If all values for a pixel are invalid, assign INVALID_ID as the result
    all_invalid = (~valid_mask).all(dim=1)
    result[all_invalid] = INVALID_ID
    return result.cpu().numpy().astype(frame_semantics.dtype)


def semantics_mapping(
    semantics_mapping_modality,
    pixels_vertices_list,
    vertices_semantic_class,
    vertices_instance,
):
    """
    Maps semantic information from vertices to pixels using the specified mapping modality.

    Args:
        semantics_mapping_modality: String specifying the mapping method (e.g., "majority_voting")
        pixels_vertices_list: Array of shape [num_pixels, 3] containing the 3 vertex indices for each pixel
        vertices_semantic_class: Array of semantic class labels for each vertex
        vertices_instance: Array of instance IDs for each vertex

    Returns:
        tuple: (pixels_mapped_semantic_class, pixels_mapped_instance)
            - pixels_mapped_semantic_class: Array of semantic class labels for each pixel
            - pixels_mapped_instance: Array of instance IDs for each pixel

    Raises:
        NotImplementedError: If the specified mapping modality is not supported
    """

    pixels_k_semantic_class = vertices_semantic_class[pixels_vertices_list]
    pixels_k_instance = vertices_instance[pixels_vertices_list]

    if semantics_mapping_modality == "majority_voting":
        pixels_mapped_semantic_class = majority_voting(pixels_k_semantic_class)
        pixels_mapped_instance = majority_voting(pixels_k_instance)
    else:
        raise NotImplementedError(
            f"Unsupported semantics mapping modality: {semantics_mapping_modality}"
        )

    return pixels_mapped_semantic_class, pixels_mapped_instance


def map_scene_semantics(cfg, scene_name, semantic_color_mapping, overwrite=False):
    scene_root = Path(cfg.root, scene_name)
    scene_meta = load_data(Path(scene_root, "scene_meta.json"), "scene_meta")
    camera_data = {k: v for k, v in scene_meta.items() if k in CAMERA_KEYS}

    # sanity checks
    if cfg.semantics_mapping_modality not in cfg.supported_semantics_mapping_modalities:
        raise NotImplementedError(
            f"Unsupported semantics mapping modality: {cfg.semantics_mapping_modality}. Supported modalities are: {cfg.supported_semantics_mapping_modalities}."
        )

    # create output directories
    semantic_class_dir_path = Path(scene_root, "rendered_semantic_class")
    instance_dir_path = Path(scene_root, "rendered_instance")
    for path in [
        semantic_class_dir_path,
        instance_dir_path,
    ]:
        if Path(path).exists():
            if overwrite:
                shutil.rmtree(path)
            else:
                raise FileExistsError(f"Path already exists: {path} ")

    rendered_mesh_faces_dir_path = Path(scene_root, "rendered_mesh_faces")

    # load labeled mesh data
    labeled_mesh_path = Path(
        scene_root, scene_meta["scene_modalities"]["labeled_mesh"]["scene_key"]
    )
    labeled_mesh_data = load_data(labeled_mesh_path, "labeled_mesh", fmt="np")
    labeled_mesh_faces = labeled_mesh_data["faces"]
    labeled_mesh_vertices_semantic_class_id = labeled_mesh_data[
        "vertices_semantic_class_id"
    ]
    labeled_mesh_vertices_instance_id = labeled_mesh_data["vertices_instance_id"]

    for frame_name in tqdm(scene_frame_names[scene_name]):
        # get the face id for each pixel of the frame
        frame_face_id_path = Path(rendered_mesh_faces_dir_path) / f"{frame_name}.npz"
        frame_face_id = load_data(frame_face_id_path)
        frame_face_id = frame_face_id.reshape(camera_data["h"] * camera_data["w"])
        # get the 3 vertices that belong to the pixel's face id
        frame_vertices_id = labeled_mesh_faces[frame_face_id]  # [h*w, 3]

        # map from vertex id to semantic id
        frame_semantic_class_id, frame_instance_id = semantics_mapping(
            cfg.semantics_mapping_modality,
            frame_vertices_id,
            labeled_mesh_vertices_semantic_class_id,
            labeled_mesh_vertices_instance_id,
        )
        # assign invalid semantic id to empty pixels
        empty_rendered_frame_faces = frame_face_id == cfg.invalid_face_id  # [h*w, 3]
        frame_semantic_class_id[empty_rendered_frame_faces] = INVALID_ID
        frame_instance_id[empty_rendered_frame_faces] = INVALID_ID

        # save
        frame_semantic_class_id = frame_semantic_class_id.reshape(
            camera_data["h"], camera_data["w"]
        )
        frame_instance_id = frame_instance_id.reshape(
            camera_data["h"], camera_data["w"]
        )

        rel_semantic_class_path = f"rendered_semantic_class/{frame_name}.png"
        rel_instance_path = f"rendered_instance/{frame_name}.png"
        store_data(
            scene_root / rel_semantic_class_path,
            frame_semantic_class_id,
            "labeled_image",
            semantic_color_mapping=semantic_color_mapping,
        )
        store_data(
            scene_root / rel_instance_path,
            frame_instance_id,
            "labeled_image",
            semantic_color_mapping=semantic_color_mapping,
        )

        # --- update frame scene_meta ---
        frame = get_frame(scene_meta, frame_name)
        frame["rendered_semantic_class"] = rel_semantic_class_path
        frame["rendered_instance"] = rel_instance_path
        set_frame(scene_meta, frame_name, frame, sort=True)

    # --- update frame_modalities ---
    frame_modalities = scene_meta["frame_modalities"]
    frame_modalities["rendered_semantic_class"] = {
        "frame_key": "rendered_semantic_class",
        "format": "labeled_image",
    }
    frame_modalities["rendered_instance"] = {
        "frame_key": "rendered_instance",
        "format": "labeled_image",
    }
    scene_meta["frame_modalities"] = frame_modalities

    # store new scene_meta
    store_data(Path(cfg.root, scene_name, "scene_meta.json"), scene_meta, "scene_meta")


if __name__ == "__main__":
    cfg = argconf_parse(str(Path(WAI_PROC_CONFIG_PATH, "semantic_mapping.yaml")))
    if cfg.get("root") is None:
        logger.info(
            "Specify the root via: 'python scripts/semantic_mapping.py root=<root_path>'"
        )

    overwrite = cfg.get("overwrite", False)
    if overwrite:
        logger.warning("Careful: Overwrite enabled")

    scene_frame_names = get_scene_frame_names(cfg)

    # get mapping from semantic id to color
    semantic_color_mapping = load_semantic_color_mapping()

    for scene_name in tqdm(scene_frame_names):
        logger.info(f"Processing: {scene_name}")
        scene_root = Path(cfg.root, scene_name)
        set_processing_state(scene_root, "semantic_mapping", "running")
        try:
            map_scene_semantics(
                cfg, scene_name, semantic_color_mapping, overwrite=overwrite
            )
        except Exception:
            logger.error(f"Mapping face ids to semantics failed on scene: {scene_name}")
            trace_message = traceback.format_exc()
            logger.error(trace_message)
            set_processing_state(
                scene_root, "semantic_mapping", "failed", message=trace_message
            )
            continue

        set_processing_state(scene_root, "semantic_mapping", "finished")
