"""
Local Prompt Generator
Generates prompts for local trading system without external API dependencies
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from .config import Config

class LocalPromptGenerator:
    """Generates structured prompts for local trading system development"""
    
    def __init__(self):
        self.tasks_dir = Config.CURSOR_TASKS_DIR
        os.makedirs(self.tasks_dir, exist_ok=True)
    
    def generate_trading_strategy_prompt(self, 
                                       market_data: Dict[str, Any],
                                       strategy_type: str,
                                       tickers: List[str],
                                       additional_context: str = "") -> str:
        """
        Generate a comprehensive prompt for implementing a local trading strategy
        
        Args:
            market_data: Dictionary containing all financial analysis data
            strategy_type: Type of strategy to implement
            tickers: List of stock symbols
            additional_context: Any additional context or requirements
            
        Returns:
            Formatted prompt string
        """
        
        # Extract data components
        sec_analysis = market_data.get("sec_filings", "No SEC data available")
        news_sentiment = market_data.get("news_sentiment", "No news data available")
        earnings_analysis = market_data.get("earnings", "No earnings data available")
        technical_analysis = market_data.get("technical", "No technical data available")
        sector_analysis = market_data.get("sector", "No sector data available")
        price_data = market_data.get("price_data", "No price data available")
        
        prompt = f"""# Local Trading Strategy Implementation

## 🎯 Mission
Build a sophisticated Python trading bot using local simulation that implements a **{strategy_type}** strategy for {', '.join(tickers)} based on comprehensive financial analysis.

## 📊 Market Context & Analysis

### Financial Data Analysis
{sec_analysis}

### Market News & Sentiment
{news_sentiment}

### Earnings Analysis
{earnings_analysis}

### Technical Analysis
{technical_analysis}

### Sector Analysis
{sector_analysis}

### Price Data Summary
{price_data}

## 🏗️ Required Implementation

### Core Files to Create
```
├── config.py              # Configuration and settings
├── data_handler.py        # Local data generation and storage
├── strategy.py            # Trading strategy implementation
├── risk_manager.py        # Risk management and position sizing
├── executor.py            # Order execution and management
├── portfolio_manager.py   # Portfolio tracking and rebalancing
├── logger.py              # Comprehensive logging system
├── main.py                # Main execution loop
├── requirements.txt       # Dependencies
└── README.md              # Documentation
```

### Key Requirements

1. **Local Data Generation**: Use synthetic data generation for testing and simulation
2. **Technical Indicators**: Implement RSI, MACD, Bollinger Bands, ATR, and custom indicators
3. **Risk Management**: Kelly Criterion, stop-loss, take-profit, and drawdown limits
4. **Order Management**: Market, limit, and bracket orders (simulated)
5. **Backtesting**: Historical strategy validation
6. **Monitoring**: Real-time performance tracking and alerts

## 🔧 Implementation Details

### 1. Configuration (config.py)
```python
class Config:
    # Trading parameters
    INITIAL_CASH = 100000.0
    MAX_POSITION_SIZE = 0.1  # 10% of portfolio
    RISK_PER_TRADE = 0.02    # 2% risk per trade
    STOP_LOSS_PCT = 0.05     # 5% stop loss
    TAKE_PROFIT_PCT = 0.15   # 15% take profit
    
    # Data parameters
    DATA_DAYS = 30
    ENABLE_SIMULATION = True
```

### 2. Data Handler (data_handler.py)
```python
class LocalDataHandler:
    def __init__(self):
        self.data_cache = {{}}
    
    def generate_historical_data(self, symbols, days=30):
        # Generate realistic OHLCV data
        pass
    
    def calculate_indicators(self, data):
        # Calculate technical indicators
        pass
    
    def get_market_data(self, symbols):
        # Get comprehensive market data
        pass
```

### 3. Strategy Implementation (strategy.py)
Implement the **{strategy_type}** strategy with:

**Core Strategy Logic:**
- Entry signals based on technical indicators
- Exit signals (profit targets, stop losses)
- Position sizing based on volatility and risk
- Market regime detection

**Technical Indicators:**
- Moving averages (SMA, EMA)
- Momentum indicators (RSI, MACD, Stochastic)
- Volatility indicators (Bollinger Bands, ATR)
- Volume analysis
- Custom indicators based on analysis

### 4. Risk Management (risk_manager.py)
```python
class RiskManager:
    def calculate_position_size(self, signal_strength, volatility, account_value):
        # Kelly Criterion implementation
        pass
    
    def check_risk_limits(self, position, account):
        # Risk limit checks
        pass
    
    def calculate_stop_loss(self, entry_price, volatility):
        # Dynamic stop loss calculation
        pass
```

