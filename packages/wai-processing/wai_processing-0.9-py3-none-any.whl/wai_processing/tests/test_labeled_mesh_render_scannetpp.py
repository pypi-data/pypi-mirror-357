import matplotlib.pyplot as plt
import numpy as np
import torch
from PIL import Image

from wai.scripts.model_wrapper.rendering import prepare_mesh_rendering, render_mesh
from wai.scripts.run_semantic_mapping import semantics_mapping
from wai.conversion import cv2gl
from wai.io import _load_labeled_mesh
from wai.semantics import (
    apply_id_to_color_mapping,
    INVALID_ID,
    load_semantic_color_mapping,
)


def main():
    # test rendering of one frame from the "00a231a370" ScanNet++ scene
    # NOTE: does not take distortion into account

    scannetpp_labeled_mesh_path = (
        "/fsx/andreasimonelli/scannetppv2_dryrun_new/00a231a370/labeled_mesh.ply"
    )
    original_image_to_render_path = (
        "/fsx/andreasimonelli/scannetppv2_dryrun_new/00a231a370/images/DSC05031.jpg"
    )
    out_image_path = "labeled_mesh_render_scannetpp.png"

    # get mapping from semantic id to color
    semantic_color_mapping = load_semantic_color_mapping()

    # converted camera data
    wai_transform_matrix = np.array(
        [
            [
                -0.8902372717857361,
                0.008976904675364494,
                -0.45540860295295715,
                2.712139844894409,
            ],
            [
                -0.45454972982406616,
                0.04694059491157532,
                0.889483630657196,
                1.0517752170562744,
            ],
            [
                0.029361959546804428,
                0.998857319355011,
                -0.03770781680941582,
                -1.7684694528579712,
            ],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=np.float32,
    )
    c2w_gl = cv2gl(wai_transform_matrix)
    c2w_gl = c2w_gl.astype(np.float32)

    # define camera (from WAI conversion)
    camera_data = {}
    camera_data["w"] = 1752
    camera_data["h"] = 1168
    camera_data["fl_x"] = 465.9176025390625
    camera_data["fl_y"] = 468.0899658203125
    camera_data["cx"] = 876.0
    camera_data["cy"] = 584.0

    # nvdiffrast rendering
    invalid_face_id = -1
    labeled_mesh_data = _load_labeled_mesh(scannetpp_labeled_mesh_path, fmt="torch")
    scene_rendering_data = prepare_mesh_rendering(labeled_mesh_data, camera_data)
    nvdiffrast_color, nvdiffrast_depth, nvdiffrast_face_ids = render_mesh(
        scene_rendering_data, c2w_gl, invalid_face_id
    )

    # map from vertex id to semantic id
    nvdiffrast_face_ids = torch.from_numpy(nvdiffrast_face_ids).view(-1)
    labeled_mesh_faces = labeled_mesh_data["faces"]
    frame_vertices_id = labeled_mesh_faces[nvdiffrast_face_ids]  # [h*w, 3]

    semantics_mapping_modality = "majority_voting"
    frame_semantic_class_id, frame_instance_id = semantics_mapping(
        semantics_mapping_modality,
        frame_vertices_id.numpy(),
        labeled_mesh_data["vertices_semantic_class_id"].numpy(),
        labeled_mesh_data["vertices_instance_id"].numpy(),
    )
    # assign invalid semantic id to empty pixels
    empty_rendered_frame_faces = nvdiffrast_face_ids == invalid_face_id  # [h*w, 3]
    frame_semantic_class_id[empty_rendered_frame_faces] = INVALID_ID
    frame_instance_id[empty_rendered_frame_faces] = INVALID_ID

    # map semantics
    frame_semantic_class_id = frame_semantic_class_id.reshape(
        camera_data["h"], camera_data["w"]
    )
    frame_instance_id = frame_instance_id.reshape(camera_data["h"], camera_data["w"])
    frame_semantic_class_id_image, _ = apply_id_to_color_mapping(
        frame_semantic_class_id, semantic_color_mapping
    )
    frame_instance_id_image, _ = apply_id_to_color_mapping(
        frame_instance_id, semantic_color_mapping
    )

    # postprocess nvdiffrast rendering
    nvdiffrast_color = (nvdiffrast_color * 255).astype(np.uint8)
    nvdiffrast_depth = np.stack([nvdiffrast_depth] * 3, axis=-1) * 255 / 10.0  # for vis
    nvdiffrast_depth = nvdiffrast_depth.astype(np.uint8)

    # create combined image
    original_image = Image.open(original_image_to_render_path).resize(
        (camera_data["w"], camera_data["h"])
    )
    nvdiffrast_combo = np.concatenate([nvdiffrast_color, nvdiffrast_depth], axis=1)
    pyrender_combo = np.concatenate(
        [frame_semantic_class_id_image, frame_instance_id_image], axis=1
    )

    # save with matplot
    fig = plt.figure(figsize=(24, 8))
    ax1 = fig.add_subplot(131)
    ax1.imshow(original_image)
    ax1.set_title("Converted ScanNet++ Image")
    ax1.axis("off")
    ax2 = fig.add_subplot(132)
    ax2.imshow(nvdiffrast_combo)
    ax2.set_title("Rendered Color (left) and Depth (right)")
    ax2.axis("off")
    ax3 = fig.add_subplot(133)
    ax3.imshow(pyrender_combo)
    ax3.set_title("Rendered Semantic Class (left) and Instance (right)")
    ax3.axis("off")
    plt.tight_layout()
    plt.savefig(out_image_path)


if __name__ == "__main__":
    main()
