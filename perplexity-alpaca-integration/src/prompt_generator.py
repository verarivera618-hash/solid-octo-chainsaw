"""
Prompt generation layer for Cursor background agents.
Converts financial data into structured prompts for autonomous trading bot development.
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from loguru import logger

from perplexity_client import PerplexityFinanceClient, FinancialQuery, QueryType

class StrategyType(Enum):
    """Types of trading strategies to generate."""
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    EARNINGS_PLAY = "earnings_play"
    SECTOR_ROTATION = "sector_rotation"
    PAIRS_TRADING = "pairs_trading"
    FUNDAMENTAL_LONG = "fundamental_long"
    EVENT_DRIVEN = "event_driven"

@dataclass
class PromptContext:
    """Context information for prompt generation."""
    tickers: List[str]
    strategy_type: StrategyType
    time_horizon: str  # "intraday", "swing", "position"
    risk_tolerance: str  # "low", "medium", "high"
    market_conditions: str  # "bullish", "bearish", "neutral", "volatile"
    additional_requirements: Optional[str] = None

class CursorPromptGenerator:
    """Generates comprehensive prompts for Cursor background agents."""
    
    def __init__(self, perplexity_client: Optional[PerplexityFinanceClient] = None):
        self.perplexity_client = perplexity_client or PerplexityFinanceClient()
    
    def generate_strategy_prompt(self, context: PromptContext, market_data: Dict[str, str]) -> str:
        """
        Generate a comprehensive strategy implementation prompt.
        
        Args:
            context: Trading strategy context
            market_data: Financial analysis data from Perplexity
        
        Returns:
            Formatted prompt for Cursor background agent
        """
        strategy_config = self._get_strategy_config(context.strategy_type)
        
        prompt = f"""# {strategy_config['name']} Trading Strategy Implementation

## 🎯 Mission
Build an autonomous Python trading bot on Alpaca's platform that implements a {strategy_config['name'].lower()} strategy for {', '.join(context.tickers)} with {context.risk_tolerance} risk tolerance and {context.time_horizon} time horizon.

## 📊 Market Analysis Context
{self._format_market_analysis(market_data)}

## 🏗️ Architecture Requirements

### 1. Project Structure
Create the following modular architecture:

```
trading_bot/
├── src/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py          # Configuration management
│   │   └── strategy_params.py   # Strategy-specific parameters
│   ├── data/
│   │   ├── __init__.py
│   │   ├── alpaca_client.py     # Alpaca data streaming
│   │   ├── data_processor.py    # Data cleaning and preparation
│   │   └── indicators.py        # Technical indicators
│   ├── strategy/
│   │   ├── __init__.py
│   │   ├── base_strategy.py     # Abstract strategy base class
│   │   ├── {context.strategy_type.value}_strategy.py  # Main strategy implementation
│   │   └── risk_manager.py      # Risk management rules
│   ├── execution/
│   │   ├── __init__.py
│   │   ├── order_manager.py     # Order execution and management
│   │   ├── portfolio_manager.py # Portfolio tracking and allocation
│   │   └── trade_logger.py      # Trade logging and audit trail
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── performance.py       # Performance analytics
│   │   └── backtester.py        # Strategy backtesting
│   └── utils/
│       ├── __init__.py
│       ├── logger.py            # Logging configuration
│       └── helpers.py           # Utility functions
├── tests/
│   ├── __init__.py
│   ├── test_strategy.py
│   ├── test_data.py
│   └── test_execution.py
├── config/
│   ├── .env.example
│   └── strategy_config.yaml
├── requirements.txt
├── main.py
└── README.md
```

### 2. Core Implementation Requirements

#### Data Integration (src/data/)
- **Alpaca Client**: Use `alpaca-py` SDK (NOT deprecated alpaca-trade-api)
- **Real-time Streaming**: WebSocket connection for live price feeds
- **Historical Data**: Fetch and cache historical bars for backtesting
- **Data Validation**: Implement data quality checks and error handling

```python
# Key requirements for alpaca_client.py:
from alpaca.data.live import StockDataStream
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

# Implement async WebSocket handlers
# Add connection retry logic
# Include rate limiting (200 requests/minute)
```

#### Strategy Implementation (src/strategy/)
{strategy_config['implementation_details']}

#### Risk Management (src/strategy/risk_manager.py)
- **Position Sizing**: {self._get_position_sizing_rules(context)}
- **Stop Loss**: {self._get_stop_loss_rules(context)}
- **Take Profit**: {self._get_take_profit_rules(context)}
- **Portfolio Limits**: Maximum {context.risk_tolerance} risk exposure per trade
- **Drawdown Protection**: Circuit breakers for excessive losses

