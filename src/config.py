"""
Central configuration for the L35 Video Compression Toolkit.

All 'magic numbers' and constants are defined here with explanations.
This ensures consistent settings across all tasks and easy tuning.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Directory paths (all relative to project root)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = PROJECT_ROOT / "input"
OUTPUT_DIR = PROJECT_ROOT / "output"
RESULTS_DIR = PROJECT_ROOT / "results"
GRAPHS_DIR = RESULTS_DIR / "graphs"
LOGS_DIR = PROJECT_ROOT / "logs"
LOG_CONFIG_PATH = LOGS_DIR / "config" / "log_config.json"

# Output subdirectories — names must match PRD exactly (spaces included)
TASK1_OUTPUT_DIR = OUTPUT_DIR / "task 1 - video information"
TASK2_OUTPUT_DIR = OUTPUT_DIR / "task 2 - motion vectors"
TASK2_FRAMES_DIR = TASK2_OUTPUT_DIR / "sample_frames"
TASK3_OUTPUT_DIR = OUTPUT_DIR / "task 3 - rotating rectangle"

# ---------------------------------------------------------------------------
# FFmpeg binary paths — winget installs to this location
# Set to None to use system PATH; override if needed
# ---------------------------------------------------------------------------
_WINGET_FFMPEG = Path.home() / (
    "AppData/Local/Microsoft/WinGet/Packages/"
    "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/"
    "ffmpeg-8.0.1-full_build/bin"
)
FFMPEG_DIR: Path | None = _WINGET_FFMPEG if _WINGET_FFMPEG.exists() else None

# ---------------------------------------------------------------------------
# Encoding parameters (used by Task 2 & Task 3 for re-encoding)
# ---------------------------------------------------------------------------
CRF_VALUE = 18          # Constant Rate Factor: 18 = visually lossless
PRESET = "medium"       # Speed/compression trade-off for libx264

# ---------------------------------------------------------------------------
# Task 3: Rectangle overlay parameters
# ---------------------------------------------------------------------------
RECT_WIDTH = 200        # Rectangle width in pixels
RECT_HEIGHT = 100       # Rectangle height in pixels
RECT_OPACITY = 0.7      # 70% opaque — background visible through rectangle
ROTATION_PERIOD = 5.0   # Seconds for one full 360-degree rotation
VELOCITY_X = 5          # Horizontal speed in pixels per frame
VELOCITY_Y = 3          # Vertical speed in pixels per frame
RECT_COLOR = (0, 0, 255)  # BGR red — high contrast on most backgrounds

# ---------------------------------------------------------------------------
# Visualization / graph styling
# ---------------------------------------------------------------------------
GRAPH_DPI = 300                          # Publication-quality resolution
FIGURE_SIZE = (10, 6)                    # Default figure size in inches
COLOR_I_FRAME = "#2196F3"               # Blue for I-frames
COLOR_P_FRAME = "#4CAF50"               # Green for P-frames
COLOR_B_FRAME = "#FF9800"               # Orange for B-frames
BITRATE_WINDOW_SEC = 1.0                # Averaging window for bitrate chart

# ---------------------------------------------------------------------------
# Logging defaults (if config file not found)
# ---------------------------------------------------------------------------
LOG_MAX_LINES = 1000    # Max lines per log file before rotation
LOG_MAX_FILES = 5       # Max log files kept on disk
