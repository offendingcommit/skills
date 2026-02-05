# Praesidia Skill - Extended Examples

This file contains detailed examples of using the Praesidia skill with OpenClaw.

---

## Example 1: Daily Agent Health Check

**Scenario:** User wants a morning report on their agent fleet

**User:** "Good morning! Give me a health report on my agents"

**Agent Process:**

1. Fetch all user's agents:
```javascript
web_fetch({
  url: "${PRAESIDIA_API_URL}/agents/discovery",
  headers: { "Authorization": "Bearer ${PRAESIDIA_API_KEY}" }
})
```

2. Group by trust level and status
3. Calculate overall fleet health
4. Present summary

**Expected Output:**
```
🌅 Good morning! Here's your agent health report:

✅ Healthy Agents (3):
1. ChatBot V2 - VERIFIED (92.5) - Active
2. Data Analyzer - VERIFIED (88.0) - Active
3. Email Assistant - STANDARD (75.0) - Active

⚠️ Needs Attention (1):
- Task Manager - LIMITED (45.0) - Inactive
  Recommendation: Review and update, or consider deactivation

📊 Overall Fleet Health: 85/100
All critical agents operational. No urgent issues.
```

---

## Example 2: Discovering and Vetting a New Agent

**Scenario:** User needs a specific capability and wants to find a trusted agent

**User:** "I need a PDF processing agent. Find me one in the marketplace."

**Agent Process:**

1. Search public agents:
```javascript
web_fetch({
  url: "${PRAESIDIA_API_URL}/agents/discovery?visibility=PUBLIC&search=pdf"
})
```

2. Filter to SERVER agents with relevant capabilities
3. Sort by trust score
4. Present top options with recommendations

**Agent Response:**
```
Found 2 public PDF processing agents:

1. PDF Master by DocTools Inc ⭐ Recommended
   - Trust: VERIFIED (90.0)
   - Capabilities: pdf:parse, pdf:extract, pdf:convert
   - Compliance: SOC2, GDPR
   - Pricing: $0.01/page
   - Agent card: https://api.praesidia.ai/agents/pdf-master/agent-card

2. Quick PDF by StartupAI
   - Trust: STANDARD (65.0)
   - Capabilities: pdf:parse, pdf:extract
   - No compliance certifications
   - Pricing: Free tier available
   - Agent card: https://api.praesidia.ai/agents/quick-pdf/agent-card

Would you like me to verify PDF Master in detail?
```

**User:** "Yes, verify PDF Master"

**Agent Process:**

Fetch detailed card:
```javascript
web_fetch({
  url: "${PRAESIDIA_API_URL}/agents/pdf-master/agent-card",
  headers: { "Authorization": "Bearer ${PRAESIDIA_API_KEY}" }
})
```

**Agent Response:**
```
✅ PDF Master is verified and safe to use!

Trust Level: VERIFIED
Trust Score: 90.0/100
Verification Status: Active
Last Verified: 3 days ago

Capabilities:
- pdf:parse - Extract text from PDFs
- pdf:extract - Extract images and metadata
- pdf:convert - Convert PDFs to other formats

Security & Compliance:
✅ SOC2 Type II certified
✅ GDPR compliant
✅ API key authentication
✅ End-to-end encryption

Guardrails Available:
- Rate limiting (100 req/min)
- File size limit (50MB)
- PII detection and redaction

Pricing:
- Free: 100 pages/month
- Pro: $0.01/page ($9.99/month for 1000 pages)

Ready to integrate? I can help you set it up.
```

---

## Example 3: Proactive Security Alert

**Scenario:** Agent notices a trust score drop

**Agent (Proactive):**
```
⚠️ Security Alert: Agent "Task Manager" trust score dropped from 68 to 45 (LIMITED → UNTRUSTED)

Last verified: 30 days ago
Current status: ACTIVE but low trust

Recommendations:
1. Review recent changes to this agent
2. Check for security incidents
3. Consider disabling until trust is restored
4. Contact agent owner for clarification

Would you like me to deactivate this agent as a precaution?
```

---

## Example 4: Building Multi-Agent Workflow