#### Order Execution (src/execution/)
- **Alpaca Trading API**: Use TradingClient for order submission
- **Order Types**: Market, Limit, Stop, Bracket orders
- **Error Handling**: Retry logic for failed orders
- **Slippage Control**: Limit orders with reasonable spreads

```python
# Key requirements for order_manager.py:
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, StopOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType

# Implement bracket orders for automatic risk management
# Add order status monitoring
# Include partial fill handling
```

### 3. Strategy-Specific Logic

{self._generate_strategy_logic(context.strategy_type, context.tickers, market_data)}

### 4. Testing and Validation

#### Unit Tests (tests/)
- Test strategy signals with historical data
- Validate risk management rules
- Mock Alpaca API responses for testing
- Test edge cases and error conditions

#### Backtesting (src/analysis/backtester.py)
- Historical performance simulation
- Risk-adjusted returns calculation
- Maximum drawdown analysis
- Sharpe ratio and other metrics

#### Paper Trading Integration
- Use Alpaca's paper trading environment
- Real-time strategy validation
- Performance monitoring dashboard

### 5. Configuration and Environment

#### Environment Variables (.env)
```bash
# Alpaca Configuration
ALPACA_API_KEY=your_paper_trading_key
ALPACA_SECRET_KEY=your_paper_trading_secret
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Strategy Parameters
STRATEGY_TYPE={context.strategy_type.value}
TICKERS={','.join(context.tickers)}
RISK_TOLERANCE={context.risk_tolerance}
TIME_HORIZON={context.time_horizon}
PORTFOLIO_SIZE=100000
MAX_POSITION_SIZE=0.1

# Risk Management
STOP_LOSS_PCT=0.02
TAKE_PROFIT_PCT=0.04
MAX_DAILY_LOSS=0.05
```

#### Strategy Configuration (config/strategy_config.yaml)
```yaml
strategy:
  name: {strategy_config['name']}
  type: {context.strategy_type.value}
  tickers: {context.tickers}
  parameters: {strategy_config['parameters']}
  
risk_management:
  max_position_size: {self._get_max_position_size(context)}
  stop_loss: {self._get_stop_loss_pct(context)}
  take_profit: {self._get_take_profit_pct(context)}
  
execution:
  order_type: "bracket"
  time_in_force: "day"
  slippage_tolerance: 0.001
```

### 6. Main Execution Loop (main.py)

```python
import asyncio
from src.data.alpaca_client import AlpacaDataClient
from src.strategy.{context.strategy_type.value}_strategy import {strategy_config['class_name']}
from src.execution.order_manager import OrderManager
from src.execution.portfolio_manager import PortfolioManager

async def main():
    # Initialize components
    data_client = AlpacaDataClient()
    strategy = {strategy_config['class_name']}()
    order_manager = OrderManager()
    portfolio_manager = PortfolioManager()
    
    # Start data streaming
    await data_client.start_streaming({context.tickers})
    
    # Main trading loop
    while True:
        # Get latest market data
        market_data = await data_client.get_latest_bars()
        
        # Generate trading signals
        signals = strategy.generate_signals(market_data)
        
        # Execute trades based on signals
        for signal in signals:
            if signal.action in ['BUY', 'SELL']:
                await order_manager.execute_order(signal)
        
        # Update portfolio metrics
        portfolio_manager.update_positions()
        
        # Risk monitoring
        if portfolio_manager.check_risk_limits():
            await order_manager.close_all_positions()
        
        await asyncio.sleep(1)  # Adjust based on strategy frequency

if __name__ == "__main__":
    asyncio.run(main())
```

### 7. Performance Monitoring

#### Logging (src/utils/logger.py)
- Structured logging with loguru
- Trade execution logs
- Performance metrics logging
- Error tracking and alerts

#### Analytics Dashboard
- Real-time P&L tracking
- Win rate and average returns
- Risk metrics monitoring
- Strategy performance visualization

### 8. Deployment and Operations

#### Docker Support
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

#### Health Checks
- API connection monitoring
- Strategy performance alerts
- System resource monitoring
- Automated restart on failures

## 🔧 Implementation Checklist

### Phase 1: Foundation
- [ ] Set up project structure
- [ ] Configure Alpaca API connections
- [ ] Implement basic data streaming
- [ ] Create strategy base class
- [ ] Add logging and configuration

