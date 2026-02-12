# Meetup Planner Bootstrap (one-time setup)

Run this setup **once** after installing the skill. The agent will check `.openclaw/workspace/memory/meetup-planner.json` to see if bootstrap is complete.

---

## 1) Check for search and crawling capabilities

**Before anything else**, check if you have the necessary capabilities to search the web and scrape event pages.

### Check for web search capability

Try to determine if you have access to web search functionality:
- Check if you have WebSearch tool available
- Check if Brave Search skill is installed: `ls ~/.openclaw/skills/brave-search* 2>/dev/null`
- Check if any other search tool/skill is available

### Check for web crawling/scraping capability

Try to determine if you have access to web crawling functionality:
- Check if you have WebFetch tool available
- Check if Firecrawl skill is installed: `ls ~/.openclaw/skills/firecrawl* 2>/dev/null`
- Check if any other crawling tool/skill is available

### If capabilities are missing

If you don't have adequate search or crawling capabilities, inform the human:

```
⚠️ I need web search and crawling capabilities to find events for you.

I recommend installing:
- Brave Search skill (for searching the web)
- Firecrawl skill (for extracting event details from pages)

Would you like me to help you install these, or would you prefer to configure different tools?
```

Wait for human response before proceeding.

**If they want to install suggested tools**, provide installation instructions:
```bash
# Install Brave Search skill
npx clawhub@1.x install brave-search@1

# Install Firecrawl skill
npx skills@1.x add firecrawl/cli@1
```

**Note**: These tools may require API keys. The human will need to configure those separately according to each tool's documentation.

---

## 2) Collect user preferences

Once you have confirmed search and crawling capabilities are available, ask the human these questions **one at a time** in a friendly, conversational way:

1. **Event types**: What types of events are you interested in?
   *(Examples: tech meetups, networking, conferences, workshops, hackathons)*

2. **Topics**: What topics excite you?
   *(Examples: AI/ML, web development, blockchain, entrepreneurship, design, data science)*

3. **Location**: What's your location or preferred event locations?
   *(Examples: "San Francisco", "Berlin", "remote" for virtual)*

4. **Format preference**: Do you prefer in-person, virtual, or hybrid events?

5. **Schedule**: What days/times work best for you?
   *(Examples: weekday evenings, weekends, any)*

6. **Time commitment**: What time commitment are you looking for?
   *(Examples: 1-2 hours, half-day, full-day, multi-day)*

7. **Organizations** (optional): Any specific organizations or communities you follow?

8. **Requirements**: Any deal-breakers or must-haves?
   *(Examples: free events only, small groups, beginner-friendly)*

---

## 3) Create preferences file

Save all responses to `.openclaw/workspace/memory/meetup-planner.json`:

```json
{
  "bootstrapComplete": true,
  "bootstrapVersion": "1.0.0",
  "lastSetupAt": "2026-02-12T19:00:00Z",
  "capabilities": {
    "webSearch": "brave-search|websearch|other",
    "webCrawl": "firecrawl|webfetch|other"
  },
  "preferences": {
    "eventTypes": ["tech meetups", "workshops"],
    "topics": ["AI/ML", "web development"],
    "location": "San Francisco",
    "formatPreference": "in-person",
    "schedule": "weekday evenings",
    "timeCommitment": "1-2 hours",
    "organizations": [],
    "requirements": ["beginner-friendly"]
  },
  "searchSchedule": {
    "enabled": true,
    "frequency": "daily",
    "time": "08:00",
    "timezone": "America/Los_Angeles"
  },
  "lastSearchAt": null,
  "lastHeartbeatAt": null
}
```

**Contract (schema):**
- Required fields: `bootstrapComplete`, `bootstrapVersion`, `capabilities`, `preferences`
- Optional fields: `lastSearchAt`, `lastHeartbeatAt`, `searchSchedule`

---

## 4) Create workspace directories

Ensure workspace structure exists:

