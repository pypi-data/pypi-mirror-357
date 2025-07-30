import logging
import os
import shutil
import tempfile
import time
import traceback
from pathlib import Path

import cv2
import numpy as np
import rerun as rr
from argconf import argconf_parse
from tqdm import tqdm
from wai import load_data, store_data
from wai.io import set_processing_state
from wai.scripts.model_wrapper.mast3r import (
    get_scene_and_corres,
    load_mast3r,
)
from wai.utils import get_scene_frame_names
from wai_processing import WAI_PROC_CONFIG_PATH

## Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def filter_filelist(filelist, keep_percentage=0.1, max_size=None, min_size=5):
    """
    Reduce the size of a list by keeping a specified percentage of elements while ensuring the result size is at least a certain minimum.
    Args:
        filelist (list): The list to be reduced.
        keep_percentage (float): The percentage of elements to keep. Must be between 0 and 1.
        min_size (int): The minimum size of the reduced list.
        max_size (int): The maximum size of the reduced list.
    Returns:
        list: The reduced list or the original list if the reduced list is smaller than the minimum size.
    """
    if not 0 <= keep_percentage <= 1:
        raise ValueError("Keep percentage must be between 0 and 1")
    num_elements_to_keep = int(len(filelist) * keep_percentage)
    if num_elements_to_keep < min_size:
        num_elements_to_keep = min_size
    if max_size is not None and num_elements_to_keep > max_size:
        num_elements_to_keep = max_size
    # Calculate the step size for sampling, in case len(filelist) is too small, we keep everything
    step_size = max(1, len(filelist) // num_elements_to_keep)
    # Sample the list using the calculated step size
    return filelist[::step_size]


def run_mast3r_on_scene(cfg, scene_name, model, overwrite, **kwargs):
    """
    Run MAST3R on a given scene.
    Args:
        cfg (dict): Configuration dictionary.
        scene_name (str): Name of the scene to process.
        model: Model to use for processing.
        overwrite (bool): Whether to overwrite existing output.
        **kwargs: Additional keyword arguments.
    Returns:
        None
    """
    from mast3r.cloud_opt.sparse_ga import to_numpy

    cfg.scene_filters = [scene_name]
    scene_root = Path(cfg.root) / scene_name
    scene_meta = load_data(Path(scene_root, "scene_meta.json"), "scene_meta")
    wai_frames = []
    scene_frame_names = get_scene_frame_names(cfg)[scene_name]

    # Delete previous generation
    out_path = scene_root / cfg.out_path
    if out_path.exists() and overwrite:
        shutil.rmtree(out_path)

    img_dir = out_path / "images"
    if img_dir.exists() and overwrite:
        shutil.rmtree(img_dir)

    img_dir.mkdir(parents=True, exist_ok=False)

    # todo: make it more reliable
    # scene_frame_names = [sc for sc in scene_frame_names if sc in to_keep]
    filelist = [
        f"{(scene_root / 'images' / s_name).as_posix()}.png"
        for s_name in scene_frame_names
    ]

    filelist = filter_filelist(filelist, cfg.filter_percentage, max_size=20, min_size=7)
    input_size = cv2.imread(filelist[0]).shape

    start_time = time.time()
    with tempfile.TemporaryDirectory(suffix="wai_mast3r_module") as tmpdirname:
        # correspondences is the list of tuples of three elements: xy1, xy2 and confs
        scene, tracked_correspondences = get_scene_and_corres(
            filelist,
            model=model,
            cache_dir=tmpdirname,
            scene_graph=cfg.scene_graph,
            lr1=cfg.lr1,
            niter1=cfg.niter1,
            lr2=cfg.lr2,
            niter2=cfg.niter2,
            device=cfg.device,
            optim_level=cfg.optim_level,
            shared_intrinsics=cfg.shared_intrinsics,
            matching_conf_thr=cfg.matching_conf_thr,
            save_correspondences=False,
        )

        correspondences, correspondences_pairs = zip(*tracked_correspondences)
        cams2world = scene.get_im_poses().cpu()
        dense_pc = scene.get_dense_pts3d()
        rgbimg = scene.imgs
        focals = scene.get_focals().cpu()
        pps = scene.get_principal_points().cpu()
        # pts3d is a list of np array of shape (h*w, 3)
        # depths is a list of np array of shape h*w
        # confs is a list of np array of shape (h, w)
        pts3d, depths, depth_confs = to_numpy(dense_pc)
        mask = to_numpy([c > 1.5 for c in depth_confs])
        focals = to_numpy(focals)
        # intrinsics
        pps = to_numpy(pps)
        # shared intrinsics
        cx, cy = pps[0]
        cams2world = to_numpy(cams2world)
        pts3d = np.concatenate([p[m.ravel()] for p, m in zip(pts3d, mask)]).reshape(
            -1, 3
        )
        rgbimg = np.concatenate([p[m] for p, m in zip(rgbimg, mask)]).reshape(-1, 3)
        valid_msk = np.isfinite(pts3d.sum(axis=1))
        pts3d = pts3d[valid_msk]
        rgbimg = rgbimg[valid_msk]
        depth_confs = np.array(depth_confs)

        h, w, _ = scene.imgs[0].shape
        depths = np.array(depths)
        depths = depths.reshape((-1, h, w))
        logger.info(
            f"Scene attributes computed. Took: {time.time() - start_time} seconds for {scene_name}"
        )

        vizualise_scene_with_rerun(pts3d, rgbimg, scene.imgs, focals, cams2world)

        logger.info(f"Storing data {out_path}")

        # frames (per-frames extrinsics parameters, depths)
        for i in range(len(scene.img_paths)):
            frame_name = os.path.basename(scene.img_paths[i]).split(".")[0]
            file_path = Path(scene.img_paths[i])
            transform_matrix = cams2world[i].tolist()
            depth_path = f"depth/{frame_name}.exr"
            depth_confs_path = f"depth_confidence/{frame_name}.exr"
            store_data(out_path / depth_path, depths[i], "depth")
            store_data(out_path / depth_confs_path, depth_confs[i], "scalar")

            os.symlink(file_path, img_dir / f"{frame_name}{file_path.suffix}")

            wai_frame = {
                "frame_name": frame_name,
                "image": str(Path("images") / f"{frame_name}{file_path.suffix}"),
                "file_path": str(Path("images") / f"{frame_name}{file_path.suffix}"),
                "transform_matrix": transform_matrix,
                "mast3r_depth": depth_path,
                "mast3r_depth_confidence": depth_confs_path,
            }

            wai_frames.append(wai_frame)

        # scene modalities (gt_pts3d, gt_pts3d_colors, correspondences)
        ## store correspondences and keep track of image order
        correspondences = to_numpy(correspondences)
        correspondences = np.array(correspondences, dtype=object)
        store_data(out_path / "correspondences.npy", correspondences)
        store_data(out_path / "correspondences_pairs.json", correspondences_pairs)
        ## store global pc
        store_data(out_path / "global_pts3d.npy", pts3d)
        store_data(out_path / "global_pts3d_colors.npy", rgbimg)
        wai_scene_modalities = {
            "gt_pts3d": {
                "path": "global_pts3d.npy",
                "format": "numpy",
            },
            "global_pts3d_colors": {
                "path": "global_pts3d_colors.npy",
                "format": "numpy",
            },
            "correspondences": {
                "path": "correspondences.npy",
                "format": "numpy",
            },
            "correspondences_pairs": {
                "path": "correspondences_pairs.json",
                "format": "readable",
            },
        }

        wai_frame_modalities = {
            "pred_depth": {"frame_key": "mast3r_depth", "format": "depth"},
            "depth_confidence": {
                "frame_key": "mast3r_depth_confidence",
                "format": "scalar",
            },
            "image": {
                "frame_key": "image",
                "format": "image",
            },
        }

        # remember to scale intrinsic, hold depth
        scale = min(input_size[0] / h, input_size[1] / w)
        fl_x = float(focals[0]) * scale
        fl_y = float(focals[0]) * scale
        cx = float(cx) * scale
        cy = float(cy) * scale

        scene_meta = {
            "scene_name": scene_name,
            "dataset_name": cfg.dataset_name,
            "version": cfg.version,
            "shared_intrinsics": True,
            "camera_model": "PINHOLE",
            "camera_convention": "opencv",
            "scale_type": "metric",
            "fl_x": fl_x,
            "fl_y": fl_y,
            "cx": cx,
            "cy": cy,
            "h": input_size[0],
            "w": input_size[1],
            "frames": wai_frames,
            "frame_modalities": wai_frame_modalities,
            "scene_modalities": wai_scene_modalities,
        }

        store_data(out_path / "scene_meta.json", scene_meta, "scene_meta")


def vizualise_scene_with_rerun(pts3d, rgbimg, imgs, focals, cams2world):
    from mast3r.cloud_opt.sparse_ga import to_numpy

    logger.info("sending info to rerun server")
    # TODO: add simple ping to the server and catch any errors it may arise to don't break.
    rr.init(application_id="mast3r wrapper", strict=True, spawn=False)
    rr.connect_tcp("0.0.0.0:9081")
    rr.log(
        "world/xyz",
        rr.Arrows3D(
            vectors=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            colors=[[255, 0, 0], [0, 255, 0], [0, 0, 255]],
        ),
    )
    imgs = to_numpy(imgs)
    rr.log("point_cloud", rr.Points3D(pts3d, colors=rgbimg))

    # add each camera
    for i, pose_c2w in enumerate(cams2world):
        intrinsics = focals[i]
        height, width = imgs[i].shape[:2]
        image = np.asarray(imgs[i])
        base_name = f"camera_{i}"
        rr.log(
            base_name,
            rr.Transform3D(
                translation=pose_c2w[:3, 3],
                mat3x3=pose_c2w[:3, :3],
                from_parent=False,
            ),
        )

        intrinsics_matrix = np.eye(3)
        intrinsics_matrix[0, 0] = intrinsics
        intrinsics_matrix[1, 1] = intrinsics

        rr.log(
            f"{base_name}/pinhole",
            rr.Pinhole(
                image_from_camera=intrinsics_matrix,
                height=height,
                width=width,
                camera_xyz=rr.ViewCoordinates.RDF,
                image_plane_distance=0.2,
            ),
        )
        rr.log(f"{base_name}/pinhole/rgb", rr.Image(image))


if __name__ == "__main__":
    import sys

    logger.debug("Command line arguments:")
    for i, arg in enumerate(sys.argv):
        logger.debug(f"  [{i}]: {arg}")

    cfg = argconf_parse(WAI_PROC_CONFIG_PATH / "mast3r/default.yaml")
    if cfg.get("root") is None:
        raise ValueError(
            "Specify the root via: 'python scripts/run_mast3r.py root=<root_path>'"
        )

    logger.info("Running Mast3r using config:")
    for key, value in dict(cfg).items():
        logger.info(f"  {key}: {value}")

    scene_frame_names = get_scene_frame_names(cfg)

    model = load_mast3r(cfg.source_code_path, cfg.model_path, cfg.device)

    logger.info(f"Processing: {len(scene_frame_names)} scenes")
    logger.debug(f"scene_frame_names = {scene_frame_names}")

    for scene_name in tqdm(scene_frame_names, "Processing scenes"):
        logger.info(f"Processing: {scene_name}")
        scene_root = Path(cfg.root) / scene_name
        set_processing_state(scene_root, "mast3r", "running")
        try:
            run_mast3r_on_scene(cfg, scene_name, model, overwrite=cfg.overwrite)
            set_processing_state(scene_root, "mast3r", "finished")
        except Exception:
            logger.error(f"Running mast3r failed on scene '{scene_name}'")
            trace_message = traceback.format_exc()
            logger.error(trace_message)
            set_processing_state(scene_root, "mast3r", "failed", message=trace_message)
            continue
