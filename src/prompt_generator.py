"""
Cursor Background Agent Prompt Generator
Converts financial insights into actionable Cursor agent prompts
"""

import os
import json
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass

from src.perplexity_client import FinancialInsight
from src.config import config

import logging
logger = logging.getLogger(__name__)


@dataclass
class CursorPrompt:
    """Container for generated Cursor agent prompts"""
    title: str
    content: str
    strategy_name: str
    tickers: List[str]
    timestamp: datetime
    file_path: str
    metadata: Dict


class PromptGenerator:
    """Generate Cursor background agent prompts from financial data"""
    
    STRATEGY_TEMPLATES = {
        "momentum": {
            "name": "Momentum Trading Strategy",
            "description": "Trend-following strategy based on price momentum and volume",
            "indicators": ["RSI", "MACD", "Volume", "Moving Averages"],
            "timeframe": "Intraday to Daily"
        },
        "mean_reversion": {
            "name": "Mean Reversion Strategy",
            "description": "Capitalize on price reversions to mean/support levels",
            "indicators": ["Bollinger Bands", "RSI", "Standard Deviation"],
            "timeframe": "Short-term (minutes to hours)"
        },
        "breakout": {
            "name": "Breakout Trading Strategy",
            "description": "Trade breakouts from consolidation patterns",
            "indicators": ["Volume", "ATR", "Support/Resistance"],
            "timeframe": "Daily to Weekly"
        },
        "news_driven": {
            "name": "News-Driven Event Strategy",
            "description": "Algorithmic response to news events and announcements",
            "indicators": ["Sentiment Score", "Volume Spike", "Price Gap"],
            "timeframe": "Immediate to Daily"
        },
        "earnings_play": {
            "name": "Earnings Play Strategy",
            "description": "Trade around earnings announcements based on historical patterns",
            "indicators": ["Implied Volatility", "Historical Earnings Reaction", "Options Flow"],
            "timeframe": "Days before/after earnings"
        },
        "sector_rotation": {
            "name": "Sector Rotation Strategy",
            "description": "Rotate between sectors based on relative strength",
            "indicators": ["Relative Strength", "Sector ETF Performance", "Economic Indicators"],
            "timeframe": "Weekly to Monthly"
        }
    }
    
    def __init__(self, tasks_dir: Optional[str] = None):
        self.tasks_dir = tasks_dir or config.cursor_tasks_dir
        os.makedirs(self.tasks_dir, exist_ok=True)
    
    def generate_trading_strategy_prompt(
        self,
        sec_insights: Optional[FinancialInsight] = None,
        news_insights: Optional[FinancialInsight] = None,
        earnings_insights: Optional[FinancialInsight] = None,
        sector_insights: Optional[FinancialInsight] = None,
        price_data_summary: Optional[str] = None,
        strategy_type: str = "momentum",
        tickers: Optional[List[str]] = None,
        custom_instructions: Optional[str] = None
    ) -> CursorPrompt:
        """
        Generate comprehensive Cursor agent prompt for trading strategy
        
        Args:
            sec_insights: SEC filings analysis
            news_insights: Market news insights
            earnings_insights: Earnings analysis
            sector_insights: Sector-wide analysis
            price_data_summary: Recent price action summary
            strategy_type: Type of strategy to implement
            tickers: List of target tickers
            custom_instructions: Additional custom requirements
        
        Returns:
            CursorPrompt object with complete prompt and metadata
        """
        strategy_info = self.STRATEGY_TEMPLATES.get(
            strategy_type, 
            self.STRATEGY_TEMPLATES["momentum"]
        )
        
        # Aggregate tickers from all insights
        all_tickers = set(tickers or [])
        for insight in [sec_insights, news_insights, earnings_insights, sector_insights]:
            if insight:
                all_tickers.update(insight.tickers)
        tickers_list = sorted(list(all_tickers))
        
        # Build context section
        context = self._build_context_section(
            sec_insights, news_insights, earnings_insights, 
            sector_insights, price_data_summary
        )
        
        # Generate prompt content
        prompt_content = f"""# Trading Strategy Implementation: {strategy_info['name']}

## 📊 Market Context

{context}

## 🎯 Strategy Overview

**Strategy Type:** {strategy_info['name']}
**Description:** {strategy_info['description']}
**Target Tickers:** {', '.join(tickers_list)}
**Key Indicators:** {', '.join(strategy_info['indicators'])}
**Timeframe:** {strategy_info['timeframe']}

## 🛠️ Implementation Requirements

### 1. Project Structure
Create the following files with proper organization:

```
alpaca_trading_bot/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration and API keys
│   ├── data_handler.py        # Alpaca data streaming
│   ├── strategy.py            # Core trading logic
│   ├── executor.py            # Order execution and management
│   ├── risk_manager.py        # Risk management and position sizing
│   └── logger.py              # Logging utilities
├── tests/
│   ├── test_strategy.py       # Strategy unit tests
│   ├── test_executor.py       # Execution tests
│   └── test_integration.py    # Integration tests
├── backtest/
│   └── backtest_runner.py     # Backtesting framework
├── main.py                     # Main execution loop
├── requirements.txt            # Dependencies
└── README.md                   # Documentation
```

### 2. Data Integration (`data_handler.py`)

**Requirements:**
- Use `alpaca-py` SDK (NOT deprecated alpaca-trade-api)
- Implement WebSocket streaming for real-time data
- Support both historical and live data fetching
- Cache data efficiently using pandas DataFrames
- Handle reconnections and error recovery

**Key Features:**
```python
class AlpacaDataHandler:
    - async def stream_bars(symbols, timeframe)
    - async def stream_trades(symbols)
    - def get_historical_bars(symbols, start, end, timeframe)
    - def get_latest_quote(symbol)
    - def get_latest_trade(symbol)
```

### 3. Strategy Implementation (`strategy.py`)

Based on the market analysis above, implement:

**Entry Signals:**
{self._generate_entry_logic(strategy_type, sec_insights, news_insights)}

**Exit Signals:**
{self._generate_exit_logic(strategy_type)}

**Risk Management:**
- Position sizing: {config.trading.max_position_size * 100}% of portfolio max
- Stop loss: {config.trading.stop_loss_pct * 100}%
- Take profit: {config.trading.take_profit_pct * 100}%
- Max daily trades: {config.trading.max_daily_trades}
- Risk per trade: {config.trading.risk_per_trade * 100}%

**Strategy Class Structure:**
```python
class TradingStrategy:
    def analyze(self, market_data) -> Signal
    def calculate_position_size(self, account, signal) -> int
    def should_enter(self, data) -> bool
    def should_exit(self, position, data) -> bool
    def get_stop_loss_price(self, entry_price, side) -> float
    def get_take_profit_price(self, entry_price, side) -> float
```

### 4. Order Execution (`executor.py`)

**Requirements:**
- Use Alpaca Trading API for order management
- Implement bracket orders (entry + stop loss + take profit)
- Handle order rejections and partial fills
- Track position state and P&L
- Implement rate limiting (200 requests/minute for Alpaca)

**Executor Features:**
```python
class OrderExecutor:
    - def submit_bracket_order(symbol, qty, side, stop_loss, take_profit)
    - def submit_market_order(symbol, qty, side)
    - def cancel_order(order_id)
    - def get_open_positions()
    - def close_position(symbol)
    - def get_account_info()
```

### 5. Risk Management (`risk_manager.py`)

Implement comprehensive risk controls:
- Portfolio-level position limits
- Maximum drawdown checks
- Daily loss limits
- Correlation-based position limits
- Volatility-adjusted position sizing

### 6. Backtesting Framework

**Requirements:**
- Use historical data from Alpaca
- Simulate order execution with realistic slippage
- Calculate performance metrics (Sharpe, Max DD, Win Rate)
- Generate trade logs and visualizations
- Support parameter optimization

### 7. Main Execution Loop (`main.py`)

**Workflow:**
1. Initialize Alpaca connections (trading + data)
2. Load strategy configuration
3. Start real-time data streams
4. Monitor for signals
5. Execute trades based on strategy
6. Update positions and risk metrics
7. Log all activities

**Features:**
- Async/await for concurrent operations
- Graceful shutdown handling
- Health checks and monitoring
- Paper trading mode (default)
- Dry-run mode for testing

## 📦 Dependencies

Include in `requirements.txt`:
```
alpaca-py>=0.21.0
pandas>=2.0.0
numpy>=1.24.0
python-dotenv>=1.0.0
asyncio>=3.4.3
websockets>=12.0
pytest>=7.4.0
ta-lib>=0.4.28  # Technical analysis
```

## 🔐 Configuration

Create `.env.example`:
```
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here
ALPACA_PAPER_TRADING=true

MAX_POSITION_SIZE=0.1
STOP_LOSS_PCT=0.02
TAKE_PROFIT_PCT=0.05
MAX_DAILY_TRADES=10
RISK_PER_TRADE=0.01
```

## ✅ Testing Requirements

### Unit Tests
- Test strategy logic with historical data
- Test order execution with mocked API
- Test risk management calculations
- Test data handler error recovery

### Integration Tests
- Test full workflow with paper trading
- Test WebSocket connectivity
- Test order lifecycle
- Test position management

### Performance Tests
- Backtest on 6+ months of data
- Achieve minimum Sharpe ratio > 1.0
- Maximum drawdown < 15%
- Win rate > 50% for this strategy type

## 🚀 Execution Instructions

1. **Setup:**
   ```bash
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Run Tests:**
   ```bash
   pytest tests/ -v
   ```

3. **Backtest:**
   ```bash
   python backtest/backtest_runner.py --start 2024-01-01 --end 2024-10-20
   ```

4. **Paper Trading:**
   ```bash
   python main.py --mode paper
   ```

5. **Live Trading** (after validation):
   ```bash
   python main.py --mode live --confirm
   ```

## ⚠️ Critical Constraints

1. **ALWAYS use paper trading** until strategy is validated
2. **NEVER hardcode API keys** - use environment variables only
3. **Implement circuit breakers** for rapid losses
4. **Log every trade decision** with timestamp and reasoning
5. **Handle API errors gracefully** with exponential backoff
6. **Respect Alpaca rate limits** (200 req/min)
7. **Use bracket orders** for automatic risk management
8. **Validate all data** before trading decisions
9. **Monitor account balance** before each trade
10. **Implement emergency stop** for system failures

{custom_instructions if custom_instructions else ""}

## 📈 Expected Deliverables

1. ✅ Fully functional trading bot with all required modules
2. ✅ Comprehensive test suite with >80% coverage
3. ✅ Backtesting results with performance metrics
4. ✅ Detailed logging and error handling
5. ✅ Documentation for setup and usage
6. ✅ Risk management integration
7. ✅ Paper trading validation results

## 🎓 Implementation Notes

Based on the financial analysis provided:
{self._generate_implementation_notes(sec_insights, news_insights, earnings_insights)}

---

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Strategy:** {strategy_info['name']}
**Tickers:** {', '.join(tickers_list)}
**Environment:** Alpaca Paper Trading (default)
"""
        
        # Save prompt
        strategy_name = f"{strategy_type}_{'_'.join(tickers_list[:3])}"
        cursor_prompt = self._save_prompt(
            prompt_content, 
            strategy_name, 
            strategy_info['name'],
            tickers_list
        )
        
        return cursor_prompt
    
    def _build_context_section(
        self, 
        sec_insights, 
        news_insights, 
        earnings_insights,
        sector_insights, 
        price_data_summary
    ) -> str:
        """Build comprehensive context section from all insights"""
        sections = []
        
        if sec_insights:
            sections.append(f"""### SEC Filings Analysis
{sec_insights.content}

**Sources:** {', '.join(sec_insights.sources[:3])}
""")
        
        if news_insights:
            sections.append(f"""### Market News & Sentiment
{news_insights.content}

**Sources:** {', '.join(news_insights.sources[:3])}
""")
        
        if earnings_insights:
            sections.append(f"""### Earnings Analysis
{earnings_insights.content}
""")
        
        if sector_insights:
            sections.append(f"""### Sector Analysis
{sector_insights.content}
""")
        
        if price_data_summary:
            sections.append(f"""### Recent Price Action
{price_data_summary}
""")
        
        return "\n\n".join(sections) if sections else "No market context provided."
    
    def _generate_entry_logic(
        self, 
        strategy_type: str, 
        sec_insights, 
        news_insights
    ) -> str:
        """Generate strategy-specific entry logic"""
        
        base_logic = {
            "momentum": """
- Price above 20-day and 50-day moving averages
- RSI between 50-70 (bullish momentum, not overbought)
- MACD line crosses above signal line
- Volume 20% above 20-day average
- Positive news sentiment from Perplexity analysis
""",
            "mean_reversion": """
- Price touches lower Bollinger Band (oversold)
- RSI below 30 (oversold condition)
- No negative news catalysts in last 24 hours
- Volume confirms reversal interest
- Price within 5% of key support level
""",
            "breakout": """
- Price breaks above consolidation range high
- Volume exceeds 2x average on breakout bar
- ATR showing increased volatility
- No immediate resistance overhead
- Sector showing relative strength
""",
            "news_driven": """
- Positive earnings surprise or major announcement
- Sentiment score > 0.7 from news analysis
- Price gap up >2% on above-average volume
- No conflicting negative news
- Institutional buying detected
""",
            "earnings_play": """
- Earnings date within 5 trading days
- Historical earnings beat rate >60%
- Implied volatility in bottom 50th percentile
- Positive analyst revisions in last 30 days
- Sector performing well relative to market
""",
            "sector_rotation": """
- Sector outperforming S&P 500 by >5% over 30 days
- Positive fundamental trends in SEC filings
- Increasing institutional ownership
- Economic indicators favorable for sector
- Relative Strength Index (sector) > 60
"""
        }
        
        return base_logic.get(strategy_type, base_logic["momentum"])
    
    def _generate_exit_logic(self, strategy_type: str) -> str:
        """Generate strategy-specific exit logic"""
        
        base_exit = f"""
- Stop loss hit: {config.trading.stop_loss_pct * 100}% below entry
- Take profit hit: {config.trading.take_profit_pct * 100}% above entry
- Time-based exit: Close at end of trading day (for intraday)
- Signal reversal: Entry conditions no longer valid
- Risk-off event: Major negative news or market shock
- Position size exceeds risk limits
"""
        return base_exit
    
    def _generate_implementation_notes(
        self, 
        sec_insights, 
        news_insights, 
        earnings_insights
    ) -> str:
        """Generate specific implementation notes based on insights"""
        notes = []
        
        if sec_insights:
            notes.append("- Monitor SEC filings for material changes or risk factor updates")
        
        if news_insights:
            notes.append("- Integrate real-time news monitoring for rapid signal adjustment")
        
        if earnings_insights:
            notes.append("- Adjust position sizing around earnings dates (increased volatility)")
        
        notes.extend([
            "- Use Alpaca's bracket orders for automatic stop-loss/take-profit",
            "- Implement exponential backoff for API rate limiting",
            "- Log all trades with decision context for post-analysis",
            "- Start with small position sizes in paper trading for validation"
        ])
        
        return "\n".join(notes)
    
    def _save_prompt(
        self, 
        content: str, 
        strategy_name: str,
        strategy_title: str, 
        tickers: List[str]
    ) -> CursorPrompt:
        """Save prompt to file and return CursorPrompt object"""
        timestamp = datetime.now()
        filename = f"{strategy_name}_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"
        file_path = os.path.join(self.tasks_dir, filename)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        metadata = {
            "created_at": timestamp.isoformat(),
            "strategy_name": strategy_name,
            "tickers": tickers,
            "file_size": len(content)
        }
        
        # Save metadata
        metadata_path = file_path.replace('.md', '_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Cursor prompt saved to: {file_path}")
        
        return CursorPrompt(
            title=strategy_title,
            content=content,
            strategy_name=strategy_name,
            tickers=tickers,
            timestamp=timestamp,
            file_path=file_path,
            metadata=metadata
        )
    
    def generate_simple_prompt(
        self, 
        task_description: str,
        context: Optional[str] = None
    ) -> CursorPrompt:
        """Generate a simple custom prompt"""
        
        content = f"""# Custom Trading Task

## Task Description
{task_description}

## Context
{context if context else "No additional context provided."}

## Requirements
- Implement using Alpaca API with alpaca-py SDK
- Include proper error handling and logging
- Use paper trading environment for testing
- Follow best practices for async/await patterns

---
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return self._save_prompt(
            content,
            "custom_task",
            "Custom Trading Task",
            []
        )
