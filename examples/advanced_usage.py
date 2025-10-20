"""
Advanced usage examples for Perplexity-Alpaca Trading Integration
"""
import sys
import os
import asyncio
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.main import PerplexityAlpacaIntegration
from src.perplexity_client import PerplexityFinanceClient
from src.alpaca_client import AlpacaDataClient, AlpacaTradingClient, AlpacaStreamClient

def example_comprehensive_analysis():
    """Example: Comprehensive analysis with all data sources"""
    print("=== Comprehensive Analysis Example ===")
    
    integration = PerplexityAlpacaIntegration()
    
    # Get all types of analysis
    tickers = ["AAPL", "MSFT", "NVDA"]
    
    print("Fetching SEC filings analysis...")
    sec_response = integration.perplexity_client.get_sec_filings_analysis(tickers)
    sec_analysis = integration.perplexity_client.extract_content(sec_response)
    
    print("Fetching market news and sentiment...")
    news_response = integration.perplexity_client.get_market_news_sentiment(tickers, hours_back=48)
    news_analysis = integration.perplexity_client.extract_content(news_response)
    
    print("Fetching earnings analysis...")
    earnings_response = integration.perplexity_client.get_earnings_analysis(tickers)
    earnings_analysis = integration.perplexity_client.extract_content(earnings_response)
    
    print("Fetching technical analysis...")
    technical_response = integration.perplexity_client.get_technical_analysis(tickers, timeframe="1D")
    technical_analysis = integration.perplexity_client.extract_content(technical_response)
    
    print("Fetching sector analysis...")
    sector_response = integration.perplexity_client.get_sector_analysis("technology")
    sector_analysis = integration.perplexity_client.extract_content(sector_response)
    
    # Get historical data with technical indicators
    print("Fetching historical data and calculating indicators...")
    historical_data = integration.alpaca_data_client.get_historical_bars(
        tickers, 
        start_date=datetime.now() - timedelta(days=60)
    )
    
    # Calculate technical indicators for each ticker
    enhanced_data = {}
    for symbol, df in historical_data.items():
        enhanced_data[symbol] = integration.alpaca_data_client.calculate_technical_indicators(df)
    
    # Format comprehensive market data
    market_data = {
        "sec_filings": sec_analysis,
        "news_sentiment": news_analysis,
        "earnings": earnings_analysis,
        "technical": technical_analysis,
        "sector": sector_analysis,
        "price_data": integration._format_price_data(historical_data),
        "enhanced_technical": enhanced_data
    }
    
    # Generate comprehensive prompt
    prompt = integration.prompt_generator.generate_trading_strategy_prompt(
        market_data=market_data,
        strategy_type="comprehensive_ai_strategy",
        tickers=tickers,
        additional_context="""
        Advanced Requirements:
        - Implement machine learning for signal enhancement
        - Use ensemble methods for entry/exit decisions
        - Include sentiment analysis in position sizing
        - Implement dynamic risk management based on volatility
        - Add portfolio optimization using modern portfolio theory
        - Include regime detection for market conditions
        - Implement walk-forward analysis for strategy validation
        """
    )
    
    # Save comprehensive prompt
    prompt_file = integration.prompt_generator.save_prompt_to_file(
        prompt=prompt,
        strategy_name="comprehensive_ai_strategy",
        tickers=tickers
    )
    
    print(f"✅ Comprehensive analysis complete! Prompt saved to: {prompt_file}")

def example_real_time_monitoring():
    """Example: Real-time monitoring and alert system"""
    print("=== Real-time Monitoring Example ===")
    
    integration = PerplexityAlpacaIntegration()
    
    # Get current account status
    status = integration.get_account_status()
    
    print("Current Account Status:")
    print(f"  Portfolio Value: ${status['account'].get('portfolio_value', 0):,.2f}")
    print(f"  Available Cash: ${status['account'].get('cash', 0):,.2f}")
    print(f"  Buying Power: ${status['account'].get('buying_power', 0):,.2f}")
    
    # Get current positions
    positions = status['positions']
    if positions:
        print(f"\nCurrent Positions ({len(positions)}):")
        total_unrealized_pl = 0
        for position in positions:
            unrealized_pl = position.get('unrealized_pl', 0)
            total_unrealized_pl += unrealized_pl
            print(f"  {position['symbol']}: {position['qty']} shares")
            print(f"    Current Price: ${position['current_price']:.2f}")
            print(f"    Unrealized P&L: ${unrealized_pl:.2f} ({position.get('unrealized_plpc', 0)*100:.2f}%)")
        
        print(f"\nTotal Unrealized P&L: ${total_unrealized_pl:.2f}")
    else:
        print("\nNo current positions")
    
    # Get recent orders
    orders = integration.alpaca_trading_client.get_orders()
    recent_orders = [order for order in orders if order['created_at'] > (datetime.now() - timedelta(days=1)).isoformat()]
    
    if recent_orders:
        print(f"\nRecent Orders ({len(recent_orders)}):")
        for order in recent_orders[:5]:  # Show last 5 orders
            print(f"  {order['symbol']}: {order['side']} {order['qty']} @ {order['order_type']}")
            print(f"    Status: {order['status']} | Created: {order['created_at']}")
    else:
        print("\nNo recent orders")

