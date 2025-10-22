# Local Trading System - No External Dependencies

A fully local trading system that operates without any external API subscriptions or dependencies. Perfect for copy-paste development and local testing.

## 🎯 Key Features

- **100% Local Operation** - No external API keys required
- **Copy-Paste Compatible** - Works entirely offline
- **Mock Data Generation** - Realistic financial data simulation
- **Local Trading Simulation** - Full trading operations without real money
- **Cursor Integration Ready** - Generate prompts for background agents

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Test the System
```bash
python local_main.py --test
```

### 3. Check Account Status
```bash
python local_main.py --status
```

### 4. Analyze Symbols
```bash
python local_main.py --symbols AAPL MSFT GOOGL --strategy local_momentum
```

### 5. Generate Cursor Prompt
```bash
python local_main.py --symbols AAPL --strategy local_momentum --generate-prompt
```

## 📁 Local System Architecture

```
src/
├── local_config.py          # Local configuration (no API keys)
├── local_data_provider.py   # Mock financial data generation
├── local_clients.py         # Local API client replacements
├── config.py               # Updated config using local settings
├── perplexity_client.py    # Local financial analysis client
└── alpaca_client.py        # Local trading client
```

## 🔧 Configuration

All configuration is handled locally in `src/local_config.py`:

```python
from src.local_config import LocalConfig

# No API keys required!
config = LocalConfig()
config.SIMULATION_MODE = True
config.INITIAL_CAPITAL = 100000.0
```

## 📊 Available Strategies

- `local_momentum` - Momentum-based trading
- `local_mean_reversion` - Mean reversion strategy  
- `local_breakout` - Breakout detection
- `local_rsi_divergence` - RSI divergence signals
- `local_moving_average_crossover` - MA crossover system
- `local_bollinger_squeeze` - Bollinger band squeeze
- `local_volume_breakout` - Volume-based breakouts

## 🎮 Usage Examples

### Basic Analysis
```python
from src.local_clients import LocalAlpacaDataClient, LocalPerplexityClient

# No API keys needed!
data_client = LocalAlpacaDataClient()
analysis_client = LocalPerplexityClient()

# Get historical data (locally generated)
data = data_client.get_historical_bars(['AAPL'], limit=100)

# Get analysis (locally generated)
analysis = analysis_client.get_technical_analysis(['AAPL'])
```

### Trading Simulation
```python
from src.local_clients import LocalAlpacaTradingClient

# No API keys needed!
trading_client = LocalAlpacaTradingClient()

# Check account (simulated)
account = trading_client.get_account()
print(f"Equity: ${account['equity']:,.2f}")

# Place order (simulated)
order = trading_client.place_market_order('AAPL', 10, 'buy')
```

## 🧪 Testing

### Run All Tests
```bash
python local_main.py --test
```

### Test Individual Components
```python
from src.local_config import LocalConfig
from src.local_clients import LocalPerplexityClient

# Test configuration
config = LocalConfig()
assert config.validate_config()

# Test data generation
client = LocalPerplexityClient()
analysis = client.get_technical_analysis(['AAPL'])
assert 'choices' in analysis
```

## 📈 Cursor Integration

### Generate Strategy Prompts
```bash
# Generate a comprehensive strategy prompt
python local_main.py --symbols AAPL MSFT --strategy local_momentum --generate-prompt

# Add custom context
python local_main.py --symbols NVDA --strategy local_breakout --generate-prompt --context "Focus on AI sector trends"
```

### Use with Cursor Background Agents
1. Run the prompt generation command
2. Copy the generated markdown file content
3. Paste into Cursor background agent
4. The agent will create a fully local trading system

## 🔒 Security & Privacy

- **No External API Calls** - All data stays local
- **No API Keys Required** - Zero external dependencies
- **Offline Operation** - Works without internet
- **Privacy Protected** - No data sent to external services

## 📦 Dependencies

Only standard Python packages required:
- `pandas` - Data manipulation
- `numpy` - Numerical computations  
- `python-dotenv` - Environment management
- `pytest` - Testing framework

**Removed Dependencies:**
- ❌ `alpaca-py` - Replaced with local simulation
- ❌ `requests` - No external API calls
- ❌ `websockets` - Local streaming simulation

## 🎯 Copy-Paste Workflow

1. **Copy this entire system** to any environment
2. **Install basic Python packages** (`pip install -r requirements.txt`)
3. **Run immediately** - no configuration needed
4. **Generate strategies** using local data
5. **Test thoroughly** with simulated trading
6. **Deploy confidently** knowing everything is local

## 🚨 Important Notes

### For Development
- All trading is simulated - no real money at risk
- Data is generated locally for testing purposes
- Performance metrics are indicative only
- Always test strategies thoroughly before live deployment

### For Production
- This system is designed for development and testing
- Real trading requires proper API integration
- Always validate strategies with real market data
- Follow proper risk management practices

## 🤝 Contributing

This local system is designed to be:
- **Self-contained** - No external dependencies
- **Modular** - Easy to extend and modify
- **Educational** - Clear code structure and documentation
- **Practical** - Ready for real strategy development

## 📄 License

MIT License - Use freely for educational and development purposes.

---

**🎉 Ready to trade locally! No subscriptions, no API keys, no external dependencies.**