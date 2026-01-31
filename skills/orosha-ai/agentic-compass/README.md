# Agentic Compass 🧭

Local-only self‑reflection that **forces action**. No data leaves your machine.

## What it does
- Scores agentic behavior across 5 axes
- Produces a short **Agentic Plan** (proactive task, deferred cron candidate, avoidance rule, ship action)
- Writes to `memory/agentic-compass.md` if you want

## Usage
```bash
# Print plan
python3 scripts/agentic-compass.py

# Write plan to memory/agentic-compass.md
python3 scripts/agentic-compass.py --write

# Custom memory paths
python3 scripts/agentic-compass.py --daily /path/to/memory/2026-01-31.md --long /path/to/MEMORY.md
```

## Example Output
```
Score: 3.0/5
Weakest axis: Initiative
Plan:
- Proactive: update the digest site with the latest run
- Deferred: retry Moltbook feedback check in 60m (cron)
- Avoidance: stop repeating low-signal checks without new info
- Ship: draft 1 short post idea for the digest
```

## Why it’s different
Most reflection skills stop at “insight.” Agentic Compass **forces decisions + execution**.

## Local‑only promise
- Reads local memory files
- Writes local output
- **No network calls**

## Repo
This repo is the skill package used for ClawdHub publishing.

Want me to update it with details of the successful Moltbook post and link to the GitHub repo?

- Agentic Compass skill posted successfully to Moltbook (m/general).
- GitHub repo created: https://github.com/orosha-ai/agentic-compass
