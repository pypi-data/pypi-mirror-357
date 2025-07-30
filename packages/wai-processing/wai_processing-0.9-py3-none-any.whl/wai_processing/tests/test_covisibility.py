from pathlib import Path

import numpy as np
from argconf import argconf_parse
from dvis import dvis
from tqdm import tqdm

from wai import load_data, load_frame, load_scene
from wai.utils import get_scene_frame_names

cfg = argconf_parse("configs/colmap_metric_aligment.yaml")
if cfg.get("root") is None:
    cfg.root = "/fsx/normanm/dl3dv_10k_wai"  # use dl3dv as reference

cfg.scene_filters = [
    {"process_state": ("metric_alignment", "finished")}
]  # ensure metric alignment was performed
cfg.scene_filters += [
    ["006771db3c057280f9277e735be6daa24339657ce999216c38da68002a443fed"]
]  # basketball court
scene_frame_names = get_scene_frame_names(cfg)

for scene_name in tqdm(scene_frame_names, "Processing scenes"):
    scene_root = Path(cfg.root) / scene_name
    scene_meta = load_data(Path(scene_root, "scene_meta.json"), "scene_meta")
    scene_data = load_scene(
        scene_root, scene_modalities="pairwise_covisibility", scene_meta=scene_meta
    )
    pairwise_covisibility = scene_data["pairwise_covisibility"]
    num_frames = len(scene_meta["frames"])
    next_idx = 0
    visited_inds = [next_idx]
    # visit
    for _ in range(num_frames):
        sample = load_frame(scene_root, next_idx, modalities="image")
        img = sample["image"]
        dvis(img.unsqueeze(0), "seq", s=400, name=f"{scene_name}")
        covis = np.copy(pairwise_covisibility[next_idx])
        covis[visited_inds] = 0
        next_idx = int(np.argmax(covis))
        visited_inds.append(next_idx)
