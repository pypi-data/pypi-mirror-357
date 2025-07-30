from pathlib import Path

import torch
from argconf import argconf_parse
from dvis import dvis
from torch.nn import functional as F
from tqdm import tqdm

from wai import load_data, load_frame
from wai.utils import get_scene_frame_names
from wai.m_ops import m_unproject

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
for scene_name, frame_names in tqdm(scene_frame_names.items()):
    scene_root = Path(cfg.root) / scene_name
    scene_meta = load_data(Path(scene_root, "scene_meta.json"), "scene_meta")
    for frame_name in frame_names[::30]:
        sample = load_frame(scene_root, frame_name, ["image", "pred_depth"], scene_meta)
        image = sample["image"]
        # depth is stored at a different resolution
        depth = F.interpolate(
            sample["pred_depth"][None, ...],
            size=(sample["h"], sample["w"]),
            mode="nearest",
        )[0]
        # create global point cloud
        pts3d = m_unproject(depth, sample["intrinsics"], sample["extrinsics"])
        dvis(
            torch.cat([pts3d, image.permute(1, 2, 0).reshape(-1, 3)], -1),
            vs=0.04,
            name=f"{scene_name}/{frame_name}",
            ms=200000,
        )
