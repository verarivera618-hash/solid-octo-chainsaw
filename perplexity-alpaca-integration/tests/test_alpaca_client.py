"""
Tests for Alpaca client functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import pandas as pd

from src.alpaca_client import (
    AlpacaDataClient, AlpacaTradingClient, MarketData, Quote, Trade
)
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.enums import OrderSide, TimeInForce

class TestAlpacaDataClient:
    """Test cases for AlpacaDataClient."""
    
    @pytest.fixture
    def mock_data_client(self):
        """Create a mock Alpaca data client."""
        with patch('src.alpaca_client.StockHistoricalDataClient') as mock_historical, \
             patch('src.alpaca_client.StockDataStream') as mock_stream:
            
            client = AlpacaDataClient(api_key="test_key", secret_key="test_secret")
            return client, mock_historical, mock_stream
    
    def test_client_initialization(self):
        """Test client initialization."""
        with patch('src.alpaca_client.StockHistoricalDataClient'), \
             patch('src.alpaca_client.StockDataStream'):
            
            client = AlpacaDataClient(api_key="test_key", secret_key="test_secret")
            assert client.api_key == "test_key"
            assert client.secret_key == "test_secret"
    
    def test_get_historical_bars(self, mock_data_client):
        """Test historical bars retrieval."""
        client, mock_historical, mock_stream = mock_data_client
        
        # Mock bar data
        mock_bar = Mock()
        mock_bar.timestamp = datetime.now()
        mock_bar.open = 150.0
        mock_bar.high = 152.0
        mock_bar.low = 149.0
        mock_bar.close = 151.0
        mock_bar.volume = 1000000
        mock_bar.vwap = 150.5
        
        mock_bars = {"AAPL": [mock_bar]}
        client.historical_client.get_stock_bars.return_value = mock_bars
        
        result = client.get_historical_bars(
            symbols=["AAPL"],
            timeframe=TimeFrame.Day,
            start=datetime.now() - timedelta(days=30)
        )
        
        assert "AAPL" in result
        assert isinstance(result["AAPL"], pd.DataFrame)
        assert len(result["AAPL"]) == 1
        assert result["AAPL"].iloc[0]['close'] == 151.0
    
    def test_get_latest_quotes(self, mock_data_client):
        """Test latest quotes retrieval."""
        client, mock_historical, mock_stream = mock_data_client
        
        # Mock quote data
        mock_quote = Mock()
        mock_quote.timestamp = datetime.now()
        mock_quote.bid_price = 149.50
        mock_quote.ask_price = 150.50
        mock_quote.bid_size = 100
        mock_quote.ask_size = 200
        
        mock_quotes = {"AAPL": mock_quote}
        client.historical_client.get_stock_latest_quote.return_value = mock_quotes
        
        result = client.get_latest_quotes(["AAPL"])
        
        assert "AAPL" in result
        assert isinstance(result["AAPL"], Quote)
        assert result["AAPL"].bid_price == 149.50
        assert result["AAPL"].ask_price == 150.50
    
    def test_market_data_structure(self):
        """Test MarketData dataclass."""
        data = MarketData(
            symbol="AAPL",
            timestamp=datetime.now(),
            open=150.0,
            high=152.0,
            low=149.0,
            close=151.0,
            volume=1000000,
            vwap=150.5
        )
        
        assert data.symbol == "AAPL"
        assert data.close == 151.0
        assert data.volume == 1000000
    
    def test_quote_structure(self):
        """Test Quote dataclass."""
        quote = Quote(
            symbol="AAPL",
            timestamp=datetime.now(),
            bid_price=149.50,
            ask_price=150.50,
            bid_size=100,
            ask_size=200
        )
        
        assert quote.symbol == "AAPL"
        assert quote.bid_price == 149.50
        assert quote.ask_price == 150.50
    
    @pytest.mark.asyncio
    async def test_streaming_handlers(self, mock_data_client):
        """Test streaming data handlers."""
        client, mock_historical, mock_stream = mock_data_client
        
        # Test bar handler
        mock_bar = Mock()
        mock_bar.symbol = "AAPL"
        mock_bar.timestamp = datetime.now()
        mock_bar.open = 150.0
        mock_bar.high = 152.0
        mock_bar.low = 149.0
        mock_bar.close = 151.0
        mock_bar.volume = 1000000
        mock_bar.vwap = 150.5
        
        await client._handle_bar(mock_bar)
        
        assert "AAPL" in client.latest_bars
        assert client.latest_bars["AAPL"].close == 151.0
    
    def test_rate_limiting(self, mock_data_client):
        """Test rate limiting functionality."""
        client, mock_historical, mock_stream = mock_data_client
        
        with patch('src.alpaca_client.time') as mock_time:
            mock_time.time.side_effect = [0, 0.1, 0.5]  # Quick successive calls
            mock_time.sleep = Mock()
            
            client._rate_limit_check()
            client._rate_limit_check()
            
            # Should call sleep for rate limiting
            mock_time.sleep.assert_called()

class TestAlpacaTradingClient:
    """Test cases for AlpacaTradingClient."""
    
    @pytest.fixture
    def mock_trading_client(self):
        """Create a mock Alpaca trading client."""
        with patch('src.alpaca_client.TradingClient') as mock_client:
            client = AlpacaTradingClient(
                api_key="test_key", 
                secret_key="test_secret", 
                paper=True
            )
            return client, mock_client
    
    def test_client_initialization(self):
        """Test trading client initialization."""
        with patch('src.alpaca_client.TradingClient'):
            client = AlpacaTradingClient(
                api_key="test_key", 
                secret_key="test_secret", 
                paper=True
            )
            assert client.api_key == "test_key"
            assert client.paper is True
    
    def test_get_account(self, mock_trading_client):
        """Test account information retrieval."""
        client, mock_client = mock_trading_client
        
        # Mock account data
        mock_account = Mock()
        mock_account.id = "test_account_id"
        mock_account.account_number = "123456789"
        mock_account.status = "ACTIVE"
        mock_account.currency = "USD"
        mock_account.buying_power = "50000.00"
        mock_account.cash = "25000.00"
        mock_account.portfolio_value = "100000.00"
        mock_account.equity = "100000.00"
        mock_account.last_equity = "99500.00"
        mock_account.multiplier = "4"
        mock_account.initial_margin = "0"
        mock_account.maintenance_margin = "0"
        mock_account.daytrade_count = 0
        mock_account.daytrading_buying_power = "200000.00"
        
        client.client.get_account.return_value = mock_account
        
        result = client.get_account()
        
        assert result['id'] == "test_account_id"
        assert result['buying_power'] == 50000.00
        assert result['portfolio_value'] == 100000.00
    
    def test_submit_market_order(self, mock_trading_client):
        """Test market order submission."""
        client, mock_client = mock_trading_client
        
        # Mock order response
        mock_order = Mock()
        mock_order.id = "order_123"
        mock_order.symbol = "AAPL"
        mock_order.qty = "10"
        mock_order.side = OrderSide.BUY
        mock_order.order_type = "market"
        mock_order.time_in_force = TimeInForce.DAY
        mock_order.status = "new"
        mock_order.created_at = datetime.now()
        mock_order.filled_qty = "0"
        mock_order.filled_avg_price = None
        
        client.client.submit_order.return_value = mock_order
        
        result = client.submit_market_order(
            symbol="AAPL",
            qty=10,
            side=OrderSide.BUY
        )
        
        assert result['id'] == "order_123"
        assert result['symbol'] == "AAPL"
        assert result['qty'] == 10.0
        assert result['side'] == OrderSide.BUY
    
    def test_submit_limit_order(self, mock_trading_client):
        """Test limit order submission."""
        client, mock_client = mock_trading_client
        
        # Mock order response
        mock_order = Mock()
        mock_order.id = "order_456"
        mock_order.symbol = "MSFT"
        mock_order.qty = "5"
        mock_order.side = OrderSide.SELL
        mock_order.order_type = "limit"
        mock_order.limit_price = "300.00"
        mock_order.time_in_force = TimeInForce.DAY
        mock_order.status = "new"
        mock_order.created_at = datetime.now()
        mock_order.filled_qty = "0"
        mock_order.filled_avg_price = None
        
        client.client.submit_order.return_value = mock_order
        
        result = client.submit_limit_order(
            symbol="MSFT",
            qty=5,
            side=OrderSide.SELL,
            limit_price=300.00
        )
        
        assert result['id'] == "order_456"
        assert result['symbol'] == "MSFT"
        assert result['limit_price'] == 300.00
    
    def test_get_positions(self, mock_trading_client):
        """Test positions retrieval."""
        client, mock_client = mock_trading_client
        
        # Mock position data
        mock_position = Mock()
        mock_position.symbol = "AAPL"
        mock_position.qty = "100"
        mock_position.side = "long"
        mock_position.market_value = "15000.00"
        mock_position.cost_basis = "14500.00"
        mock_position.unrealized_pl = "500.00"
        mock_position.unrealized_plpc = "0.0345"
        mock_position.current_price = "150.00"
        mock_position.lastday_price = "149.00"
        mock_position.change_today = "1.00"
        
        client.client.get_all_positions.return_value = [mock_position]
        
        result = client.get_positions()
        
        assert len(result) == 1
        assert result[0]['symbol'] == "AAPL"
        assert result[0]['qty'] == 100.0
        assert result[0]['unrealized_pl'] == 500.0
    
    def test_cancel_order(self, mock_trading_client):
        """Test order cancellation."""
        client, mock_client = mock_trading_client
        
        client.client.cancel_order_by_id.return_value = None
        
        result = client.cancel_order("order_123")
        
        assert result is True
        client.client.cancel_order_by_id.assert_called_once_with("order_123")
    
    def test_close_position(self, mock_trading_client):
        """Test position closing."""
        client, mock_client = mock_trading_client
        
        # Mock close position response
        mock_order = Mock()
        mock_order.id = "close_order_789"
        mock_order.symbol = "AAPL"
        mock_order.qty = "100"
        mock_order.side = OrderSide.SELL
        mock_order.order_type = "market"
        mock_order.status = "new"
        mock_order.created_at = datetime.now()
        
        client.client.close_position.return_value = mock_order
        
        result = client.close_position("AAPL")
        
        assert result['id'] == "close_order_789"
        assert result['symbol'] == "AAPL"
        assert result['qty'] == 100.0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])