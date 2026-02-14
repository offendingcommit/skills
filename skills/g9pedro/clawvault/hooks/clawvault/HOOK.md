---
name: clawvault
description: "Context death resilience — auto-checkpoint on /new, recovery detection on startup"
metadata:
  openclaw:
    emoji: "🐘"
    events: ["gateway:startup", "command:new"]
    requires:
      bins: ["clawvault"]
---

# ClawVault Hook

Integrates ClawVault's context death resilience into OpenClaw.

## Active Events

| Event | Action |
|-------|--------|
| `gateway:startup` | Checks for context death via `clawvault recover --clear`, injects alert if detected |
| `command:new` | Auto-checkpoints before session reset via `clawvault checkpoint` |

## Forward-Compatible Events

The handler also includes a `session:start` handler that will activate when OpenClaw ships `session:start` event support (currently listed as a future event in OpenClaw docs). When active, it will:

1. Extract the initial user prompt
2. Run `clawvault context "<prompt>" --format json --profile auto`
3. Inject up to 4 relevant context snippets + session recap into the session

## Installation

```bash
npm install -g clawvault
openclaw hooks enable clawvault
```

## Requirements

- ClawVault CLI installed globally (`clawvault` on PATH)
- Vault initialized (`clawvault init` or `CLAWVAULT_PATH` set)

## What It Does

### Gateway Startup

1. Runs `clawvault recover --clear` against the discovered vault
2. If context death detected → injects warning message into first agent turn
3. Clears dirty death flag for clean session start

### Command: /new

1. Creates automatic checkpoint with session key and source info
2. Captures state even if the agent forgot to run `clawvault sleep`
3. Ensures continuity across session resets

### Event Compatibility

The hook normalizes event names across separators (`.`, `:`, `/`) and checks alias payload shapes (`event`, `eventName`, `name`, `hook`, `trigger`) for robustness across OpenClaw versions.

## Vault Discovery

Auto-detects vault path via:
1. `CLAWVAULT_PATH` environment variable
2. Walking up from cwd to find `.clawvault.json`
3. Checking `memory/` subdirectory at each level (OpenClaw convention)

## Security

- Uses `execFileSync` (no shell) to prevent command injection
- All arguments passed as array, never interpolated
- Input sanitization on session keys, prompts, and display strings
- 15-second timeout on all CLI calls
