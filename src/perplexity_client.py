"""
Perplexity API client for financial data retrieval

Local-first: when PERPLEXITY_API_KEY is missing, return deterministic stubbed content
to enable fully local workflows without external subscriptions.
"""
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from .config import Config

class PerplexityFinanceClient:
    """Client for accessing Perplexity's financial data capabilities"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.PERPLEXITY_API_KEY
        self.base_url = Config.PERPLEXITY_BASE_URL
        self.headers = Config.get_perplexity_headers()
    
    def get_sec_filings_analysis(self, tickers: List[str], 
                                search_after_date: str = None) -> Dict[str, Any]:
        """
        Analyze SEC filings for given tickers
        
        Args:
            tickers: List of stock symbols to analyze
            search_after_date: Date filter in YYYY-MM-DD format
            
        Returns:
            Dictionary containing SEC filings analysis
        """
        if not search_after_date:
            search_after_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        
        payload = {
            "model": "sonar-deep-research",
            "messages": [{
                "role": "user",
                "content": f"""
                Analyze the latest SEC filings for {', '.join(tickers)}. 
                Extract and summarize:
                1. Key financial metrics and ratios
                2. Risk factors and management discussion
                3. Revenue trends and growth patterns
                4. Debt levels and cash position
                5. Management guidance and outlook
                
                Focus on the most recent 10-Q and 10-K filings.
                """
            }],
            "stream": False,
            "search_domain": "sec",
            "search_after_date_filter": search_after_date,
            "reasoning_effort": "high"
        }
        
        if not self.api_key:
            # Local stubbed content
            content = (
                f"Stubbed SEC analysis for {', '.join(tickers)} since {search_after_date}. "
                "This is local-only content for development."
            )
            return {"choices": [{"message": {"content": content}}]}

        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching SEC filings: {e}")
            return {"error": str(e)}
    
    def get_market_news_sentiment(self, tickers: List[str], 
                                 hours_back: int = 24) -> Dict[str, Any]:
        """
        Get market news and sentiment analysis for tickers
        
        Args:
            tickers: List of stock symbols to analyze
            hours_back: Hours to look back for news
            
        Returns:
            Dictionary containing news and sentiment analysis
        """
        payload = {
            "model": "sonar-pro",
            "messages": [{
                "role": "user",
                "content": f"""
                What are the latest market developments for {', '.join(tickers)}? 
                Provide:
                1. Recent news and events affecting these stocks
                2. Market sentiment analysis (Bullish/Bearish/Neutral)
                3. Price-moving catalysts and events
                4. Analyst upgrades/downgrades
                5. Sector-specific trends and outlook
                
                Focus on the last {hours_back} hours of news and developments.
                """
            }],
            "stream": False,
            "web_search_options": {
                "latest_updated": datetime.now().strftime("%Y-%m-%d"),
                "search_context_size": "high"
            }
        }
        
        if not self.api_key:
            content = (
                f"Stubbed market news and sentiment for {', '.join(tickers)} over last {hours_back} hours."
            )
            return {"choices": [{"message": {"content": content}}]}

        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching market news: {e}")
            return {"error": str(e)}
    
    def get_earnings_analysis(self, tickers: List[str]) -> Dict[str, Any]:
        """
        Get earnings analysis and expectations for tickers
        
        Args:
            tickers: List of stock symbols to analyze
            
        Returns:
            Dictionary containing earnings analysis
        """
        payload = {
            "model": "sonar-pro",
            "messages": [{
                "role": "user",
                "content": f"""
                Provide comprehensive earnings analysis for {', '.join(tickers)}:
                1. Recent earnings results and beats/misses
                2. Upcoming earnings dates and expectations
                3. Revenue and EPS growth trends
                4. Guidance updates and management commentary
                5. Analyst estimates and revisions
                6. Peer comparison and relative performance
                """
            }],
            "stream": False,
            "web_search_options": {
                "latest_updated": datetime.now().strftime("%Y-%m-%d"),
                "search_context_size": "high"
            }
        }
        
        if not self.api_key:
            content = f"Stubbed earnings analysis for {', '.join(tickers)}."
            return {"choices": [{"message": {"content": content}}]}

        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching earnings analysis: {e}")
            return {"error": str(e)}
    
    def get_technical_analysis(self, tickers: List[str], 
                              timeframe: str = "1D") -> Dict[str, Any]:
        """
        Get technical analysis for tickers
        
        Args:
            tickers: List of stock symbols to analyze
            timeframe: Timeframe for analysis (1D, 1W, 1M)
            
        Returns:
            Dictionary containing technical analysis
        """
        payload = {
            "model": "sonar-pro",
            "messages": [{
                "role": "user",
                "content": f"""
                Provide technical analysis for {', '.join(tickers)}:
                1. Current price levels and key support/resistance
                2. Moving average trends and crossovers
                3. Volume analysis and momentum indicators
                4. Chart patterns and breakout levels
                5. RSI, MACD, and other technical indicators
                6. Short-term and medium-term price targets
                
                Focus on {timeframe} timeframe analysis.
                """
            }],
            "stream": False,
            "web_search_options": {
                "latest_updated": datetime.now().strftime("%Y-%m-%d"),
                "search_context_size": "medium"
            }
        }
        
        if not self.api_key:
            content = f"Stubbed {timeframe} technical analysis for {', '.join(tickers)}."
            return {"choices": [{"message": {"content": content}}]}

        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching technical analysis: {e}")
            return {"error": str(e)}
    
    def get_sector_analysis(self, sector: str) -> Dict[str, Any]:
        """
        Get sector-wide analysis and trends
        
        Args:
            sector: Sector name (e.g., "semiconductors", "technology", "healthcare")
            
        Returns:
            Dictionary containing sector analysis
        """
        payload = {
            "model": "sonar-pro",
            "messages": [{
                "role": "user",
                "content": f"""
                Provide comprehensive analysis of the {sector} sector:
                1. Overall sector performance and trends
                2. Key drivers and catalysts
                3. Regulatory environment and policy impacts
                4. Supply chain dynamics and challenges
                5. Competitive landscape and market share shifts
                6. Growth prospects and investment themes
                7. Top performing and underperforming stocks
                """
            }],
            "stream": False,
            "web_search_options": {
                "latest_updated": datetime.now().strftime("%Y-%m-%d"),
                "search_context_size": "high"
            }
        }
        
        if not self.api_key:
            content = f"Stubbed sector analysis for {sector}."
            return {"choices": [{"message": {"content": content}}]}

        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching sector analysis: {e}")
            return {"error": str(e)}
    
    def extract_content(self, response: Dict[str, Any]) -> str:
        """Extract content from Perplexity API response"""
        try:
            if "choices" in response and len(response["choices"]) > 0:
                return response["choices"][0]["message"]["content"]
            elif "error" in response:
                return f"Error: {response['error']}"
            else:
                return "No content available"
        except (KeyError, IndexError) as e:
            return f"Error extracting content: {e}"
