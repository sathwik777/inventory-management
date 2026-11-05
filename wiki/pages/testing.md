---
title: Testing
sources: [tests/pytest.ini, tests/backend/conftest.py, tests/backend/, tests/README.md]
updated: 2026-11-05
---

# Testing

Only the backend has tests. There are no frontend tests, no linter and no type checks.

## Run the tests

```bash
cd tests
uv run pytest                                   # all tests
uv run pytest backend/test_inventory.py         # one file
uv run pytest backend/test_inventory.py::TestInventoryEndpoints::test_get_all_inventory
```

If `uv` is not installed, use `python -m pytest` with `pytest` and `httpx` installed. On 2026-11-05, 62 tests passed in about 2 seconds.

## Configuration

- `tests/pytest.ini` sets `testpaths = backend`, `-v`, `--strict-markers`, `--tb=short` and `asyncio_mode = auto`.
- `tests/backend/conftest.py` adds `server/` to `sys.path` and imports `main.app`.
- The fixture `client` gives a FastAPI `TestClient`. The fixtures `sample_inventory_item` and `sample_order` give example records.

## Test files

| File | Scope |
|---|---|
| `test_inventory.py` | Inventory list, filters, item by id, 404 |
| `test_dashboard.py` | Summary KPIs, filters, calculation accuracy |
| `test_misc_endpoints.py` | Demand (including the forecast-to-inventory SKU check), backlog, spending, root |
| `test_restocking.py` | Recommendations (budget limit, ranking, default budget) and restock orders (create, list, validation) |

`test_restocking.py` has an autouse fixture that clears `main.restock_orders` before and after each test. This is necessary because the list is module-level state.

## Gaps

- `tests/README.md` lists `test_orders.py` with 15 tests, but that file does not exist. The orders routes have no tests.
- The `/api/reports/*` routes have no tests.

Use the `backend-api-test` skill (`.claude/skills/backend-api-test`) when you write tests.

Related: [Backend API](backend-api.md), [Development Workflow](dev-workflow.md).
