# Copyright 2022 the Regents of the University of California, Nerfstudio Team and contributors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import collections
import json
import math
import os
from pathlib import Path

import numpy as np
import open3d as o3d
from argconf import argconf_parse
from PIL import Image
from scipy.spatial.transform import Rotation as R
from wai.camera import gl2cv
from wai_processing import (
    convert_scenes_wrapper,
    WAI_PROC_CONFIG_PATH,
)

# Crop radii empirically chosen to try to avoid hitting the rig base or go out of bounds
EYEFULTOWER_FISHEYE_RADII = {
    "office1a": 0.43,
    "office2": 0.45,
    "seating_area": 0.375,  # could be .45 except for camera 2
    "table": 0.45,
    "workshop": 0.45,
}

DEFAULT_FISHEYE_RADIUS = 0.45

ROTATION_PC = np.eye(4)
ROTATION_PC[:3, :3] = (
    R.from_euler("y", -90, degrees=True).as_matrix()
    @ R.from_euler("x", -90, degrees=True).as_matrix()
)


def check_aspect_ratio_match(width, height, target_width, target_height):
    """
    Check if the aspect ratio of the given width and height matches the target aspect
    ratio by using the greatest common divisor to simplify the aspect ratios and thus
    avoid floating point errors.
    Args:
        width (int): The width of the image.
        height (int): The height of the image.
        target_width (int): The target width.
        target_height (int): The target height.
    Returns:
        bool: True if the aspect ratios match, False otherwise.
    """
    # Compute the GCD of the width and height
    gcd = math.gcd(width, height)
    # Simplify the aspect ratio
    simplified_width = width // gcd
    simplified_height = height // gcd
    # Compute the GCD of the target width and height
    target_gcd = math.gcd(target_width, target_height)
    # Simplify the target aspect ratio
    simplified_target_width = target_width // target_gcd
    simplified_target_height = target_height // target_gcd
    # Check if the aspect ratio is the same as the target aspect ratio
    return (simplified_width, simplified_height) == (
        simplified_target_width,
        simplified_target_height,
    )


def find_jpgs(folder_path):
    """
    Find all relative paths to JPG files in a given folder.
    Args:
        folder_path (str): The path to the folder to search for JPG files.
    Returns:
        list: A list of relative paths to JPG files.
    """
    jpg_paths = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".jpg"):
                relative_path = os.path.relpath(os.path.join(root, file), folder_path)
                jpg_paths.append(relative_path)
    return jpg_paths


def load_and_save_point_cloud(
    eyeful_path: str, target_path: str, transform: None | np.ndarray = None
) -> None:
    """
    Load a point cloud from an eyeful path and save it as a PLY file to a target path.

    Args:
        eyeful_path (str): The path to the eyeful data.
        target_path (str): The path where the PLY file will be saved.
    """

    if not all(
        Path(eyeful_path, filename).exists()
        for filename in ("mesh.obj", "mesh.mtl", "mesh.jpg")
    ):
        raise FileNotFoundError(
            f"One or more files are missing in the eyeful path: {eyeful_path}."
            "Expected files: mesh.obj, mesh.mtl, mesh.jpg"
        )
    # Read triangle mesh from OBJ file
    mesh = o3d.io.read_triangle_mesh(str(Path(eyeful_path, "mesh.obj")))

    # Get points and colors from mesh
    points = np.asarray(mesh.vertices)
    colors = np.asarray(mesh.vertex_colors)

    # Apply transformation if provided
    if transform is not None:
        points = np.dot(points, transform[:3, :3]) + transform[:3, 3]

    # Create a point cloud with colors
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.colors = o3d.utility.Vector3dVector(colors)

    # Save point cloud to PLY file
    o3d.io.write_point_cloud(target_path, pcd)


