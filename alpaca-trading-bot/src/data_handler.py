"""
Alpaca data handler for real-time and historical market data
"""

import asyncio
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from loguru import logger
from alpaca.data import StockHistoricalDataClient, StockBarsRequest, StockTradesRequest
from alpaca.data.live import StockDataStream
from alpaca.data.timeframe import TimeFrame
from alpaca.data.models import Bar, Trade, Quote
from collections import deque
import pickle
from pathlib import Path


class DataHandler:
    """Handles all data operations with Alpaca API"""
    
    def __init__(
        self,
        api_key: str,
        secret_key: str,
        feed: str = "iex",
        cache_dir: str = "data_cache"
    ):
        self.api_key = api_key
        self.secret_key = secret_key
        self.feed = feed
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Initialize clients
        self.historical_client = StockHistoricalDataClient(api_key, secret_key)
        self.stream_client = StockDataStream(api_key, secret_key, feed=feed)
        
        # Data storage
        self.bars_buffer = {}  # Symbol -> deque of bars
        self.trades_buffer = {}  # Symbol -> deque of trades
        self.quotes_buffer = {}  # Symbol -> deque of quotes
        self.buffer_size = 1000  # Max items per buffer
        
        # Callbacks
        self.bar_callbacks = []
        self.trade_callbacks = []
        self.quote_callbacks = []
        
        # Statistics
        self.stats = {
            "bars_received": 0,
            "trades_received": 0,
            "quotes_received": 0,
            "errors": 0
        }
    
    def get_historical_bars(
        self,
        symbols: List[str],
        timeframe: TimeFrame,
        start: datetime,
        end: Optional[datetime] = None
    ) -> pd.DataFrame:
        """Fetch historical bar data"""
        
        # Check cache first
        cache_key = f"bars_{'_'.join(symbols)}_{timeframe.value}_{start.date()}_{end.date() if end else 'now'}"
        cached_data = self._load_from_cache(cache_key)
        if cached_data is not None:
            logger.info(f"Loaded historical data from cache: {cache_key}")
            return cached_data
        
        try:
            request_params = StockBarsRequest(
                symbol_or_symbols=symbols,
                timeframe=timeframe,
                start=start,
                end=end
            )
            
            bars = self.historical_client.get_stock_bars(request_params)
            
            # Convert to DataFrame
            df_list = []
            for symbol in symbols:
                if symbol in bars:
                    symbol_bars = bars[symbol]
                    df = pd.DataFrame([{
                        'symbol': symbol,
                        'timestamp': bar.timestamp,
                        'open': bar.open,
                        'high': bar.high,
                        'low': bar.low,
                        'close': bar.close,
                        'volume': bar.volume,
                        'vwap': bar.vwap,
                        'trade_count': bar.trade_count
                    } for bar in symbol_bars])
                    df_list.append(df)
            
            if df_list:
                result_df = pd.concat(df_list, ignore_index=True)
                result_df['timestamp'] = pd.to_datetime(result_df['timestamp'])
                result_df.set_index('timestamp', inplace=True)
                
                # Cache the result
                self._save_to_cache(cache_key, result_df)
                
                logger.info(f"Fetched {len(result_df)} bars for {symbols}")
                return result_df
            else:
                logger.warning(f"No data found for {symbols}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching historical bars: {e}")
            self.stats["errors"] += 1
            raise
    
    def get_latest_trades(
        self,
        symbols: List[str],
        limit: int = 100
    ) -> pd.DataFrame:
        """Fetch latest trades"""
        
        try:
            request_params = StockTradesRequest(
                symbol_or_symbols=symbols,
                limit=limit
            )
            
            trades = self.historical_client.get_stock_latest_trades(request_params)
            
            # Convert to DataFrame
            df_list = []
            for symbol, trade in trades.items():
                df_list.append({
                    'symbol': symbol,
                    'timestamp': trade.timestamp,
                    'price': trade.price,
                    'size': trade.size,
                    'conditions': trade.conditions,
                    'exchange': trade.exchange
                })
            
            if df_list:
                result_df = pd.DataFrame(df_list)
                result_df['timestamp'] = pd.to_datetime(result_df['timestamp'])
                return result_df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching latest trades: {e}")
            self.stats["errors"] += 1
            raise
    
    async def stream_bars(
        self,
        symbols: List[str],
        callback: Optional[Callable] = None
    ):
        """Stream real-time bar data"""
        
        async def bar_handler(data: Bar):
            """Handle incoming bar data"""
            symbol = data.symbol
            
            # Add to buffer
            if symbol not in self.bars_buffer:
                self.bars_buffer[symbol] = deque(maxlen=self.buffer_size)
            self.bars_buffer[symbol].append(data)
            
            # Update stats
            self.stats["bars_received"] += 1
            
            # Execute callbacks
            if callback:
                await callback(data)
            for cb in self.bar_callbacks:
                await cb(data)
            
            logger.debug(f"Bar received: {symbol} - Close: ${data.close:.2f}")
        
        # Subscribe to bar updates
        for symbol in symbols:
            self.stream_client.subscribe_bars(bar_handler, symbol)
        
        logger.info(f"Subscribed to bar stream for {symbols}")
    
    async def stream_trades(
        self,
        symbols: List[str],
        callback: Optional[Callable] = None
    ):
        """Stream real-time trade data"""
        
        async def trade_handler(data: Trade):
            """Handle incoming trade data"""
            symbol = data.symbol
            
            # Add to buffer
            if symbol not in self.trades_buffer:
                self.trades_buffer[symbol] = deque(maxlen=self.buffer_size)
            self.trades_buffer[symbol].append(data)
            
            # Update stats
            self.stats["trades_received"] += 1
            
            # Execute callbacks
            if callback:
                await callback(data)
            for cb in self.trade_callbacks:
                await cb(data)
            
            logger.debug(f"Trade received: {symbol} - Price: ${data.price:.2f} Size: {data.size}")
        
        # Subscribe to trade updates
        for symbol in symbols:
            self.stream_client.subscribe_trades(trade_handler, symbol)
        
        logger.info(f"Subscribed to trade stream for {symbols}")
    
    async def stream_quotes(
        self,
        symbols: List[str],
        callback: Optional[Callable] = None
    ):
        """Stream real-time quote data"""
        
        async def quote_handler(data: Quote):
            """Handle incoming quote data"""
            symbol = data.symbol
            
            # Add to buffer
            if symbol not in self.quotes_buffer:
                self.quotes_buffer[symbol] = deque(maxlen=self.buffer_size)
            self.quotes_buffer[symbol].append(data)
            
            # Update stats
            self.stats["quotes_received"] += 1
            
            # Execute callbacks
            if callback:
                await callback(data)
            for cb in self.quote_callbacks:
                await cb(data)
            
            logger.debug(f"Quote received: {symbol} - Bid: ${data.bid_price:.2f} Ask: ${data.ask_price:.2f}")
        
        # Subscribe to quote updates
        for symbol in symbols:
            self.stream_client.subscribe_quotes(quote_handler, symbol)
        
        logger.info(f"Subscribed to quote stream for {symbols}")
    
    async def start_streaming(self):
        """Start the WebSocket connection"""
        try:
            logger.info("Starting data stream...")
            await self.stream_client.run()
        except Exception as e:
            logger.error(f"Stream error: {e}")
            self.stats["errors"] += 1
            raise
    
    async def stop_streaming(self):
        """Stop the WebSocket connection"""
        try:
            logger.info("Stopping data stream...")
            await self.stream_client.stop()
        except Exception as e:
            logger.error(f"Error stopping stream: {e}")
    
    def get_buffer_data(
        self,
        symbol: str,
        data_type: str = "bars"
    ) -> pd.DataFrame:
        """Get buffered data as DataFrame"""
        
        if data_type == "bars" and symbol in self.bars_buffer:
            bars = list(self.bars_buffer[symbol])
            if bars:
                df = pd.DataFrame([{
                    'timestamp': bar.timestamp,
                    'open': bar.open,
                    'high': bar.high,
                    'low': bar.low,
                    'close': bar.close,
                    'volume': bar.volume
                } for bar in bars])
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)
                return df
        
        elif data_type == "trades" and symbol in self.trades_buffer:
            trades = list(self.trades_buffer[symbol])
            if trades:
                df = pd.DataFrame([{
                    'timestamp': trade.timestamp,
                    'price': trade.price,
                    'size': trade.size
                } for trade in trades])
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)
                return df
        
        elif data_type == "quotes" and symbol in self.quotes_buffer:
            quotes = list(self.quotes_buffer[symbol])
            if quotes:
                df = pd.DataFrame([{
                    'timestamp': quote.timestamp,
                    'bid_price': quote.bid_price,
                    'bid_size': quote.bid_size,
                    'ask_price': quote.ask_price,
                    'ask_size': quote.ask_size,
                    'spread': quote.ask_price - quote.bid_price
                } for quote in quotes])
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)
                return df
        
        return pd.DataFrame()
    
    def calculate_indicators(
        self,
        df: pd.DataFrame,
        indicators: List[str]
    ) -> pd.DataFrame:
        """Calculate technical indicators on price data"""
        
        result_df = df.copy()
        
        if 'SMA_20' in indicators:
            result_df['SMA_20'] = df['close'].rolling(window=20).mean()
        
        if 'SMA_50' in indicators:
            result_df['SMA_50'] = df['close'].rolling(window=50).mean()
        
        if 'RSI' in indicators:
            result_df['RSI'] = self._calculate_rsi(df['close'])
        
        if 'MACD' in indicators:
            exp1 = df['close'].ewm(span=12, adjust=False).mean()
            exp2 = df['close'].ewm(span=26, adjust=False).mean()
            result_df['MACD'] = exp1 - exp2
            result_df['MACD_signal'] = result_df['MACD'].ewm(span=9, adjust=False).mean()
        
        if 'BB' in indicators:
            sma = df['close'].rolling(window=20).mean()
            std = df['close'].rolling(window=20).std()
            result_df['BB_upper'] = sma + (std * 2)
            result_df['BB_lower'] = sma - (std * 2)
            result_df['BB_middle'] = sma
        
        if 'ATR' in indicators:
            result_df['ATR'] = self._calculate_atr(df)
        
        if 'VWAP' in indicators and 'volume' in df.columns:
            result_df['VWAP'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
        
        return result_df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    def _save_to_cache(self, key: str, data: pd.DataFrame):
        """Save data to cache"""
        cache_file = self.cache_dir / f"{key}.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
            logger.debug(f"Cached data: {key}")
        except Exception as e:
            logger.warning(f"Failed to cache data: {e}")
    
    def _load_from_cache(self, key: str) -> Optional[pd.DataFrame]:
        """Load data from cache"""
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            try:
                # Check if cache is recent (less than 1 hour old)
                if (datetime.now().timestamp() - cache_file.stat().st_mtime) < 3600:
                    with open(cache_file, 'rb') as f:
                        return pickle.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get data handler statistics"""
        return {
            **self.stats,
            "buffer_sizes": {
                "bars": {symbol: len(buffer) for symbol, buffer in self.bars_buffer.items()},
                "trades": {symbol: len(buffer) for symbol, buffer in self.trades_buffer.items()},
                "quotes": {symbol: len(buffer) for symbol, buffer in self.quotes_buffer.items()}
            }
        }