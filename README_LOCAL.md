# Local Trading System

A fully local trading system that generates synthetic market data and simulates trading strategies without any external API dependencies. Perfect for copy-paste deployment and testing.

## 🚀 Features

- **No External Dependencies**: Fully local operation, no API keys required
- **Synthetic Data Generation**: Realistic market data for testing and development
- **Strategy Simulation**: Complete trading strategy implementation and testing
- **Risk Management**: Built-in risk controls and position sizing
- **Backtesting**: Historical strategy validation
- **Performance Monitoring**: Real-time tracking and analytics

## 🏗️ Architecture

```
Local Data Provider → Strategy Engine → Order Executor → Portfolio Manager
        ↓                    ↓              ↓              ↓
   Synthetic Data → Signal Generation → Trade Simulation → Performance Tracking
```

## 📋 Core Components

### Data Sources
- **Synthetic Price Data**: OHLCV data generation with realistic patterns
- **Financial Analysis**: SEC filings, earnings, news sentiment simulation
- **Technical Analysis**: RSI, MACD, Bollinger Bands, and custom indicators
- **Sector Analysis**: Industry trends and competitive landscape simulation

### Trading Capabilities
- **Multi-strategy Support**: Momentum, mean reversion, breakout strategies
- **Risk Management**: Position sizing, stop-loss, take-profit controls
- **Portfolio Optimization**: Kelly Criterion and correlation-based sizing
- **Backtesting Framework**: Historical strategy validation

## 🛠️ Installation

### Prerequisites
- Python 3.11+
- No external API keys required

### Setup

1. **Clone or copy the repository**
```bash
# Copy all files to your local directory
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the system**
```bash
python main.py --test
```

## 🔧 Configuration

### Environment Variables (Optional)

Create a `.env` file with optional settings:

```env
# Trading Configuration
DEFAULT_STRATEGY=momentum
MAX_POSITION_SIZE=0.1
RISK_TOLERANCE=0.02
INITIAL_CASH=100000.0

# Data Configuration
DATA_DAYS=30
```

### System Settings

The system uses local configuration in `src/config.py`:

```python
class Config:
    SYSTEM_MODE = "local"  # Always local
    PAPER_TRADING = True   # Always paper trading
    INITIAL_CASH = 100000.0
    MAX_POSITION_SIZE = 0.1
    RISK_TOLERANCE = 0.02
    DATA_DAYS = 30
```

## 🚀 Usage

### Basic Usage

1. **Test the system**
```bash
python main.py --test
```

2. **Check account status**
```bash
python main.py --status
```

3. **Generate trading strategy**
```bash
python main.py --tickers AAPL MSFT --strategy momentum
```

4. **Quick analysis**
```bash
python main.py --tickers AAPL --strategy momentum --quick
```

5. **Reset account**
```bash
python main.py --reset
```

### Advanced Usage

#### Comprehensive Analysis
```python
from src.main import LocalTradingIntegration

# Initialize integration
integration = LocalTradingIntegration()

# Generate complete trading strategy
prompt_file = integration.analyze_and_generate_task(
    tickers=["AAPL", "MSFT", "NVDA"],
    strategy_name="momentum",
    additional_context="Focus on technology stocks"
)
```

#### Custom Strategy Development
```python
# Generate custom strategy prompt
market_data = {
    "sec_filings": "Custom analysis",
    "news_sentiment": "Custom sentiment data",
    "technical": "Custom technical analysis",
    "sector": "Custom sector analysis",
    "price_data": "Custom price data"
}

prompt = integration.prompt_generator.generate_trading_strategy_prompt(
    market_data=market_data,
    strategy_type="custom_strategy",
    tickers=["AAPL"],
    additional_context="Custom requirements"
)
```

## 📊 Generated Trading Bots

The system generates complete trading implementations with:

### Core Files
- `config.py`: Configuration and settings
- `data_handler.py`: Local data generation and storage
- `strategy.py`: Trading logic implementation
- `risk_manager.py`: Risk management and position sizing
- `executor.py`: Order execution and management
- `portfolio_manager.py`: Portfolio tracking and rebalancing
- `logger.py`: Comprehensive logging system
- `main.py`: Main execution loop

### Features
- **Synthetic Data Generation**: Realistic OHLCV data with technical indicators
- **Technical Indicators**: RSI, MACD, Bollinger Bands, ATR, and custom indicators
- **Risk Management**: Kelly Criterion, stop-loss, take-profit, and drawdown limits
- **Order Management**: Market, limit, and bracket orders (simulated)
- **Backtesting**: Historical strategy validation
- **Monitoring**: Real-time performance tracking and alerts

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
- `tests/test_local_data_provider.py`: Local data provider tests
- `tests/test_local_trading_client.py`: Local trading client tests
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
- No external API calls
- No sensitive data transmission
- Local data generation only
- Simulated trading environment

### Risk Controls
- Position size limits
- Daily loss limits
- Maximum drawdown controls
- Sector concentration limits
- Correlation-based position limits

## 🚨 Important Notes

### Local Operation
- **No External APIs**: System operates entirely locally
- **Simulated Trading**: All trades are simulated for testing
- **Synthetic Data**: Market data is generated, not real
- **No Real Money**: Safe for testing and development

### Trading Considerations
- **Simulation Only**: No real trading without external integration
- **Testing Focus**: Designed for strategy development and testing
- **Educational Purpose**: Suitable for learning and experimentation

## 📚 API Documentation

### Local Data Provider
- `generate_historical_data()`: Generate synthetic OHLCV data
- `get_sec_filings_analysis()`: Generate SEC analysis
- `get_market_news_sentiment()`: Generate news sentiment
- `get_earnings_analysis()`: Generate earnings data
- `get_technical_analysis()`: Generate technical analysis
- `calculate_technical_indicators()`: Calculate indicators

### Local Trading Client
- `get_account()`: Get account information
- `get_positions()`: Get current positions
- `submit_market_order()`: Submit market order
- `submit_bracket_order()`: Submit bracket order
- `close_position()`: Close position
- `get_performance_summary()`: Get performance metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This software is for educational and research purposes only. All trading is simulated and no real money is involved. Past performance is not indicative of future results. Always consult with a qualified financial advisor before making investment decisions.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Review the test cases
3. Open an issue on GitHub
4. Contact the development team

## 🔄 Updates

### Version 1.0.0
- Initial release with local-only operation
- Synthetic data generation
- Complete trading simulation
- No external dependencies
- Comprehensive testing framework

---

**Built with ❤️ for local trading simulation and strategy development**