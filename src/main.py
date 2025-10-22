"""
Main orchestrator for Local Trading System
Combines local data analysis with automated trading bot generation
No external API dependencies - fully local operation
"""
import asyncio
import argparse
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from .config import Config
from .local_data_provider import LocalDataProvider
from .local_prompt_generator import LocalPromptGenerator
from .local_trading_client import LocalTradingClient

class LocalTradingIntegration:
    """Main integration class that orchestrates the entire workflow using local data"""
    
    def __init__(self):
        self.data_provider = LocalDataProvider()
        self.prompt_generator = LocalPromptGenerator()
        self.trading_client = LocalTradingClient(paper=Config.PAPER_TRADING, initial_cash=Config.INITIAL_CASH)
        
        # Validate configuration
        if not Config.validate_config():
            raise ValueError("Invalid configuration.")
    
    def analyze_and_generate_task(self, 
                                 tickers: List[str], 
                                 strategy_name: str,
                                 additional_context: str = "") -> str:
        """
        Complete pipeline: Data → Analysis → Cursor Prompt
        
        Args:
            tickers: List of stock symbols to analyze
            strategy_name: Name of the trading strategy
            additional_context: Additional context for the strategy
            
        Returns:
            Path to the generated Cursor prompt file
        """
        print(f"🚀 Starting analysis for {', '.join(tickers)} with {strategy_name} strategy")
        
        # Step 1: Get comprehensive financial data from local provider
        print("📊 Generating SEC filings analysis...")
        sec_analysis = self.data_provider.get_sec_filings_analysis(tickers)
        
        print("📰 Generating market news and sentiment...")
        news_analysis = self.data_provider.get_market_news_sentiment(tickers)
        
        print("💰 Generating earnings analysis...")
        earnings_analysis = self.data_provider.get_earnings_analysis(tickers)
        
        print("📈 Generating technical analysis...")
        technical_analysis = self.data_provider.get_technical_analysis(tickers)
        
        # Step 2: Get sector analysis
        print("🏭 Generating sector analysis...")
        sector = self._determine_sector(tickers[0])
        sector_analysis = self.data_provider.get_sector_analysis(sector)
        
        # Step 3: Generate historical price data
        print("📊 Generating historical price data...")
        historical_data = self.data_provider.generate_historical_data(tickers, Config.DATA_DAYS)
        
        # Step 4: Calculate technical indicators
        print("🔧 Calculating technical indicators...")
        price_data_summary = self._format_price_data(historical_data)
        
        # Step 5: Combine all data into comprehensive context
        market_data = {
            "sec_filings": sec_analysis,
            "news_sentiment": news_analysis,
            "earnings": earnings_analysis,
            "technical": technical_analysis,
            "sector": sector_analysis,
            "price_data": price_data_summary,
            "historical_data": historical_data
        }
        
        # Step 6: Generate Cursor background agent prompt
        print("🤖 Generating Cursor background agent prompt...")
        cursor_prompt = self.prompt_generator.generate_trading_strategy_prompt(
            market_data=market_data,
            strategy_type=strategy_name,
            tickers=tickers,
            additional_context=additional_context
        )
        
        # Step 7: Save prompt for Cursor agent
        prompt_file = self.prompt_generator.save_prompt_to_file(
            cursor_prompt, 
            strategy_name, 
            tickers
        )
        
        print(f"\n✅ Analysis complete! Cursor prompt saved to: {prompt_file}")
        self._print_next_steps()
        
        return prompt_file
    
    def quick_analysis(self, ticker: str, strategy_type: str = "momentum") -> str:
        """
        Quick analysis for single ticker
        
        Args:
            ticker: Stock symbol
            strategy_type: Type of strategy
            
        Returns:
            Path to the generated prompt file
        """
        print(f"⚡ Quick analysis for {ticker} with {strategy_type} strategy")
        
        # Get basic market data
        news_analysis = self.data_provider.get_market_news_sentiment([ticker], hours_back=48)
        technical_analysis = self.data_provider.get_technical_analysis([ticker])
        
        # Get price data
        historical_data = self.data_provider.generate_historical_data([ticker], Config.DATA_DAYS)
        price_data = self._format_price_data(historical_data)
        
        # Generate quick prompt
        market_data = {
            "news_sentiment": news_analysis,
            "technical": technical_analysis,
            "price_data": price_data
        }
        
        cursor_prompt = self.prompt_generator.generate_trading_strategy_prompt(
            market_data=market_data,
            strategy_type=strategy_type,
            tickers=[ticker]
        )
        
        prompt_file = self.prompt_generator.save_prompt_to_file(
            cursor_prompt, 
            f"{strategy_type}_{ticker}", 
            [ticker]
        )
        
        print(f"✅ Quick analysis complete! Prompt saved to: {prompt_file}")
        return prompt_file
    
    def _determine_sector(self, ticker: str) -> str:
        """Simple sector determination based on ticker"""
        # This is a simplified approach - in production, you'd use a proper sector mapping
        tech_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'AMD', 'INTC', 'TSLA']
        if ticker.upper() in tech_tickers:
            return "technology"
        return "general"
    
    def _format_price_data(self, historical_data: Dict[str, Any]) -> str:
        """Format historical price data for prompt"""
        if not historical_data:
            return "No historical price data available"
        
        summary = []
        for symbol, df in historical_data.items():
            if df.empty:
                continue
                
            latest = df.iloc[-1]
            oldest = df.iloc[0]
            change_pct = ((latest['close'] - oldest['close']) / oldest['close']) * 100
            
            # Calculate additional metrics
            volatility = df['close'].pct_change().std() * 100
            volume_avg = df['volume'].mean()
            
            summary.append(f"""
**{symbol} Price Analysis:**
- Current Price: ${latest['close']:.2f}
- 30-day Change: {change_pct:+.2f}%
- Volatility: {volatility:.2f}%
- Average Volume: {volume_avg:,.0f}
- High: ${df['high'].max():.2f}
- Low: ${df['low'].min():.2f}
""")
        
        return "\n".join(summary)
    
    def _print_next_steps(self):
        """Print instructions for next steps"""
        print("\n" + "="*60)
        print("🎯 NEXT STEPS:")
        print("="*60)
        print("1. Open Cursor and press Ctrl+Shift+B (or ⌘B on Mac)")
        print("2. Click 'New Background Agent'")
        print("3. Copy the contents of the generated prompt file")
        print("4. Paste into the agent prompt field")
        print("5. The agent will create a new branch and implement the strategy")
        print("\n📁 Generated files are in the 'cursor_tasks/' directory")
        print("🔧 Make sure Privacy Mode is disabled in Cursor settings")
        print("💰 Ensure you have usage-based spending enabled (min $10)")
        print("="*60)
    
    def get_account_status(self) -> Dict[str, Any]:
        """Get current account status"""
        account = self.trading_client.get_account()
        positions = self.trading_client.get_positions()
        
        return {
            "account": account,
            "positions": positions,
            "timestamp": datetime.now().isoformat()
        }
    
    def test_connections(self) -> bool:
        """Test local system components"""
        print("🔍 Testing local system components...")
        
        # Test data provider
        try:
            test_data = self.data_provider.generate_historical_data(["AAPL"], 5)
            if test_data and "AAPL" in test_data:
                print("✅ Local Data Provider: Working")
            else:
                print("❌ Local Data Provider: Failed")
                return False
        except Exception as e:
            print(f"❌ Local Data Provider: Error - {e}")
            return False
        
        # Test trading client
        try:
            account = self.trading_client.get_account()
            if account:
                print("✅ Local Trading Client: Working")
            else:
                print("❌ Local Trading Client: Failed")
                return False
        except Exception as e:
            print(f"❌ Local Trading Client: Error - {e}")
            return False
        
        print("🎉 All local components working!")
        return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Local Trading System")
    parser.add_argument("--tickers", nargs="+", help="Stock symbols to analyze")
    parser.add_argument("--strategy", default="momentum", help="Trading strategy type")
    parser.add_argument("--quick", action="store_true", help="Quick analysis mode")
    parser.add_argument("--test", action="store_true", help="Test local system")
    parser.add_argument("--status", action="store_true", help="Show account status")
    parser.add_argument("--reset", action="store_true", help="Reset trading account")
    
    args = parser.parse_args()
    
    try:
        integration = LocalTradingIntegration()
        
        if args.test:
            integration.test_connections()
        elif args.status:
            status = integration.get_account_status()
            print(json.dumps(status, indent=2))
        elif args.reset:
            integration.trading_client.reset_account()
            print("✅ Account reset successfully")
        elif args.quick and args.tickers:
            for ticker in args.tickers:
                integration.quick_analysis(ticker, args.strategy)
        elif args.tickers:
            integration.analyze_and_generate_task(args.tickers, args.strategy)
        else:
            print("Please specify tickers to analyze or use --test/--status/--reset")
            print("Example: python -m src.main --tickers AAPL MSFT --strategy momentum")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())