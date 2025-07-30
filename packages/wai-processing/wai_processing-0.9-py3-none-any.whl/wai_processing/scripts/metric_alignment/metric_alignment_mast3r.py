import logging
import traceback
from pathlib import Path
from typing import Any

import torch
from argconf import argconf_parse
from tqdm import tqdm
from wai import get_scene_names, load_data, load_frame
from wai.alignment import absolute_trajectory_error
from wai.io import set_processing_state
from wai_processing import WAI_PROC_CONFIG_PATH

from .metric_alignment.metric_alignment_utils import apply_metric_alignment

## Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def mast3r_metric_alignment(
    wai_scene_root: str | Path,
    mast3r_root: str | Path,
    wai_scene_meta: dict[Any, Any],
    device: str,
):
    # Load scene_meta.json from Mast3r output
    mast3r_scene_meta = load_data(mast3r_root / "scene_meta.json", "scene_meta")
    # Sanity check intrinsics
    # TODO: This check assumes shared intrinsics, rewrite check to support per frame intrinsics
    max_focal_length_ratio = cfg.get("max_focal_length_ratio", 1.2)
    if max_focal_length_ratio and (
        wai_scene_meta["fl_x"] / mast3r_scene_meta["fl_x"] > max_focal_length_ratio
        or mast3r_scene_meta["fl_x"] / wai_scene_meta["fl_x"] > max_focal_length_ratio
    ):
        raise RuntimeError(
            "Sanity check failed: The ratio between the focal length of the WAI dataset and the Mast3r prediction"
            f"should not be bigger than {max_focal_length_ratio}. To deactivate this sanity check: 'max_focal_length_ratio=0'"
        )

    mast3r_cam_postions = []
    wai_cam_postions = []
    for mast3r_frame in mast3r_scene_meta["frames"]:
        mast3r_cam_postions.append(
            torch.tensor(mast3r_frame["transform_matrix"])[:3, 3]
        )
        wai_sample = load_frame(
            wai_scene_root,
            frame_key=mast3r_frame["frame_name"],
            modalities=[],
            scene_meta=wai_scene_meta,
        )
        wai_cam_postions.append(wai_sample["extrinsics"][:3, 3])
    mast3r_cam_postions = torch.stack(mast3r_cam_postions).to(device)
    wai_cam_postions = torch.stack(wai_cam_postions).to(device)

    # Master is already in metric scale: Thus we only need to call Umeyama with the Mast3r poses as the GT
    # We get the transform for wai2mast3r, which is wai2metric as long as the Mast3r prediction was correct
    # We only need to use the scale of umeyama as we only care about the metric alignment.
    ate, _, _, transform_dict = absolute_trajectory_error(
        # "Pred" positions are WAI in this case
        wai_cam_postions.unsqueeze(0),
        # Mast3r positions are GT in this case, because we assume that the Mast3r
        # prediction was correctly done in metric scale
        mast3r_cam_postions.unsqueeze(0),
        alignment=True,
        return_transform=True,
    )
    if transform_dict["s"].shape[0] > 1:
        raise RuntimeError(
            "Umeyama alignment only supported with batch size one for now."
        )

    wai2mast3r_scale = transform_dict["s"][0]
    max_metric_ate = cfg.get("max_metric_ate", None)
    if max_metric_ate and wai2mast3r_scale * ate > max_metric_ate:
        raise RuntimeError(
            f"Metric ATE between mast3r and WAI poses is {wai2mast3r_scale * ate} which "
            f"is bigger then threshold of {max_metric_ate} "
            "meters after alignment. Likely the Mast3r inference failed on this scene."
        )

    return wai2mast3r_scale.cpu().item()


def metric_align_scene(cfg, scene_name):
    scene_root = Path(cfg.root) / scene_name
    scene_meta = load_data(scene_root / "scene_meta.json", "scene_meta")
    if not cfg.get("force_running_metric_alignment", False) and scene_meta.get(
        "scale_type"
    ) in ["estimated_metric", "metric"]:
        logger.info(f"Scene {scene_name} already rescaled - skipping to prevent errors")
        return

    wai2metric_scale_factor = mast3r_metric_alignment(
        scene_root,
        scene_root / cfg.get("mast3r_rel_path", "mast3r/v0"),
        scene_meta,
        device=device,
    )

    apply_metric_alignment(scene_root, scene_meta, wai2metric_scale_factor, "mast3r")


if __name__ == "__main__":
    cfg = argconf_parse(WAI_PROC_CONFIG_PATH / "colmap_metric_aligment.yaml")
    if cfg.get("root") is None:
        raise ValueError(
            "Specify the root via: 'python scripts/metric_alignment_mast3r.py root=<root_path>'"
        )

    scene_names = get_scene_names(cfg)

    device = cfg.get("device", "cuda")

    for scene_name in tqdm(scene_names, "Processing scenes"):
        logger.info(f"Processing: {scene_name}")
        scene_root = Path(cfg.root) / scene_name
        set_processing_state(scene_root, "metric_alignment_mast3r", "running")
        try:
            metric_align_scene(cfg, scene_name)
        except Exception:
            logger.error(f"Conversion failed on scene: {scene_name}")
            trace_message = traceback.format_exc()
            logger.error(trace_message)
            set_processing_state(
                scene_root, "metric_alignment_mast3r", "failed", message=trace_message
            )
            continue

        # logging processing state
        set_processing_state(scene_root, "metric_alignment_mast3r", "finished")