**Scenario:** User wants to chain multiple agents together

**User:** "I want to use an agent to extract data from PDFs, then analyze it with a data agent"

**Agent Process:**

1. Verify both agents exist and are trusted:
```javascript
// Verify PDF agent
web_fetch({
  url: "${PRAESIDIA_API_URL}/agents/pdf-master/agent-card",
  headers: { "Authorization": "Bearer ${PRAESIDIA_API_KEY}" }
})

// Verify data agent
web_fetch({
  url: "${PRAESIDIA_API_URL}/agents/data-analyzer/agent-card",
  headers: { "Authorization": "Bearer ${PRAESIDIA_API_KEY}" }
})
```

2. Check compatibility (capabilities, API versions)
3. Verify trust scores are acceptable
4. Suggest workflow

**Agent Response:**
```
Great! I've verified both agents:

1. PDF Master (VERIFIED - 90.0)
   ✅ Can extract: text, tables, images
   ✅ Output formats: JSON, CSV, XML
   ✅ Trusted and compliant

2. Data Analyzer (VERIFIED - 88.0)
   ✅ Can analyze: JSON, CSV data
   ✅ Outputs: Charts, reports, insights
   ✅ Trusted and compliant

✅ These agents are compatible! Workflow:

Step 1: PDF Master extracts data → JSON
Step 2: Data Analyzer processes JSON → Insights

Both agents are highly trusted (90.0 and 88.0). Safe to proceed.

Would you like me to set up this workflow?
```

---

## Example 5: Comparing Multiple Agents

**Scenario:** User wants to compare options before choosing

**User:** "Compare all public chatbot agents for me"

**Agent Process:**

1. Search for chatbot agents:
```javascript
web_fetch({
  url: "${PRAESIDIA_API_URL}/agents/discovery?visibility=PUBLIC&search=chatbot&role=SERVER"
})
```

2. Fetch detailed cards for each
3. Build comparison table

**Agent Response:**
```
Found 3 public chatbot agents. Here's a comparison:

| Agent | Trust Score | Compliance | Pricing | Capabilities |
|-------|-------------|------------|---------|--------------|
| ChatBot Pro | 92.5 (VERIFIED) | SOC2, GDPR | $0.02/msg | message:send, context:maintain, multimodal:support |
| Simple Chat | 75.0 (STANDARD) | None | Free | message:send, context:maintain |
| Enterprise Bot | 95.0 (VERIFIED) | SOC2, GDPR, HIPAA | $0.05/msg | message:send, context:maintain, multimodal:support, analytics:track |

Recommendations:
- Best overall: ChatBot Pro (high trust, compliant, reasonable price)
- Budget option: Simple Chat (decent trust, free)
- Enterprise needs: Enterprise Bot (highest trust, HIPAA compliant)

Which one interests you?
```

---

## Example 6: Agent Registration Verification

**Scenario:** User just registered a new agent and wants to verify it's working

**User:** "I just registered my new agent 'my-bot-123'. Can you check if it's set up correctly?"

**Agent Process:**

1. Fetch agent card:
```javascript
web_fetch({
  url: "${PRAESIDIA_API_URL}/agents/my-bot-123/agent-card",
  headers: { "Authorization": "Bearer ${PRAESIDIA_API_KEY}" }
})
```

2. Validate agent card structure
3. Check trust score and status
4. Verify A2A compliance

**Agent Response:**
```
✅ Your agent "my-bot-123" is registered and accessible!

Agent Name: MyBot
Agent ID: my-bot-123
Status: ACTIVE
Trust Score: 50.0 (LIMITED) - This is normal for new agents

Agent Card: ✅ Valid A2A format
Capabilities: message:send, task:execute
Visibility: PRIVATE (only you can see it)

Next Steps to Increase Trust:
1. Complete verification process (Settings → Agents → Verify)
2. Add compliance certifications (if applicable)
3. Increase usage and positive interactions
4. Get reviews from other users

Your agent is ready to use! Trust score will increase over time.
```

---

## Example 7: Team Agent Discovery

**Scenario:** User wants to see agents shared within their team

**User:** "Show me all agents my team has access to"

