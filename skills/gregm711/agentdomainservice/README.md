# Domain Availability Skill for ClawhHub

A skill for AI agents to check domain availability using [AgentDomainService](https://agentdomainservice.com).

## What It Does

- **Check single domains** - `GET /api/lookup/{domain}` returns JSON
- **Explore across TLDs** - `GET /api/explore/{name}` checks 8 TLDs at once
- **Budget filtering** - `?max_price=20` shows only options under $20
- **Context suggestions** - `?context=keywords` for relevant alternatives

## Publishing to ClawhHub

```bash
# Install CLI
npm install -g clawdbot@latest

# Login via GitHub
clawhub login

# Publish (from this directory)
clawhub publish . \
  --slug domain-availability \
  --name "Domain Availability" \
  --version 1.0.0 \
  --tags latest
```

## Installing the Skill

```bash
clawhub install domain-availability
```

## API Endpoints

| Endpoint | Content-Type | Purpose |
|----------|--------------|---------|
| `/api/lookup/{domain}` | application/json | Check single domain |
| `/api/lookup/{domain}?format=txt` | text/plain | Check single domain (key=value) |
| `/api/explore/{name}` | application/json | Check name across 8 TLDs |
| `/api/explore/{name}?format=txt` | text/plain | Check name across 8 TLDs (key=value) |

## About AgentDomainService

AI agents can't use traditional domain registrars (GoDaddy, Namecheap) due to CAPTCHAs and anti-bot measures. AgentDomainService provides:

- **Proper API responses** - JSON/TXT with correct Content-Type headers
- **No authentication** - Just make HTTP requests
- **No rate limits** - Built for AI agents
- **Real-time data** - From Name.com
- **Caching** - Fast responses

**Base URL:** `https://agentdomainservice.com`

## License

MIT
