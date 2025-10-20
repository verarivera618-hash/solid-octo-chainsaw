"""
Unit tests for CursorPromptGenerator
"""
import pytest
import os
import tempfile
import shutil
from unittest.mock import patch
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.prompt_generator import CursorPromptGenerator

class TestCursorPromptGenerator:
    """Test cases for CursorPromptGenerator"""
    
    def setup_method(self):
        """Setup test fixtures"""
        # Create temporary directory for tests
        self.temp_dir = tempfile.mkdtemp()
        self.generator = CursorPromptGenerator()
        # Override tasks directory for testing
        self.generator.tasks_dir = self.temp_dir
    
    def teardown_method(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_generate_trading_strategy_prompt(self):
        """Test trading strategy prompt generation"""
        market_data = {
            "sec_filings": "Test SEC analysis",
            "news_sentiment": "Test news analysis",
            "earnings": "Test earnings analysis",
            "technical": "Test technical analysis",
            "sector": "Test sector analysis",
            "price_data": "Test price data"
        }
        
        prompt = self.generator.generate_trading_strategy_prompt(
            market_data=market_data,
            strategy_type="momentum",
            tickers=["AAPL", "MSFT"],
            additional_context="Test context"
        )
        
        # Check that prompt contains expected sections
        assert "# Advanced Trading Strategy Implementation Task" in prompt
        assert "momentum" in prompt
        assert "AAPL" in prompt
        assert "MSFT" in prompt
        assert "Test SEC analysis" in prompt
        assert "Test news analysis" in prompt
        assert "Test earnings analysis" in prompt
        assert "Test technical analysis" in prompt
        assert "Test sector analysis" in prompt
        assert "Test price data" in prompt
        assert "Test context" in prompt
    
    def test_save_prompt_to_file(self):
        """Test saving prompt to file"""
        market_data = {
            "sec_filings": "Test SEC analysis",
            "news_sentiment": "Test news analysis",
            "earnings": "Test earnings analysis",
            "technical": "Test technical analysis",
            "sector": "Test sector analysis",
            "price_data": "Test price data"
        }
        
        prompt = self.generator.generate_trading_strategy_prompt(
            market_data=market_data,
            strategy_type="momentum",
            tickers=["AAPL", "MSFT"]
        )
        
        filepath = self.generator.save_prompt_to_file(
            prompt=prompt,
            strategy_name="momentum",
            tickers=["AAPL", "MSFT"]
        )
        
        # Check that file was created
        assert os.path.exists(filepath)
        assert "momentum" in filepath
        assert "AAPL" in filepath
        assert "MSFT" in filepath
        
        # Check file contents
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "# Advanced Trading Strategy Implementation Task" in content
            assert "momentum" in content
    
    def test_generate_quick_strategy_prompt(self):
        """Test quick strategy prompt generation"""
        prompt = self.generator.generate_quick_strategy_prompt(
            ticker="AAPL",
            strategy_type="momentum"
        )
        
        assert "# Quick Trading Strategy Implementation" in prompt
        assert "AAPL" in prompt
        assert "momentum" in prompt
        assert "Alpaca" in prompt
    
    def test_create_cursor_agent_instructions(self):
        """Test Cursor agent instructions generation"""
        instructions = self.generator.create_cursor_agent_instructions()
        
        assert "Cursor Background Agent Setup Instructions" in instructions
        assert "Ctrl+Shift+B" in instructions
        assert "Privacy Mode" in instructions
        assert "usage-based spending" in instructions
        assert "GitHub repository" in instructions
    
    def test_prompt_contains_required_sections(self):
        """Test that generated prompt contains all required sections"""
        market_data = {
            "sec_filings": "Test SEC analysis",
            "news_sentiment": "Test news analysis",
            "earnings": "Test earnings analysis",
            "technical": "Test technical analysis",
            "sector": "Test sector analysis",
            "price_data": "Test price data"
        }
        
        prompt = self.generator.generate_trading_strategy_prompt(
            market_data=market_data,
            strategy_type="momentum",
            tickers=["AAPL"]
        )
        
        # Check for required sections
        required_sections = [
            "Mission",
            "Market Context & Analysis",
            "Implementation Requirements",
            "Core Architecture",
            "Data Integration",
            "Strategy Implementation",
            "Risk Management",
            "Order Execution",
            "Advanced Features",
            "Technical Specifications",
            "Performance Targets",
            "Implementation Steps",
            "Important Constraints",
            "Success Criteria"
        ]
        
        for section in required_sections:
            assert section in prompt, f"Missing required section: {section}"
    
    def test_prompt_contains_file_structure(self):
        """Test that prompt contains required file structure"""
        market_data = {
            "sec_filings": "Test SEC analysis",
            "news_sentiment": "Test news analysis",
            "earnings": "Test earnings analysis",
            "technical": "Test technical analysis",
            "sector": "Test sector analysis",
            "price_data": "Test price data"
        }
        
        prompt = self.generator.generate_trading_strategy_prompt(
            market_data=market_data,
            strategy_type="momentum",
            tickers=["AAPL"]
        )
        
        # Check for required files
        required_files = [
            "config.py",
            "data_handler.py",
            "strategy.py",
            "risk_manager.py",
            "executor.py",
            "portfolio_manager.py",
            "logger.py",
            "main.py"
        ]
        
        for file in required_files:
            assert file in prompt, f"Missing required file: {file}"
    
    def test_prompt_contains_dependencies(self):
        """Test that prompt contains required dependencies"""
        market_data = {
            "sec_filings": "Test SEC analysis",
            "news_sentiment": "Test news analysis",
            "earnings": "Test earnings analysis",
            "technical": "Test technical analysis",
            "sector": "Test sector analysis",
            "price_data": "Test price data"
        }
        
        prompt = self.generator.generate_trading_strategy_prompt(
            market_data=market_data,
            strategy_type="momentum",
            tickers=["AAPL"]
        )
        
        # Check for required dependencies
        required_deps = [
            "alpaca-py",
            "pandas",
            "numpy",
            "scipy",
            "scikit-learn",
            "matplotlib",
            "seaborn",
            "websockets",
            "asyncio",
            "python-dotenv"
        ]
        
        for dep in required_deps:
            assert dep in prompt, f"Missing required dependency: {dep}"