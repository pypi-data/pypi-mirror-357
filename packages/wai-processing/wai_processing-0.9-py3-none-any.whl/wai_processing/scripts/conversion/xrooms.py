import json
import logging
from pathlib import Path

import numpy as np
import pyvrs
import torch
from argconf import argconf_parse
from PIL import Image
from scipy.spatial.transform import Rotation as R
from wai import store_data
from wai_processing import (
    convert_scenes_wrapper,
    get_original_scene_names,  # noqa: F401, Needed for launch_slurm.py
    WAI_PROC_CONFIG_PATH,
)
from wai_processing.utils.mapper import DistanceToDepthConverter

## Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# XROOMS constants
XROOMS_DEPTH_VRS_NAME = (
    "Dolores-Interiors_P-ProceduralTrajectory-Eureka-SENSEI_EYE_BUFFERS-Depth.vrs"
)
XROOMS_RGB_VRS_NAME = "Dolores-Interiors_P-ProceduralTrajectory-Eureka-SENSEI_EYE_BUFFERS-SensorSimulated.vrs"
XROOMS_STREAM_ID_SETS = [
    # left eye buffer: rgb, depth stream id
    ["left", "4202-1", "340-1"],
    ["right", "4202-2", "340-1"],
]
XROOMS_VRS_SHARED_META_KEYS = ["capture_timestamp_ns", "frame_number", "frame_tag"]


def get_cameras_from_rgb_reader(reader):
    camera_calib = json.loads(
        reader.filtered_by_fields(stream_ids="4202-1", record_types="configuration")[
            0
        ].metadata_blocks[0]["factory_calibration"]
    )["CameraCalibration"]
    assert len(camera_calib) == 2, "Expected two cameras"
    out_dict = {}
    for cam_side, raw_cam in zip(["left", "right"], camera_calib):
        assert raw_cam["Distortion"]["Coefficients"] == [
            0,
            0,
            0,
            0,
            0,
        ], "Expected no distortion"
        assert raw_cam["Projection"]["Model"] == "Pinhole", (
            "Expected pinhole projection"
        )
        out_dict[cam_side] = {
            "w": raw_cam["ImageSize"][0],
            "h": raw_cam["ImageSize"][1],
            "fl_x": raw_cam["Projection"]["Coefficients"][0],
            "fl_y": raw_cam["Projection"]["Coefficients"][1],
            "cx": raw_cam["Projection"]["Coefficients"][2],
            "cy": raw_cam["Projection"]["Coefficients"][3],
            "camera_model": "PINHOLE",
        }
    return out_dict


def convert_xrooms_to_wai(cfg, scene_name):
    """
    Convert an xRooms dataset to the WAI format.
    Parameters:
    cfg (dict): Configuration dictionary.
    """
    target_scene_root = Path(cfg.root) / scene_name
    # Read the VRS file
    reader_depth = pyvrs.SyncVRSReader(
        str(Path(cfg.original_root) / scene_name / XROOMS_DEPTH_VRS_NAME),
        auto_read_configuration_records=True,
    )
    reader_rgb = pyvrs.SyncVRSReader(
        str(Path(cfg.original_root) / scene_name / XROOMS_RGB_VRS_NAME),
        auto_read_configuration_records=True,
    )
    dataset_name = cfg.get("dataset_name", "xRooms")
    version = cfg.get("version", "0.1")

    # Create all output folders
    image_dir = target_scene_root / "images"
    image_dir.mkdir(parents=True, exist_ok=False)
    depth_dir = target_scene_root / "depth"
    depth_dir.mkdir(parents=True, exist_ok=False)

    # TODO: Multi-line logging seems suboptimal. Convert to two separate lines?
    # Log VRS file overview
    logger.info(
        f"\n_______\nRGB reader:\n{reader_rgb}\n_______\nDepth reader {reader_depth}\n"
    )

    # Iterate over the two depth streams
    wai_frames = []

    cams = get_cameras_from_rgb_reader(reader_rgb)
    for stream_side, rgb_stream_id, depth_stream_id in XROOMS_STREAM_ID_SETS:
        dist2depth_converter = DistanceToDepthConverter(**cams[stream_side])
        for record_rgb, record_distance in zip(
            reader_rgb.filtered_by_fields(
                stream_ids=rgb_stream_id, record_types="data"
            ),
            reader_depth.filtered_by_fields(
                stream_ids=depth_stream_id, record_types="data"
            ),
        ):
            # Get the distance map, convert to depth, and get the pose
            distance_map = record_distance.image_blocks[0]
            depth_image = dist2depth_converter.distance_to_depth(distance_map)
            depth_meta = record_distance.metadata_blocks[0]
            pose_xyz_quat = depth_meta["camera_pose"]
            pose = np.eye(4)
            pose[:3, :3] = R.from_quat(pose_xyz_quat[3:]).as_matrix()
            pose[:3, 3] = pose_xyz_quat[:3]

            # Get RGB
            rgb_image = record_rgb.image_blocks[0]
            rgb_meta = record_rgb.metadata_blocks[0]

            # sanity check, this is synthetic data so the metadata should always be
            # perfectly in sync for the rgb and depth VRS files
            if any(
                rgb_meta[key] != depth_meta[key] for key in XROOMS_VRS_SHARED_META_KEYS
            ):
                raise RuntimeError(
                    "Metadata mismatch between depth and rgb. Depth metadata: "
                    f"{depth_meta}, RGB metadata: {rgb_meta}"
                )
            frame_name = f"{stream_side}_{rgb_meta['frame_number']:06d}"
            # Store all data
            rel_depth_out_path = Path("depth") / (frame_name + ".exr")
            rel_target_image_path = Path("images") / (frame_name + ".jpg")
            store_data(
                target_scene_root / rel_depth_out_path,
                torch.tensor(depth_image),
                "depth",
            )
            store_data(
                target_scene_root / rel_target_image_path,
                Image.fromarray((rgb_image).astype(np.uint8)),
                "image",
            )

            wai_frame = {
                "frame_name": frame_name,
                "file_path": str(rel_target_image_path),
                "image": str(rel_target_image_path),
                "depth": str(rel_depth_out_path),
                "transform_matrix": pose.tolist(),
            }
            wai_frame.update(cams[stream_side])
            wai_frames.append(wai_frame)
    scene_meta = {
        "scene_name": scene_name,
        "dataset_name": dataset_name,
        "version": version,
        "scale_type": "metric",
        "frames": wai_frames,
        "frame_modalities": {
            "image": {"frame_key": "image", "format": "image"},
            "depth": {
                "frame_key": "depth",
                "format": "depth",
            },
        },
        "scene_modalities": {},
        # slightly different cams between left and right
        "shared_intrinsics": False,
        "camera_convention": "opencv",
    }
    store_data(target_scene_root / "scene_meta.json", scene_meta, "scene_meta")


if __name__ == "__main__":
    cfg = argconf_parse(WAI_PROC_CONFIG_PATH / "conversion/xrooms.yaml")
    convert_scenes_wrapper(converter_func=convert_xrooms_to_wai, cfg=cfg)