def convert_cameras_to_wai_scene_meta(
    cfg,
    capture_name: str,
    cameras: dict,
    splits: dict,
    target_width: int,
    target_height: int,
    extension: str,
    scene_name: str,
) -> dict:
    """
    Adopted from https://github.com/nerfstudio-project/nerfstudio/blob/73fe54dda0b743616854fc839889d955522e0e68/nerfstudio/scripts/downloads/eyeful_tower.py#L171
    Args:
        capture_name: Which specific EyefulTower capture is being converted
        cameras: Data loaded from EyefulTower cameras.json
        splits: Data loaded from EyefulTower splits.json
        target_width: Width of output images
        target_height: Height of output images
        extension: Extension of output images

    Returns:
        Dict in the Nerfstudio transforms.json format, with scaled camera parameters, splits, and optional metadata.
    """
    scene_meta = {
        "scene_name": scene_name,
        "dataset_name": cfg.dataset_name,
        "version": cfg.version,
        "shared_intrinsics": False,
        "camera_convention": "opencv",
        "scale_type": "metric",
        "scene_modalities": {},
        "frame_modalities": {
            "image_distorted": {
                "frame_key": "image_distorted",
                "format": "image",
            },
        },
    }

    distortion_models = [c["distortionModel"] for c in cameras["KRT"]]
    distortion_model = list(set(distortion_models))
    assert len(distortion_model) == 1
    distortion_model = distortion_model[0]
    if distortion_model == "RadialAndTangential":
        scene_meta["camera_model"] = "OPENCV"
    elif distortion_model == "Fisheye":
        scene_meta["camera_model"] = "OPENCV_FISHEYE"
        if capture_name in EYEFULTOWER_FISHEYE_RADII:
            scene_meta["fisheye_crop_radius"] = EYEFULTOWER_FISHEYE_RADII[capture_name]
        else:
            print(
                f"WARN: Inofficial capture {capture_name} not in EYEFULTOWER_FISHEYE_RADII, using default of {DEFAULT_FISHEYE_RADIUS}"
            )
            scene_meta["fisheye_crop_radius"] = DEFAULT_FISHEYE_RADIUS
    else:
        raise NotImplementedError(f"Camera model {distortion_model} not implemented")
    split_sets = {k: set(v) for k, v in splits.items()}

    frames = []
    split_filenames = collections.defaultdict(list)
    for camera in cameras["KRT"]:
        wai_frame = {}
        wai_frame["file_path"] = str(
            Path(
                "images_distorted",
                camera["cameraId"].replace("/", "_") + f".{extension}",
            )
        )
        wai_frame["image_distorted"] = wai_frame["file_path"]
        wai_frame["frame_name"] = str(Path(wai_frame["file_path"]).stem)
        for split in split_sets:
            if camera["cameraId"] in split_sets[split]:
                split_filenames[split].append(wai_frame["file_path"])

        original_width = camera["width"]
        original_height = camera["height"]
        if original_width > original_height:
            target_width, target_height = (
                max(target_width, target_height),
                min(target_width, target_height),
            )
        else:
            target_height, target_width = (
                max(target_width, target_height),
                min(target_width, target_height),
            )
        x_scale = target_width / original_width
        y_scale = target_height / original_height

        wai_frame["w"] = target_width
        wai_frame["h"] = target_height
        K = np.array(camera["K"]).T  # Data stored as column-major
        wai_frame["fl_x"] = K[0][0] * x_scale
        wai_frame["fl_y"] = K[1][1] * y_scale
        wai_frame["cx"] = K[0][2] * x_scale
        wai_frame["cy"] = K[1][2] * y_scale

        if distortion_model == "RadialAndTangential":
            # pinhole: [k1, k2, p1, p2, k3]
            wai_frame["k1"] = camera["distortion"][0]
            wai_frame["k2"] = camera["distortion"][1]
            wai_frame["k3"] = camera["distortion"][4]
            wai_frame["k4"] = 0.0
            wai_frame["p1"] = camera["distortion"][2]
            wai_frame["p2"] = camera["distortion"][3]
        elif distortion_model == "Fisheye":
            # fisheye: [k1, k2, k3, _, _, _, p1, p2]
            wai_frame["k1"] = camera["distortion"][0]
            wai_frame["k2"] = camera["distortion"][1]
            wai_frame["k3"] = camera["distortion"][2]
            wai_frame["p1"] = camera["distortion"][6]
            wai_frame["p2"] = camera["distortion"][7]
        else:
            raise NotImplementedError("This shouldn't happen")

        T = np.array(camera["T"]).T  # Data stored as column-major
        T = np.linalg.inv(T)
        T = T[[2, 0, 1, 3], :]
        T[:, 1:3] *= -1
        opencv_pose, gl2cv_cmat = gl2cv(T, return_cmat=True)
        wai_frame["transform_matrix"] = opencv_pose.tolist()
        frames.append(wai_frame)

    frames = sorted(frames, key=lambda f: f["file_path"])

    scene_meta["frames"] = frames
    scene_meta["train_filenames"] = split_filenames["train"]
    scene_meta["val_filenames"] = split_filenames["test"]
    scene_meta["test_filenames"] = []
    scene_meta["_applied_transform"] = gl2cv_cmat.tolist()
    scene_meta["_applied_transforms"] = (
        {"opengl2opencv": gl2cv_cmat.tolist()},
    )  # transforms raw poses to opencv poses
    return scene_meta


