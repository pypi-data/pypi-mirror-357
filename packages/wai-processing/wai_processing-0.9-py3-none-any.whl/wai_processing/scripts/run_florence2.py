import logging
import os
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
from wai_processing import WAI_PROC_CONFIG_PATH

from .model_wrapper.florence2 import (
    get_caption,
    load_model,
    load_processor,
)

CAPTION_MODES = {
    "caption": "<CAPTION>",
    "detailed_caption": "<DETAILED_CAPTION>",
    "more_detailed_caption": "<MORE_DETAILED_CAPTION>",
}

## Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def run_florence2_on_scene(
    cfg, scene_name, model, processor, torch_dtype, overwrite=False
):
    """
    Processes a single scene to generate captions for each frame using the Florence2 model.
    Parameters:
    cfg (Config): Configuration object containing settings.
    scene_name (str): The name of the scene to be processed.
    model (AutoModelForCausalLM): Florence-2 model
    processor (AutoProcessor): Florence-2 processor
    torch_dtype (torch.dtype): The data type for the model's parameters (e.g., torch.float32, torch.float16).
    overwrite (bool): If True, existing outputs will be overwritten. Defaults to False.
    Returns:
    None
    """
    # Create a dataloader that only parses a single scene.
    # This ensures that every loaded frame belongs to this scene.
    cfg.scene_filters = [scene_name]
    scene_root = Path(cfg.root) / scene_name
    scene_meta = load_data(Path(scene_root, "scene_meta.json"), "scene_meta")
    caption_mode = CAPTION_MODES[cfg.caption_mode]
    single_scene_dataset = BasicSceneframeDataset(cfg)
    dataloader = DataLoader(
        single_scene_dataset,
        cfg.batch_size,
        collate_fn=single_scene_dataset.collate_fn,
        shuffle=False,
        drop_last=False,
    )

    # Delete previous generation
    out_path = scene_root / cfg.out_path
    if out_path.exists():
        if overwrite:
            shutil.rmtree(out_path)

    caption_model_id = f"florence-2-large_{cfg.caption_mode}"
    caption_path = out_path / f"{caption_model_id}.json"
    if caption_path.exists() and overwrite:
        os.remove(caption_path)

    captions = {}
    for batch in tqdm(dataloader, f"Predicting Florence2 ({scene_name})"):
        # TODO: check if this is worth to control the normalization on BasicSceneframeDataset.
        images = batch["image"] * 255.0
        batch_captions = get_caption(
            images,
            caption_mode,
            model,
            processor,
            cfg.device,
            torch_dtype,
            cfg.max_new_tokens,
        )
        for i, caption in enumerate(batch_captions):
            frame_name = batch["frame_name"][i]
            captions[frame_name] = caption[CAPTION_MODES[cfg.caption_mode]].replace(
                "<pad>", ""
            )
            # Update frame scene_meta
            frame = get_frame(scene_meta, frame_name)
            frame[caption_model_id] = f"{cfg.out_path}/{caption_model_id}.json"
            set_frame(scene_meta, frame_name, frame, sort=True)
    # Store caption file. it's important to keep the 'readable' here and not the 'caption' since we store the whole dict at once !
    # as opposed to store captions one by one and do many IO operations (which is possible with the caption format if needed)
    store_data(caption_path, captions, "readable")
    # Update frame_modalities
    frame_modalities = scene_meta["frame_modalities"]
    frame_modalities_caption = frame_modalities.get("caption", {})
    frame_modalities_caption[caption_model_id] = {
        "frame_key": caption_model_id,
        "format": "caption",
    }
    frame_modalities["caption"] = frame_modalities_caption
    scene_meta["frame_modalities"] = frame_modalities
    # Store new scene_meta
    store_data(scene_root / "scene_meta.json", scene_meta, "scene_meta")


if __name__ == "__main__":
    import sys

    logger.debug("Command line arguments:")
    for i, arg in enumerate(sys.argv):
        logger.debug(f"  [{i}]: {arg}")

    cfg = argconf_parse(WAI_PROC_CONFIG_PATH / "florence2/default.yaml")
    if cfg.get("root") is None:
        raise ValueError(
            "Specify the root via: 'python scripts/run_florence2.py root=<root_path>'"
        )

    logger.info("Running Florence-2 using config:")
    for key, value in dict(cfg).items():
        logger.info(f"  {key}: {value}")

    scene_frame_names = get_scene_frame_names(cfg)

    torch_dtype = torch.float16
    model_path = Path(cfg.model_path) / "model"
    processor_path = Path(cfg.model_path) / "processor"
    model = load_model(model_path, cfg.device, torch_dtype)
    processor = load_processor(processor_path)
    logger.info(f"Processing: {len(scene_frame_names)} scenes")
    logger.debug(f"scene_frame_names = {scene_frame_names}")

    for scene_name in tqdm(scene_frame_names, "Processing scenes"):
        logger.info(f"Processing: {scene_name}")
        scene_root = Path(cfg.root) / scene_name
        set_processing_state(scene_root, "florence2", "running")
        try:
            run_florence2_on_scene(cfg, scene_name, model, processor, torch_dtype)
            set_processing_state(scene_root, "florence2", "finished")
        except Exception:
            logger.error(f"Running florence2 failed on scene '{scene_name}'")
            trace_message = traceback.format_exc()
            logger.error(trace_message)
            set_processing_state(
                scene_root, "florence2", "failed", message=trace_message
            )
            continue
