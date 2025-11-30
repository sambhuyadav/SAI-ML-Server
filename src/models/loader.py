from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class MovenetModel:
    """Wrapper around a MoveNet TFLite interpreter."""

    def __init__(self, interpreter) -> None:  # type: ignore[no-untyped-def]
        self.interpreter = interpreter
        self.input_details = interpreter.get_input_details()
        self.output_details = interpreter.get_output_details()

    def predict_confidence(self, frame: np.ndarray) -> float:
        """Return a simple confidence metric (mean keypoint score)."""
        input_shape = self.input_details[0]["shape"]
        height, width = input_shape[1], input_shape[2]
        resized = _resize_frame(frame, width, height)
        input_tensor = np.expand_dims(resized, axis=0).astype(np.float32)
        self.interpreter.set_tensor(self.input_details[0]["index"], input_tensor)
        self.interpreter.invoke()
        keypoints = self.interpreter.get_tensor(self.output_details[0]["index"])
        # keypoints shape: [1, 1, 17, 3] -> last dim: y, x, score
        scores = keypoints[..., 2]
        return float(np.mean(scores))


def load_movenet(model_path: Path) -> Optional[MovenetModel]:
    """Load a MoveNet TFLite model if available."""
    if os.getenv("DISABLE_MOVENET", "").lower() in {"1", "true", "yes"}:
        logger.info("MoveNet loading disabled via DISABLE_MOVENET; using fallback scorer.")
        return None

    interpreter = None
    interpreter_source = "unknown"

    # Prefer tflite_runtime, fall back to TensorFlow Lite
    try:
        from tflite_runtime.interpreter import Interpreter  # type: ignore
        interpreter_source = "tflite-runtime"
    except Exception as exc:  # pragma: no cover - dependency may be missing
        logger.debug("tflite-runtime not available: %s", exc)
        try:
            from tensorflow.lite import Interpreter  # type: ignore
            interpreter_source = "tensorflow.lite"
        except Exception as tf_exc:
            logger.warning("Neither tflite-runtime nor TensorFlow Lite is available: %s", tf_exc)
            return None

    if not model_path.exists():
        logger.warning("MoveNet model not found at %s", model_path)
        return None

    try:
        interpreter = Interpreter(model_path=str(model_path))
        interpreter.allocate_tensors()
        logger.info("Loaded MoveNet model from %s via %s", model_path, interpreter_source)
    except Exception as exc:  # pragma: no cover - depends on runtime availability
        logger.error(
            "Failed to load MoveNet model from %s using %s: %s. "
            "Set DISABLE_MOVENET=1 to skip model loading in constrained environments.",
            model_path,
            interpreter_source,
            exc,
        )
        return None

    return MovenetModel(interpreter)


def _resize_frame(frame: np.ndarray, width: int, height: int) -> np.ndarray:
    import cv2

    resized = cv2.resize(frame, (width, height))
    # Normalize to [-1, 1] as expected by MoveNet
    normalized = (resized.astype(np.float32) - 127.5) / 127.5
    return normalized
