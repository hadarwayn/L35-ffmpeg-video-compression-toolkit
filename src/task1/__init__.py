"""
Task 1 — Video Statistics & Metadata Extraction.

Extracts metadata, analyzes GOP structure, computes frame statistics,
generates visualizations, and produces a human-readable report.
"""

import time
import logging
from pathlib import Path

from .metadata_extractor import extract_metadata
from .frame_statistics import extract_frame_data
from .gop_analyzer import analyze_gop
from .visualizer import generate_task1_graphs
from .report_generator import generate_report

logger = logging.getLogger("task1")


def run_task1(input_path: Path) -> None:
    """
    Orchestrate all Task 1 steps end-to-end.

    Pipeline: metadata -> frame stats -> GOP analysis -> graphs -> report.
    """
    from src.config import TASK1_OUTPUT_DIR

    start = time.time()
    logger.info("=== Task 1 START ===")

    print("  [1/5] Extracting metadata ...")
    metadata = extract_metadata(input_path, TASK1_OUTPUT_DIR)

    print("  [2/5] Extracting frame statistics ...")
    frame_df = extract_frame_data(input_path, TASK1_OUTPUT_DIR)

    print("  [3/5] Analyzing GOP structure ...")
    gop_info = analyze_gop(frame_df, TASK1_OUTPUT_DIR)

    print("  [4/5] Generating visualizations ...")
    generate_task1_graphs(frame_df, TASK1_OUTPUT_DIR)

    print("  [5/5] Writing summary report ...")
    generate_report(metadata, gop_info, frame_df, TASK1_OUTPUT_DIR)

    elapsed = time.time() - start
    logger.info("=== Task 1 DONE in %.1f s ===", elapsed)
    print(f"  Task 1 completed in {elapsed:.1f}s")
