"""
Basic usage examples for Perplexity-Alpaca Trading Integration
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.main import PerplexityAlpacaIntegration

def example_basic_analysis():
    """Example: Basic analysis for a single stock"""
    print("=== Basic Analysis Example ===")
    
    # Initialize integration
    integration = PerplexityAlpacaIntegration()
    
    # Test connections first
    if not integration.test_connections():
        print("❌ API connections failed. Please check your configuration.")
        return
    
    # Generate analysis for Apple stock
    prompt_file = integration.analyze_and_generate_task(
        tickers=["AAPL"],
        strategy_name="momentum_strategy"
    )
    
    print(f"✅ Analysis complete! Prompt saved to: {prompt_file}")

def example_multi_stock_analysis():
    """Example: Analysis for multiple stocks in the same sector"""
    print("=== Multi-Stock Analysis Example ===")
    
    integration = PerplexityAlpacaIntegration()
    
    # Analyze semiconductor stocks
    prompt_file = integration.analyze_and_generate_task(
        tickers=["AMD", "NVDA", "INTC"],
        strategy_name="semiconductor_momentum",
        additional_context="Focus on AI and data center trends"
    )
    
    print(f"✅ Multi-stock analysis complete! Prompt saved to: {prompt_file}")

def example_quick_analysis():
    """Example: Quick analysis for rapid strategy generation"""
    print("=== Quick Analysis Example ===")
    
    integration = PerplexityAlpacaIntegration()
    
    # Quick analysis for Tesla
    prompt_file = integration.quick_analysis(
        ticker="TSLA",
        strategy_type="breakout"
    )
    
    print(f"✅ Quick analysis complete! Prompt saved to: {prompt_file}")

def example_account_status():
    """Example: Check account status and positions"""
    print("=== Account Status Example ===")
    
    integration = PerplexityAlpacaIntegration()
    
    # Get account status
    status = integration.get_account_status()
    
    print("Account Information:")
    print(f"  Equity: ${status['account'].get('equity', 0):,.2f}")
    print(f"  Cash: ${status['account'].get('cash', 0):,.2f}")
    print(f"  Buying Power: ${status['account'].get('buying_power', 0):,.2f}")
    
    print(f"\nPositions ({len(status['positions'])}):")
    for position in status['positions']:
        print(f"  {position['symbol']}: {position['qty']} shares @ ${position['current_price']:.2f}")

def example_custom_strategy():
    """Example: Custom strategy with specific requirements"""
    print("=== Custom Strategy Example ===")
    
    integration = PerplexityAlpacaIntegration()
    
    # Create custom market data
    custom_market_data = {
        "sec_filings": "Custom SEC analysis focusing on revenue growth and debt levels",
        "news_sentiment": "Bullish sentiment due to recent product launches",
        "earnings": "Strong Q4 earnings beat with positive guidance",
        "technical": "Breaking above key resistance levels with high volume",
        "sector": "Technology sector showing strong momentum",
        "price_data": "Custom price analysis with specific entry/exit levels"
    }
    
    # Generate custom prompt
    prompt = integration.prompt_generator.generate_trading_strategy_prompt(
        market_data=custom_market_data,
        strategy_type="custom_breakout",
        tickers=["AAPL", "MSFT"],
        additional_context="""
        Special Requirements:
        - Focus on earnings momentum
        - Use 20-day moving average for trend confirmation
        - Implement 2% stop loss and 6% take profit
        - Only trade during market hours (9:30 AM - 4:00 PM ET)
        - Maximum 2 positions at any time
        """
    )
    
    # Save custom prompt
    prompt_file = integration.prompt_generator.save_prompt_to_file(
        prompt=prompt,
        strategy_name="custom_breakout",
        tickers=["AAPL", "MSFT"]
    )
    
    print(f"✅ Custom strategy complete! Prompt saved to: {prompt_file}")

def example_sector_analysis():
    """Example: Sector-wide analysis and strategy generation"""
    print("=== Sector Analysis Example ===")
    
    integration = PerplexityAlpacaIntegration()
    
    # Get sector analysis
    sector_response = integration.perplexity_client.get_sector_analysis("technology")
    sector_analysis = integration.perplexity_client.extract_content(sector_response)
    
    print("Sector Analysis:")
    print(sector_analysis[:500] + "..." if len(sector_analysis) > 500 else sector_analysis)
    
    # Generate strategy based on sector analysis
    market_data = {
        "sector": sector_analysis,
        "price_data": "Sector-wide price analysis",
        "news_sentiment": "Technology sector sentiment analysis"
    }
    
    prompt = integration.prompt_generator.generate_trading_strategy_prompt(
        market_data=market_data,
        strategy_type="sector_rotation",
        tickers=["AAPL", "MSFT", "GOOGL", "AMZN"],
        additional_context="Focus on sector rotation and relative strength"
    )
    
    prompt_file = integration.prompt_generator.save_prompt_to_file(
        prompt=prompt,
        strategy_name="sector_rotation",
        tickers=["AAPL", "MSFT", "GOOGL", "AMZN"]
    )
    
    print(f"✅ Sector analysis complete! Prompt saved to: {prompt_file}")

if __name__ == "__main__":
    print("Perplexity-Alpaca Trading Integration Examples")
    print("=" * 50)
    
    try:
        # Run examples
        example_basic_analysis()
        print()
        
        example_multi_stock_analysis()
        print()
        
        example_quick_analysis()
        print()
        
        example_account_status()
        print()
        
        example_custom_strategy()
        print()
        
        example_sector_analysis()
        
        print("\n🎉 All examples completed successfully!")
        print("\nNext steps (Local):")
        print("1. Open the generated prompt under local_tasks/")
        print("2. Copy its content and implement in src/")
        print("3. Run pytest and iterate locally")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        print("Please check your API configuration and try again.")