# LLM Wiki - Schema

This folder is an LLM-maintained wiki about the `inventory-management` codebase. The LLM writes and updates the pages. The human reads them and asks questions.

## Layers

1. **Sources (read-only):** the files of the repository (`server/`, `client/`, `tests/`, `scripts/`, `.claude/`). The wiki never changes a source file.
2. **Wiki (LLM-owned):** the markdown pages in `wiki/pages/`, plus `index.md` and `log.md`.
3. **Schema:** this file. It defines the conventions and the operations.

## Page conventions

- Write one topic on each page. The file name is kebab-case, for example `filter-system.md`.
- Start each page with a YAML front matter block:

  ```yaml
  ---
  title: Filter System
  sources: [server/main.py, client/src/composables/useFilters.js]
  updated: 2026-11-05
  ---
  ```

- Link other pages with relative links, for example `[Data Model](data-model.md)`.
- Give a `path:line` reference for each claim that is not obvious.
- Write facts that you read in the code. If you are not sure, write "Unverified:" before the claim.
- Use ASD-STE100 Simplified Technical English.

## Operations

### Ingest (after a code change)
1. Read the changed source files.
2. Update each page whose `sources` list contains a changed file. Change `updated`.
3. If a new topic appears, create a page and add it to `index.md`.
4. Add one entry to `log.md`.

### Query (when the human asks a question)
1. Read `index.md` to find the related pages.
2. Read those pages, then read the source files to confirm.
3. Answer with links to the pages and to the source lines.
4. If the answer is useful in the future, add it to a page and log it.

### Lint (on request)
1. For each page, confirm that the files in `sources` still exist.
2. Confirm that each `path:line` reference still points to the correct code.
3. Find pages that `index.md` does not list, and links that do not resolve.
4. Record the result in `log.md`.

## log.md format

Add new entries at the top:

```
## 2026-11-05 - ingest - <short title>
- Pages changed: a.md, b.md
- Reason: <one sentence>
```
