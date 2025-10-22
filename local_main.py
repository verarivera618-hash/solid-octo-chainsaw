#!/usr/bin/env python3
"""
Local Trading System - Main Entry Point
No external API dependencies - fully local operation
"""
import sys
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Import local components
from src.local_config import LocalConfig
from src.local_clients import LocalPerplexityClient, LocalAlpacaDataClient, LocalAlpacaTradingClient
from src.local_data_provider import extract_content

class LocalTradingSystem:
    """Main class for local trading system operation"""
    
    def __init__(self):
        self.config = LocalConfig()
        self.perplexity_client = LocalPerplexityClient()
        self.data_client = LocalAlpacaDataClient()
        self.trading_client = LocalAlpacaTradingClient()
        
        # Validate configuration
        if not self.config.validate_config():
            raise RuntimeError("Configuration validation failed")
    
    def test_system(self) -> bool:
        """Test all system components"""
        print("🧪 Testing Local Trading System...")
        
        try:
            # Test data client
            print("📊 Testing data client...")
            test_symbols = ['AAPL', 'MSFT']
            historical_data = self.data_client.get_historical_bars(test_symbols, limit=10)
            print(f"✅ Historical data retrieved for {len(historical_data)} symbols")
            
            # Test quotes
            quotes = self.data_client.get_latest_quotes(test_symbols)
            print(f"✅ Latest quotes retrieved for {len(quotes)} symbols")
            
            # Test trading client
            print("💰 Testing trading client...")
            account = self.trading_client.get_account()
            print(f"✅ Account info: ${account['equity']:,.2f} equity")
            
            # Test perplexity client
            print("🔍 Testing analysis client...")
            analysis = self.perplexity_client.get_technical_analysis(test_symbols)
            content = extract_content(analysis)
            print(f"✅ Technical analysis generated ({len(content)} characters)")
            
            print("🎉 All tests passed! System is ready for local operation.")
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
    
    def get_account_status(self) -> Dict[str, Any]:
        """Get current account status"""
        print("📈 Account Status:")
        
        account = self.trading_client.get_account()
        positions = self.trading_client.get_positions()
        
        print(f"💰 Equity: ${account['equity']:,.2f}")
        print(f"💵 Cash: ${account['cash']:,.2f}")
        print(f"🔋 Buying Power: ${account['buying_power']:,.2f}")
        print(f"📊 Positions: {len(positions)}")
        
        if positions:
            print("\n📍 Current Positions:")
            for pos in positions:
                pnl_color = "🟢" if pos['unrealized_pl'] >= 0 else "🔴"
                print(f"  {pos['symbol']}: {pos['qty']} shares @ ${pos['current_price']:.2f} "
                      f"{pnl_color} ${pos['unrealized_pl']:+.2f}")
        
        return {
            'account': account,
            'positions': positions
        }
    
    def analyze_symbols(self, symbols: List[str], strategy: str = None) -> Dict[str, Any]:
        """Analyze symbols and generate trading insights"""
        strategy = strategy or self.config.DEFAULT_STRATEGY
        
        print(f"🔍 Analyzing {len(symbols)} symbols with {strategy} strategy...")
        
        results = {}
        
        for symbol in symbols:
            print(f"\n📊 Analyzing {symbol}...")
            
            # Get historical data
            historical_data = self.data_client.get_historical_bars([symbol], limit=100)
            df = historical_data.get(symbol)
            
            if df is not None and not df.empty:
                # Calculate technical indicators
                df_with_indicators = self.data_client.calculate_technical_indicators(df)
                latest = df_with_indicators.iloc[-1]
                
                # Get various analyses
                sec_analysis = self.perplexity_client.get_sec_filings_analysis([symbol])
                news_analysis = self.perplexity_client.get_market_news_sentiment([symbol])
                technical_analysis = self.perplexity_client.get_technical_analysis([symbol])
                earnings_analysis = self.perplexity_client.get_earnings_analysis([symbol])
                
                results[symbol] = {
                    'current_price': latest['close'],
                    'rsi': latest.get('rsi', 0),
                    'macd': latest.get('macd', 0),
                    'sma_20': latest.get('sma_20', 0),
                    'sma_50': latest.get('sma_50', 0),
                    'volume_ratio': latest.get('volume_ratio', 1),
                    'sec_analysis': extract_content(sec_analysis),
                    'news_sentiment': extract_content(news_analysis),
                    'technical_analysis': extract_content(technical_analysis),
                    'earnings_analysis': extract_content(earnings_analysis)
                }
                
                print(f"✅ {symbol}: ${latest['close']:.2f} | RSI: {latest.get('rsi', 0):.1f} | "
                      f"MACD: {latest.get('macd', 0):.3f}")
            else:
                print(f"❌ No data available for {symbol}")
                results[symbol] = {'error': 'No data available'}
        
        return results
    
    def generate_strategy_prompt(self, symbols: List[str], strategy: str, 
                               additional_context: str = None) -> str:
        """Generate a comprehensive strategy prompt for Cursor agents"""
        
        print(f"📝 Generating strategy prompt for {strategy}...")
        
        # Analyze symbols
        analysis_results = self.analyze_symbols(symbols, strategy)
        
        # Generate comprehensive prompt
        prompt = f"""
# Local Trading Strategy: {strategy.replace('_', ' ').title()}

## 🎯 Objective
Implement a fully local trading strategy for {', '.join(symbols)} using the {strategy} approach.
This system operates entirely offline with no external API dependencies.

## 📊 Market Analysis

### Symbol Analysis
"""
        
        for symbol, data in analysis_results.items():
            if 'error' not in data:
                prompt += f"""
#### {symbol}
- **Current Price**: ${data['current_price']:.2f}
- **RSI**: {data['rsi']:.1f}
- **MACD**: {data['macd']:.3f}
- **SMA 20**: ${data['sma_20']:.2f}
- **SMA 50**: ${data['sma_50']:.2f}
- **Volume Ratio**: {data['volume_ratio']:.2f}x

**Technical Analysis:**
{data['technical_analysis'][:500]}...

**Market Sentiment:**
{data['news_sentiment'][:300]}...

"""
        
        prompt += f"""
## 🔧 Implementation Requirements

### Core Components
1. **Local Data Handler** (`src/local_data_handler.py`)
   - Use LocalAlpacaDataClient for historical data
   - Implement technical indicator calculations
   - No external API calls required

2. **Strategy Engine** (`src/{strategy}_strategy.py`)
   - Implement {strategy} logic
   - Use local technical indicators
   - Risk management integration

3. **Local Trading Executor** (`src/local_executor.py`)
   - Use LocalAlpacaTradingClient for order simulation
   - Position sizing based on LocalConfig
   - Stop-loss and take-profit management

4. **Portfolio Manager** (`src/local_portfolio.py`)
   - Track positions using local simulation
   - Calculate performance metrics
   - Risk management and position sizing

### Configuration
```python
# Use LocalConfig for all settings
from src.local_config import LocalConfig

config = LocalConfig()
# No API keys required - fully local operation
```

### Data Sources
```python
# All data is generated locally
from src.local_clients import LocalAlpacaDataClient, LocalPerplexityClient

data_client = LocalAlpacaDataClient()  # No API keys needed
analysis_client = LocalPerplexityClient()  # No API keys needed
```

## 📈 Strategy Logic

### Entry Conditions
- Implement {strategy}-specific entry signals
- Use local technical indicators (RSI, MACD, Bollinger Bands)
- Volume confirmation using local data

### Exit Conditions  
- Stop-loss: {LocalConfig.RISK_TOLERANCE * 100}% (configurable)
- Take-profit: Risk-reward ratio based targets
- Time-based exits for overnight positions

### Risk Management
- Maximum position size: {LocalConfig.MAX_POSITION_SIZE * 100}% of portfolio
- Portfolio heat: Maximum 3 concurrent positions
- Drawdown limit: 10% maximum portfolio drawdown

## 🧪 Testing Framework

### Backtesting
```python
# Use local historical data for backtesting
historical_data = data_client.get_historical_bars(symbols, limit=1000)
# Run strategy against historical data
# Calculate performance metrics locally
```

### Paper Trading
```python
# Use LocalTradingSimulator for paper trading
from src.local_clients import LocalAlpacaTradingClient

trading_client = LocalAlpacaTradingClient(paper=True)
# All trades are simulated locally
```

## 📋 Implementation Checklist

- [ ] Create strategy class inheriting from BaseStrategy
- [ ] Implement entry/exit signal generation
- [ ] Add technical indicator calculations
- [ ] Create risk management rules
- [ ] Implement position sizing logic
- [ ] Add performance tracking
- [ ] Create backtesting framework
- [ ] Add logging and monitoring
- [ ] Implement paper trading mode
- [ ] Create strategy documentation

## 🚀 Deployment

### Local Execution
```bash
# Run the strategy locally
python local_main.py --symbols {' '.join(symbols)} --strategy {strategy}

# Test the strategy
python local_main.py --test

# Check account status
python local_main.py --status
```

### Copy-Paste Compatibility
This system is designed for full copy-paste compatibility:
- No external API keys required
- All dependencies are local Python packages
- Mock data generation for testing
- Local simulation for trading operations

## 📊 Expected Outcomes

### Performance Targets
- Sharpe Ratio: > 1.5
- Maximum Drawdown: < 10%
- Win Rate: > 55%
- Profit Factor: > 1.3

### Monitoring
- Real-time P&L tracking (simulated)
- Risk metrics calculation
- Performance attribution
- Strategy effectiveness analysis

## 🔒 Risk Disclaimers

This is a simulation system for educational purposes:
- All trading is simulated using local data
- No real money is at risk
- Market data is generated locally
- Performance results are indicative only

---

**Generated on**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Strategy**: {strategy}
**Symbols**: {', '.join(symbols)}
**Mode**: Local Simulation (No External Dependencies)
"""
        
        if additional_context:
            prompt += f"\n\n## 📝 Additional Context\n{additional_context}\n"
        
        return prompt
    
    def save_strategy_prompt(self, prompt: str, strategy: str) -> str:
        """Save strategy prompt to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.config.CURSOR_TASKS_DIR}/local_{strategy}_{timestamp}.md"
        
        with open(filename, 'w') as f:
            f.write(prompt)
        
        print(f"💾 Strategy prompt saved to: {filename}")
        return filename

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Local Trading System")
    parser.add_argument('--test', action='store_true', help='Test system components')
    parser.add_argument('--status', action='store_true', help='Show account status')
    parser.add_argument('--symbols', nargs='+', default=['AAPL'], help='Symbols to analyze')
    parser.add_argument('--strategy', default='local_momentum', help='Strategy to use')
    parser.add_argument('--generate-prompt', action='store_true', help='Generate Cursor strategy prompt')
    parser.add_argument('--context', help='Additional context for strategy')
    
    args = parser.parse_args()
    
    try:
        system = LocalTradingSystem()
        
        if args.test:
            success = system.test_system()
            sys.exit(0 if success else 1)
        
        elif args.status:
            system.get_account_status()
        
        elif args.generate_prompt:
            prompt = system.generate_strategy_prompt(args.symbols, args.strategy, args.context)
            filename = system.save_strategy_prompt(prompt, args.strategy)
            print(f"\n🎯 Ready for Cursor! Copy the contents of {filename} into a Cursor background agent.")
        
        else:
            # Default: analyze symbols
            results = system.analyze_symbols(args.symbols, args.strategy)
            print(f"\n✅ Analysis complete for {len(results)} symbols")
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()