"""
Local data provider to replace external API dependencies
Provides mock financial data and analysis capabilities for local development
"""
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np

class LocalFinanceDataProvider:
    """Local provider for financial data without external API dependencies"""
    
    def __init__(self):
        self.mock_data_cache = {}
        self.mock_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX']
        self._initialize_mock_data()
    
    def _initialize_mock_data(self):
        """Initialize mock financial data"""
        # Generate mock price data for symbols
        for symbol in self.mock_symbols:
            base_price = random.uniform(50, 500)
            dates = pd.date_range(start=datetime.now() - timedelta(days=365), 
                                end=datetime.now(), freq='D')
            
            prices = []
            current_price = base_price
            
            for _ in dates:
                # Simulate price movement with some volatility
                change = random.uniform(-0.05, 0.05)  # ±5% daily change
                current_price *= (1 + change)
                prices.append(current_price)
            
            # Create OHLCV data
            ohlcv_data = []
            for i, price in enumerate(prices):
                high = price * random.uniform(1.0, 1.03)
                low = price * random.uniform(0.97, 1.0)
                open_price = prices[i-1] if i > 0 else price
                volume = random.randint(1000000, 10000000)
                
                ohlcv_data.append({
                    'timestamp': dates[i],
                    'open': open_price,
                    'high': high,
                    'low': low,
                    'close': price,
                    'volume': volume,
                    'trade_count': random.randint(1000, 5000),
                    'vwap': (high + low + price) / 3
                })
            
            self.mock_data_cache[symbol] = pd.DataFrame(ohlcv_data)
    
    def get_sec_filings_analysis(self, tickers: List[str], 
                                search_after_date: str = None) -> Dict[str, Any]:
        """
        Mock SEC filings analysis
        """
        analysis = {
            "choices": [{
                "message": {
                    "content": f"""
                    SEC Filings Analysis for {', '.join(tickers)}:
                    
                    **Key Financial Metrics:**
                    - Revenue Growth: {random.uniform(5, 25):.1f}% YoY
                    - Profit Margin: {random.uniform(10, 30):.1f}%
                    - Debt-to-Equity: {random.uniform(0.1, 0.8):.2f}
                    - Current Ratio: {random.uniform(1.2, 3.0):.2f}
                    
                    **Risk Factors:**
                    - Market competition and pricing pressure
                    - Supply chain dependencies
                    - Regulatory compliance requirements
                    - Economic sensitivity
                    
                    **Management Outlook:**
                    - Positive guidance for next quarter
                    - Investment in R&D and expansion
                    - Focus on operational efficiency
                    - Strong cash position maintained
                    
                    **Recent Developments:**
                    - Strong quarterly earnings performance
                    - New product launches planned
                    - Strategic partnerships announced
                    - Market share expansion initiatives
                    """
                }
            }]
        }
        return analysis
    
    def get_market_news_sentiment(self, tickers: List[str], 
                                 hours_back: int = 24) -> Dict[str, Any]:
        """
        Mock market news and sentiment analysis
        """
        sentiments = ['Bullish', 'Bearish', 'Neutral']
        sentiment = random.choice(sentiments)
        
        analysis = {
            "choices": [{
                "message": {
                    "content": f"""
                    Market News & Sentiment Analysis for {', '.join(tickers)}:
                    
                    **Overall Sentiment: {sentiment}**
                    
                    **Recent Developments:**
                    - Earnings beat expectations by {random.uniform(1, 10):.1f}%
                    - Analyst price target raised to ${random.uniform(150, 300):.0f}
                    - New product announcement driving investor interest
                    - Sector rotation benefiting technology stocks
                    
                    **Price Catalysts:**
                    - Strong quarterly guidance
                    - Market expansion opportunities
                    - Technological innovation leadership
                    - Favorable regulatory environment
                    
                    **Market Dynamics:**
                    - Increased institutional buying
                    - Options activity suggests bullish positioning
                    - Technical breakout above key resistance
                    - Volume surge indicates strong interest
                    
                    **Risk Factors:**
                    - General market volatility
                    - Macroeconomic headwinds
                    - Competitive pressure
                    - Valuation concerns at current levels
                    """
                }
            }]
        }
        return analysis
    
    def get_earnings_analysis(self, tickers: List[str]) -> Dict[str, Any]:
        """
        Mock earnings analysis
        """
        analysis = {
            "choices": [{
                "message": {
                    "content": f"""
                    Earnings Analysis for {', '.join(tickers)}:
                    
                    **Recent Earnings Results:**
                    - EPS: ${random.uniform(2, 8):.2f} (Beat by ${random.uniform(0.05, 0.30):.2f})
                    - Revenue: ${random.uniform(50, 200):.1f}B (Growth: {random.uniform(5, 25):.1f}%)
                    - Gross Margin: {random.uniform(35, 65):.1f}%
                    - Operating Margin: {random.uniform(15, 35):.1f}%
                    
                    **Upcoming Earnings:**
                    - Next earnings date: {(datetime.now() + timedelta(days=random.randint(30, 90))).strftime('%Y-%m-%d')}
                    - Consensus EPS estimate: ${random.uniform(2, 6):.2f}
                    - Revenue estimate: ${random.uniform(55, 180):.1f}B
                    
                    **Growth Trends:**
                    - 3-year revenue CAGR: {random.uniform(8, 20):.1f}%
                    - EPS growth trajectory: Strong and consistent
                    - Market share expansion in key segments
                    - International growth acceleration
                    
                    **Analyst Sentiment:**
                    - {random.randint(15, 25)} Buy ratings
                    - {random.randint(3, 8)} Hold ratings
                    - {random.randint(0, 2)} Sell ratings
                    - Average price target: ${random.uniform(180, 350):.0f}
                    """
                }
            }]
        }
        return analysis
    
    def get_technical_analysis(self, tickers: List[str], 
                              timeframe: str = "1D") -> Dict[str, Any]:
        """
        Mock technical analysis
        """
        analysis = {
            "choices": [{
                "message": {
                    "content": f"""
                    Technical Analysis for {', '.join(tickers)} ({timeframe}):
                    
                    **Current Price Levels:**
                    - Current Price: ${random.uniform(150, 300):.2f}
                    - Support Level: ${random.uniform(140, 280):.2f}
                    - Resistance Level: ${random.uniform(160, 320):.2f}
                    - 52-week Range: ${random.uniform(120, 200):.2f} - ${random.uniform(250, 400):.2f}
                    
                    **Moving Averages:**
                    - 20-day SMA: ${random.uniform(145, 295):.2f}
                    - 50-day SMA: ${random.uniform(140, 290):.2f}
                    - 200-day SMA: ${random.uniform(135, 285):.2f}
                    - Price above all major MAs (Bullish)
                    
                    **Technical Indicators:**
                    - RSI (14): {random.uniform(30, 70):.1f} (Neutral)
                    - MACD: Bullish crossover signal
                    - Bollinger Bands: Price near upper band
                    - Volume: {random.uniform(0.8, 1.5):.1f}x average
                    
                    **Chart Patterns:**
                    - Ascending triangle formation
                    - Breakout above key resistance
                    - Strong momentum indicators
                    - Bullish flag pattern developing
                    
                    **Price Targets:**
                    - Short-term: ${random.uniform(170, 320):.0f}
                    - Medium-term: ${random.uniform(200, 380):.0f}
                    - Stop-loss: ${random.uniform(130, 270):.0f}
                    """
                }
            }]
        }
        return analysis
    
    def get_sector_analysis(self, sector: str) -> Dict[str, Any]:
        """
        Mock sector analysis
        """
        analysis = {
            "choices": [{
                "message": {
                    "content": f"""
                    {sector.title()} Sector Analysis:
                    
                    **Sector Performance:**
                    - YTD Performance: {random.uniform(-10, 30):.1f}%
                    - Relative to S&P 500: {random.uniform(-5, 15):.1f}%
                    - Market Cap: ${random.uniform(500, 2000):.0f}B
                    - P/E Ratio: {random.uniform(15, 35):.1f}x
                    
                    **Key Drivers:**
                    - Digital transformation acceleration
                    - AI and automation adoption
                    - Cloud computing growth
                    - Regulatory tailwinds
                    
                    **Growth Catalysts:**
                    - Emerging market expansion
                    - New technology adoption
                    - Government infrastructure spending
                    - ESG investment trends
                    
                    **Challenges:**
                    - Supply chain constraints
                    - Talent acquisition costs
                    - Regulatory uncertainty
                    - Competitive pressure
                    
                    **Top Performers:**
                    - Leading companies showing 20%+ growth
                    - Innovation leaders gaining market share
                    - Strong balance sheet companies
                    - ESG-focused organizations
                    
                    **Investment Outlook:**
                    - Positive long-term fundamentals
                    - Near-term volatility expected
                    - Selective stock picking recommended
                    - Focus on quality and growth
                    """
                }
            }]
        }
        return analysis
    
    def get_historical_bars(self, symbols: List[str], 
                           start_date: datetime = None,
                           end_date: datetime = None,
                           limit: int = 1000) -> Dict[str, pd.DataFrame]:
        """
        Get historical bar data for symbols
        """
        result = {}
        for symbol in symbols:
            if symbol in self.mock_data_cache:
                df = self.mock_data_cache[symbol].copy()
                
                # Apply date filters if provided
                if start_date:
                    df = df[df['timestamp'] >= start_date]
                if end_date:
                    df = df[df['timestamp'] <= end_date]
                
                # Apply limit
                if limit:
                    df = df.tail(limit)
                
                result[symbol] = df
            else:
                # Generate data for unknown symbol
                result[symbol] = self._generate_mock_data(symbol, start_date, end_date, limit)
        
        return result
    
    def _generate_mock_data(self, symbol: str, start_date: datetime = None, 
                           end_date: datetime = None, limit: int = 100) -> pd.DataFrame:
        """Generate mock data for a symbol"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=limit)
        if not end_date:
            end_date = datetime.now()
        
        dates = pd.date_range(start=start_date, end=end_date, freq='D')[:limit]
        base_price = random.uniform(50, 500)
        
        data = []
        current_price = base_price
        
        for date in dates:
            change = random.uniform(-0.03, 0.03)
            current_price *= (1 + change)
            
            high = current_price * random.uniform(1.0, 1.02)
            low = current_price * random.uniform(0.98, 1.0)
            volume = random.randint(500000, 5000000)
            
            data.append({
                'timestamp': date,
                'open': current_price,
                'high': high,
                'low': low,
                'close': current_price,
                'volume': volume,
                'trade_count': random.randint(500, 2500),
                'vwap': (high + low + current_price) / 3
            })
        
        return pd.DataFrame(data)
    
    def get_latest_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Get latest quotes for symbols
        """
        quotes = {}
        for symbol in symbols:
            base_price = random.uniform(100, 400)
            spread = base_price * 0.001  # 0.1% spread
            
            quotes[symbol] = {
                'bid': base_price - spread/2,
                'ask': base_price + spread/2,
                'bid_size': random.randint(100, 1000),
                'ask_size': random.randint(100, 1000),
                'timestamp': datetime.now()
            }
        
        return quotes
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators for a DataFrame
        """
        df = df.copy()
        
        # Moving Averages
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['ema_12'] = df['close'].ewm(span=12).mean()
        df['ema_26'] = df['close'].ewm(span=26).mean()
        
        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # ATR (Average True Range)
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        df['atr'] = true_range.rolling(window=14).mean()
        
        # Volume indicators
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        # Price change indicators
        df['price_change'] = df['close'].pct_change()
        df['price_change_5d'] = df['close'].pct_change(5)
        df['price_change_20d'] = df['close'].pct_change(20)
        
        return df

class LocalTradingSimulator:
    """Local trading simulator to replace Alpaca API"""
    
    def __init__(self):
        self.account_data = {
            'account_id': 'LOCAL_ACCOUNT_001',
            'equity': 100000.0,
            'cash': 100000.0,
            'buying_power': 200000.0,
            'portfolio_value': 100000.0,
            'day_trade_count': 0,
            'pattern_day_trader': False
        }
        self.positions = []
        self.orders = []
        self.order_counter = 1000
        
    def get_account(self) -> Dict[str, Any]:
        """Get account information"""
        return self.account_data.copy()
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get current positions"""
        return self.positions.copy()
    
    def place_market_order(self, symbol: str, qty: float, side: str) -> Dict[str, Any]:
        """Simulate placing a market order"""
        order_id = f"ORDER_{self.order_counter}"
        self.order_counter += 1
        
        # Simulate current market price
        current_price = random.uniform(100, 400)
        
        order = {
            'id': order_id,
            'symbol': symbol,
            'qty': qty,
            'side': side,
            'order_type': 'market',
            'status': 'filled',
            'created_at': datetime.now(),
            'filled_at': datetime.now(),
            'filled_qty': qty,
            'filled_avg_price': current_price
        }
        
        self.orders.append(order)
        
        # Update positions
        self._update_position(symbol, qty if side == 'buy' else -qty, current_price)
        
        # Update account cash
        cost = qty * current_price
        if side == 'buy':
            self.account_data['cash'] -= cost
        else:
            self.account_data['cash'] += cost
        
        self._recalculate_account()
        
        return order
    
    def place_limit_order(self, symbol: str, qty: float, side: str, limit_price: float) -> Dict[str, Any]:
        """Simulate placing a limit order"""
        order_id = f"ORDER_{self.order_counter}"
        self.order_counter += 1
        
        order = {
            'id': order_id,
            'symbol': symbol,
            'qty': qty,
            'side': side,
            'order_type': 'limit',
            'limit_price': limit_price,
            'status': 'new',
            'created_at': datetime.now(),
            'filled_at': None,
            'filled_qty': 0,
            'filled_avg_price': 0
        }
        
        self.orders.append(order)
        return order
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        for order in self.orders:
            if order['id'] == order_id and order['status'] == 'new':
                order['status'] = 'cancelled'
                return True
        return False
    
    def get_orders(self, status: str = None) -> List[Dict[str, Any]]:
        """Get orders with optional status filter"""
        if status:
            return [order for order in self.orders if order['status'] == status]
        return self.orders.copy()
    
    def _update_position(self, symbol: str, qty_change: float, price: float):
        """Update position for a symbol"""
        for pos in self.positions:
            if pos['symbol'] == symbol:
                old_qty = pos['qty']
                old_cost = pos['cost_basis'] * old_qty
                new_qty = old_qty + qty_change
                
                if new_qty == 0:
                    self.positions.remove(pos)
                else:
                    new_cost = old_cost + (qty_change * price)
                    pos['qty'] = new_qty
                    pos['cost_basis'] = new_cost / new_qty if new_qty != 0 else 0
                    pos['current_price'] = price
                    pos['market_value'] = new_qty * price
                    pos['unrealized_pl'] = pos['market_value'] - (new_qty * pos['cost_basis'])
                    pos['unrealized_plpc'] = pos['unrealized_pl'] / (new_qty * pos['cost_basis']) if pos['cost_basis'] != 0 else 0
                return
        
        # Create new position
        if qty_change != 0:
            position = {
                'symbol': symbol,
                'qty': qty_change,
                'side': 'long' if qty_change > 0 else 'short',
                'market_value': qty_change * price,
                'cost_basis': price,
                'unrealized_pl': 0,
                'unrealized_plpc': 0,
                'current_price': price
            }
            self.positions.append(position)
    
    def _recalculate_account(self):
        """Recalculate account values"""
        total_market_value = sum(pos['market_value'] for pos in self.positions)
        self.account_data['equity'] = self.account_data['cash'] + total_market_value
        self.account_data['portfolio_value'] = self.account_data['equity']
        self.account_data['buying_power'] = self.account_data['cash'] * 2  # 2:1 margin

def extract_content(response: Dict[str, Any]) -> str:
    """Extract content from mock API response"""
    try:
        if "choices" in response and len(response["choices"]) > 0:
            return response["choices"][0]["message"]["content"]
        elif "error" in response:
            return f"Error: {response['error']}"
        else:
            return "No content available"
    except (KeyError, IndexError) as e:
        return f"Error extracting content: {e}"