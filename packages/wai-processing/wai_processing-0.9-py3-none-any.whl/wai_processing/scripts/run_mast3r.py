import logging
import os
import shutil
import tempfile
import time
import traceback
from pathlib import Path

import cv2
import numpy as np
import torch
from argconf import argconf_parse
from tqdm import tqdm
from wai import filter_scene_frames, get_scene_frame_names, load_data, store_data
from wai.io import set_processing_state
from wai_processing import WAI_PROC_CONFIG_PATH

from .model_wrapper.mast3r import (
    get_scene_and_corres,
    load_mast3r,
    load_retrieval_model,
)

## Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def run_mast3r_on_scene(cfg, scene_name, model, retrieval_model, overwrite, **kwargs):
    """
    Run MAST3R on a given scene.
    Args:
        cfg (dict): Configuration dictionary.
        scene_name (str): Name of the scene to process.
        model: Model to use for processing.
        retrieval_model: connect views based on similarity. Could be None
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

    # Delete previous generation
    out_path = scene_root / cfg.out_path
    if out_path.exists() and overwrite:
        shutil.rmtree(out_path)

    img_dir = out_path / "images"
    if img_dir.exists() and overwrite:
        shutil.rmtree(img_dir)

    img_dir.mkdir(parents=True, exist_ok=False)

    filelist = [str(scene_root / frame["file_path"]) for frame in scene_meta["frames"]]

    filelist = filter_scene_frames(
        filelist, cfg.filter_percentage, cfg.max_size, cfg.min_size
    )

    sim_matrix = None
    if retrieval_model:
        with torch.no_grad():
            sim_matrix = retrieval_model(filelist)
        # Cleanup
        del retrieval_model
        torch.cuda.empty_cache()

    input_size = cv2.imread(filelist[0]).shape

    start_time = time.time()
    with tempfile.TemporaryDirectory(suffix="wai_mast3r_module") as tmpdirname:
        # correspondences is the list of tuples of three elements: xy1, xy2 and confs
        scene, tracked_correspondences = get_scene_and_corres(
            filelist,
            model=model,
            sim_matrix=sim_matrix,
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
            ret_nb_anchors=cfg.ret_nb_anchors,
            ret_knn=cfg.ret_knn,
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
        # align with first camera's frame
        first_camera_transform = cams2world[0]
        inverse_first_camera = np.linalg.inv(first_camera_transform)
        pts3d = (
            inverse_first_camera @ np.hstack((pts3d, np.ones((pts3d.shape[0], 1)))).T
        ).T[:, :3]
        h, w, _ = scene.imgs[0].shape
        depths = np.array(depths)
        depths = depths.reshape((-1, h, w))
        logger.info(
            f"Scene attributes computed. Took: {time.time() - start_time} seconds for {scene_name}"
        )

        logger.info(f"Storing data {out_path}")

        # frames (per-frames extrinsics parameters, depths)
        for i in range(len(scene.img_paths)):
            frame_name = os.path.basename(scene.img_paths[i]).split(".")[0]
            file_path = Path(scene.img_paths[i])

            # adjust camera extrinsics to the new reference frame
            cam2world = cams2world[i]
            adjusted_transform_matrix = inverse_first_camera @ cam2world
            transform_matrix = adjusted_transform_matrix.tolist()

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

        # scene modalities (global_pts3d, global_pts3d_colors, correspondences)
        ## store correspondences and keep track of image order
        correspondences = to_numpy(correspondences)
        correspondences = np.array(correspondences, dtype=object)
        store_data(out_path / "correspondences.npy", correspondences)
        store_data(out_path / "correspondences_pairs.json", correspondences_pairs)
        ## store global pc
        store_data(out_path / "global_pts3d.npy", pts3d)
        store_data(out_path / "global_pts3d_colors.npy", rgbimg)
        wai_scene_modalities = {
            "global_pts3d": {
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
    retrieval_model = None
    if "retrieval" in cfg.scene_graph:
        retrieval_model = load_retrieval_model(
            cfg.retrieval_model_path, backbone=model, device=cfg.device
        )
    logger.info(f"Processing: {len(scene_frame_names)} scenes")
    logger.debug(f"scene_frame_names = {scene_frame_names}")

    for scene_name in tqdm(scene_frame_names, "Processing scenes"):
        logger.info(f"Processing: {scene_name}")
        scene_root = Path(cfg.root) / scene_name
        set_processing_state(scene_root, "mast3r", "running")
        try:
            run_mast3r_on_scene(
                cfg, scene_name, model, retrieval_model, overwrite=cfg.overwrite
            )
            set_processing_state(scene_root, "mast3r", "finished")
        except Exception:
            logger.error(f"Running mast3r failed on scene '{scene_name}'")
            trace_message = traceback.format_exc()
            logger.error(trace_message)
            set_processing_state(scene_root, "mast3r", "failed", message=trace_message)
            continue
