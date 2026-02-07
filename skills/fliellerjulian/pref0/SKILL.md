---
name: pref0
description: Learn user preferences from conversations and personalize responses automatically. Preferences compound over time — corrections like "use TypeScript, not JavaScript" are captured and injected into future sessions.
version: 1.0.0
user-invocable: true
metadata: {"openclaw":{"requires":{"env":["PREF0_API_KEY"]},"primaryEnv":"PREF0_API_KEY"}}
---

# pref0 — Preference Learning for AI Agents

You have access to the pref0 API. It learns user preferences from conversations and serves them back at inference time. The more conversations you track, the better it gets.

## When to use this skill

### After a conversation ends → Track it

After finishing a conversation (or at natural breakpoints), send the messages to pref0 so it can extract preferences. This is especially valuable when the user **corrects** you (e.g., "use pnpm, not npm") or states explicit preferences (e.g., "always use metric units").

### Before responding to a user → Fetch their preferences

Before generating a response, fetch the user's learned preferences and follow them. This prevents the user from having to repeat themselves across sessions.

## API Reference

**Base URL:** `https://api.pref0.com`
**Auth:** `Authorization: Bearer $PREF0_API_KEY`

### Track a conversation (POST /v1/track)

Send a conversation so pref0 can learn from it. It extracts corrections, explicit preferences, and behavioral patterns automatically.

```bash
curl -X POST https://api.pref0.com/v1/track \
  -H "Authorization: Bearer $PREF0_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "<user-id>",
    "messages": [
      { "role": "user", "content": "Help me set up a new project" },
      { "role": "assistant", "content": "Here is a project using npm and JavaScript..." },
      { "role": "user", "content": "Use pnpm, not npm. And TypeScript." },
      { "role": "assistant", "content": "Updated to pnpm and TypeScript..." }
    ]
  }'
```

**Response:**
```json
{
  "preferencesExtracted": 2,
  "patternsExtracted": 1
}
```

### Get learned preferences (GET /v1/profiles/:userId)

Retrieve the user's learned preference profile. Use `?minConfidence=0.5` to only get well-learned preferences suitable for system prompt injection.

```bash
curl https://api.pref0.com/v1/profiles/<user-id>?minConfidence=0.5 \
  -H "Authorization: Bearer $PREF0_API_KEY"
```

**Response:**
```json
{
  "userId": "user_abc123",
  "preferences": [
    {
      "key": "language",
      "value": "typescript",
      "confidence": 0.85,
      "evidence": "User said: Use TypeScript, not JavaScript",
      "firstSeen": "2026-01-15T10:00:00.000Z",
      "lastSeen": "2026-02-05T14:30:00.000Z"
    },
    {
      "key": "package_manager",
      "value": "pnpm",
      "confidence": 0.85,
      "evidence": "User said: use pnpm instead of npm",
      "firstSeen": "2026-01-15T10:00:00.000Z",
      "lastSeen": "2026-02-03T09:15:00.000Z"
    },
    {
      "key": "css_framework",
      "value": "tailwind",
      "confidence": 0.70,
      "evidence": "User said: Use Tailwind, not Bootstrap",
      "firstSeen": "2026-01-20T16:45:00.000Z",
      "lastSeen": "2026-01-20T16:45:00.000Z"
    }
  ],
  "patterns": [
    { "pattern": "prefers explicit tooling choices over defaults", "confidence": 0.60 }
  ]
}
```

Each preference includes `evidence` (the quote that triggered extraction), `firstSeen` (when first learned), and `lastSeen` (when last reinforced).

### Get system prompt string (GET /v1/profiles/:userId/prompt)

Get a ready-to-use string for system prompt injection. No JSON parsing needed — just fetch and append. Defaults to `?minConfidence=0.5`.

```bash
curl https://api.pref0.com/v1/profiles/<user-id>/prompt \
  -H "Authorization: Bearer $PREF0_API_KEY"
```

**Response:**
```json
{
  "userId": "user_abc123",
  "prompt": "The following preferences have been learned from this user's previous conversations. Follow them unless explicitly told otherwise:\n- language: typescript\n- package_manager: pnpm\n- css_framework: tailwind\n\nBehavioral patterns observed:\n- prefers explicit tooling choices over defaults"
}
```

Returns `{"prompt": ""}` if no preferences meet the confidence threshold.

### Delete a user profile (DELETE /v1/profiles/:userId)

Reset a user's learned preferences. Use for preference resets or data deletion requests.

```bash
curl -X DELETE https://api.pref0.com/v1/profiles/<user-id> \
  -H "Authorization: Bearer $PREF0_API_KEY"
```

Returns `204 No Content`.

## How to integrate into your workflow

1. **Identify the user.** Use a stable user ID (email, account ID, phone number — whatever you have).

2. **At the start of a session**, fetch preferences:
   - **Simplest:** Call `GET /v1/profiles/{userId}/prompt` and append the returned `prompt` string to your system prompt. Done.
   - **More control:** Call `GET /v1/profiles/{userId}?minConfidence=0.5` to get the full JSON with confidence scores, evidence, and timestamps per preference.

3. **At the end of a session**, track the conversation:
   - Call `POST /v1/track` with the full message history
   - pref0 handles extraction and confidence scoring automatically

4. **Preferences compound over time.** Corrections start at 0.70 confidence, implied preferences at 0.40. Each repeated signal adds +0.15, capped at 1.0.

## Confidence guide

| Signal type        | Starting confidence | Example                           |
|--------------------|--------------------:|-----------------------------------|
| Explicit correction | 0.70               | "Use Tailwind, not Bootstrap"     |
| Implied preference  | 0.40               | "Deploy it to Vercel"             |
| Behavioral pattern  | 0.30               | User consistently wants short replies |
| Each repeat         | +0.15              | Same preference across sessions   |

## Setup

1. Sign up at [pref0.com](https://pref0.com/signup)
2. Create an API key in the dashboard
3. Set the `PREF0_API_KEY` environment variable
4. First 100 requests/month are free, then $5 per 1,000 requests
