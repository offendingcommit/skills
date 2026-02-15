---
name: codecast
description: Stream coding agent sessions (Claude Code, Codex, Gemini CLI, etc.) to a Discord channel in real-time via webhook. Use when invoking coding agents and wanting transparent, observable dev sessions — no black box. Parses Claude Code's stream-json output into clean formatted Discord messages showing tool calls, file writes, bash commands, and results with zero AI token burn. Use when asked to "stream to Discord", "relay agent output", or "make dev sessions visible".
metadata: {"openclaw":{"emoji":"🎬","requires":{"anyBins":["unbuffer","python3"]}}}
---

# Codecast

Live-stream coding agent sessions to Discord. Zero AI tokens burned.

## Setup

First-time setup: see [references/setup.md](references/setup.md) for webhook creation, unbuffer install, bot token, and smoke test.

## Invocation

**⚠️ Always use `nohup` from OpenClaw — `exec background:true` kills long sessions after ~15-20s.**

### From OpenClaw (recommended)

```bash
exec command:"nohup {baseDir}/scripts/dev-relay.sh -w ~/projects/myapp -- claude -p --dangerously-skip-permissions --output-format stream-json --verbose 'Your task here. When finished, run: openclaw system event --text \"Done: summary\" --mode now' > /tmp/codecast.log 2>&1 & echo PID:\$!"
```

### Direct

```bash
bash {baseDir}/scripts/dev-relay.sh -w ~/projects/myapp -- claude -p --dangerously-skip-permissions --output-format stream-json --verbose 'Your task'
```

### Options

| Flag | Description | Default |
|------|------------|---------|
| `-w <dir>` | Working directory | Current dir |
| `-t <sec>` | Timeout | 1800 |
| `-h <sec>` | Hang threshold | 120 |
| `-n <name>` | Agent display name | Auto-detected |
| `-r <n>` | Rate limit (posts/60s) | 25 |
| `--thread` | Post into a Discord thread | Off |
| `--skip-reads` | Hide Read tool events | Off |
| `--review <url>` | PR review mode | — |
| `--parallel <file>` | Parallel tasks mode | — |
| `--resume <dir>` | Replay session | — |

For PR review, parallel tasks, Discord bridge, and Codex structured output: see [references/advanced-modes.md](references/advanced-modes.md).

## Agent Launch Checklist (MANDATORY)

Every time an OpenClaw agent launches a codecast session, do ALL of these:

1. **Start nohup session** → note PID from output
2. **Post to dev channel** → announce agent name, workdir, task
3. **Create a watcher cron job** to detect completion and report back:
   ```
   cron add → every 120000ms → isolated agentTurn →
   "Run: bash {baseDir}/scripts/codecast-watch.sh <PID> <relay-dir>
   If output is STILL_RUNNING → reply HEARTBEAT_OK
   If output starts with ✅ or ❌ or ⚠️ → post the output to <invoking-channel-id>,
   then delete this cron job (cron remove <this-job-id>)"
   ```
4. **Log to daily memory** → PID, relay dir, invoking channel, cron job ID

The relay dir is printed at launch: `📂 Relay: /tmp/dev-relay.XXXXXX`.

**Why the cron job is mandatory:** `openclaw system event` only queues for the main session heartbeat — it does NOT wake the active chat session. The cron job is the only reliable way to get notified in the channel that launched the codecast.

## Prompt Template

Always append completion notification to the inner agent's prompt:

```
<your task>

When completely finished, run: openclaw system event --text "Done: <brief summary>" --mode now
```

## Agent Support

| Agent | Output Mode | Status |
|-------|------------|--------|
| Claude Code | stream-json | Full support |
| Codex | --json JSONL | Full support |
| Any CLI | Raw ANSI | Basic support |

## Session Tracking

- **Active sessions:** `/tmp/dev-relay-sessions/<PID>.json` (auto-removed on end)
- **Event logs:** `/tmp/dev-relay.XXXXXX/stream.jsonl` (7-day auto-cleanup)
- **Interactive input:** `process:submit sessionId:<id> data:"message"`

## Reference Docs

- [Setup guide](references/setup.md) — first-time install, webhook, bot token
- [Advanced modes](references/advanced-modes.md) — PR review, parallel tasks, Discord bridge, Codex
- [Discord output](references/discord-output.md) — message formats, architecture, env vars, troubleshooting
