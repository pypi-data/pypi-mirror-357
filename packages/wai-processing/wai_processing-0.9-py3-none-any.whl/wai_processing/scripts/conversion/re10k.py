import logging
import os
import zipfile
from pathlib import Path

import numpy as np
import torch
from argconf import argconf_parse
from wai import load_data, store_data
from wai.scene_frame import _filter_scenes
from wai_processing import convert_scenes_wrapper, WAI_PROC_CONFIG_PATH

## Set up basic logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("re10k")

# Skip PIL debug messages
logging.getLogger("PIL").setLevel(logging.WARNING)

IMAGE_FOLDER_NAME = "images"
CamParamsType = dict[str, np.ndarray | tuple[float] | list[str]]


def extract_zip_and_flatten(zip_dir: Path | str, out_dir: Path | str) -> None:
    with zipfile.ZipFile(zip_dir, "r") as z:
        for file_info in z.infolist():
            if not file_info.is_dir():
                extracted_path = os.path.join(
                    out_dir, os.path.basename(file_info.filename)
                )
                with z.open(file_info) as source, open(extracted_path, "wb") as target:
                    target.write(source.read())


def fov_to_normalized_focal_length(fov):
    return (1.0 / (2 * np.tan(fov / 2))).item()


def is_temporally_ordered(cam_params: CamParamsType) -> bool:
    timestamps = [int(name) for name in cam_params["names"]]
    return all(x < y for x, y in zip(timestamps, timestamps[1:]))


def load_camera_info(file: Path) -> CamParamsType:
    if not file.exists():
        raise FileNotFoundError(f"{file} not found")

    cam_params = load_data(file, allow_pickle=True).item()

    missing_keys = [
        key for key in ["names", "poses", "fov"] if key not in cam_params.keys()
    ]
    if len(missing_keys) > 0:
        raise KeyError(
            f'{file} expected to be a dictionary with keys ["names, "poses", "fov"], but the key(s) {missing_keys} is/are missing.'
        )

    if not isinstance(cam_params["poses"], np.ndarray):
        raise TypeError(
            f'cam_params["poses"] expected to be of type np.ndarray, but has type {type(cam_params["poses"])}.'
        )

    if not isinstance(cam_params["fov"], tuple):
        raise TypeError(
            f'cam_params["fov"] expected to be a tuple, but has type {type(cam_params["fov"])}.'
        )

    if cam_params["poses"].ndim != 3 or cam_params["poses"].shape[1:] != (3, 4):
        raise ValueError(
            f'cam_params["poses"] expected to have shape Nx3x4, but has shape {cam_params["poses"].shape}.'
        )

    if len(cam_params["fov"]) != 2:
        raise ValueError(
            f'cam_params["fov"] expected to have two parameters, but has {len(cam_params["fov"])} parameters.'
        )

    return cam_params


def temporally_order_data(cam_params: CamParamsType) -> CamParamsType:
    sorted_indices = np.argsort([int(name) for name in cam_params["names"]])
    cam_params_out = {}
    cam_params_out["poses"] = cam_params["poses"][sorted_indices, ...]
    cam_params_out["names"] = [cam_params["names"][idx] for idx in sorted_indices]
    cam_params_out["fov"] = cam_params["fov"]
    return cam_params_out


