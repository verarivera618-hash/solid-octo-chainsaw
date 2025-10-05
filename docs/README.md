# Solid Octo Chainsaw - Backtesting Framework

A comprehensive, production-ready backtesting framework for trading strategy development and analysis.

## 🚀 Quick Start

```typescript
import { BacktestEngine, SimpleMovingAverageStrategy, YahooDataProvider } from 'solid-octo-chainsaw';

// Create backtest configuration
const config = {
  startDate: new Date('2020-01-01'),
  endDate: new Date('2023-12-31'),
  initialCapital: 100000,
  commission: 0.001,
  slippage: 0.0005,
  symbols: ['AAPL', 'GOOGL', 'MSFT']
};

// Initialize components
const engine = new BacktestEngine(config);
const strategy = new SimpleMovingAverageStrategy(20, 50, config.symbols);
const dataProvider = new YahooDataProvider();

// Fetch market data
const marketData = new Map();
for (const symbol of config.symbols) {
  const data = await dataProvider.getPriceData(symbol, config.startDate, config.endDate);
  marketData.set(symbol, data);
}

// Run backtest
const result = await engine.runBacktest(strategy, marketData);

console.log(`Total Return: ${(result.totalReturn * 100).toFixed(2)}%`);
console.log(`Sharpe Ratio: ${result.sharpeRatio.toFixed(2)}`);
console.log(`Max Drawdown: ${(result.maxDrawdown * 100).toFixed(2)}%`);
```

## 📁 Architecture

### Core Components

- **BacktestEngine**: Main orchestrator for running backtests
- **Portfolio**: Manages positions, cash, and portfolio value
- **TradeExecutor**: Handles trade simulation with fees and slippage
- **PerformanceAnalyzer**: Calculates comprehensive performance metrics

### Strategy System

- **Strategy Interface**: Standardized contract for all trading strategies
- **Signal Generation**: Clear buy/sell/hold signals with confidence levels
- **Parameter Validation**: Built-in strategy validation and error handling

### Data Management

- **DataProvider Interface**: Pluggable data sources
- **PriceData Structure**: Standardized market data format
- **Historical Data**: Efficient data storage and retrieval

## 🧪 Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Generate coverage report
npm run test:coverage
```

## 📊 Performance Metrics

The framework calculates comprehensive performance metrics:

- **Returns**: Total and annualized returns
- **Risk Metrics**: Sharpe ratio, maximum drawdown
- **Trade Analysis**: Win rate, profit factor, average win/loss
- **Portfolio Tracking**: Equity curve, position tracking

## 🔧 Development

```bash
# Install dependencies
npm install

# Build the project
npm run build

# Run in development mode
npm run dev

# Lint and format code
npm run lint
npm run format
```

## 📚 Documentation

- [API Reference](./api/README.md) - Complete API documentation
- [Strategy Development Guide](./guides/strategy-development.md) - How to create custom strategies
- [Examples](./examples/) - Real-world usage examples