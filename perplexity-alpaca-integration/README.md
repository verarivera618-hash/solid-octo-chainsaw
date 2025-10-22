# Perplexity-Alpaca Trading Integration

An integration that combines Perplexity's finance data with local prompt generation to implement trading strategies on Alpaca's platform—no external IDE dependencies required.

## 🎯 Overview

This integration creates an automated workflow:

1. **Perplexity API** → Real-time financial analysis (SEC filings, news, earnings)
2. **Prompt Generator** → Converts analysis into structured local prompts  
3. **Local Implementation** → You implement strategies in your editor
4. **Alpaca Trading** → Executes trades in paper/live environment

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    
│   Perplexity    │───▶│  Prompt Generator │───▶ Local Implementation
│   Finance API   │    │                  │    
└─────────────────┘    └──────────────────┘    
                                                         │
┌─────────────────┐    ┌──────────────────┐             │
│   Alpaca Data   │◄───│  Trading Bot     │◄────────────┘
│      API        │    │  Implementation  │
└─────────────────┘    └──────────────────┘
                                │
                       ┌──────────────────┐
                       │  Alpaca Trading  │
                       │      API         │
                       └──────────────────┘
```

## 🚀 Quick Start

### 1. Installation

```bash
cd perplexity-alpaca-integration
pip install -r requirements.txt
```

### 2. Configuration

Copy the environment template and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# Perplexity API
PERPLEXITY_API_KEY=your_perplexity_api_key_here

# Alpaca API (Paper Trading)
ALPACA_API_KEY=your_alpaca_paper_api_key_here
ALPACA_SECRET_KEY=your_alpaca_paper_secret_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

### 3. Test Connections

```bash
python main.py --test
```

### 4. Generate Your First Strategy

```bash
python main.py --generate \
  --tickers AAPL MSFT GOOGL \
  --strategy momentum \
  --time-horizon swing \
  --risk medium
```

### 5. Use Locally

1. Open the generated prompt under `local_tasks/`
2. Copy its content into your editor
3. Implement the described files under `src/`
4. Run tests with `pytest` and iterate locally

## 📊 Available Strategies

| Strategy | Description | Time Horizons | Risk Levels |
|----------|-------------|---------------|-------------|
| **Momentum** | Follows price momentum using technical indicators | Intraday, Swing, Position | Low, Medium, High |
| **Mean Reversion** | Trades against extreme price movements | Intraday, Swing | Low, Medium, High |
| **Breakout** | Trades breakouts from consolidation patterns | Intraday, Swing | Medium, High |
| **Earnings Play** | Trades around earnings announcements | Intraday, Swing | High |
| **Sector Rotation** | Rotates between sectors based on market cycles | Swing, Position | Low, Medium |
| **Pairs Trading** | Long/short pairs within same sector | Swing, Position | Medium, High |

## 🛠️ Usage Examples

### Market Analysis
```bash
# Get comprehensive market overview
python main.py --overview AAPL MSFT GOOGL NVDA

# Test API connections
python main.py --test
```

### Strategy Generation
```bash
# Momentum strategy for tech stocks
python main.py --generate \
  --tickers AAPL MSFT GOOGL \
  --strategy momentum \
  --time-horizon swing \
  --risk medium \
  --market bullish

# Earnings play for upcoming earnings
python main.py --generate \
  --tickers NVDA AMD \
  --strategy earnings_play \
  --time-horizon intraday \
  --risk high \
  --requirements "Focus on AI/datacenter earnings catalysts"

# Sector rotation strategy
python main.py --generate \
  --tickers XLK XLF XLE XLI \
  --strategy sector_rotation \
  --time-horizon position \
  --risk low \
  --market neutral
```

### Interactive Mode
```bash
# Run without arguments for interactive menu
python main.py
```

## 📁 Project Structure

```
perplexity-alpaca-integration/
├── src/
│   ├── config.py                 # Configuration management
│   ├── perplexity_client.py      # Perplexity API client
│   ├── prompt_generator.py       # Local prompt generation
│   ├── alpaca_client.py          # Alpaca API integration
│   └── strategy_base.py          # Trading strategy base classes
├── tests/
│   ├── test_perplexity_client.py # Perplexity client tests
│   ├── test_alpaca_client.py     # Alpaca client tests
│   └── test_integration.py       # Integration tests
├── examples/
│   └── example_usage.py          # Usage examples
├── local_tasks/                  # Generated local prompts
├── logs/                         # Application logs
├── requirements.txt              # Python dependencies
├── main.py                       # Main orchestrator
└── README.md                     # This file
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PERPLEXITY_API_KEY` | Perplexity API key | Required |
| `ALPACA_API_KEY` | Alpaca API key | Required |
| `ALPACA_SECRET_KEY` | Alpaca secret key | Required |
| `ALPACA_BASE_URL` | Alpaca API URL | `https://paper-api.alpaca.markets` |
| `PORTFOLIO_SIZE` | Portfolio size for backtesting | `100000` |
| `MAX_POSITION_SIZE` | Maximum position size (%) | `0.1` |
| `RISK_PER_TRADE` | Risk per trade (%) | `0.02` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Strategy Parameters

