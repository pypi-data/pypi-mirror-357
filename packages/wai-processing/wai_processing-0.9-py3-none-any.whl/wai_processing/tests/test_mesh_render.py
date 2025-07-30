from pathlib import Path

import torch
from argconf import argconf_parse
from dvis import dvis
from tqdm import tqdm

from wai import load_data, load_frame
from wai.m_ops import m_unproject
from wai.utils import get_scene_frame_names

cfg = argconf_parse("configs/mesh_render.yaml")
if cfg.get("root") is None:
    cfg.root = "/fsx/normanm/snpp_wai"  # use snpp as reference

cfg.scene_filters.append({"exists": "rendered_depth"})
cfg.scene_filters.append({"exists": "rendered_images"})
scene_frame_names = get_scene_frame_names(cfg)
for scene_name, frame_names in tqdm(scene_frame_names.items()):
    scene_root = Path(cfg.root) / scene_name
    scene_meta = load_data(Path(scene_root, "scene_meta.json"), "scene_meta")
    for frame_name in frame_names[::40]:
        sample = load_frame(
            scene_root, frame_name, ["depth", "rendered_image"], scene_meta
        )
        image = sample["rendered_image"]
        depth = sample["depth"]
        # create global point cloud
        pts3d = m_unproject(depth, sample["intrinsics"], sample["extrinsics"])
        dvis(
            torch.cat([pts3d, image.permute(1, 2, 0).reshape(-1, 3)], -1)[
                depth.flatten() > 0
            ][::20],
            vs=0.02,
            name=f"{scene_name}/{frame_name}",
        )
