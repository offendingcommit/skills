---
name: agentic-compass
description: Local-only self-reflection that forces an agentic plan (proactive task, deferred cron candidate, avoidance rule, ship action).
version: 0.1.0
metadata: {"openclaw":{"emoji":"🧭","requires":{"bins":["python3"]}}}
---

# Agentic Compass 🧭

**Local-only.** This skill reads your local memory files and turns reflection into **decisions + action**. It does **not** send data anywhere.

## What it does
- Scores agentic behavior across 5 axes (daily log weighted 3x)
- Generates a short **Agentic Plan** for the next 12 hours:
  - **Proactive task**
  - **Deferred task** (cron candidate)
  - **Avoidance rule** (stop a wasteful habit)
  - **Ship action** (micro-deliverable)

## Usage

```bash
# Generate plan and print to stdout
agentic-compass

# Write plan to memory/agentic-compass.md
agentic-compass --write

# Use custom memory paths
agentic-compass --daily /path/to/memory/2026-01-31.md --long /path/to/MEMORY.md
```

## Output format (example)
```
Score: 3.4/5
Weakest axis: Completion
Plan:
- Proactive: update digest site with latest run
- Deferred: retry Moltbook feedback check in 60m (cron)
- Avoidance: stop scanning every 10m unless new lead
- Ship: draft 1 short post idea for Moltbook
```

## Rules (Local-only)
- Reads **only** local files
- Writes **only** local files
- No network calls

## Script
`/scripts/agentic-compass.py`

## Tip
Run it during heartbeat or before compaction to keep momentum.
