#!/usr/bin/env python3
"""
Demonstration script for Perplexity-Alpaca Integration.
Shows the complete workflow from market analysis to Cursor prompt generation.
"""
import asyncio
import sys
import os
from datetime import datetime
from typing import List

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from main import PerplexityAlpacaIntegration
from prompt_generator import StrategyType

def print_banner():
    """Print demo banner."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    PERPLEXITY-ALPACA INTEGRATION DEMO                       ║
║                                                                              ║
║  🤖 AI-Powered Trading Strategy Generation for Cursor Background Agents     ║
║                                                                              ║
║  This demo shows the complete workflow:                                      ║
║  1. Fetch real-time financial data from Perplexity                         ║
║  2. Analyze market conditions and fundamentals                              ║
║  3. Generate comprehensive Cursor agent prompts                             ║
║  4. Create autonomous trading bot implementations                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

def print_section(title: str, emoji: str = "📋"):
    """Print a section header."""
    print(f"\n{emoji} {title}")
    print("=" * (len(title) + 4))

async def demo_workflow():
    """Demonstrate the complete workflow."""
    
    print_banner()
    
    # Check environment setup
    print_section("Environment Check", "🔧")
    
    required_vars = ['PERPLEXITY_API_KEY', 'ALPACA_API_KEY', 'ALPACA_SECRET_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file or environment")
        print("\nFor demo purposes, we'll show the workflow with mock data...")
        use_mock_data = True
    else:
        print("✅ All required environment variables found")
        use_mock_data = False
    
    # Initialize integration
    print_section("System Initialization", "⚙️")
    
    try:
        integration = PerplexityAlpacaIntegration()
        print("✅ Perplexity-Alpaca integration initialized")
        print("✅ All clients configured")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return
    
    # Test connections (if not using mock data)
    if not use_mock_data:
        print_section("Connection Testing", "🔌")
        
        try:
            results = await integration.test_connections()
            
            for service, status in results.items():
                status_icon = "✅" if status else "❌"
                print(f"{status_icon} {service.replace('_', ' ').title()}: {'Connected' if status else 'Failed'}")
            
            if not all(results.values()):
                print("\n⚠️  Some connections failed. Continuing with available services...")
        
        except Exception as e:
            print(f"❌ Connection testing failed: {e}")
            use_mock_data = True
    
    # Demonstrate different strategy types
    strategies_to_demo = [
        {
            "name": "Tech Momentum Strategy",
            "tickers": ["AAPL", "MSFT", "GOOGL"],
            "strategy": StrategyType.MOMENTUM,
            "time_horizon": "swing",
            "risk": "medium",
            "market": "bullish",
            "requirements": "Focus on AI and cloud computing catalysts"
        },
        {
            "name": "Semiconductor Sector Play",
            "tickers": ["NVDA", "AMD", "INTC"],
            "strategy": StrategyType.SECTOR_ROTATION,
            "time_horizon": "position",
            "risk": "medium",
            "market": "neutral",
            "requirements": "Monitor datacenter demand and AI chip cycles"
        },
        {
            "name": "Earnings Momentum",
            "tickers": ["TSLA", "NFLX"],
            "strategy": StrategyType.EARNINGS_PLAY,
            "time_horizon": "intraday",
            "risk": "high",
            "market": "volatile",
            "requirements": "Focus on earnings surprise and guidance revisions"
        }
    ]
    
    generated_files = []
    
    for i, strategy_config in enumerate(strategies_to_demo, 1):
        print_section(f"Strategy {i}: {strategy_config['name']}", "🎯")
        
        print(f"📊 Target Stocks: {', '.join(strategy_config['tickers'])}")
        print(f"🔄 Strategy Type: {strategy_config['strategy'].value}")
        print(f"⏱️  Time Horizon: {strategy_config['time_horizon']}")
        print(f"⚖️  Risk Level: {strategy_config['risk']}")
        print(f"📈 Market Conditions: {strategy_config['market']}")
        
        if use_mock_data:
            print("\n🔄 Using mock data for demonstration...")
            
            # Create a mock result
            mock_file = f"cursor_tasks/demo_{strategy_config['strategy'].value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            
            # Generate the actual prompt (this will work even without API keys for the structure)
            try:
                result = integration.analyze_and_generate_task(
                    tickers=strategy_config['tickers'],
                    strategy_type=strategy_config['strategy'],
                    time_horizon=strategy_config['time_horizon'],
                    risk_tolerance=strategy_config['risk'],
                    market_conditions=strategy_config['market'],
                    additional_requirements=strategy_config['requirements']
                )
                
                if result.get("success"):
                    print(f"✅ Strategy prompt generated successfully!")
                    print(f"📁 Saved to: {result['prompt_file']}")
                    generated_files.append(result['prompt_file'])
                else:
                    print(f"⚠️  Strategy generation completed with mock data")
                    generated_files.append(mock_file)
            
            except Exception as e:
                print(f"⚠️  Using simplified demo: {e}")
                generated_files.append(mock_file)
        
        else:
            print("\n🔄 Generating strategy with live data...")
            
            try:
                result = integration.analyze_and_generate_task(
                    tickers=strategy_config['tickers'],
                    strategy_type=strategy_config['strategy'],
                    time_horizon=strategy_config['time_horizon'],
                    risk_tolerance=strategy_config['risk'],
                    market_conditions=strategy_config['market'],
                    additional_requirements=strategy_config['requirements']
                )
                
                if result["success"]:
                    print(f"✅ Strategy generated successfully!")
                    print(f"📁 File: {result['prompt_file']}")
                    print(f"📊 Market Analysis: {len(result.get('market_data', {}))} data sources")
                    generated_files.append(result['prompt_file'])
                else:
                    print(f"❌ Strategy generation failed: {result.get('error', 'Unknown error')}")
            
            except Exception as e:
                print(f"❌ Error generating strategy: {e}")
        
        # Small delay between strategies
        if i < len(strategies_to_demo):
            await asyncio.sleep(1)
    
    # Summary and next steps
    print_section("Demo Summary", "📋")
    
    print(f"✅ Generated {len(generated_files)} trading strategies")
    print(f"📁 Files created in cursor_tasks/ directory:")
    
    for file_path in generated_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"   • {os.path.basename(file_path)} ({file_size:,} bytes)")
        else:
            print(f"   • {os.path.basename(file_path)} (demo file)")
    
    print_section("Next Steps with Cursor", "🚀")
    
    print("""
