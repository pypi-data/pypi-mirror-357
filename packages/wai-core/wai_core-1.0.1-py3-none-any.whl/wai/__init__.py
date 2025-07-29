# Expose core functions directly to the wai project
from . import dashboard, launch, profiling, scripts, utils, wai_dataset
from .utils.env_utils import check_environment_sync
from .wai_core import (
    get_frame,
    load_data,
    load_frame,
    load_frames,
    load_scene,
    set_frame,
    store_data,
    WAI_COLORMAP_PATH,
    WAI_CONFIG_PATH,
    WAI_MAIN_PATH,
)

__all__ = [
    "WAI_COLORMAP_PATH",
    "WAI_CONFIG_PATH",
    "WAI_MAIN_PATH",
    "check_environment_sync",
    "dashboard",
    "get_frame",
    "launch",
    "load_data",
    "load_frame",
    "load_frames",
    "load_scene",
    "profiling",
    "scripts",
    "set_frame",
    "store_data",
    "utils",
    "wai_dataset",
]


import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("wai")

if os.environ.get("SKIP_WAI_ENV_SYNC_CHECK", False):
    logger.info("Skipping wai environment sync check")
else:
    # Check if the current environment is in sync with the setup.py file.
    check_environment_sync("wai")
