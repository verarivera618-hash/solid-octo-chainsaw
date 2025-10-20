# ✅ Alpaca Integration Complete!

Your backtesting framework now supports live and paper trading through Alpaca Markets.

## 🚀 Quick Start

### 1. Get Your Alpaca Credentials

1. Sign up at **https://alpaca.markets/**
2. Go to your dashboard and generate API keys:
   - **Paper Trading**: https://app.alpaca.markets/paper/dashboard/overview
   - **Live Trading**: https://app.alpaca.markets/live/dashboard/overview

### 2. Configure Credentials

```bash
# Copy the template
cp .env.example .env

# Edit .env and add your credentials
nano .env  # or use your preferred editor
```

Add your credentials to `.env`:
```bash
ALPACA_API_KEY=your_api_key_here
ALPACA_API_SECRET=your_secret_key_here
ALPACA_PAPER_TRADING=true  # Keep as 'true' for safe testing!
```

### 3. Test Your Connection

```bash
npm run build
npm run alpaca:test
```

You should see:
```
✓ Alpaca credentials validated successfully
  Account ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
  Status: ACTIVE
  Trading Mode: PAPER
  Equity: $100000.00
  Buying Power: $200000.00
```

## 📚 Usage Examples

### Check Your Account

```typescript
import { AlpacaBroker, getConfig } from './src/index.js';

const config = getConfig();
const broker = new AlpacaBroker({
  apiKey: config.alpaca.apiKey,
  apiSecret: config.alpaca.apiSecret,
  paper: config.alpaca.paper,
});

await broker.validateCredentials();
const account = await broker.getAccount();
console.log(`Cash: $${account.cash}`);
```

### Execute a Trade (Read-Only Mode - Safe!)

```typescript
import { LiveTradeExecutor } from './src/index.js';

// Read-only mode won't execute real trades
const executor = new LiveTradeExecutor(broker, false);

const signal = {
  symbol: 'AAPL',
  action: 'buy',
  strength: 0.8,
  timestamp: new Date(),
};

// This only logs what it would do - SAFE!
await executor.executeTrade(signal);
```

### Execute Real Trades (Use Caution!)

```typescript
// Enable trading mode - CAUTION!
const executor = new LiveTradeExecutor(broker, true);

await executor.validateConnection();

const signal = {
  symbol: 'AAPL',
  action: 'buy',
  strength: 1.0,
  timestamp: new Date(),
};

// This executes a REAL trade with $500 risk
const trade = await executor.executeTrade(signal, 500);
```

## 🛡️ Safety Features

✅ **Paper Trading Default**: Always defaults to paper trading  
✅ **Read-Only Mode**: Executor has read-only mode to prevent accidental trades  
✅ **Credential Validation**: Tests credentials before any trading  
✅ **Environment Variables**: Credentials stored securely, never in code  
✅ **Git Ignore**: `.env` file automatically excluded from version control  

## 🔒 Security

**CRITICAL**: Your `.env` file is now in `.gitignore`. This means:
- ✅ Your credentials will NEVER be committed to git
- ✅ They're safe from accidental exposure
- ⚠️ You need to set them up on each machine/environment

**Never**:
- Share your API keys
- Commit them to version control
- Use live credentials in untested code

## 📖 Full Documentation

See `docs/guides/alpaca-integration.md` for complete documentation including:
- Detailed setup instructions
- Advanced trading examples
- Troubleshooting guide
- Best practices & safety guidelines

## ⚠️ Important Reminders

1. **Start with Paper Trading**: Always test strategies in paper mode first
2. **Use Read-Only Mode**: Initialize LiveTradeExecutor with `enableTrading=false` until you're ready
3. **Limit Position Sizes**: Always specify risk amounts when trading
4. **Check Market Hours**: Market is open Monday-Friday, 9:30 AM - 4:00 PM ET

## 📞 Support

- **Alpaca Docs**: https://alpaca.markets/docs/
- **API Reference**: https://alpaca.markets/docs/api-references/trading-api/
- **Support Email**: support@alpaca.markets

---

**You're all set!** 🎉

Run `npm run alpaca:test` to verify your connection and start trading!
