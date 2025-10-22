"""
Unit tests for PerplexityFinanceClient
"""
import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.perplexity_client import PerplexityFinanceClient

class TestPerplexityFinanceClient:
    """Test cases for PerplexityFinanceClient"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.client = PerplexityFinanceClient(api_key="test_key")
    
    @patch('requests.post')
    def test_get_sec_filings_analysis_success(self, mock_post):
        """Test successful SEC filings analysis"""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test SEC analysis"}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.client.get_sec_filings_analysis(["AAPL", "MSFT"])
        
        assert "choices" in result
        assert result["choices"][0]["message"]["content"] == "Test SEC analysis"
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_get_sec_filings_analysis_error(self, mock_post):
        """Test SEC filings analysis with API error"""
        mock_post.side_effect = Exception("API Error")
        
        result = self.client.get_sec_filings_analysis(["AAPL"])
        
        assert "error" in result
        assert result["error"] == "API Error"
    
    @patch('requests.post')
    def test_get_market_news_sentiment_success(self, mock_post):
        """Test successful market news sentiment analysis"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test news analysis"}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.client.get_market_news_sentiment(["AAPL"])
        
        assert "choices" in result
        assert result["choices"][0]["message"]["content"] == "Test news analysis"
    
    @patch('requests.post')
    def test_get_earnings_analysis_success(self, mock_post):
        """Test successful earnings analysis"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test earnings analysis"}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.client.get_earnings_analysis(["AAPL"])
        
        assert "choices" in result
        assert result["choices"][0]["message"]["content"] == "Test earnings analysis"
    
    @patch('requests.post')
    def test_get_technical_analysis_success(self, mock_post):
        """Test successful technical analysis"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test technical analysis"}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.client.get_technical_analysis(["AAPL"])
        
        assert "choices" in result
        assert result["choices"][0]["message"]["content"] == "Test technical analysis"
    
    @patch('requests.post')
    def test_get_sector_analysis_success(self, mock_post):
        """Test successful sector analysis"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test sector analysis"}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.client.get_sector_analysis("technology")
        
        assert "choices" in result
        assert result["choices"][0]["message"]["content"] == "Test sector analysis"
    
    def test_extract_content_success(self):
        """Test successful content extraction"""
        response = {
            "choices": [{"message": {"content": "Test content"}}]
        }
        
        result = self.client.extract_content(response)
        assert result == "Test content"
    
    def test_extract_content_error(self):
        """Test content extraction with error"""
        response = {"error": "API Error"}
        
        result = self.client.extract_content(response)
        assert result == "Error: API Error"
    
    def test_extract_content_no_choices(self):
        """Test content extraction with no choices"""
        response = {}
        
        result = self.client.extract_content(response)
        assert result == "No content available"