# using EGL to render, circumventing library installs
import os

os.environ["PYOPENGL_PLATFORM"] = "egl"

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from scipy.spatial.transform import Rotation as R

from wai.scripts.model_wrapper.rendering import (
    prepare_mesh_rendering,
    prepare_scene_rendering,
    render_mesh,
    render_scene,
)
from wai.conversion import cv2gl, gl2cv
from wai.io import _load_generic_mesh

# needed to load big texture files
Image.MAX_IMAGE_PIXELS = None


def main():
    # test rendering of one frame from eyeful apartment scene
    # NOTE: does not take distortion into account

    eyeful_mesh_path = "/fsx/andreasimonelli/test_mesh/obj_mesh/mesh.obj"
    original_image_to_render_path = (
        "/datasets/eyeful_tower_dataset_all/apartment/images-jpeg-4k/10/10_DSC0001.jpg"
    )
    out_image_path = "generic_mesh_render_eyeful.png"

    # transform for eyeful data (taken from eyeful conversion)
    mesh_transform = np.eye(4)
    mesh_transform[:3, :3] = (
        R.from_euler("y", -90, degrees=True).as_matrix()
        @ R.from_euler("x", -90, degrees=True).as_matrix()
    )
    mesh_transform = mesh_transform.astype(np.float32)

    # original camera data
    eyeful_T = np.array(
        [
            [0.5688526034355164, -0.16582050919532776, -0.8055496215820312, 0.0],
            [-0.007935762405395508, -0.9805248379707336, 0.196234792470932, 0.0],
            [-0.8224011659622192, -0.10523602366447449, -0.5590900182723999, 0.0],
            [2.5946707725524902, 0.9920039772987366, 2.6400671005249023, 1.0],
        ]
    )
    T = eyeful_T.T  # Data stored as column-major
    T = np.linalg.inv(T)
    T = T[[2, 0, 1, 3], :]
    T[:, 1:3] *= -1
    c2w, _ = gl2cv(T, return_cmat=True)
    c2w = mesh_transform @ c2w
    c2w_gl = cv2gl(c2w)
    c2w_gl = c2w_gl.astype(np.float32)

    # define camera (resized)
    x_scale = y_scale = 0.2
    eyeful_K = np.array(
        [
            [2960.5102118128075, 0.0, 0.0],
            [0.0, 2960.5102118128075, 0.0],
            [2874.4394903402335, 4314.472094388692, 1.0],
        ],
        dtype=np.float32,
    )
    K = eyeful_K.T  # Data stored as column-major
    camera_data = {}
    camera_data["w"] = int(5784 * x_scale)
    camera_data["h"] = int(8660 * y_scale)
    camera_data["fl_x"] = K[0][0] * x_scale
    camera_data["fl_y"] = K[1][1] * y_scale
    camera_data["cx"] = K[0][2] * x_scale
    camera_data["cy"] = K[1][2] * y_scale

    # load mesh data
    trimesh_data = _load_generic_mesh(eyeful_mesh_path)

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
    ax1.set_title("Original Eyeful Image (distorted)")
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
