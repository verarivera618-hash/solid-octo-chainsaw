# Local Trading System & Backtesting Framework

A fully local trading system with advanced backtesting capabilities. **No external API subscriptions required** - operates entirely on your local machine with mock data generation or local data files.

## 🚀 Overview

This system provides:
- **Local Backtesting Framework** (TypeScript) - Fast, reliable strategy testing
- **Mock Data Generation** - Realistic market data without external APIs
- **Portfolio Management** - Track positions and performance locally
- **Strategy Development** - Create and test trading strategies
- **Performance Analysis** - Comprehensive metrics and reporting

## 🏗️ Architecture

```
Local Data → Strategy Engine → Backtest → Analysis → Results
    ↓            ↓              ↓          ↓         ↓
Mock/CSV → Signal Gen → Trade Sim → Metrics → Reports (Local)
```

## 📋 Features

### Data Sources (100% Local)
- **Mock Data Generation**: Realistic OHLCV data generated locally
- **CSV Import**: Load your own historical data
- **Customizable Parameters**: Control volatility, trends, and patterns
- **No API Keys Required**: Zero external dependencies

### Trading Capabilities
- **Multi-strategy Support**: Momentum, mean reversion, breakout, and custom strategies
- **Backtesting Framework**: Fast historical strategy validation
- **Risk Management**: Position sizing, stop-loss, take-profit, and drawdown limits
- **Portfolio Tracking**: Real-time position and P&L monitoring
- **Performance Metrics**: Sharpe ratio, max drawdown, win rate, and more

### Local Development
- **TypeScript Core**: Type-safe, fast backtesting engine
- **Python Utilities**: Data processing and analysis tools
- **No Network Required**: Run entirely offline
- **Full Control**: All code and data on your machine
- **Easy Testing**: Built-in test framework

## 🛠️ Installation

### Prerequisites
- Node.js 18+ (for TypeScript backtesting)
- Python 3.11+ (for data utilities)
- No API keys or subscriptions needed!

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd local-trading-system
```

2. **Install TypeScript dependencies**
```bash
npm install
```

3. **Install Python dependencies (optional)**
```bash
pip install -r requirements.txt
```

4. **Build the project**
```bash
npm run build
```

5. **Run tests**
```bash
npm test
```

## 🔧 Configuration

### Environment Variables (Optional)

Create a `.env` file for custom settings:

```env
# Trading Configuration (all local)
DEFAULT_STRATEGY=momentum
PAPER_TRADING=true
MAX_POSITION_SIZE=0.1  # 10% of portfolio per position
RISK_TOLERANCE=0.02    # 2% stop loss

# Data Configuration
USE_MOCK_DATA=true
DATA_DIRECTORY=./data
LOG_LEVEL=INFO
```

**No API keys required!** Everything runs locally.

### Project Structure

```
/workspace/
├── src/                    # Source code
│   ├── core/              # TypeScript backtesting engine
│   ├── strategies/        # Trading strategies
│   ├── analysis/          # Performance analysis
│   ├── data/              # Data providers (all local)
│   ├── types/             # TypeScript types
│   ├── config.py          # Python configuration
│   └── logger.py          # Logging utilities
├── examples/              # Usage examples
├── tests/                 # Test suites
├── dist/                  # Compiled output
└── docs/                  # Documentation
```

## 🚀 Usage

### Basic Usage

1. **Build the project**
```bash
npm run build
```

2. **Run a basic backtest**
```bash
npm start
```

3. **Run tests**
```bash
npm test
```

4. **Watch mode (development)**
```bash
npm run dev
```

### Advanced Usage

#### Creating a Custom Strategy
```typescript
import { Strategy, PriceData, Signal } from './src/types/index.js';

class MyCustomStrategy implements Strategy {
  name = 'My Custom Strategy';
  
  generateSignals(data: PriceData[]): Signal[] {
    // Your strategy logic here
    return signals;
  }
  
  validate(): boolean {
    return true;
  }
}
```

#### Running a Backtest
```typescript
import { BacktestEngine } from './src/core/BacktestEngine.js';
import { AlpacaDataProvider } from './src/data/AlpacaDataProvider.js';

