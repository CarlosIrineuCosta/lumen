# Repository Guidelines

## Project Structure & Module Organization
- `backend/`: FastAPI service (`app/` for routers, services, models, utils), migrations in `alembic/` and `migrations/`, config helpers, and pytest setup. Secrets live in `backend/.env` (not committed).
- `frontend/`: Static/PWA assets (`index.html`, `css/`, `js/`, `assets/`, `i18n/`) with a lightweight dev server at `frontend/serve.py`.
- `scripts/`: Operational helpers for tests, data seeding, agents, and deployment (e.g., `run-full-test-suite.sh`, `seed_test_data.py`, `start-server.sh`).
- `agents/`, `docs/`, `tasks/`, `archive/`: Coordination materials, reference docs, and legacy artifacts. Prefer current guidance in `COORDINATION.md` and backend guides.

## Build, Test, and Development Commands
- Backend setup: `cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.
- Run API locally: `cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8080`.
- Serve frontend: `python frontend/serve.py` (serves `frontend/` on `http://localhost:8000`, expects API on 8080).
- Full QA sweep: `python backend/tests/run_tests.py --all --coverage` (unit + integration + security checks + lint/format, outputs `htmlcov/`).
- Targeted tests: `cd backend && python -m pytest -m integration` or `python -m pytest tests/test_*.py -q`. Use markers `unit`, `integration`, `auth`, `photos`, `slow`, `external`.

## Coding Style & Naming Conventions
- Python: format with `black app/` (88-char lines, `E203`/`W503` ignored) and lint with `flake8 app/ --max-line-length=88`. Prefer type hints, snake_case for functions/vars, PascalCase for classes, lowercase module filenames.
- FastAPI routers should stay small and composable; keep auth and database access in `services/` or `utils/`.
- Frontend: ES6 modules in `js/`, keep assets hashed or scoped per feature directory; avoid inline script bloat in `index.html`.

## Testing Guidelines
- Pytest discovery: files `test_*.py`/`*_test.py`, classes `Test*`, functions `test_*`. Mark slow or external integrations to keep default runs quick.
- Coverage floor is 70% (pytest.ini); the runner’s `--coverage` enforces 80% and writes `htmlcov/`.
- Security/quality checks come from the runner: `bandit -r app/`, `safety check`, `black --check app/`, `flake8 app/`. Keep reports (`bandit-report.json`, `safety-report.json`) out of commits.

## Commit & Pull Request Guidelines
- Commit messages: concise, present-tense summaries (e.g., “Add subscription cache invalidation”), include scope when relevant (`API`, `Frontend`, `Infra`). Avoid noisy WIP unless coordinated.
- Pull requests: describe the change, link issues/tasks, list test commands executed, and attach screenshots or cURL examples for API/UX changes. Call out breaking changes, new env vars, and migration steps explicitly.

## Security & Configuration Tips
- Never commit secrets or service-account JSON; use local `.env` and keep `firebase_service_account*.json` out of Git.
- Validate CORS origins via `ALLOWED_ORIGINS`; production should be restrictive. Default ports: API `8080`, frontend dev `8000`.
- Before running migration or seeding scripts, point to a safe database and back up `database/` artifacts; audit changes to `schema_production.sql` and `migrations/` carefully.
