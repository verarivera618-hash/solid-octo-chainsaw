# 🚀 Alpaca Integration Ready!

Your backtesting system is now configured to work with Alpaca Markets! Here's how to get started:

## ✅ What's Been Set Up

1. **Alpaca Data Provider** (`src/data/AlpacaDataProvider.ts`)
   - Fetches real-time and historical market data
   - Manages account information and positions
   - Handles order placement and cancellation

2. **Alpaca Trade Executor** (`src/core/AlpacaTradeExecutor.ts`)
   - Executes live trades through Alpaca API
   - Manages positions and orders
   - Checks market hours

3. **Configuration Integration**
   - Alpaca credentials are managed through environment variables
   - Automatic switching between paper and live trading
   - Fallback to Yahoo Finance if Alpaca not configured

## 🔐 Setting Up Your Alpaca Credentials

### Step 1: Get Your API Keys

1. **Sign up for Alpaca** (if you haven't already):
   - Go to https://app.alpaca.markets/
   - Create a free account
   - Verify your email

2. **Get Paper Trading Keys** (recommended for testing):
   - Log into your Alpaca account
   - Navigate to the "Paper Trading" section
   - Click on "View" under API Keys
   - Generate new API keys if needed
   - Copy your API Key ID and Secret Key

3. **For Live Trading** (use with extreme caution):
   - Complete account verification
   - Fund your account
   - Navigate to "Live Trading" section
   - Generate API keys

### Step 2: Configure Your Environment

Edit the `.env` file in the project root:

```bash
# Edit the .env file
nano .env
# or
vim .env
# or use any text editor
```

Replace the placeholder values with your actual credentials:

```env
ALPACA_API_KEY=PKxxxxxxxxxxxxx
ALPACA_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ALPACA_ENVIRONMENT=paper  # Use 'paper' for testing, 'live' for real trading
```

### Step 3: Test Your Connection

Run the test script to verify everything is working:

```bash
# Using npx and tsx (recommended)
npx tsx test-alpaca-connection.ts

# Or if you prefer using node after building
npm run build
node dist/../test-alpaca-connection.js
```

## 📊 What You Can Do Now

### 1. Fetch Real Market Data
```typescript
import { AlpacaDataProvider } from './src/data/AlpacaDataProvider.js';

const alpaca = new AlpacaDataProvider();
const data = await alpaca.getPriceData('AAPL', startDate, endDate);
```

### 2. Check Account Status
```typescript
const account = await alpaca.getAccountInfo();
console.log(`Buying Power: $${account.buying_power}`);
```

### 3. Execute Paper Trades
```typescript
import { AlpacaTradeExecutor } from './src/core/AlpacaTradeExecutor.js';

const executor = new AlpacaTradeExecutor(0.001, 0.0005);
// Your trading logic here
```

### 4. Monitor Positions
```typescript
const positions = await alpaca.getPositions();
positions.forEach(pos => {
  console.log(`${pos.symbol}: ${pos.qty} shares`);
});
```

## ⚠️ Important Safety Notes

1. **Always Start with Paper Trading**
   - Test your strategies thoroughly in paper mode
   - Verify your logic works as expected
   - Monitor for at least a week before considering live trading

2. **API Rate Limits**
   - Alpaca has rate limits: 200 requests/minute for most endpoints
   - The system handles this gracefully but be aware when running high-frequency strategies

3. **Security Best Practices**
   - Never commit `.env` file to version control
   - Keep your API keys secret
   - Use paper trading for all testing
   - Set up stop-losses and position limits

4. **Live Trading Checklist** (if you decide to go live):
   - [ ] Tested strategy for at least 2 weeks in paper mode
   - [ ] Verified positive returns in paper trading
   - [ ] Set maximum position sizes
   - [ ] Implemented stop-loss logic
   - [ ] Have monitoring and alerting set up
   - [ ] Started with small amounts
   - [ ] Understood all risks involved

## 🔧 Troubleshooting

### Connection Test Fails
```bash
# Check if credentials are set
cat .env | grep ALPACA

# Verify they're not placeholder values
# Should NOT see "your_api_key_here"
```

### API Errors
- **401 Unauthorized**: Check your API keys are correct
- **403 Forbidden**: Verify you're using the right environment (paper vs live)
- **429 Too Many Requests**: You've hit rate limits, slow down requests

### No Market Data
- Check if market is open: Markets are typically open Mon-Fri 9:30 AM - 4:00 PM ET
- Verify the symbol exists and is tradeable
- Check your Alpaca subscription level

## 📚 Next Steps

1. **Run the connection test** to verify setup:
   ```bash
   npx tsx test-alpaca-connection.ts
   ```

2. **Try fetching some market data** for your favorite stocks

3. **Run a backtest** using real Alpaca historical data

4. **Start paper trading** with a simple strategy

5. **Monitor and refine** your strategies based on paper trading results

## 🎉 Success Indicators

When you run the test script successfully, you should see:
- ✅ API connection confirmed
- ✅ Account information retrieved
- ✅ Current positions listed (if any)
- ✅ Recent orders shown (if any)
- ✅ Sample market data fetched
- ✅ Market hours displayed

## 📖 Resources

- [Alpaca Documentation](https://docs.alpaca.markets/)
- [Alpaca API Reference](https://docs.alpaca.markets/reference/)
- [Market Data Documentation](https://docs.alpaca.markets/docs/market-data/)
- [Trading Documentation](https://docs.alpaca.markets/docs/trading/)
- [Paper Trading Guide](https://docs.alpaca.markets/docs/paper-trading/)

---

**Remember**: Trading involves risk. Always start with paper trading and never invest more than you can afford to lose. This system is for educational purposes and should be thoroughly tested before any real money is involved.