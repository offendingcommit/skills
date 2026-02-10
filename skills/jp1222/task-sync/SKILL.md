---
name: task-sync
description: Bidirectional sync between TickTick and Google Tasks. Use when the user wants to sync tasks, lists, or completion status between TickTick (Dida) and Google Tasks, set up automated task synchronization, or manage smart lists (Today, Next 7 Days, All) from TickTick in Google Tasks.
---

# Task Sync

Bidirectional sync between TickTick and Google Tasks with smart list support.

## What It Does

- Syncs Google Task Lists <-> TickTick Projects (bidirectional, matched by name)
- Syncs tasks bidirectionally: titles, completion status, notes/content
- Maps TickTick priorities to Google title prefixes (`[★]` high, `[!]` medium)
- Pushes TickTick smart lists (Today, Next 7 Days, All) one-way to Google Tasks
- Prevents Google Calendar duplicates via date strategy: dates forwarded to TickTick then cleared from Google; only the "All" smart list retains dates

## Running

```bash
python sync.py
```

## Setup Requirements

1. Python 3.10+ with: `google-auth google-auth-oauthlib google-api-python-client requests`
2. Google Cloud project with Tasks API enabled — run `python scripts/setup_google_tasks.py`
3. TickTick developer app from developer.ticktick.com — run `python scripts/setup_ticktick.py`
4. Edit `config.json` with token paths

## Automation

```bash
# Cron: every 10 minutes
*/10 * * * * /path/to/python /path/to/sync.py >> /path/to/sync.log 2>&1
```

Or use OpenClaw's built-in cron system.

## Files

| File | Purpose |
|------|---------|
| `sync.py` | Main sync orchestrator |
| `utils/google_api.py` | Google Tasks API wrapper |
| `utils/ticktick_api.py` | TickTick Open API wrapper |
| `scripts/setup_google_tasks.py` | Google OAuth setup |
| `scripts/setup_ticktick.py` | TickTick OAuth setup |
| `config.json` | Configuration |
| `e2e_test.py` | 15 end-to-end tests |
