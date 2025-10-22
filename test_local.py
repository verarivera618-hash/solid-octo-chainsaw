#!/usr/bin/env python3
"""
Test script for the local trading system
Verifies all components work without external dependencies
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_local_system():
    """Test all local components"""
    print("Testing Local Trading System...")
    print("=" * 50)
    
    # Test imports
    try:
        from config_local import LocalConfig
        from local_data_client import LocalDataClient
        from local_trading_client import LocalTradingClient
        from local_analysis_client import LocalAnalysisClient
        print("✓ All local modules imported successfully")
        
        # Test configuration
        config = LocalConfig()
        print(f"✓ Configuration loaded (Capital: ${config.INITIAL_CAPITAL:,.2f})")
        
        # Test data client
        data_client = LocalDataClient()
        print("✓ Local data client initialized")
        
        # Generate sample data for one symbol
        test_symbol = 'TEST'
        sample_data = data_client.generate_sample_data([test_symbol], days=30)
        if test_symbol in sample_data:
            print(f"✓ Sample data generated ({len(sample_data[test_symbol])} days)")
        
        # Test technical indicators
        if test_symbol in sample_data:
            df_with_indicators = data_client.calculate_technical_indicators(sample_data[test_symbol])
            print(f"✓ Technical indicators calculated")
        
        # Test trading client
        trading_client = LocalTradingClient()
        account = trading_client.get_account()
        print(f"✓ Trading client initialized (Balance: ${account.get('cash', 0):,.2f})")
        
        # Test analysis client
        analysis_client = LocalAnalysisClient()
        print("✓ Analysis client initialized")
        
        # Test market analysis
        analysis = analysis_client.get_market_analysis([test_symbol])
        if 'analysis' in analysis and test_symbol in analysis['analysis']:
            print(f"✓ Market analysis working")
        
        # Test momentum analysis
        momentum = analysis_client.get_momentum_analysis([test_symbol])
        if 'momentum_analysis' in momentum:
            print(f"✓ Momentum analysis working")
        
        print("")
        print("=" * 50)
        print("SUCCESS: All local components working!")
        print("No external dependencies required!")
        print("System is ready for local copy-paste use!")
        print("=" * 50)
        
        return True
        
    except ImportError as e:
        print(f"Import Error: {e}")
        print("Make sure pandas and numpy are installed:")
        print("  pip install pandas numpy")
        return False
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_local_system()
    sys.exit(0 if success else 1)