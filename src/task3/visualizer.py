"""
Task 3 visualization — compression impact bar chart.

Grouped bar chart comparing original vs. modified video for:
file size, average bitrate, and average frame size.
"""

import logging
import shutil
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from src.config import GRAPH_DPI, FIGURE_SIZE, GRAPHS_DIR

logger = logging.getLogger("task3.viz")


def generate_compression_chart(
    comparison: dict[str, Any], output_dir: Path
) -> None:
    """
    Create a grouped bar chart showing original vs. overlay metrics.

    Each metric group has two bars (original = blue, modified = red)
    with percentage-increase labels on top.
    """
    orig = comparison["original"]
    modif = comparison["modified"]
    delta = comparison["delta"]

    metrics = ["file_size_bytes", "avg_bitrate_kbps", "avg_frame_size_bytes"]
    labels = ["File Size (bytes)", "Avg Bitrate (kbps)", "Avg Frame Size (bytes)"]

    orig_vals = np.array([orig[m] for m in metrics])
    mod_vals = np.array([modif[m] for m in metrics])

    x = np.arange(len(metrics))
    width = 0.35

    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    bars1 = ax.bar(x - width / 2, orig_vals, width, label="Original", color="#2196F3")
    bars2 = ax.bar(x + width / 2, mod_vals, width, label="With Overlay", color="#F44336")

    # Add percentage labels above modified bars
    for i, m in enumerate(metrics):
        pct = delta[m]["percent"]
        ax.annotate(
            f"+{pct:.1f}%",
            xy=(x[i] + width / 2, mod_vals[i]),
            xytext=(0, 8),
            textcoords="offset points",
            ha="center", fontsize=9, fontweight="bold",
        )

    ax.set_title("Compression Impact: Original vs. Overlay",
                 fontsize=14, fontweight="bold")
    ax.set_ylabel("Value")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.legend()
    ax.grid(axis="y", alpha=0.3, linestyle="--")

    plt.tight_layout()
    name = "compression_impact.png"
    fig.savefig(output_dir / name, dpi=GRAPH_DPI, bbox_inches="tight")
    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy(output_dir / name, GRAPHS_DIR / name)
    plt.close(fig)
    logger.info("Saved %s", name)
