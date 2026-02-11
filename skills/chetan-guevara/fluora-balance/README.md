# Fluora Balance Checker

💰 **Quick USDC balance checks for your Fluora wallet on Base network**

Simple, fast tool to check your wallet balance before making service purchases on the Fluora marketplace.

## Quick Start

```bash
# Install dependencies
npm install

# Check your balance
node balance.js

# Check specific address
node balance.js 0x1234...
```

## What It Does

Checks USDC balance of your Fluora wallet:
1. ✅ Reads wallet from `~/.fluora/wallets.json`
2. ✅ Derives address from private key
3. ✅ Queries Base network for USDC balance
4. ✅ Displays formatted result

## Example Output

```
💰 Checking USDC balance on Base...
Wallet: 0x7DC445b40719ab48209017f61e23D4c6D771744E

═══════════════════════════════════════════
✓ Balance: 4.85 USDC
═══════════════════════════════════════════
```

## Use Cases

### 1. Before Service Purchase
```bash
node balance.js  # Check if you have enough
```

### 2. Budget Monitoring
```bash
# Daily check
node balance.js > balance-$(date +%Y%m%d).log
```

### 3. Low Balance Alert
```javascript
import { getBalance } from './balance.js';

const result = await getBalance();
if (parseFloat(result.balance) < 5) {
  console.warn('⚠️  Low balance!');
}
```

### 4. Multiple Wallets
```bash
node balance.js 0xWallet1...
node balance.js 0xWallet2...
```

## API Usage

```javascript
import { getBalance } from './balance.js';

// Your Fluora wallet (from ~/.fluora/wallets.json)
const result = await getBalance();

// Specific address
const result = await getBalance('0x...');

// Result object
{
  address: '0x...',
  balance: '4.85',      // Formatted
  symbol: 'USDC',
  raw: '4850000',       // Raw wei value
  hasBalance: true      // Boolean
}
```

## Prerequisites

- **Node.js 18+**
- **Fluora wallet** - Run `fluora-setup` first if you haven't

## Installation

```bash
cd fluora-balance
npm install
```

## Network Info

- **Network**: Base (Coinbase L2)
- **Token**: USDC
- **Contract**: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`
- **RPC**: https://mainnet.base.org
- **Explorer**: https://basescan.org

## Troubleshooting

### "Fluora wallet not found"

Run setup first:
```bash
cd ../fluora-setup
node setup.js
```

### Balance shows 0 after funding

1. Wait 1-2 minutes (transaction pending)
2. Check network: Must be **Base** (not Ethereum)
3. Check token: Must be **USDC** (not ETH)
4. Verify on BaseScan: `https://basescan.org/address/YOUR_ADDRESS`

### Network errors

- Check internet connection
- Base RPC may be temporarily down
- Try again in a few seconds

## Cost

- **Free** - Read-only queries
- **No gas fees** - Only reads data
- **No API key needed** - Uses public RPC

## Security

✅ **Safe to use:**
- Only reads from wallet file
- Private key never leaves your machine
- No transactions sent

⚠️ **Keep secure:**
- Protect `~/.fluora/wallets.json` (chmod 600)
- Never share your private key

## Integration

Part of the Fluora ecosystem:

1. **fluora-setup** - Create wallet
2. **fluora-balance** (this) - Check balance ←
3. **fluora-skill** - Use services
4. **workflow-to-monetized-mcp** - Build services

## Performance

- **Query time**: 200-500ms
- **Rate limits**: None
- **Caching**: Not needed

## Resources

- Fluora: https://fluora.ai
- Base: https://base.org
- BaseScan: https://basescan.org
- USDC: https://www.circle.com/en/usdc

## License

MIT - See LICENSE file
