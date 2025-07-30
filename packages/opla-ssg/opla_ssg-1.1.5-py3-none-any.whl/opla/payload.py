"""Provide functions to copy static and attached files to output directory"""

import logging
import shutil
from pathlib import Path

from .templating import TEMPLATES_PATH

logger = logging.getLogger(__name__)


def copy(src: str | Path, dst: Path):
    """
    Copy a file or a directory tree to a destination directory

    Args:
        src: path to the source file or directory
        dst: path to the destination directory
    """
    src = Path(src)
    if src.is_dir():
        logger.debug(f"Copying {src} directory to {dst}")
        shutil.copytree(src, dst / src.name)
    else:
        logger.debug(f"Copying {src} file to {dst}")
        # Ensure that parent directory exists
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)


def copy_custom_static_files(config: dict[dict] | str, dst_dir: Path):
    """
    Copy custom files to a destination folder

    Args:
        config: opla config dict
        dst_dir: path to the destination folder
    """
    try:
        custom_path = Path(config["theme"]["custom"])
    except KeyError:
        return
    # Copy css and js files to custom dir tree
    for file_path in (
        config["theme"]["custom_css_files"]
        + config["theme"]["custom_js_files"]
    ):
        src_file = custom_path / "static" / file_path
        copy(src_file, dst_dir / "custom" / file_path)


def copy_static_files(config: dict[dict], dst_dir: Path):
    """
    Copy static files (if they exist) to a destination folder

    Args:
        config: opla config dict
        dst_dir: path to the destination folder
    """
    theme_name = config["theme"]["name"]
    static_path = TEMPLATES_PATH / theme_name / "static"
    if static_path.exists():
        copy(static_path, dst_dir / theme_name)


def copy_data_files(config: dict, dst_dir: Path):
    """
    Copy data files to a destination folder

    Args:
        config: opla config dict
        dst_dir: path to the destination folder
    """
    if "data" in config:
        for data in config["data"]:
            copy(data, dst_dir)


def copy_payload(config: dict, dst_dir: Path):
    """
    Copy static and attached files to a destination folder

    Args:
        config: opla config dict
        dst_dir: path to the destination folder
    """
    copy_static_files(config, dst_dir)
    copy_custom_static_files(config, dst_dir)
    copy_data_files(config, dst_dir)


def create_output_directory(dir: Path) -> Path:
    """
    Create the output directory. If it already exists, delete it and create a new one

    Args:
        dir: path to the output directory

    Returns:
        Path: the created output directory
    """
    shutil.rmtree(dir, ignore_errors=True)
    dir.mkdir(parents=True)
    return dir
