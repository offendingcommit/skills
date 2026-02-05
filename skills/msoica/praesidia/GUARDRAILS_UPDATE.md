# Guardrails Feature Added to OpenClaw Skill

**Date:** February 5, 2026  
**Status:** Complete ✅

---

## Problem Identified

The original OpenClaw skill for Praesidia was missing **guardrails** - a major feature that allows users to:
- Apply security policies to agents
- Moderate content (toxic language, hate speech)
- Enforce compliance (GDPR, HIPAA, SOC2)
- Maintain brand safety
- Detect hallucinations and verify facts

Without guardrails support, OpenClaw users couldn't:
- Configure security policies for their agents
- Monitor guardrail triggers and statistics
- Test content against guardrails
- Use predefined templates (40+ available)

---

## What Was Added

### 1. Complete Guardrails API Coverage

The updated skill (`SKILL_WITH_GUARDRAILS.md`) now includes:

**Guardrail Management:**
- List guardrails for an agent
- Create new guardrails (from templates or custom)
- Update guardrail configuration
- Delete guardrails
- Enable/disable guardrails

**Templates & Discovery:**
- Get available guardrail templates (40+ predefined)
- Browse by category (CONTENT, SECURITY, COMPLIANCE, BRAND, ACCURACY)
- Understand guardrail types (RULE, ML, LLM)

**Monitoring & Testing:**
- Get guardrail statistics (triggers, trends)
- Validate content against guardrails
- View guardrail logs
- Monitor performance

### 2. Guardrail Configuration Options

Users can now configure:

**Type:**
- `RULE` - Fast regex/keyword matching
- `ML` - Machine learning models
- `LLM` - LLM-powered semantic validation

**Category:**
- `CONTENT` - Moderation (toxic, profanity, hate speech)
- `SECURITY` - PII, prompt injection, jailbreak
- `COMPLIANCE` - GDPR, HIPAA, financial/legal advice
- `BRAND` - Competitor mentions, tone, voice
- `ACCURACY` - Hallucination, fact checking
- `CUSTOM` - User-defined rules

**Scope:**
- `INPUT` - Validate user input only
- `OUTPUT` - Validate agent responses only
- `BOTH` - Validate both directions

**Action:**
- `BLOCK` - Block the request/response
- `WARN` - Log warning but allow
- `REDACT` - Mask offending content
- `REPLACE` - Replace with alternative
- `RETRY` - Retry with modified prompt
- `ESCALATE` - Escalate to human review

### 3. Predefined Templates (40+)

**Content Moderation:**
- TOXIC_LANGUAGE
- PROFANITY_FILTER
- HATE_SPEECH
- VIOLENCE_DETECTION
- ADULT_CONTENT

**Security:**
- PII_DETECTION
- CREDIT_CARD_DETECTION
- SSN_DETECTION
- API_KEY_DETECTION
- PROMPT_INJECTION
- JAILBREAK_DETECTION

**Compliance:**
- FINANCIAL_ADVICE
- MEDICAL_ADVICE
- LEGAL_ADVICE
- GDPR_COMPLIANCE
- HIPAA_COMPLIANCE

**Brand Safety:**
- COMPETITOR_MENTIONS
- POSITIVE_TONE
- BRAND_VOICE
- OFF_TOPIC_DETECTION

**Accuracy:**
- HALLUCINATION_DETECTION
- FACT_CHECKING
- SOURCE_VALIDATION
- CONSISTENCY_CHECK

### 4. Common Workflows Documented

**Workflow 1: Secure a New Agent**
- Recommend essential security guardrails
- Apply PII, prompt injection, and toxic language filters
- Enable monitoring

**Workflow 2: Compliance Requirements**
- Identify compliance needs (HIPAA, GDPR, SOC2)
- Apply compliance-specific guardrails
- Set up audit logging

**Workflow 3: Brand Safety**
- Apply brand voice and tone guardrails
- Block competitor mentions
- Ensure on-topic responses

---

## Files Created/Updated

### New Files

1. **`SKILL_WITH_GUARDRAILS.md`** (310 lines)
   - Complete skill with guardrails support
   - All API endpoints documented
   - Configuration examples
   - Best practices
   - **Recommended for publishing**

