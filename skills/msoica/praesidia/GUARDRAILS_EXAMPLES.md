# Praesidia Guardrails - Detailed Examples

This file contains comprehensive examples of using Praesidia guardrails with OpenClaw.

---

## Example 1: Securing a Customer Support Bot

**Scenario:** User deploys a customer support chatbot and needs to apply security guardrails

**User:** "I just deployed a customer support bot. Make it secure and compliant."

**Agent Process:**

1. Recommend essential guardrails:
```
I'll help you secure your customer support bot with these essential guardrails:

1. PII Detection (CRITICAL) - Protect customer data
2. Toxic Language Filter (HIGH) - Maintain professional tone
3. Prompt Injection Detection (CRITICAL) - Prevent attacks
4. Financial Advice Warning (MEDIUM) - Compliance protection
```

2. Apply PII Detection:
```javascript
web_fetch({
  url: "${PRAESIDIA_API_URL}/organizations/${orgId}/guardrails",
  method: "POST",
  body: JSON.stringify({
    name: "PII Detection & Redaction",
    description: "Automatically detect and redact customer PII (emails, phone numbers, SSN, etc.)",
    agentId: "${agentId}",
    template: "PII_DETECTION",
    type: "ML",
    category: "SECURITY",
    scope: "BOTH",
    action: "REDACT",
    severity: "CRITICAL",
    isEnabled: true,
    priority: 0
  })
})
```

3. Apply other guardrails similarly

**Agent Response:**
```
✅ Secured your customer support bot with 4 guardrails:

1. ✓ PII Detection (ML, CRITICAL)
   - Scope: Both input & output
   - Action: Automatically redact sensitive data
   - Detects: SSN, credit cards, emails, phone numbers

2. ✓ Toxic Language Filter (RULE, HIGH)
   - Scope: Both directions
   - Action: Block toxic/abusive content
   - Protects: Agent and customer experience

3. ✓ Prompt Injection Detection (LLM, CRITICAL)
   - Scope: User input only
   - Action: Block injection attempts
   - Prevents: Security vulnerabilities

4. ✓ Financial Advice Warning (LLM, MEDIUM)
   - Scope: Agent output only
   - Action: Warn if detected
   - Compliance: Prevents unauthorized advice

Your bot is now secure! Monitor stats at: 
https://praesidia.ai/guardrails/stats
```

---

## Example 2: HIPAA Compliance for Healthcare Bot

**Scenario:** Healthcare provider needs HIPAA-compliant agent

**User:** "I'm building a healthcare assistant. What guardrails do I need for HIPAA compliance?"

**Agent Process:**

1. Check available HIPAA templates:
```javascript
web_fetch({
  url: "${PRAESIDIA_API_URL}/organizations/${orgId}/guardrails/templates"
})
```

2. Apply HIPAA-specific guardrails:
```javascript
// 1. HIPAA Compliance Guard
web_fetch({
  url: "${PRAESIDIA_API_URL}/organizations/${orgId}/guardrails",
  method: "POST",
  body: JSON.stringify({
    name: "HIPAA Compliance",
    template: "HIPAA_COMPLIANCE",
    agentId: "${agentId}",
    type: "LLM",
    category: "COMPLIANCE",
    scope: "BOTH",
    action: "BLOCK",
    severity: "CRITICAL",
    priority: 0
  })
})

// 2. PII Protection (PHI)
web_fetch({
  url: "${PRAESIDIA_API_URL}/organizations/${orgId}/guardrails",
  method: "POST",
  body: JSON.stringify({
    name: "PHI Protection",
    description: "Protected Health Information detection and redaction",
    template: "PII_DETECTION",
    agentId: "${agentId}",
    type: "ML",
    category: "SECURITY",
    scope: "BOTH",
    action: "REDACT",
    severity: "CRITICAL",
    priority: 1
  })
})

// 3. Medical Advice Warning
web_fetch({
  url: "${PRAESIDIA_API_URL}/organizations/${orgId}/guardrails",
  method: "POST",
  body: JSON.stringify({
    name: "Medical Advice Detection",
    template: "MEDICAL_ADVICE",
    agentId: "${agentId}",
    type: "LLM",
    category: "COMPLIANCE",
    scope: "OUTPUT",
    action: "WARN",
    severity: "HIGH",
    priority: 2
  })
})
```