### Phase 2: Strategy Logic
- [ ] Implement {strategy_config['name'].lower()} algorithm
- [ ] Add technical indicators
- [ ] Create signal generation logic
- [ ] Implement risk management rules
- [ ] Add backtesting framework

### Phase 3: Execution
- [ ] Build order management system
- [ ] Implement portfolio tracking
- [ ] Add error handling and retries
- [ ] Create performance monitoring
- [ ] Set up paper trading tests

### Phase 4: Testing & Validation
- [ ] Unit test all components
- [ ] Backtest strategy performance
- [ ] Validate risk management
- [ ] Test edge cases and failures
- [ ] Performance optimization

### Phase 5: Production Readiness
- [ ] Add comprehensive logging
- [ ] Implement monitoring dashboard
- [ ] Create deployment scripts
- [ ] Add health checks
- [ ] Documentation and README

## 📈 Success Metrics

### Performance Targets
- Sharpe Ratio: > 1.5
- Maximum Drawdown: < {self._get_max_drawdown_target(context)}
- Win Rate: > {self._get_win_rate_target(context)}
- Annual Return: > {self._get_return_target(context)}

### Operational Targets
- Order Fill Rate: > 95%
- System Uptime: > 99%
- API Response Time: < 100ms
- Error Rate: < 1%

## ⚠️ Critical Requirements

1. **NEVER execute real money trades** - Always use paper trading environment
2. **Implement proper error handling** for all API calls
3. **Add rate limiting** to respect Alpaca's 200 requests/minute limit
4. **Use async/await** for WebSocket connections and concurrent operations
5. **Validate all market data** before generating signals
6. **Log all trading decisions** with timestamps and reasoning
7. **Implement circuit breakers** for excessive losses
8. **Test thoroughly** before any live deployment

## 📚 Additional Context

{self._format_additional_requirements(context)}

---

**Start with Phase 1 and implement incrementally. Focus on robust error handling, comprehensive testing, and clear logging throughout the development process.**
"""
        
        return prompt
    
    def _get_strategy_config(self, strategy_type: StrategyType) -> Dict[str, Any]:
        """Get configuration for specific strategy type."""
        configs = {
            StrategyType.MOMENTUM: {
                "name": "Momentum Following",
                "class_name": "MomentumStrategy",
                "parameters": {
                    "lookback_period": 20,
                    "momentum_threshold": 0.02,
                    "volume_confirmation": True
                },
                "implementation_details": """
**Momentum Strategy Logic**:
- Track price momentum using rate of change (ROC) indicators
- Confirm momentum with volume analysis
- Enter positions when momentum exceeds threshold
- Exit when momentum reverses or stops
- Use RSI to avoid overbought/oversold conditions
                """
            },
            StrategyType.MEAN_REVERSION: {
                "name": "Mean Reversion",
                "class_name": "MeanReversionStrategy", 
                "parameters": {
                    "lookback_period": 20,
                    "deviation_threshold": 2.0,
                    "rsi_oversold": 30,
                    "rsi_overbought": 70
                },
                "implementation_details": """
**Mean Reversion Strategy Logic**:
- Calculate Bollinger Bands with 2 standard deviations
- Identify oversold conditions (price below lower band + RSI < 30)
- Identify overbought conditions (price above upper band + RSI > 70)
- Enter contrarian positions when conditions are met
- Exit when price returns to mean (middle Bollinger Band)
                """
            },
            StrategyType.BREAKOUT: {
                "name": "Breakout Trading",
                "class_name": "BreakoutStrategy",
                "parameters": {
                    "consolidation_period": 10,
                    "breakout_threshold": 0.015,
                    "volume_multiplier": 1.5
                },
                "implementation_details": """
**Breakout Strategy Logic**:
- Identify consolidation periods (low volatility)
- Detect breakouts above resistance or below support
- Confirm breakouts with increased volume
- Enter positions in direction of breakout
- Use trailing stops to capture extended moves
                """
            },
            StrategyType.EARNINGS_PLAY: {
                "name": "Earnings Event Trading",
                "class_name": "EarningsStrategy",
                "parameters": {
                    "days_before_earnings": 5,
                    "implied_volatility_threshold": 0.3,
                    "earnings_surprise_threshold": 0.05
                },
                "implementation_details": """
