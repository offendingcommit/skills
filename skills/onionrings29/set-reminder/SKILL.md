---
name: set-reminder
description: Create reminders that deliver to user's configured channels (iMessage, Discord, etc). Use when user wants to be reminded about something at a specific time or on a recurring schedule. Executes scripts/set_reminder.py with validated parameters.
---

# Set Reminder

Creates cron-based reminders with input validation and error handling.

## Usage

Run the script with one time option and a message:

```bash
scripts/set_reminder.py --at <when> --message "<text>" [--channel <name>]
scripts/set_reminder.py --every <duration> --message "<text>" [--channel <name>]
scripts/set_reminder.py --cron "<expr>" --message "<text>" [--channel <name>]
```

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--at` | One of three | One-shot: ISO datetime or relative (`+20m`, `+1h`, `+2d`) |
| `--every` | One of three | Recurring interval: `30m`, `2h`, `1d` |
| `--cron` | One of three | 5-field cron expression: `"0 9 * * *"` |
| `--message` | Yes | Reminder text |
| `--channel` | No | Channel name from config (uses default if omitted) |

**Time format rules:**
- `--at` relative: `+<number><unit>` where unit is `s`, `m`, `h`, or `d` (e.g., `+30s`, `+20m`, `+1h`, `+2d`)
- `--at` absolute: ISO 8601 format `2025-02-01T14:00:00` or with timezone `2025-02-01T14:00:00Z`
- `--every`: `<number><unit>` where unit is `s`, `m`, `h`, or `d` (e.g., `30m`, `2h`, `1d`)
- `--cron`: 5 fields (minute hour day-of-month month day-of-week)

## Examples

```bash
# Remind in 20 minutes (default channel)
scripts/set_reminder.py --at "+20m" --message "Take medicine"

# Remind at specific time
scripts/set_reminder.py --at "2025-02-01T14:00:00" --message "Meeting starts"

# Recurring every 2 hours
scripts/set_reminder.py --every "2h" --message "Drink water"

# Daily at 9 AM
scripts/set_reminder.py --cron "0 9 * * *" --message "Daily standup"

# Specific channel
scripts/set_reminder.py --at "+1h" --message "Check Discord" --channel discord
```

## Script Output

**On success:**
```
SUCCESS: Reminder created
Job ID: abc123
Channel: imessage
Message: Reminder: Take medicine
Next fire: 00:00:20 (In 20 minutes)
```

**On error:**
```
ERROR: Time '2024-01-01T00:00:00' is more than 27 hours in the past. Please use a future time.
```

## Validation

The script validates:
1. Exactly one time option provided
2. Time format is correct
3. Absolute times are not more than 27 hours in the past
4. Channel exists in config (lists available channels if not)

## Config Structure

`config.json` defines available channels and timezone:

```json
{
  "default": "imessage",
  "timezone": "America/Los_Angeles",
  "channels": {
    "imessage": "+1234567890",
    "discord": "user:123456789",
    "telegram": "-1001234567890"
  }
}
```

**Required fields:**
- `default`: Default channel name
- `timezone`: IANA timezone (e.g., "America/Los_Angeles", "UTC", "Europe/London")
- `channels`: Object mapping channel names to destinations

To add a channel, edit `config.json` and add a key-value pair under `channels`.
