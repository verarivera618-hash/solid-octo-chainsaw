"""
Local main entry point - Runs the trading system without external dependencies
"""
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any
import os
import sys

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config_local import LocalConfig
from local_data_client import LocalDataClient
from local_trading_client import LocalTradingClient, OrderSide, TimeInForce
from local_analysis_client import LocalAnalysisClient

class LocalTradingSystem:
    """Main trading system that runs completely locally"""
    
    def __init__(self):
        self.config = LocalConfig
        self.config.ensure_directories()
        
        self.data_client = LocalDataClient()
        self.trading_client = LocalTradingClient()
        self.analysis_client = LocalAnalysisClient()
        
        print("=" * 60)
        print("Local Trading System - No External Dependencies")
        print("=" * 60)
        print(f"Initial Capital: ${self.config.INITIAL_CAPITAL:,.2f}")
        print(f"Data Source: {self.config.LOCAL_DATA_SOURCE}")
        print(f"Database: {self.config.DB_PATH}")
        print("=" * 60)
    
    def run_backtest(self, symbols: List[str], strategy: str = "momentum", days: int = 30):
        """Run a backtest on historical data"""
        print(f"\nRunning backtest for {symbols} using {strategy} strategy...")
        
        # Generate or load historical data
        historical_data = self.data_client.get_historical_bars(symbols, limit=days)
        
        results = {
            'strategy': strategy,
            'symbols': symbols,
            'period': f"{days} days",
            'trades': [],
            'performance': {}
        }
        
        for symbol in symbols:
            if symbol in historical_data:
                df = historical_data[symbol]
                df = self.data_client.calculate_technical_indicators(df)
                
                # Run strategy
                if strategy == "momentum":
                    trades = self._run_momentum_strategy(symbol, df)
                elif strategy == "mean_reversion":
                    trades = self._run_mean_reversion_strategy(symbol, df)
                else:
                    trades = self._run_simple_ma_strategy(symbol, df)
                
                results['trades'].extend(trades)
        
        # Calculate performance metrics
        results['performance'] = self._calculate_performance_metrics(results['trades'])
        
        return results
    
    def _run_momentum_strategy(self, symbol: str, df: pd.DataFrame) -> List[Dict]:
        """Simple momentum strategy"""
        trades = []
        position = None
        
        for i in range(20, len(df)):
            current_row = df.iloc[i]
            
            # Entry signal
            if position is None:
                if (current_row['rsi'] > 50 and current_row['rsi'] < 70 and
                    current_row['macd'] > current_row['macd_signal']):
                    
                    # Buy signal
                    position = {
                        'symbol': symbol,
                        'entry_date': df.index[i],
                        'entry_price': current_row['close'],
                        'quantity': 100
                    }
            
            # Exit signal
            elif position is not None:
                if (current_row['rsi'] > 80 or current_row['rsi'] < 30 or
                    current_row['macd'] < current_row['macd_signal']):
                    
                    # Sell signal
                    trade = {
                        **position,
                        'exit_date': df.index[i],
                        'exit_price': current_row['close'],
                        'pnl': (current_row['close'] - position['entry_price']) * position['quantity']
                    }
                    trades.append(trade)
                    position = None
        
        return trades
    
    def _run_mean_reversion_strategy(self, symbol: str, df: pd.DataFrame) -> List[Dict]:
        """Mean reversion strategy using Bollinger Bands"""
        trades = []
        position = None
        
        for i in range(20, len(df)):
            current_row = df.iloc[i]
            
            # Entry signal
            if position is None:
                if current_row['close'] < current_row['bb_lower']:
                    # Buy signal (oversold)
                    position = {
                        'symbol': symbol,
                        'entry_date': df.index[i],
                        'entry_price': current_row['close'],
                        'quantity': 100
                    }
            
            # Exit signal
            elif position is not None:
                if current_row['close'] > current_row['bb_middle']:
                    # Sell signal (return to mean)
                    trade = {
                        **position,
                        'exit_date': df.index[i],
                        'exit_price': current_row['close'],
                        'pnl': (current_row['close'] - position['entry_price']) * position['quantity']
                    }
                    trades.append(trade)
                    position = None
        
        return trades
    
    def _run_simple_ma_strategy(self, symbol: str, df: pd.DataFrame) -> List[Dict]:
        """Simple moving average crossover strategy"""
        trades = []
        position = None
        
        for i in range(50, len(df)):
            current_row = df.iloc[i]
            prev_row = df.iloc[i-1]
            
            # Entry signal
            if position is None:
                if (prev_row['sma_20'] <= prev_row['sma_50'] and 
                    current_row['sma_20'] > current_row['sma_50']):
                    # Golden cross - buy signal
                    position = {
                        'symbol': symbol,
                        'entry_date': df.index[i],
                        'entry_price': current_row['close'],
                        'quantity': 100
                    }
            
            # Exit signal
            elif position is not None:
                if (prev_row['sma_20'] >= prev_row['sma_50'] and 
                    current_row['sma_20'] < current_row['sma_50']):
                    # Death cross - sell signal
                    trade = {
                        **position,
                        'exit_date': df.index[i],
                        'exit_price': current_row['close'],
                        'pnl': (current_row['close'] - position['entry_price']) * position['quantity']
                    }
                    trades.append(trade)
                    position = None
        
        return trades
    
    def _calculate_performance_metrics(self, trades: List[Dict]) -> Dict:
        """Calculate performance metrics from trades"""
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'average_pnl': 0,
                'best_trade': 0,
                'worst_trade': 0,
                'sharpe_ratio': 0
            }
        
        pnls = [t['pnl'] for t in trades]
        winning_trades = [p for p in pnls if p > 0]
        losing_trades = [p for p in pnls if p < 0]
        
        return {
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(trades) if trades else 0,
            'total_pnl': sum(pnls),
            'average_pnl': sum(pnls) / len(pnls) if pnls else 0,
            'best_trade': max(pnls) if pnls else 0,
            'worst_trade': min(pnls) if pnls else 0,
            'sharpe_ratio': self._calculate_sharpe_ratio(pnls)
        }
    
    def _calculate_sharpe_ratio(self, returns: List[float]) -> float:
        """Calculate Sharpe ratio from returns"""
        if not returns or len(returns) < 2:
            return 0
        
        import numpy as np
        returns_array = np.array(returns)
        
        if returns_array.std() == 0:
            return 0
        
        return (returns_array.mean() / returns_array.std()) * np.sqrt(252)
    
    def run_paper_trading(self, symbols: List[str], strategy: str = "momentum"):
        """Run paper trading simulation"""
        print(f"\nStarting paper trading for {symbols} using {strategy} strategy...")
        
        # Get account info
        account = self.trading_client.get_account()
        print(f"Starting Balance: ${account['cash']:,.2f}")
        
        # Get market analysis
        analysis = self.analysis_client.get_market_analysis(symbols)
        momentum = self.analysis_client.get_momentum_analysis(symbols)
        
        # Generate trading signals
        for symbol in symbols:
            if symbol in analysis['analysis']:
                symbol_analysis = analysis['analysis'][symbol]
                symbol_momentum = momentum['momentum_analysis'].get(symbol, {})
                
                print(f"\n{symbol}:")
                print(f"  Current Price: ${symbol_analysis['current_price']:.2f}")
                print(f"  Sentiment: {symbol_analysis['sentiment']}")
                print(f"  Trend: {symbol_analysis['trend']}")
                print(f"  Recommendation: {symbol_analysis['recommendation']}")
                print(f"  Momentum Score: {symbol_momentum.get('score', 0):.3f}")
                
                # Execute trades based on signals
                if symbol_analysis['recommendation'] in ['Buy', 'Strong Buy']:
                    # Calculate position size
                    position_size = account['buying_power'] * self.config.MAX_POSITION_SIZE
                    shares = int(position_size / symbol_analysis['current_price'])
                    
                    if shares > 0:
                        print(f"  -> Placing BUY order for {shares} shares")
                        order = self.trading_client.place_market_order(
                            symbol=symbol,
                            qty=shares,
                            side=OrderSide.BUY
                        )
                        print(f"  -> Order filled at ${order['filled_avg_price']:.2f}")
        
        # Show current positions
        positions = self.trading_client.get_positions()
        if positions:
            print("\nCurrent Positions:")
            for pos in positions:
                print(f"  {pos['symbol']}: {pos['qty']} shares @ ${pos['current_price']:.2f}")
                print(f"    P&L: ${pos['unrealized_pl']:.2f} ({pos['unrealized_plpc']:.2%})")
        
        # Show updated account
        account = self.trading_client.get_account()
        print(f"\nEnding Balance: ${account['cash']:,.2f}")
        print(f"Portfolio Value: ${account['portfolio_value']:,.2f}")
    
    def generate_report(self, output_file: str = None):
        """Generate a comprehensive trading report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'account': self.trading_client.get_account(),
            'positions': self.trading_client.get_positions(),
            'recent_orders': self.trading_client.get_orders()[:10],
            'configuration': {
                'initial_capital': self.config.INITIAL_CAPITAL,
                'max_position_size': self.config.MAX_POSITION_SIZE,
                'risk_tolerance': self.config.RISK_TOLERANCE,
                'commission_rate': self.config.COMMISSION_RATE
            }
        }
        
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"Report saved to {output_file}")
        
        return report

def main():
    """Main entry point for local trading system"""
    system = LocalTradingSystem()
    
    # Example symbols to trade
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'NVDA', 'AMD']
    
    # Menu
    while True:
        print("\n" + "=" * 60)
        print("Local Trading System Menu")
        print("=" * 60)
        print("1. Run Backtest")
        print("2. Run Paper Trading")
        print("3. View Account Status")
        print("4. View Positions")
        print("5. Analyze Markets")
        print("6. Generate Report")
        print("7. Generate Sample Data")
        print("8. Exit")
        print("=" * 60)
        
        choice = input("Enter your choice (1-8): ").strip()
        
        if choice == '1':
            # Run backtest
            strategy = input("Enter strategy (momentum/mean_reversion/ma_crossover): ").strip()
            days = int(input("Enter number of days to backtest (default 30): ").strip() or "30")
            
            results = system.run_backtest(symbols, strategy, days)
            
            print(f"\nBacktest Results:")
            print(f"Total Trades: {results['performance']['total_trades']}")
            print(f"Win Rate: {results['performance']['win_rate']:.2%}")
            print(f"Total P&L: ${results['performance']['total_pnl']:.2f}")
            print(f"Average P&L: ${results['performance']['average_pnl']:.2f}")
            print(f"Sharpe Ratio: {results['performance']['sharpe_ratio']:.2f}")
        
        elif choice == '2':
            # Run paper trading
            strategy = input("Enter strategy (momentum/mean_reversion/ma_crossover): ").strip()
            system.run_paper_trading(symbols, strategy)
        
        elif choice == '3':
            # View account
            account = system.trading_client.get_account()
            print(f"\nAccount Status:")
            print(f"  Cash: ${account['cash']:,.2f}")
            print(f"  Portfolio Value: ${account['portfolio_value']:,.2f}")
            print(f"  Buying Power: ${account['buying_power']:,.2f}")
        
        elif choice == '4':
            # View positions
            positions = system.trading_client.get_positions()
            if positions:
                print(f"\nCurrent Positions:")
                for pos in positions:
                    print(f"  {pos['symbol']}: {pos['qty']} shares")
                    print(f"    Current Price: ${pos['current_price']:.2f}")
                    print(f"    P&L: ${pos['unrealized_pl']:.2f} ({pos['unrealized_plpc']:.2%})")
            else:
                print("\nNo open positions")
        
        elif choice == '5':
            # Analyze markets
            analysis = system.analysis_client.get_market_analysis(symbols)
            for symbol, data in analysis['analysis'].items():
                print(f"\n{symbol}:")
                print(f"  Price: ${data['current_price']:.2f}")
                print(f"  Sentiment: {data['sentiment']}")
                print(f"  Trend: {data['trend']}")
                print(f"  Recommendation: {data['recommendation']}")
        
        elif choice == '6':
            # Generate report
            filename = f"reports/trading_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            system.generate_report(filename)
        
        elif choice == '7':
            # Generate sample data
            print("Generating sample data...")
            system.data_client.generate_sample_data(symbols, days=365)
            print(f"Sample data generated for {symbols}")
        
        elif choice == '8':
            print("Exiting...")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    # Handle missing pandas import
    try:
        import pandas as pd
    except ImportError:
        print("Installing required pandas library...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas", "numpy"])
        import pandas as pd
    
    main()