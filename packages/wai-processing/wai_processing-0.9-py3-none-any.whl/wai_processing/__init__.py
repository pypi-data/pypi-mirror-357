from pathlib import Path

from .utils.mapper import convert_scenes_wrapper, default_get_original_scene_names

WAI_PROC_MAIN_PATH = Path(__file__).parent.parent
WAI_PROC_CONFIG_PATH = WAI_PROC_MAIN_PATH / "wai-processing" / "configs"
WAI_PROC_SCRIPT_PATH = WAI_PROC_MAIN_PATH / "wai-processing" / "scripts"
WAI_PROC_SCRIPT_PATH = WAI_PROC_MAIN_PATH / "wai-processing" / "scripts"
WAI_SPOD_RUNS_PATH = "/fsx/xrtech/code/spod_runs"

__all__ = [
    "WAI_PROC_MAIN_PATH",
    "WAI_PROC_CONFIG_PATH",
    "WAI_PROC_SCRIPT_PATH",
    "WAI_SPOD_RUNS_PATH",
    "convert_scenes_wrapper",
    "default_get_original_scene_names",
]
