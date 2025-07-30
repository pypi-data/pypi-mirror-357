import logging
import traceback
from pathlib import Path
from typing import Any

import numpy as np
import torch
from argconf import argconf_parse
from tqdm import tqdm
from wai import get_scene_names, load_data, load_frame
from wai.alignment import absolute_trajectory_error, to_Rt
from wai.colmap_parsing_utils import load_colmap
from wai.io import set_processing_state
from wai.m_ops import m_dot, m_project
from wai.ops import resize
from wai_processing import WAI_PROC_CONFIG_PATH

from .metric_alignment.metric_alignment_utils import apply_metric_alignment

## Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def colmap_pred_depth_metric_alignment(
    scene_root: str | Path,
    scene_meta: dict[Any, Any],
    max_num_frames: int,
    device: str = "cuda",
):
    """
    Estimate metric scale factor using COLMAP sparse reconstruction and predicted metric depths.

    This function aligns COLMAP sparse reconstruction with WAI camera poses and
    computes the scale factor between predicted metric depths and COLMAP 3D points to
    convert from WAI scale to metric scale.

    Args:
        scene_root: Path to the scene directory
        scene_meta: The scene metadata dictionary
        max_num_frames: Maximum number of frames to use for alignment
        device: Device to use for computations ('cuda' or 'cpu')

    Returns:
        float: Scale factor to convert from WAI scale to metric scale

    Raises:
        RuntimeError: If alignment fails or ATE exceeds maximum threshold
    """
    colmap_path = Path(scene_root, "colmap", "sparse", "0")
    colmap_data = load_colmap(colmap_path, device=device)

    sel_im_ins = list(colmap_data["im_in2name"].keys())
    if max_num_frames < len(colmap_data["im_in2name"]):
        sel_im_ins = sorted(
            [
                int(x)
                for x in np.random.choice(
                    list(colmap_data["im_in2name"].keys()),
                    max_num_frames,
                    replace=False,
                )
            ]
        )

    # === load selected frames ===
    pred_depths = []
    extrinsics = []
    intrinsics = []

    for sel_im_in in sel_im_ins:
        colmap_img_name = colmap_data["im_in2name"][sel_im_in]
        frame_name = Path(colmap_img_name).stem  # using original frame_name
        sample = load_frame(
            scene_root, frame_name, modalities=["pred_depth"], scene_meta=scene_meta
        )
        pred_depth = (sample["pred_depth"]).to(device)
        # resize to colmap image size
        pred_depth = resize(
            pred_depth,
            size=(colmap_data["h"], colmap_data["w"]),
            modality_format="depth",
        )
        extrinsics.append(sample["extrinsics"])
        intrinsics.append(sample["intrinsics"])
        pred_depths.append(pred_depth)

    pred_depths = torch.stack(pred_depths)
    intrinsics = torch.stack(intrinsics).to(device)
    extrinsics = torch.stack(extrinsics).to(device)
    # === prepare camera info ===
    colmap_world2cam = (
        torch.stack([colmap_data["poses"][im_in] for im_in in sel_im_ins])
        .to(device)
        .float()
    )
    colmap_cam2world = colmap_world2cam.inverse()

    ### --- Align colmap -> wai ---
    # this ensures that the metric scale is relative to wai space

    # Call Umeyama alignment to align Colmap with WAI poses, e.g. for RE10K these were obtained with SLAM + BA
    ate, aligned_pred, colmap2wai, transform_dict = absolute_trajectory_error(
        colmap_cam2world[:, :3, 3].unsqueeze(0),
        extrinsics[:, :3, 3].unsqueeze(0),
        alignment=True,
        return_transform=True,
    )
    if colmap2wai.shape[0] > 1:
        raise RuntimeError(
            "Umeyama alignment only supported with batch size one for now."
        )
    colmap2wai = colmap2wai[0]

    ### Apply transforms on all relevant Colmap data ###
    # Apply to Colmap 3D points
    colmap_data["points3D_xyz"] = m_dot(colmap2wai, colmap_data["points3D_xyz"])
    # Overwrite colmap_world2cam to be wai2cam
    # colmap_cam->world->wai, remove scale so
    colmap_world2cam = to_Rt(colmap2wai @ colmap_cam2world).inverse()
    ### -------

    colmap_intrinsic = colmap_data["intrinsic"].float()

    # Sanity check intrinsics
    max_intrinsic_factor = cfg.get("max_intrinsic_factor", 1.1)
    if (
        torch.abs(1 - intrinsics[0][0][0] / colmap_intrinsic[0][0])
        > max_intrinsic_factor
    ):
        raise RuntimeError(
            "Focal length of the WAI dataset and the Colmap run differ more "
            f"than {int((max_intrinsic_factor - 1)) * 100}%, likely faulty Colmap run or faulty Colmap post processing."
        )

    colmap_point_depths = []
    pred_point_depths = []
    per_view_scale_factor = []
    valid_uv_mask = (
        (colmap_data["points3D_points2D_xy"] >= 0).all(-1)
        & (colmap_data["points3D_points2D_xy"][..., 0] < colmap_data["w"])
        & (colmap_data["points3D_points2D_xy"][..., 1] < colmap_data["h"])
    )
    for img_idx, sel_im_in in enumerate(sel_im_ins):
        covisibility_mask = colmap_data["points3D_image_ids"] == sel_im_in
        covisibility_mask &= valid_uv_mask
        point_mask = (
            covisibility_mask.sum(1) == 1
        )  # only keep points with exactly one observation in the image

        if point_mask.any():
            uv_coords = colmap_data["points3D_points2D_xy"][point_mask][
                covisibility_mask[point_mask]
            ]
            colmap_point_depth = m_project(
                colmap_data["points3D_xyz"][point_mask],
                colmap_data["intrinsic"],
                colmap_world2cam[img_idx],
            )[:, 2]
            pred_point_depth = pred_depths[img_idx][
                tuple(uv_coords[:, [1, 0]].T.long())
            ]
            colmap_point_depths.append(colmap_point_depth)
            pred_point_depths.append(pred_point_depth)
            per_view_scale_factor.append(
                (colmap_point_depth / pred_point_depth.clamp(0.001)).median()
            )
    colmap_point_depths = torch.cat(colmap_point_depths)
    pred_point_depths = torch.cat(pred_point_depths)
    per_view_scale_factor = torch.tensor(per_view_scale_factor)
    wai2metric_scale_factor = float(
        (pred_point_depths / colmap_point_depths.clamp(0.001)).median()
    )
    metric_ate = (wai2metric_scale_factor * ate).to("cpu").item()
    max_metric_ate = cfg.get("max_metric_ate", None)
    if max_metric_ate is not None and metric_ate > max_metric_ate:
        raise RuntimeError(
            f"ATE in metric scale between Colmap and dataset is {format(metric_ate, '.2f')}, "
            f"which bigger then {max_metric_ate} meters, likely faulty Colmap run."
        )

    return wai2metric_scale_factor


