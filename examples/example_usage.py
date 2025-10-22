"""
Example usage of the Perplexity-Alpaca Trading Integration
Demonstrates common workflows and patterns
"""

import asyncio
from datetime import datetime, timedelta
from alpaca.data.timeframe import TimeFrame

from src.perplexity_client import PerplexityFinanceClient
from src.prompt_generator import LocalPromptGenerator as PromptGenerator
from src.data_handler import AlpacaDataHandler
from src.executor import OrderExecutor
from src.strategy import get_strategy


def example_1_generate_local_prompt():
    """
    Example 1: Generate a local prompt
    Analyze stocks and create a local prompt for implementation
    """
    print("=" * 80)
    print("EXAMPLE 1: Generate Local Prompt")
    print("=" * 80)
    
    # Initialize clients
    perplexity = PerplexityFinanceClient()
    prompt_gen = PromptGenerator()
    data_handler = AlpacaDataHandler()
    
    # Define tickers to analyze
    tickers = ['AMD', 'NVDA']
    
    # Fetch market insights
    print("\n1. Fetching market news...")
    news_insights = perplexity.get_market_news(tickers)
    print(f"   ✅ Retrieved {len(news_insights.sources)} sources")
    
    # Fetch price data
    print("\n2. Fetching historical price data...")
    bars = data_handler.get_historical_bars(
        symbols=tickers,
        timeframe=TimeFrame.Day,
        start=datetime.now() - timedelta(days=30)
    )
    price_summary = data_handler.format_price_data_summary(tickers)
    print(f"   ✅ Retrieved data for {len(bars)} symbols")
    
    # Generate prompt
    print("\n3. Generating local prompt...")
    cursor_prompt = prompt_gen.generate_trading_strategy_prompt(
        news_insights=news_insights,
        price_data_summary=price_summary,
        strategy_type='momentum',
        tickers=tickers
    )
    
    print(f"\n✅ Prompt generated: {cursor_prompt.file_path}")
    print("\nNext: Open the file under local_tasks/, copy content, implement in src/.")


def example_2_analyze_with_strategy():
    """
    Example 2: Analyze market data with a trading strategy
    Shows how to use the strategy framework
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Analyze Market Data with Trading Strategy")
    print("=" * 80)
    
    # Initialize data handler and strategy
    data_handler = AlpacaDataHandler()
    strategy = get_strategy('momentum')
    
    ticker = 'AAPL'
    
    # Fetch historical data
    print(f"\n1. Fetching data for {ticker}...")
    bars = data_handler.get_historical_bars(
        symbols=[ticker],
        timeframe=TimeFrame.Day,
        limit=100
    )
    
    # Calculate technical indicators
    print("\n2. Calculating technical indicators...")
    df = data_handler.calculate_indicators(
        ticker,
        indicators=['SMA_20', 'SMA_50', 'RSI', 'MACD', 'BBANDS', 'Volume_SMA']
    )
    print(f"   ✅ Calculated indicators for {len(df)} bars")
    
    # Analyze with strategy
    print("\n3. Analyzing with momentum strategy...")
    signal = strategy.analyze(ticker, df)
    
    print(f"\n📊 Signal Results:")
    print(f"   Action: {signal.action}")
    print(f"   Strength: {signal.strength:.2%}")
    print(f"   Reason: {signal.reason}")
    if signal.entry_price:
        print(f"   Entry: ${signal.entry_price:.2f}")
        print(f"   Stop Loss: ${signal.stop_loss:.2f}")
        print(f"   Take Profit: ${signal.take_profit:.2f}")


def example_3_paper_trading_simulation():
    """
    Example 3: Simulate paper trading
    Shows the complete trading workflow
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Paper Trading Simulation")
    print("=" * 80)
    
    # Initialize components
    data_handler = AlpacaDataHandler()
    executor = OrderExecutor(paper=True)
    strategy = get_strategy('momentum')
    
    ticker = 'SPY'
    
    # Get account info
    print("\n1. Checking account...")
    account = executor.get_account()
    print(f"   Account Equity: ${account['equity']:,.2f}")
    print(f"   Buying Power: ${account['buying_power']:,.2f}")
    
    # Fetch and analyze data
    print(f"\n2. Analyzing {ticker}...")
    bars = data_handler.get_historical_bars(
        symbols=[ticker],
        timeframe=TimeFrame.Day,
        limit=100
    )
    
    df = data_handler.calculate_indicators(
        ticker,
        indicators=['SMA_20', 'SMA_50', 'RSI', 'MACD', 'Volume_SMA']
    )
    
    signal = strategy.analyze(ticker, df)
    
    print(f"\n📊 Signal: {signal.action} ({signal.strength:.2%})")
    print(f"   Reason: {signal.reason}")
    
    # Simulate order submission (dry run)
    if signal.action == 'BUY' and signal.strength >= 0.6:
        print("\n3. Simulating order submission...")
        
        qty = strategy.calculate_position_size(
            account_value=account['equity'],
            entry_price=signal.entry_price,
            stop_loss_price=signal.stop_loss,
            signal_strength=signal.strength
        )
        
        print(f"   Position Size: {qty} shares")
        print(f"   Entry Price: ${signal.entry_price:.2f}")
        print(f"   Stop Loss: ${signal.stop_loss:.2f} ({-2:.1f}%)")
        print(f"   Take Profit: ${signal.take_profit:.2f} ({+5:.1f}%)")
        print(f"   Total Value: ${qty * signal.entry_price:,.2f}")
        print("\n   [DRY RUN - No actual order submitted]")
    else:
        print("\n3. No trade signal - holding")


