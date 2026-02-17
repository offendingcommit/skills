---
name: payram-mcp-integration
description: Accept crypto payments instantly via PayRam MCP. Hosted server (mcp.payram.com) works immediately for testnet - zero setup required. For production, autonomous headless setup available (10 min, fully automated via env vars). Use when user says "accept crypto payments", "create payment link", "test payment", "setup PayRam", "install PayRam", "PayRam on base". Complete headless guide in references/headless-setup.md
license: MIT
metadata:
  author: PayRam
  version: 1.2.1
  mcp-server: payram
  category: payments
  tags: [crypto, stablecoins, payments, agent-commerce, USDC, USDT, Base, Ethereum, MCP, Bitcoin, headless, autonomous]
  homepage: https://payram.com
  github: https://github.com/PayRam/payram-helper-mcp-server
  documentation: https://docs.payram.com/mcp-integration
  headless-guide: https://github.com/PayRam/payram-scripts/blob/main/docs/PAYRAM_HEADLESS_AGENT.md
---

# PayRam MCP Integration

Accept crypto payments instantly - hosted MCP server ready to use, or install locally for production.

## 🚀 Instant Start (No Installation)

**Try PayRam now** - hosted MCP server at `mcp.payram.com`:

```bash
# OpenClaw: Add hosted MCP server
mcporter config add payram --command "https://mcp.payram.com"

# Test immediately
mcporter call "payram.create_payee(amount: 10, currency: 'USDC', chain: 'base')"
```

**Environment**: Testnet (Base Sepolia, Ethereum Sepolia)  
**Use case**: Testing, development, demos  
**Setup time**: 0 minutes ⚡  
**Real funds**: ❌ Not supported (testnet only)  

---

## 🤖 For AI Agents: Headless Setup (Production)

PayRam has **agent-first** installation designed for autonomous operation.

### Quick Setup (Fully Automated)
```bash
# Clone repo
git clone https://github.com/PayRam/payram-scripts
cd payram-scripts

# Set credentials (one-time)
export PAYRAM_EMAIL="agent@example.com"
export PAYRAM_PASSWORD="secure_password"

# Install and setup (non-interactive)
./agent_run_local.sh  # Choose option 1: Install
./agent_headless.sh run  # Creates wallet, deploys contracts, ready!
```

### Environment Variables (Full Automation)
```bash
PAYRAM_EMAIL="agent@example.com"
PAYRAM_PASSWORD="yourpass"
PAYRAM_PAYMENT_AMOUNT=10
PAYRAM_BLOCKCHAIN_CODE=BASE  # or ETH, POLYGON
PAYRAM_MNEMONIC="your twelve word mnemonic..."  # optional
```

**Key Features**:
- ✅ Non-interactive setup (no prompts)
- ✅ Environment variable configuration
- ✅ Automatic wallet generation
- ✅ Smart contract deployment (testnet default)
- ✅ Payment link creation
- ✅ Installs where OpenClaw runs (local machine or VPS)
- ✅ Complete troubleshooting guide included

**Full Documentation**: See `references/headless-setup.md` for complete agent automation guide.

---

## 📊 Quick Comparison

| Feature | Hosted (mcp.payram.com) | Headless Local Install |
|---------|-------------------------|------------------------|
| **Setup time** | 0 minutes ⚡ | 10 minutes |
| **Environment** | Testnet only | Testnet (default) + Mainnet |
| **Real funds** | ❌ No | ✅ Yes (after config) |
| **Installation** | None needed | Where OpenClaw runs |
| **Use case** | Testing, demos | Production payments |
| **Automation** | N/A | Fully automatable (env vars) |
| **Networks** | Base/ETH Sepolia | Base, Ethereum, Polygon, Tron |

---

## Supported Features

**Currencies**: USDC, USDT, BTC, ETH  
**Networks**: Base, Ethereum, Polygon, Tron, TON  
**MCP Tools**: `create_payee`, `send_payment`, `get_balance`, `generate_invoice`, `verify_payment`, `list_transactions`

## When to Use This Skill

This skill triggers when you need to:
- Accept crypto payments for services or products
- Create payment links or invoices
- Process stablecoin transactions (USDC/USDT)
- Set up autonomous agent payment capabilities
- Check wallet balances or payment status
- Send crypto payouts
- Enable crypto checkout on platforms

