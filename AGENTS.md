# Repository Guidelines

## Project Structure & Module Organization
- Place API and ML logic in `src/` (e.g., `src/app.py` for FastAPI entrypoint, `src/pipelines/` for rating flows, `src/utils/` for shared helpers).
- Keep response/request schemas in `src/schemas.py`; isolate model loading in `src/models/loader.py` to avoid import side effects.
- Tests live in `tests/` with fixtures in `tests/fixtures/` (short MP4s under 5s to keep the repo light).
- Store docs and reference notes in `docs/`. Large model weights stay outside the repo; track URLs and checksums in `models/README.md`.

## Build, Test, and Development Commands
- Create a virtual env: `python -m venv .venv && source .venv/bin/activate`.
- Install deps: `pip install -r requirements.txt` (FastAPI/Uvicorn plus your chosen vision library).
- Run locally with hot reload: `uvicorn src.app:app --reload`.
- Run tests: `pytest -q` or target a file `pytest -q tests/test_api.py -k video`.
- Sanity-check inference scripts: `python scripts/benchmark.py sample.mp4`.

## Coding Style & Naming Conventions
- Python 3.11+, 4-space indentation, type hints mandatory; run `ruff`, `black`, and `isort` before pushing.
- Modules/functions/vars use `snake_case`; classes `PascalCase`; constants `UPPER_SNAKE_CASE`.
- Endpoints named for actions (`/rate`, `/health`); keep validation in Pydantic schemas and ML-specific logic in pipelines.
- Avoid global state; wrap model instances in lightweight factories so tests can swap mocks easily.

## Testing Guidelines
- Use `pytest` with coverage (`pytest -q --cov=src --cov-report=term`); aim for ≥80% coverage on new code.
- Name files `test_<module>.py`; each feature should have an API test and a pipeline unit test.
- Mock external downloads and random seeds; keep fixtures small and reusable (`tests/fixtures/sample_situp.mp4`).
- For new rating types, include a golden JSON response in `tests/fixtures/`.

## Commit & Pull Request Guidelines
- Follow Conventional Commits (`feat: add sit-up rater`, `fix: handle empty upload`, `chore: pin torch version`).
- PRs must include: short summary, linked task/issue, test evidence (e.g., `pytest -q` output), and a sample request/response payload.
- When changing models, note source, license, expected input resolution, and any metrics observed.
- Keep PRs small and scoped; add screenshots/log snippets when altering error handling or observability.

## Security & Configuration Tips
- Never commit secrets or full datasets; use `.env`/`.env.example` for configuration. Validate video MIME type, duration, and size server-side.
- If weights are large, store them in external storage; document download steps and checksums. Clean temp files after inference.
