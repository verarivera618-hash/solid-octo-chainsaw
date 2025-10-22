#!/usr/bin/env python3
"""
Example usage of the Alpaca Trading Bot with Perplexity Integration
"""

import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.perplexity_client import PerplexityFinanceClient, QueryType
from src.prompt_generator import CursorPromptGenerator, StrategyType
from src.data_handler import DataHandler
from src.strategy import StrategyManager
from src.executor import OrderExecutor, RiskManager
from alpaca.data.timeframe import TimeFrame


# Load environment variables
load_dotenv()


async def example_perplexity_analysis():
    """Example: Fetch and analyze financial data from Perplexity"""
    
    print("=" * 60)
    print("EXAMPLE 1: Perplexity Financial Analysis")
    print("=" * 60)
    
    # Initialize Perplexity client
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        print("❌ Please set PERPLEXITY_API_KEY in .env file")
        return
    
    client = PerplexityFinanceClient(api_key)
    
    # Analyze semiconductor stocks
    tickers = ["AMD", "NVDA", "INTC"]
    
    print(f"\n📊 Analyzing: {', '.join(tickers)}")
    
    # Get SEC filings analysis
    print("\n🔍 Fetching SEC filings...")
    sec_analysis = await client.query_async(
        tickers=tickers,
        query_type=QueryType.SEC_FILINGS,
        reasoning_effort="high"
    )
    
    print(f"✅ SEC Analysis Complete")
    print(f"   Model used: {sec_analysis.get('model')}")
    print(f"   Content preview: {sec_analysis['content'][:200]}...")
    
    # Get market sentiment
    print("\n🔍 Fetching market sentiment...")
    sentiment = await client.query_async(
        tickers=tickers,
        query_type=QueryType.SENTIMENT,
        reasoning_effort="medium"
    )
    
    print(f"✅ Sentiment Analysis Complete")
    
    # Get comprehensive analysis
    print("\n🔍 Getting comprehensive analysis...")
    full_analysis = await client.get_comprehensive_analysis(
        tickers=tickers,
        include_types=[
            QueryType.FUNDAMENTALS,
            QueryType.MARKET_NEWS,
            QueryType.SENTIMENT
        ]
    )
    
    print(f"✅ Comprehensive Analysis Complete")
    print(f"   Analysis types: {list(full_analysis['analysis'].keys())}")
    
    return full_analysis


def example_cursor_prompt_generation(financial_data=None):
    """Example: Generate Cursor background agent prompts"""
    
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Cursor Prompt Generation")
    print("=" * 60)
    
    generator = CursorPromptGenerator(output_dir="cursor_tasks")
    
    # If no financial data provided, use mock data
    if not financial_data:
        financial_data = {
            "analysis": {
                "fundamentals": {
                    "content": "AMD shows strong revenue growth with data center segment up 122% YoY..."
                },
                "sentiment": {
                    "content": "Bullish sentiment driven by AI chip demand and market share gains..."
                }
            }
        }
    
    # Generate momentum strategy prompt
    print("\n📝 Generating momentum strategy prompt...")
    
    prompt = generator.generate_prompt(
        financial_data=financial_data,
        strategy_type=StrategyType.MOMENTUM,
        tickers=["AMD", "NVDA"],
        additional_requirements="Implement advanced risk management with correlation analysis"
    )
    
    # Save the prompt
    prompt_file = generator.save_prompt(
        prompt=prompt,
        strategy_name="momentum",
        tickers=["AMD", "NVDA"]
    )
    
    print(f"✅ Prompt saved to: {prompt_file}")
    print(f"\n📋 Prompt preview (first 500 chars):")
    print(prompt[:500] + "...")
    
    print("\n🚀 To use this prompt in Cursor:")
    print("   1. Open Cursor IDE")
    print("   2. Press Ctrl+Shift+B (or ⌘B on Mac)")
    print("   3. Click 'New Background Agent'")
    print(f"   4. Copy contents from {prompt_file}")
    print("   5. Paste into agent prompt")
    
    return prompt_file


def example_alpaca_data():
    """Example: Fetch market data from Alpaca"""
    
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Alpaca Market Data")
    print("=" * 60)
    
    # Check for Alpaca credentials
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    
    if not api_key or not secret_key:
        print("❌ Please set ALPACA_API_KEY and ALPACA_SECRET_KEY in .env file")
        return
    
    # Initialize data handler
    data_handler = DataHandler(api_key, secret_key)
    
    # Fetch historical data
    print("\n📈 Fetching historical data for AAPL...")
    
    bars = data_handler.get_historical_bars(
        symbols=["AAPL"],
        timeframe=TimeFrame.Day,
        start=datetime.now() - timedelta(days=30)
    )
    
    if not bars.empty:
        print(f"✅ Retrieved {len(bars)} bars")
        print(f"\n📊 Latest bar:")
        print(f"   Date: {bars.index[-1]}")
        print(f"   Close: ${bars['close'].iloc[-1]:.2f}")
        print(f"   Volume: {bars['volume'].iloc[-1]:,.0f}")
        
        # Calculate indicators
        print("\n📐 Calculating technical indicators...")
        
        bars_with_indicators = data_handler.calculate_indicators(
            bars,
            indicators=['RSI', 'MACD', 'BB', 'ATR']
        )
        
        print(f"✅ Indicators calculated")
        print(f"   RSI: {bars_with_indicators['RSI'].iloc[-1]:.2f}")
        print(f"   ATR: ${bars_with_indicators['ATR'].iloc[-1]:.2f}")
    
    return bars_with_indicators


