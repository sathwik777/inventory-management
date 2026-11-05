---
title: Data Model
sources: [server/mock_data.py, server/main.py, server/data/, server/generate_data.py]
updated: 2026-11-05
---

# Data Model

There is no database. `server/mock_data.py` reads seven JSON files from `server/data/` one time, when Python imports the module. The data stays in module-level lists in memory. A restart loads the files again. No route changes the seed data. Submitted restock orders go into a separate in-memory list, `restock_orders` in `main.py`. They are not written to a file.

## Data files

| File | Shape | Records | Python name | Pydantic model |
|---|---|---|---|---|
| `inventory.json` | list | 32 | `inventory_items` | `InventoryItem` |
| `orders.json` | list | 250 | `orders` | `Order` |
| `demand_forecasts.json` | list | 9 | `demand_forecasts` | `DemandForecast` |
| `backlog_items.json` | list | 4 | `backlog_items` | `BacklogItem` |
| `purchase_orders.json` | list | 0 | `purchase_orders` | `PurchaseOrder` |
| `spending.json` | dict | 3 keys | `spending_summary`, `monthly_spending`, `category_spending` | none |
| `transactions.json` | list | 56 | `recent_transactions` | none |

## Domain values

- **Warehouses:** London, San Francisco, Tokyo.
- **Categories:** Actuators, Circuit Boards, Controllers, Power Supplies, Sensors.
- **Order statuses:** Delivered, Shipped, Processing, Backordered.
- **Order months:** 2025-01 to 2025-12.

## Key fields

- `InventoryItem`: `sku`, `category`, `warehouse`, `quantity_on_hand`, `reorder_point`, `unit_cost`.
- `Order`: `order_number`, `customer`, `items` (a list of dicts with `sku`, `quantity`, `unit_price`), `status`, `order_date` (ISO date-time string), `total_value`. The fields `warehouse` and `category` are optional.
- `BacklogItem`: `order_id`, `item_sku`, `quantity_needed`, `quantity_available`, `days_delayed`, `priority`.
- `PurchaseOrder`: links to a backlog item through `backlog_item_id`.

## Relations

- `Order.items[].sku` and `BacklogItem.item_sku` refer to the inventory SKUs.
- `DemandForecast.item_sku` refers to an inventory SKU. On 2026-11-05, the 9 forecasts were changed from old catalog SKUs (WDG-001, GSK-203, ...) to inventory SKUs (PCB-001, PRS-203, ...). The demand numbers and trends did not change. The test `test_demand_forecast_skus_exist_in_inventory` keeps this rule.
- `RestockOrder.items[].sku` refers to an inventory SKU. The server copies the name, category, warehouse and unit cost from inventory.
- `BacklogItem.order_id` refers to `Order.id`.
- `PurchaseOrder.backlog_item_id` refers to `BacklogItem.id`. The backend uses it to set `has_purchase_order`.

## Change rule

When you change the structure of a JSON file, update the Pydantic model in `main.py` in the same change. Otherwise the response validation fails.

## Data generator

`server/generate_data.py` writes `data/orders.json` again (`generate_data.py:120-121`). Its product catalog uses old categories (Widgets, Components, Equipment, Consumables). See [Gotchas](gotchas.md).

Related: [Backend API](backend-api.md), [Filter System](filter-system.md).
