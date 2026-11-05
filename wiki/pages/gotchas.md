---
title: Gotchas and Known Gaps
sources: [client/src/api.js, client/src/main.js, client/src/views/Reports.vue, server/main.py, server/generate_data.py, tests/README.md]
updated: 2026-11-05
---

# Gotchas and Known Gaps

All items below were confirmed in the code on 2026-11-05.

## Broken or incomplete features

1. **Tasks API is missing.** `App.vue` calls `api.getTasks()` on mount. The backend has no `/api/tasks` route, so the request returns 404. The add, delete and toggle functions also fail.
2. **Purchase order API is missing.** `api.createPurchaseOrder` and `api.getPurchaseOrderByBacklogItem` call `/api/purchase-orders`, which does not exist. No component calls these two functions today. `server/main.py` defines `CreatePurchaseOrderRequest`, but no route uses it. `purchase_orders.json` is empty.
3. **Backlog view has no route.** `client/src/views/Backlog.vue` exists, but `main.js` does not register it.

## Risks

4. **Data generator is stale.** `server/generate_data.py` writes `data/orders.json` with old categories (Widgets, Components, Equipment, Consumables). They do not match `inventory.json`. Do not run it without a review.
5. **Year 2025 is hardcoded.** `QUARTER_MAP` and `/api/reports/quarterly` support only 2025.
6. **API URL is hardcoded.** `api.js` and `Reports.vue` use `http://localhost:8001`. A deployed build cannot use another host without a code change.
7. **Mixed component styles.** `Reports.vue` uses the classic Options API and does not use `api.js`. Do not copy this pattern.

## Documentation drift

8. `tests/README.md` lists `test_orders.py` with 15 tests. The file does not exist. 40 tests exist today.
9. The README says that all endpoints support all filters. In fact, only `/api/orders` and `/api/dashboard/summary` support all four.

## Rules from the root CLAUDE.md

- Use unique keys in `v-for`, for example `sku` or `month`. Do not use `index`.
- Validate a date before you call `.getMonth()`.
- Revenue goals: $800K for one month, $9.6M for the full year.

Related: [Frontend](frontend.md), [Backend API](backend-api.md), [Testing](testing.md).
