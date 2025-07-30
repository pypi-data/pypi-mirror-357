import logging
import shutil
import traceback
from pathlib import Path

import torch
from argconf import argconf_parse
from torch.utils.data import DataLoader
from tqdm import tqdm
from wai import (
    BasicSceneframeDataset,
    get_frame,
    get_scene_frame_names,
    load_data,
    set_frame,
    store_data,
)
from wai.io import set_processing_state
from wai.ops import stack
from wai_processing import WAI_PROC_CONFIG_PATH

from .model_wrapper.metric3Dv2 import get_depth_batch, load_model

## Set up basic logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("metric3dv2")


def run_metric3dv2_on_scene(cfg, scene_name: str, overwrite=False):
    # Create a dataloader that only parses a single scene.
    # This ensures that every loaded frame belongs to this scene.
    cfg.scene_filters = [scene_name]
    scene_root = Path(cfg.root) / scene_name
    scene_meta = load_data(Path(scene_root, "scene_meta.json"), "scene_meta")
    single_scene_dataset = BasicSceneframeDataset(cfg)
    dataloader = DataLoader(
        single_scene_dataset,
        cfg.batch_size,
        collate_fn=single_scene_dataset.collate_fn,
        shuffle=False,
        num_workers=cfg.num_workers,
        drop_last=False,
    )

    # Delete previous generation
    out_path = scene_root / cfg.out_path
    if out_path.exists():
        if overwrite:
            shutil.rmtree(out_path)

    # Iterate over all images and perform depth/normal estimation.
    for batch in tqdm(dataloader, f"Predicting Metric3Dv2 ({scene_name})"):
        batch_size = len(batch["frame_name"])
        if all(
            [
                torch.all(batch["intrinsics"][b] == batch["intrinsics"][0])
                for b in range(batch_size)
            ]
        ):
            # same intrinsics -> we can batch it
            fx, fy, cx, cy = (
                batch["intrinsics"][0, 0, 0],
                batch["intrinsics"][0, 1, 1],
                batch["intrinsics"][0, 0, 2],
                batch["intrinsics"][0, 1, 2],
            )
            images = batch["image"]
            pred_depth, confidence, pred_normal, normal_confidence = get_depth_batch(
                model, images, fx, fy, cx, cy, resize_to_orig_size=False
            )
        else:
            outputs = []
            for b in range(batch_size):
                fx, fy, cx, cy = (
                    batch["intrinsics"][b, 0, 0],
                    batch["intrinsics"][b, 1, 1],
                    batch["intrinsics"][b, 0, 2],
                    batch["intrinsics"][b, 1, 2],
                )
                images = batch["image"][b].unsqueeze(0)
                output = get_depth_batch(
                    model, images, fx, fy, cx, cy, resize_to_orig_size=False
                )
                outputs.append(output)

            # Use nested tensor as the output can be of different size
            pred_depth, confidence, pred_normal, normal_confidence = stack(
                [
                    [output[i].squeeze(0) for output in outputs]
                    for i in range(batch_size)
                ]
            )

        # Store outputs
        for b in range(batch_size):
            frame_name = batch["frame_name"][b]
            rel_depth_path = f"depth/{frame_name}.exr"
            rel_depth_confidence_path = f"depth_confidence/{frame_name}.exr"
            rel_normals_path = f"normals/{frame_name}.exr"
            rel_normal_confidences_path = f"normal_confidence/{frame_name}.exr"
            store_data(out_path / rel_depth_path, pred_depth[b], "depth")
            store_data(out_path / rel_depth_confidence_path, confidence[b], "scalar")
            store_data(
                out_path / rel_normals_path, pred_normal[b].permute(1, 2, 0), "normals"
            )
            store_data(
                out_path / rel_normal_confidences_path, normal_confidence[b], "scalar"
            )

            # Update frame scene_meta
            frame = get_frame(scene_meta, frame_name)
            frame["metric3dv2_depth"] = f"{cfg.out_path}/{rel_depth_path}"
            frame["metric3dv2_depth_confidence"] = (
                f"{cfg.out_path}/{rel_depth_confidence_path}"
            )
            frame["metric3dv2_normals"] = f"{cfg.out_path}/{rel_normals_path}"
            frame["metric3dv2_normal_confidence"] = (
                f"{cfg.out_path}/{rel_normal_confidences_path}"
            )
            set_frame(scene_meta, frame_name, frame, sort=True)

    # Update frame_modalities
    frame_modalities = scene_meta["frame_modalities"]
    frame_modalities["pred_depth"] = {
        "frame_key": "metric3dv2_depth",
        "format": "depth",
    }
    frame_modalities["depth_confidence"] = {
        "frame_key": "metric3dv2_depth_confidence",
        "format": "scalar",
    }
    frame_modalities["pred_normals"] = {
        "frame_key": "metric3dv2_normals",
        "format": "normals",
    }
    frame_modalities["normal_confidence"] = {
        "frame_key": "metric3dv2_normal_confidence",
        "format": "scalar",
    }
    scene_meta["frame_modalities"] = frame_modalities

    # Store new scene_meta
    store_data(scene_root / "scene_meta.json", scene_meta, "scene_meta")


if __name__ == "__main__":
    import sys

    logger.debug("Command line arguments:")
    for i, arg in enumerate(sys.argv):
        logger.debug(f"  [{i}]: {arg}")

    cfg = argconf_parse(WAI_PROC_CONFIG_PATH / "metric3dv2/default.yaml")
    if cfg.get("root") is None:
        raise ValueError(
            "Specify the root via: 'python scripts/run_metric3dv2.py root=<root_path>'"
        )

    logger.info("Running Metric3Dv2 using config:")
    for key, value in dict(cfg).items():
        logger.info(f"  {key}: {value}")

    overwrite = cfg.get("overwrite", False)
    if overwrite:
        logger.warning("Careful: Overwrite enabled!")

    scene_frame_names = get_scene_frame_names(cfg)

    model = load_model(cfg.model_path, cfg.ckpt_path, device="cuda")
    logger.info(f"Processing: {len(scene_frame_names)} scenes")
    logger.debug(f"scene_frame_names = {scene_frame_names}")
    for scene_name in tqdm(scene_frame_names, "Processing scenes"):
        logger.info(f"Processing: {scene_name}")
        scene_root = Path(cfg.root) / scene_name
        set_processing_state(scene_root, "metric3dv2", "running")
        try:
            run_metric3dv2_on_scene(cfg, scene_name, overwrite=overwrite)
            set_processing_state(scene_root, "metric3dv2", "finished")
        except Exception:
            logger.error(f"Running metric3dv2 failed on scene '{scene_name}'")
            trace_message = traceback.format_exc()
            logger.error(trace_message)
            set_processing_state(
                scene_root, "metric3dv2", "failed", message=trace_message
            )
            continue