def convert_scene(cfg, scene_name):
    dataset_name = cfg.get("dataset_name", "RealEstate10K")
    version = cfg.get("version", "0.1")
    scene_zipdir = Path(cfg.original_root, f"{scene_name}.zip")
    logger.info(f"Started conversion of scene {scene_name}")

    out_path = Path(cfg.root) / scene_name
    out_path_images = out_path / IMAGE_FOLDER_NAME
    os.makedirs(out_path_images)

    # Extract zip
    extract_zip_and_flatten(scene_zipdir, out_path_images)

    # Load camera info
    cam_file = out_path_images / "camera_info.npy"
    cam_params = load_camera_info(cam_file)

    # Sanity check: number of poses should match the number of images
    num_images = len(
        [f for f in out_path_images.iterdir() if f.is_file and f.name.endswith(".png")]
    )
    num_poses = cam_params["poses"].shape[0]
    if num_poses != num_images or num_poses != len(cam_params["names"]):
        raise ValueError(f"Found {num_poses} poses for {num_images} images.")

    # Sanity check: data should be temporally ordered by default; if not, sort the data
    if not is_temporally_ordered(cam_params):
        logger.warning(
            "Data does not seem to be temporally ordered. "
            "Temporally ordering the data now."
        )
        cam_params = temporally_order_data(cam_params)

    # Intrinsics
    fov_x, fov_y = cam_params["fov"]
    cx, cy = 0.5, 0.5
    fl_x = fov_to_normalized_focal_length(fov_x)
    fl_y = fov_to_normalized_focal_length(fov_y)

    wai_frames = []
    image_size = set()

    for idx in range(cam_params["poses"].shape[0]):
        frame_name = cam_params["names"][idx]
        image_path = out_path_images / f"{frame_name}.png"
        if not image_path.exists():
            raise FileNotFoundError(
                f"Pose given for image {image_path.name}, but image does not exist in {out_path_images}"
            )

        # Retrieve image size
        img = load_data(image_path, fmt="pil")
        image_size.add(img.size)

        # Store frame info
        wai_frame = {"frame_name": frame_name}
        wai_frame["image"] = f"{IMAGE_FOLDER_NAME}/{image_path.name}"
        wai_frame["file_path"] = f"{IMAGE_FOLDER_NAME}/{image_path.name}"

        # Extrinsics: convert world2cam to cam2world
        w2c_mat = cam_params["poses"][idx]
        w2c_mat_4x4 = torch.cat(
            [
                torch.from_numpy(w2c_mat),
                torch.tensor([0, 0, 0, 1], dtype=torch.float32).view(1, 4),
            ],
            0,
        )
        c2w_mat = torch.linalg.inv(w2c_mat_4x4)
        wai_frame["transform_matrix"] = c2w_mat.tolist()

        wai_frames.append(wai_frame)

    # Delete camera_info.npy, no longer needed
    os.remove(cam_file)

    # Sanity check
    if len(image_size) > 1:
        raise ValueError(
            f"Something is wrong. Detected varying image sizes {image_size}"
        )

    W, H = image_size.pop()

    # Unnormalize intrinsics
    fl_x *= W
    fl_y *= H
    cx *= W
    cy *= H

    scene_meta = {
        "scene_name": scene_name,
        "dataset_name": dataset_name,
        "version": version,
        "shared_intrinsics": True,
        "camera_model": "PINHOLE",
        "camera_convention": "opencv",
        "fl_x": fl_x,
        "fl_y": fl_y,
        "cx": cx,
        "cy": cy,
        "h": H,
        "w": W,
        "scale_type": "colmap",
    }
    scene_meta["frames"] = wai_frames
    scene_meta["frame_modalities"] = {
        "image": {"frame_key": "image", "format": "image"},
    }
    scene_meta["scene_modalities"] = {}
    # original data already in opencv convention
    scene_meta["_applied_transform"] = np.eye(4).tolist()
    scene_meta["_applied_transforms"] = {}
    store_data(out_path / "scene_meta.json", scene_meta, "scene_meta")


def get_original_scene_names(cfg):
    # originals stored in zips
    # returns the list of all original scene names after filtering
    scene_names = sorted(
        [
            scene.stem
            for scene in Path(cfg.original_root).iterdir()
            if zipfile.is_zipfile(scene)
        ]
    )

    # scene filter for batch processing (special case since stored as .zip)
    scene_names = _filter_scenes(
        cfg.original_root, scene_names, cfg.get("scene_filters")
    )
    # enable filtering for processing state
    scene_names = _filter_scenes(cfg.root, scene_names, cfg.get("scene_filters"))
    return scene_names


if __name__ == "__main__":
    cfg = argconf_parse(WAI_PROC_CONFIG_PATH / "conversion/re10k.yaml")
    convert_scenes_wrapper(
        converter_func=convert_scene,
        cfg=cfg,
        get_original_scene_names_func=get_original_scene_names,
    )
