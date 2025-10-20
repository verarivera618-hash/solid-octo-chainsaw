# Alpaca Trading Integration Guide

This guide explains how to connect your Alpaca trading account to the backtesting framework for live or paper trading.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Getting Alpaca API Credentials](#getting-alpaca-api-credentials)
- [Configuration](#configuration)
- [Testing Your Credentials](#testing-your-credentials)
- [Usage Examples](#usage-examples)
- [Safety & Best Practices](#safety--best-practices)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

1. An Alpaca trading account (paper or live)
   - Sign up at: https://alpaca.markets/
2. Node.js and npm installed
3. This project built and dependencies installed

---

## Getting Alpaca API Credentials

### Step 1: Create an Alpaca Account
1. Visit https://alpaca.markets/
2. Sign up for a free account
3. Complete the verification process

### Step 2: Generate API Keys

#### For Paper Trading (Recommended for Testing):
1. Log in to your Alpaca account
2. Navigate to https://app.alpaca.markets/paper/dashboard/overview
3. Go to "Your API Keys" section
4. Click "Generate New Key" or "View" for existing keys
5. Copy your **API Key ID** and **Secret Key**

#### For Live Trading:
1. Log in to your Alpaca account
2. Navigate to https://app.alpaca.markets/live/dashboard/overview
3. Complete account funding and approval
4. Go to "Your API Keys" section
5. Generate and copy your live API credentials

⚠️ **IMPORTANT**: Never share your secret key or commit it to version control!

---

## Configuration

### Method 1: Using Environment Variables (Recommended)

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```bash
   # Alpaca API Credentials
   ALPACA_API_KEY=your_actual_api_key_here
   ALPACA_API_SECRET=your_actual_secret_key_here
   
   # Set to true for paper trading, false for live trading
   ALPACA_PAPER_TRADING=true
   ```

3. **Never commit the `.env` file to git!** (It's already in `.gitignore`)

### Method 2: Export in Shell

```bash
export ALPACA_API_KEY="your_api_key"
export ALPACA_API_SECRET="your_secret_key"
export ALPACA_PAPER_TRADING=true
```

---

## Testing Your Credentials

After configuration, test your connection:

```bash
npm run alpaca:test
```

This will:
- ✓ Validate your credentials
- ✓ Display account information
- ✓ Show current positions
- ✓ Check market status
- ✓ List open orders

**Expected output:**
```
============================================================
🔍 Testing Alpaca API Credentials
============================================================

Testing connection...

✓ Alpaca credentials validated successfully
  Account ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
  Status: ACTIVE
  Trading Mode: PAPER
  Equity: $100000.00
  Buying Power: $200000.00

📊 Account Details:
  Portfolio Value: $100000.00
  Cash: $100000.00
  Pattern Day Trader: No
  Day Trade Count: 0

📈 Market Status: 🟢 OPEN

📦 Current Positions: 0

📋 Open Orders: 0

============================================================
✅ Alpaca credentials are valid and working!
============================================================
```

---

## Usage Examples

### Example 1: Initialize Alpaca Broker

```typescript
import { AlpacaBroker } from './brokers/AlpacaBroker.js';
import { getConfig } from './config/index.js';

const config = getConfig();

const broker = new AlpacaBroker({
  apiKey: config.alpaca.apiKey,
  apiSecret: config.alpaca.apiSecret,
  paper: config.alpaca.paper,
});

// Validate credentials
await broker.validateCredentials();
```

### Example 2: Get Account Information

```typescript
const account = await broker.getAccount();
console.log(`Buying Power: $${account.buying_power}`);
console.log(`Portfolio Value: $${account.portfolio_value}`);
```

### Example 3: Check Current Positions

```typescript
const positions = await broker.getPositions();
positions.forEach(pos => {
  console.log(`${pos.symbol}: ${pos.quantity} shares @ $${pos.averagePrice}`);
  console.log(`  P/L: $${pos.unrealizedPL} (${pos.unrealizedPLPercent}%)`);
});
```

### Example 4: Execute a Trade (Read-Only Mode)

```typescript
import { LiveTradeExecutor } from './core/LiveTradeExecutor.js';

// Initialize in read-only mode (safe, won't execute trades)
const executor = new LiveTradeExecutor(broker, false);

const signal = {
  symbol: 'AAPL',
  action: 'buy' as const,
  strength: 0.8,
  timestamp: new Date(),
};

// This will only log what it would do, not execute
await executor.executeTrade(signal);
```

### Example 5: Execute Real Trades (Use with Caution!)

```typescript
// Enable live trading (dangerous!)
const executor = new LiveTradeExecutor(broker, true);

// Validate connection first
await executor.validateConnection();

// Check if market is open
const account = await executor.getAccountInfo();
console.log(`Available cash: $${account.cash}`);

// Execute a trade
const signal = {
  symbol: 'AAPL',
  action: 'buy' as const,
  strength: 1.0,
  timestamp: new Date(),
};

// This will execute a REAL trade!
const trade = await executor.executeTrade(signal, 1000); // Risk $1000
```

### Example 6: Using Limit Orders

```typescript
const signal = {
  symbol: 'TSLA',
  action: 'buy' as const,
  strength: 1.0,
  timestamp: new Date(),
};

// Place a limit order at $200
await executor.executeLimitTrade(signal, 200.00, 500); // Risk $500
```

### Example 7: Checking Market Status

```typescript
const isOpen = await broker.isMarketOpen();
console.log(`Market is ${isOpen ? 'OPEN' : 'CLOSED'}`);

// Get market calendar
const calendar = await broker.getCalendar();
console.log('Next 5 trading days:', calendar.slice(0, 5));
```

---

## Safety & Best Practices

### 🛡️ Security
1. **Never commit credentials to git**
   - Always use environment variables
   - Keep `.env` in `.gitignore`
   
2. **Use paper trading first**
   - Test all strategies in paper mode
   - Only switch to live after thorough testing

3. **Secure your API keys**
   - Treat them like passwords
   - Regenerate if compromised
   - Use read-only keys when possible

### ⚠️ Trading Safety
1. **Start with read-only mode**
   ```typescript
   const executor = new LiveTradeExecutor(broker, false); // Read-only
   ```

2. **Use position sizing**
   ```typescript
   // Limit risk per trade
   await executor.executeTrade(signal, 100); // Only risk $100
   ```

3. **Check market status**
   ```typescript
   const isOpen = await broker.isMarketOpen();
   if (!isOpen) {
     console.log('Market is closed, skipping trade');
     return;
   }
   ```

4. **Implement circuit breakers**
   ```typescript
   const account = await broker.getAccount();
   const maxDailyLoss = 0.02; // 2% max daily loss
   const dailyLoss = (parseFloat(account.equity) - parseFloat(account.last_equity)) / parseFloat(account.last_equity);
   
   if (dailyLoss < -maxDailyLoss) {
     console.warn('Daily loss limit reached, stopping trading');
     return;
   }
   ```

### 📊 Monitoring
1. **Log all trades**
2. **Monitor positions regularly**
3. **Set up alerts for unusual activity**
4. **Review trading performance daily**

---

## Troubleshooting

### Error: "Alpaca API credentials are required"
**Solution**: Set `ALPACA_API_KEY` and `ALPACA_API_SECRET` environment variables.

### Error: "Failed to validate Alpaca credentials: 401"
**Causes**:
- Incorrect API key or secret
- Using paper credentials with live URL (or vice versa)
- API keys have been revoked

**Solution**: 
1. Verify your credentials in the Alpaca dashboard
2. Ensure you're using the correct paper/live mode
3. Regenerate your API keys if needed

### Error: "Market is closed"
**Solution**: This is normal outside trading hours. The US stock market is open Monday-Friday, 9:30 AM - 4:00 PM ET (excluding holidays).

### Error: "Insufficient buying power"
**Solution**: 
- Check your account balance
- Reduce position size
- Close existing positions to free up capital

### Trades not executing
**Checklist**:
1. Is `enableTrading` set to `true`?
2. Is the market open?
3. Do you have sufficient buying power?
4. Is the symbol valid and tradeable?

---

## Advanced Configuration

### Custom Base URL
```bash
# For paper trading
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# For live trading
ALPACA_BASE_URL=https://api.alpaca.markets
```

### Programmatic Configuration
```typescript
const broker = new AlpacaBroker({
  apiKey: 'your_key',
  apiSecret: 'your_secret',
  paper: true,
  baseUrl: 'https://paper-api.alpaca.markets',
});
```

---

## Additional Resources

- **Alpaca Documentation**: https://alpaca.markets/docs/
- **API Reference**: https://alpaca.markets/docs/api-references/trading-api/
- **Market Data**: https://alpaca.markets/docs/market-data/
- **Support**: support@alpaca.markets

---

## Disclaimer

⚠️ **Trading involves risk. This software is provided as-is without any guarantees.**

- Past performance does not guarantee future results
- You can lose money trading
- Always test strategies thoroughly in paper trading first
- Understand the risks before trading with real money
- Comply with all applicable trading regulations

**By using this integration, you acknowledge these risks and agree that you are solely responsible for your trading decisions.**