**Earnings Strategy Logic**:
- Monitor upcoming earnings announcements
- Analyze historical earnings reactions
- Position before earnings based on sentiment and options flow
- Implement straddle/strangle strategies for high IV
- Quick exits post-earnings to avoid IV crush
                """
            }
        }
        
        return configs.get(strategy_type, configs[StrategyType.MOMENTUM])
    
    def _format_market_analysis(self, market_data: Dict[str, str]) -> str:
        """Format market analysis data for prompt inclusion."""
        formatted = ""
        
        for analysis_type, content in market_data.items():
            formatted += f"\n### {analysis_type.replace('_', ' ').title()}\n"
            # Truncate long content for prompt readability
            if len(content) > 1000:
                formatted += content[:1000] + "...\n"
            else:
                formatted += content + "\n"
        
        return formatted
    
    def _generate_strategy_logic(self, strategy_type: StrategyType, tickers: List[str], market_data: Dict[str, str]) -> str:
        """Generate strategy-specific implementation logic."""
        base_logic = f"""
#### Signal Generation
Implement the following signal generation logic for {', '.join(tickers)}:

1. **Data Processing**: Clean and validate incoming price data
2. **Indicator Calculation**: Compute required technical indicators
3. **Signal Logic**: Apply strategy rules to generate BUY/SELL/HOLD signals
4. **Confirmation**: Validate signals with multiple timeframes
5. **Risk Assessment**: Evaluate position size and risk before execution

#### Market Context Integration
Based on current market analysis:
{self._extract_key_insights(market_data)}

Use this context to:
- Adjust position sizing based on market volatility
- Modify entry/exit thresholds during high uncertainty
- Implement defensive measures during bearish conditions
- Increase exposure during strong bullish trends
        """
        
        return base_logic
    
    def _extract_key_insights(self, market_data: Dict[str, str]) -> str:
        """Extract key actionable insights from market data."""
        insights = []
        
        for analysis_type, content in market_data.items():
            # Extract first few sentences as key insights
            sentences = content.split('.')[:3]
            insight = '. '.join(sentences).strip()
            if insight:
                insights.append(f"- **{analysis_type.title()}**: {insight}")
        
        return '\n'.join(insights[:5])  # Limit to 5 key insights
    
    def _get_position_sizing_rules(self, context: PromptContext) -> str:
        """Get position sizing rules based on context."""
        risk_multipliers = {
            "low": "1% of portfolio per trade",
            "medium": "2% of portfolio per trade", 
            "high": "3% of portfolio per trade"
        }
        return risk_multipliers.get(context.risk_tolerance, "2% of portfolio per trade")
    
    def _get_stop_loss_rules(self, context: PromptContext) -> str:
        """Get stop loss rules based on context."""
        stop_loss_pcts = {
            "low": "1% below entry",
            "medium": "2% below entry",
            "high": "3% below entry"
        }
        return stop_loss_pcts.get(context.risk_tolerance, "2% below entry")
    
    def _get_take_profit_rules(self, context: PromptContext) -> str:
        """Get take profit rules based on context."""
        take_profit_pcts = {
            "low": "2% above entry",
            "medium": "4% above entry", 
            "high": "6% above entry"
        }
        return take_profit_pcts.get(context.risk_tolerance, "4% above entry")
    
    def _get_max_position_size(self, context: PromptContext) -> float:
        """Get maximum position size based on risk tolerance."""
        max_sizes = {"low": 0.05, "medium": 0.10, "high": 0.15}
        return max_sizes.get(context.risk_tolerance, 0.10)
    
    def _get_stop_loss_pct(self, context: PromptContext) -> float:
        """Get stop loss percentage."""
        stop_losses = {"low": 0.01, "medium": 0.02, "high": 0.03}
        return stop_losses.get(context.risk_tolerance, 0.02)
    
    def _get_take_profit_pct(self, context: PromptContext) -> float:
        """Get take profit percentage."""
        take_profits = {"low": 0.02, "medium": 0.04, "high": 0.06}
        return take_profits.get(context.risk_tolerance, 0.04)
    
    def _get_max_drawdown_target(self, context: PromptContext) -> str:
        """Get maximum drawdown target."""
        drawdowns = {"low": "5%", "medium": "10%", "high": "15%"}
        return drawdowns.get(context.risk_tolerance, "10%")
    
    def _get_win_rate_target(self, context: PromptContext) -> str:
        """Get win rate target."""
        win_rates = {"low": "60%", "medium": "55%", "high": "50%"}
        return win_rates.get(context.risk_tolerance, "55%")
    
    def _get_return_target(self, context: PromptContext) -> str:
        """Get annual return target."""
        returns = {"low": "15%", "medium": "25%", "high": "35%"}
        return returns.get(context.risk_tolerance, "25%")
    
    def _format_additional_requirements(self, context: PromptContext) -> str:
        """Format additional requirements based on context."""
        additional = f"""
### Market Conditions Adjustments
Current market assessment: **{context.market_conditions}**

