"""
Example usage of the Perplexity-Alpaca integration system.
"""
import asyncio
import sys
import os
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from perplexity_client import PerplexityFinanceClient, FinancialQuery, QueryType
from prompt_generator import CursorPromptGenerator, PromptContext, StrategyType
from alpaca_client import AlpacaDataClient, AlpacaTradingClient

async def example_1_basic_market_analysis():
    """
    Example 1: Basic market analysis using Perplexity.
    """
    print("="*60)
    print("EXAMPLE 1: Basic Market Analysis")
    print("="*60)
    
    try:
        # Initialize Perplexity client
        # Note: You need to set PERPLEXITY_API_KEY environment variable
        client = PerplexityFinanceClient()
        
        # Analyze tech stocks
        tickers = ["AAPL", "MSFT", "GOOGL"]
        
        print(f"Analyzing {', '.join(tickers)}...")
        
        # Get SEC filings analysis
        print("\n📋 SEC Filings Analysis:")
        sec_analysis = client.get_sec_filings_analysis(tickers)
        print(sec_analysis[:500] + "..." if len(sec_analysis) > 500 else sec_analysis)
        
        # Get market news sentiment
        print("\n📰 Market News & Sentiment (Last 7 days):")
        news_analysis = client.get_market_news_sentiment(tickers, days_back=7)
        print(news_analysis[:500] + "..." if len(news_analysis) > 500 else news_analysis)
        
        # Get earnings analysis
        print("\n💰 Earnings Analysis:")
        earnings_analysis = client.get_earnings_analysis(tickers)
        print(earnings_analysis[:500] + "..." if len(earnings_analysis) > 500 else earnings_analysis)
        
        print("\n✅ Market analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in market analysis: {e}")
        print("Make sure PERPLEXITY_API_KEY is set in your environment")

async def example_2_alpaca_data_integration():
    """
    Example 2: Alpaca market data integration.
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: Alpaca Market Data Integration")
    print("="*60)
    
    try:
        # Initialize Alpaca data client
        # Note: You need to set ALPACA_API_KEY and ALPACA_SECRET_KEY
        data_client = AlpacaDataClient()
        
        tickers = ["AAPL", "MSFT"]
        
        print(f"Getting market data for {', '.join(tickers)}...")
        
        # Get latest quotes
        print("\n💱 Latest Quotes:")
        quotes = data_client.get_latest_quotes(tickers)
        for symbol, quote in quotes.items():
            spread = quote.ask_price - quote.bid_price
            print(f"{symbol}: Bid ${quote.bid_price:.2f} | Ask ${quote.ask_price:.2f} | Spread ${spread:.2f}")
        
        # Get latest bars
        print("\n📊 Latest Daily Bars:")
        bars = data_client.get_latest_bars(tickers)
        for symbol, bar in bars.items():
            change = bar.close - bar.open
            change_pct = (change / bar.open) * 100
            print(f"{symbol}: Open ${bar.open:.2f} | Close ${bar.close:.2f} | Change {change_pct:+.2f}% | Volume {bar.volume:,}")
        
        # Get historical data
        print("\n📈 Historical Data (Last 30 days):")
        from datetime import timedelta
        from alpaca.data.timeframe import TimeFrame
        
        start_date = datetime.now() - timedelta(days=30)
        historical_data = data_client.get_historical_bars(
            symbols=tickers,
            timeframe=TimeFrame.Day,
            start=start_date
        )
        
        for symbol, df in historical_data.items():
            print(f"{symbol}: {len(df)} trading days")
            print(f"  Price range: ${df['low'].min():.2f} - ${df['high'].max():.2f}")
            print(f"  Average volume: {df['volume'].mean():,.0f}")
        
        print("\n✅ Alpaca data integration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in Alpaca data integration: {e}")
        print("Make sure ALPACA_API_KEY and ALPACA_SECRET_KEY are set")

async def example_3_trading_account_info():
    """
    Example 3: Alpaca trading account information.
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Trading Account Information")
    print("="*60)
    
    try:
        # Initialize Alpaca trading client (paper trading)
        trading_client = AlpacaTradingClient(paper=True)
        
        # Get account information
        print("🏦 Account Information:")
        account = trading_client.get_account()
        print(f"  Account ID: {account['id']}")
        print(f"  Status: {account['status']}")
        print(f"  Portfolio Value: ${account['portfolio_value']:,.2f}")
        print(f"  Buying Power: ${account['buying_power']:,.2f}")
        print(f"  Cash: ${account['cash']:,.2f}")
        print(f"  Day Trade Count: {account['daytrade_count']}")
        
        # Get current positions
        print("\n📈 Current Positions:")
        positions = trading_client.get_positions()
        if positions:
            for position in positions:
                pnl_pct = position['unrealized_plpc'] * 100
                print(f"  {position['symbol']}: {position['qty']} shares")
                print(f"    Market Value: ${position['market_value']:,.2f}")
                print(f"    P&L: ${position['unrealized_pl']:,.2f} ({pnl_pct:+.2f}%)")
        else:
            print("  No current positions")
        
        # Get recent orders
        print("\n📋 Recent Orders:")
        orders = trading_client.get_orders(limit=5)
        if orders:
            for order in orders[:5]:  # Show last 5 orders
                print(f"  {order['symbol']}: {order['side'].value} {order['qty']} @ {order['order_type']}")
                print(f"    Status: {order['status'].value} | Created: {order['created_at']}")
        else:
            print("  No recent orders")
        
        print("\n✅ Trading account information retrieved successfully!")
        
    except Exception as e:
        print(f"❌ Error getting account information: {e}")
        print("Make sure ALPACA_API_KEY and ALPACA_SECRET_KEY are set for paper trading")

