# Perplexity-Alpaca Trading Integration

A sophisticated system that integrates Perplexity's live finance data with Cursor Background Agents to automatically generate and implement trading strategies on Alpaca's platform.

## 🚀 Overview

This system combines:
- **Perplexity API** for real-time financial data, SEC filings, market sentiment, and technical analysis
- **Cursor Background Agents** for autonomous trading bot development
- **Alpaca Trading API** for paper and live trading execution
- **Comprehensive risk management** and portfolio optimization

## 🏗️ Architecture

```
Perplexity API → Data Analysis → Prompt Generation → Cursor Agent → Trading Bot
     ↓              ↓              ↓              ↓           ↓
Financial Data → AI Analysis → Structured Prompt → Code Gen → Alpaca Trading
```

## 📋 Features

### Data Sources
- **SEC Filings Analysis**: 10-K, 10-Q, 8-K filings with financial metrics extraction
- **Real-time Market News**: Sentiment analysis and price-moving events
- **Earnings Analysis**: Revenue trends, guidance, and analyst estimates
- **Technical Analysis**: RSI, MACD, Bollinger Bands, and custom indicators
- **Sector Analysis**: Industry trends and competitive landscape

### Trading Capabilities
- **Multi-strategy Support**: Momentum, mean reversion, breakout, and custom strategies
- **Real-time Data Streaming**: WebSocket connections for live price feeds
- **Risk Management**: Position sizing, stop-loss, take-profit, and drawdown limits
- **Portfolio Optimization**: Kelly Criterion and correlation-based sizing
- **Backtesting Framework**: Historical strategy validation and performance analysis

### Cursor Integration
- **Automated Prompt Generation**: Context-rich prompts for background agents
- **Structured Implementation**: Complete file structure and requirements
- **Testing Framework**: Unit tests and validation procedures
- **Documentation**: Comprehensive code documentation and examples

## 🛠️ Installation

### Prerequisites
- Python 3.11+
- Cursor IDE with Background Agents enabled
- Perplexity API key
- Alpaca Trading API credentials

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd perplexity-alpaca-trading
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Run setup script**
```bash
chmod +x setup.sh
./setup.sh
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Perplexity API Configuration
PERPLEXITY_API_KEY=your_perplexity_api_key_here

# Alpaca Trading Configuration
ALPACA_API_KEY=your_alpaca_api_key_here
ALPACA_SECRET_KEY=your_alpaca_secret_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets  # Use https://api.alpaca.markets for live trading

# Trading Configuration
DEFAULT_STRATEGY=semiconductor_momentum
PAPER_TRADING=true
MAX_POSITION_SIZE=0.1  # 10% of portfolio per position
RISK_TOLERANCE=0.02    # 2% stop loss
```

### Cursor Configuration

The `.cursor/environment.json` file is pre-configured for optimal background agent performance:

```json
{
  "dockerfile": "Dockerfile",
  "setup_script": "setup.sh",
  "install_commands": ["pip install -r requirements.txt"],
  "terminal_commands": ["python main.py --test"],
  "environment_variables": {
    "PYTHONPATH": "${workspaceFolder}/src"
  }
}
```

## 🚀 Usage

### Basic Usage

1. **Test API connections**
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

### Advanced Usage

#### Comprehensive Analysis
```python
from src.main import PerplexityAlpacaIntegration

# Initialize integration
integration = PerplexityAlpacaIntegration()

# Generate complete trading strategy
prompt_file = integration.analyze_and_generate_task(
    tickers=["AAPL", "MSFT", "NVDA"],
    strategy_name="semiconductor_momentum",
    additional_context="Focus on AI and cloud computing trends"
)
```

#### Custom Strategy Development
```python
# Generate custom strategy prompt
market_data = {
    "sec_filings": "Custom SEC analysis",
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

### Using Cursor Background Agents

1. **Open Cursor** and press `Ctrl+Shift+B` (or `⌘B` on Mac)
2. **Click "New Background Agent"**
3. **Copy the contents** of the generated prompt file from `cursor_tasks/`
4. **Paste into the agent prompt field**
5. **The agent will create a new branch** and implement the strategy

## 📊 Generated Trading Bots

The Cursor background agents will generate complete trading systems with:

### Core Files
- `config.py`: API configuration and settings
- `data_handler.py`: Real-time data streaming and storage
- `strategy.py`: Trading logic implementation
- `risk_manager.py`: Risk management and position sizing
- `executor.py`: Order execution and management
- `portfolio_manager.py`: Portfolio tracking and rebalancing
- `logger.py`: Comprehensive logging system
- `main.py`: Main execution loop

### Features
- **Real-time Data Streaming**: WebSocket connections for live price feeds
- **Technical Indicators**: RSI, MACD, Bollinger Bands, ATR, and custom indicators
- **Risk Management**: Kelly Criterion, stop-loss, take-profit, and drawdown limits
- **Order Management**: Market, limit, and bracket orders
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

### Cursor Requirements
- **Privacy Mode must be disabled** for background agents
- **Usage-based spending enabled** (minimum $10 funding)
- **GitHub repository connected** with read-write privileges

### Trading Considerations
- **Paper trading only** initially - no live trading without explicit approval
- **Rate limiting** - respect Alpaca's API limits
- **Error handling** - comprehensive error handling for all operations
- **Testing** - thorough testing before live deployment

## 📚 API Documentation

### Perplexity API
- [Perplexity API Documentation](https://docs.perplexity.ai/)
- [Financial Data Access](https://docs.perplexity.ai/llms-full.txt)
- [SEC Filings Integration](https://docs.perplexity.ai/cookbook/examples/financial-news-tracker/README)

### Alpaca API
- [Alpaca Trading API](https://alpaca.markets/sdks/python/)
- [Market Data API](https://docs.alpaca.markets/docs/sdks-and-tools)
- [WebSocket Streaming](https://alpaca.markets/learn/algorithmic-trading-python-alpaca)

### Cursor Background Agents
- [Background Agents Guide](https://lgallardo.com/2025/06/11/cursor-background-agents-experience/)
- [Setup Instructions](https://madewithlove.com/blog/using-cursor-background-agents/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This software is for educational and research purposes only. Trading involves substantial risk of loss and is not suitable for all investors. Past performance is not indicative of future results. Always consult with a qualified financial advisor before making investment decisions.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Review the test cases
3. Open an issue on GitHub
4. Contact the development team

## 🔄 Updates

### Version 1.0.0
- Initial release with Perplexity-Alpaca integration
- Cursor background agent support
- Comprehensive testing framework
- Complete documentation

---

**Built with ❤️ for algorithmic trading and AI automation**