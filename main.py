#!/usr/bin/env python3
"""
L35 — Advanced Video Compression Analysis & Visualization Toolkit.

Single entry point that runs all three tasks (or a selected one):
  Task 1: Video statistics & metadata extraction
  Task 2: Motion vector & macroblock visualization
  Task 3: Moving & rotating rectangle overlay

Usage:
    python main.py              # Run all tasks
    python main.py --task 1     # Run only Task 1
    python main.py --task 2     # Run only Task 2
    python main.py --task 3     # Run only Task 3
    python main.py --input path/to/video.mp4
"""

import argparse
import sys
import time
from pathlib import Path

# Ensure the project root is on sys.path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import LOG_CONFIG_PATH
from src.utils.paths import get_input_video, ensure_output_dirs
from src.utils.logger import setup_logger, print_log_status
from src.utils.validators import validate_input_video, validate_ffmpeg


def main() -> None:
    """Parse arguments, validate environment, and run selected tasks."""
    args = _parse_args()
    logger = setup_logger("main", LOG_CONFIG_PATH)

    print("=" * 60)
    print("  L35 — Video Compression Analysis Toolkit")
    print("=" * 60)

    # --- Validate environment ---
    print("\nValidating environment ...")
    validate_ffmpeg()
    print("  FFmpeg and FFprobe OK")

    # --- Locate input video ---
    if args.input:
        video_path = Path(args.input)
    else:
        video_path = get_input_video()
    validate_input_video(video_path)
    print(f"  Input video: {video_path.name}")

    ensure_output_dirs()
    logger.info("Starting — video=%s, task=%s", video_path.name, args.task or "all")

    # --- Run tasks ---
    start = time.time()
    tasks_to_run = [args.task] if args.task else [1, 2, 3]

    for t in tasks_to_run:
        _run_task(int(t), video_path, logger)

    elapsed = time.time() - start
    print(f"\nAll done in {elapsed:.1f}s")
    print("Output saved to: output/")
    print_log_status(logger)


def _run_task(task_num: int, video_path: Path, logger) -> None:
    """Dispatch to the appropriate task runner."""
    print(f"\n{'='*60}")
    print(f"  TASK {task_num}")
    print(f"{'='*60}")

    if task_num == 1:
        from src.task1 import run_task1
        run_task1(video_path)
    elif task_num == 2:
        from src.task2 import run_task2
        run_task2(video_path)
    elif task_num == 3:
        from src.task3 import run_task3
        run_task3(video_path)
    else:
        print(f"  Unknown task number: {task_num}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="L35 Video Compression Toolkit")
    parser.add_argument("--task", type=int, choices=[1, 2, 3],
                        help="Run a single task (1, 2, or 3)")
    parser.add_argument("--input", type=str,
                        help="Path to input MP4 video")
    return parser.parse_args()


if __name__ == "__main__":
    main()
