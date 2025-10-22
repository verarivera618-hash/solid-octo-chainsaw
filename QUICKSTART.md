# Quick Start Guide

## 🚀 Get Trading in 5 Minutes

### Step 1: Setup (2 minutes)

```bash
# Run the setup script
chmod +x setup.sh
./setup.sh

# Activate virtual environment
source venv/bin/activate
```

### Step 2: Configure API Keys (1 minute)

Edit `.env` file:
```bash
# Get Perplexity API key from: https://www.perplexity.ai/api-platform
PERPLEXITY_API_KEY=pplx-xxxxx

# Get Alpaca keys from: https://alpaca.markets/
# Use paper trading keys (safe to test)
ALPACA_API_KEY=PKxxxxx
ALPACA_SECRET_KEY=xxxxx
ALPACA_PAPER_TRADING=true
```

### Step 3: Test Connection (30 seconds)

```bash
python main.py test --tickers SPY
```

Expected output:
```
✅ Alpaca connected - Account equity: $100000.00
✅ Data fetch successful - 10 bars
✅ All tests passed!
```

### Step 4: Generate Your First Strategy (1 minute)

```bash
# Analyze Apple with momentum strategy
python main.py analyze --tickers AAPL --strategy momentum
```

Output:
```
📄 Prompt file: local_tasks/momentum_AAPL_20251020_143022.md
📊 Strategy: Momentum Trading Strategy
📈 Tickers: AAPL
⏰ Generated: 2025-10-20 14:30:22
```

### Step 5: Use Locally (No external IDE required)

1. **Open the generated prompt** under `local_tasks/`
2. **Copy the content** and implement the described files under `src/`
3. **Run tests**: `pytest -v`
4. **Paper trade** only until validated

---

## 📊 Common Use Cases

### Use Case 1: Research a Stock
```bash
# Get comprehensive analysis with SEC filings and earnings
python main.py analyze \
  --tickers NVDA \
  --strategy momentum \
  --include-earnings \
  --include-sec
```

### Use Case 2: Sector Analysis
```bash
# Analyze multiple stocks in a sector
python main.py analyze \
  --tickers AMD NVDA INTC \
  --strategy momentum \
  --include-sector
```

### Use Case 3: Test a Strategy (Paper Trading)
```bash
# Run strategy in dry-run mode (simulated)
python main.py trade \
  --tickers SPY \
  --strategy momentum \
  --dry-run
```

### Use Case 4: Run Live Paper Trading
```bash
# Run with real paper trading account
python main.py trade \
  --tickers AAPL MSFT \
  --strategy momentum
```

---

## 🎯 Strategy Selection Guide

| Strategy | Best For | Market Type | Risk Level |
|----------|----------|-------------|------------|
| **Momentum** | Trending stocks | Uptrend | Medium |
| **Mean Reversion** | Range-bound stocks | Sideways | Low-Medium |
| **Breakout** | Consolidating stocks | Volatility expansion | Medium-High |

### Example Commands

```bash
# Momentum (trending markets)
python main.py analyze --tickers AAPL --strategy momentum

# Mean Reversion (oversold/overbought)
python main.py analyze --tickers SPY --strategy mean_reversion

# Breakout (consolidation patterns)
python main.py analyze --tickers TSLA --strategy breakout
```

---

## ⚡ Power User Tips

### 1. Batch Analysis
```bash
# Analyze multiple stocks at once
python main.py analyze \
  --tickers AAPL MSFT GOOGL AMZN META \
  --strategy momentum \
  --include-earnings
```

### 2. Skip Slow Queries
```bash
# Skip SEC filings for faster results
python main.py analyze \
  --tickers NVDA \
  --strategy momentum \
  --no-sec \
  --no-news
```

### 3. Enable Debug Logging
```bash
# See detailed logs
python main.py analyze \
  --tickers AAPL \
  --strategy momentum \
  --log-level DEBUG
```

### 4. Run Tests
```bash
# Run all unit tests
pytest tests/ -v

# Run specific test
pytest tests/test_strategy.py::TestMomentumStrategy -v

# Check test coverage
pytest tests/ --cov=src --cov-report=html
```

---

## ❓ Troubleshooting

### Problem: "Configuration validation failed"
**Solution**: Check your `.env` file has all required keys
```bash
cat .env  # Verify keys are set
```

### Problem: "No module named 'src'"
**Solution**: Activate virtual environment
```bash
source venv/bin/activate
```

### Problem: "Alpaca connection failed"
**Solution**: Verify your Alpaca API keys are correct
```bash
# Test connection
python -c "from src.executor import OrderExecutor; print(OrderExecutor().get_account())"
```

### Problem: Tests failing
**Solution**: Some tests require API keys
```bash
# Run only unit tests (no API needed)
pytest tests/test_strategy.py -v

# Skip integration tests
pytest tests/test_strategy.py -v
```

---

## 📚 Next Steps

1. ✅ **Read the full README.md** for detailed documentation
2. ✅ **Explore the strategies** in `src/strategy.py`
3. ✅ **Customize configuration** in `.env`
4. ✅ **Review generated prompts** in `local_tasks/`
5. ✅ **Test strategies** in paper trading before going live

---

## 🆘 Need Help?

- **Documentation**: See `README.md`
- **Perplexity API**: https://docs.perplexity.ai/
- **Alpaca API**: https://docs.alpaca.markets/
 

---

**Happy Trading! 🚀**
