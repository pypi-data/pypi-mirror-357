from copy import deepcopy
from pathlib import Path
from typing import Any, Dict

import numpy as np
from wai import get_frame, set_frame, store_data


def apply_metric_alignment(
    scene_root: Path,
    scene_meta: Dict[str, Any],
    wai2metric_scale_factor: float,
    alignment_method: str,
) -> None:
    """
    Apply metric alignment to a scene using the provided scale factor.

    Args:
        scene_root: Path to the scene directory
        scene_meta: The scene metadata dictionary
        wai2metric_scale_factor: Scale factor to convert from WAI to metric scale
        alignment_method: Name of the alignment method (e.g., 'colmap', 'mast3r')
    """
    metric_transform = np.diag([1, 1, 1, wai2metric_scale_factor])
    frame_names = [frame["frame_name"] for frame in scene_meta["frames"]]

    # --- scale all translations according to the estimated metric scale factor ---
    for frame_name in frame_names:
        metric_frame = deepcopy(
            get_frame(scene_meta, frame_name)
        )  # copy instead of overwrite for safety
        est_metric_pose = np.array(metric_frame["transform_matrix"]) @ metric_transform
        est_metric_pose[3, 3] = 1
        metric_frame["transform_matrix"] = est_metric_pose.tolist()
        set_frame(scene_meta, frame_name, metric_frame)

    # ---- update the scene meta ----
    scene_meta["_applied_transform"] = (
        np.array(scene_meta["_applied_transform"]) @ metric_transform
    ).tolist()
    applied_transforms = scene_meta.get("_applied_transforms", {})

    transform_key = f"metric_alignment_{alignment_method}"
    if transform_key not in applied_transforms:
        applied_transforms[transform_key] = metric_transform.tolist()
    else:
        # metric alignment was already applied
        i = 1
        while f"{transform_key}_{i}" in applied_transforms:
            i += 1
        applied_transforms[f"{transform_key}_{i}"] = metric_transform.tolist()

    scene_meta["scale_type"] = "metric_estimated"
    scene_meta["_applied_transforms"] = applied_transforms
    store_data(Path(scene_root, "scene_meta.json"), scene_meta, "scene_meta")
