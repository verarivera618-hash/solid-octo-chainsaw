"""
Perplexity API client for financial data retrieval
"""

import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from loguru import logger
import asyncio
import aiohttp
from enum import Enum


class SearchDomain(Enum):
    """Perplexity search domains"""
    GENERAL = "general"
    SEC = "sec"  # SEC filings
    FINANCE = "finance"
    NEWS = "news"


class QueryType(Enum):
    """Types of financial queries"""
    SEC_FILINGS = "sec_filings"
    MARKET_NEWS = "market_news"
    FUNDAMENTALS = "fundamentals"
    EARNINGS = "earnings"
    SENTIMENT = "sentiment"
    TECHNICAL = "technical"


class PerplexityFinanceClient:
    """Client for fetching financial data from Perplexity API"""
    
    def __init__(self, api_key: str, base_url: str = None, timeout: int = 30):
        self.api_key = api_key
        self.base_url = base_url or "https://api.perplexity.ai/chat/completions"
        self.timeout = timeout
        self.headers = {
            "accept": "application/json",
            "authorization": f"Bearer {api_key}",
            "content-type": "application/json"
        }
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _build_prompt(self, tickers: List[str], query_type: QueryType) -> str:
        """Build specialized prompts for different query types"""
        
        tickers_str = ", ".join(tickers)
        
        prompts = {
            QueryType.SEC_FILINGS: f"""
                Analyze the latest SEC filings (10-K, 10-Q, 8-K) for {tickers_str}.
                Extract and summarize:
                1. Key financial metrics (revenue, earnings, margins, cash flow)
                2. Major risk factors and challenges
                3. Management discussion and strategic initiatives
                4. Any material changes or events
                5. Forward guidance and outlook
                Provide specific numbers and dates where available.
            """,
            
            QueryType.MARKET_NEWS: f"""
                What are the latest market developments for {tickers_str}?
                Include:
                1. Recent price movements and trading volume
                2. Major news events and catalysts
                3. Analyst upgrades/downgrades
                4. Market sentiment (Bullish/Bearish/Neutral)
                5. Upcoming events (earnings, product launches, etc.)
                Focus on events from the last 7 days.
            """,
            
            QueryType.FUNDAMENTALS: f"""
                Provide comprehensive fundamental analysis for {tickers_str}:
                1. Valuation metrics (P/E, P/B, PEG, EV/EBITDA)
                2. Profitability metrics (ROE, ROA, profit margins)
                3. Growth metrics (revenue growth, earnings growth)
                4. Financial health (debt/equity, current ratio, cash position)
                5. Competitive position and market share
                Compare with industry averages where relevant.
            """,
            
            QueryType.EARNINGS: f"""
                Analyze the latest earnings reports for {tickers_str}:
                1. EPS actual vs. consensus estimates
                2. Revenue actual vs. estimates
                3. Key highlights from earnings call
                4. Guidance updates
                5. Market reaction to earnings
                Include quarter-over-quarter and year-over-year comparisons.
            """,
            
            QueryType.SENTIMENT: f"""
                Analyze current market sentiment for {tickers_str}:
                1. Social media sentiment (Twitter, Reddit, StockTwits)
                2. News sentiment analysis
                3. Options flow and unusual activity
                4. Institutional buying/selling
                5. Retail investor interest
                Provide an overall sentiment score and key drivers.
            """,
            
            QueryType.TECHNICAL: f"""
                Provide technical analysis for {tickers_str}:
                1. Current trend (uptrend, downtrend, sideways)
                2. Key support and resistance levels
                3. Moving average analysis (20, 50, 200 DMA)
                4. RSI and momentum indicators
                5. Volume analysis and patterns
                Include specific price levels and technical signals.
            """
        }
        
        return prompts.get(query_type, prompts[QueryType.MARKET_NEWS])
    
    async def query_async(
        self,
        tickers: List[str],
        query_type: QueryType,
        search_domain: SearchDomain = SearchDomain.GENERAL,
        reasoning_effort: str = "medium",
        structured_output: bool = False
    ) -> Dict[str, Any]:
        """Async query to Perplexity API"""
        
        prompt = self._build_prompt(tickers, query_type)
        
        payload = {
            "model": "sonar-deep-research" if reasoning_effort == "high" else "sonar-pro",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "reasoning_effort": reasoning_effort
        }
        
        # Add search domain for SEC filings
        if query_type == QueryType.SEC_FILINGS:
            payload["search_domain"] = "sec"
            payload["search_after_date_filter"] = (
                datetime.now() - timedelta(days=180)
            ).strftime("%Y-%m-%d")
        
        # Add web search options for news
        elif query_type == QueryType.MARKET_NEWS:
            payload["web_search_options"] = {
                "latest_updated": datetime.now().strftime("%Y-%m-%d"),
                "search_context_size": "high"
            }
        
        # Request structured output if needed
        if structured_output:
            payload["response_format"] = {"type": "json_object"}
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                response.raise_for_status()
                data = await response.json()
                
                result = {
                    "tickers": tickers,
                    "query_type": query_type.value,
                    "timestamp": datetime.now().isoformat(),
                    "content": data["choices"][0]["message"]["content"],
                    "model": data.get("model"),
                    "usage": data.get("usage")
                }
                
                logger.info(f"Successfully queried {query_type.value} for {tickers}")
                return result
                
        except aiohttp.ClientError as e:
            logger.error(f"API request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
    
    def query(
        self,
        tickers: List[str],
        query_type: QueryType,
        **kwargs
    ) -> Dict[str, Any]:
        """Synchronous wrapper for async query"""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self.query_async(tickers, query_type, **kwargs)
        )
    
    async def get_comprehensive_analysis(
        self,
        tickers: List[str],
        include_types: Optional[List[QueryType]] = None
    ) -> Dict[str, Any]:
        """Get comprehensive analysis combining multiple query types"""
        
        if not include_types:
            include_types = [
                QueryType.SEC_FILINGS,
                QueryType.MARKET_NEWS,
                QueryType.FUNDAMENTALS,
                QueryType.SENTIMENT
            ]
        
        # Run all queries in parallel
        tasks = []
        for query_type in include_types:
            tasks.append(self.query_async(tickers, query_type))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        analysis = {
            "tickers": tickers,
            "timestamp": datetime.now().isoformat(),
            "analysis": {}
        }
        
        for idx, query_type in enumerate(include_types):
            if isinstance(results[idx], Exception):
                logger.error(f"Failed to get {query_type.value}: {results[idx]}")
                analysis["analysis"][query_type.value] = None
            else:
                analysis["analysis"][query_type.value] = results[idx]
        
        return analysis
    
    async def monitor_news_stream(
        self,
        tickers: List[str],
        interval_minutes: int = 15,
        callback=None
    ):
        """Monitor news stream for specified tickers"""
        
        logger.info(f"Starting news monitor for {tickers} (interval: {interval_minutes}m)")
        
        while True:
            try:
                news_data = await self.query_async(
                    tickers,
                    QueryType.MARKET_NEWS,
                    reasoning_effort="low"
                )
                
                if callback:
                    await callback(news_data)
                else:
                    logger.info(f"News update: {news_data['content'][:200]}...")
                
                await asyncio.sleep(interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"Error in news monitor: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error


class FinancialDataAggregator:
    """Aggregates data from multiple sources including Perplexity"""
    
    def __init__(self, perplexity_client: PerplexityFinanceClient):
        self.perplexity = perplexity_client
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def get_trading_signals(
        self,
        tickers: List[str]
    ) -> Dict[str, Any]:
        """Generate trading signals based on comprehensive analysis"""
        
        # Get comprehensive analysis
        analysis = await self.perplexity.get_comprehensive_analysis(tickers)
        
        signals = {
            "timestamp": datetime.now().isoformat(),
            "tickers": {}
        }
        
        for ticker in tickers:
            # Parse sentiment and fundamentals to generate signal
            signal = self._analyze_for_signal(analysis, ticker)
            signals["tickers"][ticker] = signal
        
        return signals
    
    def _analyze_for_signal(
        self,
        analysis: Dict[str, Any],
        ticker: str
    ) -> Dict[str, Any]:
        """Analyze data to generate trading signal"""
        
        # This is a simplified signal generator
        # In practice, you'd implement sophisticated analysis
        
        signal = {
            "ticker": ticker,
            "action": "HOLD",  # BUY, SELL, HOLD
            "confidence": 0.5,
            "reasons": [],
            "risk_level": "MEDIUM"
        }
        
        # Extract sentiment if available
        if analysis["analysis"].get(QueryType.SENTIMENT.value):
            sentiment_content = analysis["analysis"][QueryType.SENTIMENT.value]["content"]
            if "Bullish" in sentiment_content:
                signal["action"] = "BUY"
                signal["confidence"] = 0.7
                signal["reasons"].append("Positive market sentiment")
            elif "Bearish" in sentiment_content:
                signal["action"] = "SELL"
                signal["confidence"] = 0.7
                signal["reasons"].append("Negative market sentiment")
        
        return signal