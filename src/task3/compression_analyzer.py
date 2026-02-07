"""
Compression impact analysis — before vs. after overlay.

Compares file size, average bitrate, and average frame size between
the original video and the rectangle-overlay video to quantify how
adding new visual content affects H.264 compression efficiency.
"""

import json
import logging
from pathlib import Path
from typing import Any

from src.ffmpeg_utils import run_ffprobe_json

logger = logging.getLogger("task3.compression")


def compare_compression(
    original_path: Path,
    overlay_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    """
    Compare compression metrics for original vs. overlay video.

    Returns dict with original, modified, and delta metrics.
    Also saves ``compression_comparison.json``.
    """
    orig = _get_metrics(original_path)
    modif = _get_metrics(overlay_path)

    delta = {}
    for key in orig:
        o = orig[key]
        m = modif[key]
        delta[key] = {
            "absolute": round(m - o, 2),
            "percent": round((m - o) / o * 100, 2) if o else 0,
        }

    result: dict[str, Any] = {
        "original": orig,
        "modified": modif,
        "delta": delta,
    }

    out_path = output_dir / "compression_comparison.json"
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    logger.info("Saved compression_comparison.json")
    return result


def _get_metrics(video_path: Path) -> dict[str, float]:
    """
    Extract the three key metrics we compare.

    - file_size_bytes: total container size
    - avg_bitrate_kbps: overall bitrate
    - avg_frame_size_bytes: file_size / number_of_frames (approx)
    """
    raw = run_ffprobe_json(video_path)
    fmt = raw.get("format", {})
    video = next(
        (s for s in raw.get("streams", []) if s.get("codec_type") == "video"), {}
    )

    file_size = int(fmt.get("size", 0))
    bitrate = int(fmt.get("bit_rate", 0)) / 1000  # kbps
    duration = float(fmt.get("duration", 1))

    # Estimate total frames from duration * fps
    fps_str = video.get("r_frame_rate", "30/1")
    num, den = (int(x) for x in fps_str.split("/"))
    fps = num / den if den else 30
    total_frames = max(int(duration * fps), 1)
    avg_frame_size = file_size / total_frames

    return {
        "file_size_bytes": float(file_size),
        "avg_bitrate_kbps": round(bitrate, 2),
        "avg_frame_size_bytes": round(avg_frame_size, 2),
    }