def example_strategy_signals():
    """Example: Generate trading signals"""
    
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Strategy Signal Generation")
    print("=" * 60)
    
    # Create sample market data
    import pandas as pd
    import numpy as np
    
    dates = pd.date_range(end=datetime.now(), periods=50, freq='H')
    market_data = pd.DataFrame({
        'open': np.random.uniform(148, 152, 50),
        'high': np.random.uniform(149, 153, 50),
        'low': np.random.uniform(147, 151, 50),
        'close': np.random.uniform(148, 152, 50),
        'volume': np.random.uniform(1000000, 5000000, 50),
        'RSI': np.random.uniform(30, 70, 50),
        'MACD': np.random.uniform(-1, 1, 50),
        'MACD_signal': np.random.uniform(-1, 1, 50),
        'BB_upper': 153,
        'BB_lower': 147,
        'BB_middle': 150,
        'ATR': 2.5
    }, index=dates)
    
    # Set conditions for signal generation
    market_data['close'].iloc[-1] = 151
    market_data['RSI'].iloc[-1] = 65
    market_data['MACD'].iloc[-1] = 0.5
    market_data['MACD_signal'].iloc[-1] = 0.3
    
    # Initialize strategy manager
    strategy_manager = StrategyManager({
        "strategies": {
            "momentum": {"enabled": True},
            "mean_reversion": {"enabled": True}
        }
    })
    
    # Generate signals
    print("\n🎯 Generating trading signals...")
    
    # Momentum signal
    momentum_signal = strategy_manager.get_signal(
        symbol="AAPL",
        market_data=market_data,
        strategy_name="momentum"
    )
    
    if momentum_signal:
        print(f"\n✅ Momentum Signal Generated:")
        print(f"   Symbol: {momentum_signal.symbol}")
        print(f"   Signal: {momentum_signal.signal.name}")
        print(f"   Confidence: {momentum_signal.confidence:.2%}")
        print(f"   Entry: ${momentum_signal.entry_price:.2f}")
        print(f"   Stop Loss: ${momentum_signal.stop_loss:.2f}")
        print(f"   Take Profit: ${momentum_signal.take_profit:.2f}")
        print(f"   Reasons: {', '.join(momentum_signal.reasons)}")
    else:
        print("   No momentum signal generated")
    
    # Combined signal
    combined_signal = strategy_manager.get_combined_signal(
        symbol="AAPL",
        market_data=market_data,
        sentiment_data={"sentiment_score": 0.7, "news_sentiment": "Bullish"}
    )
    
    if combined_signal:
        print(f"\n✅ Combined Signal Generated:")
        print(f"   Strategies used: {combined_signal.metadata.get('strategies')}")
        print(f"   Signal: {combined_signal.signal.name}")
        print(f"   Confidence: {combined_signal.confidence:.2%}")


def example_risk_management():
    """Example: Risk management validation"""
    
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Risk Management")
    print("=" * 60)
    
    risk_manager = RiskManager({
        "max_position_size": 0.1,
        "max_daily_loss": 0.02,
        "max_drawdown": 0.1,
        "max_positions": 5,
        "min_cash_reserve": 0.2
    })
    
    # Calculate position size
    print("\n💰 Calculating position size...")
    
    position_size = risk_manager.calculate_position_size(
        capital=100000,
        entry_price=150,
        stop_loss=147,
        risk_per_trade=0.02
    )
    
    print(f"   Capital: $100,000")
    print(f"   Entry Price: $150")
    print(f"   Stop Loss: $147")
    print(f"   Risk per Trade: 2%")
    print(f"✅ Calculated Position Size: {position_size} shares")
    print(f"   Position Value: ${position_size * 150:,.2f}")
    print(f"   Max Risk: ${position_size * (150 - 147):,.2f}")
    
    # Validate trade
    print("\n🛡️ Validating trade against risk rules...")
    
    from src.strategy import TradingSignal, Signal
    
    test_signal = TradingSignal(
        symbol="AAPL",
        signal=Signal.BUY,
        confidence=0.75,
        entry_price=150,
        stop_loss=147,
        take_profit=156,
        position_size=position_size,
        reasons=["Test signal"],
        timestamp=datetime.now(),
        metadata={}
    )
    
    # Mock portfolio state
    is_valid, violations = risk_manager.validate_trade(
        signal=test_signal,
        portfolio_value=100000,
        cash_available=50000,
        current_positions=[]  # No existing positions
    )
    
    if is_valid:
        print("✅ Trade passes all risk checks")
    else:
        print(f"❌ Trade rejected. Violations:")
        for violation in violations:
            print(f"   - {violation}")
    
    # Get risk report
    print("\n📊 Risk Report:")
    report = risk_manager.get_risk_report()
    for key, value in report.items():
        if key != "risk_violations":
            print(f"   {key}: {value}")


async def main():
    """Run all examples"""
    
    print("\n" + "🚀 ALPACA TRADING BOT - USAGE EXAMPLES 🚀".center(60))
    print("=" * 60)
    
    # Example 1: Perplexity Analysis
    financial_data = await example_perplexity_analysis()
    
    # Example 2: Cursor Prompt Generation
    example_cursor_prompt_generation(financial_data)
    
    # Example 3: Alpaca Market Data
    example_alpaca_data()
    
    # Example 4: Strategy Signals
    example_strategy_signals()
    
    # Example 5: Risk Management
    example_risk_management()
    
    print("\n" + "=" * 60)
    print("✅ All examples completed successfully!")
    print("\n📚 For more information, see README.md")
    print("💡 To start trading: python main.py --mode trade")
    print("🤖 To generate Cursor prompts: python main.py --mode generate")


if __name__ == "__main__":
    # Run async main
    asyncio.run(main())