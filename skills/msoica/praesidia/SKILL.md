---
name: Praesidia
description: Verify AI agents, fetch A2A agent cards, and manage agent identity via Praesidia's trust and verification layer.
metadata: {"openclaw":{"requires":{"env":["PRAESIDIA_API_KEY"]},"primaryEnv":"PRAESIDIA_API_KEY","homepage":"https://praesidia.ai","emoji":"🛡️"}}
---

# Praesidia Agent Identity & Verification

Use Praesidia to verify AI agent identities, fetch A2A agent cards, list your agents, and check trust scores.

## What This Skill Does

- **Verify agent identity** - Check if an agent is registered and verified in Praesidia
- **Fetch agent cards** - Get A2A-compliant agent cards with capabilities and metadata
- **List agents** - Discover your registered agents or public agents
- **Check trust scores** - View agent trust levels and verification status

## Prerequisites

You need:
1. A Praesidia account - sign up at https://praesidia.ai
2. An API key from your Praesidia dashboard (Settings → API Keys)

## Configuration

Set your API key in `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "praesidia": {
        "apiKey": "your_praesidia_api_key_here",
        "env": {
          "PRAESIDIA_API_URL": "https://api.praesidia.ai"
        }
      }
    }
  }
}
```

If you're running Praesidia locally or on a custom domain, set `PRAESIDIA_API_URL` accordingly (default: `https://api.praesidia.ai`).

## How to Use

### Verify an Agent

When the user asks to verify an agent by ID:

```
User: "Verify agent abc-123"
```

**Your task:**
1. Use the `web_fetch` tool to call Praesidia's agent card endpoint
2. Construct the URL: `{PRAESIDIA_API_URL}/agents/{agentId}/agent-card`
3. Include the Authorization header: `Authorization: Bearer {PRAESIDIA_API_KEY}`
4. Fetch and parse the response

**Example web_fetch call:**
```javascript
web_fetch({
  url: "${PRAESIDIA_API_URL}/agents/abc-123/agent-card",
  headers: {
    "Authorization": "Bearer ${PRAESIDIA_API_KEY}",
    "Accept": "application/json"
  }
})
```

**Successful response** includes:
- Agent name and description
- Capabilities (what the agent can do)
- Trust level (UNTRUSTED, LIMITED, STANDARD, VERIFIED, TRUSTED)
- Trust score (0-100)
- Verification status
- Compliance certifications (SOC2, GDPR, etc.)

**Present to user:**
- Agent name and description
- Trust level and score
- Verification status
- Key capabilities
- Any compliance certifications

### Fetch Agent Card by URL

When the user provides an agent card URL:

```
User: "Fetch the agent card from https://example.com/.well-known/agent-card.json"
```

**Your task:**
1. Use `web_fetch` to fetch the provided URL directly
2. Parse the A2A agent card JSON
3. Summarize the agent's capabilities and metadata

Note: For Praesidia-registered agents, prefer using the Praesidia API (previous section) to get trust and verification data.

### List Your Agents

When the user asks to see their agents:

```
User: "Show me my registered agents"
User: "List all my agents"
```

**Your task:**
1. Use `web_fetch` to call Praesidia's discovery endpoint
2. URL: `{PRAESIDIA_API_URL}/agents/discovery`
3. Include Authorization header
4. Parse the list and present agent names, IDs, roles, and card URLs

**Example web_fetch call:**
```javascript
web_fetch({
  url: "${PRAESIDIA_API_URL}/agents/discovery",
  headers: {
    "Authorization": "Bearer ${PRAESIDIA_API_KEY}",
    "Accept": "application/json"
  }
})
```

**Optional filters** (add as query params):
- `?role=SERVER` - only server agents
- `?role=CLIENT` - only client agents
- `?status=ACTIVE` - only active agents
- `?visibility=PUBLIC` - only public agents
- `?search=chatbot` - search by name

**Present to user:**
- List of agents with:
  - Name and description
  - Agent ID
  - Role (CLIENT or SERVER)
  - Status (ACTIVE, INACTIVE, etc.)
  - Trust level
  - Link to agent card

### Discover Public Agents

When the user wants to find public agents:

```
User: "Find public chatbot agents"
User: "Show me all public SERVER agents"
```

**Your task:**
1. Use `web_fetch` to call `{PRAESIDIA_API_URL}/agents/discovery?visibility=PUBLIC`
2. Add `&role=SERVER` or `&search=chatbot` as needed
3. No Authorization header needed for public agents (but including it shows more results)

## Error Handling

If the API returns an error:
- **401 Unauthorized**: API key is missing or invalid. Ask user to check `PRAESIDIA_API_KEY` in config.
- **404 Not Found**: Agent doesn't exist or user doesn't have access.
- **403 Forbidden**: User doesn't have permission to access this agent.
- **500 Internal Error**: Praesidia API issue. Suggest trying again later.

## Environment Variables

- `PRAESIDIA_API_KEY` (required) - Your Praesidia API key
- `PRAESIDIA_API_URL` (optional) - API base URL (default: `https://api.praesidia.ai`)

## Privacy & Security

- All requests use HTTPS
- API keys are never logged or exposed to the user
- Only authenticated requests can access private/team/organization agents
- Public agents are accessible without authentication

## Examples

**Example 1: Verify an agent**
```
User: "Is agent chatbot-v2 verified?"

You: [Call web_fetch with {PRAESIDIA_API_URL}/agents/chatbot-v2/agent-card]

Response: "✅ ChatBot V2 is verified!
- Trust Level: VERIFIED
- Trust Score: 92.5/100
- Status: ACTIVE
- Capabilities: message:send, task:create, data:analyze
- Compliance: SOC2, GDPR
- Last verified: 2 days ago"
```

**Example 2: List user's agents**
```
User: "Show me all my server agents"

You: [Call web_fetch with {PRAESIDIA_API_URL}/agents/discovery?role=SERVER]

Response: "Found 3 server agents:

1. ChatBot V2 (chatbot-v2)
   - Role: SERVER | Status: ACTIVE
   - Trust: VERIFIED (92.5)
   - Card: https://api.praesidia.ai/agents/chatbot-v2/agent-card

2. Data Analyzer (data-analyzer-1)
   - Role: SERVER | Status: ACTIVE
   - Trust: STANDARD (75.0)
   - Card: https://api.praesidia.ai/agents/data-analyzer-1/agent-card

3. Task Manager (task-mgr)
   - Role: SERVER | Status: INACTIVE
   - Trust: LIMITED (45.0)
   - Card: https://api.praesidia.ai/agents/task-mgr/agent-card"
```

**Example 3: Discover public agents**
```
User: "Find public agents for data analysis"

You: [Call web_fetch with {PRAESIDIA_API_URL}/agents/discovery?visibility=PUBLIC&search=data]

Response: "Found 2 public data analysis agents:

1. OpenData Analyzer by Acme Corp
   - Capabilities: data:analyze, chart:generate, report:create
   - Trust: VERIFIED (88.0)
   
2. CSV Processor by DataTools
   - Capabilities: file:parse, data:transform, export:json
   - Trust: STANDARD (70.0)"
```

## Tips

- Always use the agent card endpoint for Praesidia-registered agents to get trust and verification data
- When listing agents, filter by `role=SERVER` if the user wants agents they can call/use
- Present trust scores clearly - users care about verification and compliance
- For external agent cards (not in Praesidia), note that trust data isn't available

## Support

For issues or questions:
- Praesidia Documentation: https://praesidia.ai/docs
- Community: https://discord.gg/praesidia
- Email: support@praesidia.ai