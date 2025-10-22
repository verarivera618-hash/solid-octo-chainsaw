"""
Local Data Provider
Replaces external API calls with local data generation and analysis
"""

import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class LocalDataProvider:
    """
    Local data provider that generates synthetic market data and analysis
    Replaces Perplexity API and Alpaca API calls
    """
    
    def __init__(self):
        self.sector_mapping = {
            'AAPL': 'technology',
            'MSFT': 'technology', 
            'GOOGL': 'technology',
            'AMZN': 'technology',
            'NVDA': 'technology',
            'AMD': 'technology',
            'INTC': 'technology',
            'TSLA': 'automotive',
            'JPM': 'financial',
            'JNJ': 'healthcare',
            'PG': 'consumer_goods',
            'KO': 'consumer_goods'
        }
        
        # Cache for generated data
        self.data_cache: Dict[str, Any] = {}
        
    def generate_historical_data(self, symbols: List[str], days: int = 30) -> Dict[str, pd.DataFrame]:
        """
        Generate synthetic historical price data
        
        Args:
            symbols: List of stock symbols
            days: Number of days of data to generate
            
        Returns:
            Dictionary mapping symbols to DataFrames with OHLCV data
        """
        result = {}
        
        for symbol in symbols:
            # Generate realistic price data
            base_price = random.uniform(50, 500)
            prices = [base_price]
            
            # Generate price movements with some trend
            trend = random.uniform(-0.001, 0.001)  # Daily trend
            volatility = random.uniform(0.01, 0.03)  # Daily volatility
            
            for i in range(days - 1):
                # Random walk with trend
                change = np.random.normal(trend, volatility)
                new_price = prices[-1] * (1 + change)
                prices.append(max(new_price, 1.0))  # Ensure positive prices
            
            # Generate OHLCV data
            data = []
            for i, close in enumerate(prices):
                # Generate realistic OHLC from close price
                daily_vol = close * random.uniform(0.01, 0.05)
                high = close + random.uniform(0, daily_vol)
                low = close - random.uniform(0, daily_vol)
                open_price = low + random.uniform(0, high - low)
                
                # Ensure OHLC relationships are valid
                high = max(high, open_price, close)
                low = min(low, open_price, close)
                
                volume = random.randint(1000000, 10000000)
                
                data.append({
                    'timestamp': datetime.now() - timedelta(days=days-i-1),
                    'open': round(open_price, 2),
                    'high': round(high, 2),
                    'low': round(low, 2),
                    'close': round(close, 2),
                    'volume': volume,
                    'vwap': round((high + low + close) / 3, 2),
                    'trade_count': random.randint(1000, 10000)
                })
            
            df = pd.DataFrame(data)
            df.set_index('timestamp', inplace=True)
            result[symbol] = df
            
        return result
    
    def get_sec_filings_analysis(self, tickers: List[str]) -> str:
        """
        Generate synthetic SEC filings analysis
        
        Args:
            tickers: List of stock symbols
            
        Returns:
            Formatted analysis string
        """
        analysis_parts = []
        
        for ticker in tickers:
            # Generate realistic financial metrics
            revenue_growth = random.uniform(-0.1, 0.3)
            profit_margin = random.uniform(0.05, 0.25)
            debt_ratio = random.uniform(0.1, 0.6)
            pe_ratio = random.uniform(10, 30)
            
            analysis = f"""
**{ticker} SEC Filings Analysis:**
- Revenue Growth (YoY): {revenue_growth:.1%}
- Profit Margin: {profit_margin:.1%}
- Debt-to-Equity Ratio: {debt_ratio:.2f}
- P/E Ratio: {pe_ratio:.1f}
- Recent 10-K Filing: Strong financial position with {revenue_growth:.1%} revenue growth
- Key Risks: Market volatility, regulatory changes, competitive pressures
- Management Discussion: Focus on innovation and market expansion
"""
            analysis_parts.append(analysis)
        
        return "\n".join(analysis_parts)
    
    def get_market_news_sentiment(self, tickers: List[str], hours_back: int = 24) -> str:
        """
        Generate synthetic market news and sentiment analysis
        
        Args:
            tickers: List of stock symbols
            hours_back: Hours of news to analyze
            
        Returns:
            Formatted sentiment analysis
        """
        sentiment_keywords = {
            'positive': ['strong earnings', 'growth', 'innovation', 'partnership', 'expansion', 'beat expectations'],
            'negative': ['decline', 'missed', 'concerns', 'challenges', 'volatility', 'regulatory'],
            'neutral': ['announced', 'reported', 'trading', 'market', 'shares', 'quarterly']
        }
        
        analysis_parts = []
        
        for ticker in tickers:
            # Generate sentiment score
            sentiment_score = random.uniform(-1, 1)
            
            if sentiment_score > 0.3:
                sentiment = 'positive'
                news_items = random.sample(sentiment_keywords['positive'], 2)
            elif sentiment_score < -0.3:
                sentiment = 'negative'
                news_items = random.sample(sentiment_keywords['negative'], 2)
            else:
                sentiment = 'neutral'
                news_items = random.sample(sentiment_keywords['neutral'], 2)
            
            # Generate news headlines
            headlines = [
                f"{ticker} {news_items[0]} in latest quarterly report",
                f"Analysts {news_items[1]} outlook for {ticker}",
                f"Market reacts to {ticker} {news_items[0]} announcement"
            ]
            
            analysis = f"""
**{ticker} Market News & Sentiment (Last {hours_back}h):**
- Overall Sentiment: {sentiment.title()} (Score: {sentiment_score:.2f})
- Key Headlines:
  • {headlines[0]}
  • {headlines[1]}
  • {headlines[2]}
- Social Media Sentiment: {random.uniform(-0.5, 0.5):.2f}
- Analyst Recommendations: {random.choice(['Buy', 'Hold', 'Sell'])} (Target: ${random.uniform(50, 500):.2f})
- Market Impact: {random.choice(['Low', 'Medium', 'High'])} volatility expected
"""
            analysis_parts.append(analysis)
        
        return "\n".join(analysis_parts)
    
    def get_earnings_analysis(self, tickers: List[str]) -> str:
        """
        Generate synthetic earnings analysis
        
        Args:
            tickers: List of stock symbols
            
        Returns:
            Formatted earnings analysis
        """
        analysis_parts = []
        
        for ticker in tickers:
            # Generate earnings metrics
            eps_actual = random.uniform(0.5, 5.0)
            eps_estimate = eps_actual * random.uniform(0.8, 1.2)
            eps_surprise = ((eps_actual - eps_estimate) / eps_estimate) * 100
            
            revenue_actual = random.uniform(1000, 10000)  # Millions
            revenue_estimate = revenue_actual * random.uniform(0.9, 1.1)
            revenue_surprise = ((revenue_actual - revenue_estimate) / revenue_estimate) * 100
            
            analysis = f"""
**{ticker} Earnings Analysis:**
- EPS Actual: ${eps_actual:.2f} (Estimate: ${eps_estimate:.2f})
- EPS Surprise: {eps_surprise:+.1f}%
- Revenue: ${revenue_actual:.0f}M (Estimate: ${revenue_estimate:.0f}M)
- Revenue Surprise: {revenue_surprise:+.1f}%
- Next Quarter Guidance: {random.choice(['Raised', 'Maintained', 'Lowered'])}
- Year-over-Year Growth: {random.uniform(-0.1, 0.4):.1%}
- Analyst Consensus: {random.choice(['Beat', 'Met', 'Missed'])} expectations
"""
            analysis_parts.append(analysis)
        
        return "\n".join(analysis_parts)
    
    def get_technical_analysis(self, tickers: List[str]) -> str:
        """
        Generate synthetic technical analysis
        
        Args:
            tickers: List of stock symbols
            
        Returns:
            Formatted technical analysis
        """
        analysis_parts = []
        
        for ticker in tickers:
            # Generate technical indicators
            rsi = random.uniform(20, 80)
            macd_signal = random.choice(['Bullish', 'Bearish', 'Neutral'])
            trend = random.choice(['Uptrend', 'Downtrend', 'Sideways'])
            support = random.uniform(50, 200)
            resistance = random.uniform(250, 500)
            
            analysis = f"""
**{ticker} Technical Analysis:**
- RSI (14): {rsi:.1f} ({'Overbought' if rsi > 70 else 'Oversold' if rsi < 30 else 'Neutral'})
- MACD Signal: {macd_signal}
- Trend: {trend}
- Support Level: ${support:.2f}
- Resistance Level: ${resistance:.2f}
- Moving Averages: Price {'above' if random.random() > 0.5 else 'below'} 20-day SMA
- Volume: {'Above average' if random.random() > 0.5 else 'Below average'}
- Technical Rating: {random.choice(['Strong Buy', 'Buy', 'Hold', 'Sell', 'Strong Sell'])}
"""
            analysis_parts.append(analysis)
        
        return "\n".join(analysis_parts)
    
    def get_sector_analysis(self, sector: str) -> str:
        """
        Generate synthetic sector analysis
        
        Args:
            sector: Sector name
            
        Returns:
            Formatted sector analysis
        """
        sector_performance = random.uniform(-0.1, 0.2)
        outlook = random.choice(['Positive', 'Neutral', 'Negative'])
        
        analysis = f"""
**{sector.title()} Sector Analysis:**
- Sector Performance (YTD): {sector_performance:.1%}
- Market Outlook: {outlook}
- Key Drivers: {random.choice(['Technology innovation', 'Regulatory changes', 'Economic growth', 'Consumer demand'])}
- Top Performers: {random.choice(['Large-cap growth', 'Value stocks', 'Dividend payers'])}
- Sector P/E Ratio: {random.uniform(15, 35):.1f}
- Risk Factors: {random.choice(['Interest rate sensitivity', 'Regulatory headwinds', 'Competition', 'Economic cycles'])}
- Investment Theme: {random.choice(['Digital transformation', 'Sustainability', 'AI adoption', 'Supply chain optimization'])}
"""
        return analysis
    
    def calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators on price data
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added technical indicators
        """
        df = data.copy()
        
        # Simple Moving Averages
        df['SMA_20'] = df['close'].rolling(window=20).mean()
        df['SMA_50'] = df['close'].rolling(window=50).mean()
        df['SMA_200'] = df['close'].rolling(window=200).mean()
        
        # Exponential Moving Averages
        df['EMA_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['close'].ewm(span=26, adjust=False).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        
        # Bollinger Bands
        df['BB_Middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (2 * bb_std)
        df['BB_Lower'] = df['BB_Middle'] - (2 * bb_std)
        
        # Volume indicators
        df['Volume_SMA'] = df['volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['volume'] / df['Volume_SMA']
        
        return df
    
    def get_market_summary(self, symbols: List[str]) -> str:
        """
        Generate overall market summary
        
        Args:
            symbols: List of symbols analyzed
            
        Returns:
            Formatted market summary
        """
        market_sentiment = random.choice(['Bullish', 'Bearish', 'Neutral'])
        volatility = random.choice(['Low', 'Medium', 'High'])
        
        summary = f"""
**Market Summary:**
- Overall Sentiment: {market_sentiment}
- Market Volatility: {volatility}
- Key Events: {random.choice(['Earnings season', 'Fed meeting', 'Economic data release', 'Geopolitical developments'])}
- Sector Rotation: {random.choice(['Technology', 'Healthcare', 'Financials', 'Energy'])} leading
- Risk Appetite: {random.choice(['Risk-on', 'Risk-off', 'Mixed'])}
- Trading Volume: {random.choice(['Above average', 'Below average', 'Normal'])}
- Market Breadth: {random.choice(['Positive', 'Negative', 'Neutral'])}
"""
        return summary
    
    def extract_content(self, response: str) -> str:
        """
        Extract content from response (placeholder for API response parsing)
        
        Args:
            response: Response string
            
        Returns:
            Extracted content
        """
        return response