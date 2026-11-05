# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Factory Inventory Management System Demo with GitHub integration - Full-stack application with Vue 3 frontend, Python FastAPI backend, and in-memory mock data (no database).

> ⚠️ **This repository and any fork you create are PUBLIC.** Do not commit credentials, internal hostnames, or private registry URLs. `client/.npmrc` pins the public npm registry and `client/package-lock.json` is gitignored to prevent locally-configured registries from leaking into commits — leave both in place.

## Critical Tool Usage Rules

### Subagents
Use the Task tool with these specialized subagents for appropriate tasks:

- **vue-expert**: Use for Vue 3 frontend features, UI components, styling, and client-side functionality
  - Examples: Creating components, fixing reactivity issues, performance optimization, complex state management
  - **MANDATORY RULE: ANY time you need to create or significantly modify a .vue file, you MUST delegate to vue-expert**
- **code-reviewer**: Use after writing significant code to review quality and best practices
- **security-auditor**: Use for security reviews (defined in `.claude/agents/`)
- **Explore**: Use for understanding codebase structure, searching for patterns, or answering questions about how components work
- **general-purpose**: Use for complex multi-step tasks or when other agents don't fit

### Skills
- **backend-api-test** skill: Use when writing or modifying tests in `tests/backend` directory with pytest and FastAPI TestClient

### MCP Tools
- **ALWAYS use GitHub MCP tools** (`mcp__github__*`) for ALL GitHub operations
  - Exception: Local branches only - use `git checkout -b` instead of `mcp__github__create_branch`
- **ALWAYS use Playwright MCP tools** (`mcp__playwright__*`) for browser testing
  - Test against: `http://localhost:3000` (frontend), `http://localhost:8001` (API)

## Stack
- **Frontend**: Vue 3 + Composition API + Vite (port 3000)
- **Backend**: Python FastAPI (port 8001)
- **Data**: JSON files in `server/data/` loaded via `server/mock_data.py`

## Commands

```bash
# Backend (port 8001, docs at /docs)
cd server
uv sync                      # installs runtime + dev deps (pytest, httpx)
uv run python main.py

# Frontend (port 3000)
cd client
npm install && npm run dev
npm run build                # output: client/dist/

# Backend tests (pytest.ini lives in tests/, testpaths = backend)
cd tests
uv run pytest                                    # all tests
uv run pytest backend/test_inventory.py          # one file
uv run pytest backend/test_inventory.py::TestInventoryEndpoints::test_get_all_inventory  # one test
```

- No linter, formatter or frontend test suite is configured.
- `scripts/start.sh` / `stop.sh` are macOS/Linux only. On Windows, start each server in its own terminal. If `uv` is not installed, `pip install fastapi uvicorn pydantic pytest httpx` and use `python` instead of `uv run python`.
- `tests/README.md` lists `test_orders.py`, but that file does not exist. Orders endpoints have no tests today.

## Architecture

- **Backend is one file.** All routes and all Pydantic models are in `server/main.py`. `server/mock_data.py` loads every `server/data/*.json` file once at import time into module-level lists. Seed data is read-only. The only write route is `POST /api/restock-orders`, which appends to the in-memory `restock_orders` list in `main.py` (a restart clears it).
- **Shared filtering.** `apply_filters()` and `filter_by_month()` in `main.py` do all filtering. The value `'all'` means "no filter". `month` accepts `YYYY-MM` or a quarter key (`Q1-2025` … `Q4-2025`, hardcoded to 2025 in `QUARTER_MAP`).
- **Derived fields.** Some responses are computed, not stored. For example, `/api/backlog` adds `has_purchase_order` from `purchase_orders.json`, and `/api/reports/*` aggregates orders by quarter and month.
- **Frontend filter state is a singleton.** `client/src/composables/useFilters.js` holds module-level refs, so all views share one filter state. `FilterBar.vue` writes it, and each view watches it and calls `client/src/api.js`. `api.js` hardcodes `http://localhost:8001/api` and drops `'all'` values from the query string.
- **i18n.** UI strings come from `client/src/locales/en.js` and `ja.js` through `useI18n.js`. Add each new UI string to both locale files.
- **Known gaps.** `api.js` calls `/api/tasks` and `/api/purchase-orders`, which the backend does not have (404). `views/Backlog.vue` has no route. Details are in `wiki/pages/gotchas.md`.
- **Tests.** `tests/backend/conftest.py` puts `server/` on `sys.path` and imports `main.app` into a `TestClient` fixture named `client`.

## Key Patterns

**Filter System**: 4 filters (Time Period, Warehouse, Category, Order Status) apply to all data via query params
**Data Flow**: Vue filters → `client/src/api.js` → FastAPI → In-memory filtering → Pydantic validation → Computed properties
**Reactivity**: Raw data in refs (`allOrders`, `inventoryItems`), derived data in computed properties

## API Endpoints
- `GET /api/inventory`, `/api/inventory/{id}` - Filters: warehouse, category
- `GET /api/orders`, `/api/orders/{id}` - Filters: warehouse, category, status, month
- `GET /api/dashboard/summary` - All filters
- `GET /api/demand`, `/api/backlog` - No filters
- `GET /api/spending/*` - Summary, monthly, categories, transactions
- `GET /api/reports/quarterly`, `/api/reports/monthly-trends` - No filters
- `GET /api/restocking/recommendations?budget=` - Priority-greedy picks from demand forecasts (joined to inventory on SKU)
- `GET`, `POST /api/restock-orders` - Submitted restock orders with category lead times (`LEAD_TIME_DAYS`)

## Common Issues
1. Use unique keys in v-for (not `index`) - use `sku`, `month`, etc.
2. Validate dates before `.getMonth()` calls
3. Update Pydantic models when changing JSON data structure
4. Inventory filters don't support month (no time dimension)
5. Revenue goals: $800K/month single, $9.6M YTD all months

## File Locations
- Views: `client/src/views/*.vue`
- API Client: `client/src/api.js`
- Backend: `server/main.py`, `server/mock_data.py`
- Data: `server/data/*.json`
- Styles: `client/src/App.vue`

## Design System
- Colors: Slate/gray (#0f172a, #64748b, #e2e8f0)
- Status: green/blue/yellow/red
- Charts: Custom SVG, CSS Grid for layouts
- No emojis in UI
