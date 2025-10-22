"""
Prompt generation layer for Cursor background agents
Converts financial data into structured prompts for autonomous trading bot development
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from .config import Config

class CursorPromptGenerator:
    """Generates structured prompts for Cursor background agents"""
    
    def __init__(self):
        self.tasks_dir = Config.CURSOR_TASKS_DIR
        os.makedirs(self.tasks_dir, exist_ok=True)
    
    def generate_trading_strategy_prompt(self, 
                                       market_data: Dict[str, Any],
                                       strategy_type: str,
                                       tickers: List[str],
                                       additional_context: str = "") -> str:
        """
        Generate a comprehensive prompt for Cursor background agent to implement trading strategy
        
        Args:
            market_data: Dictionary containing all financial analysis data
            strategy_type: Type of strategy to implement
            tickers: List of stock symbols
            additional_context: Any additional context or requirements
            
        Returns:
            Formatted prompt string for Cursor agent
        """
        
        # Extract data components
        sec_analysis = market_data.get("sec_filings", "No SEC data available")
        news_sentiment = market_data.get("news_sentiment", "No news data available")
        earnings_analysis = market_data.get("earnings", "No earnings data available")
        technical_analysis = market_data.get("technical", "No technical data available")
        sector_analysis = market_data.get("sector", "No sector data available")
        price_data = market_data.get("price_data", "No price data available")
        
        prompt = f"""# Advanced Trading Strategy Implementation Task

## 🎯 Mission
Build a sophisticated Python trading bot using local simulation that implements a **{strategy_type}** strategy for {', '.join(tickers)} based on comprehensive financial analysis.

## 📊 Market Context & Analysis

### SEC Filings Analysis
{sec_analysis}

### Market News & Sentiment
{news_sentiment}

### Earnings Analysis
{earnings_analysis}

### Technical Analysis
{technical_analysis}

### Sector Analysis
{sector_analysis}

### Recent Price Action
{price_data}

{additional_context}

## 🏗️ Implementation Requirements

### 1. Core Architecture
Create a modular, production-ready trading system with the following components:

**File Structure:**
```
src/
├── config.py              # Configuration and API keys
├── data_handler.py        # Alpaca data streaming and storage
├── strategy.py            # Trading logic implementation
├── risk_manager.py        # Risk management and position sizing
├── executor.py            # Order execution and management
├── portfolio_manager.py   # Portfolio tracking and rebalancing
├── logger.py              # Comprehensive logging system
└── main.py                # Main execution loop
```

### 2. Data Integration (data_handler.py)
- **Real-time Data Streaming**: Use Alpaca's WebSocket API for live price feeds
- **Historical Data**: Implement efficient data storage using pandas DataFrames
- **Data Validation**: Add comprehensive data quality checks and error handling
- **Performance Optimization**: Cache frequently accessed data and implement efficient data structures

```python
# Example structure for data_handler.py
class AlpacaDataHandler:
    def __init__(self, api_key, secret_key, paper=True):
        # Initialize Alpaca clients
        pass
    
    async def start_streaming(self, symbols):
        # WebSocket streaming implementation
        pass
    
    def get_historical_data(self, symbol, timeframe, start_date, end_date):
        # Historical data retrieval
        pass
    
    def calculate_technical_indicators(self, data):
        # Technical analysis calculations
        pass
```

### 3. Strategy Implementation (strategy.py)
Implement the **{strategy_type}** strategy with the following features:

**Core Strategy Logic:**
- **Entry Signals**: Based on technical indicators, fundamental analysis, and market sentiment
- **Exit Signals**: Implement multiple exit conditions (profit targets, stop losses, time-based)
- **Position Sizing**: Dynamic position sizing based on volatility and risk tolerance
- **Market Regime Detection**: Adapt strategy based on market conditions (trending vs. ranging)

