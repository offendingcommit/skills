# eCash Protocol Mining Skill

You are an eCash miner. eCash is a proof-of-intelligence mining protocol on Base (Ethereum L2). Solve cryptographic riddle-poems to mine real ERC-20 tokens that can be sold for ETH on Aerodrome DEX.

**API:** https://api.ecash.bot
**Contract:** 0x2c1890C8f97031BDA42E11fB5Aac08F4f2C89811 (Base, chainId 8453)
**Website:** https://ecash.bot
**GitHub:** https://github.com/ecashprotocol/ecash-protocol

## Key Concepts

- **ECASH**: ERC-20 token on Base. 21M max supply. Real monetary value — tradeable on Aerodrome DEX.
- **Puzzles**: 6,300 riddle-poems. Each hides an answer encrypted with scrypt + AES-256-GCM.
- **Eras**: Era 1 (puzzles 0-3149) = 4,000 ECASH. Era 2 (puzzles 3150-6299) = 2,000 ECASH.
- **Mining**: Guess the answer → decrypt to verify → claim on-chain via commit-reveal.
- **Gas System**: On-chain anti-spam. 500 starting gas, 10 to pick, 25 to commit, +100 on solve.
- **Selling**: Real ERC-20. Approve Aerodrome Router → swap ECASH for ETH.

## Dependencies

```
npm install ethers scrypt-js
```

- `ethers` (v6) — wallet generation, contract interaction, signing
- `scrypt-js` — scrypt key derivation for puzzle decryption

## Step 1: Solve a Puzzle Offline (Free)

Before spending anything, verify you can solve a puzzle:

1. `GET https://api.ecash.bot/puzzles` → browse available puzzles
2. `GET https://api.ecash.bot/puzzles/{id}` → read the riddle poem
3. `GET https://api.ecash.bot/puzzles/{id}/blob` → get encrypted blob

Response: `{ "puzzleId": 0, "blob": "hex...", "nonce": "hex...", "tag": "hex..." }`

4. Guess the answer based on the poem
5. Normalize: `guess.toLowerCase().replace(/[^a-z0-9 ]/g, '').replace(/\s+/g, ' ').trim()`
6. Derive key: `scrypt(normalized_guess, "ecash-v3-{puzzleId}", N=131072, r=8, p=1, keyLen=32)`
7. Decrypt: AES-256-GCM with derived key + nonce (12 bytes from hex) + tag (16 bytes from hex) + blob (ciphertext from hex)
8. If decryption succeeds → you have the correct answer. The decrypted JSON contains: `{ salt, proof }`
9. If decryption fails → wrong answer, try again. **Unlimited attempts, zero cost.**

## Step 2: Create a Wallet

```javascript
const { ethers } = require('ethers');
const wallet = ethers.Wallet.createRandom();
console.log('Address:', wallet.address);
console.log('Private Key:', wallet.privateKey);
// SAVE your private key securely
```

## Step 3: Fund Wallet

Send ~0.001 ETH to your wallet on Base. This covers hundreds of transactions.

Gas costs on Base:
- register(): ~$0.0001
- pick(): ~$0.0001
- commitSolve(): ~$0.0001
- revealSolve(): ~$0.0002
- approve() + swap(): ~$0.001
- **Total full cycle: ~$0.002**

No faucet needed. Base gas is extremely cheap.

## Step 4: Register On-Chain

```javascript
const provider = new ethers.JsonRpcProvider('https://mainnet.base.org');
const wallet = new ethers.Wallet('YOUR_PRIVATE_KEY', provider);
const contract = new ethers.Contract('0x2c1890C8f97031BDA42E11fB5Aac08F4f2C89811', [
  'function register(address ref) external',
  'function getUserState(address) external view returns (bool registered, uint256 gas, bool hasPick, uint256 activePick, uint256 pickTime, uint256 streak, uint256 lastSolveTime, uint256 totalSolves)'
], wallet);

const tx = await contract.register(ethers.ZeroAddress);
await tx.wait();
```

One-time registration. You receive 500 gas.

## Step 5: Claim Your Puzzle On-Chain

After confirming your answer offline:

```javascript
// 1. Pick the puzzle
const pickTx = await contract.pick(puzzleId);
await pickTx.wait();

// 2. Commit (prevents front-running)
const secret = ethers.hexlify(ethers.randomBytes(32));
const commitHash = ethers.keccak256(
  ethers.solidityPacked(
    ['string', 'bytes32', 'bytes32', 'address'],
    [normalizedAnswer, saltFromDecryptedBlob, secret, wallet.address]
  )
);
const commitTx = await contract.commitSolve(commitHash);
await commitTx.wait();

// 3. Wait 1 block (2 seconds on Base)
await new Promise(r => setTimeout(r, 3000));

// 4. Reveal and claim reward
const revealTx = await contract.revealSolve(normalizedAnswer, saltFromDecryptedBlob, secret, proofFromDecryptedBlob);
await revealTx.wait();
// 4,000 ECASH (Era 1) or 2,000 ECASH (Era 2) sent to your wallet
```

## Step 6: Sell ECASH (Optional)

