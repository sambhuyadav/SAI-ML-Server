# Render Deployment

Use these settings when creating a Render Web Service so the health check finds the running server and MoveNet errors are handled cleanly.

- **Runtime:** Python 3.11 (set env var `PYTHON_VERSION=3.11` if using a blueprint)
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `uvicorn src.app:app --host 0.0.0.0 --port $PORT`
- **Health check path:** `/health`
- **Optional:** Set `DISABLE_MOVENET=1` if the container image lacks the CPU features or libs required for the bundled `movenet.tflite`; the API will fall back to deterministic scoring.

If you prefer a Render blueprint, add a `render.yaml` with the same start command and health check path. The `models/movenet.tflite` file is shipped with the repo, so no external downloads are required.
