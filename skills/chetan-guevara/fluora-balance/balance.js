#!/usr/bin/env node
/**
 * Fluora Balance Checker
 * 
 * Check USDC balance of your Fluora wallet on Base network
 */

import { ethers } from 'ethers';
import fs from 'fs/promises';
import path from 'path';
import os from 'os';

// Base Mainnet RPC
const BASE_RPC = "https://mainnet.base.org";

// USDC contract address on Base Mainnet
const USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913";

// Minimal ERC20 ABI
const ERC20_ABI = [
  "function balanceOf(address account) view returns (uint256)",
  "function decimals() view returns (uint8)",
  "function symbol() view returns (string)"
];

const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[36m',
  red: '\x1b[31m',
  bold: '\x1b[1m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

/**
 * Get wallet address from Fluora wallets.json
 */
async function getWalletAddress() {
  const walletsPath = path.join(os.homedir(), '.fluora', 'wallets.json');
  
  try {
    const content = await fs.readFile(walletsPath, 'utf8');
    const wallets = JSON.parse(content);
    
    // Try both possible key names
    const baseWallet = wallets.USDC_BASE_MAINNET || wallets.BASE_MAINNET;
    if (!baseWallet || !baseWallet.privateKey) {
      throw new Error('Base Mainnet wallet not found in wallets.json');
    }
    
    // Derive address from private key
    const wallet = new ethers.Wallet(baseWallet.privateKey);
    return wallet.address;
    
  } catch (error) {
    if (error.code === 'ENOENT') {
      throw new Error('Fluora wallet not found. Run fluora-setup first.');
    }
    throw error;
  }
}

/**
 * Check USDC balance on Base network
 */
async function checkBalance(walletAddress) {
  try {
    log('\n💰 Checking USDC balance on Base...', 'blue');
    log(`Wallet: ${walletAddress}`, 'blue');
    log('');
    
    // Create provider
    const provider = new ethers.JsonRpcProvider(BASE_RPC);
    
    // Create contract instance
    const usdcContract = new ethers.Contract(
      USDC_ADDRESS,
      ERC20_ABI,
      provider
    );
    
    // Fetch balance + decimals
    const [balance, decimals, symbol] = await Promise.all([
      usdcContract.balanceOf(walletAddress),
      usdcContract.decimals(),
      usdcContract.symbol()
    ]);
    
    // Format balance
    const formattedBalance = ethers.formatUnits(balance, decimals);
    const balanceFloat = parseFloat(formattedBalance);
    
    // Display result
    log('═══════════════════════════════════════════', 'bold');
    if (balanceFloat > 0) {
      log(`✓ Balance: ${formattedBalance} ${symbol}`, 'green');
    } else {
      log(`Balance: ${formattedBalance} ${symbol}`, 'yellow');
      log('\n⚠️  Your wallet has no USDC.', 'yellow');
      log('To fund your wallet:', 'yellow');
      log('  1. Send USDC to the address above', 'yellow');
      log('  2. Select "Base" network (NOT Ethereum mainnet)', 'yellow');
      log('  3. Check balance on: https://basescan.org', 'blue');
    }
    log('═══════════════════════════════════════════', 'bold');
    log('');
    
    return {
      address: walletAddress,
      balance: formattedBalance,
      symbol: symbol,
      raw: balance.toString(),
      hasBalance: balanceFloat > 0
    };
    
  } catch (error) {
    log(`❌ Error checking balance: ${error.message}`, 'red');
    throw error;
  }
}

/**
 * Main function
 */
export async function getBalance(walletAddressOverride = null) {
  try {
    // Get wallet address (from file or override)
    const address = walletAddressOverride || await getWalletAddress();
    
    // Check balance
    const result = await checkBalance(address);
    
    return result;
    
  } catch (error) {
    log(`\n❌ Failed: ${error.message}`, 'red');
    
    if (error.message.includes('wallet not found')) {
      log('\n💡 To get started:', 'blue');
      log('   1. Run: node fluora-setup/setup.js', 'blue');
      log('   2. Or install globally: npm install -g fluora-mcp', 'blue');
      log('   3. Then run: npx fluora-mcp', 'blue');
    }
    
    return {
      success: false,
      error: error.message
    };
  }
}

// CLI entry point
if (import.meta.url === `file://${process.argv[1]}`) {
  const walletArg = process.argv[2];
  getBalance(walletArg);
}
