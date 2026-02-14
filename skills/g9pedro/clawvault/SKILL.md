---
name: clawvault
version: 2.4.2
description: "Agent memory system with memory graph, context profiles, checkpoint/recover, structured storage, semantic search, observational memory, task tracking, canvas dashboards, Obsidian integration, and Tailscale networking. Use when: storing/searching memories, preventing context death, graph-aware context retrieval, repairing broken sessions, tracking tasks, generating dashboards. Don't use when: general file I/O."
author: Versatly
repository: https://github.com/Versatly/clawvault
homepage: https://clawvault.dev
docs: https://docs.clawvault.dev
metadata:
  {
    "openclaw":
      {
        "emoji": "🐘",
        "kind": "cli",
        "requires":
          {
            "bins": ["clawvault"],
            "env_optional": ["CLAWVAULT_PATH", "GEMINI_API_KEY", "OPENCLAW_HOME", "OPENCLAW_STATE_DIR"]
          },
        "install":
          [
            {
              "id": "node",
              "kind": "node",
              "package": "clawvault",
              "bins": ["clawvault"],
              "label": "Install ClawVault CLI (npm)"
            }
          ],
        "hooks":
          {
            "clawvault":
              {
                "events": ["gateway:startup", "command:new"],
                "capabilities":
                  [
                    "auto-checkpoint before session reset (/new)",
                    "context death detection and alert injection on startup"
                  ],
                "does_not":
                  [
                    "make network calls (except optional GEMINI_API_KEY for observe/reflect, Tailscale for serve/peers)",
                    "access external APIs or cloud services (except optional Tailscale mesh)",
                    "send telemetry or analytics",
                    "modify files outside vault directory and OpenClaw session transcripts"
                  ]
              }
          },
        "capabilities":
          [
            "reads/writes markdown files in vault directory",
            "reads/modifies OpenClaw session transcripts (repair-session, with backup)",
            "builds memory graph index (.clawvault/graph-index.json)",
            "runs qmd for semantic search (optional, graceful fallback)",
            "LLM API calls for observe/reflect (optional, requires GEMINI_API_KEY)",
            "task tracking with status, priority, and blocking relationships",
            "Obsidian JSON Canvas dashboard generation (4 templates: default, brain, project-board, sprint)",
            "Obsidian Bases view generation (5 .base files for task management)",
            "Neural graph theme with colored nodes by category",
            "Tailscale-based vault networking, cross-vault search, observation forwarding"
          ]
      }
  }
---

# ClawVault 🐘

An elephant never forgets. Structured memory for AI agents.

