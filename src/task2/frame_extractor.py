"""
Extract representative sample frames from the MV overlay video.

Saves 5-8 PNGs categorised by frame type and motion intensity:
- I-frame (grid only, no arrows)
- P-frames with green forward MVs
- B-frame with bi-directional MVs (if present)
- Highest-motion frame (auto-detected)
- Lowest-motion frame (auto-detected)
"""

import logging
from pathlib import Path

from src.ffmpeg_utils import run_ffmpeg, run_ffprobe_frames
from src.config import TASK1_OUTPUT_DIR

logger = logging.getLogger("task2.frames")


def extract_sample_frames(
    original_path: Path,
    overlay_path: Path,
    frames_dir: Path,
) -> None:
    """
    Pull representative frames from the overlay video.

    Uses FFmpeg ``select`` filter to pick specific frame types,
    and heuristic packet-size ranking for motion intensity.
    """
    frames_dir.mkdir(parents=True, exist_ok=True)

    _extract_by_type(overlay_path, frames_dir, "I", "frame_iframe_001.png", count=1)
    _extract_by_type(overlay_path, frames_dir, "P", "frame_pframe_050.png", count=1)
    _extract_by_type(overlay_path, frames_dir, "P", "frame_pframe_100.png", count=1, skip=60)
    _extract_by_type(overlay_path, frames_dir, "B", "frame_bframe_075.png", count=1)
    _extract_motion_extremes(original_path, overlay_path, frames_dir)


def _extract_by_type(
    video: Path, out_dir: Path, ptype: str, filename: str,
    count: int = 1, skip: int = 0,
) -> None:
    """Extract *count* frame(s) of a given picture type via FFmpeg select."""
    # select filter: eq(pict_type,I) where I=1, P=2, B=3
    type_map = {"I": "I", "P": "P", "B": "B"}
    select_expr = f"eq(pict_type\\,{type_map[ptype]})"

    out_path = out_dir / filename
    args = [
        "ffmpeg", "-y",
        "-flags2", "+export_mvs",
        "-i", str(video),
        "-vf", f"select='{select_expr}',setpts=N/TB",
        "-vsync", "vfr",
        "-frames:v", str(count),
        "-ss", str(skip / 30) if skip else "0",
        str(out_path),
    ]

    try:
        run_ffmpeg(args, timeout=120)
        logger.info("Extracted %s (%s-frame)", filename, ptype)
    except Exception as exc:
        logger.warning("Could not extract %s-frame: %s", ptype, exc)


def _extract_motion_extremes(
    original: Path, overlay: Path, out_dir: Path
) -> None:
    """
    Auto-detect high-motion and low-motion frames by packet size.

    Larger packets in P/B-frames indicate more residual data,
    which correlates with higher motion activity.
    """
    import pandas as pd
    import numpy as np

    csv_path = TASK1_OUTPUT_DIR / "frame_statistics.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
    else:
        import io
        raw = run_ffprobe_frames(original)
        cols = ["key_frame", "pts_time", "pkt_size", "pict_type", "coded_picture_number"]
        df = pd.read_csv(io.StringIO(raw), header=None, names=cols)
        df["pkt_size"] = pd.to_numeric(df["pkt_size"], errors="coerce").fillna(0)
        df.insert(0, "frame_number", range(len(df)))

    # Only consider P/B frames for motion detection
    pb = df[df["pict_type"].isin(["P", "B"])].copy()
    if pb.empty:
        return

    hi_idx = int(pb.loc[pb["pkt_size"].idxmax(), "frame_number"])
    lo_idx = int(pb.loc[pb["pkt_size"].idxmin(), "frame_number"])

    _extract_frame_number(overlay, out_dir, hi_idx, "frame_high_motion.png")
    _extract_frame_number(overlay, out_dir, lo_idx, "frame_low_motion.png")


def _extract_frame_number(video: Path, out_dir: Path, n: int, fname: str) -> None:
    """Extract a specific frame by number from the overlay video."""
    args = [
        "ffmpeg", "-y",
        "-i", str(video),
        "-vf", f"select='eq(n\\,{n})'",
        "-vsync", "vfr",
        "-frames:v", "1",
        str(out_dir / fname),
    ]
    try:
        run_ffmpeg(args, timeout=60)
        logger.info("Extracted %s (frame #%d)", fname, n)
    except Exception as exc:
        logger.warning("Could not extract frame #%d: %s", n, exc)
