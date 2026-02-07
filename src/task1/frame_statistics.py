"""
Per-frame statistics extraction and CSV generation.

Uses FFprobe to get one row per video frame with:
frame_number, pict_type (I/P/B), key_frame flag, packet size, PTS time.
"""

import io
import logging
from pathlib import Path

import pandas as pd

from src.ffmpeg_utils import run_ffprobe_frames

logger = logging.getLogger("task1.frames")

# Column names matching actual ffprobe CSV output order
# (ffprobe emits columns alphabetically, not in -show_entries order)
_COLUMNS = ["key_frame", "pts_time", "pkt_size", "pict_type", "coded_picture_number"]


def extract_frame_data(input_path: Path, output_dir: Path) -> pd.DataFrame:
    """
    Extract per-frame data from *input_path* and save as CSV.

    Returns:
        DataFrame with columns:
        frame_number, pict_type, key_frame, pkt_size, pts_time.
    """
    raw_csv = run_ffprobe_frames(input_path)

    df = pd.read_csv(
        io.StringIO(raw_csv),
        header=None,
        names=_COLUMNS,
    )

    # Coerce numeric columns (ffprobe may emit 'N/A' for some fields)
    df["pkt_size"] = pd.to_numeric(df["pkt_size"], errors="coerce").fillna(0).astype(int)
    df["pts_time"] = pd.to_numeric(df["pts_time"], errors="coerce").fillna(0.0)
    df["key_frame"] = pd.to_numeric(df["key_frame"], errors="coerce").fillna(0).astype(int)

    # Add a simple sequential frame number starting at 0
    df.insert(0, "frame_number", range(len(df)))

    # Reorder columns to match PRD specification
    df = df[["frame_number", "pict_type", "key_frame", "pkt_size", "pts_time"]]

    csv_path = output_dir / "frame_statistics.csv"
    df.to_csv(csv_path, index=False)
    logger.info("Saved frame_statistics.csv (%d frames)", len(df))

    return df
