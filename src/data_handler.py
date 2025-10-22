"""
Alpaca Data Handler
Real-time and historical market data integration using alpaca-py SDK
"""

import asyncio
from typing import List, Dict, Optional, Callable
from datetime import datetime, timedelta
import pandas as pd
import logging

from alpaca.data import StockHistoricalDataClient, StockDataStream
from alpaca.data.requests import (
    StockBarsRequest, 
    StockLatestQuoteRequest,
    StockLatestTradeRequest,
    StockSnapshotRequest
)
from alpaca.data.timeframe import TimeFrame
from alpaca.data.models import Bar, Trade, Quote

from src.config import config

logger = logging.getLogger(__name__)


class AlpacaDataHandler:
    """
    Handle real-time and historical market data from Alpaca
    Supports WebSocket streaming and REST API data fetching
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None
    ):
        self.api_key = api_key or config.alpaca.api_key
        self.secret_key = secret_key or config.alpaca.secret_key
        
        # Historical data client
        self.historical_client = StockHistoricalDataClient(
            self.api_key, 
            self.secret_key
        )
        
        # Streaming client
        self.stream_client = StockDataStream(
            self.api_key, 
            self.secret_key
        )
        
        # Data cache
        self.bars_cache: Dict[str, pd.DataFrame] = {}
        self.quotes_cache: Dict[str, Quote] = {}
        self.trades_cache: Dict[str, Trade] = {}
        
        # Callbacks
        self.bar_callbacks: List[Callable] = []
        self.trade_callbacks: List[Callable] = []
        self.quote_callbacks: List[Callable] = []
        
        # Stream status
        self.is_streaming = False
    
    # ============= Historical Data Methods =============
    
    def get_historical_bars(
        self,
        symbols: List[str],
        timeframe: TimeFrame = TimeFrame.Day,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch historical bar data for symbols
        
        Args:
            symbols: List of stock symbols
            timeframe: Bar timeframe (Day, Hour, Minute, etc.)
            start: Start datetime (default: 30 days ago)
            end: End datetime (default: now)
            limit: Maximum number of bars per symbol
        
        Returns:
            Dictionary mapping symbols to DataFrame of bars
        """
        if start is None:
            start = datetime.now() - timedelta(days=30)
        if end is None:
            end = datetime.now()
        
        request = StockBarsRequest(
            symbol_or_symbols=symbols,
            timeframe=timeframe,
            start=start,
            end=end,
            limit=limit
        )
        
        try:
            bars = self.historical_client.get_stock_bars(request)
            
            # Convert to DataFrames
            result = {}
            for symbol in symbols:
                if symbol in bars:
                    df = bars[symbol].df
                    result[symbol] = df
                    # Cache the data
                    self.bars_cache[symbol] = df
                    logger.info(f"Fetched {len(df)} bars for {symbol}")
                else:
                    logger.warning(f"No data available for {symbol}")
            
            return result
        
        except Exception as e:
            logger.error(f"Failed to fetch historical bars: {e}")
            raise
    
    def get_latest_quote(self, symbols: List[str]) -> Dict[str, Quote]:
        """
        Get latest quote for symbols
        
        Args:
            symbols: List of stock symbols
        
        Returns:
            Dictionary mapping symbols to Quote objects
        """
        request = StockLatestQuoteRequest(symbol_or_symbols=symbols)
        
        try:
            quotes = self.historical_client.get_stock_latest_quote(request)
            
            # Update cache
            for symbol, quote in quotes.items():
                self.quotes_cache[symbol] = quote
            
            return quotes
        
        except Exception as e:
            logger.error(f"Failed to fetch latest quotes: {e}")
            raise
    
    def get_latest_trade(self, symbols: List[str]) -> Dict[str, Trade]:
        """
        Get latest trade for symbols
        
        Args:
            symbols: List of stock symbols
        
        Returns:
            Dictionary mapping symbols to Trade objects
        """
        request = StockLatestTradeRequest(symbol_or_symbols=symbols)
        
        try:
            trades = self.historical_client.get_stock_latest_trade(request)
            
            # Update cache
            for symbol, trade in trades.items():
                self.trades_cache[symbol] = trade
            
            return trades
        
        except Exception as e:
            logger.error(f"Failed to fetch latest trades: {e}")
            raise
    
    def get_snapshot(self, symbols: List[str]) -> Dict:
        """
        Get market snapshot (latest quote, trade, bars, etc.)
        
        Args:
            symbols: List of stock symbols
        
        Returns:
            Dictionary with snapshot data
        """
        request = StockSnapshotRequest(symbol_or_symbols=symbols)
        
        try:
            snapshots = self.historical_client.get_stock_snapshot(request)
            return snapshots
        
        except Exception as e:
            logger.error(f"Failed to fetch snapshots: {e}")
            raise
    
    # ============= Real-time Streaming Methods =============
    
    async def stream_bars(
        self, 
        symbols: List[str],
        callback: Optional[Callable] = None
    ):
        """
        Stream real-time bar data
        
        Args:
            symbols: List of symbols to stream
            callback: Function to call when bar received
        """
        if callback:
            self.bar_callbacks.append(callback)
        
        async def bar_handler(bar: Bar):
            """Handle incoming bar data"""
            symbol = bar.symbol
            logger.debug(f"Received bar for {symbol}: {bar.close}")
            
            # Update cache
            if symbol not in self.bars_cache:
                self.bars_cache[symbol] = pd.DataFrame()
            
            # Append to cache
            bar_data = {
                'timestamp': bar.timestamp,
                'open': bar.open,
                'high': bar.high,
                'low': bar.low,
                'close': bar.close,
                'volume': bar.volume,
                'vwap': bar.vwap,
                'trade_count': bar.trade_count
            }
            
            self.bars_cache[symbol] = pd.concat([
                self.bars_cache[symbol],
                pd.DataFrame([bar_data])
            ]).tail(1000)  # Keep last 1000 bars
            
            # Call registered callbacks
            for cb in self.bar_callbacks:
                try:
                    if asyncio.iscoroutinefunction(cb):
                        await cb(bar)
                    else:
                        cb(bar)
                except Exception as e:
                    logger.error(f"Error in bar callback: {e}")
        
        # Subscribe to bars
        self.stream_client.subscribe_bars(bar_handler, *symbols)
    
    async def stream_trades(
        self, 
        symbols: List[str],
        callback: Optional[Callable] = None
    ):
        """
        Stream real-time trade data
        
        Args:
            symbols: List of symbols to stream
            callback: Function to call when trade received
        """
        if callback:
            self.trade_callbacks.append(callback)
        
        async def trade_handler(trade: Trade):
            """Handle incoming trade data"""
            symbol = trade.symbol
            logger.debug(f"Received trade for {symbol}: {trade.price} x {trade.size}")
            
            # Update cache
            self.trades_cache[symbol] = trade
            
            # Call registered callbacks
            for cb in self.trade_callbacks:
                try:
                    if asyncio.iscoroutinefunction(cb):
                        await cb(trade)
                    else:
                        cb(trade)
                except Exception as e:
                    logger.error(f"Error in trade callback: {e}")
        
        # Subscribe to trades
        self.stream_client.subscribe_trades(trade_handler, *symbols)
    
    async def stream_quotes(
        self, 
        symbols: List[str],
        callback: Optional[Callable] = None
    ):
        """
        Stream real-time quote data
        
        Args:
            symbols: List of symbols to stream
            callback: Function to call when quote received
        """
        if callback:
            self.quote_callbacks.append(callback)
        
        async def quote_handler(quote: Quote):
            """Handle incoming quote data"""
            symbol = quote.symbol
            logger.debug(f"Received quote for {symbol}: Bid {quote.bid_price}, Ask {quote.ask_price}")
            
            # Update cache
            self.quotes_cache[symbol] = quote
            
            # Call registered callbacks
            for cb in self.quote_callbacks:
                try:
                    if asyncio.iscoroutinefunction(cb):
                        await cb(quote)
                    else:
                        cb(quote)
                except Exception as e:
                    logger.error(f"Error in quote callback: {e}")
        
        # Subscribe to quotes
        self.stream_client.subscribe_quotes(quote_handler, *symbols)
    
    async def start_streaming(self):
        """Start the WebSocket stream"""
        if self.is_streaming:
            logger.warning("Stream already running")
            return
        
        logger.info("Starting Alpaca data stream...")
        self.is_streaming = True
        
        try:
            await self.stream_client.run()
        except Exception as e:
            logger.error(f"Stream error: {e}")
            self.is_streaming = False
            raise
    
    async def stop_streaming(self):
        """Stop the WebSocket stream"""
        if not self.is_streaming:
            return
        
        logger.info("Stopping Alpaca data stream...")
        await self.stream_client.close()
        self.is_streaming = False
    
    # ============= Data Analysis Methods =============
    
    def calculate_indicators(
        self, 
        symbol: str,
        indicators: List[str] = None
    ) -> pd.DataFrame:
        """
        Calculate technical indicators on cached data
        
        Args:
            symbol: Stock symbol
            indicators: List of indicators to calculate
                       ['SMA', 'EMA', 'RSI', 'MACD', 'BBANDS']
        
        Returns:
            DataFrame with indicators
        """
        if symbol not in self.bars_cache or self.bars_cache[symbol].empty:
            raise ValueError(f"No cached data for {symbol}")
        
        df = self.bars_cache[symbol].copy()
        
        if indicators is None:
            indicators = ['SMA_20', 'SMA_50', 'RSI', 'MACD']
        
        # Simple Moving Averages
        if 'SMA_20' in indicators:
            df['SMA_20'] = df['close'].rolling(window=20).mean()
        if 'SMA_50' in indicators:
            df['SMA_50'] = df['close'].rolling(window=50).mean()
        if 'SMA_200' in indicators:
            df['SMA_200'] = df['close'].rolling(window=200).mean()
        
        # Exponential Moving Averages
        if 'EMA_12' in indicators:
            df['EMA_12'] = df['close'].ewm(span=12, adjust=False).mean()
        if 'EMA_26' in indicators:
            df['EMA_26'] = df['close'].ewm(span=26, adjust=False).mean()
        
        # RSI
        if 'RSI' in indicators:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        if 'MACD' in indicators:
            if 'EMA_12' not in df.columns:
                df['EMA_12'] = df['close'].ewm(span=12, adjust=False).mean()
            if 'EMA_26' not in df.columns:
                df['EMA_26'] = df['close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        
        # Bollinger Bands
        if 'BBANDS' in indicators:
            df['BB_Middle'] = df['close'].rolling(window=20).mean()
            bb_std = df['close'].rolling(window=20).std()
            df['BB_Upper'] = df['BB_Middle'] + (2 * bb_std)
            df['BB_Lower'] = df['BB_Middle'] - (2 * bb_std)
        
        # Volume indicators
        if 'Volume_SMA' in indicators:
            df['Volume_SMA'] = df['volume'].rolling(window=20).mean()
            df['Volume_Ratio'] = df['volume'] / df['Volume_SMA']
        
        return df
    
    def get_price_summary(self, symbol: str) -> Dict:
        """
        Get summary statistics for a symbol
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Dictionary with price statistics
        """
        if symbol not in self.bars_cache or self.bars_cache[symbol].empty:
            raise ValueError(f"No cached data for {symbol}")
        
        df = self.bars_cache[symbol]
        latest = df.iloc[-1]
        oldest = df.iloc[0]
        
        return {
            'symbol': symbol,
            'latest_price': float(latest['close']),
            'latest_time': latest.name,
            'change': float(latest['close'] - oldest['close']),
            'change_pct': float((latest['close'] - oldest['close']) / oldest['close'] * 100),
            'high': float(df['high'].max()),
            'low': float(df['low'].min()),
            'avg_volume': float(df['volume'].mean()),
            'latest_volume': float(latest['volume']),
            'bars_count': len(df)
        }
    
    def format_price_data_summary(self, symbols: List[str]) -> str:
        """
        Format price data for multiple symbols as text summary
        
        Args:
            symbols: List of symbols to summarize
        
        Returns:
            Formatted string summary
        """
        summaries = []
        for symbol in symbols:
            try:
                summary = self.get_price_summary(symbol)
                summaries.append(
                    f"{summary['symbol']}: ${summary['latest_price']:.2f} "
                    f"({summary['change_pct']:+.2f}% over {summary['bars_count']} periods)"
                )
            except ValueError:
                summaries.append(f"{symbol}: No data available")
        
        return "\n".join(summaries)
    
    # ============= Utility Methods =============
    
    def clear_cache(self, symbol: Optional[str] = None):
        """Clear cached data"""
        if symbol:
            self.bars_cache.pop(symbol, None)
            self.quotes_cache.pop(symbol, None)
            self.trades_cache.pop(symbol, None)
            logger.info(f"Cleared cache for {symbol}")
        else:
            self.bars_cache.clear()
            self.quotes_cache.clear()
            self.trades_cache.clear()
            logger.info("Cleared all cache")
    
    def get_cached_bars(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get cached bars for a symbol"""
        return self.bars_cache.get(symbol)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.is_streaming:
            asyncio.run(self.stop_streaming())
