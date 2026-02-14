---
name: thrd
description: "Automate email account provisioning and management via the thrd.email API. Use to: (1) Instantly provision new email accounts (tenant name optional), (2) Retrieve API keys and inbox details, (3) Poll for inbound emails, (4) Send/Reply to emails (idempotency required), and (5) Track outbound status. Ideal for creating autonomous AI email agents without human intervention."
---

# Thrd Email Skill

This skill allows you to manage email accounts for AI agents using the [thrd.email](https://thrd.email) infrastructure.

## Workflows

### Provision a New Email Account

To create a new email account, run the onboarding script. The `tenant_name` is now optional:

```bash
python3 scripts/onboard.py [tenant_name]
```

This returns a JSON with your `apiKey`, `inbox` address, and endpoints. **Save the API Key securely.**

### Manage Emails and Track Delivery

For detailed API usage (polling, sending, replying, and checking delivery status), see [references/api.md](references/api.md).

## Tools

- `scripts/onboard.py`: Instant provisioning of a new email inbox.
