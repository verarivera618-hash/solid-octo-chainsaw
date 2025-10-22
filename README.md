# Perplexity-Alpaca Trading Integration (Local-Only)

A sophisticated system that integrates Perplexity's live finance data and generates local prompts to implement trading strategies on Alpaca's platform—no external IDE subscriptions required.

## 🚀 Overview

This system combines:
- **Perplexity API** for real-time financial data, SEC filings, market sentiment, and technical analysis
- **Local Prompt Generation** for copy/paste into your local editor
- **Alpaca Trading API** for paper and live trading execution
- **Comprehensive risk management** and portfolio optimization

## 🏗️ Architecture

```
Perplexity API → Data Analysis → Local Prompt Generation → Trading Bot
     ↓              ↓                      ↓                  ↓
Financial Data → AI Analysis → Structured Prompt → Alpaca Trading
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

### Local Prompt Workflow
- **Automated Prompt Generation**: Context-rich prompts saved under `local_tasks/`
- **Structured Implementation**: Complete file structure and requirements
- **Testing Framework**: Unit tests and validation procedures
- **Documentation**: Comprehensive code documentation and examples

## 🛠️ Installation

### Prerequisites
- Python 3.11+
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

### Local Prompt Directory

Generated prompts are saved under `local_tasks/`. Copy the content into your local editor and implement the described files.

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

### Using Locally

1. Open the generated prompt in `local_tasks/`
2. Copy the content and implement the specified files in `src/`
3. Run tests with `pytest`
4. Paper trade only until fully validated

## 📊 Generated Trading Bots

You will implement complete trading systems with:

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

### Local Workflow Notes
- No external IDE or subscription required
- Keep credentials in environment variables

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

### Version 1.1.0
- Removed Cursor dependencies; local-only prompt workflow
- Retained core trading and analysis capabilities
- Improved local docs and quickstart

---

**Built with ❤️ for algorithmic trading and AI automation**
