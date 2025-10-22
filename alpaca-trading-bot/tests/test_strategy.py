"""
Test suite for trading strategies
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.strategy import (
    MomentumStrategy,
    MeanReversionStrategy,
    SentimentStrategy,
    StrategyManager,
    Signal,
    TradingSignal
)


@pytest.fixture
def sample_market_data():
    """Generate sample market data for testing"""
    dates = pd.date_range(end=datetime.now(), periods=100, freq='H')
    
    data = pd.DataFrame({
        'open': np.random.uniform(140, 160, 100),
        'high': np.random.uniform(145, 165, 100),
        'low': np.random.uniform(135, 155, 100),
        'close': np.random.uniform(140, 160, 100),
        'volume': np.random.uniform(1000000, 5000000, 100),
        'RSI': np.random.uniform(20, 80, 100),
        'MACD': np.random.uniform(-2, 2, 100),
        'MACD_signal': np.random.uniform(-2, 2, 100),
        'BB_upper': np.random.uniform(155, 165, 100),
        'BB_lower': np.random.uniform(135, 145, 100),
        'BB_middle': np.random.uniform(145, 155, 100),
        'ATR': np.random.uniform(1, 3, 100)
    }, index=dates)
    
    return data


@pytest.fixture
def sample_sentiment_data():
    """Generate sample sentiment data"""
    return {
        "sentiment_score": 0.75,
        "news_sentiment": "Bullish",
        "social_mentions_trend": 1.8,
        "catalyst": "Earnings beat expectations"
    }


class TestMomentumStrategy:
    """Test momentum trading strategy"""
    
    def test_initialization(self):
        """Test strategy initialization"""
        config = {"rsi_threshold_buy": 65}
        strategy = MomentumStrategy(config)
        
        assert strategy.name == "Momentum"
        assert strategy.rsi_threshold_buy == 65
    
    def test_bullish_signal(self, sample_market_data):
        """Test bullish signal generation"""
        strategy = MomentumStrategy({})
        
        # Set bullish conditions
        sample_market_data['RSI'].iloc[-1] = 65
        sample_market_data['close'].iloc[-1] = sample_market_data['high'].rolling(20).max().iloc[-1]
        
        signal = strategy.analyze("AAPL", sample_market_data)
        
        assert signal is not None
        assert signal.signal in [Signal.BUY, Signal.STRONG_BUY]
        assert signal.confidence > 0.5
    
    def test_position_sizing(self):
        """Test position size calculation"""
        strategy = MomentumStrategy({"max_position_size": 0.1})
        
        size = strategy.calculate_position_size(
            capital=100000,
            risk_per_trade=0.02,
            entry_price=150,
            stop_loss=147
        )
        
        assert size > 0
        assert size * 150 <= 100000 * 0.1  # Max position size constraint


class TestMeanReversionStrategy:
    """Test mean reversion strategy"""
    
    def test_oversold_signal(self, sample_market_data):
        """Test oversold buy signal"""
        strategy = MeanReversionStrategy({})
        
        # Set oversold conditions
        sample_market_data['close'].iloc[-1] = sample_market_data['BB_lower'].iloc[-1] - 1
        sample_market_data['RSI'].iloc[-1] = 25
        
        signal = strategy.analyze("AAPL", sample_market_data)
        
        assert signal is not None
        assert signal.signal == Signal.BUY
        assert signal.stop_loss < signal.entry_price
    
    def test_overbought_signal(self, sample_market_data):
        """Test overbought sell signal"""
        strategy = MeanReversionStrategy({})
        
        # Set overbought conditions
        sample_market_data['close'].iloc[-1] = sample_market_data['BB_upper'].iloc[-1] + 1
        sample_market_data['RSI'].iloc[-1] = 75
        
        signal = strategy.analyze("AAPL", sample_market_data)
        
        assert signal is not None
        assert signal.signal == Signal.SELL


class TestSentimentStrategy:
    """Test sentiment-based strategy"""
    
    def test_positive_sentiment(self, sample_market_data, sample_sentiment_data):
        """Test positive sentiment signal"""
        strategy = SentimentStrategy({})
        
        signal = strategy.analyze("AAPL", sample_market_data, sample_sentiment_data)
        
        assert signal is not None
        assert signal.signal == Signal.BUY
        assert "sentiment" in signal.metadata
    
    def test_no_sentiment_data(self, sample_market_data):
        """Test behavior with no sentiment data"""
        strategy = SentimentStrategy({})
        
        signal = strategy.analyze("AAPL", sample_market_data, None)
        
        assert signal is None


class TestStrategyManager:
    """Test strategy manager"""
    
    def test_initialization(self):
        """Test manager initialization"""
        config = {
            "strategies": {
                "momentum": {"enabled": True},
                "mean_reversion": {"enabled": False}
            }
        }
        
        manager = StrategyManager(config)
        
        assert "momentum" in manager.strategies
        assert "mean_reversion" not in manager.strategies
    
    def test_get_signal(self, sample_market_data):
        """Test getting signal from specific strategy"""
        manager = StrategyManager({
            "strategies": {"momentum": {"enabled": True}}
        })
        
        signal = manager.get_signal("AAPL", sample_market_data, strategy_name="momentum")
        
        # Signal may be None if conditions not met
        assert signal is None or isinstance(signal, TradingSignal)
    
    def test_combined_signal(self, sample_market_data, sample_sentiment_data):
        """Test combined signal from multiple strategies"""
        config = {
            "strategies": {
                "momentum": {"enabled": True},
                "sentiment": {"enabled": True}
            },
            "strategy_weights": {
                "momentum": 0.5,
                "sentiment": 0.5
            }
        }
        
        manager = StrategyManager(config)
        
        # Force bullish conditions
        sample_market_data['RSI'].iloc[-1] = 70
        sample_market_data['close'].iloc[-1] = 160
        
        signal = manager.get_combined_signal("AAPL", sample_market_data, sample_sentiment_data)
        
        if signal:
            assert signal.metadata.get("combined") == True
            assert "strategies" in signal.metadata


class TestTradingSignal:
    """Test trading signal object"""
    
    def test_signal_creation(self):
        """Test creating a trading signal"""
        signal = TradingSignal(
            symbol="AAPL",
            signal=Signal.BUY,
            confidence=0.8,
            entry_price=150.00,
            stop_loss=147.00,
            take_profit=156.00,
            position_size=100,
            reasons=["RSI bullish", "MACD crossover"],
            timestamp=datetime.now(),
            metadata={"rsi": 65}
        )
        
        assert signal.symbol == "AAPL"
        assert signal.signal == Signal.BUY
        assert signal.confidence == 0.8
        assert len(signal.reasons) == 2
        assert "rsi" in signal.metadata


@pytest.mark.parametrize("signal_type,expected", [
    (Signal.STRONG_BUY, 2),
    (Signal.BUY, 1),
    (Signal.HOLD, 0),
    (Signal.SELL, -1),
    (Signal.STRONG_SELL, -2)
])
def test_signal_values(signal_type, expected):
    """Test signal enum values"""
    assert signal_type.value == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])