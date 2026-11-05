---
title: Backend API
sources: [server/main.py]
updated: 2026-11-05
---

# Backend API

The backend is one FastAPI app in `server/main.py`. It has 17 GET routes and 1 POST route (`/api/restock-orders`). Uvicorn serves it on `0.0.0.0:8001` (`server/main.py:307-309`). Interactive docs are at `http://localhost:8001/docs`.

## Routes

| Route | Filters | Response | Notes |
|---|---|---|---|
| `GET /` | - | `{message, version}` | API information |
| `GET /api/inventory` | warehouse, category | `List[InventoryItem]` | `main.py:128` |
| `GET /api/inventory/{item_id}` | - | `InventoryItem` | 404 if not found |
| `GET /api/orders` | warehouse, category, status, month | `List[Order]` | `main.py:144` |
| `GET /api/orders/{order_id}` | - | `Order` | 404 if not found |
| `GET /api/demand` | - | `List[DemandForecast]` | Raw data |
| `GET /api/backlog` | - | `List[BacklogItem]` | Adds `has_purchase_order` (`main.py:169-180`) |
| `GET /api/dashboard/summary` | warehouse, category, status, month | dict | Calculated KPIs (`main.py:182-208`) |
| `GET /api/spending/summary` | - | dict | From `spending.json` |
| `GET /api/spending/monthly` | - | list | From `spending.json` |
| `GET /api/spending/categories` | - | list | From `spending.json` |
| `GET /api/spending/transactions` | - | list | From `transactions.json` |
| `GET /api/reports/quarterly` | - | list | Aggregates orders by quarter (`main.py:230-274`) |
| `GET /api/reports/monthly-trends` | - | list | Aggregates orders by `YYYY-MM` |
| `GET /api/restocking/recommendations` | `budget` (optional) | dict | Ranked candidates with a `recommended` flag |
| `GET /api/restock-orders` | - | `List[RestockOrder]` | Newest first |
| `POST /api/restock-orders` | - | `RestockOrder` (201) | Body: `{budget, items: [{sku, quantity}]}` |

## Restocking

`build_restock_candidates()` joins each demand forecast to `inventory_items` on SKU. It keeps items with a gap > 0 (gap = `forecasted_demand - current_demand`). It sorts by trend (increasing first), then by gap (largest first), then by SKU.

`/api/restocking/recommendations` walks the ranked list. It marks an item `recommended` if its `line_total` fits the remaining budget. If an item does not fit, the walk skips it and continues, so a smaller item later in the list can still fit.

- `max_budget` = the sum of all line totals, rounded up to the next 500. Today it is 7000.
- If `budget` is missing, the default is 50 % of `max_budget`, rounded to 100.
- A negative budget returns 400.

`POST /api/restock-orders` validates the request and stores the order:

- `items` must have at least 1 entry, and each `quantity` must be > 0 (422). A duplicate SKU, an unknown SKU or a total over the budget returns 400.
- The server takes `unit_cost` from inventory. It ignores a price from the client.
- `lead_time_days` = the largest lead time of the item categories (`LEAD_TIME_DAYS`): Circuit Boards 14, Controllers 12, Actuators 10, Sensors 7, Power Supplies 5, other 10.
- `expected_delivery` = `submitted_date` + `lead_time_days`. `order_number` = `RST-<year>-<4-digit sequence>`.
- The order is added to the module-level `restock_orders` list. A restart clears it.

## Dashboard summary calculation

`/api/dashboard/summary` filters inventory with warehouse and category only. It filters orders with all four filters. Then it calculates:

- `total_inventory_value`: sum of `quantity_on_hand * unit_cost`.
- `low_stock_items`: count of items where `quantity_on_hand <= reorder_point`.
- `pending_orders`: count of orders with status `Processing` or `Backordered`.
- `total_backlog_items`: count of all backlog items. Filters do not apply.
- `total_orders_value`: sum of `total_value` of the filtered orders.

## Response models

The Pydantic models are in `main.py:59-121`. See [Data Model](data-model.md). The spending, summary and report routes have no `response_model`, so FastAPI does not validate them.

## CORS

CORS allows all origins, methods and headers (`main.py:50-56`). This is acceptable only for local use.

Related: [Filter System](filter-system.md), [Data Model](data-model.md), [Gotchas](gotchas.md).
