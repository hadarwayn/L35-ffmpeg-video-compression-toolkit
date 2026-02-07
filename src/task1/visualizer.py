"""
Task 1 visualizations — three publication-quality graphs.

1. Frame Type Distribution (pie chart)
2. Frame Size Distribution by Type (box plot)
3. Bitrate Over Time (line chart with I-frame markers)

All saved as 300 DPI PNGs in both the task output folder and results/graphs/.
"""

import logging
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import (
    COLOR_I_FRAME, COLOR_P_FRAME, COLOR_B_FRAME,
    GRAPH_DPI, FIGURE_SIZE, BITRATE_WINDOW_SEC, GRAPHS_DIR,
)

logger = logging.getLogger("task1.viz")
_COLORS = {"I": COLOR_I_FRAME, "P": COLOR_P_FRAME, "B": COLOR_B_FRAME}


def generate_task1_graphs(frame_df: pd.DataFrame, output_dir: Path) -> None:
    """Create and save all three Task 1 graphs."""
    _pie_chart(frame_df, output_dir)
    _box_plot(frame_df, output_dir)
    _bitrate_line(frame_df, output_dir)


def _save(fig: plt.Figure, output_dir: Path, name: str) -> None:
    """Save to task output AND results/graphs/."""
    fig.savefig(output_dir / name, dpi=GRAPH_DPI, bbox_inches="tight")
    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy(output_dir / name, GRAPHS_DIR / name)
    plt.close(fig)
    logger.info("Saved %s", name)


def _pie_chart(df: pd.DataFrame, out: Path) -> None:
    """Pie chart showing I/P/B frame percentage distribution."""
    counts = df["pict_type"].value_counts()
    labels = [f"{t} ({counts[t]:,})" for t in counts.index]
    colors = [_COLORS.get(t, "#999") for t in counts.index]

    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    ax.pie(counts.values, labels=labels, colors=colors,
           autopct="%1.1f%%", startangle=140, textprops={"fontsize": 11})
    ax.set_title("Frame Type Distribution", fontsize=14, fontweight="bold")
    _save(fig, out, "frame_type_distribution.png")


def _box_plot(df: pd.DataFrame, out: Path) -> None:
    """Box plot of frame sizes (bytes) grouped by type I/P/B."""
    present = [t for t in ["I", "P", "B"] if t in df["pict_type"].values]
    data = [df.loc[df["pict_type"] == t, "pkt_size"].values for t in present]
    colors = [_COLORS.get(t, "#999") for t in present]

    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    bp = ax.boxplot(data, labels=present, patch_artist=True, notch=True)
    for patch, c in zip(bp["boxes"], colors):
        patch.set_facecolor(c)
        patch.set_alpha(0.7)

    ax.set_title("Frame Size Distribution by Type", fontsize=14, fontweight="bold")
    ax.set_xlabel("Frame Type")
    ax.set_ylabel("Packet Size (bytes)")
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    _save(fig, out, "frame_sizes_by_type.png")


def _bitrate_line(df: pd.DataFrame, out: Path) -> None:
    """Line chart of bitrate over time with I-frame vertical markers."""
    times = df["pts_time"].values.astype(float)
    sizes = df["pkt_size"].values.astype(float)
    if times[-1] == 0:
        return  # Cannot compute meaningful bitrate

    # 1-second windowed average bitrate (kbps)
    duration = times[-1]
    bins = np.arange(0, duration + BITRATE_WINDOW_SEC, BITRATE_WINDOW_SEC)
    indices = np.digitize(times, bins) - 1
    bitrate = np.zeros(len(bins) - 1)
    for i in range(len(bitrate)):
        mask = indices == i
        bitrate[i] = np.sum(sizes[mask]) * 8 / 1000 / BITRATE_WINDOW_SEC

    bin_centers = (bins[:-1] + bins[1:]) / 2

    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    ax.plot(bin_centers, bitrate, linewidth=1.5, color="#2E86AB", label="Bitrate (kbps)")

    # Mark I-frame positions
    i_times = times[df["pict_type"].values == "I"]
    for t in i_times:
        ax.axvline(t, color=COLOR_I_FRAME, alpha=0.25, linewidth=0.8)
    ax.axvline(t, color=COLOR_I_FRAME, alpha=0.25, linewidth=0.8, label="I-frame")

    ax.set_title("Bitrate Over Time", fontsize=14, fontweight="bold")
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Bitrate (kbps)")
    ax.legend()
    ax.grid(alpha=0.3, linestyle="--")
    _save(fig, out, "bitrate_over_time.png")
