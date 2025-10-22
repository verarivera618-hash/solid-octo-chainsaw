"""
Main orchestrator for Perplexity-Alpaca Trading Integration
Combines financial data analysis with automated trading bot generation
"""
import asyncio
import argparse
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from .config import Config
from .perplexity_client import PerplexityFinanceClient
from .prompt_generator import LocalPromptGenerator as CursorPromptGenerator
from .alpaca_client import AlpacaDataClient, AlpacaTradingClient

class PerplexityAlpacaIntegration:
    """Main integration class that orchestrates the entire workflow"""
    
    def __init__(self):
        self.perplexity_client = PerplexityFinanceClient()
        self.prompt_generator = CursorPromptGenerator()
        self.alpaca_data_client = AlpacaDataClient()
        self.alpaca_trading_client = AlpacaTradingClient(paper=Config.PAPER_TRADING)
        
        # Validate configuration
        if not Config.validate_config():
            raise ValueError("Invalid configuration. Please check your API keys.")
    
    def analyze_and_generate_task(self, 
                                 tickers: List[str], 
                                 strategy_name: str,
                                 additional_context: str = "") -> str:
        """
        Complete pipeline: Data → Analysis → Local Prompt
        
        Args:
            tickers: List of stock symbols to analyze
            strategy_name: Name of the trading strategy
            additional_context: Additional context for the strategy
            
        Returns:
            Path to the generated Cursor prompt file
        """
        print(f"🚀 Starting analysis for {', '.join(tickers)} with {strategy_name} strategy")
        
        # Step 1: Get comprehensive financial data from Perplexity
        print("📊 Fetching SEC filings analysis...")
        sec_response = self.perplexity_client.get_sec_filings_analysis(tickers)
        sec_analysis = self.perplexity_client.extract_content(sec_response)
        
        print("📰 Fetching market news and sentiment...")
        news_response = self.perplexity_client.get_market_news_sentiment(tickers)
        news_analysis = self.perplexity_client.extract_content(news_response)
        
        print("💰 Fetching earnings analysis...")
        earnings_response = self.perplexity_client.get_earnings_analysis(tickers)
        earnings_analysis = self.perplexity_client.extract_content(earnings_response)
        
        print("📈 Fetching technical analysis...")
        technical_response = self.perplexity_client.get_technical_analysis(tickers)
        technical_analysis = self.perplexity_client.extract_content(technical_response)
        
        # Step 2: Get sector analysis (assuming all tickers are in the same sector)
        print("🏭 Fetching sector analysis...")
        sector = self._determine_sector(tickers[0])  # Simple sector determination
        sector_response = self.perplexity_client.get_sector_analysis(sector)
        sector_analysis = self.perplexity_client.extract_content(sector_response)
        
        # Step 3: Get historical price data from Alpaca
        print("📊 Fetching historical price data from Alpaca...")
        historical_data = self.alpaca_data_client.get_historical_bars(
            tickers, 
            start_date=datetime.now() - timedelta(days=30)
        )
        
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
        
        # Step 6: Generate local prompt
        print("🤖 Generating local prompt...")
        cursor_prompt = self.prompt_generator.generate_trading_strategy_prompt(
            market_data=market_data,
            strategy_type=strategy_name,
            tickers=tickers,
            additional_context=additional_context
        )
        
        # Step 7: Save prompt locally
        prompt_file = self.prompt_generator.save_prompt_to_file(
            cursor_prompt, 
            strategy_name, 
            tickers
        )
        
        print(f"\n✅ Analysis complete! Prompt saved to: {prompt_file}")
        self._print_next_steps_local()
        
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
        news_response = self.perplexity_client.get_market_news_sentiment([ticker], hours_back=48)
        news_analysis = self.perplexity_client.extract_content(news_response)
        
        technical_response = self.perplexity_client.get_technical_analysis([ticker])
        technical_analysis = self.perplexity_client.extract_content(technical_response)
        
        # Get price data
        historical_data = self.alpaca_data_client.get_historical_bars([ticker])
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
    
    def _print_next_steps_local(self):
        """Print local-only next steps"""
        print("\n" + "="*60)
        print("🎯 NEXT STEPS (Local):")
        print("="*60)
        print("1. Open the generated prompt file under 'local_tasks/'")
        print("2. Copy its content and implement the described files in src/")
        print("3. Use paper trading mode; do not execute live trades")
        print("4. Run pytest and iterate locally")
        print("="*60)
    
    def get_account_status(self) -> Dict[str, Any]:
        """Get current Alpaca account status"""
        account = self.alpaca_trading_client.get_account()
        positions = self.alpaca_trading_client.get_positions()
        
        return {
            "account": account,
            "positions": positions,
            "timestamp": datetime.now().isoformat()
        }
    
    def test_connections(self) -> bool:
        """Test all API connections"""
        print("🔍 Testing API connections...")
        
        # Test Perplexity
        try:
            test_response = self.perplexity_client.get_market_news_sentiment(["AAPL"], hours_back=1)
            if "error" not in test_response:
                print("✅ Perplexity API: Connected")
            else:
                print("❌ Perplexity API: Failed")
                return False
        except Exception as e:
            print(f"❌ Perplexity API: Error - {e}")
            return False
        
        # Test Alpaca
        try:
            account = self.alpaca_trading_client.get_account()
            if account:
                print("✅ Alpaca API: Connected")
            else:
                print("❌ Alpaca API: Failed")
                return False
        except Exception as e:
            print(f"❌ Alpaca API: Error - {e}")
            return False
        
        print("🎉 All connections successful!")
        return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Perplexity-Alpaca Trading Integration")
    parser.add_argument("--tickers", nargs="+", help="Stock symbols to analyze")
    parser.add_argument("--strategy", default="momentum", help="Trading strategy type")
    parser.add_argument("--quick", action="store_true", help="Quick analysis mode")
    parser.add_argument("--test", action="store_true", help="Test API connections")
    parser.add_argument("--status", action="store_true", help="Show account status")
    
    args = parser.parse_args()
    
    try:
        integration = PerplexityAlpacaIntegration()
        
        if args.test:
            integration.test_connections()
        elif args.status:
            status = integration.get_account_status()
            print(json.dumps(status, indent=2))
        elif args.quick and args.tickers:
            for ticker in args.tickers:
                integration.quick_analysis(ticker, args.strategy)
        elif args.tickers:
            integration.analyze_and_generate_task(args.tickers, args.strategy)
        else:
            print("Please specify tickers to analyze or use --test/--status")
            print("Example: python -m src.main --tickers AAPL MSFT --strategy momentum")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())