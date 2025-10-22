"""
Perplexity API client for financial data retrieval.
"""
import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
from loguru import logger

from config import get_settings

settings = get_settings()

class QueryType(Enum):
    """Types of financial queries supported."""
    SEC_FILINGS = "sec_filings"
    MARKET_NEWS = "market_news"
    FUNDAMENTALS = "fundamentals"
    EARNINGS = "earnings"
    ANALYST_RATINGS = "analyst_ratings"
    SECTOR_ANALYSIS = "sector_analysis"

@dataclass
class FinancialQuery:
    """Structure for financial data queries."""
    tickers: List[str]
    query_type: QueryType
    time_range: Optional[str] = None
    specific_query: Optional[str] = None

class PerplexityFinanceClient:
    """Client for fetching financial data from Perplexity API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.perplexity_api_key
        self.base_url = settings.perplexity_base_url
        self.rate_limit = settings.perplexity_rate_limit
        self.last_request_time = 0
        
        if not self.api_key:
            raise ValueError("Perplexity API key is required")
    
    def _rate_limit_check(self):
        """Ensure we don't exceed rate limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = 60 / self.rate_limit  # seconds between requests
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, payload: Dict) -> Dict:
        """Make authenticated request to Perplexity API."""
        self._rate_limit_check()
        
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.api_key}",
            "content-type": "application/json"
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Perplexity API request failed: {e}")
            raise
    
    def get_sec_filings_analysis(self, tickers: List[str], filing_types: Optional[List[str]] = None) -> str:
        """
        Analyze SEC filings for given tickers.
        
        Args:
            tickers: List of stock symbols
            filing_types: Optional list of filing types (10-K, 10-Q, 8-K, etc.)
        
        Returns:
            Comprehensive analysis of SEC filings
        """
        filing_filter = ""
        if filing_types:
            filing_filter = f" Focus on {', '.join(filing_types)} filings."
        
        payload = {
            "model": "sonar-deep-research",
            "messages": [{
                "role": "user",
                "content": f"""Analyze the latest SEC filings for {', '.join(tickers)}.{filing_filter}
                
                Extract and summarize:
                1. Key financial metrics and trends
                2. Risk factors and management concerns
                3. Business outlook and guidance
                4. Capital allocation strategies
                5. Competitive positioning
                6. Any material changes or events
                
                Provide quantitative data where available and highlight any red flags or positive catalysts."""
            }],
            "search_domain": "sec",
            "reasoning_effort": "high",
            "stream": False
        }
        
        response = self._make_request(payload)
        return response['choices'][0]['message']['content']
    
    def get_market_news_sentiment(self, tickers: List[str], days_back: int = 7) -> str:
        """
        Get recent market news and sentiment analysis.
        
        Args:
            tickers: List of stock symbols
            days_back: Number of days to look back for news
        
        Returns:
            Market news summary with sentiment analysis
        """
        start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        payload = {
            "model": "sonar-pro",
            "messages": [{
                "role": "user",
                "content": f"""Analyze recent market developments for {', '.join(tickers)} over the last {days_back} days.
                
                Provide:
                1. Key news events and announcements
                2. Market sentiment analysis (Bullish/Bearish/Neutral with confidence scores)
                3. Price-moving catalysts and their potential impact
                4. Analyst upgrades/downgrades and price target changes
                5. Institutional activity and insider trading
                6. Sector-wide trends affecting these stocks
                
                Include specific dates and quantify impact where possible."""
            }],
            "web_search_options": {
                "latest_updated": start_date,
                "search_context_size": "high"
            },
            "stream": False
        }
        
        response = self._make_request(payload)
        return response['choices'][0]['message']['content']
    
    def get_earnings_analysis(self, tickers: List[str]) -> str:
        """
        Analyze recent earnings reports and upcoming earnings.
        
        Args:
            tickers: List of stock symbols
        
        Returns:
            Earnings analysis and expectations
        """
        payload = {
            "model": "sonar-pro",
            "messages": [{
                "role": "user",
                "content": f"""Provide comprehensive earnings analysis for {', '.join(tickers)}.
                
                Include:
                1. Latest earnings results vs expectations
                2. Key metrics: Revenue, EPS, margins, guidance
                3. Management commentary and outlook
                4. Upcoming earnings dates and analyst expectations
                5. Historical earnings trends and seasonality
                6. Earnings surprise history and market reactions
                
                Highlight any earnings-related catalysts or concerns."""
            }],
            "web_search_options": {
                "search_context_size": "high"
            },
            "stream": False
        }
        
        response = self._make_request(payload)
        return response['choices'][0]['message']['content']
    
    def get_analyst_ratings(self, tickers: List[str]) -> str:
        """
        Get current analyst ratings and price targets.
        
        Args:
            tickers: List of stock symbols
        
        Returns:
            Analyst ratings summary
        """
        payload = {
            "model": "sonar-pro",
            "messages": [{
                "role": "user",
                "content": f"""Summarize current analyst ratings and price targets for {', '.join(tickers)}.
                
                Provide:
                1. Consensus ratings (Buy/Hold/Sell) and distribution
                2. Average price targets and ranges
                3. Recent rating changes and their rationale
                4. Top-rated analysts' opinions
                5. Institutional price target revisions
                6. Comparison to current market prices
                
                Include specific analyst firms and their track records where available."""
            }],
            "web_search_options": {
                "search_context_size": "medium"
            },
            "stream": False
        }
        
        response = self._make_request(payload)
        return response['choices'][0]['message']['content']
    
    def get_sector_analysis(self, sector: str, tickers: Optional[List[str]] = None) -> str:
        """
        Analyze sector trends and positioning.
        
        Args:
            sector: Sector name (e.g., "Technology", "Healthcare")
            tickers: Optional list of specific tickers within the sector
        
        Returns:
            Sector analysis and trends
        """
        ticker_context = ""
        if tickers:
            ticker_context = f" with specific focus on {', '.join(tickers)}"
        
        payload = {
            "model": "sonar-pro",
            "messages": [{
                "role": "user",
                "content": f"""Analyze the {sector} sector{ticker_context}.
                
                Cover:
                1. Current sector performance and trends
                2. Key drivers and headwinds
                3. Regulatory environment and policy impacts
                4. Competitive landscape and market leaders
                5. Valuation metrics vs historical averages
                6. Growth prospects and investment themes
                7. Sector rotation patterns and institutional flows
                
                Provide actionable insights for trading and investment decisions."""
            }],
            "web_search_options": {
                "search_context_size": "high"
            },
            "stream": False
        }
        
        response = self._make_request(payload)
        return response['choices'][0]['message']['content']
    
    def get_comprehensive_analysis(self, query: FinancialQuery) -> Dict[str, str]:
        """
        Get comprehensive financial analysis based on query type.
        
        Args:
            query: FinancialQuery object with analysis parameters
        
        Returns:
            Dictionary with analysis results
        """
        results = {}
        
        try:
            if query.query_type == QueryType.SEC_FILINGS:
                results['sec_analysis'] = self.get_sec_filings_analysis(query.tickers)
            
            elif query.query_type == QueryType.MARKET_NEWS:
                days_back = int(query.time_range) if query.time_range else 7
                results['news_sentiment'] = self.get_market_news_sentiment(query.tickers, days_back)
            
            elif query.query_type == QueryType.EARNINGS:
                results['earnings_analysis'] = self.get_earnings_analysis(query.tickers)
            
            elif query.query_type == QueryType.ANALYST_RATINGS:
                results['analyst_ratings'] = self.get_analyst_ratings(query.tickers)
            
            elif query.query_type == QueryType.FUNDAMENTALS:
                # Comprehensive fundamental analysis
                results['sec_analysis'] = self.get_sec_filings_analysis(query.tickers)
                results['earnings_analysis'] = self.get_earnings_analysis(query.tickers)
                results['analyst_ratings'] = self.get_analyst_ratings(query.tickers)
            
            elif query.query_type == QueryType.SECTOR_ANALYSIS:
                sector = query.specific_query or "Technology"
                results['sector_analysis'] = self.get_sector_analysis(sector, query.tickers)
            
            # Always include recent news for context
            if 'news_sentiment' not in results:
                results['news_sentiment'] = self.get_market_news_sentiment(query.tickers, 3)
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            results['error'] = str(e)
        
        return results
    
    def get_structured_data(self, tickers: List[str], query_type: str) -> Dict:
        """
        Get structured financial data in JSON format.
        
        Args:
            tickers: List of stock symbols
            query_type: Type of data to retrieve
        
        Returns:
            Structured data dictionary
        """
        payload = {
            "model": "sonar-pro",
            "messages": [{
                "role": "user",
                "content": f"""Extract structured financial data for {', '.join(tickers)} related to {query_type}.
                
                Return data in JSON format with the following structure:
                {{
                    "ticker": {{
                        "current_price": float,
                        "market_cap": float,
                        "pe_ratio": float,
                        "revenue_growth": float,
                        "sentiment_score": float (-1 to 1),
                        "analyst_rating": string,
                        "price_target": float,
                        "key_metrics": {{}},
                        "recent_events": []
                    }}
                }}"""
            }],
            "response_format": {"type": "json_object"},
            "stream": False
        }
        
        try:
            response = self._make_request(payload)
            content = response['choices'][0]['message']['content']
            return json.loads(content)
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse structured data: {e}")
            return {}

# Example usage and testing
if __name__ == "__main__":
    client = PerplexityFinanceClient()
    
    # Test SEC filings analysis
    tickers = ["AAPL", "MSFT", "GOOGL"]
    query = FinancialQuery(
        tickers=tickers,
        query_type=QueryType.FUNDAMENTALS
    )
    
    results = client.get_comprehensive_analysis(query)
    
    for analysis_type, content in results.items():
        print(f"\n=== {analysis_type.upper()} ===")
        print(content[:500] + "..." if len(content) > 500 else content)