**Agent Response:**
```
✅ HIPAA Compliance guardrails applied:

🔒 CRITICAL Guardrails (3):
1. HIPAA Compliance (LLM)
   - Enforces HIPAA data handling rules
   - Blocks non-compliant interactions
   - Audit trail enabled

2. PHI Protection (ML)
   - Detects Protected Health Information
   - Automatically redacts sensitive data
   - Covers: Names, addresses, medical records, etc.

3. Medical Advice Detection (LLM)
   - Flags potential medical advice
   - Warns when crossing compliance boundaries
   - Escalates for review

✅ Your healthcare assistant is now HIPAA-compliant!

Important reminders:
- All interactions are logged for audit
- Regular compliance reviews recommended
- BAA (Business Associate Agreement) required
- Monitor guardrail logs daily

Next steps:
1. Test with sample conversations
2. Review guardrail stats weekly
3. Adjust thresholds as needed
4. Document all configurations
```

---

## Example 3: Brand Safety for Marketing Bot

**Scenario:** Marketing team wants to ensure brand voice consistency

**User:** "Make sure our marketing bot stays on brand and doesn't mention competitors"

**Agent Process:**

1. Apply brand safety guardrails:
```javascript
// 1. Competitor Mentions
web_fetch({
  url: "${PRAESIDIA_API_URL}/organizations/${orgId}/guardrails",
  method: "POST",
  body: JSON.stringify({
    name: "Block Competitor Mentions",
    template: "COMPETITOR_MENTIONS",
    agentId: "${agentId}",
    type: "RULE",
    category: "BRAND",
    scope: "OUTPUT",
    action: "REPLACE",
    severity: "HIGH",
    priority: 0,
    config: {
      keywords: ["CompetitorA", "CompetitorB", "OtherBrand"],
      caseSensitive: false,
      replacementText: "industry-leading solutions"
    }
  })
})

// 2. Positive Tone
web_fetch({
  url: "${PRAESIDIA_API_URL}/organizations/${orgId}/guardrails",
  method: "POST",
  body: JSON.stringify({
    name: "Maintain Positive Tone",
    template: "POSITIVE_TONE",
    agentId: "${agentId}",
    type: "LLM",
    category: "BRAND",
    scope: "OUTPUT",
    action: "RETRY",
    severity: "MEDIUM",
    priority: 1,
    config: {
      prompt: "Ensure the response is positive, professional, and aligned with our brand voice"
    }
  })
})

// 3. Off-Topic Detection
web_fetch({
  url: "${PRAESIDIA_API_URL}/organizations/${orgId}/guardrails",
  method: "POST",
  body: JSON.stringify({
    name: "Stay On Topic",
    template: "OFF_TOPIC_DETECTION",
    agentId: "${agentId}",
    type: "LLM",
    category: "BRAND",
    scope: "OUTPUT",
    action: "REPLACE",
    severity: "MEDIUM",
    priority: 2,
    config: {
      allowedTopics: ["product features", "pricing", "customer support", "company news"],
      replacementText: "I'm here to help with questions about our products and services."
    }
  })
})
```

