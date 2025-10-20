"""
Integration tests for the Perplexity-Alpaca system
NOTE: These tests require valid API keys in .env
"""

import pytest
import os
from datetime import datetime, timedelta

# Skip all tests if API keys not configured
pytestmark = pytest.mark.skipif(
    not os.getenv("ALPACA_API_KEY") or not os.getenv("PERPLEXITY_API_KEY"),
    reason="API keys not configured"
)


from alpaca.data.timeframe import TimeFrame
from src.data_handler import AlpacaDataHandler
from src.executor import OrderExecutor
from src.perplexity_client import PerplexityFinanceClient


class TestAlpacaDataHandler:
    """Integration tests for Alpaca data handler"""
    
    @pytest.fixture
    def data_handler(self):
        """Create data handler instance"""
        return AlpacaDataHandler()
    
    def test_get_historical_bars(self, data_handler):
        """Test fetching historical bar data"""
        bars = data_handler.get_historical_bars(
            symbols=['AAPL'],
            timeframe=TimeFrame.Day,
            start=datetime.now() - timedelta(days=10),
            limit=10
        )
        
        assert 'AAPL' in bars
        assert len(bars['AAPL']) > 0
        assert 'close' in bars['AAPL'].columns
    
    def test_get_latest_quote(self, data_handler):
        """Test getting latest quote"""
        quotes = data_handler.get_latest_quote(['AAPL'])
        
        assert 'AAPL' in quotes
        assert hasattr(quotes['AAPL'], 'bid_price')
        assert hasattr(quotes['AAPL'], 'ask_price')
    
    def test_calculate_indicators(self, data_handler):
        """Test technical indicator calculation"""
        # Fetch data first
        bars = data_handler.get_historical_bars(
            symbols=['AAPL'],
            timeframe=TimeFrame.Day,
            limit=100
        )
        
        # Calculate indicators
        df = data_handler.calculate_indicators(
            'AAPL',
            indicators=['SMA_20', 'RSI', 'MACD']
        )
        
        assert 'SMA_20' in df.columns
        assert 'RSI' in df.columns
        assert 'MACD' in df.columns
    
    def test_get_price_summary(self, data_handler):
        """Test price summary generation"""
        # Fetch data first
        data_handler.get_historical_bars(
            symbols=['AAPL'],
            timeframe=TimeFrame.Day,
            limit=30
        )
        
        summary = data_handler.get_price_summary('AAPL')
        
        assert summary['symbol'] == 'AAPL'
        assert 'latest_price' in summary
        assert 'change_pct' in summary


class TestOrderExecutor:
    """Integration tests for order executor (paper trading only)"""
    
    @pytest.fixture
    def executor(self):
        """Create executor instance"""
        return OrderExecutor(paper=True)
    
    def test_get_account(self, executor):
        """Test getting account information"""
        account = executor.get_account()
        
        assert 'equity' in account
        assert 'cash' in account
        assert 'buying_power' in account
        assert isinstance(account['equity'], float)
    
    def test_get_positions(self, executor):
        """Test getting positions"""
        positions = executor.get_positions()
        
        assert isinstance(positions, list)
    
    def test_get_position_summary(self, executor):
        """Test position summary"""
        summary = executor.get_position_summary()
        
        assert 'total_positions' in summary
        assert 'total_value' in summary
        assert 'positions' in summary


@pytest.mark.slow
class TestPerplexityClient:
    """
    Integration tests for Perplexity client
    WARNING: These tests cost money (API usage)
    """
    
    @pytest.fixture
    def client(self):
        """Create Perplexity client"""
        return PerplexityFinanceClient()
    
    @pytest.mark.skip(reason="Costs money - run manually")
    def test_get_market_news(self, client):
        """Test fetching market news"""
        insights = client.get_market_news(['AAPL'])
        
        assert insights.content is not None
        assert len(insights.content) > 0
        assert insights.query_type == 'market_news'
        assert 'AAPL' in insights.tickers
    
    @pytest.mark.skip(reason="Costs money - run manually")
    def test_get_sec_filings(self, client):
        """Test SEC filings analysis"""
        insights = client.get_sec_filings_analysis(['AAPL'])
        
        assert insights.content is not None
        assert insights.query_type == 'sec_filings'
        assert len(insights.sources) > 0
