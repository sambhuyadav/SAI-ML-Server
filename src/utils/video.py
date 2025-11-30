from __future__ import annotations

import logging
from pathlib import Path
from typing import List

import cv2
import numpy as np

logger = logging.getLogger(__name__)


def sample_frames(path: Path, max_frames: int = 8) -> List[np.ndarray]:
    """Grab up to N frames from a video for quick analysis."""
    frames: List[np.ndarray] = []
    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        logger.warning("Could not open video: %s", path)
        return frames

    try:
        while len(frames) < max_frames:
            success, frame = capture.read()
            if not success or frame is None:
                break
            frames.append(frame)
    finally:
        capture.release()

    return frames
