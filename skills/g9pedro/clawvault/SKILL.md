---
name: clawvault
version: 1.11.3
description: Agent memory system with checkpoint/recover, structured storage, observational memory, and session transcript repair. Integrates with OpenClaw's qmd memory backend for BM25+vector+reranker search. Use when: storing/searching memories, preventing context death, repairing broken sessions. Don't use when: general file I/O.
author: Versatly
repository: https://github.com/Versatly/clawvault
homepage: https://clawvault.dev
metadata: {"openclaw":{"emoji":"🐘","requires":{"bins":["clawvault"]},"env":{"CLAWVAULT_PATH":{"required":false,"description":"Vault directory path (auto-discovered if not set)"},"GEMINI_API_KEY":{"required":false,"description":"Only used by observe --compress for LLM compression. No other command uses this."}},"hooks":{"clawvault":{"events":["gateway:startup","command:new"],"capabilities":["executes clawvault CLI via child_process","reads vault state files","injects recovery alerts into session on context death","runs clawvault checkpoint before /new","runs clawvault observe --compress on session transcript (if GEMINI_API_KEY set)"],"does_not":["modify session transcripts (only the repair-session CLI command does that, never the hook)","make network calls (the hook itself makes zero network calls; observe --compress may call Gemini API)","access files outside the vault directory and session transcript path"]}},"install":[{"id":"node","kind":"node","package":"clawvault","bins":["clawvault"],"label":"Install ClawVault CLI (npm)"}]}}
---

# ClawVault 🐘

An elephant never forgets. Structured memory for OpenClaw agents.

