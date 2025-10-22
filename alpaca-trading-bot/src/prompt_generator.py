"""
Prompt generation layer for Cursor background agents
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
from loguru import logger
from enum import Enum


class StrategyType(Enum):
    """Trading strategy types"""
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    PAIRS_TRADING = "pairs_trading"
    SENTIMENT_BASED = "sentiment_based"
    FUNDAMENTAL_VALUE = "fundamental_value"
    OPTIONS_SPREAD = "options_spread"
    MARKET_MAKING = "market_making"
    ARBITRAGE = "arbitrage"


class CursorPromptGenerator:
    """Generates prompts for Cursor background agents based on financial data"""
    
    def __init__(self, output_dir: str = "cursor_tasks"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.prompt_templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Load prompt templates for different strategies"""
        return {
            StrategyType.MOMENTUM: self._momentum_template(),
            StrategyType.MEAN_REVERSION: self._mean_reversion_template(),
            StrategyType.SENTIMENT_BASED: self._sentiment_template(),
            StrategyType.FUNDAMENTAL_VALUE: self._fundamental_template(),
            StrategyType.PAIRS_TRADING: self._pairs_trading_template(),
        }
    
    def generate_prompt(
        self,
        financial_data: Dict[str, Any],
        strategy_type: StrategyType,
        tickers: List[str],
        additional_requirements: Optional[str] = None
    ) -> str:
        """Generate a comprehensive prompt for Cursor agent"""
        
        base_template = self.prompt_templates.get(
            strategy_type,
            self._default_template()
        )
        
        # Format the financial data
        formatted_data = self._format_financial_data(financial_data)
        
        # Build the complete prompt
        prompt = f"""
# 🚀 Automated Trading Bot Implementation Task

## 📊 Market Analysis & Context

{formatted_data}

## 🎯 Implementation Requirements

### Strategy: {strategy_type.value.replace('_', ' ').title()}
**Target Assets:** {', '.join(tickers)}

{base_template}

## 📁 Required File Structure

Create the following files with complete implementation:

```
alpaca-trading-bot/
├── src/
│   ├── config.py              # Configuration management
│   ├── data_handler.py        # Alpaca data streaming
│   ├── indicators.py          # Technical indicators
│   ├── strategy.py            # Trading strategy logic
│   ├── risk_manager.py        # Risk management
│   ├── executor.py            # Order execution
│   ├── portfolio.py           # Portfolio management
│   ├── backtester.py          # Backtesting engine
│   └── monitor.py             # Real-time monitoring
├── tests/
│   ├── test_strategy.py       # Strategy unit tests
│   ├── test_risk_manager.py   # Risk management tests
│   ├── test_executor.py       # Execution tests
│   └── test_integration.py    # Integration tests
├── notebooks/
│   └── strategy_analysis.ipynb # Analysis notebook
├── logs/
│   └── .gitkeep
├── docker-compose.yml          # Container orchestration
├── Dockerfile                  # Container definition
├── main.py                     # Main execution entry
└── README.md                   # Documentation
```

## 🔧 Technical Implementation Details

### 1. Data Handler (`data_handler.py`)
```python
# Implement real-time data streaming from Alpaca
# - WebSocket connection for live bars and trades
# - Historical data fetching with caching
# - Data normalization and cleaning
# - Support for multiple timeframes
```

### 2. Strategy Module (`strategy.py`)
```python
# Implement the {strategy_type.value} strategy
# - Signal generation based on indicators
# - Entry and exit logic
# - Position sizing calculations
# - Multi-timeframe analysis
```

### 3. Risk Manager (`risk_manager.py`)
```python
# Comprehensive risk management
# - Position size limits
# - Portfolio heat management
# - Correlation analysis
# - Drawdown protection
# - Stop-loss and take-profit management
```

### 4. Order Executor (`executor.py`)
```python
# Smart order execution
# - Market, limit, and stop orders
# - Bracket orders for risk management
# - Order tracking and management
# - Slippage handling
# - Failed order retry logic
```

### 5. Testing Suite
- Unit tests with >80% coverage
- Integration tests with mock Alpaca API
- Backtesting on historical data
- Performance metrics calculation

## ⚙️ Configuration Requirements

### Environment Variables
```env
ALPACA_API_KEY=<paper_trading_key>
ALPACA_SECRET_KEY=<paper_trading_secret>
ENABLE_WEBSOCKET=true
MAX_POSITION_SIZE=0.1
STOP_LOSS_PERCENT=2
TAKE_PROFIT_PERCENT=5
```

### Docker Configuration
```dockerfile
FROM python:3.11-slim
# Complete Dockerfile with all dependencies
```

## 🎨 Implementation Guidelines

1. **Code Quality**
   - Type hints for all functions
   - Comprehensive docstrings
   - Clean, modular architecture
   - Async/await for I/O operations

2. **Error Handling**
   - Graceful API failure handling
   - Connection retry logic
   - Circuit breakers for API limits
   - Comprehensive logging

3. **Performance**
   - Efficient data structures
   - Minimal API calls
   - Caching where appropriate
   - Vectorized calculations with NumPy

4. **Monitoring**
   - Real-time performance metrics
   - Trade logging
   - Alert system for anomalies
   - Prometheus metrics export

{additional_requirements if additional_requirements else ""}

## 🚦 Success Criteria

1. ✅ All tests passing (pytest)
2. ✅ Successfully connects to Alpaca paper trading
3. ✅ Executes trades based on strategy signals
4. ✅ Implements proper risk management
5. ✅ Logs all decisions and trades
6. ✅ Handles errors gracefully
7. ✅ Documentation complete

## 🔄 Post-Implementation Tasks

1. Run backtesting on 6 months of historical data
2. Calculate Sharpe ratio, max drawdown, win rate
3. Optimize strategy parameters
4. Set up monitoring dashboard
5. Create deployment guide

---
**Note:** Focus on production-ready code with proper error handling, testing, and documentation. The bot should be ready to run in paper trading mode immediately after implementation.
"""
        
        return prompt
    
    def _format_financial_data(self, data: Dict[str, Any]) -> str:
        """Format financial data for inclusion in prompt"""
        
        formatted = []
        
        if "analysis" in data:
            for analysis_type, content in data["analysis"].items():
                if content and "content" in content:
                    formatted.append(f"### {analysis_type.upper()}\n{content['content']}\n")
        
        if "market_data" in data:
            formatted.append(f"### MARKET DATA\n{json.dumps(data['market_data'], indent=2)}\n")
        
        if "signals" in data:
            formatted.append(f"### TRADING SIGNALS\n{json.dumps(data['signals'], indent=2)}\n")
        
        return "\n".join(formatted) if formatted else "No financial data provided"
    
    def _momentum_template(self) -> str:
        """Template for momentum strategy"""
        return """
### Strategy Specifics: Momentum Trading

Implement a momentum-based strategy with the following components:

1. **Indicators:**
   - RSI (14-period) for momentum confirmation
   - MACD for trend direction
   - Volume analysis for breakout confirmation
   - ATR for volatility-based position sizing

2. **Entry Conditions:**
   - Price breaks above 20-day high
   - RSI > 50 and rising
   - MACD line crosses above signal line
   - Volume > 1.5x 20-day average

3. **Exit Conditions:**
   - Trailing stop at 2x ATR
   - RSI divergence detected
   - Price closes below 10-day MA

4. **Risk Management:**
   - Max 3 concurrent positions
   - Position size based on ATR
   - Daily loss limit of 2% of portfolio
"""
    
    def _mean_reversion_template(self) -> str:
        """Template for mean reversion strategy"""
        return """
### Strategy Specifics: Mean Reversion

Implement a mean reversion strategy with the following components:

1. **Indicators:**
   - Bollinger Bands (20, 2)
   - RSI for oversold/overbought conditions
   - Volume-weighted average price (VWAP)
   - Z-score for deviation measurement

2. **Entry Conditions:**
   - Price touches lower Bollinger Band
   - RSI < 30 (oversold)
   - Price > 2 standard deviations below VWAP
   - No major news events

3. **Exit Conditions:**
   - Price reaches middle Bollinger Band
   - RSI > 50
   - Stop loss at 3% below entry

4. **Risk Management:**
   - Scale into positions (1/3 at each level)
   - Max exposure per symbol: 5% of portfolio
   - Avoid trades during earnings season
"""
    
    def _sentiment_template(self) -> str:
        """Template for sentiment-based strategy"""
        return """
### Strategy Specifics: Sentiment-Based Trading

Implement a sentiment-driven strategy:

1. **Data Sources:**
   - Perplexity sentiment analysis
   - News sentiment scoring
   - Social media mentions trend
   - Options flow analysis

2. **Entry Conditions:**
   - Sentiment score > 0.7 (bullish)
   - Increasing positive mentions
   - Call/Put ratio > 1.5
   - Positive news catalyst identified

3. **Exit Conditions:**
   - Sentiment turns negative
   - Take profit at 5%
   - Stop loss at 2%

4. **Risk Management:**
   - Reduce position size during high volatility
   - No trades during major economic releases
   - Daily sentiment monitoring
"""
    
    def _fundamental_template(self) -> str:
        """Template for fundamental value strategy"""
        return """
### Strategy Specifics: Fundamental Value Investing

Implement a fundamental analysis strategy:

1. **Screening Criteria:**
   - P/E ratio below industry average
   - Positive earnings growth
   - Strong cash flow
   - Low debt-to-equity ratio

2. **Entry Conditions:**
   - Stock trades below intrinsic value
   - Recent positive earnings surprise
   - Insider buying detected
   - Technical support confirmed

3. **Exit Conditions:**
   - Stock reaches fair value
   - Fundamental deterioration
   - Better opportunity identified

4. **Risk Management:**
   - Diversify across sectors
   - Position size based on conviction
   - Regular rebalancing monthly
"""
    
    def _pairs_trading_template(self) -> str:
        """Template for pairs trading strategy"""
        return """
### Strategy Specifics: Statistical Pairs Trading

Implement a pairs trading strategy:

1. **Pair Selection:**
   - Cointegration test (p-value < 0.05)
   - Historical correlation > 0.8
   - Same sector/industry
   - Similar market cap

2. **Entry Conditions:**
   - Z-score > 2 or < -2
   - Mean reversion expected
   - No earnings/events upcoming
   - Adequate liquidity

3. **Exit Conditions:**
   - Z-score returns to 0
   - Pair correlation breaks
   - Maximum holding period (10 days)

4. **Risk Management:**
   - Dollar-neutral positions
   - Stop loss at z-score = 3
   - Max 5 pairs simultaneously
"""
    
    def _default_template(self) -> str:
        """Default strategy template"""
        return """
### Strategy: Custom Implementation

Implement a flexible trading strategy based on the provided financial data.
Focus on risk-adjusted returns and capital preservation.
"""
    
    def save_prompt(
        self,
        prompt: str,
        strategy_name: str,
        tickers: List[str]
    ) -> Path:
        """Save prompt to file for Cursor agent"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{strategy_name}_{'-'.join(tickers)}_{timestamp}.md"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(prompt)
        
        logger.info(f"Prompt saved to: {filepath}")
        
        # Also create a latest symlink for easy access
        latest_link = self.output_dir / f"{strategy_name}_latest.md"
        if latest_link.exists():
            latest_link.unlink()
        latest_link.symlink_to(filepath.name)
        
        return filepath
    
    def generate_and_save(
        self,
        financial_data: Dict[str, Any],
        strategy_type: StrategyType,
        tickers: List[str],
        additional_requirements: Optional[str] = None
    ) -> Path:
        """Generate and save prompt in one step"""
        
        prompt = self.generate_prompt(
            financial_data,
            strategy_type,
            tickers,
            additional_requirements
        )
        
        return self.save_prompt(
            prompt,
            strategy_type.value,
            tickers
        )