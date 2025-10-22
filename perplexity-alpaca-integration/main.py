"""
Main integration orchestrator for Perplexity-Alpaca trading system.
"""
import asyncio
import argparse
import sys
from datetime import datetime
from typing import List, Dict, Optional
from loguru import logger

from src.config import get_settings
from src.perplexity_client import PerplexityFinanceClient, FinancialQuery, QueryType
from src.prompt_generator import CursorPromptGenerator, PromptContext, StrategyType
from src.alpaca_client import AlpacaDataClient, AlpacaTradingClient

settings = get_settings()

class PerplexityAlpacaIntegration:
    """Main integration class for Perplexity-Alpaca trading system."""
    
    def __init__(self):
        # Initialize clients
        self.perplexity_client = PerplexityFinanceClient()
        self.prompt_generator = CursorPromptGenerator(self.perplexity_client)
        self.data_client = AlpacaDataClient()
        self.trading_client = AlpacaTradingClient(paper=True)
        
        logger.info("Perplexity-Alpaca integration initialized")
    
    def analyze_and_generate_task(
        self,
        tickers: List[str],
        strategy_type: StrategyType,
        time_horizon: str = "swing",
        risk_tolerance: str = "medium",
        market_conditions: str = "neutral",
        additional_requirements: Optional[str] = None
    ) -> Dict:
        """
        Complete pipeline: Data → Analysis → Cursor Prompt Generation.
        
        Args:
            tickers: List of stock symbols
            strategy_type: Type of strategy to implement
            time_horizon: Trading time horizon
            risk_tolerance: Risk tolerance level
            market_conditions: Current market conditions assessment
            additional_requirements: Additional custom requirements
        
        Returns:
            Dictionary with analysis results and generated prompt
        """
        logger.info(f"Starting analysis and task generation for {tickers}")
        
        try:
            # Create prompt context
            context = PromptContext(
                tickers=tickers,
                strategy_type=strategy_type,
                time_horizon=time_horizon,
                risk_tolerance=risk_tolerance,
                market_conditions=market_conditions,
                additional_requirements=additional_requirements
            )
            
            # Generate comprehensive task
            result = self.prompt_generator.generate_complete_task(context)
            
            if result["success"]:
                logger.success(f"Task generated successfully: {result['prompt_file']}")
                self._print_next_steps(result['prompt_file'])
            else:
                logger.error(f"Task generation failed: {result['error']}")
            
            return result
        
        except Exception as e:
            logger.error(f"Error in analyze_and_generate_task: {e}")
            return {"success": False, "error": str(e)}
    
    def _print_next_steps(self, prompt_file: str):
        """Print next steps for the user."""
        print("\n" + "="*60)
        print("🚀 CURSOR BACKGROUND AGENT SETUP")
        print("="*60)
        print(f"✅ Cursor prompt saved to: {prompt_file}")
        print("\n📋 Next Steps:")
        print("1. Open Cursor IDE")
        print("2. Press Ctrl+Shift+B (or ⌘B on Mac) to open Background Agents")
        print("3. Click 'New Background Agent'")
        print(f"4. Copy the contents of '{prompt_file}' into the agent prompt")
        print("5. The agent will create a new branch and implement the strategy")
        print("\n⚠️  Important Notes:")
        print("- Ensure Privacy Mode is disabled in Cursor settings")
        print("- Make sure you have usage-based spending enabled (min $10)")
        print("- The agent will use paper trading by default")
        print("- Monitor the agent's progress in the Background Agents panel")
        print("="*60)
    
    async def test_connections(self) -> Dict[str, bool]:
        """
        Test connections to all services.
        
        Returns:
            Dictionary with connection test results
        """
        results = {}
        
        # Test Perplexity connection
        try:
            test_query = FinancialQuery(
                tickers=["AAPL"],
                query_type=QueryType.MARKET_NEWS,
                time_range="1"
            )
            self.perplexity_client.get_comprehensive_analysis(test_query)
            results["perplexity"] = True
            logger.success("Perplexity API connection successful")
        except Exception as e:
            results["perplexity"] = False
            logger.error(f"Perplexity API connection failed: {e}")
        
        # Test Alpaca data connection
        try:
            self.data_client.get_latest_quotes(["AAPL"])
            results["alpaca_data"] = True
            logger.success("Alpaca Data API connection successful")
        except Exception as e:
            results["alpaca_data"] = False
            logger.error(f"Alpaca Data API connection failed: {e}")
        
        # Test Alpaca trading connection
        try:
            self.trading_client.get_account()
            results["alpaca_trading"] = True
            logger.success("Alpaca Trading API connection successful")
        except Exception as e:
            results["alpaca_trading"] = False
            logger.error(f"Alpaca Trading API connection failed: {e}")
        
        return results
    
    def get_market_overview(self, tickers: List[str]) -> Dict:
        """
        Get comprehensive market overview for tickers.
        
        Args:
            tickers: List of stock symbols
        
        Returns:
            Dictionary with market overview data
        """
        logger.info(f"Getting market overview for {tickers}")
        
        try:
            # Get fundamental analysis
            fundamental_query = FinancialQuery(
                tickers=tickers,
                query_type=QueryType.FUNDAMENTALS
            )
            fundamental_data = self.perplexity_client.get_comprehensive_analysis(fundamental_query)
            
            # Get current market data from Alpaca
            latest_quotes = self.data_client.get_latest_quotes(tickers)
            latest_bars = self.data_client.get_latest_bars(tickers)
            
            return {
                "success": True,
                "tickers": tickers,
                "fundamental_analysis": fundamental_data,
                "current_quotes": {symbol: {
                    "bid": quote.bid_price,
                    "ask": quote.ask_price,
                    "spread": quote.ask_price - quote.bid_price,
                    "timestamp": quote.timestamp.isoformat()
                } for symbol, quote in latest_quotes.items()},
                "current_bars": {symbol: {
                    "close": bar.close,
                    "volume": bar.volume,
                    "timestamp": bar.timestamp.isoformat()
                } for symbol, bar in latest_bars.items()},
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error getting market overview: {e}")
            return {"success": False, "error": str(e)}
    
    def list_available_strategies(self) -> List[Dict]:
        """
        List available trading strategies.
        
        Returns:
            List of strategy information dictionaries
        """
        strategies = [
            {
                "type": "momentum",
                "name": "Momentum Following",
                "description": "Follows price momentum using technical indicators",
                "time_horizons": ["intraday", "swing", "position"],
                "risk_levels": ["low", "medium", "high"]
            },
            {
                "type": "mean_reversion",
                "name": "Mean Reversion",
                "description": "Trades against extreme price movements",
                "time_horizons": ["intraday", "swing"],
                "risk_levels": ["low", "medium", "high"]
            },
            {
                "type": "breakout",
                "name": "Breakout Trading",
                "description": "Trades breakouts from consolidation patterns",
                "time_horizons": ["intraday", "swing"],
                "risk_levels": ["medium", "high"]
            },
            {
                "type": "earnings_play",
                "name": "Earnings Event Trading",
                "description": "Trades around earnings announcements",
                "time_horizons": ["intraday", "swing"],
                "risk_levels": ["high"]
            },
            {
                "type": "sector_rotation",
                "name": "Sector Rotation",
                "description": "Rotates between sectors based on market cycles",
                "time_horizons": ["swing", "position"],
                "risk_levels": ["low", "medium"]
            },
            {
                "type": "pairs_trading",
                "name": "Pairs Trading",
                "description": "Long/short pairs within same sector",
                "time_horizons": ["swing", "position"],
                "risk_levels": ["medium", "high"]
            }
        ]
        
        return strategies

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Perplexity-Alpaca Trading Integration")
    parser.add_argument("--test", action="store_true", help="Test API connections")
    parser.add_argument("--overview", nargs="+", help="Get market overview for tickers")
    parser.add_argument("--generate", action="store_true", help="Generate trading strategy")
    parser.add_argument("--tickers", nargs="+", required=False, help="Stock tickers to analyze")
    parser.add_argument("--strategy", choices=["momentum", "mean_reversion", "breakout", "earnings_play", "sector_rotation", "pairs_trading"], 
                       default="momentum", help="Strategy type")
    parser.add_argument("--time-horizon", choices=["intraday", "swing", "position"], 
                       default="swing", help="Trading time horizon")
    parser.add_argument("--risk", choices=["low", "medium", "high"], 
                       default="medium", help="Risk tolerance")
    parser.add_argument("--market", choices=["bullish", "bearish", "neutral", "volatile"], 
                       default="neutral", help="Market conditions")
    parser.add_argument("--requirements", type=str, help="Additional requirements")
    
    args = parser.parse_args()
    
    # Configure logging
    logger.remove()
    logger.add(sys.stdout, level=settings.log_level)
    logger.add(settings.log_file, rotation="1 day", retention="30 days", level="DEBUG")
    
    # Initialize integration
    integration = PerplexityAlpacaIntegration()
    
    if args.test:
        # Test connections
        print("Testing API connections...")
        results = asyncio.run(integration.test_connections())
        
        print("\n" + "="*40)
        print("CONNECTION TEST RESULTS")
        print("="*40)
        for service, status in results.items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {service.replace('_', ' ').title()}: {'Connected' if status else 'Failed'}")
        print("="*40)
        
        if all(results.values()):
            print("\n🎉 All connections successful! Ready to generate trading strategies.")
        else:
            print("\n⚠️  Some connections failed. Please check your API keys and configuration.")
            sys.exit(1)
    
    elif args.overview:
        # Get market overview
        overview = integration.get_market_overview(args.overview)
        
        if overview["success"]:
            print(f"\n📊 Market Overview for {', '.join(args.overview)}")
            print("="*60)
            
            # Print current prices
            for symbol in args.overview:
                if symbol in overview["current_quotes"]:
                    quote = overview["current_quotes"][symbol]
                    print(f"{symbol}: Bid ${quote['bid']:.2f} | Ask ${quote['ask']:.2f} | Spread ${quote['spread']:.2f}")
            
            print("\n📈 Fundamental Analysis Summary:")
            for analysis_type, content in overview["fundamental_analysis"].items():
                print(f"\n{analysis_type.replace('_', ' ').title()}:")
                # Print first 200 characters of analysis
                print(content[:200] + "..." if len(content) > 200 else content)
        else:
            print(f"❌ Failed to get market overview: {overview['error']}")
            sys.exit(1)
    
    elif args.generate:
        # Generate trading strategy
        if not args.tickers:
            print("❌ Please specify tickers with --tickers")
            sys.exit(1)
        
        print(f"🔄 Generating {args.strategy} strategy for {', '.join(args.tickers)}...")
        
        result = integration.analyze_and_generate_task(
            tickers=args.tickers,
            strategy_type=StrategyType(args.strategy),
            time_horizon=args.time_horizon,
            risk_tolerance=args.risk,
            market_conditions=args.market,
            additional_requirements=args.requirements
        )
        
        if not result["success"]:
            print(f"❌ Strategy generation failed: {result['error']}")
            sys.exit(1)
    
    else:
        # Interactive mode
        print("🤖 Perplexity-Alpaca Trading Integration")
        print("="*50)
        
        # List available strategies
        strategies = integration.list_available_strategies()
        print("\n📋 Available Strategies:")
        for i, strategy in enumerate(strategies, 1):
            print(f"{i}. {strategy['name']} ({strategy['type']})")
            print(f"   {strategy['description']}")
        
        print(f"\n💡 Examples:")
        print(f"  Test connections: python main.py --test")
        print(f"  Market overview: python main.py --overview AAPL MSFT GOOGL")
        print(f"  Generate strategy: python main.py --generate --tickers AAPL MSFT --strategy momentum --risk medium")
        print(f"\n📚 For full options: python main.py --help")

if __name__ == "__main__":
    main()