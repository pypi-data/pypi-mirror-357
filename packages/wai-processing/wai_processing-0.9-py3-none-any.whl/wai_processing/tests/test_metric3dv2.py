from pathlib import Path

import torch
from argconf import argconf_parse
from dvis import dvis
from torch.nn import functional as F
from tqdm import tqdm

from wai import load_data, load_frame
from wai.utils import get_scene_frame_names
from wai.m_ops import m_unproject

cfg = argconf_parse("configs/metric3dv2.yaml")
if cfg.get("root") is None:
    cfg.root = "/fsx/normanm/snpp_wai"  # use snpp as reference

cfg.scene_filters = [
    {"process_state": ["metric3dv2", "finished"]}
]  # ensure metric3dv2 run successful
scene_frame_names = get_scene_frame_names(cfg)
for scene_name, frame_names in tqdm(scene_frame_names.items()):
    scene_root = Path(cfg.root) / scene_name
    scene_meta = load_data(Path(scene_root, "scene_meta.json"), "scene_meta")
    for frame_name in frame_names[::50]:
        sample = load_frame(
            scene_root,
            frame_name,
            ["image", "pred_depth", "depth_confidence"],
            scene_meta,
        )
        image = sample["image"]
        # depth is stored at a different resolution
        depth = F.interpolate(
            sample["pred_depth"][None, ...],
            size=(sample["h"], sample["w"]),
            mode="nearest",
        )[0]
        depth_confidence = F.interpolate(
            sample["depth_confidence"][None, ...],
            size=(sample["h"], sample["w"]),
            mode="nearest",
        )[0]
        # create global point cloud
        pts3d = m_unproject(depth, sample["intrinsics"], sample["extrinsics"])
        dvis(
            torch.cat([pts3d, image.permute(1, 2, 0).reshape(-1, 3)], -1)[
                depth_confidence.flatten() > 0.97
            ],
            vs=0.05,
            name=f"{scene_name}/{frame_name}",
            ms=100000,
        )
