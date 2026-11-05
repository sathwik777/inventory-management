---
title: Filter System
sources: [client/src/composables/useFilters.js, client/src/components/FilterBar.vue, client/src/api.js, server/main.py]
updated: 2026-11-05
---

# Filter System

The four global filters go through every layer of the app. This is the main cross-cutting feature.

## The four filters

| UI label | Frontend ref | Query parameter | Backend comparison |
|---|---|---|---|
| Time Period | `selectedPeriod` | `month` | substring of `order_date`, or quarter key |
| Location | `selectedLocation` | `warehouse` | exact match |
| Category | `selectedCategory` | `category` | case-insensitive |
| Order Status | `selectedStatus` | `status` | case-insensitive |

The value `'all'` means "no filter" in all layers.

## Flow

1. The user changes a dropdown in `FilterBar.vue`. The dropdown writes a ref in `useFilters`.
2. The refs are at module level (`useFilters.js:3-7`). All components share the same state, so this works as a singleton.
3. Each view uses `watch` on the refs that it needs, and loads its data again.
4. `getCurrentFilters()` changes the names to the API names: `selectedLocation` becomes `warehouse`, and `selectedPeriod` becomes `month`.
5. `api.js` builds a `URLSearchParams` string and leaves out the value `'all'`.
6. In `server/main.py`, `apply_filters()` (lines 33-47) filters by warehouse, category and status. `filter_by_month()` (lines 17-31) filters by month.
7. FastAPI validates the result with the `response_model`, then returns JSON.
8. The view keeps the raw data in refs and calculates the display values in `computed` properties.

## Month and quarter values

- `YYYY-MM`, for example `2025-03`: matches orders whose `order_date` contains that string.
- `Q1-2025` to `Q4-2025`: matches the three months in `QUARTER_MAP` (`main.py:10-15`).
- An unknown quarter key returns all items without a filter.

## Limits

- Inventory has no time dimension, so `/api/inventory` ignores `month` and `status`.
- `/api/demand`, `/api/backlog`, `/api/spending/*` and `/api/reports/*` ignore all filters. Views such as `Demand.vue` filter some data on the client side instead.
- `Reports.vue` does not use the filters at all.
- `total_backlog_items` on the dashboard always counts all backlog items.

Related: [Backend API](backend-api.md), [Frontend](frontend.md).