> **Built for [OpenClaw](https://openclaw.ai)** — install via `clawhub install clawvault`

## Security & Transparency

**What this skill does — full disclosure:**

| Capability | Scope | Opt-in? |
|---|---|---|
| Read/write markdown files | Your vault directory only (`CLAWVAULT_PATH` or auto-discovered) | Always active |
| Search vault (keyword + semantic) | Read-only queries via `qmd` CLI | Always active |
| Checkpoint/recover/wake/sleep | Writes state files inside `.clawvault/` in your vault | Always active |
| `repair-session` — fix broken session transcripts | Reads + modifies JSONL files in `~/.openclaw/agents/`. **Always creates `.bak` backup before writing.** Use `--dry-run` to preview changes without modifying anything. | Explicit command only |
| OpenClaw hook (`handler.js`) | Runs on `gateway:startup` and `command:new` events. Calls `clawvault checkpoint` and `clawvault recover`. Does NOT make network calls. | **Opt-in** — must run `openclaw hooks enable clawvault` |
| `observe --compress` — LLM compression | Sends session transcript text to Gemini Flash API to extract observations. **This is the ONLY feature that makes external API calls.** Requires `GEMINI_API_KEY` to be set. Without the key, this feature is completely inert. | Explicit command only + requires API key |

**Network calls:** Zero by default. The only feature that contacts an external API is `observe --compress`, and only when you explicitly run it with a valid `GEMINI_API_KEY`. All other commands are pure local filesystem operations.

**Environment variables used:**
- `CLAWVAULT_PATH` — vault location (optional, auto-discovered if not set)
- `OPENCLAW_HOME` / `OPENCLAW_STATE_DIR` — used by `repair-session` to locate session transcripts
- `GEMINI_API_KEY` — used **only** by `observe --compress` for LLM compression. If not set, observe runs without compression (rule-based fallback). No other command reads this key.
- `CLAWVAULT_NO_LLM=1` — force-disable all LLM calls even if API key is present

**No cloud sync. No telemetry. No analytics. No phone-home. All data stays on your machine.**

## Hook Behavior (`hooks/clawvault/handler.js`)

The bundled hook is **opt-in** — it does nothing until you run `openclaw hooks enable clawvault`.

When enabled, it handles two events:

| Event | What it does | Network calls? |
|---|---|---|
| `gateway:startup` | Runs `clawvault recover --clear` to check for context death. If detected, injects a recovery alert into the session. | **None** |
| `command:new` | Runs `clawvault checkpoint` to save state before reset. Then runs `clawvault observe --compress` on the session transcript if a transcript file exists. | **Only if `GEMINI_API_KEY` is set** (for observe compression). Without the key, observe uses rule-based fallback with zero network calls. |

**What the hook does NOT do:**
- Does NOT modify session transcripts (that's `repair-session`, a separate explicit CLI command)
- Does NOT read or write files outside the vault directory
- Does NOT phone home, collect analytics, or contact any server except the optional Gemini API for observe

The hook executes the `clawvault` CLI binary via `child_process.execSync`. The binary must be installed separately (`npm install -g clawvault`). The hook source is fully readable at `hooks/clawvault/handler.js`.

## Install

```bash
npm install -g clawvault
```

## Setup

```bash
# Initialize vault (creates folder structure + templates)
clawvault init ~/my-vault

# Or set env var to use existing vault
export CLAWVAULT_PATH=/path/to/memory

# Optional: shell integration (aliases + CLAWVAULT_PATH)
clawvault shell-init >> ~/.bashrc
```

## Quick Start for New Agents

```bash
# Start your session (recover + recap + summary)
clawvault wake

# Capture and checkpoint during work
clawvault capture "TODO: Review PR tomorrow"
clawvault checkpoint --working-on "PR review" --focus "type guards"

# End your session with a handoff
clawvault sleep "PR review + type guards" --next "respond to CI" --blocked "waiting for CI"

# Health check when something feels off
clawvault doctor
```

## Core Commands

### Wake + Sleep (primary)

```bash
clawvault wake
clawvault sleep "what I was working on" --next "ship v1" --blocked "waiting for API key"
```

### Store memories by type

```bash
# Types: fact, feeling, decision, lesson, commitment, preference, relationship, project
clawvault remember decision "Use Postgres over SQLite" --content "Need concurrent writes for multi-agent setup"
clawvault remember lesson "Context death is survivable" --content "Checkpoint before heavy work"
clawvault remember relationship "Justin Dukes" --content "Client contact at Hale Pet Door"
```

### Quick capture to inbox

```bash
clawvault capture "TODO: Review PR tomorrow"
```

### Search (requires qmd installed)

```bash
# Keyword search (fast)
clawvault search "client contacts"

# Semantic search (slower, more accurate)
clawvault vsearch "what did we decide about the database"
```

## Context Death Resilience

### Wake (start of session)

```bash
clawvault wake
```

### Sleep (end of session)

```bash
clawvault sleep "what I was working on" --next "finish docs" --blocked "waiting for review"
```

### Checkpoint (save state frequently)

```bash
clawvault checkpoint --working-on "PR review" --focus "type guards" --blocked "waiting for CI"
```

### Recover (manual check)

```bash
clawvault recover --clear
# Shows: death time, last checkpoint, recent handoff
```

### Handoff (manual session end)

```bash
clawvault handoff \
  --working-on "ClawVault improvements" \
  --blocked "npm token" \
  --next "publish to npm, create skill" \
  --feeling "productive"
```

### Recap (bootstrap new session)

```bash
clawvault recap
# Shows: recent handoffs, active projects, pending commitments, lessons
```

## Auto-linking

Wiki-link entity mentions in markdown files:

```bash
# Link all files
clawvault link --all

# Link single file
clawvault link memory/2024-01-15.md
```

## Folder Structure

```
vault/
├── .clawvault/           # Internal state
│   ├── last-checkpoint.json
│   └── dirty-death.flag
├── decisions/            # Key choices with reasoning
├── lessons/              # Insights and patterns
├── people/               # One file per person
├── projects/             # Active work tracking
├── handoffs/             # Session continuity
├── inbox/                # Quick captures
└── templates/            # Document templates
```

## Best Practices

1. **Wake at session start** — `clawvault wake` restores context
2. **Checkpoint every 10-15 min** during heavy work
3. **Sleep before session end** — `clawvault sleep` captures next steps
4. **Use types** — knowing WHAT you're storing helps WHERE to put it
5. **Wiki-link liberally** — `[[person-name]]` builds your knowledge graph

## Checklist for AGENTS.md

```markdown
## Memory Checklist
- [ ] Run `clawvault wake` at session start
- [ ] Checkpoint during heavy work
- [ ] Capture key decisions/lessons with `clawvault remember`
- [ ] Use wiki-links like `[[person-name]]`
- [ ] End with `clawvault sleep "..." --next "..." --blocked "..."`
- [ ] Run `clawvault doctor` when something feels off
```

## Session Transcript Repair (v1.5.0+)

When the Anthropic API rejects with "unexpected tool_use_id found in tool_result blocks", use:

```bash
# See what's wrong (dry-run)
clawvault repair-session --dry-run

# Fix it
clawvault repair-session

# Repair a specific session
clawvault repair-session --session <id> --agent <agent-id>

# List available sessions
clawvault repair-session --list
```

**What it fixes:**
- Orphaned `tool_result` blocks referencing non-existent `tool_use` IDs
- Aborted tool calls with partial JSON
- Broken parent chain references

Backups are created automatically (use `--no-backup` to skip).

## Troubleshooting

- **qmd not installed** — run `bun install -g github:tobi/qmd` or `npm install -g qmd`
- **No ClawVault found** — run `clawvault init` or set `CLAWVAULT_PATH`
- **CLAWVAULT_PATH missing** — run `clawvault shell-init` and add to shell rc
- **Too many orphan links** — run `clawvault link --orphans`
- **Inbox backlog warning** — process or archive inbox items
- **"unexpected tool_use_id" error** — run `clawvault repair-session`

## Integration with qmd

ClawVault uses [qmd](https://github.com/tobi/qmd) for search:

```bash
# Install qmd
bun install -g github:tobi/qmd

# Add vault as collection
qmd collection add /path/to/vault --name my-memory --mask "**/*.md"

# Update index
qmd update && qmd embed
```

## Environment Variables

- `CLAWVAULT_PATH` — Default vault path (skips auto-discovery)
- `OPENCLAW_HOME` — OpenClaw home directory (used by repair-session)
- `OPENCLAW_STATE_DIR` — OpenClaw state directory (used by repair-session)
- `GEMINI_API_KEY` — Used by `observe` for LLM-powered compression (optional)

## Architecture: ClawVault + qmd

ClawVault and qmd serve complementary roles:

- **ClawVault** handles structured memory: storing, categorizing, routing observations, session continuity (wake/sleep/checkpoint), and entity linking. It writes markdown files organized by category.
- **qmd** handles search: BM25 keyword search, vector embeddings for semantic search, and reranker for accuracy. It indexes the markdown files ClawVault produces.

Together: ClawVault writes → qmd indexes → you search with `qmd query` (BM25 + vectors + neural reranker for best accuracy).

### OpenClaw Config Recommendation

```yaml
memory:
  backend: "qmd"
  vault: "${CLAWVAULT_PATH}"
```

The default `qmd query` pipeline uses BM25 keyword matching, vector embeddings, and a neural reranker for the most accurate results.

### Low-Memory Environments

The neural reranker requires ~8GB+ RAM. On constrained machines (e.g., small VPS, WSL2 with limited memory), `qmd query` may OOM. You can set `qmd.command` in your OpenClaw config to a wrapper script that routes to `qmd vsearch` (vectors only, no reranker) instead. This is a host-specific workaround, not the recommended default.

## Links

- npm: https://www.npmjs.com/package/clawvault
- GitHub: https://github.com/Versatly/clawvault
- Issues: https://github.com/Versatly/clawvault/issues
