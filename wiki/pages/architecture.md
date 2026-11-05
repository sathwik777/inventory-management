---
title: Architecture
sources: [client/src/, server/main.py, server/mock_data.py, server/data/]
updated: 2026-11-05
---

# Architecture

The system has three tiers in two processes. There is no database and no authentication. The only write path is `POST /api/restock-orders`, which appends to an in-memory list.

```
Browser (localhost:3000)
  Vue 3 SPA
    views/  ->  composables/ (useFilters, useI18n, useAuth)
    api.js  (axios, base URL http://localhost:8001/api)
        |
        |  HTTP GET (+ POST restock orders), JSON, CORS "*"
        v
FastAPI (uvicorn, localhost:8001)
  main.py: routes -> apply_filters / filter_by_month -> Pydantic response_model
        |
        |  Python import (one time, at start)
        v
mock_data.py -> server/data/*.json  (7 files, in-memory lists)
```

## Tiers

| Tier | Technology | Main files | Responsibility |
|---|---|---|---|
| Presentation | Vue 3, vue-router 4, Vite 8 | `client/src/views/*.vue`, `App.vue` | Pages, charts, modals, filters |
| Client state | Vue composables | `client/src/composables/*.js` | Shared filter state, locale, mock user |
| API client | axios | `client/src/api.js` | Build query strings, call the API |
| API | FastAPI, Pydantic 2, uvicorn | `server/main.py` | Routes, filters, KPIs, validation |
| Data | JSON files | `server/mock_data.py`, `server/data/` | Load the seed data into memory |

## Design decisions

- **In-memory data:** the demo starts quickly and needs no database. All filters and aggregates are Python list comprehensions.
- **Singleton composables:** module-level refs give a global store without Pinia or Vuex.
- **Hand-made charts:** SVG and CSS `div` bars keep the bundle small, with no chart library.
- **One backend file:** all routes and models are in `main.py`. This is easy to read for a workshop.

## Request example: Dashboard

1. `Dashboard.vue` mounts. It calls `getDashboardSummary`, `getOrders`, `getInventory` and `getBacklog`.
2. FastAPI filters the in-memory lists and calculates the KPIs.
3. The view stores the responses in refs. `computed` properties make the chart and table data.
4. If a filter changes, `watch` calls `loadData` again.

Related: [Overview](overview.md), [Filter System](filter-system.md), [Frontend](frontend.md), [Backend API](backend-api.md).
