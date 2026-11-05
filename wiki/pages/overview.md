---
title: Overview
sources: [README.md, CLAUDE.md]
updated: 2026-11-05
---

# Overview

The Factory Inventory Management System is a full-stack demo for a Claude Code workshop. It shows inventory, orders, demand forecasts, spending and reports for a factory with three warehouses.

## Facts

| Item | Value |
|---|---|
| Frontend | Vue 3 + Vite, port 3000 |
| Backend | Python FastAPI, port 8001 |
| Data | 7 JSON seed files (read-only) plus in-memory restock orders |
| Pages | 7 routed views (Dashboard, Inventory, Orders, Demand, Restocking, Spending, Reports) |
| API | 17 GET routes, 1 POST route |
| Languages | English, Japanese |
| Tests | 62 backend pytest tests |
| Repository | Public on GitHub |

## Main features

- A dashboard with KPIs, an order donut chart, inventory by category and a shortage table.
- Four global filters: time period, warehouse, category and order status.
- Demand trends with reorder suggestions.
- Restocking: a budget slider, recommended items from the demand forecast, and "Place Order". Submitted orders show in the Orders tab with the delivery lead time.
- Spending: revenue, cost and profit by month.
- Quarterly and monthly reports.

## Read next

1. [Architecture](architecture.md)
2. [Filter System](filter-system.md)
3. [Gotchas and Known Gaps](gotchas.md)
