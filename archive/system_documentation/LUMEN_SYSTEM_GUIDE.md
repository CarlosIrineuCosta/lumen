# Lumen Operating Guide
This document is the authoritative reference for the Lumen Photo Management System. Previous instruction files now live in `backup/docs/`; update this guide whenever process changes.

## 1. Project Snapshot
- **Stack:** FastAPI backend (`backend/app`), vanilla JS frontend (`frontend/`) using a Poor-Man's Module pattern (`window.Lumen*` globals).
- **Database:** PostgreSQL 16 (primary), Redis 6+ (caching).
- **Frontend Libraries:** The UI is built with our custom glassmorphism CSS on top of Preline UI components. It uses jQuery, justifiedGallery, and lightGallery for photo displays. See `docs/core/_TECH_STACK.md` for the full list and required script loading order.
- **Services:** Local storage service (`backend/app/storage/local_storage.py`), Firebase auth flow (`frontend/js/modules/auth.js`), and background utilities in `scripts/`.
- **Active Workstream:** Restore photo upload & profile flows, address security review from 2025-10-02, finish glass component migration.

## 2. Environments & Access Control
- **Development:** Linux host at `/home/cdc/Storage/NVMe/projects/lumen`. Run all work locally; never edit production files directly.
- **Production:** EDIS Swiss VPS (`83.172.136.127`) reachable through CI/CD only. Request explicit approval before deployment.
- **Access Rules:** No new Markdown files or folders in the repo root without owner approval; archive drafts under `docs/` or `backup/docs/`.

## 3. Repository Layout
- `backend/app/` – FastAPI routers (`api/endpoints/`), services (photo, series, auth), database models, storage adapters.
- `frontend/` – Static SPA served from `index.html`; JS modules under `frontend/js/modules/`, glassmorphism CSS in `frontend/css/`, localized strings in `frontend/i18n/`.
- `scripts/` – Operational tooling (`start-server.sh`, `agent_protocol.py`, agent automation under `scripts/agents/`).
- `.agents/` – Delegated task queue and outputs; `.postbox/` tracks verification todos/completions.
- `backup/docs/` – Archive of superseded task lists and instruction memos.

## 4. Daily Workflow
1. **Morning check:** Review `.postbox/todo.md` and latest task file inside `tasks/`. Confirm there are no conflicting WIP changes with `git status`.
2. **Start Servers:** Use the `scripts/server-manager.sh` script (e.g., `./scripts/server-manager.sh start`) to run the backend and frontend servers. This handles environment variables and ports correctly.
3. **Access App:** The frontend is available at `http://100.106.201.33:8000` and the backend API at `http://100.106.201.33:8080`.
4. **During work:** Keep functions <50 lines, document non-obvious logic with concise comments, prefer descriptive names. Never introduce build tooling or frameworks.
5. **After changes:** Run `python scripts/agent_protocol.py verify <files>` and inspect `.postbox/issues.md`. Execute `python -m pytest backend/tests -v` (HTML coverage emitted to `backend/htmlcov/`). Note gaps in `.postbox/completed.md` once resolved.

## 5. Coding Standards & Conventions
- **Python:** PEP 8, 4-space indentation, prefer type hints, explicit error handling. Database access goes through `SessionLocal`; avoid raw SQL unless parameterized (`sqlalchemy.text`).
- **JavaScript:** Globals under `window.Lumen*`; script load order matches `index.html`. Use camelCase for functions, kebab-case filenames. No ES module syntax, React, or bundlers. Keep DOM hooks stable for `LumenApp` orchestrator.
- **CSS:** Continue glass design (`frontend/css/glassmorphism-core.css`, `glass.css`). Validate responsive states before commit.
- **Security hygiene:** Never store secrets in source; configure GLM API and Firebase keys via environment (`backend/.env`, `frontend/js/config.js`).

## 6. Tooling & Commands
- **Verification:** `python scripts/agent_protocol.py verify file1 file2` to open structured checks.
- **System summary:** `python scripts/agent_protocol.py summary` for message/task snapshot.
- **Agent delegation:** `/delegate review "security" backend/app/api/endpoints/auth.py` (see `.agents/README.md`). For details on model selection and tuning, see `docs/GLM_MODEL_SELECTION_GUIDE.md`.
- **Testing:** `python -m pytest backend/tests -v` (coverage gate 70% via `pytest.ini`). Frontend Playwright tests should live under `frontend/tests/` once recreated.
- **GLM configuration:** Store `GLM_API_KEY`, `GLM_MODEL`, `GLM_BASE_URL` in `backend/.env`; never commit keys. Validate with the snippet in `backup/docs/GLM_API_SETUP.md` when onboarding.

## 7. Security & Performance Priorities
- `[Resolved 2025-10-05]` Duplicate `check-registration` route removed and responses now HTML-escape user fields in `backend/app/api/endpoints/auth.py:30` and `backend/app/api/endpoints/auth.py:220`.
- `[Resolved 2025-10-05]` Photo uploads enforce size/type validation and safe handle creation in both `backend/app/services/photo_service.py:96` and `backend/app/services/photo_service_v2.py:114`.
- `[Open]` Database pooling – `backend/app/database/connection.py` still uses `NullPool`; replace with a bounded pool suited for FastAPI to avoid connection churn.
- `[Open]` Input filtering – `LocationService.resolve_city` continues broad `.contains` lookups; tighten matching to avoid injection and improve accuracy.
- `[Open]` Cache invalidation & pagination – adopt cursor-based pagination and consistent cache invalidation in photo services before production load.
- Document progress inside this section when remediations land.

## 8. Current Feature Focus
- **Upload modal recovery:** `frontend/js/modules/upload.js` expects DaisyUI-style modal IDs while HTML lacks matching structure; restore `<dialog id="upload-modal">` and wire `LumenUI` helpers.
- **Profile modal flow:** `LumenProfile.showProfile()` currently no-ops; trace through `frontend/js/modules/profile.js` and ensure markup exists so auth checks resolve.
- **Search & filtering polish:** Implement client-side tag filtering and structured search results (`photos/users/series`) per `backup/docs/GEMINI_IMPLEMENTATION_PLAN_12H.md`.
- **Agent system tuning:** Continue GLM 4.6 evaluation (see archived `tasks_20251002.md`) and maintain `/delegate status` hygiene.

## 9. Multi-Agent & Verification Protocol
- Message routing lives in `.agents/messages/`; scripts under `scripts/agents/` manage review batches.
- After every change set: `python scripts/agent_protocol.py verify ...`, read `.postbox/issues.md`, then append completion notes to `.postbox/completed.md` and daily `tasks/YYYY-MM-DD.md`.
- Parallelize safe reviews/tests/docs via `/delegate` commands; risky code changes require coordinator approval before applying proposals from `.agents/coordinated/`.

## 10. Documentation & Record Keeping
- Legacy guidance resides under `backup/docs/` (including `CLAUDE_*.md`, `tasks_*.md`, GLM setup, and security reviews). Do not edit these in place; summarize relevant updates here instead.
- New documentation should live under `docs/` (or subfolders) and follow concise, actionable writing. Keep this guide up to date and notify the team when sections change.

---
**Owner:** Development Team (Claude Code coordinator)  
**Last Consolidated:** 2025-10-05  
**Next Review:** Align with weekly sprint kickoff or after major architecture shifts.
