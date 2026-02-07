"""
Task 3 — Moving & Rotating Rectangle Overlay.

Demonstrates the decompress -> edit -> recompress pipeline by drawing
a semi-transparent, bouncing, rotating rectangle on every frame,
then measuring the compression impact.
"""

import time
import logging
from pathlib import Path

from .rectangle_overlay import render_overlay
from .compression_analyzer import compare_compression
from .visualizer import generate_compression_chart

logger = logging.getLogger("task3")


def run_task3(input_path: Path) -> None:
    """
    Orchestrate all Task 3 steps.

    Pipeline: render overlay -> analyze compression -> generate chart.
    """
    from src.config import TASK3_OUTPUT_DIR

    start = time.time()
    logger.info("=== Task 3 START ===")

    print("  [1/3] Rendering rectangle overlay ...")
    overlay_path = render_overlay(input_path, TASK3_OUTPUT_DIR)

    print("  [2/3] Analyzing compression impact ...")
    comparison = compare_compression(input_path, overlay_path, TASK3_OUTPUT_DIR)

    print("  [3/3] Generating compression chart ...")
    generate_compression_chart(comparison, TASK3_OUTPUT_DIR)

    elapsed = time.time() - start
    logger.info("=== Task 3 DONE in %.1f s ===", elapsed)
    print(f"  Task 3 completed in {elapsed:.1f}s")
