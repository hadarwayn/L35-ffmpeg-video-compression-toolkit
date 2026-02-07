"""
GOP (Group of Pictures) structure analysis.

Detects the GOP pattern (e.g. IBBBPBBBP), calculates GOP length,
determines if it is fixed or variable, and computes I-frame statistics.
"""

import json
import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger("task1.gop")


def analyze_gop(
    frame_df: pd.DataFrame, output_dir: Path
) -> dict[str, Any]:
    """
    Analyse the GOP structure from per-frame data.

    Returns dict with pattern, lengths, I-frame stats, bitrate-per-type,
    and peak bitrate info. Also saves ``gop_analysis.json``.
    """
    types = frame_df["pict_type"].values
    sizes = frame_df["pkt_size"].values.astype(float)
    times = frame_df["pts_time"].values.astype(float)

    # --- frame type counts ---
    counts = frame_df["pict_type"].value_counts().to_dict()
    total = len(frame_df)

    # --- detect GOP pattern ---
    pattern, gop_lengths = _detect_gop(types)
    gop_lengths_arr = np.array(gop_lengths) if gop_lengths else np.array([total])
    is_fixed = bool(np.std(gop_lengths_arr) < 1.0) if len(gop_lengths_arr) > 1 else True

    # --- I-frame statistics ---
    i_sizes = sizes[types == "I"]
    i_indices = np.where(types == "I")[0]
    i_distances = np.diff(i_indices) if len(i_indices) > 1 else np.array([0])

    fps = _estimate_fps(times, total)
    i_stats = _iframe_stats(i_sizes, i_distances, fps)

    # --- bitrate per frame type ---
    bitrate_by_type = {
        t: float(np.mean(sizes[types == t])) for t in ["I", "P", "B"] if (types == t).any()
    }

    # --- peak bitrate moment ---
    peak_idx = int(np.argmax(sizes))
    peak_info = {
        "frame_number": peak_idx,
        "timestamp_sec": round(float(times[peak_idx]), 3),
        "size_bytes": int(sizes[peak_idx]),
    }

    result: dict[str, Any] = {
        "gop_pattern": pattern,
        "gop_lengths": gop_lengths,
        "avg_gop_length": round(float(np.mean(gop_lengths_arr)), 1),
        "is_fixed_gop": is_fixed,
        "frame_counts": counts,
        "total_frames": total,
        "i_frame_stats": i_stats,
        "avg_size_by_type_bytes": bitrate_by_type,
        "peak_bitrate": peak_info,
    }

    (output_dir / "gop_analysis.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    logger.info("Saved gop_analysis.json")
    return result


# --------------------------------------------------------------------------
# Internal helpers
# --------------------------------------------------------------------------

def _detect_gop(types: np.ndarray) -> tuple[str, list[int]]:
    """Return the first GOP pattern string and a list of all GOP lengths."""
    i_positions = np.where(types == "I")[0]
    if len(i_positions) < 2:
        return "".join(types[:30]), [len(types)]

    # First full GOP: from first I-frame to (but not including) second I-frame
    first_gop = types[i_positions[0]: i_positions[1]]
    pattern = "".join(first_gop)

    lengths = [int(i_positions[i + 1] - i_positions[i]) for i in range(len(i_positions) - 1)]
    return pattern, lengths


def _estimate_fps(times: np.ndarray, total: int) -> float:
    """Estimate FPS from PTS timestamps."""
    duration = times[-1] - times[0] if len(times) > 1 else 1.0
    return total / duration if duration > 0 else 30.0


def _iframe_stats(sizes: np.ndarray, distances: np.ndarray, fps: float) -> dict:
    """Compute aggregate I-frame statistics (count, avg/min/max/std size, interval)."""
    if len(sizes) == 0:
        return {}
    return {
        "count": int(len(sizes)),
        "avg_size_bytes": round(float(np.mean(sizes)), 1),
        "min_size_bytes": int(np.min(sizes)),
        "max_size_bytes": int(np.max(sizes)),
        "std_size_bytes": round(float(np.std(sizes)), 1),
        "avg_distance_frames": round(float(np.mean(distances)), 1),
        "avg_distance_sec": round(float(np.mean(distances)) / fps, 3) if fps else 0,
    }