**Agent Response:**
```
✅ Brand safety guardrails configured:

🎨 Brand Protection (3 guardrails):

1. Block Competitor Mentions (RULE, HIGH)
   - Detects: CompetitorA, CompetitorB, OtherBrand
   - Action: Replace with "industry-leading solutions"
   - Scope: Agent output only
   - Case insensitive matching

2. Maintain Positive Tone (LLM, MEDIUM)
   - Analyzes sentiment and brand voice
   - Action: Retry with positive framing
   - Ensures professional, upbeat responses

3. Stay On Topic (LLM, MEDIUM)
   - Allowed topics: Products, pricing, support
   - Action: Redirect off-topic conversations
   - Maintains focus on value proposition

Your marketing bot will now:
✅ Never mention competitors
✅ Always maintain positive tone
✅ Stay focused on your offerings
✅ Align with brand voice

Test it out and monitor stats to see how often guardrails trigger!
```

---

## Example 4: Testing Content Before Deployment

**Scenario:** User wants to test a message against guardrails before going live

**User:** "Check if this message passes our guardrails: 'Hi! My email is john@example.com and my SSN is 123-45-6789. Can you help?'"

**Agent Process:**

```javascript
web_fetch({
  url: "${PRAESIDIA_API_URL}/organizations/${orgId}/guardrails/validate",
  method: "POST",
  body: JSON.stringify({
    content: "Hi! My email is john@example.com and my SSN is 123-45-6789. Can you help?",
    agentId: "${agentId}",
    scope: "INPUT"
  })
})
```

**Agent Response:**
```
⚠️ Content validation failed - 2 guardrails triggered:

1. 🚨 PII Detection (CRITICAL)
   - Detected: Email address, Social Security Number
   - Action: REDACT
   - Modified content: "Hi! My email is [REDACTED] and my SSN is [REDACTED]. Can you help?"

2. ⚠️ Sensitive Data Warning (HIGH)
   - Detected: Personal identifiers in plain text
   - Recommendation: User should not share this information

✅ Modified safe content:
"Hi! My email is [REDACTED] and my SSN is [REDACTED]. Can you help?"

Recommendation:
- The content has been automatically sanitized
- Original message would be blocked/redacted
- Educate users not to share sensitive data
```

---

## Example 5: Monitoring Guardrail Performance

**Scenario:** User wants to see how guardrails are performing

**User:** "Show me guardrail stats for the last month"

**Agent Process:**

```javascript
web_fetch({
  url: "${PRAESIDIA_API_URL}/organizations/${orgId}/guardrails/stats?agentId=${agentId}",
  headers: {
    "Authorization": "Bearer ${PRAESIDIA_API_KEY}"
  }
})
```

**Agent Response:**
```
📊 Guardrail Statistics (Last 30 Days)

Overall Summary:
- Total guardrails: 5 active
- Total triggers: 1,247
- Blocked interactions: 89
- Redacted content: 445
- Warnings logged: 713

Breakdown by Guardrail:

1. PII Detection (CRITICAL)
   ├─ Triggers: 445 (35.7%)
   ├─ Action: Redacted 445 instances
   ├─ Most common: Email addresses (234), Phone numbers (156)
   └─ Trend: ↓ 12% vs last month

2. Toxic Language Filter (HIGH)
   ├─ Triggers: 89 (7.1%)
   ├─ Action: Blocked 89 interactions
   ├─ Peak days: Weekends
   └─ Trend: → Stable

3. Prompt Injection Detection (CRITICAL)
   ├─ Triggers: 12 (1.0%)
   ├─ Action: Blocked all attempts
   ├─ Attack vectors: 9 DAN, 3 role-play
   └─ Trend: ↓ 20% vs last month

4. Financial Advice Warning (MEDIUM)
   ├─ Triggers: 234 (18.8%)
   ├─ Action: Warned 234 times
   ├─ False positives: ~15% (needs tuning)
   └─ Trend: ↑ 8% vs last month

5. Off-Topic Detection (MEDIUM)
   ├─ Triggers: 467 (37.4%)
   ├─ Action: Redirected conversations
   ├─ Common topics: Unrelated questions
   └─ Trend: ↑ 5% vs last month

🎯 Recommendations:
1. ✅ PII Detection working well - no changes needed
2. ✅ Toxic Language filter effective
3. ⚠️ Financial Advice has 15% false positives - consider adjusting threshold
4. ℹ️ Off-Topic triggers increasing - may need to expand allowed topics

Would you like to adjust any guardrail settings?
```