// Initialize components
const dataProvider = new AlpacaDataProvider(); // Uses local mock data
const config = {
  initialCapital: 100000,
  commission: 0.001,
  slippage: 0.001
};

// Run backtest
const engine = new BacktestEngine(config);
const marketData = await dataProvider.getPriceData('AAPL', startDate, endDate);
const results = await engine.runBacktest(strategy, new Map([['AAPL', marketData]]));

console.log(results);
```

### Using Local Data

1. **Mock Data (Default)**: Automatically generated realistic price data
```typescript
const provider = new AlpacaDataProvider(); // Automatically uses mock data
```

2. **Custom CSV Data**: Load your own historical data
```python
import pandas as pd
data = pd.read_csv('./data/my_data.csv')
```

## 📊 Core Components

### TypeScript Backtesting Framework

#### Core Modules
- `BacktestEngine.ts`: Main backtesting engine
- `Portfolio.ts`: Position and cash management
- `TradeExecutor.ts`: Order simulation with commissions/slippage
- `PerformanceAnalyzer.ts`: Calculate metrics and generate reports

#### Data Providers (All Local)
- `AlpacaDataProvider.ts`: Mock data generator (no external calls)
- `YahooDataProvider.ts`: Local data provider
- Custom providers: Easy to implement your own

#### Strategy Framework
- `SimpleMovingAverageStrategy.ts`: Example strategy
- Easy to extend with your own strategies
- Type-safe interfaces for signals and positions

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration

# Run with coverage
pytest --cov=src
```

### Test Structure
- `tests/test_perplexity_client.py`: Perplexity API client tests
- `tests/test_alpaca_client.py`: Alpaca trading client tests
- `tests/test_prompt_generator.py`: Prompt generation tests
- `tests/test_integration.py`: End-to-end workflow tests

## 📈 Performance Monitoring

### Key Metrics
- **Sharpe Ratio**: Target > 1.5
- **Maximum Drawdown**: Target < 10%
- **Win Rate**: Target > 55%
- **Profit Factor**: Target > 1.3

### Monitoring Tools
- Real-time P&L tracking
- Risk-adjusted return calculations
- Portfolio heat mapping
- Performance attribution analysis

## 🔒 Security & Risk Management

### Security Features
- Environment variable configuration
- No hardcoded API keys
- Secure credential management
- Paper trading by default

### Risk Controls
- Position size limits
- Daily loss limits
- Maximum drawdown controls
- Sector concentration limits
- Correlation-based position limits

## 🚨 Important Notes

### Local Operation
- **No internet required**: All operations run locally
- **No subscriptions**: Zero external API dependencies
- **Full privacy**: Your data never leaves your machine
- **Open source**: Modify and extend as needed

### Development Guidelines
- **Test thoroughly**: Use the built-in test framework
- **Version control**: All changes tracked in git
- **Type safety**: TypeScript ensures code quality
- **Performance**: Fast backtests with local data

## 📚 Documentation

### Local Resources
- `docs/api/`: TypeScript API documentation
- `docs/guides/`: Usage guides and tutorials
- `examples/`: Working code examples
- `tests/`: Test cases showing usage patterns

### Key Concepts
- **Backtesting**: Simulate strategies on historical data
- **Mock Data**: Realistic synthetic market data
- **Risk Management**: Position sizing and stop losses
- **Performance Metrics**: Sharpe ratio, max drawdown, etc.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This software is for educational and research purposes only. This is a backtesting and development framework with mock data - not for live trading. Trading involves substantial risk of loss and is not suitable for all investors. Past performance is not indicative of future results.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Review the test cases
3. Open an issue on GitHub
4. Contact the development team

## 🔄 Updates

### Version 2.0.0 - Local Edition
- **Removed all external dependencies**: No API subscriptions required
- **100% local operation**: Run entirely offline
- **Mock data generation**: Realistic synthetic market data
- **Enhanced backtesting**: Fast TypeScript engine
- **Privacy-first**: Your data stays on your machine

### Version 1.0.0
- Initial release with external integrations

---

**Built with ❤️ for local algorithmic trading development**
