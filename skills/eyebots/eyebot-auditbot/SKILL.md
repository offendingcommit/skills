---
name: eyebot-auditbot
description: AI-powered smart contract security scanner and auditor
version: 1.0.0
author: ILL4NE
metadata:
  api_endpoint: http://93.186.255.184:8001
  pricing:
    per_use: $3
    lifetime: $25
  chains: [base, ethereum, polygon, arbitrum]
---

# Eyebot AuditBot 🔍

AI-powered smart contract security scanner. Detect vulnerabilities, rug pulls, honeypots, and security issues before they become problems.

## API Endpoint
`http://93.186.255.184:8001`

## Usage
```bash
# Request payment
curl -X POST "http://93.186.255.184:8001/a2a/request-payment?agent_id=auditbot&caller_wallet=YOUR_WALLET"

# After payment, verify and execute
curl -X POST "http://93.186.255.184:8001/a2a/verify-payment?request_id=...&tx_hash=..."
```

## Pricing
- Per-use: $3
- Lifetime (unlimited): $25
- All 15 agents bundle: $200

## Capabilities
- Reentrancy vulnerability detection
- Honeypot and rug pull detection
- Owner privilege analysis
- Tax and fee analysis
- Liquidity lock verification
- Holder distribution analysis
- Similar contract comparison
- Risk scoring (0-100)
- Detailed vulnerability reports
