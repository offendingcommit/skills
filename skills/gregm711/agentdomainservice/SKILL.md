---
name: domain-availability
description: Check domain availability, explore TLDs, and help users find the perfect domain name via AgentDomainService API
homepage: https://agentdomainservice.com
emoji: 🌐
metadata:
  clawdbot:
    primaryEnv: any
    requires:
      bins: []
      env: []
---

# Domain Availability for AI Agents

Check domain availability, explore names across TLDs, and help users find the perfect domain name.

**Base URL:** `https://agentdomainservice.com`

No authentication. No rate limits. Proper JSON/TXT responses with correct Content-Type headers.

---

## Quick Reference

| Task | Endpoint | Content-Type |
|------|----------|--------------|
| Check single domain (JSON) | `GET /api/lookup/{domain}` | application/json |
| Check single domain (TXT) | `GET /api/lookup/{domain}?format=txt` | text/plain |
| Explore 8 TLDs (JSON) | `GET /api/explore/{name}` | application/json |
| Explore 8 TLDs (TXT) | `GET /api/explore/{name}?format=txt` | text/plain |
| Documentation | `GET /llms.txt` | text/plain |

---

## 1. Check Single Domain

**When:** User asks "Is example.com available?"

```
GET https://agentdomainservice.com/api/lookup/myapp.com
```

### JSON Response

```json
{
  "fqdn": "myapp.com",
  "available": true,
  "status": "available",
  "premium": false,
  "price": {
    "amount": 12.99,
    "currency": "USD",
    "period": "year"
  },
  "renewal": {
    "amount": 12.99,
    "currency": "USD",
    "period": "year"
  },
  "checked_at": "2025-01-15T10:30:00.000Z",
  "source": "namecom",
  "cache": {
    "hit": false,
    "ttl_seconds": 120,
    "stale": false
  },
  "tlds": [
    {"domain": "myapp.com", "tld": "com", "available": true, "status": "available", "price": 12.99, "premium": false},
    {"domain": "myapp.io", "tld": "io", "available": true, "status": "available", "price": 49.99, "premium": false}
  ],
  "suggestions": [
    {"domain": "getmyapp.com", "available": true, "price": 12.99, "premium": false}
  ]
}
```

### TXT Response

```
GET https://agentdomainservice.com/api/lookup/myapp.com?format=txt
```

```
fqdn=myapp.com
available=true
status=available
premium=false
price_amount=12.99
price_currency=USD
price_period=year
renewal_amount=12.99
checked_at=2025-01-15T10:30:00Z
source=namecom
cache_hit=false
ttl_seconds=120
stale=false

# all_tlds
myapp.com=available:$12.99
myapp.io=available:$49.99
myapp.dev=taken

# suggestions
getmyapp.com=$12.99
```

### Query Parameters

| Param | Description | Example |
|-------|-------------|---------|
| `format` | `json` (default) or `txt` | `txt` |
| `context` | Keywords for better suggestions | `payment+processing` |
| `max_price` | Filter suggestions by max USD | `20` |

---

## 2. Explore Name Across TLDs

**When:** User likes a name but wants to see TLD options.

```
GET https://agentdomainservice.com/api/explore/coolstartup
```

Checks 8 TLDs: `.com`, `.io`, `.dev`, `.ai`, `.app`, `.co`, `.net`, `.org`

### JSON Response

```json
{
  "name": "coolstartup",
  "checked_at": "2025-01-15T10:30:00.000Z",
  "summary": {
    "available_count": 6,
    "taken_count": 2,
    "total": 8,
    "cheapest": {
      "domain": "coolstartup.net",
      "tld": "net",
      "price": 11.99
    }
  },
  "results": [
    {"tld": "com", "domain": "coolstartup.com", "available": false, "status": "registered"},
    {"tld": "io", "domain": "coolstartup.io", "available": true, "status": "available", "purchase_price": 49.99},
    {"tld": "dev", "domain": "coolstartup.dev", "available": true, "status": "available", "purchase_price": 14.99},
    {"tld": "ai", "domain": "coolstartup.ai", "available": true, "status": "available", "purchase_price": 89.99}
  ],
  "suggestions": [
    {"domain": "mycoolstartup.com", "available": true, "price": 12.99, "premium": false}
  ]
}
```

### TXT Response

```
GET https://agentdomainservice.com/api/explore/coolstartup?format=txt
```

```
name=coolstartup
checked_at=2025-01-15T10:30:00.000Z
available_count=6
taken_count=2
cheapest=coolstartup.net:$11.99

# results
coolstartup.com=registered
coolstartup.io=available:$49.99
coolstartup.dev=available:$14.99
coolstartup.ai=available:$89.99
coolstartup.app=available:$17.99
coolstartup.co=available:$24.99
coolstartup.net=available:$11.99
coolstartup.org=available:$11.99

# suggestions
mycoolstartup.com=$12.99
```

---

## Status Values

| Status | `available` | Meaning |
|--------|-------------|---------|
| `available` | `true` | Can register |
| `registered` | `false` | Already taken |
| `unknown` | `false` | Error/timeout |

**Key:** The `available` field is ALWAYS boolean (`true`/`false`), never undefined.

---

## Workflow Examples

### Direct Check
```
User: "Is cloudmesh.com available?"

1. GET /api/lookup/cloudmesh.com
2. Parse: available=false
3. Show suggestions from response
4. "cloudmesh.com is taken. Available alternatives: cloudmesh.io ($49.99), cloudmesh.dev ($14.99)"
```

### Explore TLDs
```
User: "What's available for aihelper?"

1. GET /api/explore/aihelper
2. Parse results array
3. "aihelper.com is taken, but these are available:
   - aihelper.io - $49.99/year
   - aihelper.ai - $89.99/year
   - aihelper.dev - $14.99/year (cheapest)"
```

### Budget Search
```
User: "Find me a domain under $20"

1. GET /api/explore/myapp?max_price=20
2. Only TLDs under $20 shown
3. "Here are options under $20: myapp.dev ($14.99), myapp.app ($17.99)"
```

### With Context
```
User: "I need a domain for my AI writing assistant"

1. GET /api/lookup/aiwriter.com?context=AI+writing+assistant
2. Returns availability + relevant suggestions
3. "aiwriter.com is taken. Try: writeai.io ($49.99), aiauthor.com ($12.99)"
```

---

## TLD Pricing Guide

| TLD | Best For | Typical Price |
|-----|----------|---------------|
| `.com` | Universal, established | $12-15/yr |
| `.io` | Tech startups | $40-60/yr |
| `.ai` | AI/ML companies | $80-180/yr |
| `.dev` | Developer tools | $14-18/yr |
| `.app` | Mobile/web apps | $16-20/yr |
| `.co` | Startups | $24-30/yr |
| `.net` | Classic | $11-15/yr |
| `.org` | Non-profits | $11-15/yr |

---

## Key Points

- **Use `/api/` routes** - Returns proper JSON/TXT with correct Content-Type
- **`available` is ALWAYS boolean** - Never undefined or null
- **No authentication required** - Just make HTTP requests
- **Results are cached** - Fast responses, safe to retry
- **Use `?format=txt`** - Easiest to parse, key=value pairs

---

## Source

AgentDomainService: https://agentdomainservice.com
Documentation: https://agentdomainservice.com/llms.txt
