# Praesidia OpenClaw Skill

This skill enables OpenClaw to verify AI agent identities, fetch A2A agent cards, and manage agents through Praesidia's trust and verification layer.

## Installation

### From ClawHub (Recommended)

```bash
clawhub install praesidia
```

### Manual Installation

1. Copy this folder to your OpenClaw skills directory:
   - Global: `~/.openclaw/skills/praesidia/`
   - Workspace: `<workspace>/skills/praesidia/`

2. OpenClaw will pick it up in the next session

## Setup

### 1. Get a Praesidia API Key

1. Sign up at [https://praesidia.ai](https://praesidia.ai)
2. Navigate to Settings → API Keys
3. Create a new API key
4. Copy the key (you'll need it for configuration)

### 2. Configure OpenClaw

Add the API key to your OpenClaw configuration at `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "praesidia": {
        "apiKey": "pk_live_abc123...",
        "env": {
          "PRAESIDIA_API_URL": "https://api.praesidia.ai"
        }
      }
    }
  }
}
```

**Configuration options:**
- `apiKey` (required) - Your Praesidia API key
- `env.PRAESIDIA_API_URL` (optional) - API base URL
  - Production: `https://api.praesidia.ai` (default)
  - Local development: `http://localhost:3000`
  - Custom deployment: your server URL

### 3. Verify Setup

Start a new OpenClaw session and ask:

```
"List my Praesidia agents"
```

If configured correctly, OpenClaw will fetch and display your agents.

## Usage

### Verify an Agent

```
"Verify agent chatbot-v2"
"Is agent data-analyzer-1 verified?"
```

### Fetch Agent Card

```
"Get the agent card for chatbot-v2"
"Fetch card from https://example.com/.well-known/agent-card.json"
```

### List Your Agents

```
"Show me my registered agents"
"List all my server agents"
"Find my active agents"
```

### Discover Public Agents

```
"Find public chatbot agents"
"Show me all public SERVER agents"
"Search for data analysis agents"
```

## Features

- ✅ **Agent Verification** - Check if agents are registered and verified
- ✅ **Trust Scores** - View trust levels (0-100) and verification status
- ✅ **A2A Agent Cards** - Fetch standard Agent-to-Agent protocol cards
- ✅ **Agent Discovery** - List your agents or discover public agents
- ✅ **Compliance Info** - View certifications (SOC2, GDPR, etc.)
- ✅ **Role Filtering** - Filter by CLIENT/SERVER agents
- ✅ **Secure** - All requests use HTTPS and authentication

## API Endpoints Used

The skill calls these Praesidia API endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/agents/:id/agent-card` | GET | Fetch A2A agent card for a specific agent |
| `/agents/discovery` | GET | List/discover agents with filters |

**Authentication:** Bearer token via `Authorization` header

## Troubleshooting

### "API key is missing or invalid"

**Problem:** `PRAESIDIA_API_KEY` is not configured or incorrect

**Solution:**
1. Check that the API key is set in `~/.openclaw/openclaw.json`
2. Verify the key format starts with `pk_live_` or `pk_test_`
3. Generate a new key from Praesidia dashboard if needed

### "Agent not found"

**Problem:** Agent doesn't exist or you don't have access

**Solution:**
1. Verify the agent ID is correct
2. Check that the agent is in your organization/team
3. For public agents, ensure `visibility=PUBLIC`

### "Connection refused"

**Problem:** Cannot reach the Praesidia API

**Solution:**
1. Check your internet connection
2. Verify `PRAESIDIA_API_URL` is correct
3. For local development, ensure the server is running

### Skill not loaded

**Problem:** OpenClaw doesn't recognize the skill

**Solution:**
1. Verify the skill is in the correct directory
2. Check that `SKILL.md` exists and has valid frontmatter
3. Start a new OpenClaw session to pick up the skill
4. Run `openclaw skills` to list loaded skills

## Development

### Local Praesidia Instance

If running Praesidia locally:

```json
{
  "skills": {
    "entries": {
      "praesidia": {
        "apiKey": "pk_test_local",
        "env": {
          "PRAESIDIA_API_URL": "http://localhost:3000"
        }
      }
    }
  }
}
```

### Testing

Ask OpenClaw to verify an agent:

```
"Verify agent test-agent-1"
```

Expected response should include trust score, verification status, and capabilities.

## Security & Privacy

- ✅ All requests use HTTPS (production)
- ✅ API keys are stored locally in OpenClaw config (not in skill)
- ✅ Keys are never logged or exposed to users
- ✅ Authentication required for private/team/org agents
- ✅ Public agents accessible without auth

## Support

- **Documentation:** [https://praesidia.ai/docs](https://praesidia.ai/docs)
- **Issues:** [GitHub Issues](https://github.com/praesidia/praesidia/issues)
- **Community:** [Discord](https://discord.gg/praesidia)
- **Email:** support@praesidia.ai

## ClawHub

This skill is published on ClawHub: [https://clawhub.ai/skills/praesidia](https://clawhub.ai/skills/praesidia)

**Tags:** `identity`, `a2a`, `agents`, `trust`, `verification`, `security`

## License

MIT License - See main repository for details

## Version

Current version: 1.0.0

For updates: `clawhub update praesidia` or check [ClawHub](https://clawhub.ai)
