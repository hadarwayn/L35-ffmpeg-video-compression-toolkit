"""
Core rendering pipeline: decompress -> draw rectangle -> recompress.

Reads every frame with OpenCV, draws a semi-transparent rotating
rectangle, writes to a temp file, then remuxes audio (if present)
via FFmpeg to produce the final output.
"""

import csv
import logging
import subprocess
from pathlib import Path

import cv2
import numpy as np

from src.config import (
    RECT_OPACITY, RECT_COLOR, CRF_VALUE, PRESET, TASK3_OUTPUT_DIR, FFMPEG_DIR,
)
from src.ffmpeg_utils import _bin
from .motion_logic import RectangleState, draw_rotated_rectangle

logger = logging.getLogger("task3.overlay")


def render_overlay(input_path: Path, output_dir: Path) -> Path:
    """
    Render the rectangle overlay on every frame and save the result.

    Steps:
    1. Open video with OpenCV, read resolution and fps.
    2. For each frame: compute position/angle, draw rectangle, write frame.
    3. If original has audio, remux audio track into the output via FFmpeg.

    Returns:
        Path to the final ``overlay_video.mp4``.
    """
    cap = cv2.VideoCapture(str(input_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Temp output (no audio) — will be remuxed afterwards
    temp_path = output_dir / "_temp_overlay.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(temp_path), fourcc, fps, (w, h))

    state = RectangleState(w, h, fps)
    log_rows: list[list] = []

    for n in range(total):
        ok, frame = cap.read()
        if not ok:
            break

        cx, cy, angle, vx, vy = state.update(n)
        draw_rotated_rectangle(frame, cx, cy, angle, RECT_OPACITY, RECT_COLOR)
        writer.write(frame)

        log_rows.append([n, round(n / fps, 4), round(cx, 1), round(cy, 1),
                         round(angle, 2), round(vx, 1), round(vy, 1)])

        if n % 200 == 0:
            logger.info("Frame %d / %d", n, total)

    cap.release()
    writer.release()

    # Save position log CSV
    _write_log(log_rows, output_dir)

    # Remux: re-encode video with libx264 + copy audio if present
    final_path = output_dir / "overlay_video.mp4"
    _remux(input_path, temp_path, final_path)
    temp_path.unlink(missing_ok=True)

    logger.info("Created %s", final_path.name)
    return final_path


def _write_log(rows: list[list], output_dir: Path) -> None:
    """Save per-frame rectangle state as CSV."""
    path = output_dir / "rectangle_log.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["frame_number", "timestamp_sec", "center_x", "center_y",
                     "angle_degrees", "velocity_x", "velocity_y"])
        w.writerows(rows)
    logger.info("Saved rectangle_log.csv (%d rows)", len(rows))


def _remux(original: Path, temp_video: Path, final: Path) -> None:
    """Re-encode video to H.264 and copy audio from original if present."""
    cmd = [
        _bin("ffmpeg"), "-y",
        "-i", str(temp_video),
        "-i", str(original),
        "-map", "0:v:0",
        "-map", "1:a?",
        "-c:v", "libx264", "-crf", str(CRF_VALUE), "-preset", PRESET,
        "-c:a", "copy",
        "-shortest",
        str(final),
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=600)