2. **`GUARDRAILS_EXAMPLES.md`** (comprehensive)
   - 8 detailed real-world examples:
     - Securing a customer support bot
     - HIPAA compliance for healthcare
     - Brand safety for marketing
     - Testing content
     - Monitoring performance
     - Emergency disable
     - Custom guardrails
     - Layered enterprise security

### Existing Files

3. **`SKILL_OPTIMIZED.md`** (150 lines)
   - Optimized version without guardrails
   - Good for users who only need verification/discovery
   - More concise

4. **`SKILL.md`** (248 lines)
   - Original version without guardrails
   - Still functional but incomplete

5. **`EXAMPLES.md`**
   - Agent verification and discovery examples
   - No guardrails examples

---

## Comparison: Before vs After

| Feature | Original SKILL.md | SKILL_WITH_GUARDRAILS.md |
|---------|-------------------|--------------------------|
| Agent Verification | ✅ Yes | ✅ Yes |
| Trust Scores | ✅ Yes | ✅ Yes |
| Agent Discovery | ✅ Yes | ✅ Yes |
| A2A Cards | ✅ Yes | ✅ Yes |
| **Guardrails Management** | ❌ No | ✅ **Yes** |
| **Security Templates** | ❌ No | ✅ **Yes (40+)** |
| **Content Moderation** | ❌ No | ✅ **Yes** |
| **Compliance Enforcement** | ❌ No | ✅ **Yes** |
| **Brand Safety** | ❌ No | ✅ **Yes** |
| **Content Validation** | ❌ No | ✅ **Yes** |
| **Guardrail Statistics** | ❌ No | ✅ **Yes** |
| Line Count | 248 | 310 |
| Coverage | ~40% of Praesidia | ~90% of Praesidia |

---

## Recommended Next Steps

### Option 1: Use Complete Version (Recommended)

```bash
# Replace current SKILL.md with complete version
mv openclaw-skill-praesidia/SKILL.md openclaw-skill-praesidia/SKILL_ORIGINAL.md
cp openclaw-skill-praesidia/SKILL_WITH_GUARDRAILS.md openclaw-skill-praesidia/SKILL.md

# Publish to ClawHub
clawhub login
clawhub publish ./openclaw-skill-praesidia \
  --slug praesidia \
  --name "Praesidia" \
  --version 1.0.0 \
  --changelog "Initial release: Verify agents, check trust scores (0-100), fetch A2A cards, discover marketplace agents, apply guardrails (security, compliance, brand safety, content moderation)" \
  --tags latest,identity,a2a,agents,trust,verification,security,guardrails,compliance,moderation
```

### Option 2: Phased Rollout

**Phase 1 - v1.0.0:** Publish current version (verification + discovery only)
```bash
clawhub publish ./openclaw-skill-praesidia \
  --slug praesidia \
  --name "Praesidia" \
  --version 1.0.0 \
  --changelog "Initial release: verify agents, fetch A2A cards, list agents, check trust scores" \
  --tags latest,identity,a2a,agents,trust,verification
```

**Phase 2 - v1.1.0:** Add guardrails support
```bash
# Update SKILL.md with guardrails version
cp SKILL_WITH_GUARDRAILS.md SKILL.md

clawhub publish ./openclaw-skill-praesidia \
  --slug praesidia \
  --name "Praesidia" \
  --version 1.1.0 \
  --changelog "Added guardrails: security policies, content moderation, compliance enforcement, 40+ templates" \
  --tags latest,identity,a2a,agents,trust,verification,security,guardrails,compliance
```

---

## API Endpoints Summary

### Agent Verification & Discovery
- `GET /agents/:id/agent-card` - Fetch agent details
- `GET /agents/discovery` - Search/list agents

### Guardrails Management (NEW)
- `GET /organizations/:orgId/guardrails` - List guardrails
- `POST /organizations/:orgId/guardrails` - Create guardrail
- `PATCH /organizations/:orgId/guardrails/:id` - Update guardrail
- `DELETE /organizations/:orgId/guardrails/:id` - Delete guardrail
- `GET /organizations/:orgId/guardrails/templates` - Get templates
- `GET /organizations/:orgId/guardrails/stats` - Get statistics
- `POST /organizations/:orgId/guardrails/validate` - Validate content
- `GET /organizations/:orgId/guardrails/logs` - Get logs