---

## Example 6: Emergency Disable

**Scenario:** Guardrail causing too many false positives

**User:** "The financial advice guardrail is blocking too many legitimate responses. Disable it temporarily."

**Agent Process:**

```javascript
// Get guardrail ID first
web_fetch({
  url: "${PRAESIDIA_API_URL}/organizations/${orgId}/guardrails?agentId=${agentId}"
})

// Then disable specific guardrail
web_fetch({
  url: "${PRAESIDIA_API_URL}/organizations/${orgId}/guardrails/${guardrailId}",
  method: "PATCH",
  body: JSON.stringify({
    isEnabled: false
  })
})
```

**Agent Response:**
```
✅ Temporarily disabled "Financial Advice Warning" guardrail

Status: DISABLED
Previous state: 234 triggers, 15% false positive rate

⚠️ Important reminders:
- Compliance protection is now reduced
- Monitor agent responses manually
- Re-enable after tuning the guardrail

To tune and re-enable:
1. Review recent logs to identify false positives
2. Adjust threshold or prompt
3. Test with validation endpoint
4. Re-enable when satisfied

Would you like help tuning the guardrail settings?
```

---

## Example 7: Custom Guardrail for Specific Use Case

**Scenario:** User needs a custom rule not covered by templates

**User:** "Create a guardrail that blocks any mention of our unreleased Product X"

**Agent Process:**

```javascript
web_fetch({
  url: "${PRAESIDIA_API_URL}/organizations/${orgId}/guardrails",
  method: "POST",
  body: JSON.stringify({
    name: "Block Unreleased Product Mentions",
    description: "Prevent discussion of Product X before official launch",
    agentId: "${agentId}",
    type: "RULE",
    category: "CUSTOM",
    scope: "OUTPUT",
    action: "REPLACE",
    severity: "HIGH",
    priority: 0,
    config: {
      keywords: ["Product X", "ProductX", "Project Phoenix", "Phoenix"],
      caseSensitive: false,
      replacementText: "We have exciting new products coming soon! Stay tuned for announcements."
    }
  })
})
```

**Agent Response:**
```
✅ Custom guardrail created: "Block Unreleased Product Mentions"

Configuration:
- Type: RULE (keyword matching)
- Category: CUSTOM
- Triggers on: "Product X", "ProductX", "Project Phoenix", "Phoenix"
- Action: Replace with teaser message
- Severity: HIGH
- Priority: 0 (highest)

How it works:
1. Agent starts generating a response
2. If any blocked keyword is detected
3. Replace with: "We have exciting new products coming soon!"
4. Log the trigger for monitoring

Example:
❌ User: "Tell me about Product X"
✅ Agent: "We have exciting new products coming soon! Stay tuned for announcements."

The guardrail is now active and protecting your pre-launch information!
```

---

## Example 8: Layered Security Approach

**Scenario:** Enterprise security requirements

**User:** "Set up maximum security for our enterprise agent handling sensitive data"

**Agent Process:**

Apply multiple layers of security guardrails:

