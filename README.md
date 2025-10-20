# Perplexity-Alpaca Trading Integration

A comprehensive system that integrates Perplexity's finance API with Cursor background agents and Alpaca trading platform for automated algorithmic trading.

## 🎯 Overview

This system provides a complete pipeline for:
1. **Financial Intelligence**: Fetch real-time market data, SEC filings, earnings reports, and sentiment analysis from Perplexity
2. **Automated Strategy Generation**: Convert financial insights into detailed Cursor background agent prompts
3. **Algorithmic Trading**: Execute trades on Alpaca with multiple built-in strategies and risk management

## 🏗️ Architecture

```
┌─────────────────────┐
│  Perplexity API     │
│  - SEC Filings      │
│  - Market News      │
│  - Earnings Data    │
│  - Sector Analysis  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Prompt Generator    │
│ Creates Cursor      │
│ Agent Tasks         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Trading Strategies  │
│ - Momentum          │
│ - Mean Reversion    │
│ - Breakout          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Alpaca Trading     │
│  - Paper Trading    │
│  - Live Trading     │
│  - Risk Management  │
└─────────────────────┘
```

## 📦 Installation

### Prerequisites

- Python 3.11 or higher
- Perplexity API key ([Get one here](https://www.perplexity.ai/api-platform))
- Alpaca API keys ([Sign up here](https://alpaca.markets/))

### Quick Start

1. **Clone or download this repository**

2. **Run the setup script**:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Configure your API keys**:
   Edit `.env` file with your credentials:
   ```bash
   PERPLEXITY_API_KEY=pplx-xxxxx
   ALPACA_API_KEY=PKxxxxx
   ALPACA_SECRET_KEY=xxxxx
   ALPACA_PAPER_TRADING=true
   ```

4. **Test the installation**:
   ```bash
   source venv/bin/activate
   python main.py test --tickers AAPL
   ```

## 🚀 Usage

### Mode 1: Generate Cursor Background Agent Prompts

Analyze stocks and generate comprehensive prompts for Cursor agents:

```bash
# Basic analysis with momentum strategy
python main.py analyze --tickers AMD NVDA INTC --strategy momentum

# Include SEC filings and earnings analysis
python main.py analyze \
  --tickers AAPL MSFT GOOGL \
  --strategy breakout \
  --include-earnings \
  --include-sector

# Skip SEC filings (faster, less comprehensive)
python main.py analyze \
  --tickers TSLA \
  --strategy mean_reversion \
  --no-sec
```

**Output**: Creates a detailed markdown file in `cursor_tasks/` that you can copy into Cursor's background agent interface.

### Mode 2: Live Trading (Paper Trading Recommended)

Run automated trading with real-time data:

```bash
# Dry run (simulated trades, no execution)
python main.py trade \
  --tickers AAPL MSFT \
  --strategy momentum \
  --dry-run

# Live paper trading (safe - uses Alpaca paper account)
python main.py trade \
  --tickers SPY QQQ \
  --strategy momentum

# WARNING: Real money trading (requires confirmation)
# Set ALPACA_PAPER_TRADING=false in .env first
python main.py trade --tickers AAPL --strategy momentum
```

### Mode 3: Testing and Validation

```bash
# Test API connections
python main.py test --tickers SPY

# Run unit tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 📊 Available Strategies

### 1. Momentum Strategy
- **Best for**: Trending markets
- **Entry**: Price above moving averages, RSI 50-70, MACD crossover, volume surge
- **Exit**: RSI > 70 or price below SMA_20
- **Risk**: 2% stop loss, 5% take profit

### 2. Mean Reversion Strategy
- **Best for**: Range-bound markets
- **Entry**: Price at Bollinger Band extremes, RSI oversold/overbought
- **Exit**: Return to mean or opposite extreme
- **Risk**: Tight stop losses due to volatility

### 3. Breakout Strategy
- **Best for**: Consolidation periods
- **Entry**: Price breaks consolidation range with volume
- **Exit**: Failed breakout or profit target
- **Risk**: Moderate, confirmed by volume

## 🛠️ Project Structure

```
.
├── src/
│   ├── config.py              # Configuration management
│   ├── perplexity_client.py   # Perplexity API integration
│   ├── prompt_generator.py    # Cursor prompt generation
│   ├── data_handler.py        # Alpaca data streaming
│   ├── strategy.py            # Trading strategies
│   └── executor.py            # Order execution
├── tests/
│   ├── test_strategy.py       # Strategy unit tests
│   └── test_integration.py    # Integration tests
├── cursor_tasks/              # Generated prompts
├── logs/                      # Trading logs
├── main.py                    # Main orchestrator
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container setup
└── .env.example               # Environment template
```

## 🔐 Configuration

Edit `.env` file to customize:

```bash
# Risk Management
MAX_POSITION_SIZE=0.1      # Max 10% per position
STOP_LOSS_PCT=0.02         # 2% stop loss
TAKE_PROFIT_PCT=0.05       # 5% take profit
MAX_DAILY_TRADES=10        # Daily trade limit
RISK_PER_TRADE=0.01        # 1% account risk per trade

# Logging
LOG_LEVEL=INFO             # DEBUG for verbose output
LOG_FILE=logs/trading.log
```

## 🎓 How to Use with Cursor Background Agents

1. **Generate a prompt**:
   ```bash
   python main.py analyze --tickers AMD --strategy momentum
   ```

2. **Open Cursor**:
   - Press `Ctrl+Shift+B` (or `⌘B` on Mac)
   - Click "New Background Agent"

3. **Copy the generated prompt**:
   - Open the file from `cursor_tasks/`
   - Copy entire contents

4. **Paste into Cursor**:
   - Agent will automatically create a new branch
   - Implement the strategy
   - Run tests
   - Provide you with working code

5. **Review and deploy**:
   - Review the generated code
   - Test in paper trading
   - Merge when satisfied

## 📈 Example Workflow

```bash
# 1. Analyze semiconductor stocks
python main.py analyze \
  --tickers AMD NVDA INTC \
  --strategy momentum \
  --include-earnings \
  --include-sector

# Output: cursor_tasks/momentum_AMD_NVDA_INTC_20251020_143022.md

# 2. Use Cursor agent to implement the strategy
# (Agent creates src/strategies/semiconductor_momentum.py)

# 3. Backtest the generated strategy
python backtest/backtest_runner.py \
  --strategy semiconductor_momentum \
  --start 2024-01-01 \
  --end 2024-10-20

# 4. Run in paper trading
python main.py trade \
  --tickers AMD NVDA INTC \
  --strategy momentum \
  --dry-run
```

## ⚠️ Important Safety Notes

### ⚡ ALWAYS USE PAPER TRADING FIRST
- Set `ALPACA_PAPER_TRADING=true` in `.env`
- Validate strategies for at least 30 days
- Never trade with money you can't afford to lose

### 🔒 API Security
- Never commit `.env` file to git
- Use environment variables for all keys
- Rotate keys regularly
- Use separate keys for paper/live trading

### 📉 Risk Management
- Respect position size limits
- Use stop losses on every trade
- Monitor for rapid losses
- Implement circuit breakers

### 🧪 Testing Requirements
- Run unit tests before deployment
- Backtest on 6+ months of data
- Validate in paper trading
- Monitor for at least 2 weeks live

## 🔧 Troubleshooting

### API Connection Issues
```bash
# Test Alpaca connection
python -c "from src.executor import OrderExecutor; print(OrderExecutor().get_account())"

# Test Perplexity (costs API credits!)
python -c "from src.perplexity_client import PerplexityFinanceClient; \
  print(PerplexityFinanceClient().get_market_news(['AAPL']))"
```

### Module Import Errors
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=/path/to/project:$PYTHONPATH

# Or activate virtual environment
source venv/bin/activate
```

### Rate Limiting
- Alpaca: 200 requests/minute
- Perplexity: Varies by plan
- System includes automatic rate limiting

## 📚 Documentation

- [Perplexity API Docs](https://docs.perplexity.ai/)
- [Alpaca API Docs](https://docs.alpaca.markets/)
- [Cursor Background Agents](https://forum.cursor.com/t/cursor-background-agents/)

## 🤝 Contributing

This is a background agent project. To contribute:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## 📝 License

MIT License - See LICENSE file for details

## ⚖️ Disclaimer

**This software is for educational purposes only.**

- NOT financial advice
- Use at your own risk
- Past performance ≠ future results
- Algorithmic trading involves substantial risk
- Consult a financial advisor before trading
- The authors assume no liability for trading losses

---

**Built with**: Python • Alpaca API • Perplexity AI • Cursor Background Agents

**Happy Trading! 🚀📈**
