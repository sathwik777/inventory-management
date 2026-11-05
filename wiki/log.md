# Wiki Log

## 2026-11-05 - ingest - Restocking feature
- Pages changed: backend-api.md, data-model.md, frontend.md, testing.md, overview.md, architecture.md, claude-tooling.md.
- Reason: new Restocking tab, 3 new routes (`/api/restocking/recommendations`, `GET`/`POST /api/restock-orders`), demand forecasts realigned to inventory SKUs, 22 new tests (62 in total).
- Note: project agents and MCP servers were not loaded because the session started in the parent folder.

## 2026-11-05 - ingest - initial wiki
- Pages created: overview, architecture, frontend, backend-api, data-model, filter-system, i18n, dev-workflow, testing, claude-tooling, gotchas.
- Reason: first full read of the codebase (server, client, tests, .claude).
- Findings: `/api/tasks` and `/api/purchase-orders` do not exist on the backend. `Backlog.vue` has no route. `generate_data.py` is stale. `tests/README.md` lists a test file that does not exist.
