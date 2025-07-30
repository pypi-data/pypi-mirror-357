import logging
import traceback
from pathlib import Path
from shutil import rmtree
from time import time

import pycolmap
from argconf import argconf_parse
from tqdm import tqdm
from wai import filter_scene_frames, get_scene_frame_names, load_data
from wai.io import set_processing_state
from wai_processing import (
    WAI_PROC_CONFIG_PATH,
)

logger = logging.getLogger(__name__)

COLMAP_CAMERA_MODES = [
    "AUTO",
    "SINGLE",
    "PER_FOLDER",
    "PER_IMAGE",
]


def run_colmap_on_scene(cfg, scene_name: str):
    # pycolmap --> CPU only for now as we cannot compile pycolmap with CUDA
    # due to missing SLURM modules on the AWS cluster --> Need to reach out to
    # META HPC team to enable these modules
    scene_root: Path = Path(cfg.root) / scene_name
    if (scene_root / "colmap").exists():
        rmtree(str(scene_root / "colmap"))
    output_path: Path = scene_root / "colmap" / "sparse"
    database_path = output_path / "0" / "database.db"
    image_dir: Path = scene_root / "images"
    (output_path / "0").mkdir(exist_ok=True, parents=True)

    start_time = time()
    image_list = []
    if cfg.get("max_size", None):
        scene_meta = load_data(scene_root / "scene_meta.json", "scene_meta")
        all_image_names = [frame["image"] for frame in scene_meta["frames"]]
        # Filter all frames with equal spacing
        image_list = filter_scene_frames(
            all_image_names,
            cfg.filter_percentage,
            cfg.max_size,
            cfg.get("min_size", None),
            file_name_only=True,
        )

    cam_model = cfg.get("camera_model", "SIMPLE_PINHOLE")
    camera_mode = cfg.get("camera_mode", "SINGLE")
    if camera_mode not in COLMAP_CAMERA_MODES:
        raise ValueError(
            f"Expected camera mode to be in {COLMAP_CAMERA_MODES}, but got {camera_mode}."
        )
    reader_opts = pycolmap.ImageReaderOptions()
    reader_opts.camera_model = cam_model
    reader_opts.default_focal_length_factor = cfg.get(
        "default_focal_length_factor", 0.5
    )
    sift_opts = pycolmap.SiftExtractionOptions()
    # TODO: Expose all SIFT options and extract feature options, ideally inherit directly all
    # configurable options from the pybindings
    sift_opts.max_image_size = cfg.get("max_image_size", 3200)
    pycolmap.extract_features(
        database_path,
        image_dir,
        image_list=image_list,
        camera_model=cam_model,
        camera_mode=camera_mode,
        reader_options=reader_opts,
        sift_options=sift_opts,
    )
    feature_matching_mode = cfg.get("feature_matching_mode", "exhaustive")
    if feature_matching_mode == "exhaustive":
        pycolmap.match_exhaustive(database_path)
    elif feature_matching_mode == "sequential":
        pycolmap.match_sequential(database_path=database_path)
    elif "vocabtree":
        pycolmap.match_vocabtree(database_path=database_path)
    else:
        raise NotImplementedError(
            f"Feature matching strategy '{feature_matching_mode}' not available."
        )
    # TODO: Add all options from mapper and BA, ideally inherit directly from pybindings
    logger.info("Incremental Mapping")
    all_recons = pycolmap.incremental_mapping(database_path, image_dir, output_path)
    if len(all_recons) == 0:
        raise RuntimeError(
            "Colmap incremental mapper failed and produced no reconstruction."
        )
    # only taking the first / largest recon
    recon = all_recons[0]
    logger.info("Refinement with bundle adjustment")
    pycolmap.bundle_adjustment(recon)
    recon.write(output_path)
    runtime = time() - start_time
    logger.info(f"Runtime for Colmap on scene {scene_name}: {runtime:.2f} seconds")


if __name__ == "__main__":
    # TODO (duncanzauss): Add sanity check here to confirm that colmap is properly installed
    cfg = argconf_parse(WAI_PROC_CONFIG_PATH / "colmap/default.yaml")
    if cfg.get("root") is None:
        raise ValueError(
            "Specify the root via: 'python scripts/run_colmap.py root=<wai_root_path>'"
        )

    logger.info("Running Colmap using config:")
    for key, value in dict(cfg).items():
        logger.info(f"  {key}: {value}")
    scene_frame_names = get_scene_frame_names(cfg)
    logger.info(f"Processing: {len(scene_frame_names)} scenes")
    logger.debug(f"scene_frame_names = {scene_frame_names}")
    for scene_name in tqdm(scene_frame_names, "Processing scenes"):
        logger.info(f"Processing: {scene_name}")
        scene_root = Path(cfg.root) / scene_name
        set_processing_state(scene_root, "colmap", "running")
        try:
            run_colmap_on_scene(cfg, scene_name)
            set_processing_state(scene_root, "colmap", "finished")
        except Exception:
            logger.error(f"Running colmap failed on scene '{scene_name}'")
            trace_message = traceback.format_exc()
            logger.error(trace_message)
            set_processing_state(scene_root, "colmap", "failed", message=trace_message)
            continue
