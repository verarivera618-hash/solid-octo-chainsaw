"""
Perplexity API Client for Financial Data Retrieval
Supports SEC filings, market news, sentiment analysis, and real-time updates
"""

import requests
import json
from typing import List, Dict, Optional, Literal
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

from src.config import config

logger = logging.getLogger(__name__)


@dataclass
class FinancialInsight:
    """Container for financial insights from Perplexity"""
    content: str
    sources: List[str]
    timestamp: datetime
    query_type: str
    tickers: List[str]
    citations: Optional[List[Dict]] = None


class PerplexityFinanceClient:
    """Client for fetching financial data from Perplexity API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.perplexity.api_key
        self.base_url = config.perplexity.base_url
        self.session = requests.Session()
        self.session.headers.update({
            "accept": "application/json",
            "authorization": f"Bearer {self.api_key}",
            "content-type": "application/json"
        })
    
    def get_sec_filings_analysis(
        self, 
        tickers: List[str], 
        filing_types: Optional[List[str]] = None,
        date_filter: Optional[str] = None,
        reasoning_effort: Literal["low", "medium", "high"] = "high"
    ) -> FinancialInsight:
        """
        Analyze SEC filings for specified tickers
        
        Args:
            tickers: List of stock symbols (e.g., ["AMD", "NVDA"])
            filing_types: Types of filings (10-K, 10-Q, 8-K, S-1, etc.)
            date_filter: Date to filter filings after (YYYY-MM-DD)
            reasoning_effort: Analysis depth (low, medium, high)
        
        Returns:
            FinancialInsight object with analysis results
        """
        filing_types_str = ", ".join(filing_types) if filing_types else "latest"
        date_filter = date_filter or (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        
        query = f"""
        Analyze the {filing_types_str} SEC filings for {', '.join(tickers)}.
        
        Extract and summarize:
        1. Key financial metrics (revenue, earnings, margins, cash flow)
        2. Risk factors and material changes
        3. Management Discussion & Analysis (MD&A) highlights
        4. Significant changes from previous filings
        5. Forward-looking statements and guidance
        6. Any red flags or concerns
        
        Provide specific numbers and dates where applicable.
        """
        
        payload = {
            "model": config.perplexity.deep_research_model,
            "messages": [{"role": "user", "content": query}],
            "stream": False,
            "search_domain": "sec",
            "search_after_date_filter": date_filter,
            "reasoning_effort": reasoning_effort,
            "return_citations": True
        }
        
        try:
            response = self._make_request(payload)
            return self._parse_response(response, "sec_filings", tickers)
        except Exception as e:
            logger.error(f"SEC filings analysis failed: {e}")
            raise
    
    def get_market_news(
        self, 
        tickers: List[str],
        search_context: Literal["low", "medium", "high"] = "high",
        include_sentiment: bool = True
    ) -> FinancialInsight:
        """
        Fetch latest market news and developments
        
        Args:
            tickers: List of stock symbols
            search_context: Amount of context to include
            include_sentiment: Include sentiment analysis
        
        Returns:
            FinancialInsight with news and sentiment
        """
        sentiment_prompt = """
        Include sentiment analysis (Bullish/Bearish/Neutral) with confidence levels.
        """ if include_sentiment else ""
        
        query = f"""
        What are the latest market developments and news for {', '.join(tickers)}?
        
        Include:
        1. Recent price-moving events
        2. Earnings announcements and analyst ratings
        3. Product launches, partnerships, or strategic changes
        4. Industry trends affecting these companies
        5. Competitor movements
        {sentiment_prompt}
        
        Focus on actionable insights from the last 7 days.
        """
        
        payload = {
            "model": config.perplexity.default_model,
            "messages": [{"role": "user", "content": query}],
            "stream": False,
            "web_search_options": {
                "latest_updated": datetime.now().strftime("%Y-%m-%d"),
                "search_context_size": search_context
            },
            "return_citations": True
        }
        
        try:
            response = self._make_request(payload)
            return self._parse_response(response, "market_news", tickers)
        except Exception as e:
            logger.error(f"Market news fetch failed: {e}")
            raise
    
    def get_earnings_analysis(
        self, 
        tickers: List[str],
        include_transcripts: bool = True
    ) -> FinancialInsight:
        """
        Analyze recent earnings reports and calls
        
        Args:
            tickers: List of stock symbols
            include_transcripts: Include earnings call transcript analysis
        
        Returns:
            FinancialInsight with earnings analysis
        """
        transcript_prompt = """
        Analyze earnings call transcripts for management tone, guidance changes, 
        and analyst questions/concerns.
        """ if include_transcripts else ""
        
        query = f"""
        Analyze the most recent earnings reports for {', '.join(tickers)}.
        
        Provide:
        1. Actual vs. expected results (EPS, revenue)
        2. Year-over-year and quarter-over-quarter growth
        3. Key metrics and KPIs mentioned
        4. Forward guidance and outlook
        5. Market reaction (price movement post-earnings)
        {transcript_prompt}
        
        Highlight any surprises or concerning trends.
        """
        
        payload = {
            "model": config.perplexity.deep_research_model,
            "messages": [{"role": "user", "content": query}],
            "stream": False,
            "reasoning_effort": "high",
            "return_citations": True
        }
        
        try:
            response = self._make_request(payload)
            return self._parse_response(response, "earnings_analysis", tickers)
        except Exception as e:
            logger.error(f"Earnings analysis failed: {e}")
            raise
    
    def get_sector_analysis(
        self, 
        sector: str,
        key_tickers: Optional[List[str]] = None
    ) -> FinancialInsight:
        """
        Analyze sector-wide trends and impacts
        
        Args:
            sector: Sector name (e.g., "semiconductors", "technology")
            key_tickers: Optional list of key stocks in the sector
        
        Returns:
            FinancialInsight with sector analysis
        """
        ticker_context = f" Focus on {', '.join(key_tickers)}." if key_tickers else ""
        
        query = f"""
        Provide a comprehensive analysis of the {sector} sector.{ticker_context}
        
        Include:
        1. Current sector trends and themes
        2. Regulatory or macroeconomic impacts
        3. Supply chain or industry-specific challenges
        4. Emerging opportunities or threats
        5. Relative performance vs. broader market
        6. Analyst outlook and institutional sentiment
        
        Provide actionable insights for trading decisions.
        """
        
        payload = {
            "model": config.perplexity.default_model,
            "messages": [{"role": "user", "content": query}],
            "stream": False,
            "web_search_options": {
                "search_context_size": "high"
            },
            "return_citations": True
        }
        
        try:
            response = self._make_request(payload)
            return self._parse_response(
                response, 
                "sector_analysis", 
                key_tickers or [sector]
            )
        except Exception as e:
            logger.error(f"Sector analysis failed: {e}")
            raise
    
    def get_custom_analysis(
        self, 
        query: str,
        model: Optional[str] = None,
        use_sec_domain: bool = False
    ) -> FinancialInsight:
        """
        Execute custom financial query
        
        Args:
            query: Custom query string
            model: Model to use (defaults to sonar-pro)
            use_sec_domain: Search SEC filings domain
        
        Returns:
            FinancialInsight with custom analysis
        """
        payload = {
            "model": model or config.perplexity.default_model,
            "messages": [{"role": "user", "content": query}],
            "stream": False,
            "return_citations": True
        }
        
        if use_sec_domain:
            payload["search_domain"] = "sec"
        
        try:
            response = self._make_request(payload)
            return self._parse_response(response, "custom_analysis", [])
        except Exception as e:
            logger.error(f"Custom analysis failed: {e}")
            raise
    
    def _make_request(self, payload: Dict) -> Dict:
        """Execute API request with retry logic"""
        for attempt in range(config.perplexity.max_retries):
            try:
                response = self.session.post(
                    self.base_url,
                    json=payload,
                    timeout=config.perplexity.timeout
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                if attempt == config.perplexity.max_retries - 1:
                    raise
        
        raise Exception("Max retries exceeded")
    
    def _parse_response(
        self, 
        response: Dict, 
        query_type: str, 
        tickers: List[str]
    ) -> FinancialInsight:
        """Parse Perplexity API response into FinancialInsight"""
        try:
            content = response['choices'][0]['message']['content']
            citations = response.get('citations', [])
            
            # Extract sources from citations
            sources = []
            if citations:
                sources = [
                    citation.get('url', citation.get('title', 'Unknown'))
                    for citation in citations
                ]
            
            return FinancialInsight(
                content=content,
                sources=sources,
                timestamp=datetime.now(),
                query_type=query_type,
                tickers=tickers,
                citations=citations
            )
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse response: {e}")
            raise ValueError(f"Invalid response format: {e}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
