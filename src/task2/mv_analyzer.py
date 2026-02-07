"""
Motion vector statistics analysis.

Produces ``mv_analysis.json`` with frame counts, B-frame presence,
and video characteristics that affect MV density.
"""

import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd

from src.ffmpeg_utils import run_ffprobe_json
from src.config import TASK1_OUTPUT_DIR

logger = logging.getLogger("task2.mv_stats")


def analyze_motion_vectors(
    input_path: Path, output_dir: Path
) -> dict[str, Any]:
    """
    Compute motion-vector related statistics and save to JSON.

    Uses per-frame data (from Task 1 CSV if available, else re-extracts)
    and video metadata to compile the analysis.
    """
    frame_df = _load_frame_data(input_path)
    meta = run_ffprobe_json(input_path)
    video_stream = next(
        (s for s in meta.get("streams", []) if s.get("codec_type") == "video"), {}
    )

    total = len(frame_df)
    counts = frame_df["pict_type"].value_counts().to_dict()
    i_count = counts.get("I", 0)
    b_count = counts.get("B", 0)

    result: dict[str, Any] = {
        "total_frames_analyzed": total,
        "frames_with_motion_vectors": total - i_count,
        "frames_without_motion_vectors": i_count,
        "has_b_frames": b_count > 0,
        "b_frame_count": b_count,
        "frame_type_counts": counts,
        "video_characteristics": {
            "resolution": f"{video_stream.get('width')}x{video_stream.get('height')}",
            "frame_rate": video_stream.get("r_frame_rate"),
            "codec": video_stream.get("codec_name"),
            "profile": video_stream.get("profile"),
        },
        "color_legend": {
            "green": "Forward MV (P-frame) — block came from a previous frame",
            "blue": "Forward MV (B-frame) — block came from a previous frame",
            "red": "Backward MV (B-frame) — block came from a future frame",
            "grid": "Macroblock boundaries — 16x16 pixel blocks",
        },
    }

    out_path = output_dir / "mv_analysis.json"
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    logger.info("Saved mv_analysis.json")
    return result


def _load_frame_data(input_path: Path) -> pd.DataFrame:
    """Load frame data from Task 1 CSV or re-extract if not available."""
    csv_path = TASK1_OUTPUT_DIR / "frame_statistics.csv"
    if csv_path.exists():
        return pd.read_csv(csv_path)

    # Fall back to fresh extraction
    import io
    from src.ffmpeg_utils import run_ffprobe_frames

    raw = run_ffprobe_frames(input_path)
    cols = ["key_frame", "pts_time", "pkt_size", "pict_type", "coded_picture_number"]
    df = pd.read_csv(io.StringIO(raw), header=None, names=cols)
    df.insert(0, "frame_number", range(len(df)))
    return df
