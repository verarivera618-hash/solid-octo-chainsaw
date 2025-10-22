"""
Tests for Perplexity client functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.perplexity_client import (
    PerplexityFinanceClient, FinancialQuery, QueryType
)

class TestPerplexityFinanceClient:
    """Test cases for PerplexityFinanceClient."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Perplexity client."""
        with patch('src.perplexity_client.requests') as mock_requests:
            mock_response = Mock()
            mock_response.json.return_value = {
                'choices': [{
                    'message': {
                        'content': 'Test financial analysis content'
                    }
                }]
            }
            mock_response.raise_for_status.return_value = None
            mock_requests.post.return_value = mock_response
            
            client = PerplexityFinanceClient(api_key="test_key")
            return client, mock_requests
    
    def test_client_initialization(self):
        """Test client initialization."""
        client = PerplexityFinanceClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.rate_limit == 60  # Default rate limit
    
    def test_sec_filings_analysis(self, mock_client):
        """Test SEC filings analysis."""
        client, mock_requests = mock_client
        
        result = client.get_sec_filings_analysis(["AAPL", "MSFT"])
        
        assert result == "Test financial analysis content"
        mock_requests.post.assert_called_once()
        
        # Check the request payload
        call_args = mock_requests.post.call_args
        payload = call_args[1]['json']
        
        assert payload['model'] == 'sonar-deep-research'
        assert payload['search_domain'] == 'sec'
        assert 'AAPL' in payload['messages'][0]['content']
        assert 'MSFT' in payload['messages'][0]['content']
    
    def test_market_news_sentiment(self, mock_client):
        """Test market news sentiment analysis."""
        client, mock_requests = mock_client
        
        result = client.get_market_news_sentiment(["AAPL"], days_back=5)
        
        assert result == "Test financial analysis content"
        mock_requests.post.assert_called_once()
        
        # Check the request payload
        call_args = mock_requests.post.call_args
        payload = call_args[1]['json']
        
        assert payload['model'] == 'sonar-pro'
        assert 'web_search_options' in payload
        assert 'AAPL' in payload['messages'][0]['content']
    
    def test_earnings_analysis(self, mock_client):
        """Test earnings analysis."""
        client, mock_requests = mock_client
        
        result = client.get_earnings_analysis(["GOOGL"])
        
        assert result == "Test financial analysis content"
        mock_requests.post.assert_called_once()
        
        call_args = mock_requests.post.call_args
        payload = call_args[1]['json']
        
        assert 'earnings' in payload['messages'][0]['content'].lower()
        assert 'GOOGL' in payload['messages'][0]['content']
    
    def test_comprehensive_analysis(self, mock_client):
        """Test comprehensive analysis."""
        client, mock_requests = mock_client
        
        query = FinancialQuery(
            tickers=["AAPL", "MSFT"],
            query_type=QueryType.FUNDAMENTALS
        )
        
        result = client.get_comprehensive_analysis(query)
        
        # Should make multiple calls for comprehensive analysis
        assert mock_requests.post.call_count >= 2
        assert isinstance(result, dict)
        assert 'sec_analysis' in result or 'earnings_analysis' in result
    
    def test_rate_limiting(self, mock_client):
        """Test rate limiting functionality."""
        client, mock_requests = mock_client
        
        # Mock time to test rate limiting
        with patch('src.perplexity_client.time') as mock_time:
            mock_time.time.side_effect = [0, 0.5, 1.0, 1.5]  # Simulate time progression
            mock_time.sleep = Mock()
            
            # Make two quick requests
            client.get_sec_filings_analysis(["AAPL"])
            client.get_sec_filings_analysis(["MSFT"])
            
            # Should have called sleep due to rate limiting
            mock_time.sleep.assert_called()
    
    def test_structured_data_parsing(self, mock_client):
        """Test structured data parsing."""
        client, mock_requests = mock_client
        
        # Mock JSON response
        mock_requests.post.return_value.json.return_value = {
            'choices': [{
                'message': {
                    'content': '{"AAPL": {"current_price": 150.0, "sentiment_score": 0.7}}'
                }
            }]
        }
        
        result = client.get_structured_data(["AAPL"], "fundamentals")
        
        assert isinstance(result, dict)
        assert "AAPL" in result
        assert result["AAPL"]["current_price"] == 150.0
    
    @patch('src.perplexity_client.requests.post')
    def test_api_error_handling(self, mock_post):
        """Test API error handling."""
        # Mock API error
        mock_post.side_effect = Exception("API Error")
        
        client = PerplexityFinanceClient(api_key="test_key")
        
        with pytest.raises(Exception):
            client.get_sec_filings_analysis(["AAPL"])
    
    def test_query_type_enum(self):
        """Test QueryType enum values."""
        assert QueryType.SEC_FILINGS.value == "sec_filings"
        assert QueryType.MARKET_NEWS.value == "market_news"
        assert QueryType.FUNDAMENTALS.value == "fundamentals"
        assert QueryType.EARNINGS.value == "earnings"
    
    def test_financial_query_structure(self):
        """Test FinancialQuery dataclass."""
        query = FinancialQuery(
            tickers=["AAPL", "MSFT"],
            query_type=QueryType.SEC_FILINGS,
            time_range="30",
            specific_query="Focus on revenue growth"
        )
        
        assert query.tickers == ["AAPL", "MSFT"]
        assert query.query_type == QueryType.SEC_FILINGS
        assert query.time_range == "30"
        assert query.specific_query == "Focus on revenue growth"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])