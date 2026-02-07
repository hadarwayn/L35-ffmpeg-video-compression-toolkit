"""
Path resolution utilities for the L35 toolkit.

Every path is RELATIVE — the project works on any computer.
Functions auto-create output directories so tasks don't need to worry.
"""

from pathlib import Path
from typing import Optional


def get_project_root() -> Path:
    """
    Return the absolute path to the project root directory.

    Works from any file because we navigate up from *this* file's location.
    This file lives at: project_root/src/utils/paths.py  → 3 levels up.
    """
    return Path(__file__).resolve().parent.parent.parent


def get_input_video(input_dir: Optional[Path] = None) -> Path:
    """
    Find the first .mp4 file inside the input directory.

    Args:
        input_dir: Override input directory (defaults to project_root/input).

    Returns:
        Path to the discovered MP4 video file.

    Raises:
        FileNotFoundError: If no MP4 file is found in the input directory.
    """
    if input_dir is None:
        input_dir = get_project_root() / "input"

    mp4_files = sorted(input_dir.glob("*.mp4"))
    if not mp4_files:
        raise FileNotFoundError(
            f"No .mp4 video found in {input_dir}. "
            "Please place an H.264 MP4 video in the input/ folder."
        )
    return mp4_files[0]


def ensure_output_dirs() -> None:
    """
    Create all required output directories if they do not exist.

    Called once at startup so individual tasks never need to create folders.
    """
    from src.config import (
        TASK1_OUTPUT_DIR,
        TASK2_OUTPUT_DIR,
        TASK2_FRAMES_DIR,
        TASK3_OUTPUT_DIR,
        GRAPHS_DIR,
        LOGS_DIR,
    )

    for d in [
        TASK1_OUTPUT_DIR,
        TASK2_OUTPUT_DIR,
        TASK2_FRAMES_DIR,
        TASK3_OUTPUT_DIR,
        GRAPHS_DIR,
        LOGS_DIR,
    ]:
        d.mkdir(parents=True, exist_ok=True)
