"""
Rectangle movement and rotation mathematics.

The rectangle starts at the centre of the video, moves diagonally,
bounces off the frame edges, and rotates 360 degrees every 5 seconds.
Think of it like a DVD screensaver logo bouncing around the screen.
"""

import math
from typing import Tuple

import numpy as np

from src.config import (
    RECT_WIDTH, RECT_HEIGHT, VELOCITY_X, VELOCITY_Y, ROTATION_PERIOD,
)


class RectangleState:
    """Track position, velocity, and rotation of the overlay rectangle."""

    def __init__(self, frame_w: int, frame_h: int, fps: float) -> None:
        """
        Initialise the rectangle at the centre of the frame.

        Args:
            frame_w: Video frame width in pixels.
            frame_h: Video frame height in pixels.
            fps: Frames per second of the video.
        """
        self.frame_w = frame_w
        self.frame_h = frame_h
        self.fps = fps

        # Start at centre
        self.cx = frame_w / 2.0
        self.cy = frame_h / 2.0
        self.vx = float(VELOCITY_X)
        self.vy = float(VELOCITY_Y)

    def update(self, frame_num: int) -> Tuple[float, float, float, float, float]:
        """
        Advance the rectangle by one frame.

        Returns:
            (cx, cy, angle_deg, vx, vy) after the update.
        """
        # Move
        self.cx += self.vx
        self.cy += self.vy

        # Bounce off edges — keep rectangle fully inside the frame.
        # The bounding box of a rotated 200x100 rect can be up to ~224 px
        # so we use half the diagonal as safe margin.
        half_diag = math.sqrt(RECT_WIDTH**2 + RECT_HEIGHT**2) / 2.0

        if self.cx - half_diag < 0:
            self.cx = half_diag
            self.vx = abs(self.vx)
        elif self.cx + half_diag > self.frame_w:
            self.cx = self.frame_w - half_diag
            self.vx = -abs(self.vx)

        if self.cy - half_diag < 0:
            self.cy = half_diag
            self.vy = abs(self.vy)
        elif self.cy + half_diag > self.frame_h:
            self.cy = self.frame_h - half_diag
            self.vy = -abs(self.vy)

        # Rotation: 360 degrees every ROTATION_PERIOD seconds
        angle_deg = (360.0 * frame_num) / (self.fps * ROTATION_PERIOD) % 360.0

        return self.cx, self.cy, angle_deg, self.vx, self.vy


def draw_rotated_rectangle(
    frame: np.ndarray,
    cx: float, cy: float,
    angle_deg: float,
    opacity: float,
    color: Tuple[int, int, int],
) -> np.ndarray:
    """
    Draw a semi-transparent rotated rectangle on *frame* (in-place).

    Uses OpenCV's ``RotatedRect`` -> ``boxPoints`` -> ``fillConvexPoly``
    pipeline, then alpha-blends with the background.
    """
    import cv2

    # Compute the 4 corner points of the rotated rectangle
    rect = ((cx, cy), (RECT_WIDTH, RECT_HEIGHT), angle_deg)
    box = cv2.boxPoints(rect).astype(np.int32)

    # Create overlay and draw filled rectangle
    overlay = frame.copy()
    cv2.fillConvexPoly(overlay, box, color)

    # Alpha-blend: result = opacity * overlay + (1 - opacity) * original
    cv2.addWeighted(overlay, opacity, frame, 1 - opacity, 0, dst=frame)
    return frame
