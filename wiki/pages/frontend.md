---
title: Frontend
sources: [client/src/main.js, client/src/App.vue, client/src/api.js, client/src/views/, client/src/components/, client/vite.config.js]
updated: 2026-11-05
---

# Frontend

The frontend is a Vue 3 single-page app that Vite builds. The Vite dev server runs on port 3000. There is no proxy and there are no path aliases (`client/vite.config.js`). The only plugin is `@vitejs/plugin-vue`. Runtime dependencies are `vue`, `vue-router` and `axios`.

## Boot and layout

- `client/src/main.js` creates the app and a router with `createWebHistory`, then mounts it on `#app`.
- `App.vue` has a sticky top navigation bar with the logo, the tabs, `LanguageSwitcher` and `ProfileMenu`. Below it are `FilterBar` and `<router-view />`.
- `App.vue` also holds `ProfileDetailsModal` and `TasksModal`. On mount, it calls `api.getTasks()` (`App.vue:91`).
- The global CSS is the unscoped `<style>` block in `App.vue` (lines 164-486). There is no CSS framework.

## Routes and views

| Path | View | API calls | Filters watched |
|---|---|---|---|
| `/` | `Dashboard.vue` | `getDashboardSummary`, `getOrders`, `getInventory`, `getBacklog` | all four |
| `/inventory` | `Inventory.vue` | `getInventory` | location, category |
| `/orders` | `Orders.vue` | `getOrders`, `getRestockOrders` | all four (not for submitted restock orders) |
| `/demand` | `Demand.vue` | `getDemandForecasts`, `getInventory({})` | location, category |
| `/restocking` | `Restocking.vue` | `getRestockRecommendations`, `createRestockOrder` | none |
| `/spending` | `Spending.vue` | spending functions, `getOrders()` | period |
| `/reports` | `Reports.vue` | direct `axios` calls to `/api/reports/*` | none |
| (no route) | `Backlog.vue` | `getBacklog`, `getInventory({})` | location, category |

`Backlog.vue` exists, but `main.js:13-20` does not register it. Users cannot open it.

## API client

`client/src/api.js` exports one object, `api`. Its base URL is hardcoded as `http://localhost:8001/api`. Each function adds the filters as query parameters and leaves out the value `'all'`.

These `api.js` functions call routes that the backend does not have, so they get HTTP 404:

- `getTasks`, `createTask`, `deleteTask`, `toggleTask` call `/api/tasks`.
- `createPurchaseOrder` and `getPurchaseOrderByBacklogItem` call `/api/purchase-orders`. No component calls them today.

## Restocking view

`client/src/views/Restocking.vue` has three cards:

1. **Budget:** an `<input type="range">` from 0 to `max_budget` with step 100. `@input` changes only the displayed value. `@change` (when the user releases the slider) loads the recommendations again. The first load sends no budget, so the server default (50 % of the max) applies.
2. **Candidates:** a table with a checkbox for each item. New recommendations reset the checkboxes to the `recommended` flags. The user can check any item. `selectedMap` is a plain object in a ref, keyed by SKU.
3. **Summary:** the selected total, the remaining budget (red if negative) and the order lead time (the largest lead time of the selected items). "Place Order" is disabled if nothing is selected, the total is over the budget, or a request is in progress.

Money values use `formatCurrencyWithDecimals(..., 2)` through the local `formatMoney()`. The budget labels use `formatCurrency` (whole numbers). The global filters do not apply to this view.

The Orders view shows the submitted restock orders in a separate card above the stat cards. It loads them one time on mount, not in the filter `watch`.

## Components

| Component | Used in | Purpose |
|---|---|---|
| `FilterBar.vue` | App.vue | Four dropdowns bound to `useFilters` |
| `LanguageSwitcher.vue` | App.vue | Toggles EN and JA |
| `ProfileMenu.vue` | App.vue | Avatar menu: profile, tasks, logout |
| `ProfileDetailsModal.vue` | App.vue | Shows `useAuth().currentUser` |
| `TasksModal.vue` | App.vue | Add, delete and toggle tasks |
| `ProductDetailModal.vue` | Dashboard | Product revenue and stock |
| `BacklogDetailModal.vue` | Dashboard | Backlog shortage detail |
| `InventoryDetailModal.vue` | Inventory | Item detail and cost |
| `CostDetailModal.vue` | Spending | Cost by category |

## Code style

- Most views use `export default { setup() }`.
- Most modal components use `<script setup>`.
- `Reports.vue` is the exception. It uses the classic Options API (`data()`, `methods`) and calls `axios` directly.
- Charts are hand-made. The order donut on the Dashboard is inline SVG (`Dashboard.vue:87-113`). The bar charts are `div` elements with a percentage height. There is no chart library.

## Composables

- `useFilters`: shared filter state. See [Filter System](filter-system.md).
- `useI18n`: locale, translation and currency. See [Internationalization](i18n.md).
- `useAuth`: mock authentication. `isAuthenticated` is always `true`, and `logout()` only shows an `alert()` (`useAuth.js:92-97`). The profile of `currentUser` changes with the locale.

Related: [Architecture](architecture.md), [Gotchas](gotchas.md).
