import logging
import os
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from argconf import argconf_parse
from PIL import Image
from wai import load_data, store_data
from wai.camera import rotate_pinhole_90degcw
from wai.io import set_processing_state
from wai_processing import (
    convert_scenes_wrapper,
    WAI_PROC_CONFIG_PATH,
)

"""
This script converts iPhone Hyperscape captures into the wai format.
The input rflib datasets can be provided in two formats:
1. Original (distorted) format,
2. Undistorted format, obtained through a pre-processing step using a FBLearner flow (example: f676080317).

Note: This script is not intended for converting Hyperscape HMD captures into the wai format.
"""

HYPERSCAPE_PINHOLE_CAM_KEYS = ["fl_x", "fl_y", "cx", "cy"]
HYPERSCAPE_DISTORTION_PARAM_KEYS = [
    "k1",
    "k2",
    "p1",
    "p2",
    "k3",
]  # order corresponds to the OpenCV convention

## Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

rot90 = torch.from_numpy(
    np.array(
        [[0, 1, 0], [-1, 0, 0], [0, 0, 1]],
        dtype=np.float32,
    ),
)


def remove_per_frame_params(frames, keys):
    for frame in frames:
        for k in keys:
            if k in frame:
                del frame[k]


def convert_hyperscape_scene(cfg, scene_name):
    dataset_name = cfg.get("dataset_name", "hyperscape")
    version = cfg.get("version", "0.1")
    scene_id = cfg.get("scene_id", "scene_0")
    rotate_to_portrait = cfg.get("rotate_to_portrait", True)

    rflib2wai = {
        "depth": "depth_iphone",
        "foreground": "masks",
        "rgb": "images",
    }

    rflib_root = Path(cfg.original_root) / scene_name / "rflib_dataset"
    scene_root = rflib_root / "scenes" / scene_id
    logger.info(f"Started conversion of scene {scene_name}")
    out_path = Path(cfg.root) / scene_name
    scene_metadata = load_data(scene_root / "scene_metadata.ptz")
    n_images = len(scene_metadata["images"])
    modalities = [m.name for m in scene_root.iterdir() if m.is_dir()]

    # Sanity check: modalities "rgb" and "camera" must be present
    for m in ["rgb", "camera"]:
        if m not in modalities:
            raise FileNotFoundError(f"The rflib dataset does not contain {m}.")

    # More sanity checks: are all folders complete?
    rgb_paths = sorted((scene_root / "rgb").iterdir())
    for m in modalities:
        if m == "_global":
            continue
        n_files = (
            len(rgb_paths)
            if m == "rgb"
            else sum(1 for item in (scene_root / m).iterdir() if item.is_file())
        )
        if n_files != n_images:
            raise IOError(
                f'Scene consists of {n_images} images, but the "{m}" folder contains {n_files} files.'
            )

    # Load the first camera to determine whether we have a distorted or undistorted rflib dataset
    cam = load_data(scene_root / "camera" / f"{rgb_paths[0].stem}.ptz")
    distorted = True if cam["distortion"] is not None else False

    # Prepare output folder structure
    suffix = ""
    if distorted:
        suffix = "_distorted"
        for k in rflib2wai.keys():
            rflib2wai[k] += suffix

    for m in modalities:
        if m not in rflib2wai.keys():
            continue
        os.makedirs(out_path / rflib2wai[m])

    logger.info(f"Processing {n_images} images")
    wai_frames = []
    camera_params = defaultdict(set)

    for rgb_path in rgb_paths:
        frame_name = rgb_path.stem
        wai_frame = {"frame_name": frame_name}

        # RGB images
        target_image_path = f"{rflib2wai['rgb']}/{rgb_path.name}"
        wai_frame[f"image{suffix}"] = target_image_path
        wai_frame["file_path"] = target_image_path
        if rotate_to_portrait:
            # 270 degrees anti-clockwise rotation
            img = load_data(rgb_path, "image", fmt="pil").transpose(Image.ROTATE_270)
            store_data(out_path / target_image_path, img, "image")
        else:
            os.symlink(rgb_path, out_path / target_image_path)

        # Masks
        if "foreground" in modalities:
            target_mask_path = f"{rflib2wai['foreground']}/{rgb_path.name}"
            wai_frame[f"mask_path{suffix}"] = target_mask_path
            if rotate_to_portrait:
                # 270 degrees anti-clockwise rotation
                mask = load_data(
                    scene_root / "foreground" / f"{frame_name}.png", "binary", fmt="pil"
                ).transpose(Image.ROTATE_270)
                store_data(out_path / target_mask_path, mask, "binary")
            else:
                os.symlink(
                    scene_root / "foreground" / rgb_path.name,
                    out_path / target_mask_path,
                )

        # Depths: convert to *.exr
        depth = load_data(scene_root / "depth" / f"{frame_name}.ptz")
        target_depth_path = f"{rflib2wai['depth']}/{frame_name}.exr"
        wai_frame[f"depth_iphone{suffix}"] = target_depth_path
        if rotate_to_portrait:
            # 90 degrees clockwise rotation
            depth = torch.rot90(depth, k=-1)
        store_data(out_path / target_depth_path, depth, "depth")

        # Intrinsics & extrinsics
        cam = load_data(scene_root / "camera" / f"{frame_name}.ptz")
        if cam["camera_type"] != "pinhole":
            raise RuntimeError("Detected non-pinhole camera model!")
        if not distorted and cam["distortion"] is not None:
            raise RuntimeError("Expected all cameras to be without distortion!")

        intrinsics = cam["intrinsics"].tolist()
        cam2world = torch.eye(4)
        R_inv = cam["rotation"].mT
        cam2world[:3, :3] = R_inv
        cam2world[:3, 3] = -R_inv @ cam["translation"]

        if rotate_to_portrait:
            cam2world[:3, :3] = cam2world[:3, :3] @ rot90
            _, _, fx, fy, cx, cy = rotate_pinhole_90degcw(
                img.height,  # img is rotated already
                img.width,
                intrinsics[0],
                intrinsics[1],
                intrinsics[2],
                intrinsics[3],
            )
            intrinsics = [fx, fy, cx, cy]

        camera_params["intrinsics"].add(tuple(intrinsics))
        for camera_key, value in zip(HYPERSCAPE_PINHOLE_CAM_KEYS, intrinsics):
            wai_frame[camera_key] = value

        if cam["distortion"] is not None:
            distortion = cam["distortion"].tolist()
            if len(distortion) != 5:
                raise RuntimeError(
                    f"Expected 5 distortion parameters (k1, k2, p1, p2, k3) but found {len(distortion)} parameters for the camera with ID {frame_name}."
                )

            camera_params["distortion"].add(tuple(distortion))
            for camera_key, value in zip(HYPERSCAPE_DISTORTION_PARAM_KEYS, distortion):
                wai_frame[camera_key] = value

        wai_frame["transform_matrix"] = cam2world.tolist()
        wai_frames.append(wai_frame)

    if "_global" in modalities:
        pc_path = scene_root / "_global" / "point_cloud.ply"
        if not pc_path.exists():
            raise FileNotFoundError(f"Could not find SfM point cloud {pc_path}")
        os.symlink(pc_path, out_path / "point_cloud.ply")

    shared_intrinsics = True if len(camera_params["intrinsics"]) == 1 else False
    if distorted and len(camera_params["distortion"]) != 1:
        shared_intrinsics = False
    scene_meta = {
        "scene_name": scene_name,
        "dataset_name": dataset_name,
        "version": version,
        "shared_intrinsics": shared_intrinsics,
        "camera_model": "PINHOLE" if not distorted else "OPENCV",
        "camera_convention": "opencv",
    }

    if shared_intrinsics:
        # Remove per-frame intrinsics
        remove_per_frame_params(wai_frames, keys=HYPERSCAPE_PINHOLE_CAM_KEYS)
        intrinsics = camera_params["intrinsics"].pop()
        for camera_key, value in zip(HYPERSCAPE_PINHOLE_CAM_KEYS, intrinsics):
            scene_meta[camera_key] = value

        if distorted:
            remove_per_frame_params(wai_frames, keys=HYPERSCAPE_DISTORTION_PARAM_KEYS)
            distortion = camera_params["distortion"].pop()
            for camera_key, value in zip(HYPERSCAPE_DISTORTION_PARAM_KEYS, distortion):
                scene_meta[camera_key] = value

    scene_meta["w"], scene_meta["h"] = load_data(
        out_path / wai_frames[0][f"image{suffix}"], "image", fmt="pil"
    ).size  # correct dimensions for both original or rotated images
    scene_meta["scale_type"] = "metric"
    scene_meta["frames"] = wai_frames
    scene_meta["frame_modalities"] = {
        f"image{suffix}": {"frame_key": f"image{suffix}", "format": "image"},
        f"depth_iphone{suffix}": {
            "frame_key": f"depth_iphone{suffix}",
            "format": "depth",
        },
    }
    if "foreground" in modalities:
        scene_meta["frame_modalities"][f"mask{suffix}"] = {
            "frame_key": f"mask_path{suffix}",
            "format": "binary",
        }

    if "_global" in modalities:
        scene_meta["scene_modalities"] = {
            "points_3d": {"path": "point_cloud.ply", "format": "ply"}
        }

    if rotate_to_portrait:
        transform = torch.eye(4)
        transform[:3, :3] = rot90
        scene_meta["_applied_transform"] = transform.tolist()
        scene_meta["_applied_transforms"] = {"image_rotation": transform.tolist()}
    else:
        # Original data already in opencv convention
        scene_meta["_applied_transform"] = np.eye(4).tolist()
        scene_meta["_applied_transforms"] = {}
    scene_meta_fname = f"scene_meta{suffix}.json"
    store_data(out_path / scene_meta_fname, scene_meta, "scene_meta")
    if not distorted:
        set_processing_state(out_path, "undistortion", "finished")


if __name__ == "__main__":
    cfg = argconf_parse(WAI_PROC_CONFIG_PATH / "conversion/hyperscape.yaml")
    convert_scenes_wrapper(convert_hyperscape_scene, cfg)
