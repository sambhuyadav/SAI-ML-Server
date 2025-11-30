from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import RedirectResponse

from src.models.loader import load_movenet
from src.pipelines.rater import VideoRater
from src.schemas import RatingResponse, TestQuality, SUPPORTED_QUALITIES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Movement Rating API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Attempt to load MoveNet; fallback logic is handled in the pipeline.
MOVENET_PATH = Path("models/movenet.tflite")
video_rater = VideoRater(model=load_movenet(MOVENET_PATH), default_quality=TestQuality.FLEXIBILITY)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def docs_redirect() -> RedirectResponse:
    """Redirect root to Swagger UI for easy browser testing."""
    return RedirectResponse(url="/docs")


@app.post("/rate", response_model=RatingResponse)
async def rate_video(
    metadata: Annotated[
        TestQuality,
        Form(
            description="Select the quality being tested.",
            json_schema_extra={"enum": SUPPORTED_QUALITIES},
        ),
    ],
    file: UploadFile = File(..., description="MP4 video to rate"),
) -> RatingResponse:
    """Accept a video upload and return a score 0-10 for the specified test."""
    quality = metadata
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is required.")

    suffix = Path(file.filename).suffix or ".mp4"
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            temp_path = Path(tmp.name)
    except Exception as exc:  # pragma: no cover - file I/O errors are environment-specific
        logger.error("Failed to persist uploaded file: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to persist uploaded file.")

    rating = video_rater.rate(temp_path, quality=quality)
    temp_path.unlink(missing_ok=True)
    return rating
