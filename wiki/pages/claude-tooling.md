---
title: Claude Code Tooling
sources: [CLAUDE.md, .claude/, .mcp.json]
updated: 2026-11-05
---

# Claude Code Tooling

This repository is a demo for a Claude Code workshop. The `.claude/` folder holds agents, slash commands, a skill and a hook.

## Agents (`.claude/agents/`)

| Agent | Model | Tools | Use |
|---|---|---|---|
| `vue-expert` | sonnet | Read, Write, Edit, Glob, Grep, Bash, Playwright | Mandatory for each new or large change to a `.vue` file |
| `code-reviewer` | sonnet | Read, Grep, Glob | Review after significant code changes |
| `security-auditor` | haiku | Read, Grep, Glob | Fast security review of changed files |

## Slash commands (`.claude/commands/`)

| Command | Purpose |
|---|---|
| `/start` | Start the frontend and backend servers |
| `/stop` | Stop the servers |
| `/test` | Run tests and report |
| `/demo-branch` | Create a demo branch with a number that increments |
| `/reset-branch` | Go back to `main` and delete the last branch |
| `/optimize` | No `description` in the front matter |

## Skill

`backend-api-test` (`.claude/skills/backend-api-test`) gives rules for pytest tests in `tests/backend/`.

## Hook

`.claude/hooks/post-tool-use.sh` writes each tool call to `logs/tool-usage-YYYY-MM-DD.log`. It uses `jq` if it is installed. No `.claude/settings.json` in this repository registers the hook, so it does not run by default.

## MCP servers

- `.mcp.json` defines `playwright` (`@playwright/mcp@0.0.37`) and `github` (`@modelcontextprotocol/server-github`).
- The `github` server reads the token from the environment variable `GITHUB_PERSONAL_ACCESS_TOKEN`.
- `.claude/mcp-config.json` is a second, older copy that uses `@playwright/mcp@latest`.

## Session start folder

Start Claude Code in the `inventory-management/` folder. If the session starts in a parent folder, Claude Code does not load the project agents (`vue-expert`, `code-reviewer`, `security-auditor`) or the MCP servers from `.mcp.json`. On 2026-11-05 this happened: the `vue-expert` agent was "not found", and no `mcp__playwright__*` tools were available.

Playwright is also installed globally on the development machine: npm `playwright@1.64.1` with Chromium, and Python `playwright 1.60`. A plain Playwright script can test the UI when the MCP tools are not loaded.

## Rules from the root CLAUDE.md

- Use the GitHub MCP tools for all GitHub operations. Use `git checkout -b` for local branches.
- Use the Playwright MCP tools for browser tests against ports 3000 and 8001.
- The repository is public. Do not commit credentials, internal hostnames or private registry URLs. Keep `client/.npmrc`, and keep `client/package-lock.json` out of git.

Related: [Development Workflow](dev-workflow.md).
