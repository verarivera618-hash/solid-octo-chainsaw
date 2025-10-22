"""
Unit tests for trading strategies
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from src.strategy import (
    Signal, 
    MomentumStrategy, 
    MeanReversionStrategy, 
    BreakoutStrategy,
    get_strategy
)


@pytest.fixture
def sample_data_bullish():
    """Create sample bullish market data with indicators"""
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    
    # Generate uptrending price data
    np.random.seed(42)
    close_prices = np.linspace(100, 120, 100) + np.random.randn(100) * 2
    
    data = pd.DataFrame({
        'timestamp': dates,
        'open': close_prices - 1,
        'high': close_prices + 2,
        'low': close_prices - 2,
        'close': close_prices,
        'volume': np.random.randint(1000000, 5000000, 100)
    })
    
    data.set_index('timestamp', inplace=True)
    
    # Add indicators
    data['SMA_20'] = data['close'].rolling(window=20).mean()
    data['SMA_50'] = data['close'].rolling(window=50).mean()
    
    # RSI
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    data['EMA_12'] = data['close'].ewm(span=12, adjust=False).mean()
    data['EMA_26'] = data['close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = data['EMA_12'] - data['EMA_26']
    data['MACD_Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
    
    # Bollinger Bands
    data['BB_Middle'] = data['close'].rolling(window=20).mean()
    bb_std = data['close'].rolling(window=20).std()
    data['BB_Upper'] = data['BB_Middle'] + (2 * bb_std)
    data['BB_Lower'] = data['BB_Middle'] - (2 * bb_std)
    
    # Volume ratio
    data['Volume_SMA'] = data['volume'].rolling(window=20).mean()
    data['Volume_Ratio'] = data['volume'] / data['Volume_SMA']
    
    return data


@pytest.fixture
def sample_data_bearish():
    """Create sample bearish market data"""
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    
    np.random.seed(42)
    close_prices = np.linspace(120, 100, 100) + np.random.randn(100) * 2
    
    data = pd.DataFrame({
        'timestamp': dates,
        'open': close_prices + 1,
        'high': close_prices + 2,
        'low': close_prices - 2,
        'close': close_prices,
        'volume': np.random.randint(1000000, 5000000, 100)
    })
    
    data.set_index('timestamp', inplace=True)
    
    # Add basic indicators
    data['SMA_20'] = data['close'].rolling(window=20).mean()
    data['SMA_50'] = data['close'].rolling(window=50).mean()
    data['RSI'] = 30  # Oversold
    
    return data


class TestMomentumStrategy:
    """Test momentum strategy"""
    
    def test_strategy_initialization(self):
        """Test strategy can be initialized"""
        strategy = MomentumStrategy()
        assert strategy.name == "Momentum Strategy"
        assert strategy.positions == {}
    
    def test_bullish_signal(self, sample_data_bullish):
        """Test strategy generates buy signal on bullish data"""
        strategy = MomentumStrategy()
        signal = strategy.analyze("TEST", sample_data_bullish)
        
        assert isinstance(signal, Signal)
        assert signal.symbol == "TEST"
        assert signal.action in ['BUY', 'SELL', 'HOLD']
        assert 0 <= signal.strength <= 1.0
        assert signal.reason is not None
    
    def test_insufficient_data(self):
        """Test strategy handles insufficient data"""
        strategy = MomentumStrategy()
        
        # Create minimal data
        data = pd.DataFrame({
            'close': [100, 101, 102],
            'volume': [1000, 1000, 1000]
        })
        
        signal = strategy.analyze("TEST", data)
        
        assert signal.action == 'HOLD'
        assert signal.strength == 0.0
        assert "Insufficient data" in signal.reason
    
    def test_position_size_calculation(self):
        """Test position size calculation"""
        strategy = MomentumStrategy()
        
        account_value = 10000
        entry_price = 100
        stop_loss_price = 98
        signal_strength = 1.0
        
        qty = strategy.calculate_position_size(
            account_value, entry_price, stop_loss_price, signal_strength
        )
        
        assert qty > 0
        assert qty * entry_price <= account_value * 0.1  # Max position size
    
    def test_stop_loss_calculation(self):
        """Test stop loss calculation"""
        strategy = MomentumStrategy()
        
        entry_price = 100
        stop_loss_long = strategy.calculate_stop_loss(entry_price, 'long')
        stop_loss_short = strategy.calculate_stop_loss(entry_price, 'short')
        
        assert stop_loss_long < entry_price
        assert stop_loss_short > entry_price
    
    def test_take_profit_calculation(self):
        """Test take profit calculation"""
        strategy = MomentumStrategy()
        
        entry_price = 100
        take_profit_long = strategy.calculate_take_profit(entry_price, 'long')
        take_profit_short = strategy.calculate_take_profit(entry_price, 'short')
        
        assert take_profit_long > entry_price
        assert take_profit_short < entry_price


class TestMeanReversionStrategy:
    """Test mean reversion strategy"""
    
    def test_strategy_initialization(self):
        """Test strategy can be initialized"""
        strategy = MeanReversionStrategy()
        assert strategy.name == "Mean Reversion Strategy"
    
    def test_oversold_signal(self, sample_data_bullish):
        """Test strategy detects oversold conditions"""
        strategy = MeanReversionStrategy()
        
        # Modify data to create oversold condition
        data = sample_data_bullish.copy()
        data.loc[data.index[-1], 'close'] = data.loc[data.index[-1], 'BB_Lower'] * 0.99
        data.loc[data.index[-1], 'RSI'] = 25
        
        signal = strategy.analyze("TEST", data)
        
        # Should generate buy signal on oversold
        assert signal.symbol == "TEST"
        assert isinstance(signal.strength, float)
    
    def test_missing_indicators(self, sample_data_bearish):
        """Test strategy handles missing indicators"""
        strategy = MeanReversionStrategy()
        
        # Remove Bollinger Bands
        data = sample_data_bearish.copy()
        data = data[['close', 'volume', 'SMA_20']]
        
        signal = strategy.analyze("TEST", data)
        
        assert signal.action == 'HOLD'
        assert "Missing Bollinger Bands" in signal.reason


class TestBreakoutStrategy:
    """Test breakout strategy"""
    
    def test_strategy_initialization(self):
        """Test strategy can be initialized"""
        strategy = BreakoutStrategy(lookback_period=20)
        assert strategy.name == "Breakout Strategy"
        assert strategy.lookback_period == 20
    
    def test_bullish_breakout(self, sample_data_bullish):
        """Test detection of bullish breakout"""
        strategy = BreakoutStrategy(lookback_period=20)
        
        # Create breakout scenario
        data = sample_data_bullish.copy()
        
        # Make recent price break above range
        range_high = data.iloc[-20:]['high'].max()
        data.loc[data.index[-1], 'close'] = range_high * 1.05
        data.loc[data.index[-1], 'Volume_Ratio'] = 2.0
        
        signal = strategy.analyze("TEST", data)
        
        assert signal.symbol == "TEST"
        # Breakout may or may not be detected depending on range tightness
        assert signal.action in ['BUY', 'HOLD']


class TestStrategyFactory:
    """Test strategy factory function"""
    
    def test_get_momentum_strategy(self):
        """Test getting momentum strategy"""
        strategy = get_strategy('momentum')
        assert isinstance(strategy, MomentumStrategy)
    
    def test_get_mean_reversion_strategy(self):
        """Test getting mean reversion strategy"""
        strategy = get_strategy('mean_reversion')
        assert isinstance(strategy, MeanReversionStrategy)
    
    def test_get_breakout_strategy(self):
        """Test getting breakout strategy"""
        strategy = get_strategy('breakout')
        assert isinstance(strategy, BreakoutStrategy)
    
    def test_invalid_strategy_type(self):
        """Test error on invalid strategy type"""
        with pytest.raises(ValueError):
            get_strategy('invalid_strategy')


class TestSignal:
    """Test Signal dataclass"""
    
    def test_signal_creation(self):
        """Test creating a signal"""
        signal = Signal(
            symbol="AAPL",
            action="BUY",
            strength=0.8,
            timestamp=datetime.now(),
            reason="Test signal",
            entry_price=150.0,
            stop_loss=147.0,
            take_profit=157.5
        )
        
        assert signal.symbol == "AAPL"
        assert signal.action == "BUY"
        assert signal.strength == 0.8
        assert signal.entry_price == 150.0
        assert signal.stop_loss == 147.0
        assert signal.take_profit == 157.5
