import os
from pathlib import Path

import cv2
import numpy as np
import torch
from argconf import argconf_parse
from scipy.spatial.transform import Rotation as R
from wai import store_data
from wai_processing import (
    convert_scenes_wrapper,
    WAI_PROC_CONFIG_PATH,
)

# Usage:
# python -m wai.scripts.conversion.tartanair_v2

ROT_TARTANAIR_TO_WAI = (
    R.from_euler("x", 90, degrees=True).as_matrix()
    @ R.from_euler("y", 90, degrees=True).as_matrix()
)

TARTAN_AIR_PINHOLE_CAM_KEYS = [
    "lcam_front",
    "lcam_back",
    "lcam_left",
    "lcam_right",
    "lcam_top",
    "lcam_bottom",
    "rcam_front",
    "rcam_back",
    "rcam_left",
    "rcam_right",
    "rcam_top",
    "rcam_bottom",
]


TARTAN_AIR_FISHEYE_CAM_KEYS = [
    "lcam_fish",
    "rcam_fish",
]

TARTAN_AIR_EQUIRECT_CAM_KEYS = [
    "lcam_equirect",
    "rcam_equirect",
]

TARTAN_AIR_ALL_CAM_KEYS = (
    TARTAN_AIR_PINHOLE_CAM_KEYS
    + TARTAN_AIR_FISHEYE_CAM_KEYS
    + TARTAN_AIR_EQUIRECT_CAM_KEYS
)

GEOMETRIC_ENV_TO_MAX_DEPTH = {
    "Prison": 80.0,
    "OldTown": 80.0,
    "ShoreCaves": 120.0,
    "OldBrickHouse": 35.0,
}


def get_depth_from_env(env_name):
    for geometric_env, max_depth in GEOMETRIC_ENV_TO_MAX_DEPTH.items():
        # Subtrsing check, i.e. "OldTown" in "OldTownSummer" would return True
        if geometric_env in env_name:
            return max_depth
    # default depth of 200m for all other cases
    return 200.0


def pos_quat2SE(quat_data):
    SO = R.from_quat(quat_data[3:7]).as_matrix() @ ROT_TARTANAIR_TO_WAI
    SE = np.matrix(np.eye(4))
    SE[0:3, 0:3] = np.matrix(SO)
    SE[0:3, 3] = np.matrix(quat_data[0:3]).T
    return SE


