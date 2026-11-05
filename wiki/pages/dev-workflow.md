---
title: Development Workflow
sources: [README.md, scripts/start.sh, scripts/stop.sh, client/package.json, server/pyproject.toml]
updated: 2026-11-05
---

# Development Workflow

## Prerequisites

- Node.js `^20.19.0` or `>=22.12.0` (`client/package.json`).
- Python `>=3.11` (`server/pyproject.toml`).
- `uv` is recommended. `pip` also works.

## Start the servers

On macOS or Linux, run `./scripts/start.sh`. The script installs dependencies if they are missing. It writes logs to `/tmp/inventory-backend.log` and `/tmp/inventory-frontend.log`. Run `./scripts/stop.sh` to stop the servers.

On Windows, the scripts do not work. Start each server in its own terminal:

```bash
# Terminal 1 - backend
cd server
uv sync
uv run python main.py        # or: pip install fastapi uvicorn pydantic && python main.py

# Terminal 2 - frontend
cd client
npm install
npm run dev
```

## URLs

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| API | http://localhost:8001/api |
| API docs (Swagger) | http://localhost:8001/docs |

## Build

`cd client && npm run build` writes the static build to `client/dist/`. The build still calls the API at `http://localhost:8001/api`, because `client/src/api.js` hardcodes that URL.

## Change checklist

1. If you change a JSON structure, update the Pydantic model in `server/main.py`.
2. If you add an endpoint, add a function in `client/src/api.js` and tests in `tests/backend/`.
3. If you add UI text, add the key to `client/src/locales/en.js` and `ja.js`.
4. Run `cd tests && uv run pytest`.

Related: [Testing](testing.md), [Claude Code Tooling](claude-tooling.md).
