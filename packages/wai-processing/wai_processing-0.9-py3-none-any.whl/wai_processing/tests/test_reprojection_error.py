import logging

# small test to compare reprojection errors using different intrinsics
import torch
from einops import rearrange, repeat

from wai import load_frames
from wai.m_ops import in_image, m_image_sampling, m_project, m_unproject

## Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

scene_root = (
    "/fsx/stuckerc/test_conversion/ase_wai_conversion_undistortion_arialib_dist2depth/0"
)

scene_root = "/fsx/stuckerc/test_conversion/ase_wai_conversion_undistortion_arialib_dist2depth_vrs_intrinsics/0"
frames_data = load_frames(
    scene_root, [f"{idx:07}" for idx in range(0, 50, 1)], ["image", "depth", "mask"]
)
v, c, h, w = frames_data["image"].shape
pts3d = m_unproject(
    frames_data["depth"], frames_data["intrinsics"], frames_data["extrinsics"]
)
pts3d_colored = torch.cat(
    [pts3d, rearrange(frames_data["image"], "v c h w -> v (h w) c")], -1
)
reproj_pts = m_project(
    repeat(pts3d, "v n c -> v1 (v n) c", v1=v),
    frames_data["intrinsics"],
    frames_data["extrinsics"].inverse(),
)  # <target_frame> x [all world pts] x [i,j,depth]
target_src_reproj_pts = rearrange(reproj_pts, "t (s n) c -> t s n c", s=v)
valid_mask = in_image(reproj_pts, h, w, min_depth=0.1)
target_depth_values, target_depth_masks = m_image_sampling(
    frames_data["depth"].unsqueeze(-3),
    reproj_pts,
    "nearest",
    min_depth=0.1,
)
target_src_depths, target_src_masks = (
    rearrange(target_depth_values[..., 0], "t (s n) -> t s n", s=v),
    rearrange(target_depth_masks, "t (s n)-> t s n", s=v),
)


depth_reproj_errors = []
image_reproj_errors = []
for src_idx in range(v):
    for target_idx in range(v):
        if src_idx == target_idx:
            continue
        src_target_proj_depth = torch.zeros(h, w)
        src_target_proj_depth[
            tuple(
                target_src_reproj_pts[target_idx, src_idx, :, :2][
                    target_src_masks[target_idx, src_idx]
                ]
                .round()
                .clamp(1, h - 1)
                .int()
                .T
            )
        ] = target_src_depths[target_idx, src_idx][
            target_src_masks[target_idx, src_idx]
        ]
        src_target_proj_img = torch.zeros(h, w, 3)
        src_target_proj_img[
            tuple(
                target_src_reproj_pts[target_idx, src_idx, :, :2][
                    target_src_masks[target_idx, src_idx]
                ]
                .round()
                .clamp(1, h - 1)
                .int()
                .T
            )
        ] = rearrange(frames_data["image"][src_idx], "c h w -> (h w) c")[
            target_src_masks[target_idx, src_idx]
        ]
        src_target_valid_mask = (frames_data["depth"][target_idx] > 0) & (
            src_target_proj_depth > 0
        )
        # filter out occluded areas

        src_target_depth_reproj_err_unmasked = torch.abs(
            frames_data["depth"][target_idx] - src_target_proj_depth
        )
        src_target_image_reproj_err_unmasked = torch.abs(
            frames_data["image"][target_idx].permute(1, 2, 0) - src_target_proj_img
        ).mean(-1)
        src_target_valid_mask &= src_target_depth_reproj_err_unmasked < 0.3
        if src_target_valid_mask.any():
            src_target_depth_reproj_error = src_target_depth_reproj_err_unmasked[
                src_target_valid_mask
            ].mean()
            src_target_image_reproj_err_zeroed = (
                src_target_image_reproj_err_unmasked.clone()
            )
            src_target_image_reproj_err_zeroed[~src_target_valid_mask] = 0

            src_target_image_reproj_err = src_target_image_reproj_err_unmasked[
                src_target_valid_mask
            ].mean()
            depth_reproj_errors.append(src_target_depth_reproj_error)
            image_reproj_errors.append(src_target_image_reproj_err)
logger.info(f"Average depth error: {torch.stack(depth_reproj_errors).mean().item()}")
logger.info(f"Average image error: {torch.stack(image_reproj_errors).mean().item()}")
