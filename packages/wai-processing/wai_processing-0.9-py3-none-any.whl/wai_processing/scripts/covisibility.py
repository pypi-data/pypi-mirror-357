import logging
import math
import shutil
import traceback
from pathlib import Path

import torch
import torch.nn.functional as F
from argconf import argconf_parse
from einops import einsum, repeat
from torch.utils.data import DataLoader
from tqdm import tqdm
from wai import (
    BasicSceneframeDataset,
    get_scene_names,
    load_data,
    store_data,
)
from wai.intersection_check import (
    create_frustum_from_intrinsics,
    frustum_intersection_check,
)
from wai.io import set_processing_state
from wai.m_ops import in_image, m_dot, m_project, m_unproject
from wai.ops import resize

## Set up basic logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("covisibility")


def compute_covisibility(cfg, scene_name: str, overwrite=False):
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

    depths = []
    depth_h = 0
    depth_w = 0
    valid_depth_masks = []
    intrinsics = []
    cam2worlds = []
    world_pts3d = []

    # Load cameras and depth maps for all frames.
    for batch in tqdm(dataloader, f"Loading depth maps ({scene_name})"):
        depth = batch["depth"].to(device)  # ensure correct key remapping in config
        # Check for depth confidence values if available
        depth_confidences = batch.get("depth_confidence")
        if depth_confidences is not None:
            depth_confidences = depth_confidences.to(device)

        # Validate configuration parameters
        if (
            cfg.get("downscale_factor") is not None
            and cfg.get("target_size") is not None
        ):
            raise ValueError("Either set downscale_factor or target_size, not both.")

        # Determine scaling parameters
        scale, size = None, None
        if cfg.get("downscale_factor") is not None and cfg.downscale_factor > 1:
            scale = 1 / cfg.downscale_factor
        elif cfg.get("target_size"):
            size = cfg.target_size  # Rescale to a fixed resolution

        # Rescale depth maps if needed
        if scale or size:
            depth = resize(depth, scale=scale, size=size, modality_format="depth")
            if depth_confidences is not None:
                depth_confidences = resize(
                    depth_confidences,
                    scale=scale,
                    size=size,
                    modality_format="depth",
                )

        # Ensure consistent depth map dimensions
        if depth_h == 0 and depth_w == 0:
            depth_h, depth_w = depth.shape[-2:]
        elif depth_h != depth.shape[-2] or depth_w != depth.shape[-1]:
            raise ValueError("Depth resolutions vary, set target_size in the config")

        # Create mask for valid depth values
        valid_depth_mask = depth > 0
        if depth_confidences is not None:
            valid_depth_mask &= depth_confidences > cfg.depth_confidence_thresh

        # Calculate scaling factors for intrinsics
        scale_h = depth_h / torch.tensor(batch["h"])
        scale_w = depth_w / torch.tensor(batch["w"])

        # Adjust intrinsics for the scaled depth maps
        depth_intrinsics = torch.clone(batch["intrinsics"])
        depth_intrinsics[:, :1] *= scale_w[:, None, None]
        depth_intrinsics[:, 1:2] *= scale_h[:, None, None]

        # Unproject the depth to 3D points
        depth_intrinsics = depth_intrinsics.to(device)
        curr_batch_cam2worlds = batch["extrinsics"].to(device)
        curr_batch_world_pts3d = m_unproject(
            depth,
            depth_intrinsics,
            curr_batch_cam2worlds,
        )

        # Store processed data
        depths.append(depth)
        valid_depth_masks.append(valid_depth_mask)
        intrinsics.append(depth_intrinsics)
        cam2worlds.append(curr_batch_cam2worlds)
        list_curr_batch_world_pts3d = list(
            torch.unbind(curr_batch_world_pts3d.cpu(), dim=0)
        )
        world_pts3d.extend(
            list_curr_batch_world_pts3d
        )  # Keep on CPU to save GPU memory

    depths = torch.cat(depths)  # <num_frames> x H x W
    intrinsics = torch.cat(intrinsics)  # <num_frames> x 3 x 3
    cam2worlds = torch.cat(cam2worlds)  # <num_frames> x 4 x 4
    valid_depth_masks = torch.cat(valid_depth_masks)  # <num_frames> x H x W

    num_frames = depths.shape[0]
    assert intrinsics.shape[0] == num_frames, (
        f"First dim of concatentated intrinsics {intrinsics.shape[0]} doesn't match with expected num of frames: {num_frames}"
    )
    assert cam2worlds.shape[0] == num_frames, (
        f"First dim of concatentated extrinsics {cam2worlds.shape[0]} doesn't match with expected num of frames: {num_frames}"
    )
    assert valid_depth_masks.shape[0] == num_frames, (
        f"First dim of concatentated valid depth masks doesn't match with expected num of frames: {num_frames}"
    )
    assert len(world_pts3d) == num_frames, (
        f"Length of list containing 3d points in world frame {len(world_pts3d)} doesn't match with expected num of frames: {num_frames}"
    )

    if cfg.get("perform_frustum_check", True):
        # Frustum check
        near_vals = torch.tensor(
            [
                depth[valid_mask].min() if valid_mask.any() else torch.tensor(0)
                for depth, valid_mask in zip(depths, valid_depth_masks)
            ]
        ).to(device)
        far_vals = torch.tensor(
            [
                depth[valid_mask].max() if valid_mask.any() else torch.tensor(0)
                for depth, valid_mask in zip(depths, valid_depth_masks)
            ]
        ).to(device)
        frustums = create_frustum_from_intrinsics(intrinsics, near_vals, far_vals)
        frustums_homog = torch.cat(
            [frustums, torch.ones_like(frustums[:, :, :1])], dim=-1
        )
        frustums_world = einsum(cam2worlds, frustums_homog, "b i k, b v k -> b v i")
        frustums_world = frustums_world[:, :, :3]

        # Compute batched frustum intersection check
        frustum_intersection = frustum_intersection_check(
            frustums_world, chunk_size=500, device=device
        )

        # Free up memory by removing unneeded tensors
        del frustums, frustums_homog, frustums_world, near_vals, far_vals
        torch.cuda.empty_cache()

    # Loop over all the views to compute the pairwise overlap
    pairwise_covisibility = torch.zeros((num_frames, num_frames), device="cpu")
    logger.info("Computing pairwise overlap for each view ...")

    # Process in chunks to avoid OOM
    for idx in tqdm(
        range(num_frames),
        f"Computing exhaustive pairwise covisibility for each view ({scene_name})",
    ):
        # Get the remaining views which pass the frustum intersection check
        if cfg.get("perform_frustum_check", True):
            ov_inds = frustum_intersection[idx].argwhere()[:, 0].to(device)
        else:
            ov_inds = torch.arange(num_frames).to(device)
        if len(ov_inds) == 0:
            continue

        # Process overlapping views in sub-chunks if needed
        overlap_score = torch.zeros((num_frames,), device="cpu")
        ov_chunk_size = 4000
        for ov_start in range(0, len(ov_inds), ov_chunk_size):
            ov_end = min(ov_start + ov_chunk_size, len(ov_inds))
            ov_inds_chunk = ov_inds[ov_start:ov_end]
            v_rem = len(ov_inds_chunk)
            if v_rem == 0:
                continue

            # Project the depth map v into all the overlapping views in this chunk
            view_cam_pts3d = m_dot(
                torch.inverse(cam2worlds[ov_inds_chunk]),
                repeat(world_pts3d[idx].to(device), "... -> V ...", V=v_rem),
            )
            reprojected_pts = m_project(
                view_cam_pts3d, intrinsics[ov_inds_chunk]
            ).reshape(v_rem, depth_h, depth_w, 3)

            # Filter out points which are outside the image boundaries
            valid_mask = (
                in_image(reprojected_pts, depth_h, depth_w, min_depth=0.04)
                & valid_depth_masks[idx]
            )

            # If any points are valid, compute the covisibility
            if valid_mask.any():
                normalized_pts = (
                    2
                    * reprojected_pts[..., [1, 0]]
                    / torch.tensor([depth_w - 1, depth_h - 1], device=device)
                    - 1
                )
                normalized_pts = torch.clamp(normalized_pts, min=-1.0, max=1.0)
                depth_lu = F.grid_sample(
                    depths[ov_inds_chunk].unsqueeze(1),
                    normalized_pts,
                    mode="nearest",
                    align_corners=True,
                )[:, 0]
                expected_depth = reprojected_pts[..., 2]
                reprojection_error = torch.abs(expected_depth - depth_lu)
                depth_assoc_thres = (
                    cfg.depth_assoc_error_thres
                    + cfg.depth_assoc_rel_error_thres * expected_depth
                    - math.log(0.5) * cfg.depth_assoc_error_temp
                )
                valid_depth_projection = (
                    reprojection_error < depth_assoc_thres
                ) & valid_mask
                if cfg.denominator_mode == "valid_target_depth":
                    # divide by the number of valid depth points in the target view
                    comp_covisibility_score = valid_depth_projection.sum(
                        [1, 2]
                    ) / valid_depth_masks[ov_inds_chunk].sum([1, 2]).clamp(1)
                    comp_covisibility_score = comp_covisibility_score.clamp(
                        0, 1
                    )  # in case in the target view there more valid depth points than in the source view
                elif cfg.denominator_mode == "full":
                    # divide by the total number of pixels
                    comp_covisibility_score = valid_depth_projection.sum([1, 2]) / (
                        depth_h * depth_w
                    )
                else:
                    raise NotImplementedError(
                        f"denominator_mode not supported: {cfg.denominator_mode}"
                    )
                overlap_score[ov_inds_chunk.cpu()] = comp_covisibility_score.cpu()

        # Update the pairwise overlap matrix
        pairwise_covisibility[idx] = overlap_score

        # Free memory
        torch.cuda.empty_cache()

    mmap_store_name = store_data(
        scene_root / cfg.out_path / "pairwise_covisibility.npy",
        pairwise_covisibility,
        "mmap",
    )

    # Update the scene meta
    scene_modalities = scene_meta["scene_modalities"]
    scene_modalities["pairwise_covisibility"] = {
        "scene_key": f"{cfg.out_path}/{mmap_store_name}",
        "format": "mmap",
    }
    store_data(scene_root / "scene_meta.json", scene_meta, "scene_meta")


