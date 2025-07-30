# using EGL to render, circumventing library installs
import os

os.environ["PYOPENGL_PLATFORM"] = "egl"

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from wai.scripts.model_wrapper.rendering import (
    prepare_mesh_rendering,
    prepare_scene_rendering,
    render_mesh,
    render_scene,
)
from wai.conversion import cv2gl, gl2cv
from wai.io import _load_generic_mesh


def main():
    # test rendering of one frame from the "00a231a370" ScanNet++ scene
    # NOTE: does not take distortion into account

    scannetpp_original_mesh_path = (
        "/datasets/scannetpp/data/00a231a370/scans/mesh_aligned_0.05.ply"
    )
    original_image_to_render_path = (
        "/datasets/scannetpp/data/00a231a370/dslr/resized_images/DSC05031.JPG"
    )
    out_image_path = "generic_mesh_render_scannetpp.png"

    # transform to opencv for ScanNet++ data
    mesh_transform = np.array(
        [[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]], dtype=np.float32
    )

    # original camera data
    org_nerfstudio_transform_matrix = np.array(
        [
            [
                -0.8902372870470251,
                -0.008976904219514819,
                0.45540859449705906,
                2.7121398397668854,
            ],
            [
                -0.4545497201853293,
                -0.04694059309916689,
                -0.8894836325638252,
                1.0517752341396065,
            ],
            [
                0.02936195890250176,
                -0.9988573451249848,
                0.037707816951869186,
                -1.7684693983793762,
            ],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=np.float32,
    )
    c2w, _ = gl2cv(org_nerfstudio_transform_matrix, return_cmat=True)
    c2w = np.linalg.inv(mesh_transform) @ c2w
    c2w_gl = cv2gl(c2w)
    c2w_gl = c2w_gl.astype(np.float32)

    # define camera (resized)
    x_scale = y_scale = 1.0
    camera_data = {}
    camera_data["w"] = int(1752 * x_scale)
    camera_data["h"] = int(1168 * y_scale)
    camera_data["fl_x"] = 615.6242422392195 * x_scale
    camera_data["fl_y"] = 618.4946019037377 * y_scale
    camera_data["cx"] = 880.2934171549766 * x_scale
    camera_data["cy"] = 590.0591417837228 * y_scale

    trimesh_data = _load_generic_mesh(scannetpp_original_mesh_path)

    # nvdiffrast rendering
    mesh_rendering_data = prepare_mesh_rendering(trimesh_data, camera_data)
    nvdiffrast_color, nvdiffrast_depth, _ = render_mesh(
        mesh_rendering_data, c2w_gl, invalid_face_id=-1
    )

    # pyrender rendering
    scene_rendering_data = prepare_scene_rendering(trimesh_data, camera_data)
    pyrender_color, pyrender_depth = render_scene(scene_rendering_data, c2w_gl)

    # postprocess nvdiffrast rendering
    nvdiffrast_color = (nvdiffrast_color * 255).astype(np.uint8)
    nvdiffrast_depth = np.stack([nvdiffrast_depth] * 3, axis=-1) * 255 / 10.0  # for vis
    nvdiffrast_depth = nvdiffrast_depth.astype(np.uint8)

    # postprocess pyrender rendering
    pyrender_color = (pyrender_color * 255).astype(np.uint8)
    pyrender_depth = np.stack([pyrender_depth] * 3, axis=-1) * 255 / 10.0  # for vis
    pyrender_depth = pyrender_depth.astype(np.uint8)

    # create combined image
    original_image = Image.open(original_image_to_render_path).resize(
        (camera_data["w"], camera_data["h"])
    )
    nvdiffrast_combo = np.concatenate([nvdiffrast_color, nvdiffrast_depth], axis=1)
    pyrender_combo = np.concatenate([pyrender_color, pyrender_depth], axis=1)

    # save with matplot
    fig = plt.figure(figsize=(24, 8))
    ax1 = fig.add_subplot(131)
    ax1.imshow(original_image)
    ax1.set_title("Original ScanNet++ Image (distorted)")
    ax1.axis("off")
    ax2 = fig.add_subplot(132)
    ax2.imshow(nvdiffrast_combo)
    ax2.set_title("Nvdiffrast Rendered Color (left) and Depth (right)")
    ax2.axis("off")
    ax3 = fig.add_subplot(133)
    ax3.imshow(pyrender_combo)
    ax3.set_title("Pyrender Rendered Color (left) and Depth (right)")
    ax3.axis("off")
    plt.tight_layout()
    plt.savefig(out_image_path)


if __name__ == "__main__":
    main()
