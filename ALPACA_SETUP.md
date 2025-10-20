# Alpaca Integration Setup Guide

This guide will help you set up and run the backtesting system with your Alpaca credentials for live market data and trading capabilities.

## 🚀 Quick Start

### 1. Get Your Alpaca API Keys

1. Go to [Alpaca Markets](https://alpaca.markets/) and create an account
2. Navigate to your [Paper Trading Dashboard](https://app.alpaca.markets/paper/dashboard/overview)
3. Generate your API keys:
   - Click on "View" next to "Your API Keys"
   - Copy your **API Key ID** and **Secret Key**

⚠️ **Important**: Start with paper trading keys for testing. Never use live trading keys until you're confident in your setup.

### 2. Configure Your Credentials

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and add your credentials:
   ```bash
   # Replace with your actual API keys
   ALPACA_API_KEY=your_api_key_here
   ALPACA_SECRET_KEY=your_secret_key_here
   ALPACA_BASE_URL=https://paper-api.alpaca.markets
   ALPACA_DRY_RUN=true
   ```

### 3. Test Your Connection

Run the simple test script to verify your credentials:

```bash
node test-alpaca.js
```

You should see output like:
```
🚀 Testing Alpaca API connection...
📊 Using PAPER trading environment
✅ Account access successful!
💰 Account equity: $100000.00
💵 Buying power: $200000.00
🎉 All tests completed successfully!
```

### 4. Install Dependencies

```bash
npm install
```

### 5. Build and Run

```bash
# Build the TypeScript project
npm run build

# Run the example
npm start
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ALPACA_API_KEY` | Your Alpaca API key | Required |
| `ALPACA_SECRET_KEY` | Your Alpaca secret key | Required |
| `ALPACA_BASE_URL` | API endpoint URL | `https://paper-api.alpaca.markets` |
| `ALPACA_DRY_RUN` | Enable dry run mode (no real trades) | `true` |

### Trading Environments

- **Paper Trading** (Recommended for testing):
  ```
  ALPACA_BASE_URL=https://paper-api.alpaca.markets
  ```

- **Live Trading** (Use with caution):
  ```
  ALPACA_BASE_URL=https://api.alpaca.markets
  ```

## 📊 Features

### 1. Real Market Data
- Fetch historical price data from Alpaca
- Get real-time quotes and market data
- Support for multiple timeframes

### 2. Live Trading Capabilities
- Execute buy/sell orders through Alpaca
- Monitor positions and account status
- Order management and tracking

### 3. Backtesting with Real Data
- Run backtests using actual historical market data
- Compare strategies with real market conditions
- Analyze performance with accurate data

## 🛡️ Safety Features

### Dry Run Mode
By default, the system runs in "dry run" mode, which means:
- ✅ All API calls work normally
- ✅ Market data is fetched
- ✅ Strategies generate signals
- ❌ **No actual trades are executed**

To enable live trading, set `ALPACA_DRY_RUN=false` in your `.env` file.

### Paper Trading
Even with dry run disabled, using paper trading credentials ensures:
- ✅ Full trading functionality
- ✅ Real market data
- ❌ **No real money at risk**

## 📈 Usage Examples

### Basic Backtest with Alpaca Data

```typescript
import { AlpacaDataProvider, BacktestEngine, SimpleMovingAverageStrategy } from './src/index.js';

const dataProvider = new AlpacaDataProvider(
  process.env.ALPACA_API_KEY,
  process.env.ALPACA_SECRET_KEY
);

const strategy = new SimpleMovingAverageStrategy(20, 50, ['AAPL', 'GOOGL']);
const engine = new BacktestEngine(config);

// Fetch real market data
const marketData = new Map();
const data = await dataProvider.getPriceData('AAPL', startDate, endDate);
marketData.set('AAPL', data);

// Run backtest
const results = await engine.runBacktest(strategy, marketData);
```

### Live Trading Setup

```typescript
import { AlpacaTradeExecutor } from './src/index.js';

const executor = new AlpacaTradeExecutor(
  process.env.ALPACA_API_KEY,
  process.env.ALPACA_SECRET_KEY,
  process.env.ALPACA_BASE_URL,
  true // dry run mode
);

// Execute a trade signal
const trade = await executor.executeTrade(signal, position, availableCash);
```

## 🔍 Troubleshooting

### Common Issues

1. **401 Unauthorized Error**
   - Check your API keys are correct
   - Verify you're using the right environment (paper vs live)
   - Ensure your API keys are active

2. **Market Data Access Issues**
   - Some account types have limited market data access
   - This is normal and doesn't affect basic functionality

3. **TypeScript Compilation Errors**
   - Run `npm run build` to check for errors
   - Use the JavaScript test script (`node test-alpaca.js`) for quick testing

### Getting Help

1. Check the [Alpaca API Documentation](https://alpaca.markets/docs/)
2. Verify your account status in the [Alpaca Dashboard](https://app.alpaca.markets/)
3. Review the error messages in the console output

## ⚠️ Important Warnings

1. **Always start with paper trading** - Never use live credentials until you're confident
2. **Test thoroughly** - Run extensive backtests before any live trading
3. **Monitor your trades** - Keep track of all executed orders
4. **Understand the risks** - Trading involves risk of loss
5. **Follow regulations** - Ensure compliance with trading regulations in your jurisdiction

## 🎯 Next Steps

1. ✅ Set up your Alpaca credentials
2. ✅ Test the connection
3. ✅ Run a simple backtest with real data
4. ✅ Develop and test your trading strategies
5. ⚠️ Only then consider live trading (with paper money first!)

---

**Remember**: This system is for educational and research purposes. Always understand the risks involved in trading and never risk more than you can afford to lose.