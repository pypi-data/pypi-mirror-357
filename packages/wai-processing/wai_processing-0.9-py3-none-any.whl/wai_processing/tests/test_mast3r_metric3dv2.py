from pathlib import Path

import numpy as np
import torch
from argconf import argconf_parse
from dvis import dvis
from tqdm import tqdm
from wai import load_data, load_frame, load_scene
from wai.conversion import resize
from wai.m_ops import m_unproject
from wai.utils import get_scene_names
from wai_processing import WAI_PROC_CONFIG_PATH

cfg = argconf_parse(WAI_PROC_CONFIG_PATH / "metric3dv2/default.yaml")
cfg.root = "/fsx/nelsonantunes/dryrun/re10k"

# TODO: Proposal to remove these tests from the current script and add them in a separate one.
# here we should only import tests, not define them:
# https://ghe.oculus-rep.com/mb-research/wai/pull/6#discussion_r30881
cfg.scene_filters = []
scene_names = get_scene_names(cfg)
for scene_name in tqdm(scene_names):
    scene_root = Path(cfg.root) / scene_name
    master_scene_root = Path(scene_root, "mast3r", "v0")
    scene_meta = load_data(Path(scene_root, "scene_meta.json"), "scene_meta")
    master_scene_meta = load_data(master_scene_root / "scene_meta.json", "scene_meta")
    frame_names = [frame["frame_name"] for frame in scene_meta["frames"]]
    mast3r_frame_names = [frame["frame_name"] for frame in master_scene_meta["frames"]]
    mast3r_scene_data = load_scene(
        master_scene_root, scene_modalities=["gt_pts3d", "global_pts3d_colors"]
    )
    # mast3r global point cloud
    dvis(
        np.concatenate(
            [mast3r_scene_data["gt_pts3d"], mast3r_scene_data["global_pts3d_colors"]],
            -1,
        ),
        vs=0.01,
        name=f"mast3r_{scene_name}/global_pts3d",
        ms=100000,
        l=2,
    )
    for frame_name in mast3r_frame_names[::4]:
        sample = load_frame(
            scene_root,
            frame_name,
            ["image", "pred_depth", "depth_confidence"],
            scene_meta,
        )
        image = sample["image"]
        # depth is stored at a different resolution
        depth = resize(
            sample["pred_depth"],
            size=(sample["h"], sample["w"]),
            modality_format="depth",
        )
        depth_confidence = resize(
            sample["depth_confidence"],
            size=(sample["h"], sample["w"]),
            modality_format="depth",
        )
        mast3r_sample = load_frame(
            master_scene_root,
            frame_name,
            ["image", "pred_depth", "depth_confidence"],
            master_scene_meta,
        )
        image = mast3r_sample["image"]
        # depth is stored at a different resolution
        mast3r_depth = resize(
            mast3r_sample["pred_depth"],
            size=(mast3r_sample["h"], mast3r_sample["w"]),
            modality_format="depth",
        )
        mast3r_depth_confidence = resize(
            mast3r_sample["depth_confidence"],
            size=(mast3r_sample["h"], mast3r_sample["w"]),
            modality_format="depth",
        )

        # create global point cloud
        pts3d = m_unproject(
            depth, mast3r_sample["intrinsics"], mast3r_sample["extrinsics"]
        )
        mast3r_pts3d = m_unproject(
            mast3r_depth, mast3r_sample["intrinsics"], mast3r_sample["extrinsics"]
        )
        dvis(
            torch.cat([pts3d, image.permute(1, 2, 0).reshape(-1, 3)], -1)[
                depth_confidence.flatten() > 0.97
            ],
            vs=0.05,
            name=f"{scene_name}/{frame_name}",
            ms=100000,
            l=1,
        )
        dvis(
            torch.cat([mast3r_pts3d, image.permute(1, 2, 0).reshape(-1, 3)], -1)[
                mast3r_depth_confidence.flatten() > 1.5
            ],
            vs=0.05,
            name=f"mast3r_{scene_name}/{frame_name}",
            ms=100000,
            l=2,
        )
