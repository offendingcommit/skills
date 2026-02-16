---
name: soulforge
description: "Dispatch multi-step coding workflows to Claude Code CLI or Codex CLI from YAML definitions via a persistent background daemon. Use when: (1) implementing a feature end-to-end (plan → implement → verify → PR), (2) delegating coding tasks to run in the background while you do other work, (3) running development workflows that need human review checkpoints, (4) automating feature branch creation, implementation, and PR submission. Requires the @ghostwater/soulforge npm package."
metadata:
  {
    "openclaw":
      {
        "emoji": "🔥",
        "requires": { "bins": ["soulforge", "claude", "gh", "git"], "env": [] },
        "install":
          [
            {
              "id": "npm",
              "kind": "npm",
              "package": "@ghostwater/soulforge",
              "global": true,
              "bins": ["soulforge"],
              "label": "Install Soulforge CLI (npm)",
            },
          ],
      },
  }
---

# Soulforge

Soulforge is a daemon-based workflow engine that dispatches coding steps to executor CLIs (Claude Code, Codex) and pauses at human review checkpoints.

## Install & Start

```bash
npm install -g @ghostwater/soulforge
soulforge daemon start
```

## Core Workflow

```bash
# Run a feature-dev workflow against a repo
soulforge run feature-dev "Add user authentication with JWT tokens" \
  --var repo=/path/to/project \
  --var build_cmd="npm run build" \
  --var test_cmd="npm test"
```

This auto-creates a git worktree, then runs: **plan → review → implement → verify → test → PR → final-review**.

Steps using `executor: self` pause for human approval:

```bash
soulforge approve <run-id>              # approve checkpoint
soulforge reject <run-id> --reason "…"  # reject with feedback
```

## Key Commands

| Command | What it does |
|---------|-------------|
| `soulforge run <workflow> "<task>" [flags]` | Start a workflow run |
| `soulforge status [<query>]` | Check run status (ID prefix or task substring) |
| `soulforge runs` | List all runs |
| `soulforge approve <run-id>` | Approve a checkpoint |
| `soulforge reject <run-id> --reason "…"` | Reject a checkpoint |
| `soulforge cancel <run-id>` | Cancel a running workflow |
| `soulforge resume <run-id>` | Resume a failed run |
| `soulforge events [--run <id>] [--follow]` | Stream workflow events |
| `soulforge logs [<lines>]` | Show daemon log |
| `soulforge daemon start/stop/status` | Manage the daemon |

## Run Flags

- `--var key=value` — pass variables (e.g. `repo`, `build_cmd`, `test_cmd`)
- `--workdir <path>` — use an existing directory instead of auto-creating a worktree
- `--no-worktree` — work directly in the repo (no worktree creation)
- `--branch <name>` — custom branch name (default: auto-generated from task)
- `--callback-url <url>` — POST notification on run completion (see Callbacks below)
- `--callback-headers <json>` — headers for callback request
- `--callback-body <json>` — body template with `{{run_id}}`, `{{status}}`, `{{task}}` placeholders

## Callbacks

Soulforge supports framework-agnostic callbacks. On run completion, it POSTs to any URL you configure:

```bash
soulforge run feature-dev "Add caching layer" \
  --var repo=/path/to/project \
  --callback-url "http://127.0.0.1:18789/hooks/agent" \
  --callback-headers '{"Authorization":"Bearer <token>","Content-Type":"application/json"}' \
  --callback-body '{"message":"Soulforge run {{run_id}} finished: {{status}}. Task: {{task}}","sessionKey":"<your-session-key>"}'
```

The callback system is fully opaque — Soulforge doesn't know what's receiving the POST. Callers own routing.

## Prerequisites

Soulforge requires:
- **`soulforge` CLI** — installed globally via `npm install -g @ghostwater/soulforge` ([source](https://github.com/ghostwater-ai/soulforge), maintainer: `@ghostwater` npm org)
- **`claude` CLI** (Claude Code) or **`codex` CLI** — the executor that actually runs code
- **`gh` CLI** — for PR creation steps (authenticated via `gh auth login`)
- **`git`** — for worktree creation and branch management

Credentials are managed by the executor CLIs, not by Soulforge.

## Security Notes

- **Callbacks are opt-in** — Soulforge only POSTs to URLs you explicitly provide via `--callback-url`. Never embed secrets in `--callback-headers` or `--callback-body` unless you trust the receiving endpoint. Prefer localhost or internal URLs.
- **Daemon blast radius** — The daemon can modify repos and invoke CLIs with whatever credentials those CLIs have. Run initial tests against non-sensitive repos.
- **Credential scoping** — Ensure `gh`, `claude`/`codex` are scoped to minimum necessary permissions.

## Workflow Format

See [references/workflow-format.md](references/workflow-format.md) for the full YAML schema and how to write custom workflows.

## Convention: Specs as GitHub Issues

Write detailed specs as GitHub issue bodies, then reference them in the task string:

```bash
soulforge run feature-dev "Find the full task https://github.com/org/repo/issues/42" \
  --var repo=/path/to/project
```

The executor reads the issue URL and implements accordingly.

## Git Worktree Behavior

By default, when `--var repo=<path>` points to a git repository:
- **Bare+worktree layout** (`.bare/` + `main/`): creates worktree in sibling `worktrees/` directory
- **Standard `.git` layout**: creates worktree in `worktrees/` inside the repo
- **Not a git repo**: works in-place (no git operations)

Override with `--workdir` (use existing directory) or `--no-worktree` (work directly in repo).
