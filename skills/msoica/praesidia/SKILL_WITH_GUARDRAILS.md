---
name: Praesidia
description: Verify AI agents, check trust scores (0-100), fetch A2A agent cards, discover marketplace agents, apply guardrails for security and compliance. Use when user mentions agent verification, trust scores, agent discovery, A2A protocol, agent identity, agent marketplace, guardrails, security policies, content moderation, or asks "is this agent safe?" or "find agents that can [task]" or "apply guardrails to protect my agent".
metadata: {"openclaw":{"requires":{"env":["PRAESIDIA_API_KEY"]},"primaryEnv":"PRAESIDIA_API_KEY","homepage":"https://praesidia.ai","emoji":"🛡️"}}
---

# Praesidia Agent Identity, Verification & Guardrails

Verify AI agents, check trust scores (0-100), discover marketplace agents, and apply guardrails for security and compliance.

## Core Capabilities

- **Verify agents** - Check if an agent is registered, verified, and trustworthy
- **Trust scores** - View 0-100 trust ratings and verification status
- **Agent discovery** - Search marketplace for public agents by capability
- **Guardrails** - Apply security policies and content moderation to agents
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

### 1. Verify an Agent

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
- ✓ Verification status
- 🔧 Capabilities
- 📜 Compliance (SOC2, GDPR, etc.)
- 🔗 Agent card URL

---

### 2. List Guardrails for an Agent

**User says:** "What guardrails are configured for my agent?" / "Show me security policies for chatbot-v2"

**Your action:**
```javascript
// First, get the user's organization ID from their profile or context
// Then fetch guardrails
web_fetch({
  url: "${PRAESIDIA_API_URL}/organizations/${orgId}/guardrails?agentId=${agentId}",
  headers: {
    "Authorization": "Bearer ${PRAESIDIA_API_KEY}",
    "Accept": "application/json"
  }
})
```

**Present to user:**
- List of guardrails with:
  - Name and description
  - Type (RULE, ML, LLM)
  - Category (CONTENT, SECURITY, COMPLIANCE, etc.)
  - Action (BLOCK, WARN, REDACT, REPLACE)
  - Scope (INPUT, OUTPUT, BOTH)
  - Enabled status
  - Trigger count

**Example output:**
```
Found 3 guardrails for ChatBot V2:

1. PII Detection (ENABLED)
   - Type: ML | Category: SECURITY
   - Scope: BOTH (input & output)
   - Action: REDACT sensitive data
   - Triggered: 45 times

2. Toxic Language Filter (ENABLED)
   - Type: RULE | Category: CONTENT
   - Scope: BOTH
   - Action: BLOCK toxic content
   - Triggered: 12 times

3. Financial Advice Warning (ENABLED)
   - Type: LLM | Category: COMPLIANCE
   - Scope: OUTPUT only
   - Action: WARN if detected
   - Triggered: 3 times
```

---

### 3. Get Available Guardrail Templates

**User says:** "What guardrail templates are available?" / "Show me security templates"

**Your action:**
```javascript
web_fetch({
  url: "${PRAESIDIA_API_URL}/organizations/${orgId}/guardrails/templates",
  headers: {
    "Authorization": "Bearer ${PRAESIDIA_API_KEY}",
    "Accept": "application/json"
  }
})
```

**Available Templates:**

**Content Moderation:**
- TOXIC_LANGUAGE - Detect toxic/harmful language
- PROFANITY_FILTER - Filter profanity
- HATE_SPEECH - Detect hate speech
- VIOLENCE_DETECTION - Detect violent content
- ADULT_CONTENT - Filter adult content

**Security:**
- PII_DETECTION - Detect personally identifiable information
- CREDIT_CARD_DETECTION - Detect credit card numbers
- SSN_DETECTION - Detect social security numbers
- API_KEY_DETECTION - Detect leaked API keys
- PROMPT_INJECTION - Detect prompt injection attacks
- JAILBREAK_DETECTION - Detect jailbreak attempts

**Compliance:**
- FINANCIAL_ADVICE - Flag financial advice
- MEDICAL_ADVICE - Flag medical advice
- LEGAL_ADVICE - Flag legal advice
- GDPR_COMPLIANCE - Enforce GDPR rules
- HIPAA_COMPLIANCE - Enforce HIPAA rules