```bash
# Create main workspace directory
mkdir -p ~/.openclaw/workspace/memory

# Create event data directory
mkdir -p ~/.openclaw/workspace/meetup-planner/{events,backups}

# Set proper permissions (owner only)
chmod 700 ~/.openclaw/workspace/meetup-planner
chmod 600 ~/.openclaw/workspace/memory/meetup-planner.json
```

Initialize empty data files:

```bash
# Events database
echo '{"events":[],"lastUpdated":null}' > ~/.openclaw/workspace/meetup-planner/events/events.json

# Reminders
echo '{"reminders":[]}' > ~/.openclaw/workspace/meetup-planner/events/reminders.json
```

---

## 5) Set up daily search automation (optional)

Ask the human in a friendly, conversational way:

1. **"Would you like me to automatically search for new events every day?"**
   - If no: Update `searchSchedule.enabled` to `false` and skip to step 6
   - If yes: Continue with the questions below

2. **"Great! What time would you like me to search for events each day?"**
   - Examples: "8:00 AM", "morning", "evening"
   - Default: 8:00 AM
   - Store in `searchSchedule.time`

3. **"What timezone are you in?"**
   - Examples: "America/Los_Angeles", "Europe/Berlin", "Asia/Tokyo"
   - Default: use system timezone
   - Store in `searchSchedule.timezone`

4. **"At what time would you like me to inform you about new events that might interest you?"**
   - This should be when they check their notifications/messages
   - Could be same as search time or different
   - Examples: "Right when you find them", "At 9 AM", "In the evening"

Update the `searchSchedule` section in `.openclaw/workspace/memory/meetup-planner.json` with their answers.

### Create cron job

```bash
# Create cron job for daily searches (adjust time based on human's preference)
(crontab -l 2>/dev/null; echo "0 8 * * * cd ~/.openclaw/workspace && echo 'run meetup-planner search' | claude-cli") | crontab -
```

**Note**: Adjust the cron syntax (the "0 8" part) based on their preferred time and timezone.

### Confirm to human

Tell them in a friendly way:
```
✅ Perfect! I've set up daily automated searches for you.

Here's what will happen:
• I'll search for new events every day at [TIME] [TIMEZONE]
• I'll let you know about events that match your interests at [NOTIFICATION_TIME]
• You can pause searches anytime by saying "pause search"
• You can resume them with "resume search"
• You can change the schedule anytime with "update preferences"
```

---

## 6) Confirmation & first search

After all steps complete, tell the human in a friendly, excited way:

```
🎉 All set! Meetup Planner is ready to go!

Here's what I've set up for you:
• Search capability: [tool name] ✓
• Crawling capability: [tool name] ✓
• Your preferences: saved ✓
• Daily searches: [enabled/disabled] ✓

[If enabled] I'll search for new events every day at [TIME] [TIMEZONE] and let you know about interesting matches at [NOTIFICATION_TIME].

[If disabled] Just let me know when you want me to search for events by saying "search now".

Want to see what I can find for you right now? I can run a search immediately to show you events matching your interests!
```

**Wait for their response:**
- If they say yes: Run Phase 2 (Daily Search Routine) from SKILL.md
- If they say no: "No problem! I'll be ready whenever you need me. Just say 'search now' anytime!"

**Important**: Set `bootstrapComplete: true` in the JSON file before ending this conversation.

---

## Idempotency (important!)

**Before starting bootstrap:**
1. Check if `.openclaw/workspace/memory/meetup-planner.json` exists
2. Check if `bootstrapComplete: true` is set
3. If already complete, ask human: "Meetup Planner is already set up. Would you like to:
   - Update your preferences
   - Run a search now
   - Skip (nothing to do)"

**Don't redo setup if already complete** unless human explicitly asks to reconfigure.

---

## Troubleshooting

**Search/crawl tools not available:**
- Provide installation instructions for recommended tools
- Or ask human what alternative tools they'd like to use

**Cron setup fails:**
- Provide manual cron configuration instructions
- Offer alternative: "I can search manually when you ask me to"

**Permissions errors:**
- Check file permissions with `ls -la`
- Fix with `chmod 600` or `chmod 700`

---

**Bootstrap version**: 1.0.0
**Last updated**: 2026-02-12
