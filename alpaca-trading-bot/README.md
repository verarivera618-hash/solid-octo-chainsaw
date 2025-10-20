# 🚀 Alpaca Trading Bot with Perplexity Finance Integration

A sophisticated algorithmic trading system that combines Perplexity's real-time financial intelligence with Alpaca's trading platform, orchestrated through Cursor's AI-powered background agents.

## 🌟 Features

- **Real-time Financial Intelligence**: Leverages Perplexity API for SEC filings, market news, and sentiment analysis
- **Multi-Strategy Trading**: Implements momentum, mean reversion, and sentiment-based strategies
- **Cursor Agent Integration**: Generates prompts for Cursor background agents to autonomously build trading strategies
- **Risk Management**: Comprehensive position sizing, stop-loss, and portfolio risk controls
- **Paper Trading**: Safe testing environment with Alpaca's paper trading API
- **Live Data Streaming**: WebSocket connections for real-time market data
- **Automated Execution**: Bracket orders with automatic stop-loss and take-profit

## 📋 Prerequisites

- Python 3.9+
- Perplexity API key (for financial data)
- Alpaca API keys (paper trading recommended)
- Cursor IDE (for agent integration)
- Minimum $10 in Cursor usage credits (for background agents)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/alpaca-trading-bot.git
cd alpaca-trading-bot
```

### 2. Run Setup Script
```bash
chmod +x setup.sh
./setup.sh
```

### 3. Configure API Keys
Edit the `.env` file with your API credentials:
```env
# Perplexity API
PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxx

# Alpaca API (Paper Trading)
ALPACA_API_KEY=PKxxxxxxxxxxxxx
ALPACA_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxx
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Trading Configuration
PAPER_TRADING=true
MAX_POSITION_SIZE=0.1
DEFAULT_STOP_LOSS=0.02
DEFAULT_TAKE_PROFIT=0.05
```

## 🚀 Quick Start

### Option 1: Generate Cursor Agent Prompt

Generate a prompt for Cursor's background agent to build a custom strategy:

```bash
# Generate momentum strategy for tech stocks
python main.py --mode generate --symbols AAPL MSFT NVDA --strategy momentum

# Generate sentiment-based strategy
python main.py --mode generate --symbols TSLA GME AMC --strategy sentiment
```

**Using the Generated Prompt in Cursor:**
1. Open Cursor IDE
2. Press `Ctrl+Shift+B` (Windows/Linux) or `⌘B` (Mac)
3. Click "New Background Agent"
4. Copy the contents from `cursor_tasks/[strategy]_latest.md`
5. Paste into the agent prompt
6. The agent will create a new branch and implement the strategy

### Option 2: Run the Trading Bot

Start the automated trading bot with live market analysis:

```bash
# Trade with default symbols (AAPL, MSFT, GOOGL)
python main.py --mode trade

# Trade specific symbols with 10-minute intervals
python main.py --mode trade --symbols AMD NVDA INTC --interval 10
```

## 📊 Architecture

```
┌─────────────────────┐
│  Perplexity API     │
│  - SEC Filings      │
│  - Market News      │
│  - Sentiment Data   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Data Aggregator    │
│  - Parse Analysis   │
│  - Extract Signals  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐     ┌─────────────────────┐
│  Strategy Manager   │◄────►│  Alpaca Market Data │
│  - Momentum         │     │  - Real-time Bars   │
│  - Mean Reversion   │     │  - Historical Data  │
│  - Sentiment-based  │     └─────────────────────┘
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Risk Manager       │
│  - Position Sizing  │
│  - Stop Loss/TP     │
│  - Portfolio Limits │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Order Executor     │
│  - Bracket Orders   │
│  - Order Management │
│  - Alpaca Trading   │
└─────────────────────┘
```

## 🎯 Trading Strategies

### 1. Momentum Strategy
- Identifies stocks breaking above 20-day highs
- Uses RSI, MACD, and volume confirmation
- Implements trailing stops based on ATR

### 2. Mean Reversion Strategy
- Trades oversold/overbought conditions
- Bollinger Bands and RSI indicators
- Targets return to mean prices

### 3. Sentiment-Based Strategy
- Analyzes Perplexity's financial news sentiment
- Social media trend analysis
- News catalyst identification

## 🔧 Configuration

### Strategy Configuration
Edit `src/config.py` to adjust strategy parameters:

```python
strategies = {
    "momentum": {
        "enabled": True,
        "rsi_threshold_buy": 60,
        "volume_multiplier": 1.5
    },
    "mean_reversion": {
        "enabled": True,
        "bb_periods": 20,
        "rsi_oversold": 30
    }
}
```

### Risk Management Settings
```python
risk_config = {
    "max_position_size": 0.1,      # 10% of portfolio
    "max_daily_loss": 0.02,         # 2% daily loss limit
    "max_drawdown": 0.1,            # 10% max drawdown
    "max_positions": 5,             # Max concurrent positions
    "min_cash_reserve": 0.2         # 20% cash reserve
}
```

## 📈 Usage Examples

### Example 1: Analyzing Tech Stocks with Perplexity
```python
from src.perplexity_client import PerplexityFinanceClient, QueryType

