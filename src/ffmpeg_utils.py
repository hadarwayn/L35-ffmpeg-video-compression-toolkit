"""
Thin wrappers around FFmpeg and FFprobe subprocess calls.

Every function uses ``subprocess.run()`` with **list** arguments
(never ``shell=True``) to prevent command-injection vulnerabilities.
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Any

from src.config import FFMPEG_DIR

logger = logging.getLogger("ffmpeg_utils")


def _bin(name: str = "ffmpeg") -> str:
    """Resolve the full path to an FFmpeg binary."""
    if FFMPEG_DIR and (FFMPEG_DIR / f"{name}.exe").exists():
        return str(FFMPEG_DIR / f"{name}.exe")
    return name


# ---------------------------------------------------------------------------
# FFprobe helpers
# ---------------------------------------------------------------------------

def run_ffprobe_json(input_path: Path) -> dict[str, Any]:
    """
    Run ``ffprobe -print_format json -show_format -show_streams`` and
    return the parsed JSON as a Python dict.

    This is the "ID card" of a video — container info, stream details,
    codec parameters, all in one structured output.
    """
    cmd = [
        _bin("ffprobe"),
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        str(input_path),
    ]
    logger.info("Running: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def run_ffprobe_frames(input_path: Path) -> str:
    """
    Extract per-frame data (picture type, size, timestamps) as CSV text.

    Returns raw CSV lines — one row per frame — with columns:
    ``key_frame, pict_type, pts_time, pkt_size, coded_picture_number``.
    """
    cmd = [
        _bin("ffprobe"),
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries",
        "frame=key_frame,pict_type,pts_time,pkt_size,coded_picture_number",
        "-of", "csv=p=0",
        str(input_path),
    ]
    logger.info("Running: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout


# ---------------------------------------------------------------------------
# FFmpeg execution
# ---------------------------------------------------------------------------

def run_ffmpeg(args: list[str], timeout: int = 300) -> subprocess.CompletedProcess:
    """
    Execute an FFmpeg command given as a list of arguments.

    The first element should be the ffmpeg binary or it will be prepended.

    Args:
        args: Full argument list, e.g. ["-i", "in.mp4", "-c:v", ...].
        timeout: Max seconds before the process is killed.

    Returns:
        The CompletedProcess instance.

    Raises:
        subprocess.CalledProcessError: If FFmpeg exits with non-zero code.
    """
    if args[0] not in ("ffmpeg", "ffmpeg.exe") and "ffmpeg" not in args[0]:
        args = [_bin("ffmpeg")] + args
    elif not Path(args[0]).is_absolute():
        args[0] = _bin("ffmpeg")

    logger.info("Running: %s", " ".join(args))
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        logger.error("FFmpeg stderr: %s", result.stderr[-500:])
        raise subprocess.CalledProcessError(
            result.returncode, args, result.stdout, result.stderr
        )
    return result
