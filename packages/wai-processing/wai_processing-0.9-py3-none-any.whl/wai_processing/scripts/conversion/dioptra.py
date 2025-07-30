import logging
import os
from pathlib import Path

import numpy as np
from argconf import argconf_parse
from wai import load_data, store_data
from wai.camera import DISTORTION_PARAM_KEYS, gl2cv, PINHOLE_CAM_KEYS
from wai_processing import (
    convert_scenes_wrapper,
    WAI_PROC_CONFIG_PATH,
)

## Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

DIOPTRA_CAMERA_MODEL = "PINHOLE"


def check_for_shared_camera_parameters(metadata):
    parameters = {k: metadata["frames"][0][k] for k in PINHOLE_CAM_KEYS}
    for frame in metadata["frames"]:
        for cam_key in PINHOLE_CAM_KEYS:
            if frame[cam_key] != parameters[cam_key]:
                raise RuntimeError(
                    "Expected the camera intrinsics for all frames to be the same, but found a mismatched entry",
                    f"\n\n First frame:\n{metadata['frames'][0]}\n Second frame:\n{frame}",
                )
        if frame["camera_model"] == "OPENCV" and any(
            [key in frame for key in DISTORTION_PARAM_KEYS]
        ):
            raise RuntimeError("Expected all dioptra cams to not have distortion.")
    # logger.info("Checked that the intrinsics for all frames are the same")
    parameters["camera_model"] = DIOPTRA_CAMERA_MODEL
    return parameters


def process_single_nerfstudio_scene(cfg, scene_name: str):
    source_dir = Path(cfg.original_root, scene_name)
    transforms_fn = Path(source_dir, "nerfstudio_format", "transforms.json")
    logger.info(f"Processing scene: {scene_name}")
    out_path = Path(cfg.root) / scene_name
    meta = load_data(transforms_fn)
    frames = meta["frames"]

    image_out_path = out_path / "images"
    os.makedirs(image_out_path)
    wai_frames = []

    # In the source dataset the intrinsics are specified per frame, but are actually shared,
    # sanity check all frames --> camera parameters for each frame should be the same
    # Then writing the data to wai with shared parameters
    shared_camera_parameters = check_for_shared_camera_parameters(meta)

    for frame in frames:
        frame_name = Path(frame["file_path"]).stem
        wai_frame = {"frame_name": frame_name}
        org_transform_matrix = np.array(frame["transform_matrix"]).astype(np.float32)
        opencv_pose, gl2cv_cmat = gl2cv(org_transform_matrix, return_cmat=True)
        # link distorted images
        source_image_path = Path(source_dir, "nerfstudio_format", frame["file_path"])
        target_image_path = (
            f"images/{frame_name}{os.path.splitext(source_image_path)[1]}"
        )
        os.symlink(source_image_path, out_path / target_image_path)
        wai_frame["image"] = target_image_path
        wai_frame["file_path"] = target_image_path
        wai_frame["transform_matrix"] = opencv_pose.tolist()
        wai_frames.append(wai_frame)

    scene_meta = {
        "scene_name": scene_name,
        "dataset_name": cfg.dataset_name,
        "version": cfg.version,
        "shared_intrinsics": True,
        "camera_convention": "opencv",
        "scale_type": "metric",
        "camera_model": DIOPTRA_CAMERA_MODEL,
        "frames": wai_frames,
        "frame_modalities": {"image": {"frame_key": "image", "format": "image"}},
        "scene_modalities": {},  # No addtional modalities for now, should get global PC for Dioptra Navvis VLX
        "_applied_transform": gl2cv_cmat.tolist(),
        "_applied_transforms": {
            "opengl2opencv": gl2cv_cmat.tolist()
        },  # transforms raw poses to opencv poses
    }

    for camera_key in PINHOLE_CAM_KEYS:
        scene_meta[camera_key] = shared_camera_parameters[camera_key]

    store_data(out_path / "scene_meta.json", scene_meta, "scene_meta")


if __name__ == "__main__":
    cfg = argconf_parse(WAI_PROC_CONFIG_PATH / "conversion/dioptra.yaml")
    convert_scenes_wrapper(process_single_nerfstudio_scene, cfg)
