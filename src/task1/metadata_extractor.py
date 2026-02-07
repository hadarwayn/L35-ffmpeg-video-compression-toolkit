"""
Extract full video metadata using FFprobe JSON output.

Parses container info (format, duration, bitrate, size), video stream
(resolution, fps, codec, profile, pixel format, color info), and audio
stream (codec, sample rate, channels, bitrate).
"""

import json
import logging
from pathlib import Path
from typing import Any

from src.ffmpeg_utils import run_ffprobe_json

logger = logging.getLogger("task1.metadata")


def extract_metadata(
    input_path: Path, output_dir: Path
) -> dict[str, Any]:
    """
    Run ffprobe on *input_path*, save raw JSON, return structured dict.

    The returned dict has three top-level keys:
    ``container``, ``video``, ``audio`` (audio may be ``None``).
    """
    raw = run_ffprobe_json(input_path)

    # Persist the raw ffprobe output for reference
    (output_dir / "metadata.json").write_text(
        json.dumps(raw, indent=2), encoding="utf-8"
    )
    logger.info("Saved metadata.json")

    return _structure(raw)


def _structure(raw: dict) -> dict[str, Any]:
    """Reorganise raw ffprobe JSON into a cleaner hierarchy."""
    fmt = raw.get("format", {})
    streams = raw.get("streams", [])

    video = next((s for s in streams if s.get("codec_type") == "video"), {})
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)

    result: dict[str, Any] = {
        "container": _parse_container(fmt),
        "video": _parse_video(video),
        "audio": _parse_audio(audio) if audio else None,
    }
    return result


def _parse_container(fmt: dict) -> dict[str, Any]:
    """Extract container-level info: format, duration, bitrate, size."""
    return {
        "format_name": fmt.get("format_name"),
        "duration_sec": float(fmt.get("duration", 0)),
        "bitrate_kbps": int(fmt.get("bit_rate", 0)) / 1000,
        "file_size_bytes": int(fmt.get("size", 0)),
        "nb_streams": int(fmt.get("nb_streams", 0)),
    }


def _parse_video(v: dict) -> dict[str, Any]:
    """Extract video stream fields: resolution, fps, codec, pix_fmt, colour."""
    fps_str = v.get("r_frame_rate", "0/1")
    num, den = (int(x) for x in fps_str.split("/"))
    fps = num / den if den else 0

    avg_str = v.get("avg_frame_rate", "0/1")
    anum, aden = (int(x) for x in avg_str.split("/"))
    avg_fps = anum / aden if aden else 0

    return {
        "width": v.get("width"),
        "height": v.get("height"),
        "display_aspect_ratio": v.get("display_aspect_ratio"),
        "fps": round(fps, 3),
        "avg_fps": round(avg_fps, 3),
        "codec_name": v.get("codec_name"),
        "profile": v.get("profile"),
        "level": v.get("level"),
        "pix_fmt": v.get("pix_fmt"),
        "color_space": v.get("color_space"),
        "color_primaries": v.get("color_primaries"),
        "color_transfer": v.get("color_transfer"),
        "bit_depth": v.get("bits_per_raw_sample"),
    }


def _parse_audio(a: dict) -> dict[str, Any]:
    """Extract audio stream fields: codec, sample rate, channels, bitrate."""
    return {
        "codec_name": a.get("codec_name"),
        "sample_rate": a.get("sample_rate"),
        "channels": a.get("channels"),
        "channel_layout": a.get("channel_layout"),
        "bitrate_kbps": int(a.get("bit_rate", 0)) / 1000,
    }