def convert_eyeful_tower_to_wai(cfg, scene_name: str):
    target_scene_root = Path(cfg.root) / scene_name
    # No addtional output folders needed, softlinking to original
    source_scene_root = Path(cfg.original_root, scene_name)

    # Load cameras.json
    with open(source_scene_root / "cameras.json", "r") as f:
        cameras = json.load(f)
    # Load splits.json
    with open(source_scene_root / "splits.json", "r") as f:
        splits = json.load(f)

    # Convert cameras.json to transforms.json
    scene_meta_distorted = convert_cameras_to_wai_scene_meta(
        cfg,
        scene_name,
        cameras,
        splits,
        cfg.target_width,
        cfg.target_height,
        cfg.target_extension,
        scene_name,
    )

    scene_meta_distorted["scene_modalities"] = {
        "points_3d": {
            "path": "point_cloud.ply",  # path to a scene_level point cloud
            "format": "ply",
        }
    }

    print(f"Writing scene_meta_distorted.json to {target_scene_root}")
    with open(target_scene_root / "scene_meta_distorted.json", "w") as f:
        json.dump(scene_meta_distorted, f, indent=4)

    # softlink images
    if (source_scene_root / "images-jpeg-4k").exists():
        rel_jpg_paths = find_jpgs(str(source_scene_root / "images-jpeg-4k"))
        (target_scene_root / "images_distorted").mkdir(parents=True, exist_ok=True)
        for jpg_path in rel_jpg_paths:
            os.symlink(
                source_scene_root / "images-jpeg-4k" / jpg_path,
                target_scene_root / "images_distorted" / jpg_path.replace("/", "_"),
            )
    elif (source_scene_root / "images-jpeg").exists():
        # This is only needed for the inofficial scenes where the downscaled jpgs are
        # not directly provided
        rel_jpg_paths = find_jpgs(str(source_scene_root / "images-jpeg"))
        (target_scene_root / "images_distorted").mkdir(parents=True, exist_ok=True)
        for jpg_path in rel_jpg_paths:
            source_image_path = source_scene_root / "images-jpeg" / jpg_path
            target_image_path = (
                target_scene_root / "images_distorted" / jpg_path.replace("/", "_")
            )
            # TODO: The loading, resizing and saving of this 8K images takes very long
            # due to the large file size. This should be optimized.
            # Read the source image
            img = Image.open(source_image_path)
            # Get the dimensions of the source image
            width, height = img.size
            # Check if the aspect ratio is the same as the target aspect ratio
            if check_aspect_ratio_match(
                width, height, cfg.target_width, cfg.target_height
            ):
                raise RuntimeError(
                    f"Aspect ratio mismatch for {jpg_path}, actual aspect ratio is "
                    f"{width / height}, expected aspect ratio is "
                    f"{cfg.target_width / cfg.target_height}."
                )
            # Resize the image to the target dimensions
            resized_img = img.resize((cfg.target_width, cfg.target_height))
            # Write the resized image to the target path
            resized_img.save(target_image_path)
    else:
        raise NotImplementedError(
            "Folder named 'images-jpeg-4k' or 'images-jpeg', "
            f"needs to exist in {source_scene_root}"
        )

    # TODO: Migrate this to WAI and then rerun with store_global_pc
    if cfg.get("store_global_pc", False):
        # Finally write the global point cloud to disk
        load_and_save_point_cloud(
            str(source_scene_root),
            str(target_scene_root / "point_cloud.ply"),
            transform=ROTATION_PC,
        )


if __name__ == "__main__":
    cfg = argconf_parse(
        WAI_PROC_CONFIG_PATH / "conversion/eyeful_official_and_inofficial.yaml"
    )
    convert_scenes_wrapper(converter_func=convert_eyeful_tower_to_wai, cfg=cfg)
