"""
Shared utility functions: path resolution, logging, validation.
"""

from .paths import get_project_root, get_input_video, ensure_output_dirs
from .logger import setup_logger, print_log_status
from .validators import validate_input_video, validate_ffmpeg

__all__ = [
    "get_project_root",
    "get_input_video",
    "ensure_output_dirs",
    "setup_logger",
    "print_log_status",
    "validate_input_video",
    "validate_ffmpeg",
]
