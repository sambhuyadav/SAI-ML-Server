from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

# Ensure src is on path for direct invocation without installation.
import sys
from pathlib import Path as _Path

sys.path.append(str(_Path(__file__).resolve().parents[1]))

from src.app import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_rate_fallback_for_small_file() -> None:
    # Create a tiny placeholder file; fallback logic should still return 200 and a score.
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(b"not-a-real-video")
        tmp_path = Path(tmp.name)

    with tmp_path.open("rb") as handle:
        files = {"file": ("sample.mp4", handle, "video/mp4")}
        response = client.post("/rate", data={"metadata": "Agility"}, files=files)

    tmp_path.unlink(missing_ok=True)

    assert response.status_code == 200
    payload = response.json()
    assert payload["test"]["nameOfTest"] == "4 x 10 mts Shuttle Run"
    assert payload["test"]["qualityTested"] == "Agility"
    assert "ratingScale" not in payload["test"]
    assert 0.0 <= payload["test"]["score"] <= 10.0
