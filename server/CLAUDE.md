# CLAUDE.md - Server

Guidance for the FastAPI backend. See the root `CLAUDE.md` for architecture and commands.

## Run

```bash
uv run python main.py    # http://localhost:8001, docs at /docs
```

Restart the server after you change a file in `data/`. Data loads once at import time.

## Conventions

- All routes and Pydantic models are in `main.py`. Keep new endpoints there unless the file grows a lot.
- Use `apply_filters()` and `filter_by_month()` for filtering. Treat `None` and `'all'` as "no filter". Compare `category` and `status` case-insensitively, and compare `warehouse` exactly.
- Set `response_model=` on list and detail endpoints. Return `HTTPException(404)` when an id is not found.
- Do not mutate the module-level lists from `mock_data.py`. Copy items first, as `get_backlog()` does.
- When you change the structure of a JSON file, update the matching Pydantic model in the same change.
- Keep `category`, `warehouse` and `sku` values consistent across `inventory.json`, `orders.json` and `backlog_items.json`.

## Gotchas

- Do not run `generate_data.py` without a check first. It writes `data/orders.json` again with an old product catalog (Widgets, Components, ...). That catalog does not match the categories in `inventory.json`.
- `QUARTER_MAP` and `/api/reports/quarterly` support only 2025.
- `restock_orders` is the only mutable state. Tests clear it with an autouse fixture in `tests/backend/test_restocking.py`.
- Each `item_sku` in `demand_forecasts.json` must exist in `inventory.json`. The restocking routes join on it, and `test_demand_forecast_skus_exist_in_inventory` checks it.
- `CreatePurchaseOrderRequest` and `PurchaseOrder` are defined, but there is no purchase-order POST route. `data/purchase_orders.json` is empty.
- `client/src/api.js` calls `/api/tasks` (GET, POST, PATCH, DELETE) and `/api/purchase-orders`. These routes do not exist, so the calls return 404.
- CORS allows all origins. This is acceptable for the local demo only.

## Add an endpoint

1. Add or update the Pydantic model in `main.py`.
2. Add the route, and use the shared filter helpers if it takes filters.
3. Add the client function in `client/src/api.js`.
4. Add tests in `tests/backend/` (use the `backend-api-test` skill). Run them with `cd ../tests && uv run pytest`.