**Brand Safety:**
- COMPETITOR_MENTIONS - Detect competitor mentions
- POSITIVE_TONE - Ensure positive tone
- BRAND_VOICE - Maintain brand voice
- OFF_TOPIC_DETECTION - Detect off-topic responses

**Accuracy:**
- HALLUCINATION_DETECTION - Detect hallucinations
- FACT_CHECKING - Verify facts
- SOURCE_VALIDATION - Validate sources
- CONSISTENCY_CHECK - Check consistency

---

### 4. Apply a Guardrail to an Agent

**User says:** "Add PII detection to my chatbot" / "Apply toxic language filter to agent xyz"

**Your action:**
```javascript
web_fetch({
  url: "${PRAESIDIA_API_URL}/organizations/${orgId}/guardrails",
  method: "POST",
  headers: {
    "Authorization": "Bearer ${PRAESIDIA_API_KEY}",
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    name: "PII Detection",
    description: "Automatically detect and redact PII",
    agentId: "${agentId}",
    template: "PII_DETECTION",
    type: "ML",
    category: "SECURITY",
    scope: "BOTH",
    action: "REDACT",
    severity: "HIGH",
    isEnabled: true,
    priority: 0
  })
})
```

**Guardrail Options:**

**Type:**
- RULE - Simple regex/keyword matching (fast)
- ML - Machine learning model (balanced)
- LLM - LLM-powered validation (most accurate)

**Category:**
- CONTENT - Content moderation
- SECURITY - Security checks
- COMPLIANCE - Regulatory compliance
- BRAND - Brand safety
- ACCURACY - Accuracy checks
- CUSTOM - Custom rules

**Scope:**
- INPUT - Validate user input only
- OUTPUT - Validate agent output only
- BOTH - Validate both directions

**Action:**
- BLOCK - Block the request/response entirely
- WARN - Log warning but allow through
- REDACT - Mask the offending content
- REPLACE - Replace with alternative content
- RETRY - Retry with modified prompt
- ESCALATE - Escalate to human review

**Severity:**
- LOW, MEDIUM, HIGH, CRITICAL

---

### 5. Get Guardrail Statistics

**User says:** "Show me guardrail stats" / "How many times have guardrails been triggered?"

**Your action:**
```javascript
web_fetch({
  url: "${PRAESIDIA_API_URL}/organizations/${orgId}/guardrails/stats",
  headers: {
    "Authorization": "Bearer ${PRAESIDIA_API_KEY}",
    "Accept": "application/json"
  }
})
```

**Present:**
- Total guardrails configured
- Total triggers across all guardrails
- Breakdown by category
- Most triggered guardrails
- Recent activity

---

### 6. Validate Content Against Guardrails

**User says:** "Check if this message passes guardrails: [content]"

**Your action:**
```javascript
web_fetch({
  url: "${PRAESIDIA_API_URL}/organizations/${orgId}/guardrails/validate",
  method: "POST",
  headers: {
    "Authorization": "Bearer ${PRAESIDIA_API_KEY}",
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    content: "User's message here",
    agentId: "${agentId}",
    scope: "INPUT"
  })
})
```

**Response shows:**
- Whether content passed or failed
- Which guardrails were triggered
- Suggested actions (block, redact, warn)
- Modified content (if redaction applied)

---

### 7. Discover Public Agents

**User says:** "Find public data analysis agents" / "Show me chatbot agents"

**Your action:**
```javascript
web_fetch({
  url: "${PRAESIDIA_API_URL}/agents/discovery?visibility=PUBLIC&search=data",
  headers: { "Accept": "application/json" }
})
```

**Filters available:**
- `?visibility=PUBLIC` - public marketplace agents
- `?role=SERVER` - agents that provide services
- `?status=ACTIVE` - only active agents
- `?search=keyword` - search by name/description

---

### 8. List User's Agents

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

## Guardrails Best Practices

When helping users with guardrails:

