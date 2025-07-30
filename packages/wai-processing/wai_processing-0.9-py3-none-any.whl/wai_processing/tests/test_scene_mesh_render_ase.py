# using EGL to render, circumventing library installs
import os

os.environ["PYOPENGL_PLATFORM"] = "egl"

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pyvrs
from PIL import Image
from projectaria_tools.core import calibration
from projectaria_tools.core.calibration import device_calibration_from_json_string
from scipy.spatial.transform import Rotation as R
from wai.conversion import cv2gl, gl2cv
from wai.io import _load_generic_mesh

from wai.scripts.conversion.ase import (
    read_trajectory_file,
    RGB_IMAGE_SIZE,
    rot90,
    rotate_pinhole_90degcw,
)
from wai.scripts.model_wrapper.rendering import prepare_scene_rendering, render_scene


def main():
    # test scene rendering on one frame from ase 10000 scene
    # NOTE: does not take distortion into account

    sensor_name = "camera-rgb"
    ase_vrs_path = "/datasets/AriaSyntheticDataset/10000/out.vrs"
    ase_mesh_path = "/fsx/andreasimonelli/test_mesh/glb_mesh/scene.glb"
    original_image_to_render_path = (
        "/datasets/AriaSyntheticDataset/10000/render/images/0/rgb0000000.jpg"
    )
    out_image_path = "scene_render_ase.png"

    # Load sensor calibrations
    reader = pyvrs.SyncVRSReader(ase_vrs_path)
    sensors_calib = device_calibration_from_json_string(reader.file_tags["calib_json"])

    # Load device extrinsics
    trajectory_file = Path("/datasets/AriaSyntheticDataset/10000/gt_trajectory_mps.csv")
    trajectory = read_trajectory_file(trajectory_file)

    # Relative pose of the sensor w.r.t. the Aria device coordinate system
    cam_calib = sensors_calib.get_camera_calib(sensor_name)
    T_device_from_camera = cam_calib.get_transform_device_camera().to_matrix()
    T_device_from_camera[:3, :3] = T_device_from_camera[:3, :3] @ rot90

    # transform for ase mesh
    mesh_transform = np.eye(4)
    mesh_transform[:3, :3] = (
        R.from_euler("y", -90, degrees=True).as_matrix()
        @ R.from_euler("x", -90, degrees=True).as_matrix()
    )
    mesh_transform = mesh_transform.astype(np.float32)

    # get c2w in opencv and opengl format (for rendering)
    w2c = np.array(trajectory["Ts_world_from_device"][0] @ T_device_from_camera)
    c2w = np.linalg.inv(w2c)
    c2w = c2w[[2, 0, 1, 3], :]
    c2w[:, 1:3] *= -1
    c2w, _ = gl2cv(c2w, return_cmat=True)
    rot90_add = np.eye(4)
    rot90_add[:3, :3] = R.from_euler("y", -90, degrees=True).as_matrix()
    c2w = mesh_transform @ c2w @ rot90_add
    c2w_gl = cv2gl(c2w)
    c2w_gl = c2w_gl.astype(np.float32)

    # define camera (resized)
    image_size = (
        (RGB_IMAGE_SIZE, RGB_IMAGE_SIZE)
        if sensor_name == "camera-rgb"
        else cam_calib.get_image_size().tolist()
    )

    # get intrinsics
    pinhole = calibration.get_linear_camera_calibration(
        image_width=image_size[0],
        image_height=image_size[1],
        focal_length=cam_calib.get_focal_lengths()[0],
    )
    fx, fy = pinhole.get_focal_lengths().tolist()
    cx, cy = pinhole.get_principal_point().tolist()
    W, H = pinhole.get_image_size().tolist()
    W, H, fx, fy, cx, cy = rotate_pinhole_90degcw(W, H, fx, fy, cx, cy)
    camera_data = {}
    camera_data["w"] = int(W)
    camera_data["h"] = int(H)
    camera_data["fl_x"] = fx
    camera_data["fl_y"] = fy
    camera_data["cx"] = cx
    camera_data["cy"] = cy

    # scene rendering
    ase_mesh = _load_generic_mesh(ase_mesh_path)

    rendering_data = prepare_scene_rendering(ase_mesh, camera_data)
    pyrender_color, pyrender_depth = render_scene(rendering_data, c2w_gl)

    # postprocess pyrender rendering
    pyrender_color = (pyrender_color * 255).astype(np.uint8)
    pyrender_depth = np.stack([pyrender_depth] * 3, axis=-1) * 255 / 10.0  # for vis
    pyrender_depth = pyrender_depth.astype(np.uint8)

    # create combined image
    original_image = Image.open(original_image_to_render_path).resize(
        (camera_data["w"], camera_data["h"])
    )
    # original_image = original_image.rotate(-90)
    pyrender_combo = np.concatenate([pyrender_color, pyrender_depth], axis=1)

    # save with matplot
    fig = plt.figure(figsize=(24, 8))
    ax1 = fig.add_subplot(121)
    ax1.imshow(original_image)
    ax1.set_title("Original ASE Image (distorted)")
    ax1.axis("off")
    ax2 = fig.add_subplot(122)
    ax2.imshow(pyrender_combo)
    ax2.set_title("Pyrender Rendered Color (left) and Depth (right)")
    ax2.axis("off")
    plt.tight_layout()
    plt.savefig(out_image_path)


if __name__ == "__main__":
    main()