**Technical Indicators to Include:**
- Moving averages (SMA, EMA, WMA)
- Momentum indicators (RSI, MACD, Stochastic)
- Volatility indicators (Bollinger Bands, ATR)
- Volume analysis (Volume Profile, OBV)
- Custom indicators based on the analysis above

**Fundamental Integration:**
- Incorporate earnings data and SEC filing insights
- Use sentiment analysis for position timing
- Factor in sector rotation and macro trends

### 4. Risk Management (risk_manager.py)
Implement comprehensive risk management:

**Position Sizing:**
- Kelly Criterion for optimal position sizing
- Maximum position size limits (configurable)
- Correlation-based position limits
- Volatility-adjusted position sizing

**Risk Controls:**
- Stop-loss orders (trailing and fixed)
- Take-profit targets
- Maximum drawdown limits
- Daily loss limits
- Sector concentration limits

**Portfolio Management:**
- Real-time P&L tracking
- Risk-adjusted return calculations
- Portfolio heat mapping
- Rebalancing logic

### 5. Order Execution (executor.py)
Robust order management system:

**Order Types:**
- Market orders for immediate execution
- Limit orders for better pricing
- Bracket orders for automated risk management
- Stop orders for risk control

**Execution Features:**
- Order routing optimization
- Slippage minimization
- Fill quality analysis
- Order status tracking and alerts

### 6. Advanced Features

**Machine Learning Integration:**
- Implement basic ML models for signal enhancement
- Use historical data for model training
- Feature engineering from technical indicators
- Model performance tracking

**Backtesting Framework:**
- Historical strategy testing
- Walk-forward analysis
- Monte Carlo simulation
- Performance attribution analysis

**Monitoring & Alerts:**
- Real-time performance monitoring
- Email/SMS alerts for important events
- Dashboard for strategy performance
- Log analysis and debugging tools

## 🔧 Technical Specifications

### Dependencies
```python
# Add to requirements.txt
alpaca-py>=0.20.0
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
websockets>=11.0.0
asyncio>=3.4.3
python-dotenv>=1.0.0
```

### Configuration Management
- Use environment variables for all sensitive data
- Implement configuration validation
- Support both paper and live trading modes
- Easy strategy parameter adjustment

### Error Handling & Logging
- Comprehensive error handling for all API calls
- Structured logging with different levels
- Automatic retry logic for failed operations
- Graceful degradation when services are unavailable

### Testing Requirements
- Unit tests for all core functions
- Integration tests with Alpaca API
- Strategy backtesting validation
- Performance benchmarking

## 📈 Performance Targets

**Trading Performance:**
- Target Sharpe ratio > 1.5
- Maximum drawdown < 10%
- Win rate > 55%
- Profit factor > 1.3

**System Performance:**
- Sub-second order execution
- 99.9% uptime
- Real-time data processing
- Efficient memory usage

## 🚀 Implementation Steps

1. **Setup & Configuration**: Initialize Alpaca clients and configure environment
2. **Data Pipeline**: Implement real-time data streaming and historical data access
3. **Strategy Core**: Build the main trading logic based on the analysis above
4. **Risk Management**: Implement comprehensive risk controls
5. **Order Execution**: Build robust order management system
6. **Testing & Validation**: Comprehensive testing and backtesting
7. **Monitoring**: Real-time monitoring and alerting system
8. **Documentation**: Complete documentation and usage examples

## ⚠️ Important Constraints

- **Use alpaca-py library** (not deprecated alpaca-trade-api)
- **Paper trading only** initially - no live trading without explicit approval
- **Rate limiting** - respect Alpaca's API limits
- **Error handling** - graceful handling of all edge cases
- **Security** - never hardcode API keys or sensitive data
- **Testing** - comprehensive testing before any live deployment

## 🎯 Success Criteria

The implementation will be considered successful when:
1. All core components are implemented and tested
2. Strategy shows positive performance in backtesting
3. Real-time data streaming works reliably
4. Risk management prevents significant losses
5. Code is production-ready with proper error handling
6. Comprehensive documentation is provided