Adjust strategy parameters based on market conditions:
- **Bullish**: Increase position sizes, extend profit targets
- **Bearish**: Reduce exposure, tighten stops, focus on shorts
- **Neutral**: Standard parameters, focus on range-bound strategies
- **Volatile**: Reduce position sizes, widen stops, increase monitoring

### Time Horizon Considerations
Strategy optimized for **{context.time_horizon}** trading:
- **Intraday**: Focus on 1-5 minute bars, quick exits
- **Swing**: Use daily bars, hold 2-10 days
- **Position**: Weekly/monthly analysis, hold weeks to months
        """
        
        if context.additional_requirements:
            additional += f"\n### Custom Requirements\n{context.additional_requirements}"
        
        return additional
    
    def save_prompt_for_cursor(self, prompt: str, strategy_name: str, tickers: List[str]) -> str:
        """
        Save generated prompt to file for Cursor background agent.
        
        Args:
            prompt: Generated prompt content
            strategy_name: Name of the strategy
            tickers: List of tickers involved
        
        Returns:
            Path to saved prompt file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ticker_str = '_'.join(tickers)
        filename = f"cursor_tasks/{strategy_name}_{ticker_str}_{timestamp}.md"
        
        # Ensure directory exists
        os.makedirs("cursor_tasks", exist_ok=True)
        
        # Add metadata header
        metadata = f"""---
generated_at: {datetime.now().isoformat()}
strategy: {strategy_name}
tickers: {', '.join(tickers)}
generator: Perplexity-Alpaca Integration v1.0
---

"""
        
        full_content = metadata + prompt
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            logger.info(f"Cursor prompt saved to: {filename}")
            return filename
        
        except Exception as e:
            logger.error(f"Failed to save prompt: {e}")
            raise
    
    def generate_complete_task(self, context: PromptContext) -> Dict[str, Any]:
        """
        Generate complete task with market analysis and prompt.
        
        Args:
            context: Trading strategy context
        
        Returns:
            Dictionary with analysis data and generated prompt
        """
        logger.info(f"Generating task for {context.strategy_type.value} strategy on {context.tickers}")
        
        # Gather comprehensive market data
        market_data = {}
        
        try:
            # Get fundamental analysis
            fundamental_query = FinancialQuery(
                tickers=context.tickers,
                query_type=QueryType.FUNDAMENTALS
            )
            fundamental_data = self.perplexity_client.get_comprehensive_analysis(fundamental_query)
            market_data.update(fundamental_data)
            
            # Get recent news and sentiment
            news_query = FinancialQuery(
                tickers=context.tickers,
                query_type=QueryType.MARKET_NEWS,
                time_range="7"
            )
            news_data = self.perplexity_client.get_comprehensive_analysis(news_query)
            market_data.update(news_data)
            
            # Generate strategy prompt
            prompt = self.generate_strategy_prompt(context, market_data)
            
            # Save prompt for Cursor
            strategy_name = f"{context.strategy_type.value}_{context.time_horizon}"
            prompt_file = self.save_prompt_for_cursor(prompt, strategy_name, context.tickers)
            
            return {
                "success": True,
                "context": context,
                "market_data": market_data,
                "prompt": prompt,
                "prompt_file": prompt_file,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Failed to generate complete task: {e}")
            return {
                "success": False,
                "error": str(e),
                "context": context,
                "timestamp": datetime.now().isoformat()
            }

# Example usage
if __name__ == "__main__":
    # Initialize components
    perplexity_client = PerplexityFinanceClient()
    prompt_generator = CursorPromptGenerator(perplexity_client)
    
    # Define strategy context
    context = PromptContext(
        tickers=["AAPL", "MSFT", "GOOGL"],
        strategy_type=StrategyType.MOMENTUM,
        time_horizon="swing",
        risk_tolerance="medium",
        market_conditions="bullish",
        additional_requirements="Focus on tech sector rotation patterns"
    )
    
    # Generate complete task
    result = prompt_generator.generate_complete_task(context)
    
    if result["success"]:
        print(f"✅ Task generated successfully!")
        print(f"📁 Prompt saved to: {result['prompt_file']}")
        print(f"\n🚀 Next steps:")
        print("1. Open Cursor and press Ctrl+Shift+B (or ⌘B on Mac)")
        print("2. Click 'New Background Agent'")
        print(f"3. Copy the contents of {result['prompt_file']} into the agent prompt")
        print("4. The agent will create a new branch and implement the strategy")
    else:
        print(f"❌ Task generation failed: {result['error']}")