async def analyze_tech():
    client = PerplexityFinanceClient(api_key="your_key")
    
    # Get comprehensive analysis
    analysis = await client.get_comprehensive_analysis(
        tickers=["AAPL", "MSFT"],
        include_types=[
            QueryType.SEC_FILINGS,
            QueryType.MARKET_NEWS,
            QueryType.SENTIMENT
        ]
    )
    
    return analysis
```

### Example 2: Executing a Trade Signal
```python
from src.strategy import TradingSignal, Signal
from src.executor import OrderExecutor

executor = OrderExecutor(api_key, secret_key, paper=True)

signal = TradingSignal(
    symbol="AAPL",
    signal=Signal.BUY,
    confidence=0.75,
    entry_price=150.00,
    stop_loss=147.00,
    take_profit=156.00,
    position_size=100
)

order = executor.execute_signal(signal, order_type="bracket")
```

### Example 3: Generating Cursor Prompt
```python
from src.prompt_generator import CursorPromptGenerator, StrategyType

generator = CursorPromptGenerator()

prompt = generator.generate_prompt(
    financial_data=perplexity_analysis,
    strategy_type=StrategyType.MOMENTUM,
    tickers=["AMD", "NVDA"],
    additional_requirements="Focus on semiconductor sector dynamics"
)

# Save for Cursor agent
prompt_file = generator.save_prompt(prompt, "semiconductor_strategy", ["AMD", "NVDA"])
```

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html

# Run specific test
pytest tests/test_strategy.py -v
```

## 🐳 Docker Deployment

Build and run with Docker:
```bash
# Build image
docker build -t alpaca-trading-bot .

# Run container
docker run -d \
  --name trading-bot \
  --env-file .env \
  alpaca-trading-bot
```

Using Docker Compose:
```bash
docker-compose up -d
```

## 📊 Performance Monitoring

The bot provides real-time performance metrics:

- **Execution Report**: Order success rate, volume, commissions
- **Risk Report**: Daily P&L, drawdown, position counts
- **Strategy Report**: Win rate, signal accuracy per strategy
- **Data Statistics**: Stream health, buffer sizes, API calls

Access metrics via logs or export to monitoring systems.

## 🔐 Security Best Practices

1. **Never commit API keys** - Use environment variables
2. **Use paper trading** for testing and development
3. **Set conservative risk limits** initially
4. **Monitor positions regularly** via Alpaca dashboard
5. **Implement stop-losses** on all positions
6. **Keep logs secure** - They may contain sensitive data

## 🤝 Cursor Agent Integration

### Setting Up Cursor Background Agents

1. **Disable Privacy Mode**: Settings → Privacy → Disable
2. **Fund Usage Credits**: Minimum $10 in account
3. **Connect GitHub**: Enable read-write access
4. **Configure Environment**: Use provided `.cursor/environment.json`

### Workflow with Cursor Agents

1. Generate prompt with financial analysis from Perplexity
2. Launch Cursor background agent with prompt
3. Agent creates feature branch and implements strategy
4. Review generated code and test in paper trading
5. Merge to main when satisfied with performance

## 📚 API Documentation

### Perplexity Finance API
- [API Documentation](https://docs.perplexity.ai)
- Rate limits: 100 requests/minute
- Models: sonar-pro, sonar-deep-research
- Domains: sec, finance, news

### Alpaca Trading API
- [API Documentation](https://alpaca.markets/docs)
- Paper trading endpoint: `https://paper-api.alpaca.markets`
- WebSocket feed: IEX (free) or SIP (paid)
- Rate limits: 200 requests/minute

## 🚨 Troubleshooting

### Common Issues

**Issue**: WebSocket connection fails
```bash
# Solution: Check firewall and use IEX feed
MARKET_DATA_FEED=iex
```

**Issue**: Perplexity rate limit exceeded
```bash
# Solution: Increase analysis interval
python main.py --interval 15  # 15 minutes between analyses
```

**Issue**: Cursor agent not starting
```bash
# Solution: Ensure privacy mode is disabled and credits available
# Check: Cursor Settings → Privacy → Disabled
# Check: Cursor Settings → Usage → Credits > $0
```

## 📈 Roadmap

- [ ] Backtesting framework with historical data
- [ ] Options trading strategies
- [ ] Multi-asset portfolio optimization
- [ ] Advanced risk metrics (VaR, Sharpe ratio)
- [ ] Web dashboard for monitoring
- [ ] Integration with TradingView webhooks
- [ ] Machine learning signal enhancement
- [ ] Automated strategy optimization

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

**IMPORTANT**: This software is for educational purposes only. 

- Trading involves substantial risk of loss
- Past performance does not guarantee future results
- Always use paper trading for testing
- Never trade with money you cannot afford to lose
- Consult with qualified financial advisors

The authors assume no responsibility for financial losses incurred using this software.

## 🙏 Acknowledgments

- [Perplexity AI](https://perplexity.ai) for financial intelligence
- [Alpaca Markets](https://alpaca.markets) for trading infrastructure
- [Cursor](https://cursor.sh) for AI-powered development
- Open source community for amazing libraries

## 📞 Support

- **Documentation**: [Full Docs](https://docs.yoursite.com)
- **Issues**: [GitHub Issues](https://github.com/yourusername/alpaca-trading-bot/issues)
- **Discord**: [Join Community](https://discord.gg/yourserver)
- **Email**: support@yoursite.com

---

Built with ❤️ for algorithmic traders