🎯 How to Use Generated Strategies with Cursor Background Agents:

1. 📂 Open Cursor IDE in your project directory
2. ⌨️  Press Ctrl+Shift+B (or ⌘B on Mac) to open Background Agents panel
3. ➕ Click "New Background Agent" 
4. 📋 Copy contents from any generated file in cursor_tasks/
5. 🤖 Let the agent autonomously implement your trading strategy!

⚙️ Cursor Requirements:
   • Privacy Mode must be DISABLED
   • Usage-based spending enabled (minimum $10)
   • GitHub repository with read-write access

🔒 Safety Notes:
   • All strategies default to PAPER TRADING
   • Review generated code before live deployment
   • Start with small position sizes
   • Monitor performance closely
    """)
    
    print_section("Available Commands", "💻")
    
    print("""
🛠️ Try these commands to explore the system:

# Test all API connections
python main.py --test

# Get market overview for specific stocks
python main.py --overview AAPL MSFT GOOGL NVDA

# Generate a custom strategy
python main.py --generate --tickers AAPL MSFT --strategy momentum --risk medium

# Run interactive mode
python main.py

# See all available options
python main.py --help
    """)
    
    print_section("Demo Complete", "🎉")
    
    print("""
✨ The Perplexity-Alpaca integration is ready to use!

This system combines:
• 🧠 Perplexity's real-time financial analysis
• 🤖 Cursor's autonomous code generation
• 📈 Alpaca's professional trading infrastructure

Perfect for algorithmic traders who want AI-powered strategy development! 🚀
    """)

def main():
    """Main demo entry point."""
    try:
        asyncio.run(demo_workflow())
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
        print("Thanks for trying the Perplexity-Alpaca integration!")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        print("Please check your configuration and try again")

if __name__ == "__main__":
    main()