def metric_align_scene(cfg, scene_name):
    scene_root = Path(cfg.root) / scene_name
    scene_meta = load_data(scene_root / "scene_meta.json", "scene_meta")
    if not cfg.get("force_running_metric_alignment", False) and scene_meta.get(
        "scale_type"
    ) in ["estimated_metric", "metric"]:
        logger.info(f"Scene {scene_name} already rescaled - skipping to prevent errors")
        return

    wai2metric_scale_factor = colmap_pred_depth_metric_alignment(
        scene_root,
        scene_meta,
        max_num_frames=cfg.max_num_frames,
        device=device,
    )

    apply_metric_alignment(scene_root, scene_meta, wai2metric_scale_factor, "colmap")


if __name__ == "__main__":
    cfg = argconf_parse(WAI_PROC_CONFIG_PATH / "colmap_metric_aligment.yaml")
    if cfg.get("root") is None:
        raise ValueError(
            "Specify the root via: 'python scripts/metric_alignment_colmap.py root=<root_path>'"
        )

    scene_names = get_scene_names(cfg)

    device = cfg.get("device", "cuda")

    for scene_name in tqdm(scene_names, "Processing scenes"):
        logger.info(f"Processing: {scene_name}")
        scene_root = Path(cfg.root) / scene_name
        set_processing_state(scene_root, "metric_alignment_colmap", "running")
        try:
            metric_align_scene(cfg, scene_name)
        except Exception:
            logger.error(f"Conversion failed on scene: {scene_name}")
            trace_message = traceback.format_exc()
            logger.error(trace_message)
            set_processing_state(
                scene_root, "metric_alignment_colmap", "failed", message=trace_message
            )
            continue

        # logging processing state
        set_processing_state(scene_root, "metric_alignment_colmap", "finished")
