
# Trading Strategy Implementation Task

## Context

## SEC Filings Analysis
Demo SEC summary for: AMD, NVDA, INTC

## Market News & Sentiment
Demo news and sentiment for: AMD, NVDA, INTC

## Recent Price Action (Last 30 Days)
AMD: $100.00 (+2.00% over period)
NVDA: $100.00 (+2.00% over period)
INTC: $100.00 (+2.00% over period)


## Task
Build a Python trading bot on Alpaca's platform that:

1. **Data Integration**
   - Connect to Alpaca's Market Data API using alpaca-py SDK
   - Set up WebSocket streaming for real-time price updates
   - Store historical data using pandas DataFrames

2. **Strategy Implementation** (semiconductor_momentum_strategy)
   - Implement entry/exit logic based on the financial analysis above
   - Include risk management with stop-loss and take-profit levels
   - Add position sizing based on portfolio percentage

3. **Alpaca Trading Integration**
   - Use Alpaca Trading API for order execution
   - Implement bracket orders for automated risk management
   - Add logging for all trades and decisions

4. **Testing Requirements**
   - Use Alpaca's paper trading environment
   - Create unit tests for strategy logic
   - Add backtesting functionality using historical data

## Code Structure
Create the following files:
- `src/config.py`: API keys and configuration
- `src/data_handler.py`: Alpaca data streaming and storage
- `src/strategy.py`: Trading logic implementation
- `src/executor.py`: Order execution and management
- `main.py`: Main execution loop
- `tests/test_strategy.py`: Unit tests

## Constraints
- Use alpaca-py library (not deprecated alpaca-trade-api)
- Implement proper error handling for API calls
- Add rate limiting to respect Alpaca's API limits
- Use async/await for WebSocket connections