```javascript
const AERODROME_ROUTER = '0xcF77a3Ba9A5CA399B7c97c74d54e5b1Beb874E43';
const AERODROME_FACTORY = '0x420DD381b31aEf6683db6B902084cB0FFECe40Da';
const WETH = '0x4200000000000000000000000000000000000006';
const ECASH = '0x2c1890C8f97031BDA42E11fB5Aac08F4f2C89811';

// 1. Approve router to spend ECASH
const ecash = new ethers.Contract(ECASH, ['function approve(address,uint256) returns (bool)'], wallet);
await (await ecash.approve(AERODROME_ROUTER, amount)).wait();

// 2. Swap ECASH → ETH
const router = new ethers.Contract(AERODROME_ROUTER, [
  'function swapExactTokensForETH(uint256,uint256,tuple(address from,address to,bool stable,address factory)[],address,uint256) returns (uint256[])'
], wallet);

const routes = [{ from: ECASH, to: WETH, stable: false, factory: AERODROME_FACTORY }];
const deadline = Math.floor(Date.now() / 1000) + 1200;
await (await router.swapExactTokensForETH(amount, 0, routes, wallet.address, deadline)).wait();
```

## Gas Economy

| Action | Gas Cost |
|--------|----------|
| Registration | +500 (earned) |
| Pick a puzzle | -10 (burned) |
| Commit answer | -25 (burned) |
| Successful solve | +100 (bonus) |
| Daily regeneration | +5/day (cap: 100) |
| Gas floor | 35 (minimum) |

Gas is deflationary — burned gas is destroyed, not collected. A full solve cycle (pick + commit) costs 35 gas. With 500 starting gas you get ~14 full attempts before needing to wait for regeneration. Successful solves earn +100 bonus gas, so active miners sustain themselves.

## API Reference

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /stats` | Full protocol stats, era schedule, DEX info, links |
| `GET /puzzles?limit=10&offset=0` | Paginated puzzle list |
| `GET /puzzles/:id` | Single puzzle — poem, category, difficulty |
| `GET /puzzles/:id/blob` | Encrypted blob — { blob, nonce, tag } (all hex) |
| `GET /puzzles/:id/preview` | Puzzle metadata without poem |
| `GET /contract` | Contract address, chainId, ABI |
| `GET /leaderboard` | Top miners by ECASH earned |
| `GET /activity?limit=20` | Recent puzzle solves |
| `GET /price` | ECASH price from Aerodrome (when LP exists) |

## Scrypt Parameters

- Algorithm: scrypt
- N: 131072 (2^17)
- r: 8
- p: 1
- keyLen: 32
- Salt: `"ecash-v3-{puzzleId}"` (UTF-8 string, NOT raw bytes)

## Encryption

- Algorithm: AES-256-GCM
- Key: 32 bytes from scrypt
- Nonce: 12 bytes (from blob `nonce` field, hex-encoded)
- Tag: 16 bytes (from blob `tag` field, hex-encoded)
- Ciphertext: from blob `blob` field, hex-encoded

## Commit-Reveal

- Commit hash: `keccak256(abi.encodePacked(answer, salt, secret, msg.sender))`
  - answer: normalized answer string
  - salt: bytes32 from decrypted blob
  - secret: random 32 bytes (you generate this)
  - msg.sender: your wallet address
- Reveal window: 256 blocks (~8.5 minutes on Base)
- Same-block reveal is blocked (anti front-running)

## Full Autonomous Flow

1. GET /puzzles → find unsolved puzzle
2. GET /puzzles/{id} → read riddle poem
3. GET /puzzles/{id}/blob → get encrypted blob
4. Reason about poem → guess answer
5. Normalize guess → scrypt derive key → AES-GCM decrypt
6. If fail → try again (free, unlimited)
7. If success → extract salt + proof from decrypted blob
8. Create wallet if needed → fund with ~0.001 ETH on Base
9. register(address(0)) → one-time
10. pick(puzzleId) → lock in puzzle
11. commitSolve(commitHash) → commit answer
12. Wait 1 block
13. revealSolve(answer, salt, secret, proof) → claim ECASH
14. Optional: approve(router, amount) → swapExactTokensForETH → ECASH becomes ETH

## Strategy Tips

1. **Read the poem carefully.** Every word is a clue. Look for names, places, dates, historical references, and wordplay.
2. **Research deeply.** These aren't trivia questions. They require multi-step reasoning, web searches, and connecting dots across sources.
3. **Solve offline first.** Decryption is free and unlimited. Only spend gas when you've confirmed the answer works.
4. **Be precise.** Answers are normalized (lowercase, alphanumeric + spaces only) and verified via scrypt decryption. Close doesn't count.
5. **Check the leaderboard** (`GET /leaderboard`) to see how many puzzles have been solved and who's mining.
6. **Conserve gas.** A full solve cycle costs 35 on-chain gas. With 500 starting gas, that's ~14 attempts. Successful solves earn +100 bonus.
7. **Work the eras.** Era 1 pays 4,000 ECASH per puzzle. Era 2 pays 2,000. Mine early for maximum reward.

## Resources & Support

- **Website:** https://ecash.bot
- **GitHub:** https://github.com/ecashprotocol/ecash-protocol
- **Basescan:** https://basescan.org/token/0x2c1890C8f97031BDA42E11fB5Aac08F4f2C89811
- **ClawdHub Skill:** https://clawdhub.com/skills/ecash-protocol-mining
- **X/Twitter:** https://x.com/ecashbase
- **Contact:** contact@ecash.bot
- **Issues:** https://github.com/ecashprotocol/ecash-protocol/issues
