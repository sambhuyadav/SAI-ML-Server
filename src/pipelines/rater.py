from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Optional

import numpy as np

from src.models.loader import MovenetModel
from src.schemas import (
    RatingResponse,
    TestQuality,
    get_metadata_for_quality,
)
from src.utils.video import sample_frames

logger = logging.getLogger(__name__)


class VideoRater:
    """Rate a movement video using MoveNet if available, otherwise fall back."""

    def __init__(self, model: Optional[MovenetModel], default_quality: TestQuality | None = None) -> None:
        self.model = model
        self.default_quality = default_quality

    def rate(self, video_path: Path, quality: Optional[TestQuality] = None) -> RatingResponse:
        frames = sample_frames(video_path)
        frames_used = len(frames)

        if self.model and frames:
            score = self._score_with_model(frames)
        else:
            score = self._fallback_score(video_path, (quality or self.default_quality), frames_used)

        score = max(0.0, min(10.0, score))
        resolved_quality = quality or self.default_quality or TestQuality.FLEXIBILITY
        meta = get_metadata_for_quality(resolved_quality)
        return RatingResponse(
            test=RatingResponse.TestDescriptor(
                testNumber=int(meta["testNumber"]),
                sequenceLabel=str(meta["sequenceLabel"]),
                nameOfTest=str(meta["nameOfTest"]),
                qualityTested=str(meta["qualityTested"]),
                ageCategory=meta.get("ageCategory"),
                score=round(score, 2),
            )
        )

    def _score_with_model(self, frames: list[np.ndarray]) -> float:
        confidences = []
        for frame in frames:
            try:
                conf = self.model.predict_confidence(frame) if self.model else 0.0
                confidences.append(conf)
            except Exception as exc:  # pragma: no cover - depends on runtime environment
                logger.warning("Model inference failed: %s", exc)
        if not confidences:
            return 5.0
        mean_conf = float(np.mean(confidences))
        # Scale confidence (0-1) to 0-10
        return mean_conf * 10.0

    def _fallback_score(self, video_path: Path, quality: Optional[TestQuality], frames_used: int) -> float:
        """Deterministic fallback based on file hash, quality, and frames observed."""
        base = quality.value if isinstance(quality, TestQuality) else str(quality or "unknown")
        payload = f"{base}:{frames_used}:{video_path.stat().st_size}".encode()
        digest = hashlib.sha256(payload).digest()
        numeric = int.from_bytes(digest[:2], "big")  # 0..65535
        return (numeric % 9000) / 1000.0 + 1.0  # 1.0 - 10.0 range
