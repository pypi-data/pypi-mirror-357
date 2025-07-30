"""Script to batch process datasets using slurm arrays with sequential stage support."""

import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from math import ceil
from pathlib import Path
from typing import Any, Dict, List, Optional

from argconf import argconf_parse
from wai.launch.launch_utils import (
    _escape_scene_names,
    import_function_from_path,
    parse_string_to_dict,
)
from wai.utils import get_scene_names
from wai_processing import (
    WAI_PROC_CONFIG_PATH,
    WAI_PROC_MAIN_PATH,
    WAI_PROC_SCRIPT_PATH,
    WAI_SPOD_RUNS_PATH,
)

## Set up basic logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("slurm_stage")


def create_slurm_array_script(
    script_path: str,
    config_path: str,
    root: str,
    scene_batches: list,
    data_split: Optional[str] = None,
    additional_args: str = "",
    conda_env: str = "pytorch",
    working_dir: Optional[str] = None,
) -> str:
    """Create a SLURM array job script that processes scene batches."""

    # Create the batch script content
    script_content = f"""#!/bin/bash
#SBATCH --array=0-{len(scene_batches) - 1}

# Activate conda environment
source ~/.bashrc
conda activate {conda_env}

# Change to working directory if specified
{f"cd {working_dir}" if working_dir else ""}

# Get the scene batch for this array task
SCENE_BATCHES=({" ".join([f'"{_escape_scene_names(batch)}"' for batch in scene_batches])})
SCENE_BATCH="${{SCENE_BATCHES[$SLURM_ARRAY_TASK_ID]}}"

# Build the command
CMD="python {script_path} {config_path} root={root} '+scene_filters=$SCENE_BATCH'"
{f'CMD="$CMD data_split={data_split}"' if data_split else ""}
{f'CMD="$CMD {additional_args}"' if additional_args else ""}

echo "Running array task $SLURM_ARRAY_TASK_ID with command: $CMD"
eval $CMD
"""

    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as f:
        f.write(script_content)
        return f.name


