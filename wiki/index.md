# Inventory Management - LLM Wiki

An LLM-maintained knowledge base about this codebase. Read `CLAUDE.md` in this folder for the rules that keep it current.

## Start here

- [Overview](pages/overview.md) - what the app is, key facts and numbers
- [Architecture](pages/architecture.md) - tiers, diagram, design decisions

## System

- [Frontend](pages/frontend.md) - Vue app, routes, views, components, `api.js`
- [Backend API](pages/backend-api.md) - FastAPI routes, KPI calculation, CORS
- [Data Model](pages/data-model.md) - JSON files, Pydantic models, relations
- [Filter System](pages/filter-system.md) - the four global filters through all layers
- [Internationalization](pages/i18n.md) - EN/JA, `t()`, currency conversion

## Work

- [Development Workflow](pages/dev-workflow.md) - start, build, change checklist
- [Testing](pages/testing.md) - pytest setup, commands, gaps
- [Claude Code Tooling](pages/claude-tooling.md) - agents, commands, skill, hook, MCP
- [Gotchas and Known Gaps](pages/gotchas.md) - missing endpoints, stale scripts, drift

## Related

- [Architecture page (HTML)](../docs/architecture.html)
- [Change log](log.md)