def example_risk_management_strategy():
    """Example: Risk-focused strategy generation"""
    print("=== Risk Management Strategy Example ===")
    
    integration = PerplexityAlpacaIntegration()
    
    # Get account information for risk calculations
    account = integration.alpaca_trading_client.get_account()
    portfolio_value = account.get('portfolio_value', 100000)  # Default to 100k if not available
    
    # Calculate risk parameters
    max_position_size = portfolio_value * 0.1  # 10% max position
    daily_loss_limit = portfolio_value * 0.02  # 2% daily loss limit
    max_drawdown = portfolio_value * 0.05  # 5% max drawdown
    
    # Generate risk-focused market data
    market_data = {
        "sec_filings": "Risk-focused SEC analysis emphasizing debt levels and cash position",
        "news_sentiment": "Sentiment analysis with volatility considerations",
        "technical": "Technical analysis with risk-adjusted indicators",
        "sector": "Sector analysis with correlation considerations",
        "price_data": "Price data with volatility and risk metrics"
    }
    
    # Generate risk management prompt
    prompt = integration.prompt_generator.generate_trading_strategy_prompt(
        market_data=market_data,
        strategy_type="risk_managed_momentum",
        tickers=["AAPL", "MSFT", "GOOGL"],
        additional_context=f"""
        Risk Management Requirements:
        - Maximum position size: ${max_position_size:,.2f} (10% of portfolio)
        - Daily loss limit: ${daily_loss_limit:,.2f} (2% of portfolio)
        - Maximum drawdown: ${max_drawdown:,.2f} (5% of portfolio)
        - Use Kelly Criterion for position sizing
        - Implement correlation-based position limits
        - Add volatility-adjusted position sizing
        - Include sector concentration limits (max 30% in any sector)
        - Implement dynamic stop-loss based on ATR
        - Add time-based exit rules (max 5 days per position)
        - Include portfolio heat mapping
        - Implement real-time risk monitoring and alerts
        """
    )
    
    # Save risk management prompt
    prompt_file = integration.prompt_generator.save_prompt_to_file(
        prompt=prompt,
        strategy_name="risk_managed_momentum",
        tickers=["AAPL", "MSFT", "GOOGL"]
    )
    
    print(f"✅ Risk management strategy complete! Prompt saved to: {prompt_file}")

def example_sector_rotation_strategy():
    """Example: Sector rotation strategy based on relative strength"""
    print("=== Sector Rotation Strategy Example ===")
    
    integration = PerplexityAlpacaIntegration()
    
    # Define sectors and their representative stocks
    sectors = {
        "technology": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"],
        "healthcare": ["JNJ", "PFE", "UNH", "ABBV", "MRK"],
        "financial": ["JPM", "BAC", "WFC", "GS", "MS"],
        "consumer": ["WMT", "PG", "KO", "PEP", "MCD"],
        "industrial": ["BA", "CAT", "GE", "MMM", "HON"]
    }
    
    # Get sector analysis for each sector
    sector_analyses = {}
    for sector_name, tickers in sectors.items():
        print(f"Analyzing {sector_name} sector...")
        response = integration.perplexity_client.get_sector_analysis(sector_name)
        sector_analyses[sector_name] = integration.perplexity_client.extract_content(response)
    
    # Get technical analysis for all tickers
    all_tickers = [ticker for tickers in sectors.values() for ticker in tickers]
    technical_response = integration.perplexity_client.get_technical_analysis(all_tickers)
    technical_analysis = integration.perplexity_client.extract_content(technical_response)
    
    # Generate sector rotation prompt
    market_data = {
        "sector_analyses": sector_analyses,
        "technical": technical_analysis,
        "price_data": f"Multi-sector price analysis for {len(all_tickers)} stocks"
    }
    
    prompt = integration.prompt_generator.generate_trading_strategy_prompt(
        market_data=market_data,
        strategy_type="sector_rotation",
        tickers=all_tickers,
        additional_context="""
        Sector Rotation Strategy Requirements:
        - Implement relative strength analysis across sectors
        - Use momentum indicators to identify sector leadership
        - Rotate between top 2-3 performing sectors
        - Maintain sector diversification (max 40% in any sector)
        - Use sector ETFs for broad exposure when appropriate
        - Implement mean reversion for oversold sectors
        - Add seasonal patterns and calendar effects
        - Include economic cycle considerations
        - Implement dynamic rebalancing based on volatility
        - Add sector correlation analysis for risk management
        """
    )
    
    # Save sector rotation prompt
    prompt_file = integration.prompt_generator.save_prompt_to_file(
        prompt=prompt,
        strategy_name="sector_rotation",
        tickers=all_tickers
    )
    
    print(f"✅ Sector rotation strategy complete! Prompt saved to: {prompt_file}")