if __name__ == "__main__":
    import sys

    logger.debug("Command line arguments:")
    for i, arg in enumerate(sys.argv):
        logger.debug(f"  [{i}]: {arg}")

    cfg = argconf_parse()
    if cfg.get("root") is None:
        raise ValueError(
            "Specify the root via: 'python scripts/covisibility.py root=<root_path>'"
        )
    if cfg.get("frame_modalities") is None:
        raise ValueError("Specify the modality to use for depth in frame_modalities'")

    logger.info("Running covisibility using config:")
    for key, value in dict(cfg).items():
        logger.info(f"  {key}: {value}")

    overwrite = cfg.get("overwrite", False)
    if overwrite:
        logger.warning("Careful: Overwrite enabled!")

    device = cfg.get("device", "cuda")
    scene_names = get_scene_names(cfg)
    logger.info(f"processing: {len(scene_names)} scenes")
    logger.debug(f"scene_names = {scene_names}")

    for scene_name in tqdm(scene_names, "Processing scenes"):
        logger.info(f"Processing: {scene_name}")
        scene_root = Path(cfg.root) / scene_name
        set_processing_state(scene_root, "covisibility", "running")
        try:
            compute_covisibility(cfg, scene_name, overwrite=overwrite)
            set_processing_state(scene_root, "covisibility", "finished")
        except Exception:
            logging.error(f"Computing covisibility failed on scene '{scene_name}'")
            trace_message = traceback.format_exc()
            logger.error(trace_message)
            set_processing_state(
                scene_root, "covisibility", "failed", message=trace_message
            )
            continue
