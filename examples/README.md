# Usage Examples

This directory contains comprehensive examples demonstrating how to use the Perplexity-Alpaca Trading Integration system.

## 📁 Files

- `basic_usage.py` - Basic usage examples for getting started
- `advanced_usage.py` - Advanced examples with complex strategies
- `README.md` - This documentation file

## 🚀 Quick Start

### Basic Examples

Run the basic examples to get started:

```bash
python examples/basic_usage.py
```

This will demonstrate:
- Single stock analysis
- Multi-stock analysis
- Quick analysis mode
- Account status checking
- Custom strategy generation
- Sector analysis

### Advanced Examples

Run the advanced examples for complex strategies:

```bash
python examples/advanced_usage.py
```

This will demonstrate:
- Comprehensive analysis with all data sources
- Real-time monitoring and alerts
- Risk management strategies
- Sector rotation strategies
- Earnings-based trading strategies
- Real-time data streaming

## 📊 Example Strategies

### 1. Basic Momentum Strategy
```python
integration.analyze_and_generate_task(
    tickers=["AAPL"],
    strategy_name="momentum_strategy"
)
```

### 2. Semiconductor Sector Strategy
```python
integration.analyze_and_generate_task(
    tickers=["AMD", "NVDA", "INTC"],
    strategy_name="semiconductor_momentum",
    additional_context="Focus on AI and data center trends"
)
```

### 3. Risk-Managed Strategy
```python
# See advanced_usage.py for complete example
# Includes Kelly Criterion, correlation limits, and dynamic risk management
```

### 4. Sector Rotation Strategy
```python
# See advanced_usage.py for complete example
# Analyzes multiple sectors and implements rotation logic
```

### 5. Earnings Play Strategy
```python
# See advanced_usage.py for complete example
# Focuses on earnings announcements and volatility trading
```

## 🔧 Configuration

Before running examples, ensure you have:

1. **API Keys configured** in `.env` file
2. **Dependencies installed** (`pip install -r requirements.txt`)
3. **Cursor IDE** with Background Agents enabled

## 📈 Generated Outputs

Each example generates:
- **Comprehensive prompts** for Cursor background agents
- **Structured market analysis** from Perplexity
- **Technical indicators** and price data
- **Risk management parameters**
- **Complete trading strategy specifications**

## 🎯 Next Steps

After running examples:

1. **Open Cursor** and press `Ctrl+Shift+B`
2. **Click "New Background Agent"**
3. **Copy the generated prompt** from `cursor_tasks/` directory
4. **Paste into the agent prompt field**
5. **The agent will implement** the complete trading strategy

## ⚠️ Important Notes

- **Paper trading only** - Examples use paper trading mode by default
- **API limits** - Be mindful of Perplexity and Alpaca API rate limits
- **Testing** - Always test strategies with paper trading first
- **Risk management** - Implement proper risk controls before live trading

## 🆘 Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Check your `.env` file configuration
   - Verify API keys are correct
   - Ensure you have sufficient API credits

2. **Import Errors**
   - Make sure you're running from the project root
   - Check that all dependencies are installed
   - Verify Python path configuration

3. **Cursor Agent Issues**
   - Ensure Privacy Mode is disabled
   - Check that usage-based spending is enabled
   - Verify GitHub repository connection

### Getting Help

- Check the main README.md for detailed documentation
- Review the test cases in the `tests/` directory
- Open an issue on GitHub for specific problems

## 📚 Additional Resources

- [Main Documentation](../README.md)
- [API Documentation](../docs/)
- [Test Cases](../tests/)
- [Configuration Guide](../docs/configuration.md)

---

**Happy Trading! 🚀📈**