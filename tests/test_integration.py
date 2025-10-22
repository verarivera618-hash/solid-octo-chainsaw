"""
Integration tests for the complete workflow
"""
import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.main import PerplexityAlpacaIntegration

class TestPerplexityAlpacaIntegration:
    """Integration tests for the main workflow"""
    
    def setup_method(self):
        """Setup test fixtures"""
        # Mock the configuration validation
        with patch('src.config.Config.validate_config', return_value=True):
            self.integration = PerplexityAlpacaIntegration()
    
    @patch('src.perplexity_client.PerplexityFinanceClient.get_sec_filings_analysis')
    @patch('src.perplexity_client.PerplexityFinanceClient.get_market_news_sentiment')
    @patch('src.perplexity_client.PerplexityFinanceClient.get_earnings_analysis')
    @patch('src.perplexity_client.PerplexityFinanceClient.get_technical_analysis')
    @patch('src.perplexity_client.PerplexityFinanceClient.get_sector_analysis')
    @patch('src.alpaca_client.AlpacaDataClient.get_historical_bars')
    @patch('src.prompt_generator.CursorPromptGenerator.save_prompt_to_file')
    def test_analyze_and_generate_task_success(self, 
                                             mock_save_prompt,
                                             mock_get_bars,
                                             mock_get_sector,
                                             mock_get_technical,
                                             mock_get_earnings,
                                             mock_get_news,
                                             mock_get_sec):
        """Test successful complete workflow"""
        # Mock all the API responses
        mock_get_sec.return_value = {"choices": [{"message": {"content": "SEC analysis"}}]}
        mock_get_news.return_value = {"choices": [{"message": {"content": "News analysis"}}]}
        mock_get_earnings.return_value = {"choices": [{"message": {"content": "Earnings analysis"}}]}
        mock_get_technical.return_value = {"choices": [{"message": {"content": "Technical analysis"}}]}
        mock_get_sector.return_value = {"choices": [{"message": {"content": "Sector analysis"}}]}
        mock_get_bars.return_value = {"AAPL": Mock()}
        mock_save_prompt.return_value = "test_prompt_file.md"
        
        # Mock the extract_content method
        with patch.object(self.integration.perplexity_client, 'extract_content') as mock_extract:
            mock_extract.side_effect = ["SEC analysis", "News analysis", "Earnings analysis", 
                                      "Technical analysis", "Sector analysis"]
            
            # Mock the _format_price_data method
            with patch.object(self.integration, '_format_price_data', return_value="Price data"):
                result = self.integration.analyze_and_generate_task(
                    tickers=["AAPL"],
                    strategy_name="momentum"
                )
        
        # Verify the result
        assert result == "test_prompt_file.md"
        mock_save_prompt.assert_called_once()
    
    @patch('src.perplexity_client.PerplexityFinanceClient.get_market_news_sentiment')
    @patch('src.perplexity_client.PerplexityFinanceClient.get_technical_analysis')
    @patch('src.alpaca_client.AlpacaDataClient.get_historical_bars')
    @patch('src.prompt_generator.CursorPromptGenerator.save_prompt_to_file')
    def test_quick_analysis_success(self, 
                                   mock_save_prompt,
                                   mock_get_bars,
                                   mock_get_technical,
                                   mock_get_news):
        """Test successful quick analysis workflow"""
        # Mock API responses
        mock_get_news.return_value = {"choices": [{"message": {"content": "News analysis"}}]}
        mock_get_technical.return_value = {"choices": [{"message": {"content": "Technical analysis"}}]}
        mock_get_bars.return_value = {"AAPL": Mock()}
        mock_save_prompt.return_value = "quick_prompt_file.md"
        
        # Mock the extract_content method
        with patch.object(self.integration.perplexity_client, 'extract_content') as mock_extract:
            mock_extract.side_effect = ["News analysis", "Technical analysis"]
            
            # Mock the _format_price_data method
            with patch.object(self.integration, '_format_price_data', return_value="Price data"):
                result = self.integration.quick_analysis("AAPL", "momentum")
        
        # Verify the result
        assert result == "quick_prompt_file.md"
        mock_save_prompt.assert_called_once()
    
    def test_determine_sector(self):
        """Test sector determination logic"""
        # Test tech tickers
        assert self.integration._determine_sector("AAPL") == "technology"
        assert self.integration._determine_sector("MSFT") == "technology"
        assert self.integration._determine_sector("NVDA") == "technology"
        
        # Test non-tech tickers
        assert self.integration._determine_sector("JNJ") == "general"
        assert self.integration._determine_sector("WMT") == "general"
    
    def test_format_price_data(self):
        """Test price data formatting"""
        # Mock historical data
        mock_df = Mock()
        mock_df.empty = False
        mock_df.iloc = [Mock(), Mock()]
        mock_df.iloc[0].__getitem__.return_value = 100.0  # oldest close
        mock_df.iloc[-1].__getitem__.return_value = 110.0  # latest close
        mock_df['high'].max.return_value = 115.0
        mock_df['low'].min.return_value = 95.0
        mock_df['close'].pct_change.return_value.std.return_value = 0.02
        mock_df['volume'].mean.return_value = 1000000
        
        historical_data = {"AAPL": mock_df}
        
        result = self.integration._format_price_data(historical_data)
        
        assert "AAPL Price Analysis" in result
        assert "Current Price" in result
        assert "30-day Change" in result
        assert "Volatility" in result
        assert "Average Volume" in result
    
    def test_format_price_data_empty(self):
        """Test price data formatting with empty data"""
        result = self.integration._format_price_data({})
        assert result == "No historical price data available"
    
    @patch('src.alpaca_client.AlpacaTradingClient.get_account')
    @patch('src.alpaca_client.AlpacaTradingClient.get_positions')
    def test_get_account_status(self, mock_get_positions, mock_get_account):
        """Test account status retrieval"""
        # Mock account and positions data
        mock_get_account.return_value = {"account_id": "test", "equity": 100000}
        mock_get_positions.return_value = [{"symbol": "AAPL", "qty": 100}]
        
        result = self.integration.get_account_status()
        
        assert "account" in result
        assert "positions" in result
        assert "timestamp" in result
        assert result["account"]["account_id"] == "test"
        assert len(result["positions"]) == 1
    
    @patch('src.perplexity_client.PerplexityFinanceClient.get_market_news_sentiment')
    @patch('src.alpaca_client.AlpacaTradingClient.get_account')
    def test_test_connections_success(self, mock_get_account, mock_get_news):
        """Test successful connection testing"""
        # Mock successful responses
        mock_get_news.return_value = {"choices": [{"message": {"content": "Test"}}]}
        mock_get_account.return_value = {"account_id": "test"}
        
        result = self.integration.test_connections()
        
        assert result is True
    
    @patch('src.perplexity_client.PerplexityFinanceClient.get_market_news_sentiment')
    def test_test_connections_perplexity_failure(self, mock_get_news):
        """Test connection testing with Perplexity failure"""
        # Mock Perplexity failure
        mock_get_news.side_effect = Exception("Perplexity API Error")
        
        result = self.integration.test_connections()
        
        assert result is False
    
    @patch('src.perplexity_client.PerplexityFinanceClient.get_market_news_sentiment')
    @patch('src.alpaca_client.AlpacaTradingClient.get_account')
    def test_test_connections_alpaca_failure(self, mock_get_account, mock_get_news):
        """Test connection testing with Alpaca failure"""
        # Mock Perplexity success, Alpaca failure
        mock_get_news.return_value = {"choices": [{"message": {"content": "Test"}}]}
        mock_get_account.side_effect = Exception("Alpaca API Error")
        
        result = self.integration.test_connections()
        
        assert result is False
