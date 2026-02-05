---
name: Praesidia
description: Verify AI agents, check trust scores (0-100), fetch A2A agent cards, discover marketplace agents. Use when user mentions agent verification, trust scores, agent discovery, A2A protocol, agent identity, agent marketplace, or asks "is this agent safe?" or "find agents that can [task]".
metadata: {"openclaw":{"requires":{"env":["PRAESIDIA_API_KEY"]},"primaryEnv":"PRAESIDIA_API_KEY","homepage":"https://praesidia.ai","emoji":"🛡️"}}
---

# Praesidia Agent Identity & Verification

Verify AI agents, check trust scores (0-100), and discover marketplace agents via Praesidia's identity layer.

## Core Capabilities

- **Verify agents** - Check if an agent is registered, verified, and trustworthy
- **Trust scores** - View 0-100 trust ratings and verification status
- **Agent discovery** - Search marketplace for public agents by capability
- **A2A protocol** - Fetch standard Agent-to-Agent protocol cards

## Prerequisites

1. Praesidia account: https://praesidia.ai
2. API key from Settings → API Keys
3. Configure in `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "praesidia": {
        "apiKey": "pk_live_your_key_here",
        "env": {
          "PRAESIDIA_API_URL": "https://api.praesidia.ai"
        }
      }
    }
  }
}
```

For local development, use `http://localhost:3000` as the URL.

---

## Quick Reference

### Verify an Agent

**User says:** "Is agent chatbot-v2 safe?" / "Verify agent chatbot-v2"

**Your action:**
```javascript
web_fetch({
  url: "${PRAESIDIA_API_URL}/agents/chatbot-v2/agent-card",
  headers: {
    "Authorization": "Bearer ${PRAESIDIA_API_KEY}",
    "Accept": "application/json"
  }
})
```

**Present to user:**
- ✅ Agent name & description
- 🛡️ **Trust score (0-100)** and trust level
- ✓ Verification status (verified date)
- 🔧 Capabilities (what the agent can do)
- 📜 Compliance (SOC2, GDPR, etc.)
- 🔗 Agent card URL

**Example output:**
```
✅ ChatBot V2 is verified and safe to use!

Trust Score: 92.5/100 (VERIFIED)
Status: ACTIVE
Capabilities: message:send, task:create, data:analyze
Compliance: SOC2, GDPR
Last verified: 2 days ago

Agent card: https://api.praesidia.ai/agents/chatbot-v2/agent-card
```

---

### Discover Public Agents

**User says:** "Find public data analysis agents" / "Show me chatbot agents"

**Your action:**
```javascript
web_fetch({
  url: "${PRAESIDIA_API_URL}/agents/discovery?visibility=PUBLIC&search=data",
  headers: { "Accept": "application/json" }
  // Authorization optional for public agents (includes it for more results)
})
```

**Filters available:**
- `?visibility=PUBLIC` - public marketplace agents
- `?role=SERVER` - agents that provide services
- `?role=CLIENT` - agents that consume services
- `?status=ACTIVE` - only active agents
- `?search=keyword` - search by name/description

**Present to user:**
- List of matching agents with:
  - Name, description, agent ID
  - Trust score and level
  - Role (SERVER/CLIENT)
  - Key capabilities
  - Link to full card

**Example output:**
```
Found 2 public data analysis agents:

1. OpenData Analyzer (VERIFIED - 88.0/100)
   - Capabilities: data:analyze, chart:generate, report:create
   - Role: SERVER | Status: ACTIVE
   - Card: https://api.praesidia.ai/agents/opendata-1/agent-card

2. CSV Processor (STANDARD - 70.0/100)
   - Capabilities: file:parse, data:transform, export:json
   - Role: SERVER | Status: ACTIVE
   - Card: https://api.praesidia.ai/agents/csv-proc/agent-card
```

---

### List User's Agents

**User says:** "Show my agents" / "List all my server agents"