> **Docs:** [docs.clawvault.dev](https://docs.clawvault.dev) | **npm:** [clawvault](https://www.npmjs.com/package/clawvault)

## Security & Transparency

**What this skill does:**
- Reads/writes markdown files in your vault directory (`CLAWVAULT_PATH` or auto-discovered)
- `repair-session` reads and modifies OpenClaw session transcripts — creates backups before writing
- Installs an OpenClaw **hook** (`hooks/clawvault/handler.js`) that runs on `gateway:startup` and `command:new` to auto-checkpoint and detect context death
- `observe` makes LLM API calls (Gemini Flash by default) to compress session transcripts
- `reflect` makes LLM API calls to generate weekly reflection summaries
- `serve` starts an HTTP API on your Tailscale IP for cross-vault networking

**Environment variables used:**
- `CLAWVAULT_PATH` — vault location (optional, auto-discovered)
- `OPENCLAW_HOME` / `OPENCLAW_STATE_DIR` — used by `repair-session` to find transcripts
- `GEMINI_API_KEY` — used by `observe` and `reflect` for LLM compression (optional)

**No cloud sync — all data stays local.**

## Install

```bash
npm install -g clawvault
```

## Init & Setup

```bash
# Initialize a new vault (creates categories + ledger + templates + welcome note)
clawvault init ~/my-vault

# Minimal vault (memory categories only, no tasks/bases/graph)
clawvault init ~/my-vault --minimal

# Custom categories
clawvault init ~/my-vault --categories "notes,ideas,contacts,projects"

# Skip specific features
clawvault init ~/my-vault --no-bases --no-tasks --no-graph

# Apply neural graph theme on init
clawvault init ~/my-vault --theme neural

# Generate canvas on init
clawvault init ~/my-vault --canvas brain

# Full Obsidian setup (theme + bases + canvas on existing vault)
clawvault setup
clawvault setup --theme neural --canvas brain --bases

# Or set env var to use existing vault
export CLAWVAULT_PATH=/path/to/memory
```

### Init Flags (v2.4.0+)

| Flag | Description |
|------|-------------|
| `-n, --name <name>` | Vault name (defaults to directory name) |
| `--minimal` | Memory categories only — no tasks, bases, or graph |
| `--categories <list>` | Comma-separated custom categories |
| `--no-bases` | Skip Obsidian Bases file generation |
| `--no-tasks` | Skip tasks/ and backlog/ directories |
| `--no-graph` | Skip initial graph build |
| `--canvas <template>` | Generate canvas (default, brain, project-board, sprint) |
| `--theme <style>` | Graph color theme (neural, minimal, none) |
| `--qmd` | Set up qmd semantic search collection |

### Setup Flags (v2.4.0+)

| Flag | Description |
|------|-------------|
| `--theme <style>` | Graph color theme: neural (default), minimal, none |
| `--graph-colors / --no-graph-colors` | Enable/skip graph color scheme |
| `--bases / --no-bases` | Generate/skip Obsidian Bases views |
| `--canvas [template]` | Generate canvas dashboard |
| `--force` | Overwrite existing configuration files |
| `-v, --vault <path>` | Vault path |

## Quick Start

```bash
# Start your session
clawvault wake

# Capture and checkpoint during work
clawvault capture "TODO: Review PR tomorrow"
clawvault checkpoint --working-on "PR review" --focus "type guards"

# End your session
clawvault sleep "PR review + type guards" --next "respond to CI" --blocked "waiting for CI"

# Health check
clawvault doctor
```

## What's New

### v2.4.x — Init Customization + Canvas Templates + Neural Theme + Obsidian Bases

- **Init flags:** `--minimal`, `--categories`, `--no-bases`, `--no-tasks`, `--no-graph`, `--canvas`, `--theme`, `--name`
- **Existing vault detection:** Init errors on existing vault instead of silently overwriting
- **4 canvas templates:** default, brain (4-quadrant architecture), project-board (owner-centric), sprint
- **Canvas flags:** `--owner`, `--width`, `--height`, `--include-done`, `--list-templates`
- **Setup flags:** `--theme neural|minimal|none`, `--graph-colors`, `--bases`, `--canvas`, `--force`
- **Neural graph theme:** Dark bg, colored nodes by category/tag, green neural links, golden focus glow
- **Obsidian Bases:** 5 .base files auto-generated (all-tasks, blocked, by-project, by-owner, backlog)
- **Date handling fix:** Bare dates in frontmatter no longer crash commands

### v2.3.0 — Task Tracking + Canvas Dashboard + Tailscale Networking

- **Task management:** `clawvault task` (add/list/update/done/show) and `clawvault backlog` (add/list/promote)
- **Canvas dashboard:** `clawvault canvas` generates Obsidian JSON Canvas
- **Blocked view:** `clawvault blocked` for quick view of blocked tasks
- **Tailscale networking:** `clawvault serve`, `clawvault peers`, `clawvault net-search`

### v2.2.0 — Ledger + Reflection + Replay

- **Ledger-first architecture:** `ledger/raw/` source of truth
- **Reflections:** `clawvault reflect` generates weekly reflections
- **Replay/Rebuild/Archive:** `clawvault replay`, `clawvault rebuild`, `clawvault archive`

### v2.0.0 — Memory Graph + Context Profiles

- Memory graph from wiki-links, tags, frontmatter
- Graph-aware context retrieval with profiles (default, planning, incident, handoff)
- OpenClaw compat diagnostics

---

## Core Commands

### Wake + Sleep

```bash
clawvault wake
clawvault sleep "what I was working on" --next "ship v1" --blocked "waiting for API key"
```

### Store memories by type

```bash
clawvault remember decision "Use Postgres over SQLite" --content "Need concurrent writes"
clawvault remember lesson "Context death is survivable" --content "Checkpoint before heavy work"
clawvault remember relationship "Justin Dukes" --content "Client at Hale Pet Door"
```

### Quick capture

```bash
clawvault capture "TODO: Review PR tomorrow"
```

### Search

```bash
clawvault search "client contacts"        # Keyword (fast)
clawvault vsearch "database decision"     # Semantic (slower, more accurate)
```

## Task Tracking (v2.3.0+)

```bash
clawvault task add "Ship v2.4.0" --priority high
clawvault task list
clawvault task list --status blocked
clawvault task update <id> --status in-progress
clawvault task done <id>
clawvault blocked                          # Quick blocked view
clawvault backlog add "Voice memo capture"
clawvault backlog promote <id>
```

## Canvas Dashboard (v2.3.0+)

```bash
# Generate with default template
clawvault canvas

# Choose template
clawvault canvas --template brain           # 4-quadrant architecture view
clawvault canvas --template project-board   # Owner-centric with agent/human cards
clawvault canvas --template sprint          # Sprint-focused view

# Filter and customize
clawvault canvas --owner agent-alpha        # Filter to one owner
clawvault canvas --include-done             # Include completed tasks
clawvault canvas --width 1600 --height 1200

# List available templates
clawvault canvas --list-templates
```

## Obsidian Integration (v2.4.0+)

### Neural Graph Theme

```bash
clawvault setup --theme neural    # Dark bg, colored nodes, green links, golden glow
clawvault setup --theme minimal   # Subtle category colors
clawvault setup --theme none      # No theme changes
```

### Bases Views

Auto-generated `.base` files for Obsidian Bases plugin:
- `all-tasks.base` — Active tasks grouped by status
- `blocked.base` — Blocked tasks with blockers
- `by-project.base` — Tasks grouped by project
- `by-owner.base` — Tasks grouped by owner (agent/human)
- `backlog.base` — Backlog items by source

```bash
clawvault setup --bases           # Generate bases files
```

## Observer (v2.1.0+)

```bash
clawvault observe                  # Watch current session
clawvault observe --compress file  # One-shot compression
```

Observations use scored importance: `[type|c=confidence|i=importance]`

## Ledger (v2.2.0+)

```bash
clawvault reflect                  # Generate weekly reflection
clawvault replay --last 7d         # Replay recent events
clawvault rebuild                  # Rebuild from raw ledger
clawvault archive --before 2026-01-01
```

## Memory Graph (v2.0.0+)

```bash
clawvault graph                    # View graph summary
clawvault graph --refresh          # Rebuild index
clawvault context "topic"          # Graph-aware context retrieval
clawvault context --profile planning "Q1 roadmap"
clawvault entities                 # List linkable entities
clawvault link --all               # Auto-link mentions
```

## Context Death Resilience

```bash
clawvault wake                     # Start session (recover + recap)
clawvault checkpoint --working-on "task" --focus "details"
clawvault sleep "summary" --next "next steps" --blocked "blockers"
clawvault recover --clear          # Manual recovery check
clawvault handoff --working-on "task" --next "next" --blocked "blocker"
```

## Tailscale Networking (v2.3.0+)

```bash
clawvault serve                    # Serve vault on Tailscale (port 7283)
clawvault peers                    # Manage vault peers
clawvault net-search "query"       # Cross-vault search
```

## Session Repair

```bash
clawvault repair-session --dry-run
clawvault repair-session
clawvault repair-session --list
```

Fixes orphaned tool_result blocks, aborted tool calls, broken parent chains.

## Vault Structure

```
vault/
├── .clawvault.json          # Vault config
├── .clawvault/              # Internal state (graph-index, checkpoints)
├── decisions/
├── lessons/
├── people/
├── projects/
├── goals/
├── preferences/
├── patterns/
├── commitments/
├── handoffs/
├── transcripts/
├── agents/
├── research/
├── inbox/
├── tasks/                   # Task tracking
├── backlog/                 # Backlog items
├── templates/               # 7 templates (daily-note, decision, checkpoint, etc.)
├── ledger/
│   ├── raw/                 # Raw session transcripts
│   ├── observations/        # Compressed observations
│   └── reflections/         # Weekly reflections
├── *.base                   # Obsidian Bases views (5 files)
├── dashboard.canvas         # Generated canvas
└── README.md                # Auto-generated vault docs
```

**16 default categories:** decisions, lessons, people, projects, goals, preferences, patterns, commitments, handoffs, transcripts, agents, research, inbox, tasks, backlog, templates

Custom categories supported via `--categories` on init.

## OpenClaw Hook

The bundled hook (`hooks/clawvault/handler.js`) provides:

| Event | Action |
|-------|--------|
| `gateway:startup` | Runs `clawvault recover --clear`, injects alert if context death detected |
| `command:new` | Auto-checkpoints before session reset |

**Note:** The hook also has a `session:start` handler for forward compatibility — it will activate when OpenClaw adds `session:start` event support.

Enable:
```bash
openclaw hooks enable clawvault
```

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `CLAWVAULT_PATH` | Default vault path (skips auto-discovery) |
| `OPENCLAW_HOME` | OpenClaw home directory (for repair-session) |
| `OPENCLAW_STATE_DIR` | OpenClaw state directory (for repair-session) |
| `GEMINI_API_KEY` | LLM compression for observe/reflect (optional) |

## Troubleshooting

- **qmd not installed** — `npm install -g qmd` or `bun install -g github:tobi/qmd`
- **No vault found** — `clawvault init` or set `CLAWVAULT_PATH`
- **Init fails "already exists"** — vault already initialized at that path
- **"unexpected tool_use_id"** — `clawvault repair-session`
- **Graph out of date** — `clawvault graph --refresh`
- **Old emoji observations** — `clawvault migrate-observations`
- **OpenClaw drift** — `clawvault compat`

## Links

- Docs: https://docs.clawvault.dev
- npm: https://www.npmjs.com/package/clawvault
- GitHub: https://github.com/Versatly/clawvault
