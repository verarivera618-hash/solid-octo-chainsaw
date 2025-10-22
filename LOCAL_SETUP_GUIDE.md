# 🚀 Local Trading System - Quick Setup Guide

## ✅ No External Dependencies Required!

This system now operates **100% locally** with **zero external API subscriptions**.

## 📦 Installation

```bash
# 1. Install TypeScript dependencies
npm install

# 2. Install Python dependencies (optional)
pip install -r requirements.txt

# 3. Build the project
npm run build
```

## 🧪 Verify Installation

```bash
# Run all tests
npm test

# Expected output:
# Test Suites: 3 passed, 3 total
# Tests:       19 passed, 19 total
```

## 🎯 Quick Start

### Running a Backtest

```typescript
import { BacktestEngine } from './src/core/BacktestEngine.js';
import { SimpleMovingAverageStrategy } from './src/strategies/SimpleMovingAverageStrategy.js';
import { AlpacaDataProvider } from './src/data/AlpacaDataProvider.js';

// 1. Initialize components
const strategy = new SimpleMovingAverageStrategy(20, 50, ['AAPL']);
const dataProvider = new AlpacaDataProvider(); // Uses local mock data

// 2. Get data (generated locally)
const startDate = new Date('2023-01-01');
const endDate = new Date('2023-12-31');
const marketData = await dataProvider.getPriceData('AAPL', startDate, endDate);

// 3. Configure backtest
const config = {
  initialCapital: 100000,
  commission: 0.001,
  slippage: 0.001
};

// 4. Run backtest
const engine = new BacktestEngine(config);
const results = await engine.runBacktest(
  strategy, 
  new Map([['AAPL', marketData]])
);

// 5. View results
console.log('Sharpe Ratio:', results.sharpeRatio);
console.log('Max Drawdown:', results.maxDrawdown);
console.log('Total Return:', results.totalReturn);
```

## 📂 Project Structure

```
/workspace/
├── src/
│   ├── core/              # Backtesting engine
│   │   ├── BacktestEngine.ts
│   │   ├── Portfolio.ts
│   │   └── TradeExecutor.ts
│   ├── strategies/        # Trading strategies
│   │   └── SimpleMovingAverageStrategy.ts
│   ├── data/              # Data providers (all local)
│   │   ├── AlpacaDataProvider.ts (mock data)
│   │   └── YahooDataProvider.ts (mock data)
│   ├── analysis/          # Performance analysis
│   │   └── PerformanceAnalyzer.ts
│   ├── types/             # TypeScript types
│   ├── config.py          # Python config (local only)
│   └── logger.py          # Logging utilities
├── tests/
│   └── unit/              # Unit tests
├── examples/              # Usage examples
├── dist/                  # Compiled output
└── docs/                  # Documentation
```

## 🔧 Configuration

### Optional: Environment Variables

Create a `.env` file (no API keys needed):

```env
# Trading Configuration (all local)
DEFAULT_STRATEGY=momentum
PAPER_TRADING=true
MAX_POSITION_SIZE=0.1
RISK_TOLERANCE=0.02

# Data Configuration
USE_MOCK_DATA=true
DATA_DIRECTORY=./data
LOG_LEVEL=INFO
```

## 🎨 Creating Custom Strategies

```typescript
import type { Strategy, PriceData, Signal } from './src/types/index.js';

export class MyCustomStrategy implements Strategy {
  name = 'My Custom Strategy';
  description = 'Description here';
  parameters = { /* your parameters */ };
  
  generateSignals(data: PriceData[]): Signal[] {
    // Your strategy logic
    const signals: Signal[] = [];
    // ... analyze data and generate signals
    return signals;
  }
  
  validate(): boolean {
    // Validate strategy configuration
    return true;
  }
}
```

## 📊 Available Features

### Core Features
- ✅ **Backtesting Engine** - Fast, accurate strategy testing
- ✅ **Portfolio Management** - Position tracking and P&L
- ✅ **Trade Execution Simulation** - Realistic order fills with commissions/slippage
- ✅ **Performance Analysis** - Sharpe ratio, max drawdown, win rate, etc.
- ✅ **Mock Data Generation** - Realistic OHLCV data without APIs

### Data Providers
- ✅ **Local Mock Data** - Generate realistic market data
- ✅ **CSV Import** - Load your own historical data (easy to add)
- ✅ **Custom Providers** - Implement your own data sources

### Strategies
- ✅ **Moving Average Crossover** - Example strategy included
- ✅ **Custom Strategies** - Easy to implement your own

## 🧪 Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run specific test file
npm test Portfolio.test.ts
```

## 🐛 Troubleshooting

### Build Errors
```bash
# Clean and rebuild
rm -rf dist/
npm run build
```

### Test Failures
```bash
# Make sure project is built
npm run build
npm test
```

### TypeScript Errors
```bash
# Check TypeScript version
npx tsc --version

# Clean node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📚 Documentation

- **Main README**: [README.md](./README.md)
- **Changes Summary**: [CHANGES_SUMMARY.md](./CHANGES_SUMMARY.md)
- **API Docs**: [docs/api/](./docs/api/)
- **Examples**: [examples/README.md](./examples/README.md)

## 🎉 What's Different?

### ❌ Removed (External Dependencies)
- Perplexity API (required subscription)
- Alpaca Trading API (required account)
- External data streaming
- Cloud services
- Network requirements

### ✅ Kept (Local Operation)
- Complete backtesting framework
- Portfolio management
- Strategy development tools
- Performance analysis
- All core functionality
- Full test suite

## 💡 Use Cases

Perfect for:
- 📖 **Learning** - Study algorithmic trading without costs
- 🔬 **Research** - Test strategies with realistic data
- 🛠️ **Development** - Build and debug strategies locally
- 🎓 **Education** - Teach trading concepts
- 🔒 **Privacy** - Keep all data on your machine

## 🚫 Not Included

This is a **backtesting and development framework**, not a live trading system:
- ❌ No live trading
- ❌ No real market data feeds
- ❌ No broker integration
- ❌ No cloud services

Use this for **strategy development and testing** only.

## 📈 Next Steps

1. ✅ Install dependencies (`npm install`)
2. ✅ Build project (`npm run build`)
3. ✅ Run tests (`npm test`)
4. 📊 Create your own strategy
5. 🧪 Backtest with local data
6. 📉 Analyze results
7. 🔄 Iterate and improve!

## 🆘 Support

- Check [README.md](./README.md) for detailed docs
- Review test files in [tests/unit/](./tests/unit/)
- Read the code - it's well-commented!

---

**🎊 Enjoy 100% local trading system development!**

No subscriptions. No external APIs. Full privacy. Complete control.