## 📝 Additional Notes

- Focus on code quality and maintainability
- Implement proper async/await patterns for WebSocket connections
- Use type hints throughout the codebase
- Follow PEP 8 style guidelines
- Add comprehensive docstrings for all functions
- Implement proper exception handling and logging

---

**Generated on**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Strategy Type**: {strategy_type}
**Target Symbols**: {', '.join(tickers)}
**Analysis Date**: {datetime.now().strftime("%Y-%m-%d")}

This prompt provides comprehensive context for building a sophisticated trading system. The Cursor background agent should use this information to create a production-ready implementation that incorporates all the financial analysis and technical requirements specified above.
"""

        return prompt
    
    def save_prompt_to_file(self, prompt: str, strategy_name: str, 
                           tickers: List[str]) -> str:
        """
        Save the generated prompt to a file for Cursor background agent
        
        Args:
            prompt: The generated prompt string
            strategy_name: Name of the strategy
            tickers: List of tickers for the strategy
            
        Returns:
            Path to the saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{strategy_name}_{'_'.join(tickers)}_{timestamp}.md"
        filepath = os.path.join(self.tasks_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(prompt)
        
        print(f"✅ Cursor prompt saved to: {filepath}")
        return filepath
    
    def generate_quick_strategy_prompt(self, ticker: str, 
                                     strategy_type: str = "momentum") -> str:
        """
        Generate a quick prompt for simple strategy implementation
        
        Args:
            ticker: Stock symbol
            strategy_type: Type of strategy
            
        Returns:
            Simplified prompt string
        """
        prompt = f"""# Quick Trading Strategy Implementation

## Task
Build a Python trading bot for {ticker} using a {strategy_type} strategy on Alpaca's platform.

## Requirements
1. Connect to Alpaca's Market Data API
2. Implement {strategy_type} trading logic
3. Add basic risk management (stop-loss, take-profit)
4. Use paper trading mode
5. Include logging and error handling

## Files to Create
- `config.py`: API configuration
- `strategy.py`: Trading logic
- `executor.py`: Order execution
- `main.py`: Main execution loop

## Implementation Notes
- Use alpaca-py library
- Implement proper async/await for WebSocket
- Add comprehensive error handling
- Include unit tests

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        return prompt
    
    def create_cursor_agent_instructions(self) -> str:
        """
        Create instructions for setting up Cursor background agents
        
        Returns:
            Instructions string
        """
        instructions = f"""
# Cursor Background Agent Setup Instructions

## Prerequisites
1. **Disable Privacy Mode** in Cursor settings
2. **Enable usage-based spending** (minimum $10 funding)
3. **Connect GitHub repository** with read-write privileges
4. **Configure environment** with .cursor/environment.json

## How to Use Generated Prompts

### Method 1: Manual Launch
1. Open Cursor and press `Ctrl+Shift+B` (or `⌘B` on Mac)
2. Click "New Background Agent"
3. Copy the contents of the generated prompt file
4. Paste into the agent prompt field
5. The agent will create a new branch and implement the strategy

### Method 2: GitHub Issues (Workaround)
1. Create a new GitHub issue with the prompt content
2. Use Linear integration to delegate to Cursor agent
3. The agent will process the issue and implement the solution

### Method 3: Direct File Integration
1. Place prompt files in the `{self.tasks_dir}/` directory
2. Use Cursor's file-based agent triggers (if available)
3. Monitor the agent's progress through the Cursor interface

## Generated Files Location
All generated prompts are saved in: `{os.path.abspath(self.tasks_dir)}/`

## Next Steps After Agent Completion
1. Review the generated code
2. Test the implementation with paper trading
3. Validate strategy performance
4. Deploy to live trading (if approved)
5. Monitor and optimize performance

## Troubleshooting
- Ensure all API keys are properly configured
- Check Cursor agent logs for any errors
- Verify Alpaca API connectivity
- Test with small position sizes initially
"""
        return instructions