def example_earnings_play_strategy():
    """Example: Earnings-based trading strategy"""
    print("=== Earnings Play Strategy Example ===")
    
    integration = PerplexityAlpacaIntegration()
    
    # Get earnings analysis for high-volatility stocks
    earnings_stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "AMD", "INTC"]
    
    print("Fetching earnings analysis...")
    earnings_response = integration.perplexity_client.get_earnings_analysis(earnings_stocks)
    earnings_analysis = integration.perplexity_client.extract_content(earnings_response)
    
    # Get options volatility analysis
    print("Fetching volatility analysis...")
    volatility_response = integration.perplexity_client.get_technical_analysis(
        earnings_stocks, 
        timeframe="1D"
    )
    volatility_analysis = integration.perplexity_client.extract_content(volatility_response)
    
    # Generate earnings play prompt
    market_data = {
        "earnings": earnings_analysis,
        "technical": volatility_analysis,
        "price_data": "Earnings-focused price analysis with volatility metrics"
    }
    
    prompt = integration.prompt_generator.generate_trading_strategy_prompt(
        market_data=market_data,
        strategy_type="earnings_play",
        tickers=earnings_stocks,
        additional_context="""
        Earnings Play Strategy Requirements:
        - Focus on stocks with upcoming earnings announcements
        - Implement volatility-based position sizing
        - Use straddle/strangle strategies for high volatility
        - Implement earnings surprise prediction models
        - Add pre-earnings momentum analysis
        - Include post-earnings drift strategies
        - Implement earnings calendar integration
        - Add analyst estimate tracking and revisions
        - Use options strategies for leverage and risk management
        - Implement earnings-based stop losses
        - Add sector-specific earnings patterns
        - Include management guidance analysis
        """
    )
    
    # Save earnings play prompt
    prompt_file = integration.prompt_generator.save_prompt_to_file(
        prompt=prompt,
        strategy_name="earnings_play",
        tickers=earnings_stocks
    )
    
    print(f"✅ Earnings play strategy complete! Prompt saved to: {prompt_file}")

async def example_real_time_streaming():
    """Example: Real-time data streaming setup"""
    print("=== Real-time Streaming Example ===")
    
    # Initialize streaming client
    stream_client = AlpacaStreamClient()
    
    # Define callback functions
    async def on_bar_update(bar):
        print(f"Bar update for {bar.symbol}: ${bar.close:.2f} (Volume: {bar.volume:,})")
    
    async def on_quote_update(quote):
        print(f"Quote update for {quote.symbol}: Bid ${quote.bid_price:.2f} Ask ${quote.ask_price:.2f}")
    
    # Subscribe to real-time data
    tickers = ["AAPL", "MSFT"]
    
    try:
        print(f"Subscribing to real-time data for {tickers}...")
        await stream_client.subscribe_to_bars(tickers, on_bar_update)
        await stream_client.subscribe_to_quotes(tickers, on_quote_update)
        
        print("Starting real-time data stream...")
        print("Press Ctrl+C to stop...")
        
        # Start streaming (this will run indefinitely)
        await stream_client.start_streaming()
        
    except KeyboardInterrupt:
        print("\nStopping real-time stream...")
        await stream_client.stop_streaming()
        print("Stream stopped.")

if __name__ == "__main__":
    print("Perplexity-Alpaca Trading Integration - Advanced Examples")
    print("=" * 60)
    
    try:
        # Run advanced examples
        example_comprehensive_analysis()
        print()
        
        example_real_time_monitoring()
        print()
        
        example_risk_management_strategy()
        print()
        
        example_sector_rotation_strategy()
        print()
        
        example_earnings_play_strategy()
        
        print("\n🎉 All advanced examples completed successfully!")
        print("\nFor real-time streaming example, run:")
        print("python examples/advanced_usage.py --streaming")
        
    except Exception as e:
        print(f"❌ Error running advanced examples: {e}")
        print("Please check your API configuration and try again.")