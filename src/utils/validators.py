"""
Input and environment validation for the L35 toolkit.

Checks that the input video exists and is MP4, and that FFmpeg/FFprobe
are installed with the features we need (libx264 encoder, codecview filter).
"""

import subprocess
from pathlib import Path

from src.config import FFMPEG_DIR


def _ffmpeg_bin(name: str = "ffmpeg") -> str:
    """Return the full path string to an FFmpeg binary, or just the name."""
    if FFMPEG_DIR and (FFMPEG_DIR / f"{name}.exe").exists():
        return str(FFMPEG_DIR / f"{name}.exe")
    return name


def validate_input_video(path: Path) -> Path:
    """
    Verify the input file exists and has an .mp4 extension.

    Args:
        path: Path to the video file.

    Returns:
        The validated Path (unchanged).

    Raises:
        FileNotFoundError: File does not exist.
        ValueError: File is not an MP4.
    """
    if not path.exists():
        raise FileNotFoundError(f"Input video not found: {path}")
    if path.suffix.lower() != ".mp4":
        raise ValueError(
            f"Expected an .mp4 file, got '{path.suffix}'. "
            "Please provide an H.264 MP4 video."
        )
    return path


def validate_ffmpeg() -> None:
    """
    Ensure FFmpeg and FFprobe are accessible and have required features.

    Checks:
    1. ``ffmpeg -version`` runs successfully.
    2. ``ffprobe -version`` runs successfully.
    3. libx264 encoder is available.
    4. codecview filter is available.

    Raises:
        RuntimeError: If any check fails, with a helpful fix message.
    """
    _check_binary("ffmpeg")
    _check_binary("ffprobe")
    _check_encoder("libx264")
    _check_filter("codecview")


def _check_binary(name: str) -> None:
    """Verify that a binary (ffmpeg / ffprobe) can be executed."""
    try:
        subprocess.run(
            [_ffmpeg_bin(name), "-version"],
            capture_output=True,
            check=True,
        )
    except FileNotFoundError:
        raise RuntimeError(
            f"'{name}' not found. Install FFmpeg: "
            "https://ffmpeg.org/download.html"
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"'{name}' failed: {exc.stderr.decode()}")


def _check_encoder(encoder: str) -> None:
    """Verify that a specific encoder (e.g. libx264) is compiled in."""
    result = subprocess.run(
        [_ffmpeg_bin(), "-encoders"],
        capture_output=True,
        text=True,
    )
    if encoder not in result.stdout:
        raise RuntimeError(
            f"FFmpeg lacks the '{encoder}' encoder. "
            "Install a full build: https://ffmpeg.org/download.html"
        )


def _check_filter(filt: str) -> None:
    """Verify that a specific filter (e.g. codecview) is compiled in."""
    result = subprocess.run(
        [_ffmpeg_bin(), "-filters"],
        capture_output=True,
        text=True,
    )
    if filt not in result.stdout:
        raise RuntimeError(
            f"FFmpeg lacks the '{filt}' filter. "
            "Install a full build: https://ffmpeg.org/download.html"
        )