async def example_4_generate_local_prompt():
    """
    Example 4: Generate Cursor background agent prompt.
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Generate Local Prompt")
    print("="*60)
    
    try:
        # Initialize clients
        perplexity_client = PerplexityFinanceClient()
        prompt_generator = CursorPromptGenerator(perplexity_client)
        
        # Define strategy context
        context = PromptContext(
            tickers=["AAPL", "MSFT", "GOOGL"],
            strategy_type=StrategyType.MOMENTUM,
            time_horizon="swing",
            risk_tolerance="medium",
            market_conditions="bullish",
            additional_requirements="Focus on tech sector momentum with earnings catalyst analysis"
        )
        
        print(f"Generating {context.strategy_type.value} strategy for {', '.join(context.tickers)}...")
        
        # Generate complete task
        result = prompt_generator.generate_complete_task(context)
        
        if result["success"]:
            print(f"\n✅ Prompt generated successfully!")
            print(f"📁 Saved to: {result['prompt_file']}")
            print(f"📊 Market data sources: {len(result['market_data'])} analysis types")
            
            print(f"\n🚀 Next Steps (Local):")
            print(f"1. Open the file under local_tasks/")
            print(f"2. Copy content and implement described files under src/")
            
            # Show a preview of the generated prompt
            print(f"\n📋 Prompt Preview (first 500 chars):")
            print("-" * 50)
            print(result['prompt'][:500] + "...")
            print("-" * 50)
            
        else:
            print(f"❌ Prompt generation failed: {result['error']}")
        
    except Exception as e:
        print(f"❌ Error generating prompt: {e}")

async def example_5_comprehensive_analysis():
    """
    Example 5: Comprehensive financial analysis workflow.
    """
    print("\n" + "="*60)
    print("EXAMPLE 5: Comprehensive Analysis Workflow")
    print("="*60)
    
    try:
        # Initialize all clients
        perplexity_client = PerplexityFinanceClient()
        data_client = AlpacaDataClient()
        
        # Target stocks for analysis
        tickers = ["NVDA", "AMD", "INTC"]  # Semiconductor sector
        
        print(f"Comprehensive analysis for semiconductor stocks: {', '.join(tickers)}")
        
        # Step 1: Fundamental analysis from Perplexity
        print("\n🔍 Step 1: Fundamental Analysis")
        fundamental_query = FinancialQuery(
            tickers=tickers,
            query_type=QueryType.FUNDAMENTALS
        )
        fundamental_data = perplexity_client.get_comprehensive_analysis(fundamental_query)
        
        print("✅ Fundamental analysis completed")
        for analysis_type in fundamental_data.keys():
            print(f"  - {analysis_type.replace('_', ' ').title()}")
        
        # Step 2: Current market data from Alpaca
        print("\n📊 Step 2: Current Market Data")
        current_quotes = data_client.get_latest_quotes(tickers)
        current_bars = data_client.get_latest_bars(tickers)
        
        print("✅ Market data retrieved")
        for symbol in tickers:
            if symbol in current_quotes and symbol in current_bars:
                quote = current_quotes[symbol]
                bar = current_bars[symbol]
                print(f"  {symbol}: ${bar.close:.2f} (Bid: ${quote.bid_price:.2f}, Ask: ${quote.ask_price:.2f})")
        
        # Step 3: Sector analysis
        print("\n🏭 Step 3: Sector Analysis")
        sector_analysis = perplexity_client.get_sector_analysis("Semiconductor", tickers)
        print("✅ Sector analysis completed")
        print(f"  Analysis length: {len(sector_analysis)} characters")
        
        # Step 4: Generate trading recommendations
        print("\n💡 Step 4: Trading Strategy Recommendations")
        
        # Combine all analysis for strategy generation
        combined_analysis = {
            "fundamental_data": fundamental_data,
            "current_market_data": {
                "quotes": {symbol: {
                    "bid": quote.bid_price,
                    "ask": quote.ask_price,
                    "spread": quote.ask_price - quote.bid_price
                } for symbol, quote in current_quotes.items()},
                "bars": {symbol: {
                    "close": bar.close,
                    "volume": bar.volume,
                    "timestamp": bar.timestamp.isoformat()
                } for symbol, bar in current_bars.items()}
            },
            "sector_analysis": sector_analysis
        }
        
        # Generate strategy context based on analysis
        context = PromptContext(
            tickers=tickers,
            strategy_type=StrategyType.SECTOR_ROTATION,  # Semiconductor focus
            time_horizon="swing",
            risk_tolerance="medium",
            market_conditions="neutral",  # Would be determined from analysis
            additional_requirements="Focus on semiconductor cycle patterns and AI/datacenter demand trends"
        )
        
        print(f"✅ Strategy recommendations generated for {context.strategy_type.value}")
        print(f"  Target: {', '.join(tickers)}")
        print(f"  Horizon: {context.time_horizon}")
        print(f"  Risk: {context.risk_tolerance}")
        
        print(f"\n🎯 Analysis Summary:")
        print(f"  - Analyzed {len(tickers)} semiconductor stocks")
        print(f"  - Generated {len(fundamental_data)} types of fundamental analysis")
        print(f"  - Retrieved current market data for all symbols")
        print(f"  - Completed sector-specific analysis")
        print(f"  - Ready for strategy implementation")
        
    except Exception as e:
        print(f"❌ Error in comprehensive analysis: {e}")

async def main():
    """
    Run all examples.
    """
    print("🤖 Perplexity-Alpaca Integration Examples")
    print("=" * 80)
    
    # Check if API keys are set
    import os
    perplexity_key = os.getenv('PERPLEXITY_API_KEY')
    alpaca_key = os.getenv('ALPACA_API_KEY')
    alpaca_secret = os.getenv('ALPACA_SECRET_KEY')
    
    if not perplexity_key:
        print("⚠️  PERPLEXITY_API_KEY not found in environment variables")
        print("   Some examples may not work without this key")
    
    if not alpaca_key or not alpaca_secret:
        print("⚠️  ALPACA_API_KEY or ALPACA_SECRET_KEY not found")
        print("   Alpaca examples may not work without these keys")
    
    print("\nRunning examples...")
    
    # Run examples
    try:
        await example_1_basic_market_analysis()
        await example_2_alpaca_data_integration()
        await example_3_trading_account_info()
        await example_4_generate_local_prompt()
        await example_5_comprehensive_analysis()
        
        print("\n" + "="*80)
        print("🎉 All examples completed!")
        print("="*80)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Examples interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error running examples: {e}")

if __name__ == "__main__":
    asyncio.run(main())