"""
Task 2 — Motion Vector & Macroblock Visualization.

Generates an overlay video showing motion vectors and macroblock grid,
extracts representative sample frames, and computes MV statistics.
"""

import time
import logging
from pathlib import Path

from .mv_visualizer import generate_mv_video
from .frame_extractor import extract_sample_frames
from .mv_analyzer import analyze_motion_vectors

logger = logging.getLogger("task2")


def run_task2(input_path: Path) -> None:
    """
    Orchestrate all Task 2 steps.

    Pipeline: overlay video -> sample frames -> MV statistics.
    """
    from src.config import TASK2_OUTPUT_DIR, TASK2_FRAMES_DIR

    start = time.time()
    logger.info("=== Task 2 START ===")

    print("  [1/3] Generating motion vector overlay video ...")
    overlay_path = generate_mv_video(input_path, TASK2_OUTPUT_DIR)

    print("  [2/3] Extracting sample frames ...")
    extract_sample_frames(input_path, overlay_path, TASK2_FRAMES_DIR)

    print("  [3/3] Computing MV statistics ...")
    analyze_motion_vectors(input_path, TASK2_OUTPUT_DIR)

    elapsed = time.time() - start
    logger.info("=== Task 2 DONE in %.1f s ===", elapsed)
    print(f"  Task 2 completed in {elapsed:.1f}s")