**Agent Process:**

1. Fetch team and org agents:
```javascript
web_fetch({
  url: "${PRAESIDIA_API_URL}/agents/discovery",
  headers: { "Authorization": "Bearer ${PRAESIDIA_API_KEY}" }
})
```

2. Filter to TEAM and ORGANIZATION visibility
3. Group by owner
4. Show sharing status

**Agent Response:**
```
Found 5 agents shared with your team:

Your Agents (2):
1. ChatBot V2 - VERIFIED (92.5) - TEAM visibility
2. Data Analyzer - STANDARD (75.0) - TEAM visibility

Team Members' Agents (3):
1. Email Bot (by john@company.com) - VERIFIED (88.0) - TEAM visibility
2. Scheduler (by sarah@company.com) - STANDARD (70.0) - TEAM visibility
3. Report Generator (by admin@company.com) - VERIFIED (90.0) - ORGANIZATION visibility

All agents are accessible to your team. Trust scores look good.
```

---

## Example 8: Compliance-Focused Search

**Scenario:** Enterprise user needs HIPAA-compliant agents

**User:** "Find me agents that are HIPAA compliant"

**Agent Process:**

1. Search all agents:
```javascript
web_fetch({
  url: "${PRAESIDIA_API_URL}/agents/discovery?visibility=PUBLIC",
  headers: { "Authorization": "Bearer ${PRAESIDIA_API_KEY}" }
})
```

2. Filter response for agents with HIPAA in compliance array
3. Present with trust scores

**Agent Response:**
```
Found 2 HIPAA-compliant agents:

1. Medical Assistant Pro
   - Trust: VERIFIED (95.0)
   - Compliance: SOC2, GDPR, HIPAA
   - Capabilities: medical:analyze, patient:interact, record:maintain
   - Pricing: $0.10/interaction
   - Last audit: 15 days ago
   
2. Healthcare Chatbot
   - Trust: VERIFIED (90.0)
   - Compliance: HIPAA, SOC2
   - Capabilities: appointment:schedule, symptom:check
   - Pricing: $0.05/interaction
   - Last audit: 7 days ago

Both agents are highly trusted and actively maintained. Medical Assistant Pro
has the highest trust score and most comprehensive compliance.
```

---

## Example 9: Error Recovery

**Scenario:** Agent encounters an error and guides user to fix it

**User:** "Verify agent xyz-123"

**Agent Response (Error):**
```
❌ Failed to verify agent xyz-123

Error: 401 Unauthorized - API key is invalid

Troubleshooting steps:
1. Check that PRAESIDIA_API_KEY is set in ~/.openclaw/openclaw.json
2. Verify the key format: should start with pk_live_ or pk_test_
3. Generate a new key if needed: https://praesidia.ai → Settings → API Keys
4. Restart OpenClaw after updating the config

Current config location: ~/.openclaw/openclaw.json
Expected format:
{
  "skills": {
    "entries": {
      "praesidia": {
        "apiKey": "pk_live_your_key_here"
      }
    }
  }
}

Would you like me to help you set up a new API key?
```

---

## Example 10: Scheduled Monitoring

**Scenario:** User sets up a recurring check

**User:** "Check my agent trust scores every Monday and alert me if any drop below 70"

**Agent (Confirmation):**
```
✅ Scheduled monitoring created!

Schedule: Every Monday at 9:00 AM
Trigger: Trust score < 70
Action: Send alert

I'll check these agents:
- ChatBot V2 (current: 92.5)
- Data Analyzer (current: 75.0)
- Email Assistant (current: 75.0)
- Task Manager (current: 45.0) ⚠️ Already below threshold

⚠️ Note: Task Manager (45.0) is currently below your threshold.
Would you like me to send you a report now?
```

---

## Tips for Using These Examples

1. **Adapt to context** - Use the pattern that best matches the user's request
2. **Always show trust scores** - Users care about safety and verification
3. **Explain trust levels** - Many users won't know what VERIFIED means
4. **Be proactive** - Suggest next steps based on the results
5. **Handle errors gracefully** - Guide users to fix issues rather than just showing errors
