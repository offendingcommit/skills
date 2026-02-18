---
name: unhuman
description: Search, register, and manage domain names via unhuman.domains. Pay with bitcoin using agent-wallet. Use when the user wants to find available domains, register a new domain, manage DNS records, update nameservers, or renew a domain. Supports autonomous registration with --wallet flag for agent-wallet auto-pay (MDK 402 payment flow).
---

# unhuman — Domain Management CLI

Register and manage domains at [unhuman.domains](https://unhuman.domains), paid with bitcoin via Lightning Network.

## Install

```bash
npx unhuman domains <command>
```

No install needed — runs via npx.

## Commands

### Search domains

```bash
npx unhuman domains search myproject
npx unhuman domains search myproject --tld com,dev,xyz
npx unhuman domains search myproject --json
```

Returns availability and pricing for each TLD.

### Register a domain

```bash
# Auto-pay with agent-wallet (fully autonomous)
npx unhuman domains register mysite.xyz --wallet --email recovery@example.com

# Manual payment (prints invoice, waits for preimage)
npx unhuman domains register mysite.xyz --email recovery@example.com
```

- `--wallet` pays automatically via `@moneydevkit/agent-wallet`
- `--email` sets recovery email (recommended)
- On success, stores management token to `~/.unhuman/tokens.json`

### Domain info

```bash
npx unhuman domains info mysite.xyz
```

Requires stored management token.

### DNS records

```bash
# List current records
npx unhuman domains dns mysite.xyz

# Set records (replaces entire zone)
npx unhuman domains dns set mysite.xyz --records '[{"type":"A","name":"@","value":"1.2.3.4","ttl":3600}]'
```

### Update nameservers

```bash
npx unhuman domains nameservers mysite.xyz ns1.example.com ns2.example.com
```

### Renew a domain

```bash
npx unhuman domains renew mysite.xyz --wallet
npx unhuman domains renew mysite.xyz --wallet --period 2
```

### Recover management token

```bash
# Step 1: Request code
npx unhuman domains recover mysite.xyz --email recovery@example.com

# Step 2: Confirm with code from email
npx unhuman domains recover mysite.xyz --email recovery@example.com --code 123456
```

### List stored tokens

```bash
npx unhuman domains tokens
```

## Agent-Wallet Integration

When `--wallet` is passed, the CLI:
1. Submits the request → gets a 402 with Lightning invoice
2. Pays via `npx @moneydevkit/agent-wallet send <invoice>`
3. Retries with the preimage as proof of payment
4. Fully autonomous — no human interaction needed

Requires a running agent-wallet daemon (`npx @moneydevkit/agent-wallet start`).

## Notes

- All commands support `--json` for machine-readable output
- Management tokens stored at `~/.unhuman/tokens.json`
- Prices are in USD, paid in bitcoin at current exchange rate
- Recovery email is optional but recommended for token recovery