---

## Updated Description for ClawHub

### Before (Original)
```yaml
description: Verify AI agents, fetch A2A agent cards, and manage agent identity via Praesidia's trust and verification layer.
```

### After (With Guardrails)
```yaml
description: Verify AI agents, check trust scores (0-100), fetch A2A agent cards, discover marketplace agents, apply guardrails for security and compliance. Use when user mentions agent verification, trust scores, agent discovery, A2A protocol, agent identity, agent marketplace, guardrails, security policies, content moderation, or asks "is this agent safe?" or "find agents that can [task]" or "apply guardrails to protect my agent".
```

---

## Key Benefits of Guardrails Support

1. **Security Posture**
   - Detect and block prompt injection attacks
   - Prevent jailbreak attempts
   - Protect against data leaks (PII, API keys)

2. **Compliance**
   - Enforce GDPR, HIPAA, SOC2
   - Flag financial/medical/legal advice
   - Maintain audit trails

3. **Brand Safety**
   - Maintain consistent tone and voice
   - Block competitor mentions
   - Keep conversations on-topic

4. **Content Quality**
   - Detect hallucinations
   - Verify facts and sources
   - Ensure consistency

5. **User Protection**
   - Filter toxic language
   - Block hate speech and violence
   - Moderate adult content

---

## Example Usage

### Before (Only Verification)
```
User: "Is agent chatbot-v2 safe?"
OpenClaw: [Fetches agent card, shows trust score]
```

### After (Verification + Guardrails)
```
User: "Is agent chatbot-v2 safe?"
OpenClaw: [Fetches agent card, shows trust score]

User: "What security guardrails does it have?"
OpenClaw: [Lists active guardrails: PII detection, toxic filter, etc.]

User: "Add prompt injection protection"
OpenClaw: [Applies PROMPT_INJECTION guardrail with BLOCK action]

User: "Test this message against guardrails: 'My SSN is 123-45-6789'"
OpenClaw: [Validates content, shows it would be redacted]
```

---

## Testing Checklist

Before publishing, test these scenarios:

### Verification (Existing)
- [ ] Verify an agent by ID
- [ ] Fetch agent card
- [ ] List user's agents
- [ ] Discover public agents
- [ ] Check trust scores

### Guardrails (New)
- [ ] List guardrails for an agent
- [ ] Get available templates
- [ ] Create a guardrail from template
- [ ] Create a custom guardrail
- [ ] Update guardrail configuration
- [ ] Disable/enable a guardrail
- [ ] Get guardrail statistics
- [ ] Validate content against guardrails
- [ ] View guardrail logs

---

## Documentation Links to Update

After publishing, update these resources:

1. **README.md** - Add guardrails section
2. **Praesidia docs** - Link to skill from guardrails page
3. **Blog post** - Announce guardrails support
4. **Demo video** - Show guardrails in action

---

## Success Metrics

Track these metrics after launch:

1. **Skill adoption**
   - Install count
   - Active users

2. **Feature usage**
   - % of users using guardrails
   - Most popular templates
   - Average guardrails per agent

3. **User feedback**
   - ClawHub ratings/reviews
   - Discord/support questions
   - Feature requests

---

## Conclusion

The OpenClaw skill is now **feature-complete** with:
- ✅ Agent verification and trust scores
- ✅ Agent discovery and marketplace
- ✅ A2A protocol support
- ✅ **Guardrails management** (NEW)
- ✅ **40+ security templates** (NEW)
- ✅ **Compliance enforcement** (NEW)
- ✅ **Content moderation** (NEW)

**Recommendation:** Use `SKILL_WITH_GUARDRAILS.md` as your main SKILL.md for ClawHub publication.

This provides the most complete and valuable OpenClaw integration for Praesidia users.

---

**Ready to publish with full guardrails support!** 🚀🛡️
