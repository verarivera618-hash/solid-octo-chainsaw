# Trading Strategy Backtesting Framework

An advanced backtesting framework for trading strategy prediction and analysis, now with **Alpaca Markets integration** for live market data and trading capabilities.

## 🚀 Features

- **Real Market Data**: Fetch historical and live data from Alpaca Markets
- **Live Trading**: Execute trades through Alpaca's API (paper and live trading)
- **Strategy Backtesting**: Test your strategies with real market data
- **Risk Management**: Built-in safety features and dry-run mode
- **Performance Analysis**: Comprehensive trading performance metrics

## 🏁 Quick Start with Alpaca

1. **Get your Alpaca API keys** from [Alpaca Markets](https://app.alpaca.markets/paper/dashboard/overview)
2. **Set up your credentials**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```
3. **Test your connection**:
   ```bash
   node test-alpaca.js
   ```
4. **Install and run**:
   ```bash
   npm install
   npm run build
   npm start
   ```

## 📖 Documentation

- [**Alpaca Setup Guide**](./ALPACA_SETUP.md) - Complete setup instructions
- [Strategy Development Guide](./docs/guides/strategy-development.md)
- [API Documentation](./docs/api/README.md)

## ⚠️ Safety First

This system includes multiple safety features:
- **Dry run mode** by default (no real trades)
- **Paper trading** environment for testing
- **Comprehensive logging** and monitoring

**Always start with paper trading and never risk more than you can afford to lose.** 