1. **Start with templates** - Use predefined templates before custom rules
2. **Layer security** - Combine multiple guardrails (PII + Toxic + Compliance)
3. **Test before enabling** - Use validate endpoint to test content first
4. **Monitor triggers** - Check stats regularly to tune thresholds
5. **Scope appropriately** - Use INPUT for user content, OUTPUT for agent responses
6. **Choose right action**:
   - **BLOCK** for critical security issues (PII, prompt injection)
   - **REDACT** for sensitive data that can be masked
   - **WARN** for compliance/brand issues that need logging
   - **ESCALATE** for edge cases requiring human review

---

## Common Guardrail Workflows

### Workflow 1: Secure a New Agent

```
User: "I just deployed a new chatbot. Make it secure."

You: 
1. List available security templates
2. Recommend essential guardrails:
   - PII_DETECTION (REDACT, HIGH)
   - PROMPT_INJECTION (BLOCK, CRITICAL)
   - TOXIC_LANGUAGE (BLOCK, HIGH)
3. Apply recommended guardrails
4. Enable monitoring and alerts
```

### Workflow 2: Compliance Requirements

```
User: "My agent handles healthcare data. What guardrails do I need?"

You:
1. Check if HIPAA compliance is required
2. Apply HIPAA-specific guardrails:
   - HIPAA_COMPLIANCE (BLOCK, CRITICAL)
   - PII_DETECTION (REDACT, HIGH)
   - MEDICAL_ADVICE (WARN, HIGH)
3. Set scope to BOTH (input & output)
4. Enable audit logging
```

### Workflow 3: Brand Safety

```
User: "Ensure my agent stays on brand"

You:
1. Apply brand guardrails:
   - POSITIVE_TONE (REPLACE, MEDIUM)
   - COMPETITOR_MENTIONS (BLOCK, HIGH)
   - OFF_TOPIC_DETECTION (WARN, MEDIUM)
2. Test with sample messages
3. Monitor trigger stats
4. Tune thresholds based on results
```

---

## API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/agents/:id/agent-card` | GET | Fetch agent details + trust score |
| `/agents/discovery` | GET | List/search agents |
| `/organizations/:orgId/guardrails` | GET | List guardrails |
| `/organizations/:orgId/guardrails` | POST | Create guardrail |
| `/organizations/:orgId/guardrails/:id` | PATCH | Update guardrail |
| `/organizations/:orgId/guardrails/:id` | DELETE | Delete guardrail |
| `/organizations/:orgId/guardrails/templates` | GET | Get templates |
| `/organizations/:orgId/guardrails/stats` | GET | Get statistics |
| `/organizations/:orgId/guardrails/validate` | POST | Validate content |

---

## Error Handling

| Error | Meaning | What to tell user |
|-------|---------|-------------------|
| 401 Unauthorized | API key missing/invalid | "Check PRAESIDIA_API_KEY in ~/.openclaw/openclaw.json" |
| 403 Forbidden | No permission | "You don't have access to this agent/organization" |
| 404 Not Found | Agent/guardrail doesn't exist | "Not found. Check the ID" |
| 400 Bad Request | Invalid guardrail config | "Invalid configuration. Check template and parameters" |
| 500 Server Error | Praesidia API issue | "Praesidia API temporarily unavailable. Try again" |

---

## Environment Variables

- `PRAESIDIA_API_KEY` (required) - Your API key from https://praesidia.ai
- `PRAESIDIA_API_URL` (optional) - Defaults to `https://api.praesidia.ai`
  - Production: `https://api.praesidia.ai`
  - Local dev: `http://localhost:3000`
  - Custom: Your deployment URL

---

## Additional Resources

- **Setup guide:** See README.md in this skill folder
- **API documentation:** https://praesidia.ai/docs/api
- **Guardrails guide:** https://praesidia.ai/docs/guardrails
- **A2A protocol:** https://a2a-protocol.org
- **Support:** support@praesidia.ai or https://discord.gg/praesidia

---

## Security & Privacy

- All production requests use HTTPS
- API keys stored in OpenClaw config (never exposed to users)
- Guardrails processed server-side (ML/LLM models not exposed)
- Guardrail logs available for compliance audits
- Trust verification protects against malicious agents
