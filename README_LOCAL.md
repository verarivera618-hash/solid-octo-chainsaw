# Local Trading System - No External Dependencies

This is a completely local version of the trading system that requires NO external API subscriptions, keys, or services. Everything runs on your local machine with simulated data.

## Features

- ✅ **100% Local Operation** - No external API calls
- ✅ **No Subscriptions Required** - Completely free to use
- ✅ **Paper Trading Simulation** - Test strategies without real money
- ✅ **Local Data Generation** - Realistic market data simulation
- ✅ **Technical Analysis** - Full suite of indicators
- ✅ **Backtesting Engine** - Test strategies on historical data
- ✅ **Risk Management** - Built-in risk analytics
- ✅ **SQLite Database** - Local data storage

## Quick Start

### Python Version

1. Install dependencies:
```bash
pip install -r requirements_local.txt
```

2. Run the local trading system:
```bash
python src/local_main.py
```

### TypeScript Version

1. Install dependencies:
```bash
npm install
```

2. Build the project:
```bash
npm run build
```

3. Run the system:
```bash
npm start
```

## Architecture

### Core Components

1. **LocalDataClient** (`src/local_data_client.py`)
   - Generates realistic market data
   - Stores data in SQLite database
   - Calculates technical indicators
   - No external API calls

2. **LocalTradingClient** (`src/local_trading_client.py`)
   - Simulates order execution
   - Manages paper trading portfolio
   - Tracks positions and P&L
   - Handles all order types

3. **LocalAnalysisClient** (`src/local_analysis_client.py`)
   - Technical analysis engine
   - Momentum scoring
   - Risk analysis
   - Pattern recognition
   - All computation done locally

4. **LocalConfig** (`src/config_local.py`)
   - Configuration management
   - No API keys needed
   - Local endpoints only

## Usage Examples

### Generate Sample Data
```python
from src.local_data_client import LocalDataClient

client = LocalDataClient()
data = client.generate_sample_data(['AAPL', 'GOOGL', 'MSFT'], days=365)
```

### Run a Backtest
```python
from src.local_main import LocalTradingSystem

system = LocalTradingSystem()
results = system.run_backtest(
    symbols=['AAPL', 'GOOGL'],
    strategy='momentum',
    days=30
)
```

### Paper Trading
```python
system = LocalTradingSystem()
system.run_paper_trading(
    symbols=['NVDA', 'AMD'],
    strategy='mean_reversion'
)
```

### Get Market Analysis
```python
from src.local_analysis_client import LocalAnalysisClient

analyst = LocalAnalysisClient()
analysis = analyst.get_market_analysis(['AAPL', 'MSFT'])
```

## Strategies Included

1. **Momentum Strategy**
   - Based on RSI and MACD indicators
   - Identifies trending stocks

2. **Mean Reversion Strategy**
   - Uses Bollinger Bands
   - Trades oversold/overbought conditions

3. **Moving Average Crossover**
   - Classic SMA 20/50 strategy
   - Golden cross and death cross signals

## Database Schema

The system uses SQLite with the following tables:

- `stock_data` - Historical price data
- `quotes` - Real-time quote simulation
- `account` - Account balance and info
- `positions` - Current holdings
- `orders` - Order history
- `trades` - Executed trades

## Local API Endpoints

The system can optionally expose local REST endpoints:

- `http://localhost:8080/api/data` - Market data
- `http://localhost:8080/api/trading` - Trading operations
- `http://localhost:8080/api/analysis` - Analysis results
- `http://localhost:8080/api/backtest` - Backtesting
- `http://localhost:8080/api/portfolio` - Portfolio management

## Configuration

Edit `src/config_local.py` to customize:

```python
INITIAL_CAPITAL = 100000.0  # Starting balance
MAX_POSITION_SIZE = 0.1     # 10% per position
COMMISSION_RATE = 0.001     # 0.1% commission
SLIPPAGE_RATE = 0.0005      # 0.05% slippage
```

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

## Copy-Paste Ready

This entire system can be copied to any machine and will work immediately without any external setup:

1. Copy all files
2. Install Python dependencies (pandas, numpy)
3. Run `python src/local_main.py`

No API keys, no subscriptions, no external services required!

## Data Sources

The system can work with:
- Generated sample data (built-in)
- CSV files (import your own)
- JSON files (import your own)
- SQLite database (automatic)

## Limitations

Since this runs locally without external data:
- Historical data is simulated (unless you import your own)
- Real-time quotes are simulated
- No actual trading (paper trading only)
- No real market news or events

## Future Enhancements

Potential additions while keeping it local:
- Web interface (Flask/FastAPI)
- More technical indicators
- Machine learning strategies (scikit-learn)
- Portfolio optimization
- Monte Carlo simulations
- More chart patterns

## License

MIT License - Free to use, modify, and distribute

## Support

This is a standalone system requiring no external support. All functionality is self-contained and documented in the code.