```javascript
// Layer 1: Input validation
const inputGuardrails = [
  { template: "PII_DETECTION", action: "REDACT", severity: "CRITICAL" },
  { template: "PROMPT_INJECTION", action: "BLOCK", severity: "CRITICAL" },
  { template: "JAILBREAK_DETECTION", action: "BLOCK", severity: "CRITICAL" },
  { template: "API_KEY_DETECTION", action: "REDACT", severity: "CRITICAL" },
  { template: "CREDIT_CARD_DETECTION", action: "REDACT", severity: "CRITICAL" },
  { template: "SSN_DETECTION", action: "REDACT", severity: "CRITICAL" }
];

// Layer 2: Content moderation
const contentGuardrails = [
  { template: "TOXIC_LANGUAGE", action: "BLOCK", severity: "HIGH" },
  { template: "HATE_SPEECH", action: "BLOCK", severity: "CRITICAL" },
  { template: "PROFANITY_FILTER", action: "REDACT", severity: "HIGH" }
];

// Layer 3: Compliance
const complianceGuardrails = [
  { template: "GDPR_COMPLIANCE", action: "BLOCK", severity: "CRITICAL" },
  { template: "FINANCIAL_ADVICE", action: "ESCALATE", severity: "HIGH" },
  { template: "LEGAL_ADVICE", action: "ESCALATE", severity: "HIGH" }
];

// Layer 4: Output validation
const outputGuardrails = [
  { template: "HALLUCINATION_DETECTION", action: "WARN", severity: "MEDIUM" },
  { template: "FACT_CHECKING", action: "WARN", severity: "MEDIUM" },
  { template: "SOURCE_VALIDATION", action: "WARN", severity: "MEDIUM" }
];

// Apply all guardrails
[...inputGuardrails, ...contentGuardrails, ...complianceGuardrails, ...outputGuardrails]
  .forEach((config, index) => {
    web_fetch({
      url: "${PRAESIDIA_API_URL}/organizations/${orgId}/guardrails",
      method: "POST",
      body: JSON.stringify({
        ...config,
        agentId: "${agentId}",
        priority: index,
        isEnabled: true
      })
    });
  });
```

**Agent Response:**
```
✅ Enterprise security suite deployed: 18 guardrails

🔒 Layer 1: Input Validation (6 guardrails)
- PII, Prompt Injection, Jailbreak, API Keys, Credit Cards, SSN
- Action: Block/Redact threats before processing
- All set to CRITICAL severity

🛡️ Layer 2: Content Moderation (3 guardrails)
- Toxic language, Hate speech, Profanity
- Action: Block harmful content
- HIGH to CRITICAL severity

📜 Layer 3: Compliance (3 guardrails)
- GDPR, Financial advice, Legal advice
- Action: Block violations, Escalate edge cases
- CRITICAL severity

✓ Layer 4: Output Validation (6 guardrails)
- Hallucination, Fact checking, Source validation
- Action: Warn on potential issues
- MEDIUM severity (allows pass-through with logging)

Your enterprise agent now has:
- ✅ 18 active guardrails
- ✅ 4 layers of protection
- ✅ Prioritized evaluation (critical checks first)
- ✅ Comprehensive audit logging
- ✅ Full compliance coverage

Security posture: MAXIMUM 🔒

Monitor: https://praesidia.ai/guardrails/stats
```

---

## Tips for Using Guardrails

1. **Start with templates** - Predefined templates are battle-tested
2. **Layer defenses** - Multiple guardrails provide depth
3. **Test before enabling** - Use validate endpoint to test
4. **Monitor regularly** - Check stats weekly to tune
5. **Adjust thresholds** - Start strict, relax based on data
6. **Document decisions** - Keep notes on why guardrails were configured
7. **Plan for updates** - Review quarterly as threats evolve
8. **Balance security and UX** - Too strict = poor user experience

---

## Troubleshooting

### Guardrail not triggering

1. Check if enabled: `isEnabled: true`
2. Verify scope matches your use case (INPUT/OUTPUT/BOTH)
3. Check priority (lower number = higher priority)
4. Test with validation endpoint to confirm trigger

### Too many false positives

1. Review guardrail logs
2. Adjust threshold (if ML/LLM)
3. Refine keywords/patterns (if RULE)
4. Consider changing action (WARN instead of BLOCK)
5. Add allowed values to config

### Guardrail causing latency

1. Check type: RULE is fastest, LLM is slowest
2. Consider moving LLM checks to async/background
3. Use WARN action for non-critical checks
4. Optimize priority order (critical checks first)