Customize strategy behavior in your prompts:

```python
# Risk Management
STOP_LOSS_PCT=0.02          # 2% stop loss
TAKE_PROFIT_PCT=0.04        # 4% take profit
MAX_DAILY_LOSS=0.05         # 5% daily loss limit

# Position Sizing
MAX_POSITION_SIZE=0.1       # 10% max position
RISK_PER_TRADE=0.02         # 2% risk per trade

# Rate Limiting
PERPLEXITY_RATE_LIMIT=60    # 60 requests/minute
ALPACA_RATE_LIMIT=200       # 200 requests/minute
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_perplexity_client.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

Run example usage:

```bash
python examples/example_usage.py
```

## 📈 Generated Trading Bot Features

When Cursor agents implement your strategies, they create:

### Core Components
- **Data Integration**: Real-time Alpaca WebSocket streaming
- **Strategy Logic**: Customized algorithm based on your analysis
- **Risk Management**: Stop-loss, take-profit, position sizing
- **Order Execution**: Market, limit, and bracket orders
- **Portfolio Tracking**: Real-time P&L and performance metrics

### Advanced Features
- **Backtesting Framework**: Historical performance validation
- **Paper Trading**: Safe testing environment
- **Error Handling**: Robust API error recovery
- **Logging**: Comprehensive trade and decision logging
- **Monitoring**: Real-time performance dashboards

### Example Generated Structure
```python
trading_bot/
├── src/
│   ├── config/settings.py
│   ├── data/alpaca_client.py
│   ├── strategy/momentum_strategy.py
│   ├── execution/order_manager.py
│   ├── analysis/backtester.py
│   └── utils/logger.py
├── tests/
├── main.py
└── README.md
```

## 🔒 Security & Risk Management

### API Security
- All API keys stored in environment variables
- No hardcoded credentials in code
- Rate limiting to prevent API abuse
- Error handling for API failures

### Trading Risk
- **Paper Trading Default**: All strategies start in paper trading
- **Position Limits**: Configurable maximum position sizes
- **Stop Losses**: Automatic risk management
- **Daily Loss Limits**: Circuit breakers for excessive losses

### Cursor Agent Safety
- **Privacy Mode**: Disable for background agents (required)
- **Code Review**: Always review generated code before live trading
- **Incremental Testing**: Test strategies thoroughly before deployment

## 🚨 Important Warnings

⚠️ **NEVER use real money without thorough testing**
⚠️ **Always review generated code before execution**  
⚠️ **Start with paper trading and small position sizes**
⚠️ **Monitor strategies closely, especially initially**
⚠️ **Understand the risks of algorithmic trading**

## 📚 API Documentation

### Perplexity Finance Capabilities
- **SEC Filings**: 10-K, 10-Q, 8-K analysis
- **Real-time News**: Market sentiment analysis
- **Earnings Data**: Results and expectations
- **Analyst Ratings**: Consensus and price targets
- **Sector Analysis**: Industry trends and positioning

### Alpaca Trading Features
- **Market Data**: Real-time and historical data
- **Order Types**: Market, limit, stop, bracket orders
- **Account Management**: Portfolio tracking and risk monitoring
- **Paper Trading**: Risk-free testing environment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🆘 Support

### Common Issues

**API Connection Errors**
- Verify API keys are correctly set in `.env`
- Check API key permissions and rate limits
- Ensure paper trading keys for Alpaca

**Cursor Agent Issues**
- Disable Privacy Mode in Cursor settings
- Ensure usage-based spending is enabled
- Check prompt file formatting

**Strategy Performance**
- Always backtest before live trading
- Monitor for overfitting to historical data
- Adjust parameters based on market conditions

### Getting Help

1. Check the [examples](examples/) directory
2. Review test files for usage patterns
3. Run `python main.py --help` for command options
4. Check logs in `logs/` directory for debugging

---

**Ready to build autonomous trading strategies with AI? Start with `python main.py --test` and let Cursor agents do the heavy lifting!** 🚀