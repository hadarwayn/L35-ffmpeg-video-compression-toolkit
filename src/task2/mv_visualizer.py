"""
Generate a motion-vector overlay video using FFmpeg's ``codecview`` filter.

The output shows:
- Green arrows for P-frame forward motion vectors
- Blue arrows for B-frame forward motion vectors
- Red arrows for B-frame backward motion vectors
- 16x16 macroblock grid on every frame
"""

import logging
from pathlib import Path

from src.config import CRF_VALUE, PRESET
from src.ffmpeg_utils import run_ffmpeg

logger = logging.getLogger("task2.mv_viz")


def generate_mv_video(input_path: Path, output_dir: Path) -> Path:
    """
    Create ``motion_vectors_overlay.mp4`` with MV arrows and block grid.

    Args:
        input_path: Path to the original H.264 MP4 video.
        output_dir: Directory where the overlay video will be saved.

    Returns:
        Path to the generated overlay video.

    How it works:
        ``-flags2 +export_mvs`` tells the decoder to expose motion vector data.
        ``codecview=mv=pf+bf+bb`` draws the arrows:
            pf = P-frame forward, bf = B-frame forward, bb = B-frame backward.
        ``:block=1`` draws the 16x16 macroblock grid on every frame.
    """
    output_path = output_dir / "motion_vectors_overlay.mp4"

    args = [
        "ffmpeg",
        "-y",                          # Overwrite if exists
        "-flags2", "+export_mvs",      # Export motion vector side data
        "-i", str(input_path),
        "-vf", "codecview=mv=pf+bf+bb:block=1",
        "-c:v", "libx264",
        "-crf", str(CRF_VALUE),
        "-preset", PRESET,
        "-an",                         # Drop audio (visual-only output)
        str(output_path),
    ]

    run_ffmpeg(args, timeout=600)
    logger.info("Created %s", output_path.name)
    return output_path