### 5. Order Executor (executor.py)
```python
class LocalOrderExecutor:
    def __init__(self, initial_cash=100000.0):
        self.cash = initial_cash
        self.positions = {{}}
    
    def submit_order(self, symbol, qty, side, order_type='market'):
        # Simulate order execution
        pass
    
    def get_positions(self):
        # Get current positions
        pass
    
    def get_account(self):
        # Get account status
        pass
```

### 6. Portfolio Manager (portfolio_manager.py)
```python
class PortfolioManager:
    def __init__(self, initial_cash):
        self.initial_cash = initial_cash
        self.positions = {{}}
        self.trade_history = []
    
    def update_positions(self, new_trades):
        # Update portfolio with new trades
        pass
    
    def calculate_performance(self):
        # Calculate performance metrics
        pass
    
    def rebalance_portfolio(self):
        # Portfolio rebalancing logic
        pass
```

## 📈 Performance Requirements

### Target Metrics
- **Sharpe Ratio**: > 1.5
- **Maximum Drawdown**: < 10%
- **Win Rate**: > 55%
- **Profit Factor**: > 1.3
- **Average Trade Duration**: < 5 days

### Monitoring
- Real-time P&L tracking
- Risk-adjusted return calculations
- Portfolio heat mapping
- Performance attribution analysis

## 🧪 Testing Requirements

### Unit Tests
- Test all strategy components
- Test risk management functions
- Test order execution logic
- Test portfolio calculations

### Integration Tests
- End-to-end strategy testing
- Backtesting with historical data
- Performance validation
- Error handling tests

### Backtesting
- Use at least 1 year of historical data
- Include transaction costs and slippage
- Test multiple market conditions
- Validate strategy robustness

## 📝 Documentation Requirements

### Code Documentation
- Comprehensive docstrings
- Type hints for all functions
- Clear variable naming
- Inline comments for complex logic

### README.md
- Installation instructions
- Usage examples
- Configuration options
- Performance results
- Troubleshooting guide

## 🚀 Getting Started

1. **Setup Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   pip install -r requirements.txt
   ```

2. **Run the Strategy**
   ```bash
   python main.py --tickers {' '.join(tickers)} --strategy {strategy_type}
   ```

3. **Monitor Performance**
   - Check logs for trade execution
   - Monitor portfolio performance
   - Review risk metrics

## ⚠️ Important Notes

- **Local Simulation Only**: This system uses simulated data and trading
- **No Real Money**: All trades are simulated for testing purposes
- **Risk Management**: Implement proper risk controls
- **Testing**: Thoroughly test before any real implementation
- **Documentation**: Maintain comprehensive documentation

## 🎯 Success Criteria

The implementation will be considered successful if:
1. All core files are created and functional
2. Strategy logic is correctly implemented
3. Risk management is properly integrated
4. Backtesting shows positive results
5. Code is well-documented and tested
6. Performance meets target metrics

---

**Additional Context:**
{additional_context}

**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Strategy Type:** {strategy_type}
**Target Symbols:** {', '.join(tickers)}
"""

        return prompt
    
    def save_prompt_to_file(self, prompt: str, strategy_name: str, tickers: List[str]) -> str:
        """
        Save prompt to file for Cursor agent
        
        Args:
            prompt: Generated prompt
            strategy_name: Name of the strategy
            tickers: List of tickers
            
        Returns:
            Path to saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{strategy_name}_{'_'.join(tickers)}_{timestamp}.md"
        filepath = os.path.join(self.tasks_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(prompt)
        
        return filepath
    
    def generate_quick_prompt(self, ticker: str, strategy_type: str, market_data: Dict[str, Any]) -> str:
        """
        Generate a quick prompt for single ticker analysis
        
        Args:
            ticker: Stock symbol
            strategy_type: Type of strategy
            market_data: Market data dictionary
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""# Quick Trading Strategy: {strategy_type} for {ticker}

## Market Data
{market_data.get('news_sentiment', 'No news data')}

## Technical Analysis
{market_data.get('technical', 'No technical data')}

## Price Data
{market_data.get('price_data', 'No price data')}

## Implementation
Create a simple trading bot that implements a {strategy_type} strategy for {ticker}.

### Requirements:
1. Generate synthetic data for {ticker}
2. Implement {strategy_type} strategy logic
3. Add basic risk management
4. Include performance tracking
5. Create simple backtesting

### Files to create:
- `config.py` - Configuration
- `strategy.py` - Strategy implementation  
- `data_handler.py` - Data generation
- `main.py` - Execution script
- `requirements.txt` - Dependencies

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return prompt