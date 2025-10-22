#!/usr/bin/env python3
"""
Demo script showing the local trading system in action
No external dependencies - fully copy-paste compatible
"""
import time
from src.local_clients import LocalPerplexityClient, LocalAlpacaDataClient, LocalAlpacaTradingClient
from src.local_data_provider import extract_content

def demo_local_system():
    """Demonstrate the local trading system capabilities"""
    
    print("🚀 Local Trading System Demo")
    print("=" * 50)
    print("✅ No external API keys required")
    print("✅ No internet connection needed")
    print("✅ Fully copy-paste compatible")
    print("✅ All data generated locally")
    print()
    
    # Initialize clients (no API keys needed!)
    print("🔧 Initializing local clients...")
    data_client = LocalAlpacaDataClient()
    trading_client = LocalAlpacaTradingClient()
    analysis_client = LocalPerplexityClient()
    print("✅ All clients initialized successfully")
    print()
    
    # Demo 1: Get account information
    print("💰 Demo 1: Account Information")
    account = trading_client.get_account()
    print(f"   Account ID: {account['account_id']}")
    print(f"   Equity: ${account['equity']:,.2f}")
    print(f"   Cash: ${account['cash']:,.2f}")
    print(f"   Buying Power: ${account['buying_power']:,.2f}")
    print()
    
    # Demo 2: Get market data
    print("📊 Demo 2: Market Data")
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    
    print(f"   Getting historical data for {symbols}...")
    historical_data = data_client.get_historical_bars(symbols, limit=5)
    
    for symbol, df in historical_data.items():
        if not df.empty:
            latest = df.iloc[-1]
            print(f"   {symbol}: ${latest['close']:.2f} (Volume: {latest['volume']:,})")
    
    print(f"\n   Getting latest quotes for {symbols}...")
    quotes = data_client.get_latest_quotes(symbols)
    
    for symbol, quote in quotes.items():
        print(f"   {symbol}: Bid ${quote['bid']:.2f} / Ask ${quote['ask']:.2f}")
    print()
    
    # Demo 3: Technical analysis
    print("🔍 Demo 3: Technical Analysis")
    symbol = 'AAPL'
    
    print(f"   Analyzing {symbol}...")
    analysis = analysis_client.get_technical_analysis([symbol])
    content = extract_content(analysis)
    
    # Show first few lines of analysis
    lines = content.split('\n')[:10]
    for line in lines:
        if line.strip():
            print(f"   {line.strip()}")
    print("   ...")
    print()
    
    # Demo 4: Trading simulation
    print("💸 Demo 4: Trading Simulation")
    
    print(f"   Placing buy order for 10 shares of {symbol}...")
    order = trading_client.place_market_order(symbol, 10, 'buy')
    
    if order:
        print(f"   ✅ Order placed: {order['id']}")
        print(f"   Symbol: {order['symbol']}")
        print(f"   Quantity: {order['qty']}")
        print(f"   Side: {order['side']}")
        print(f"   Status: {order['status']}")
        print(f"   Filled Price: ${order['filled_avg_price']:.2f}")
    
    # Check positions
    print(f"\n   Checking positions...")
    positions = trading_client.get_positions()
    
    if positions:
        for pos in positions:
            pnl_symbol = "🟢" if pos['unrealized_pl'] >= 0 else "🔴"
            print(f"   {pos['symbol']}: {pos['qty']} shares @ ${pos['current_price']:.2f} "
                  f"{pnl_symbol} ${pos['unrealized_pl']:+.2f}")
    else:
        print("   No positions found")
    
    # Check updated account
    print(f"\n   Updated account info...")
    updated_account = trading_client.get_account()
    print(f"   Cash: ${updated_account['cash']:,.2f}")
    print(f"   Equity: ${updated_account['equity']:,.2f}")
    print()
    
    # Demo 5: Market sentiment
    print("📰 Demo 5: Market Sentiment")
    
    print(f"   Getting market sentiment for {symbol}...")
    sentiment = analysis_client.get_market_news_sentiment([symbol])
    sentiment_content = extract_content(sentiment)
    
    # Extract sentiment from content
    sentiment_lines = sentiment_content.split('\n')[:8]
    for line in sentiment_lines:
        if line.strip():
            print(f"   {line.strip()}")
    print("   ...")
    print()
    
    # Demo 6: Performance metrics
    print("📈 Demo 6: Performance Calculation")
    
    # Calculate some basic metrics
    if positions:
        total_value = sum(pos['market_value'] for pos in positions)
        total_pnl = sum(pos['unrealized_pl'] for pos in positions)
        total_cost = sum(pos['qty'] * pos['cost_basis'] for pos in positions)
        
        if total_cost > 0:
            return_pct = (total_pnl / total_cost) * 100
            print(f"   Total Position Value: ${total_value:.2f}")
            print(f"   Total P&L: ${total_pnl:+.2f}")
            print(f"   Return: {return_pct:+.2f}%")
        else:
            print("   No performance data available yet")
    else:
        print("   No positions to calculate performance")
    
    print()
    print("🎉 Demo Complete!")
    print("=" * 50)
    print("Key Benefits:")
    print("✅ No external API subscriptions needed")
    print("✅ No internet connection required")
    print("✅ Perfect for development and testing")
    print("✅ Full copy-paste compatibility")
    print("✅ Realistic market simulation")
    print("✅ Ready for Cursor background agents")

if __name__ == "__main__":
    demo_local_system()