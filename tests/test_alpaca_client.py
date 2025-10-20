"""
Unit tests for Alpaca clients
"""
import pytest
from unittest.mock import Mock, patch
import pandas as pd
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.alpaca_client import AlpacaDataClient, AlpacaTradingClient

class TestAlpacaDataClient:
    """Test cases for AlpacaDataClient"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.client = AlpacaDataClient(api_key="test_key", secret_key="test_secret")
    
    @patch('src.alpaca_client.StockHistoricalDataClient')
    def test_get_historical_bars_success(self, mock_client_class):
        """Test successful historical bars retrieval"""
        # Mock bar data
        mock_bar1 = Mock()
        mock_bar1.timestamp = "2024-01-01T00:00:00Z"
        mock_bar1.open = 100.0
        mock_bar1.high = 105.0
        mock_bar1.low = 95.0
        mock_bar1.close = 102.0
        mock_bar1.volume = 1000000
        mock_bar1.trade_count = 1000
        mock_bar1.vwap = 101.0
        
        mock_bar2 = Mock()
        mock_bar2.timestamp = "2024-01-02T00:00:00Z"
        mock_bar2.open = 102.0
        mock_bar2.high = 108.0
        mock_bar2.low = 98.0
        mock_bar2.close = 105.0
        mock_bar2.volume = 1200000
        mock_bar2.trade_count = 1100
        mock_bar2.vwap = 103.0
        
        # Mock client and response
        mock_client = Mock()
        mock_client.get_stock_bars.return_value = {"AAPL": [mock_bar1, mock_bar2]}
        mock_client_class.return_value = mock_client
        self.client.data_client = mock_client
        
        result = self.client.get_historical_bars(["AAPL"])
        
        assert "AAPL" in result
        assert isinstance(result["AAPL"], pd.DataFrame)
        assert len(result["AAPL"]) == 2
        assert result["AAPL"].iloc[0]["close"] == 102.0
    
    @patch('src.alpaca_client.StockHistoricalDataClient')
    def test_get_historical_bars_error(self, mock_client_class):
        """Test historical bars retrieval with error"""
        mock_client = Mock()
        mock_client.get_stock_bars.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        self.client.data_client = mock_client
        
        result = self.client.get_historical_bars(["AAPL"])
        
        assert result == {}
    
    def test_calculate_technical_indicators(self):
        """Test technical indicators calculation"""
        # Create sample data
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
        
        df = pd.DataFrame({
            'open': prices + np.random.randn(100) * 0.1,
            'high': prices + np.abs(np.random.randn(100) * 0.5),
            'low': prices - np.abs(np.random.randn(100) * 0.5),
            'close': prices,
            'volume': np.random.randint(1000000, 2000000, 100)
        }, index=dates)
        
        result = self.client.calculate_technical_indicators(df)
        
        # Check that technical indicators are calculated
        assert 'sma_20' in result.columns
        assert 'sma_50' in result.columns
        assert 'ema_12' in result.columns
        assert 'ema_26' in result.columns
        assert 'macd' in result.columns
        assert 'rsi' in result.columns
        assert 'bb_upper' in result.columns
        assert 'bb_lower' in result.columns
        assert 'atr' in result.columns
        
        # Check that indicators have reasonable values
        assert not result['sma_20'].isna().all()
        assert not result['rsi'].isna().all()
        assert result['rsi'].max() <= 100
        assert result['rsi'].min() >= 0

class TestAlpacaTradingClient:
    """Test cases for AlpacaTradingClient"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.client = AlpacaTradingClient(api_key="test_key", secret_key="test_secret")
    
    @patch('src.alpaca_client.TradingClient')
    def test_get_account_success(self, mock_client_class):
        """Test successful account retrieval"""
        # Mock account data
        mock_account = Mock()
        mock_account.id = "test_account_id"
        mock_account.equity = 100000.0
        mock_account.cash = 50000.0
        mock_account.buying_power = 100000.0
        mock_account.portfolio_value = 100000.0
        mock_account.day_trade_count = 0
        mock_account.pattern_day_trader = False
        
        # Mock client
        mock_client = Mock()
        mock_client.get_account.return_value = mock_account
        mock_client_class.return_value = mock_client
        self.client.trading_client = mock_client
        
        result = self.client.get_account()
        
        assert result['account_id'] == "test_account_id"
        assert result['equity'] == 100000.0
        assert result['cash'] == 50000.0
    
    @patch('src.alpaca_client.TradingClient')
    def test_get_account_error(self, mock_client_class):
        """Test account retrieval with error"""
        mock_client = Mock()
        mock_client.get_account.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        self.client.trading_client = mock_client
        
        result = self.client.get_account()
        
        assert result == {}
    
    @patch('src.alpaca_client.TradingClient')
    def test_get_positions_success(self, mock_client_class):
        """Test successful positions retrieval"""
        # Mock position data
        mock_position = Mock()
        mock_position.symbol = "AAPL"
        mock_position.qty = 100.0
        mock_position.side = "long"
        mock_position.market_value = 15000.0
        mock_position.cost_basis = 14000.0
        mock_position.unrealized_pl = 1000.0
        mock_position.unrealized_plpc = 0.071
        mock_position.current_price = 150.0
        
        # Mock client
        mock_client = Mock()
        mock_client.get_all_positions.return_value = [mock_position]
        mock_client_class.return_value = mock_client
        self.client.trading_client = mock_client
        
        result = self.client.get_positions()
        
        assert len(result) == 1
        assert result[0]['symbol'] == "AAPL"
        assert result[0]['qty'] == 100.0
        assert result[0]['unrealized_pl'] == 1000.0
    
    @patch('src.alpaca_client.TradingClient')
    def test_place_market_order_success(self, mock_client_class):
        """Test successful market order placement"""
        from src.alpaca_client import OrderSide, TimeInForce
        
        # Mock order
        mock_order = Mock()
        mock_order.id = "test_order_id"
        mock_order.symbol = "AAPL"
        mock_order.qty = 100.0
        mock_order.side = OrderSide.BUY
        
        # Mock client
        mock_client = Mock()
        mock_client.submit_order.return_value = mock_order
        mock_client_class.return_value = mock_client
        self.client.trading_client = mock_client
        
        result = self.client.place_market_order("AAPL", 100.0, OrderSide.BUY)
        
        assert result is not None
        assert result.symbol == "AAPL"
        assert result.qty == 100.0
    
    @patch('src.alpaca_client.TradingClient')
    def test_place_market_order_error(self, mock_client_class):
        """Test market order placement with error"""
        from src.alpaca_client import OrderSide
        
        mock_client = Mock()
        mock_client.submit_order.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        self.client.trading_client = mock_client
        
        result = self.client.place_market_order("AAPL", 100.0, OrderSide.BUY)
        
        assert result is None