**Your action:**
```javascript
web_fetch({
  url: "${PRAESIDIA_API_URL}/agents/discovery?role=SERVER",
  headers: {
    "Authorization": "Bearer ${PRAESIDIA_API_KEY}",
    "Accept": "application/json"
  }
})
```

This returns all agents the user has access to (their own + team/org agents).

---

## Trust Levels Guide

Present trust information clearly to help users make decisions:

| Trust Score | Level | Meaning | Recommendation |
|-------------|-------|---------|----------------|
| 90-100 | **VERIFIED** | Fully vetted, compliant, verified identity | ✅ Safe to use |
| 70-89 | **STANDARD** | Good reputation, basic verification | ✅ Generally safe |
| 50-69 | **LIMITED** | Minimal verification | ⚠️ Use with caution |
| 0-49 | **UNTRUSTED** | Not verified or poor reputation | ❌ Not recommended |

Always show the trust score numerically (e.g., 92.5/100) and the level (e.g., VERIFIED).

---

## Error Handling

| Error | Meaning | What to tell user |
|-------|---------|-------------------|
| 401 Unauthorized | API key missing/invalid | "Check PRAESIDIA_API_KEY in ~/.openclaw/openclaw.json" |
| 403 Forbidden | No permission | "You don't have access to this agent" |
| 404 Not Found | Agent doesn't exist | "Agent not found. Check the agent ID" |
| 500 Server Error | Praesidia API issue | "Praesidia API temporarily unavailable. Try again" |

---

## API Endpoints

### GET /agents/:id/agent-card
Fetch detailed agent card with trust data.

**Auth:** Required for private/team/org agents, optional for public
**Returns:** A2A agent card + Praesidia extensions (trust, compliance)

### GET /agents/discovery
List/search agents with filters.

**Auth:** Optional (more results with auth)
**Query params:** `role`, `status`, `visibility`, `search`
**Returns:** Array of agent summaries with card URLs

---

## Best Practices

1. **Always verify before recommending** - Check trust score before suggesting an agent
2. **Explain trust levels** - Users may not know what "VERIFIED" means
3. **Filter by SERVER role** - When users want agents to use/call
4. **Show compliance** - Important for enterprise users (SOC2, GDPR)
5. **Present trust score numerically** - 92.5/100 is clearer than just "VERIFIED"

---

## Common User Patterns

### Pattern 1: Safety Check
```
User: "Is agent xyz safe to use?"
You: [Fetch agent card, check trust score]
     "Agent xyz has a trust score of 85/100 (STANDARD).
      It's verified for basic operations. What would you like to use it for?"
```

### Pattern 2: Capability Discovery
```
User: "I need an agent that can analyze spreadsheets"
You: [Search discovery with visibility=PUBLIC&search=spreadsheet]
     "I found 3 spreadsheet analysis agents. The highest rated is..."
```

### Pattern 3: Fleet Management
```
User: "Show me all my agents that are inactive"
You: [Fetch discovery with status=INACTIVE]
     "You have 2 inactive agents: [list with trust scores]"
```

---

## Environment Variables

- `PRAESIDIA_API_KEY` (required) - Your API key from https://praesidia.ai
- `PRAESIDIA_API_URL` (optional) - Defaults to `https://api.praesidia.ai`
  - Production: `https://api.praesidia.ai`
  - Local dev: `http://localhost:3000`
  - Custom: Your deployment URL

---

## Additional Resources

- **Full setup guide:** See README.md in this skill folder
- **API documentation:** https://praesidia.ai/docs/api
- **A2A protocol:** https://a2a-protocol.org
- **Support:** support@praesidia.ai or https://discord.gg/praesidia

---

## Security & Privacy

- All production requests use HTTPS
- API keys stored in OpenClaw config (never exposed to users)
- Private/team/org agents require authentication
- Public agents accessible without auth
- Trust verification protects against malicious agents
