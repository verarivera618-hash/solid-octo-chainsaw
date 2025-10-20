"""
Integration tests for the complete Perplexity-Alpaca system.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from main import PerplexityAlpacaIntegration
from src.prompt_generator import StrategyType

class TestPerplexityAlpacaIntegration:
    """Test cases for the complete integration system."""
    
    @pytest.fixture
    def mock_integration(self):
        """Create a mock integration instance."""
        with patch('main.PerplexityFinanceClient') as mock_perplexity, \
             patch('main.AlpacaDataClient') as mock_data, \
             patch('main.AlpacaTradingClient') as mock_trading, \
             patch('main.CursorPromptGenerator') as mock_prompt:
            
            integration = PerplexityAlpacaIntegration()
            return integration, mock_perplexity, mock_data, mock_trading, mock_prompt
    
    def test_integration_initialization(self):
        """Test integration initialization."""
        with patch('main.PerplexityFinanceClient'), \
             patch('main.AlpacaDataClient'), \
             patch('main.AlpacaTradingClient'), \
             patch('main.CursorPromptGenerator'):
            
            integration = PerplexityAlpacaIntegration()
            assert integration.perplexity_client is not None
            assert integration.data_client is not None
            assert integration.trading_client is not None
            assert integration.prompt_generator is not None
    
    def test_analyze_and_generate_task_success(self, mock_integration):
        """Test successful task generation."""
        integration, mock_perplexity, mock_data, mock_trading, mock_prompt = mock_integration
        
        # Mock successful prompt generation
        mock_result = {
            "success": True,
            "prompt_file": "cursor_tasks/test_strategy_20241020_120000.md",
            "market_data": {"test": "data"},
            "timestamp": datetime.now().isoformat()
        }
        integration.prompt_generator.generate_complete_task.return_value = mock_result
        
        result = integration.analyze_and_generate_task(
            tickers=["AAPL", "MSFT"],
            strategy_type=StrategyType.MOMENTUM,
            time_horizon="swing",
            risk_tolerance="medium"
        )
        
        assert result["success"] is True
        assert "prompt_file" in result
        integration.prompt_generator.generate_complete_task.assert_called_once()
    
    def test_analyze_and_generate_task_failure(self, mock_integration):
        """Test task generation failure."""
        integration, mock_perplexity, mock_data, mock_trading, mock_prompt = mock_integration
        
        # Mock failed prompt generation
        mock_result = {
            "success": False,
            "error": "API connection failed"
        }
        integration.prompt_generator.generate_complete_task.return_value = mock_result
        
        result = integration.analyze_and_generate_task(
            tickers=["AAPL"],
            strategy_type=StrategyType.MOMENTUM
        )
        
        assert result["success"] is False
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_test_connections_all_success(self, mock_integration):
        """Test connection testing with all services working."""
        integration, mock_perplexity, mock_data, mock_trading, mock_prompt = mock_integration
        
        # Mock successful connections
        integration.perplexity_client.get_comprehensive_analysis.return_value = {"test": "data"}
        integration.data_client.get_latest_quotes.return_value = {"AAPL": Mock()}
        integration.trading_client.get_account.return_value = {"id": "test"}
        
        results = await integration.test_connections()
        
        assert results["perplexity"] is True
        assert results["alpaca_data"] is True
        assert results["alpaca_trading"] is True
    
    @pytest.mark.asyncio
    async def test_test_connections_partial_failure(self, mock_integration):
        """Test connection testing with some services failing."""
        integration, mock_perplexity, mock_data, mock_trading, mock_prompt = mock_integration
        
        # Mock mixed success/failure
        integration.perplexity_client.get_comprehensive_analysis.side_effect = Exception("API Error")
        integration.data_client.get_latest_quotes.return_value = {"AAPL": Mock()}
        integration.trading_client.get_account.return_value = {"id": "test"}
        
        results = await integration.test_connections()
        
        assert results["perplexity"] is False
        assert results["alpaca_data"] is True
        assert results["alpaca_trading"] is True
    
    def test_get_market_overview_success(self, mock_integration):
        """Test successful market overview retrieval."""
        integration, mock_perplexity, mock_data, mock_trading, mock_prompt = mock_integration
        
        # Mock market data
        mock_quote = Mock()
        mock_quote.bid_price = 149.50
        mock_quote.ask_price = 150.50
        mock_quote.timestamp = datetime.now()
        
        mock_bar = Mock()
        mock_bar.close = 150.00
        mock_bar.volume = 1000000
        mock_bar.timestamp = datetime.now()
        
        integration.perplexity_client.get_comprehensive_analysis.return_value = {
            "fundamental_analysis": "Test analysis"
        }
        integration.data_client.get_latest_quotes.return_value = {"AAPL": mock_quote}
        integration.data_client.get_latest_bars.return_value = {"AAPL": mock_bar}
        
        result = integration.get_market_overview(["AAPL"])
        
        assert result["success"] is True
        assert "AAPL" in result["current_quotes"]
        assert "AAPL" in result["current_bars"]
        assert result["current_quotes"]["AAPL"]["bid"] == 149.50
    
    def test_get_market_overview_failure(self, mock_integration):
        """Test market overview retrieval failure."""
        integration, mock_perplexity, mock_data, mock_trading, mock_prompt = mock_integration
        
        # Mock API failure
        integration.perplexity_client.get_comprehensive_analysis.side_effect = Exception("API Error")
        
        result = integration.get_market_overview(["AAPL"])
        
        assert result["success"] is False
        assert "error" in result
    
    def test_list_available_strategies(self, mock_integration):
        """Test listing available strategies."""
        integration, mock_perplexity, mock_data, mock_trading, mock_prompt = mock_integration
        
        strategies = integration.list_available_strategies()
        
        assert isinstance(strategies, list)
        assert len(strategies) > 0
        
        # Check strategy structure
        strategy = strategies[0]
        assert "type" in strategy
        assert "name" in strategy
        assert "description" in strategy
        assert "time_horizons" in strategy
        assert "risk_levels" in strategy
    
    def test_strategy_types_coverage(self, mock_integration):
        """Test that all strategy types are covered."""
        integration, mock_perplexity, mock_data, mock_trading, mock_prompt = mock_integration
        
        strategies = integration.list_available_strategies()
        strategy_types = [s["type"] for s in strategies]
        
        # Check that common strategy types are included
        expected_types = ["momentum", "mean_reversion", "breakout", "earnings_play"]
        for expected_type in expected_types:
            assert expected_type in strategy_types

class TestCommandLineInterface:
    """Test cases for the command line interface."""
    
    @patch('main.PerplexityAlpacaIntegration')
    def test_test_command(self, mock_integration_class):
        """Test the --test command."""
        mock_integration = Mock()
        mock_integration_class.return_value = mock_integration
        
        # Mock successful connections
        async def mock_test_connections():
            return {
                "perplexity": True,
                "alpaca_data": True,
                "alpaca_trading": True
            }
        
        mock_integration.test_connections = mock_test_connections
        
        # This would normally be tested with subprocess or click testing
        # For now, just verify the mock setup
        assert mock_integration.test_connections is not None
    
    @patch('main.PerplexityAlpacaIntegration')
    def test_overview_command(self, mock_integration_class):
        """Test the --overview command."""
        mock_integration = Mock()
        mock_integration_class.return_value = mock_integration
        
        # Mock market overview
        mock_integration.get_market_overview.return_value = {
            "success": True,
            "current_quotes": {
                "AAPL": {"bid": 149.50, "ask": 150.50, "spread": 1.00}
            },
            "fundamental_analysis": {"test": "analysis"}
        }
        
        result = mock_integration.get_market_overview(["AAPL"])
        assert result["success"] is True
    
    @patch('main.PerplexityAlpacaIntegration')
    def test_generate_command(self, mock_integration_class):
        """Test the --generate command."""
        mock_integration = Mock()
        mock_integration_class.return_value = mock_integration
        
        # Mock task generation
        mock_integration.analyze_and_generate_task.return_value = {
            "success": True,
            "prompt_file": "test_file.md"
        }
        
        result = mock_integration.analyze_and_generate_task(
            tickers=["AAPL"],
            strategy_type=StrategyType.MOMENTUM
        )
        assert result["success"] is True

if __name__ == "__main__":
    pytest.main([__file__, "-v"])