## MCP Server Setup

### Option 1: Public MCP Server (Fastest)

```json
{
  "mcpServers": {
    "payram": {
      "url": "https://mcp.payram.com"
    }
  }
}
```

### Option 2: Self-Hosted (Maximum Sovereignty)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/PayRam/payram-scripts/main/setup_payram.sh)"
# MCP server runs at http://localhost:3333/mcp
```

For OpenClaw:
```bash
mcporter config add payram --command "https://mcp.payram.com"
```

## Available MCP Tools

| Tool | Purpose | Example |
|------|---------|---------|
| `create_payee` | Generate payment address | "Create $50 USDC invoice on Base" |
| `send_payment` | Initiate outbound payment | "Send 100 USDC to 0xABC..." |
| `get_balance` | Check wallet balance | "Check my USDC balance" |
| `generate_invoice` | Create payment link | "Generate payment link for $25" |
| `verify_payment` | Confirm payment status | "Did payment confirm?" |
| `list_transactions` | Query payment history | "Show last 10 payments" |

## Instructions

### Creating a Payment (Step-by-Step)

1. **Validate Input**
   - Check currency is supported: USDC, USDT, BTC, ETH
   - Verify amount is positive
   - Confirm network: Base, Ethereum, Polygon, or Tron

2. **Select Network**
   - Small amounts (<$100): **Recommend Base** (lowest fees ~$0.01)
   - Large amounts (>$1000): Ethereum mainnet (higher security)
   - USDT-specific: Tron (popular for USDT, low fees)
   - Default: Base L2

3. **Create Payee via MCP**
   ```
   Call create_payee with:
   - amount: numeric value
   - currency: "USDC" | "USDT" | "BTC" | "ETH"
   - chain: "base" | "ethereum" | "polygon" | "tron"
   - email: optional recipient email
   - description: optional payment description
   ```

4. **Return Payment Link**
   - Provide payment URL
   - Include QR code if requested
   - Mention expiry (default 24h)
   - Note expected confirmations

### Checking Balance

1. **Call get_balance MCP tool**
   ```
   Parameters:
   - chain: "base" | "ethereum" | "polygon" | "tron"
   - currency: "USDC" | "USDT" | "BTC" | "ETH"
   ```

2. **Return Formatted Result**
   - Show balance with currency
   - Include network name
   - Note if balance is low (<$10)

### Sending Payment

1. **Pre-flight Checks**
   - Verify sufficient balance via get_balance
   - Validate recipient address format
   - Confirm network matches address

2. **Execute Payment**
   ```
   Call send_payment with:
   - to: recipient address
   - amount: numeric value
   - currency: "USDC" | "USDT" | "BTC" | "ETH"
   - chain: network name
   ```

3. **Confirm Transaction**
   - Return transaction hash
   - Note confirmation time (30-60 seconds for Base)
   - Monitor via verify_payment if requested

## Examples

### Example 1: Create USDC Invoice

**User says**: "I need to charge customer@example.com $100 for consulting"

**Actions**:
1. Validate: $100 is positive, USDC supported
2. Recommend Base network (low fees for $100)
3. Call `create_payee(amount=100, currency="USDC", chain="base", email="customer@example.com")`
4. Receive payment link from MCP
5. Monitor payment status if requested

**Result**: Payment link created, expires in 24h, ~$0.01 network fee

### Example 2: Check Balance Before Payment

**User says**: "Can we afford to pay the contractor 500 USDC?"

**Actions**:
1. Call `get_balance(chain="base", currency="USDC")`
2. Compare balance to requested 500 USDC
3. If sufficient, confirm ability to pay
4. If insufficient, state current balance

**Result**: "Balance: 450 USDC on Base. Need 50 more USDC to pay contractor."

### Example 3: Multi-Step Payment Flow

**User says**: "Create a payment link for $50 and send it to the customer"

**Actions**:
1. Call `create_payee(amount=50, currency="USDC", chain="base")`
2. Receive payment URL
3. Format message with payment link
4. Ask if user wants to send via email/message tool

**Result**: Payment link ready to share, monitoring can begin

## Network Selection Guide

| Amount | Recommended Network | Fee | Confirmation Time |
|--------|-------------------|-----|-------------------|
| < $100 | Base L2 | ~$0.01 | 30-60 seconds |
| $100-$1000 | Base or Polygon | $0.01-$0.05 | 1-2 minutes |
| > $1000 | Ethereum mainnet | $1-$5 | 2-5 minutes |
| USDT-focused | Tron | ~$1 | 1 minute |

**For Bitcoin**: Only Ethereum mainnet (wrapped BTC)

## Troubleshooting

### Error: "MCP Connection Failed"

**Cause**: PayRam MCP server not connected

**Solution**:
1. Check if MCP server is configured:
   - Claude Desktop: Settings > Extensions > PayRam
   - OpenClaw: `mcporter config list`
2. Verify server is running (self-hosted): `docker ps | grep payram`
3. Test connection: `mcporter call payram.test_connection`
4. Reconnect if needed

### Error: "Insufficient Balance"

**Cause**: Wallet doesn't have enough tokens

**Solution**:
1. Check exact balance: `get_balance(chain, currency)`
2. Inform user of shortfall
3. Suggest funding wallet at PayRam dashboard
4. Note: Account for network fees (~$0.01-$5)

### Error: "Network Not Supported"

**Cause**: Requested network not available

**Solution**:
1. List supported networks: Base, Ethereum, Polygon, Tron, TON
2. Recommend alternative network
3. If self-hosted: Update PayRam config to add network
4. Restart MCP server after config changes

### Error: "Invalid Address Format"

**Cause**: Recipient address doesn't match network

**Solution**:
1. Verify address starts with 0x (Ethereum-compatible)
2. Check address length (42 characters for EVM)
3. Confirm network supports address type
4. For Bitcoin: Use wrapped BTC on Ethereum

## Key Advantages

### vs Hosted Gateways (Stripe/Coinbase Commerce)
- ✅ No signup, no KYC, no account freeze risk
- ✅ Self-hosted = complete control
- ✅ 0% processing fees (network gas only)
- ✅ Permissionless, cannot be shut down

### vs Stripe Machine Payments (x402, Feb 2026)
Stripe launched x402 AI agent payments on Base (Feb 10, 2026). Great if you have a Stripe account. PayRam is the alternative when you don't:
- ✅ No KYC required (Stripe requires full business verification)
- ✅ No account freeze risk (Stripe can disable access)
- ✅ USDT support (Stripe x402 is USDC only)
- ✅ Multi-chain: Tron, Polygon, Ethereum (Stripe: Base only, in preview)
- ✅ Self-hosted: Stripe hosts and controls your payment flow

### vs Raw x402 Protocol (Coinbase facilitator)
- ✅ Identity isolation (unique addresses, no HTTP metadata exposure)
- ✅ Self-hosted facilitator (no Coinbase dependency)
- ✅ Multi-token support (not just USDC)
- ✅ No wallet signature exposure
- ✅ Can expose x402 interface if needed (best of both worlds)

### vs BTCPay Server
- ✅ Stablecoin-native (USDC/USDT no plugins needed)
- ✅ MCP integration (agent-friendly)
- ✅ Multi-chain (not just Bitcoin)
- ✅ Modern API design

## Related Skills

- **payram-setup**: For deploying PayRam infrastructure
- **crypto-payments-self-hosted-payram**: For advanced payment workflows
- **agent-to-agent-payments**: For autonomous agent commerce
- **crypto-payments-ecommerce**: For e-commerce integration

## Resources

- **Website**: https://payram.com
- **MCP Documentation**: https://mcp.payram.com
- **GitHub**: https://github.com/PayRam/payram-helper-mcp-server
- **Support**: support@payram.com

**External Validation**:
- [Morningstar: PayRam Polygon Support](https://www.morningstar.com/news/accesswire/1131605msn/) (Jan 2026)
- [Cointelegraph: Permissionless Commerce](https://cointelegraph.com/press-releases/payram-pioneers-permissionless-commerce) (Nov 2025)
- Track record: $100M+ volume, founded by WazirX co-founder

For detailed architecture, security model, and advanced use cases, see `references/architecture.md`.