# Create iterator for a single scene with hard & easy trajectory difficulty
def process_tartan_air_scene(cfg, scene_name):
    """
    We create a single WAI scene for any given Tartan Air scene, merging all difficulties and trajectories.
    Expected input folder layout for the raw Tartanair dataset:
    └── AbandonedCable (scene_name)
        └── Data_easy  (or hard)
            └── P001   (trajectory_type)
                ├── depth_lcam_back (folder with depth maps)
                ├── depth_lcam_bottom
                ├── depth_..._... (continue for all other cam types and left and right camera rig)
                ├── image_lcam_back (folder with images)
                ├── image_lcam_bottom
                ├── image_..._... (continue for all other cam types and left and right camera rig)
                ├── pose_lcam_back.txt
                ├── pose_lcam_back.txt
                └── pose_..._....txt
            └── P... (all other trajs)
        └── Data_hard
            └── P... (same structure as for easy)
    └── Scene_ABC (all 74 scenes with the same structure, number of trajectories per scene may vary)
    """
    scene_root = Path(cfg.original_root) / scene_name
    target_scene_root = Path(cfg.root) / scene_name
    image_dir = target_scene_root / "images"
    image_dir.mkdir(parents=True, exist_ok=False)
    depth_dir = target_scene_root / "depth"
    depth_dir.mkdir(parents=True, exist_ok=False)
    wai_frames = []

    cam_ids = cfg.get("cam_ids", TARTAN_AIR_PINHOLE_CAM_KEYS)
    if not set(cam_ids).issubset(TARTAN_AIR_PINHOLE_CAM_KEYS):
        raise RuntimeError(
            f"Specified trajectory ids {set(cam_ids) - set(TARTAN_AIR_PINHOLE_CAM_KEYS)} "
            f"are no valid camera keys, valid camera keys are:."
        )

    # There is no proper handling of infinite distance (sky) in Tartanair
    # Ski will return very large values like 3000m, thus clamping depth
    max_depth = get_depth_from_env(scene_name)
    for difficulty in cfg.difficulties:
        # If None --> Use all trajectories per scene and difficulty
        available_trajectory_ids = [
            full_path.stem for full_path in (scene_root / difficulty).iterdir()
        ]
        trajectory_ids = cfg.get("trajectory_ids", available_trajectory_ids)
        if not set(trajectory_ids).issubset(available_trajectory_ids):
            raise RuntimeError(
                f"Specified trajectory ids {set(trajectory_ids) - set(available_trajectory_ids)} "
                f"are not available for scene {scene_root / difficulty}."
            )
        for traj_id in trajectory_ids:
            for cam_key in cam_ids:
                # Process camera txt file
                posefile = Path(
                    scene_root, difficulty, traj_id, "pose_" + cam_key + ".txt"
                )
                poselist = np.loadtxt(posefile).astype(np.float32)
                all_poses = []
                for pose_quaternion in poselist:
                    all_poses.append(pos_quat2SE(pose_quaternion))
                image_folder = Path(scene_root, difficulty, traj_id, "image_" + cam_key)
                for image_path, cam_pose in zip(
                    sorted(image_folder.rglob("*")), all_poses
                ):
                    frame_name = (
                        f"{difficulty}_{traj_id}_image_{cam_key}_{image_path.stem[:6]}"
                    )
                    rel_target_image_path = (
                        Path("images") / f"{frame_name}{image_path.suffix}"
                    )

                    # TODO: It would be better to directly symlink the whole folder but the raw frames
                    # have conflicting filenames across different trajs etc., thus symlinking on file
                    # level
                    # Softlink images to WAI path
                    os.symlink(image_path, target_scene_root / rel_target_image_path)
                    # Process depth images
                    depth_rgba = cv2.imread(
                        str(image_path)
                        .replace("image", "depth")
                        .replace(".png", "_depth.png"),
                        cv2.IMREAD_UNCHANGED,
                    )
                    depth_image = np.squeeze(depth_rgba.view("<f4"), axis=-1)
                    if (depth_image.shape[0] != 640) or (depth_image.shape[1] != 640):
                        # Just sanity checking the depth map size as the camera intrinsics are hard-coded below, i
                        raise RuntimeError(
                            f"Mismatched depth map shape {depth_image.shape}, expected width and height of 640"
                        )
                    if max_depth is not None:
                        depth_image[depth_image > max_depth] = 0
                    rel_depth_out_path = Path("depth") / (frame_name + ".exr")
                    store_data(
                        target_scene_root / rel_depth_out_path,
                        torch.tensor(depth_image),
                        "depth",
                    )
                    wai_frame = {
                        "frame_name": frame_name,
                        "image": str(rel_target_image_path),
                        "file_path": str(rel_target_image_path),
                        "depth": str(rel_depth_out_path),
                        "transform_matrix": cam_pose.tolist(),
                    }
                    wai_frames.append(wai_frame)

    scene_meta = {
        "scene_name": scene_name,
        "dataset_name": cfg.dataset_name,
        "version": cfg.version,
        "shared_intrinsics": True,
        "camera_model": "PINHOLE",
        "camera_convention": "opencv",
        "scale_type": "metric",
        "scene_modalities": {},
        "fl_x": 320,
        "fl_y": 320,
        "cx": 320,
        "cy": 320,
        "h": 640,
        "w": 640,
        "frames": wai_frames,
        "frame_modalities": {
            "image": {"frame_key": "image", "format": "image"},
            "depth": {
                "frame_key": "depth",
                "format": "depth",
            },
        },
    }
    store_data(target_scene_root / "scene_meta.json", scene_meta, "scene_meta")


if __name__ == "__main__":
    cfg = argconf_parse(WAI_PROC_CONFIG_PATH / "conversion/tartanair_v2.yaml")
    convert_scenes_wrapper(process_tartan_air_scene, cfg)
