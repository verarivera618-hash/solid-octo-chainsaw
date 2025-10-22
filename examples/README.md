# Usage Examples

This directory contains examples demonstrating how to use the Local Trading System.

## 📁 Files

- `README.md` - This documentation file

## 🚀 Quick Start

### TypeScript Backtesting

Run a backtest with the example strategy:

```bash
npm run build
npm start
```

### Running Tests

```bash
npm test
```

This will run:
- Portfolio management tests
- Backtesting engine tests
- Strategy implementation tests

## 📊 Example Strategy

### Simple Moving Average Crossover
```typescript
import { SimpleMovingAverageStrategy } from '../src/strategies/SimpleMovingAverageStrategy.js';
import { BacktestEngine } from '../src/core/BacktestEngine.js';
import { AlpacaDataProvider } from '../src/data/AlpacaDataProvider.js';

// Initialize strategy with parameters
const strategy = new SimpleMovingAverageStrategy(20, 50, ['AAPL']);

// Get local mock data
const dataProvider = new AlpacaDataProvider();
const startDate = new Date('2023-01-01');
const endDate = new Date('2023-12-31');
const marketData = await dataProvider.getPriceData('AAPL', startDate, endDate);

// Run backtest
const config = {
  initialCapital: 100000,
  commission: 0.001,
  slippage: 0.001
};
const engine = new BacktestEngine(config);
const results = await engine.runBacktest(strategy, new Map([['AAPL', marketData]]));

console.log('Backtest Results:', results);
```

## 🔧 Configuration

Before running examples, ensure you have:

1. **Dependencies installed** (`npm install`)
2. **Project built** (`npm run build`)

No API keys or external services required!

## 📈 Output

Backtests generate:
- **Performance metrics** (Sharpe ratio, max drawdown, win rate)
- **Trade history** with timestamps and prices
- **Equity curve** showing portfolio value over time
- **Risk metrics** and statistics

## 🎯 Next Steps

1. **Modify strategies** in `src/strategies/`
2. **Create custom data providers** for your data sources
3. **Adjust risk parameters** in the config
4. **Run backtests** with different parameters
5. **Analyze results** using the performance analyzer

## ⚠️ Important Notes

- **Local only** - All data is generated or loaded locally
- **No external APIs** - Zero dependencies on external services
- **Mock data** - Default data provider generates realistic synthetic data
- **Backtesting only** - This is a development framework, not for live trading

## 🆘 Troubleshooting

### Common Issues

1. **Build Errors**
   - Run `npm install` to install dependencies
   - Check TypeScript version compatibility
   - Clear `dist/` folder and rebuild

2. **Test Failures**
   - Ensure project is built (`npm run build`)
   - Check that tests are in `tests/` directory
   - Run tests in watch mode for debugging (`npm run test:watch`)

3. **Import Errors**
   - Use `.js` extensions in TypeScript imports (ESM)
   - Check module paths are correct
   - Verify `tsconfig.json` settings

### Getting Help

- Check the main README.md for detailed documentation
- Review the test cases in the `tests/unit/` directory
- Check TypeScript API documentation in `docs/api/`

## 📚 Additional Resources

- [Main Documentation](../README.md)
- [TypeScript API Docs](../docs/api/)
- [Test Cases](../tests/unit/)
- [Core Engine Code](../src/core/)

---

**Happy Backtesting! 🚀📈**