import logging
import shutil
import traceback
from pathlib import Path

import numpy as np
import torch
from argconf import argconf_parse
from tqdm import tqdm
from wai import (
    get_frame,
    get_scene_frame_names,
    load_data,
    load_frame,
    set_frame,
    store_data,
)
from wai.camera import CAMERA_KEYS, cv2gl
from wai.io import set_processing_state
from wai_processing import WAI_PROC_CONFIG_PATH

from .model_wrapper.rendering import (
    prepare_mesh_rendering,
    prepare_scene_rendering,
    render_mesh,
    render_scene,
)

## Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def rendering(cfg, scene_name, overwrite=False):
    scene_root = Path(cfg.root, scene_name)
    scene_meta = load_data(Path(scene_root, "scene_meta.json"), "scene_meta")
    camera_data = {k: v for k, v in scene_meta.items() if k in CAMERA_KEYS}
    mesh_to_render_name, mesh_to_render_ext = cfg.mesh_to_render.split(".")

    # sanity checks
    if scene_meta["camera_model"] != "PINHOLE":
        raise ValueError(
            "Mesh rendering only supports pinhole camera models, run undistortion first!"
        )
    if not scene_meta["shared_intrinsics"]:
        raise NotImplementedError("We only support a single camera model per scene atm")
    if not torch.cuda.is_available() and cfg.rendering_type == "labeled_mesh":
        raise ValueError("Labeled mesh rendering is only supported on GPU.")
    if mesh_to_render_name not in scene_meta["scene_modalities"]:
        raise ValueError(
            f"Mesh {mesh_to_render_name} is not available in scene_modalities."
        )
    if (
        cfg.rendering_type == "scene"
        and "rendered_face_ids" in cfg.frame_modalities_to_render
    ):
        raise ValueError("Rendering face ids is not supported in scene rendering.")
    if any(
        fmr not in cfg.supported_frame_modalities_to_render
        for fmr in cfg.frame_modalities_to_render
    ):
        raise ValueError(
            f"Found unsupported frame modalities to render. Allowed modalities are: {cfg.supported_frame_modalities_to_render}"
        )
    if mesh_to_render_ext not in cfg.supported_mesh_formats:
        raise ValueError(
            f"Unsupported mesh format .{mesh_to_render_ext}. Supported formats are: {cfg.supported_mesh_formats}"
        )

    # create output directories
    for fmr in cfg.frame_modalities_to_render:
        fmr_dir_path = Path(scene_root, f"rendered_{fmr}")
        if Path(fmr_dir_path).exists():
            if overwrite:
                shutil.rmtree(fmr_dir_path)
            else:
                raise FileExistsError(f"Path already exists: {fmr_dir_path} ")

    # load mesh data
    mesh_path = Path(
        scene_root, scene_meta["scene_modalities"][mesh_to_render_name]["scene_key"]
    )
    if cfg.rendering_type == "labeled_mesh":
        mesh_data = load_data(mesh_path, format="labeled_mesh", fmt="torch")
    elif cfg.rendering_type in ["mesh", "scene"]:
        # generic mesh loader
        mesh_data = load_data(mesh_path, format="mesh")
    else:
        raise ValueError(f"Unsupported rendering type: {cfg.rendering_type}")

    # prepare rendering
    if cfg.rendering_type in ["mesh", "labeled_mesh"]:
        scene_rendering_data = prepare_mesh_rendering(mesh_data, camera_data)
    elif cfg.rendering_type == "scene":
        scene_rendering_data = prepare_scene_rendering(mesh_data, camera_data)

    # render scene frames
    for frame_name in tqdm(scene_frame_names[scene_name]):
        sample = load_frame(scene_root, frame_name)
        c2w = sample["extrinsics"].numpy()
        if cfg.get("mesh_transform") is not None:
            # apply the inverse of the mesh_transform to extrinsics
            c2w = np.linalg.inv(cfg.mesh_transform) @ c2w
        # gl convention needed for rendering (nvdiffrast and pyrender)
        c2w_gl = cv2gl(c2w)

        # render
        if cfg.rendering_type in ["mesh", "labeled_mesh"]:
            color, depth, face_id = render_mesh(
                scene_rendering_data,
                c2w_gl,
                cfg.invalid_face_id,
                cfg.near,
                cfg.far,
            )
        elif cfg.rendering_type == "scene":
            color, depth = render_scene(scene_rendering_data, c2w_gl)

        # --- update frame scene_meta ---
        frame = get_frame(scene_meta, frame_name)

        # rendered depth
        if "rendered_depth" in cfg.frame_modalities_to_render:
            rel_depth_frame_path = f"{'rendered_depth'}/{frame_name}.exr"
            store_data(
                scene_root / rel_depth_frame_path,
                depth,
                "depth",
            )
            frame["rendered_depth"] = rel_depth_frame_path

        # rendered image
        if "rendered_image" in cfg.frame_modalities_to_render:
            rel_color_frame_path = f"{'rendered_image'}/{frame_name}.png"
            store_data(
                scene_root / rel_color_frame_path,
                color,
                "image",
            )
            frame["rendered_image"] = rel_color_frame_path

        # rendered mesh faces
        if "rendered_mesh_faces" in cfg.frame_modalities_to_render:
            rel_mesh_faces_frame_path = f"{'rendered_mesh_faces'}/{frame_name}.npz"
            store_data(
                scene_root / rel_mesh_faces_frame_path,
                face_id,
                "numpy",
            )
            frame["rendered_mesh_faces"] = rel_mesh_faces_frame_path

        # update frame data in scene_meta
        set_frame(scene_meta, frame_name, frame, sort=True)

    # --- update frame_modalities ---
    frame_modalities = scene_meta["frame_modalities"]
    if "rendered_depth" in cfg.frame_modalities_to_render:
        frame_modalities["rendered_depth"] = {
            "frame_key": "rendered_depth",
            "format": "depth",
        }
    if "rendered_image" in cfg.frame_modalities_to_render:
        frame_modalities["rendered_image"] = {
            "frame_key": "rendered_image",
            "format": "image",
        }
    if "rendered_mesh_faces" in cfg.frame_modalities_to_render:
        frame_modalities["rendered_mesh_faces"] = {
            "frame_key": "rendered_mesh_faces",
            "format": "numpy",
        }

    scene_meta["frame_modalities"] = frame_modalities

    # store new scene_meta
    store_data(Path(cfg.root, scene_name, "scene_meta.json"), scene_meta, "scene_meta")


if __name__ == "__main__":
    cfg = argconf_parse(str(Path(WAI_PROC_CONFIG_PATH, "rendering.yaml")))
    if cfg.get("root") is None:
        logger.info(
            "Specify the root via: 'python scripts/run_rendering.py root=<root_path>'"
        )

    overwrite = cfg.get("overwrite", False)
    if overwrite:
        logger.warning("Careful: Overwrite enabled")

    scene_frame_names = get_scene_frame_names(cfg)

    for scene_name in tqdm(scene_frame_names):
        logger.info(f"Processing: {scene_name}")
        scene_root = Path(cfg.root, scene_name)
        set_processing_state(scene_root, "rendering", "running")
        try:
            rendering(cfg, scene_name, overwrite=overwrite)
        except Exception:
            logger.error(f"Rendering failed on scene: {scene_name}")
            trace_message = traceback.format_exc()
            logger.error(trace_message)
            set_processing_state(
                scene_root, "rendering", "failed", message=trace_message
            )
            continue

        set_processing_state(scene_root, "rendering", "finished")