async def example_4_realtime_monitoring():
    """
    Example 4: Real-time data monitoring
    Shows how to stream live market data
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Real-time Data Monitoring (5 seconds)")
    print("=" * 80)
    
    data_handler = AlpacaDataHandler()
    tickers = ['AAPL']
    
    # Define callback for incoming bars
    bar_count = 0
    
    async def on_bar(bar):
        nonlocal bar_count
        bar_count += 1
        print(f"📊 {bar.symbol}: ${bar.close:.2f} @ {bar.timestamp}")
    
    # Subscribe to bars
    print(f"\n1. Subscribing to {tickers}...")
    await data_handler.stream_bars(tickers, callback=on_bar)
    
    # Run stream for 5 seconds
    print("2. Streaming data (5 seconds)...")
    stream_task = asyncio.create_task(data_handler.start_streaming())
    
    await asyncio.sleep(5)
    
    # Stop streaming
    print("\n3. Stopping stream...")
    await data_handler.stop_streaming()
    
    try:
        await stream_task
    except:
        pass
    
    print(f"\n✅ Received {bar_count} bars")


def example_5_multi_ticker_analysis():
    """
    Example 5: Analyze multiple tickers
    Compare signals across different stocks
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Multi-Ticker Analysis")
    print("=" * 80)
    
    data_handler = AlpacaDataHandler()
    strategy = get_strategy('momentum')
    
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
    
    print(f"\nAnalyzing {len(tickers)} stocks...\n")
    
    # Fetch data for all tickers
    bars_dict = data_handler.get_historical_bars(
        symbols=tickers,
        timeframe=TimeFrame.Day,
        limit=100
    )
    
    signals = []
    
    for ticker in tickers:
        if ticker in bars_dict:
            # Calculate indicators
            df = data_handler.calculate_indicators(
                ticker,
                indicators=['SMA_20', 'SMA_50', 'RSI', 'MACD']
            )
            
            # Get signal
            signal = strategy.analyze(ticker, df)
            signals.append(signal)
            
            # Display
            print(f"{ticker:6} | {signal.action:4} | {signal.strength:5.1%} | {signal.reason[:50]}")
    
    # Find strongest signals
    buy_signals = [s for s in signals if s.action == 'BUY']
    if buy_signals:
        strongest = max(buy_signals, key=lambda s: s.strength)
        print(f"\n🎯 Strongest BUY signal: {strongest.symbol} ({strongest.strength:.1%})")
    else:
        print("\n⚠️  No buy signals found")


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "PERPLEXITY-ALPACA EXAMPLES" + " " * 32 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Example 1: Generate local prompt (most common)
    example_1_generate_local_prompt()
    
    # Example 2: Strategy analysis
    example_2_analyze_with_strategy()
    
    # Example 3: Paper trading simulation
    example_3_paper_trading_simulation()
    
    # Example 4: Real-time monitoring (async)
    # Uncomment to run (requires market hours or paper trading data)
    # asyncio.run(example_4_realtime_monitoring())
    
    # Example 5: Multi-ticker analysis
    example_5_multi_ticker_analysis()
    
    print("\n" + "=" * 80)
    print("✅ All examples completed!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Check generated prompts in local_tasks/")
    print("2. Run your own analysis with main.py")
    print("3. Customize strategies in src/strategy.py")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    # Note: Some examples require valid API keys in .env
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. Valid API keys in .env")
        print("2. Activated virtual environment (source venv/bin/activate)")
        print("3. Installed dependencies (pip install -r requirements.txt)")
