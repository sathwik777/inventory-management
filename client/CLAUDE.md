# CLAUDE.md - Client

Guidance for the Vue 3 frontend. See the root `CLAUDE.md` for architecture and commands.

## Run

```bash
npm run dev      # http://localhost:3000
npm run build    # output: dist/
```

## Conventions

- Delegate each new or large `.vue` change to the `vue-expert` agent (rule from the root `CLAUDE.md`).
- Views use `export default { setup() }`. Small modal components use `<script setup>`. Do not copy `Reports.vue`. It uses the classic Options API and calls `axios` directly.
- Call the backend only through `src/api.js`. Leave out filter values that are `'all'`.
- Use `useFilters()` for the global filters. The refs are module-level singletons. Call `getCurrentFilters()` to get the API parameter names (`warehouse`, `month`).
- Keep raw API data in refs. Calculate display data in `computed` properties. Reload in a `watch` on the filter refs that the view uses.
- Show loading and error states. Use the global `.loading` and `.error` classes from `App.vue`.
- Add each UI string to both `src/locales/en.js` and `ja.js`, and render it with `t()`.
- Format money with `src/utils/currency.js` and `currentCurrency` from `useI18n()`. Do not format money by hand.
- Draw charts with inline SVG or CSS. Do not add a chart library.
- Use unique `v-for` keys (`sku`, `id`, `month`). Do not use `index`.
- Validate a date before you call `.getMonth()`.
- Do not use emojis in the UI. Use the slate palette (`#0f172a`, `#64748b`, `#e2e8f0`).

## Gotchas

- `api.getTasks()` and the other task functions call `/api/tasks`. The purchase order functions call `/api/purchase-orders`. The backend has neither route, so the calls return 404.
- `src/views/Backlog.vue` is not registered in `src/main.js`.
- The API base URL `http://localhost:8001/api` is hardcoded. There is no Vite proxy.