def submit_slurm_array_job(
    script_file: str,
    job_name: str,
    cpus: int,
    gpus: int,
    mem: str,
    nodelist: Optional[str] = None,
    dependency_job_id: Optional[str] = None,
) -> str:
    """Submit a SLURM array job using sbatch and return the job ID."""

    sbatch_cmd = [
        "sbatch",
        f"--job-name={job_name}",
        f"--cpus-per-task={cpus}",
        f"--mem={mem}",
    ]

    if gpus > 0:
        sbatch_cmd.append(f"--gres=gpu:{gpus}")

    if nodelist:
        sbatch_cmd.append(f"--nodelist={nodelist}")

    # Add dependency if specified
    if dependency_job_id:
        sbatch_cmd.append(f"--dependency=afterok:{dependency_job_id}")

    sbatch_cmd.append(script_file)

    logger.info(f"Submitting SLURM array job with command: {' '.join(sbatch_cmd)}")

    try:
        result = subprocess.run(sbatch_cmd, capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        logger.info(f"SLURM job submitted successfully: {output}")

        # Extract job ID from output (format: "Submitted batch job 12345")
        job_id = output.split()[-1]
        return job_id
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to submit SLURM job: {e.stderr}")
        raise


def get_scene_names_for_stage(
    stage_name: str,
    stage_cfg: Dict[str, Any],
    main_cfg: Any,
    additional_scene_filters: List[Any],
) -> List[str]:
    """Get scene names for a specific stage."""
    if stage_name == "conversion":
        scene_names = import_function_from_path(
            WAI_PROC_SCRIPT_PATH / stage_cfg["script"], "get_original_scene_names"
        )(main_cfg)
        # now enable filtering also on process_state (if root exists)
        if Path(main_cfg.root).exists():
            scene_names = get_scene_names(main_cfg, scene_names=scene_names)
    else:
        if additional_scene_filters:
            main_cfg.scene_filters = main_cfg.scene_filters + additional_scene_filters
        scene_names = get_scene_names(main_cfg)

    return scene_names


def process_single_stage(
    cfg: Any,
    stage_name: str,
    dependency_job_id: Optional[str] = None,
    shared_code_path: Optional[str] = None,
) -> Optional[str]:
    """Process a single stage and return the job ID if submitted."""
    logger.info(f"Processing stage: {stage_name}")

    stage_cfg = cfg.stages.get(stage_name)
    if stage_cfg is None:
        logger.warning(f"Stage '{stage_name}' is null or not configured, skipping...")
        return dependency_job_id  # Return the previous job ID to maintain chain

    # Set resources using stage settings (if available)
    gpus = stage_cfg.get("gpus", cfg.gpus)
    cpus = stage_cfg.get("cpus", cfg.cpus)
    mem = stage_cfg.get("mem", cfg.mem)
    scenes_per_job = stage_cfg.get("scenes_per_job", cfg.scenes_per_job)

    dataset_name = Path(cfg.conf).stem
    main_cfg = argconf_parse(
        WAI_PROC_CONFIG_PATH / stage_cfg["config"], cli_overwrite=False
    )
    main_cfg.root = cfg.root
    data_split = cfg.get("data_split")
    if "data_split" in main_cfg:
        main_cfg.data_split = data_split
    if cfg.get("dry_run_filter") is not None:
        logger.info(f"Prefilter for a dry run: {cfg.dry_run_filter}")
        main_cfg["scene_filters"] = main_cfg.get("scene_filters", []) + [
            cfg.dry_run_filter
        ]

    # Resolve additional CLI arguments set for this stage via the config
    additional_scene_filters = []
    additional_args = ""
    for cli_param in stage_cfg.get("additional_cli_params", []):
        if match := re.match(r"\+scene_filters=(.+)", cli_param):
            additional_scene_filters.append(parse_string_to_dict(match.group(1)))
        else:
            additional_args += f" {cli_param}"

    # Get scene names for this stage
    scene_names = get_scene_names_for_stage(
        stage_name, stage_cfg, main_cfg, additional_scene_filters
    )
    num_scenes = len(scene_names)

    logger.info(f"--- Processing {num_scenes:,} scenes for stage '{stage_name}' ---")
    logger.debug(f"scene_names = {scene_names}")

    max_slurm_jobs = cfg.get("max_num_slurm_jobs", 20)
    num_array_tasks = ceil(num_scenes / scenes_per_job)

    # Safety measures to avoid launching too many array tasks
    if num_array_tasks > max_slurm_jobs:
        raise RuntimeError(
            f"Stage '{stage_name}' would launch {num_array_tasks} array tasks, but only {max_slurm_jobs} allowed.\n"
            "If this is intentional you can increase the maximum number of jobs by passing the 'max_num_slurm_jobs=<your_new_max_number_of_allowed_jobs>'"
        )

    # Create scene batches for array processing
    scene_batches = []
    for start_idx in range(0, num_scenes, scenes_per_job):
        end_idx = min(start_idx + scenes_per_job, num_scenes)
        job_scene_names = scene_names[start_idx:end_idx]
        scene_batches.append(job_scene_names)

    # Set up paths
    locked_cfg = cfg.get("locked", False)
    script_path = (
        f"{WAI_PROC_SCRIPT_PATH}/{stage_cfg['script']}"
        if not locked_cfg
        else f"{shared_code_path}/wai/scripts/{stage_cfg['script']}"
    )
    config_path = (
        f"{WAI_PROC_CONFIG_PATH}/{stage_cfg['config']}"
        if not locked_cfg
        else f"{shared_code_path}/wai/configs/{stage_cfg['config']}"
    )
    working_dir = shared_code_path if locked_cfg else None

    job_name = f"{dataset_name}_{stage_name}_array"

    launch_on_slurm = cfg.get("launch_on_slurm", False)

    if launch_on_slurm:
        # Create and submit SLURM array job
        slurm_script = create_slurm_array_script(
            script_path=script_path,
            config_path=config_path,
            root=cfg.root,
            scene_batches=scene_batches,
            data_split=data_split,
            additional_args=additional_args,
            conda_env=cfg.conda_env,
            working_dir=working_dir,
        )

        try:
            job_id = submit_slurm_array_job(
                script_file=slurm_script,
                job_name=job_name,
                cpus=cpus,
                gpus=gpus,
                mem=mem,
                nodelist=cfg.get("nodelist"),
                dependency_job_id=dependency_job_id,
            )
            logger.info(
                f"Successfully submitted SLURM array job '{job_name}' with {num_array_tasks} tasks (Job ID: {job_id})"
            )
            return job_id
        finally:
            # Clean up temporary script file
            if os.path.exists(slurm_script):
                os.unlink(slurm_script)
    else:
        # Dry run - show what would be submitted
        logger.info(
            f"\nWould submit SLURM array job for stage '{stage_name}' with the following configuration:"
        )
        logger.info(f"  Job name: {job_name}")
        logger.info(
            f"  Array tasks: 0-{len(scene_batches) - 1} ({len(scene_batches)} total)"
        )
        logger.info(f"  CPUs per task: {cpus}")
        logger.info(f"  GPUs per task: {gpus}")
        logger.info(f"  Memory per task: {mem}")
        logger.info(f"  Conda environment: {cfg.conda_env}")
        if cfg.get("nodelist"):
            logger.info(f"  Node list: {cfg.get('nodelist')}")
        if working_dir:
            logger.info(f"  Working directory: {working_dir}")
        if dependency_job_id:
            logger.info(f"  Dependency: afterok:{dependency_job_id}")

        logger.info("\nScene batches per array task:")
        for i, batch in enumerate(scene_batches):
            logger.info(f"  Task {i}: {len(batch)} scenes")

        return None


def process_all_stages(cfg: Any, shared_code_path: Optional[str] = None) -> None:
    """Process all stages sequentially with dependencies."""
    logger.info("Processing all stages sequentially...")

    # Get the ordered list of stages from the config
    stages_config = cfg.stages
    if not stages_config:
        raise ValueError("No stages configuration found")

    # Convert to ordered list (preserving YAML order)
    stage_names = list(stages_config.keys())
    logger.info(f"Found {len(stage_names)} stages to process: {stage_names}")

    previous_job_id = None
    submitted_jobs = []

    for stage_name in stage_names:
        try:
            job_id = process_single_stage(
                cfg=cfg,
                stage_name=stage_name,
                dependency_job_id=previous_job_id,
                shared_code_path=shared_code_path,
            )

            if job_id:
                submitted_jobs.append((stage_name, job_id))
                previous_job_id = job_id
                logger.info(f"Stage '{stage_name}' submitted with Job ID: {job_id}")
            else:
                logger.info(f"Stage '{stage_name}' skipped or dry run")

        except Exception as e:
            logger.error(f"Failed to process stage '{stage_name}': {e}")
            if cfg.get("launch_on_slurm", False):
                # In production mode, stop the pipeline on error
                raise
            else:
                # In dry run mode, continue to show what would happen
                continue

    if submitted_jobs:
        logger.info(f"\nSuccessfully submitted {len(submitted_jobs)} stage jobs:")
        for stage_name, job_id in submitted_jobs:
            logger.info(f"  {stage_name}: Job ID {job_id}")
        logger.info("\nJobs will execute sequentially based on dependencies.")
    else:
        logger.info("\nNo jobs were submitted (dry run mode).")


if __name__ == "__main__":
    logger.debug("Command line arguments:")
    for i, arg in enumerate(sys.argv):
        logger.debug(f"  [{i}]: {arg}")

    cfg = argconf_parse()

    # Check for sequential processing mode
    process_all = cfg.get("all_stages", False) or cfg.get("sequential", False)

    if not process_all and cfg.get("stage") is None:
        raise ValueError(
            "Either set 'stage' for single stage processing or 'all_stages=true'/'sequential=true' for sequential processing.\n"
            "Examples:\n"
            "  Single stage: python launch/slurm_stage.py configs/launch/dl3dv.yaml stage=undistort\n"
            "  All stages: python launch/slurm_stage.py configs/launch/dl3dv.yaml all_stages=true"
        )

    if cfg.get("conda_env") is None:
        raise ValueError(
            "Pass the name of your conda environment like `conda_env=pytorch`"
        )

    logger.info("Running slurm_stage using config:")
    for key, value in dict(cfg).items():
        logger.info(f"  {key}: {value}")

    # Handle locked code setup (shared for all stages)
    locked_cfg = cfg.get("locked", False)
    launch_on_slurm = cfg.get("launch_on_slurm", False)
    shared_code_path: Optional[str] = None

    if locked_cfg and launch_on_slurm:
        unique_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_path = os.path.join(
            WAI_SPOD_RUNS_PATH, "sequential" if process_all else cfg.stage
        )
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        shared_code_path = os.path.join(base_path, unique_id)
        shutil.copytree(WAI_PROC_MAIN_PATH, shared_code_path)
        logger.info(f"locked version of wai at: {shared_code_path}")

    if process_all:
        # Process all stages sequentially
        process_all_stages(cfg, shared_code_path)
    else:
        # Process single stage (original behavior)
        stage_name = cfg.stage
        if cfg.stages.get(stage_name) is None:
            raise ValueError(f"Stage not supported: {stage_name}")

        job_id = process_single_stage(
            cfg=cfg,
            stage_name=stage_name,
            shared_code_path=shared_code_path,
        )

        if not launch_on_slurm:
            logger.info(
                "\nThis command did not launch any jobs. If the above configuration looks correct, "
                "run the command with 'launch_on_slurm=true' to schedule the SLURM array job."
            )
