---
name: openclaw-mem
version: 1.2.0
description: "Keep your agent fast and smart. Auto-journals history to keep the context window clean and efficient."
---

# OpenClaw Memory Librarian

A background librarian that turns messy daily logs into concise knowledge, saving tokens while preserving important context.

> ⚠️ **CRITICAL REQUIREMENT**
>
> You **MUST** enable session memory in your OpenClaw configuration for this skill to work.

## Enable Session Memory

**CLI**
```bash
clawdbot config set agents.defaults.memorySearch.experimental.sessionMemory true
```

**JSON (`~/.openclaw/openclaw.json`)**
```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "experimental": {
          "sessionMemory": true
        }
      }
    }
  }
}
```

> Without this, the agent cannot access past session context to generate summaries.

---

## Workflow

1. **Read** recent daily logs (`memory/YYYY-MM-DD.md`)
2. **Summarize** valuable information into a monthly journal (`memory/journal/YYYY-MM.md`)
3. **Prune** raw logs older than 14 days

---

## Journaling Strategy

When summarizing logs, do **NOT** copy the chat. Extract the **signal**.

### Journal Structure (`memory/journal/YYYY-MM.md`)

```markdown
## YYYY-MM-DD Summary

### 🧠 Decisions
- [Decision]

### 🛠️ Changes
- Installed: [Tool/Skill]
- Configured: [Setting]
- Refactored: [File]

### 🚫 Blockers & Errors
- [Problem] → [Solution]

### 💡 Insights
- [Lesson learned]
- [User preference discovered]
```

> ### 🧹 Noise Filter Rules
>
> **IGNORE**
> - Greetings, confirmations
> - Short-lived errors fixed immediately
>
> **KEEP**
> - Final outcomes
> - Architectural decisions
> - New capabilities
> - Security-relevant changes
>
> **LINK**
> - Always link relevant files (e.g. `skills/openclaw-mem/SKILL.md`)

---

## Retention Policy (The Pruner)

After journaling is complete and verified:

> - Identify `memory/YYYY-MM-DD.md` files older than 14 days
> - **DELETE** them to free context space
> - Safety check: ensure the date is actually >14 days in the past

---

## Automation & Best Practices

### Recommended Cron Schedule

Run daily (e.g. at **04:30 AM**) to keep memory clean automatically.

```json
{
  "name": "Daily Memory Librarian",
  "schedule": { "kind": "cron", "expr": "30 4 * * *", "tz": "Europe/Berlin" },
  "payload": {
    "kind": "agentTurn",
    "message": "Run openclaw-mem to organize daily logs into the monthly journal and prune old raw files."
  },
  "sessionTarget": "isolated"
}
```

---

## Daily Reset Workflow

The librarian runs in an **isolated background session**.

**Best Practice**
1. Librarian runs at night (cleans files on disk)
2. You type `/reset` in the morning
   - Clears RAM context
   - Reloads compact journal instead of raw logs
   - Result: fresh context, low token usage, full long-term memory

---

## Usage

**Run full cycle**
```
Run openclaw-mem to organize my logs.
```

**Summarize only (no delete)**
```
Run openclaw-mem but keep the raw files.
```
