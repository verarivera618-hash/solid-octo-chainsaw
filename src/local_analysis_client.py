"""
Local analysis client - Replaces Perplexity with local analysis capabilities
No external API calls required
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
try:
    from .local_data_client import LocalDataClient
except ImportError:
    from local_data_client import LocalDataClient

class LocalAnalysisClient:
    """Client for local financial analysis without external dependencies"""
    
    def __init__(self):
        self.data_client = LocalDataClient()
    
    def get_market_analysis(self, tickers: List[str]) -> Dict[str, Any]:
        """
        Perform local market analysis for given tickers
        """
        analysis = {}
        
        for ticker in tickers:
            # Get historical data
            hist_data = self.data_client.get_historical_bars([ticker], limit=100)
            
            if ticker in hist_data and not hist_data[ticker].empty:
                df = hist_data[ticker]
                df = self.data_client.calculate_technical_indicators(df)
                
                # Calculate analysis metrics
                analysis[ticker] = {
                    'current_price': float(df['close'].iloc[-1]),
                    'price_change_1d': float(df['price_change'].iloc[-1]) if 'price_change' in df else 0,
                    'price_change_5d': float(df['price_change_5d'].iloc[-1]) if 'price_change_5d' in df else 0,
                    'price_change_20d': float(df['price_change_20d'].iloc[-1]) if 'price_change_20d' in df else 0,
                    'volume_ratio': float(df['volume_ratio'].iloc[-1]) if 'volume_ratio' in df else 1,
                    'rsi': float(df['rsi'].iloc[-1]) if 'rsi' in df else 50,
                    'macd': float(df['macd'].iloc[-1]) if 'macd' in df else 0,
                    'bb_position': float(df['bb_position'].iloc[-1]) if 'bb_position' in df else 0.5,
                    'sentiment': self._calculate_sentiment(df),
                    'trend': self._identify_trend(df),
                    'support_levels': self._find_support_resistance(df, 'support'),
                    'resistance_levels': self._find_support_resistance(df, 'resistance'),
                    'recommendation': self._generate_recommendation(df)
                }
            else:
                # Generate default analysis if no data
                analysis[ticker] = self._generate_default_analysis()
        
        return {
            'analysis': analysis,
            'timestamp': datetime.now().isoformat(),
            'summary': self._generate_summary(analysis)
        }
    
    def get_technical_analysis(self, tickers: List[str], timeframe: str = "1D") -> Dict[str, Any]:
        """
        Perform technical analysis for tickers
        """
        results = {}
        
        for ticker in tickers:
            hist_data = self.data_client.get_historical_bars([ticker], limit=200)
            
            if ticker in hist_data and not hist_data[ticker].empty:
                df = hist_data[ticker]
                df = self.data_client.calculate_technical_indicators(df)
                
                results[ticker] = {
                    'indicators': {
                        'sma_20': float(df['sma_20'].iloc[-1]) if 'sma_20' in df else None,
                        'sma_50': float(df['sma_50'].iloc[-1]) if 'sma_50' in df else None,
                        'ema_12': float(df['ema_12'].iloc[-1]) if 'ema_12' in df else None,
                        'ema_26': float(df['ema_26'].iloc[-1]) if 'ema_26' in df else None,
                        'rsi': float(df['rsi'].iloc[-1]) if 'rsi' in df else None,
                        'macd': float(df['macd'].iloc[-1]) if 'macd' in df else None,
                        'macd_signal': float(df['macd_signal'].iloc[-1]) if 'macd_signal' in df else None,
                        'bb_upper': float(df['bb_upper'].iloc[-1]) if 'bb_upper' in df else None,
                        'bb_middle': float(df['bb_middle'].iloc[-1]) if 'bb_middle' in df else None,
                        'bb_lower': float(df['bb_lower'].iloc[-1]) if 'bb_lower' in df else None,
                        'atr': float(df['atr'].iloc[-1]) if 'atr' in df else None
                    },
                    'signals': self._generate_trading_signals(df),
                    'patterns': self._identify_patterns(df),
                    'strength': self._calculate_trend_strength(df)
                }
        
        return {
            'technical_analysis': results,
            'timestamp': datetime.now().isoformat(),
            'timeframe': timeframe
        }
    
    def get_momentum_analysis(self, tickers: List[str]) -> Dict[str, Any]:
        """
        Analyze momentum for given tickers
        """
        momentum_scores = {}
        
        for ticker in tickers:
            hist_data = self.data_client.get_historical_bars([ticker], limit=60)
            
            if ticker in hist_data and not hist_data[ticker].empty:
                df = hist_data[ticker]
                df = self.data_client.calculate_technical_indicators(df)
                
                # Calculate momentum score
                score = 0
                weights = {
                    'price_momentum': 0.3,
                    'volume_momentum': 0.2,
                    'rsi_momentum': 0.2,
                    'macd_momentum': 0.3
                }
                
                # Price momentum
                if 'price_change_5d' in df and df['price_change_5d'].iloc[-1] > 0:
                    score += weights['price_momentum'] * min(df['price_change_5d'].iloc[-1] * 100, 1)
                
                # Volume momentum
                if 'volume_ratio' in df and df['volume_ratio'].iloc[-1] > 1.2:
                    score += weights['volume_momentum']
                
                # RSI momentum
                if 'rsi' in df:
                    rsi = df['rsi'].iloc[-1]
                    if 50 < rsi < 70:
                        score += weights['rsi_momentum'] * ((rsi - 50) / 20)
                
                # MACD momentum
                if 'macd' in df and 'macd_signal' in df:
                    if df['macd'].iloc[-1] > df['macd_signal'].iloc[-1]:
                        score += weights['macd_momentum']
                
                momentum_scores[ticker] = {
                    'score': round(score, 3),
                    'rank': None,  # Will be set after all scores calculated
                    'signal': 'BUY' if score > 0.6 else 'HOLD' if score > 0.3 else 'SELL'
                }
        
        # Rank tickers by momentum score
        sorted_tickers = sorted(momentum_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        for rank, (ticker, _) in enumerate(sorted_tickers, 1):
            momentum_scores[ticker]['rank'] = rank
        
        return {
            'momentum_analysis': momentum_scores,
            'timestamp': datetime.now().isoformat(),
            'top_movers': [ticker for ticker, _ in sorted_tickers[:3]]
        }
    
    def get_risk_analysis(self, tickers: List[str]) -> Dict[str, Any]:
        """
        Perform risk analysis for tickers
        """
        risk_metrics = {}
        
        for ticker in tickers:
            hist_data = self.data_client.get_historical_bars([ticker], limit=252)  # 1 year
            
            if ticker in hist_data and not hist_data[ticker].empty:
                df = hist_data[ticker]
                
                # Calculate returns
                returns = df['close'].pct_change().dropna()
                
                # Calculate risk metrics
                volatility = returns.std() * np.sqrt(252)  # Annualized
                var_95 = np.percentile(returns, 5)  # Value at Risk
                max_drawdown = self._calculate_max_drawdown(df['close'])
                sharpe_ratio = (returns.mean() * 252) / (returns.std() * np.sqrt(252)) if returns.std() > 0 else 0
                
                risk_metrics[ticker] = {
                    'volatility': round(volatility, 4),
                    'var_95': round(var_95, 4),
                    'max_drawdown': round(max_drawdown, 4),
                    'sharpe_ratio': round(sharpe_ratio, 2),
                    'risk_level': self._classify_risk_level(volatility),
                    'beta': self._calculate_beta(returns)  # Simplified beta
                }
        
        return {
            'risk_analysis': risk_metrics,
            'timestamp': datetime.now().isoformat(),
            'portfolio_risk': self._calculate_portfolio_risk(risk_metrics)
        }
    
    def _calculate_sentiment(self, df: pd.DataFrame) -> str:
        """Calculate market sentiment from technical indicators"""
        sentiment_score = 0
        
        if 'rsi' in df and not df['rsi'].isna().all():
            rsi = df['rsi'].iloc[-1]
            if rsi > 70:
                sentiment_score -= 1
            elif rsi < 30:
                sentiment_score += 1
            else:
                sentiment_score += 0.5 if rsi > 50 else -0.5
        
        if 'macd' in df and 'macd_signal' in df:
            if df['macd'].iloc[-1] > df['macd_signal'].iloc[-1]:
                sentiment_score += 1
            else:
                sentiment_score -= 1
        
        if 'close' in df and 'sma_50' in df:
            if df['close'].iloc[-1] > df['sma_50'].iloc[-1]:
                sentiment_score += 0.5
            else:
                sentiment_score -= 0.5
        
        if sentiment_score > 1:
            return "Bullish"
        elif sentiment_score < -1:
            return "Bearish"
        else:
            return "Neutral"
    
    def _identify_trend(self, df: pd.DataFrame) -> str:
        """Identify the current trend"""
        if len(df) < 20:
            return "Unknown"
        
        recent_prices = df['close'].tail(20)
        slope = np.polyfit(range(len(recent_prices)), recent_prices, 1)[0]
        
        if slope > 0.5:
            return "Strong Uptrend"
        elif slope > 0:
            return "Uptrend"
        elif slope < -0.5:
            return "Strong Downtrend"
        elif slope < 0:
            return "Downtrend"
        else:
            return "Sideways"
    
    def _find_support_resistance(self, df: pd.DataFrame, level_type: str) -> List[float]:
        """Find support or resistance levels"""
        if len(df) < 20:
            return []
        
        prices = df['close'].values
        levels = []
        
        if level_type == 'support':
            # Find local minima
            for i in range(1, len(prices) - 1):
                if prices[i] < prices[i-1] and prices[i] < prices[i+1]:
                    levels.append(float(prices[i]))
        else:
            # Find local maxima
            for i in range(1, len(prices) - 1):
                if prices[i] > prices[i-1] and prices[i] > prices[i+1]:
                    levels.append(float(prices[i]))
        
        # Return top 3 most significant levels
        return sorted(list(set(levels)))[-3:] if levels else []
    
    def _generate_recommendation(self, df: pd.DataFrame) -> str:
        """Generate trading recommendation based on analysis"""
        score = 0
        
        # Check RSI
        if 'rsi' in df and not df['rsi'].isna().all():
            rsi = df['rsi'].iloc[-1]
            if 30 < rsi < 70:
                score += 1 if rsi > 50 else -1
        
        # Check MACD
        if 'macd' in df and 'macd_signal' in df:
            if df['macd'].iloc[-1] > df['macd_signal'].iloc[-1]:
                score += 1
            else:
                score -= 1
        
        # Check moving averages
        if 'close' in df and 'sma_20' in df and 'sma_50' in df:
            close = df['close'].iloc[-1]
            if close > df['sma_20'].iloc[-1] > df['sma_50'].iloc[-1]:
                score += 2
            elif close < df['sma_20'].iloc[-1] < df['sma_50'].iloc[-1]:
                score -= 2
        
        if score >= 2:
            return "Strong Buy"
        elif score == 1:
            return "Buy"
        elif score == 0:
            return "Hold"
        elif score == -1:
            return "Sell"
        else:
            return "Strong Sell"
    
    def _generate_trading_signals(self, df: pd.DataFrame) -> Dict[str, str]:
        """Generate trading signals from technical indicators"""
        signals = {}
        
        # RSI signals
        if 'rsi' in df:
            rsi = df['rsi'].iloc[-1]
            if rsi > 70:
                signals['rsi'] = 'Overbought'
            elif rsi < 30:
                signals['rsi'] = 'Oversold'
            else:
                signals['rsi'] = 'Neutral'
        
        # MACD signals
        if 'macd' in df and 'macd_signal' in df:
            if df['macd'].iloc[-1] > df['macd_signal'].iloc[-1]:
                signals['macd'] = 'Bullish'
            else:
                signals['macd'] = 'Bearish'
        
        # Moving average signals
        if 'close' in df and 'sma_20' in df and 'sma_50' in df:
            if df['sma_20'].iloc[-1] > df['sma_50'].iloc[-1]:
                signals['ma_cross'] = 'Golden Cross'
            else:
                signals['ma_cross'] = 'Death Cross'
        
        # Bollinger Band signals
        if 'close' in df and 'bb_upper' in df and 'bb_lower' in df:
            close = df['close'].iloc[-1]
            if close > df['bb_upper'].iloc[-1]:
                signals['bollinger'] = 'Upper Band Breach'
            elif close < df['bb_lower'].iloc[-1]:
                signals['bollinger'] = 'Lower Band Breach'
            else:
                signals['bollinger'] = 'Within Bands'
        
        return signals
    
    def _identify_patterns(self, df: pd.DataFrame) -> List[str]:
        """Identify chart patterns (simplified)"""
        patterns = []
        
        if len(df) < 20:
            return patterns
        
        # Check for simple patterns
        recent_closes = df['close'].tail(10).values
        
        # Ascending triangle (simplified)
        if all(recent_closes[i] <= recent_closes[i+1] for i in range(len(recent_closes)-1)):
            patterns.append("Ascending Pattern")
        
        # Descending pattern
        elif all(recent_closes[i] >= recent_closes[i+1] for i in range(len(recent_closes)-1)):
            patterns.append("Descending Pattern")
        
        # Range bound
        elif max(recent_closes) - min(recent_closes) < df['close'].std() * 0.5:
            patterns.append("Range Bound")
        
        return patterns
    
    def _calculate_trend_strength(self, df: pd.DataFrame) -> float:
        """Calculate trend strength (0-1 scale)"""
        if len(df) < 20:
            return 0.5
        
        # Use ADX concept (simplified)
        recent_changes = df['close'].pct_change().tail(20)
        positive_changes = recent_changes[recent_changes > 0]
        negative_changes = recent_changes[recent_changes < 0]
        
        if len(positive_changes) > len(negative_changes) * 2:
            return min(0.9, len(positive_changes) / 20)
        elif len(negative_changes) > len(positive_changes) * 2:
            return max(0.1, 1 - len(negative_changes) / 20)
        else:
            return 0.5
    
    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        """Calculate maximum drawdown"""
        cumulative = (1 + prices.pct_change()).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return float(drawdown.min())
    
    def _calculate_beta(self, returns: pd.Series) -> float:
        """Calculate simplified beta (would normally compare to market index)"""
        # Simplified: use volatility as proxy
        return float(returns.std() * np.sqrt(252) / 0.15)  # Assume market vol of 15%
    
    def _classify_risk_level(self, volatility: float) -> str:
        """Classify risk level based on volatility"""
        if volatility < 0.15:
            return "Low"
        elif volatility < 0.25:
            return "Medium"
        elif volatility < 0.35:
            return "High"
        else:
            return "Very High"
    
    def _calculate_portfolio_risk(self, risk_metrics: Dict) -> Dict[str, Any]:
        """Calculate overall portfolio risk"""
        if not risk_metrics:
            return {"overall_risk": "Unknown"}
        
        avg_volatility = np.mean([m['volatility'] for m in risk_metrics.values()])
        avg_sharpe = np.mean([m['sharpe_ratio'] for m in risk_metrics.values()])
        
        return {
            'average_volatility': round(avg_volatility, 4),
            'average_sharpe_ratio': round(avg_sharpe, 2),
            'risk_level': self._classify_risk_level(avg_volatility),
            'diversification_benefit': 0.1  # Simplified
        }
    
    def _generate_default_analysis(self) -> Dict[str, Any]:
        """Generate default analysis when no data available"""
        return {
            'current_price': 100.0,
            'price_change_1d': 0,
            'price_change_5d': 0,
            'price_change_20d': 0,
            'volume_ratio': 1.0,
            'rsi': 50,
            'macd': 0,
            'bb_position': 0.5,
            'sentiment': 'Neutral',
            'trend': 'Unknown',
            'support_levels': [],
            'resistance_levels': [],
            'recommendation': 'Hold'
        }
    
    def _generate_summary(self, analysis: Dict) -> str:
        """Generate summary of analysis"""
        if not analysis:
            return "No analysis available"
        
        bullish_count = sum(1 for a in analysis.values() if a.get('sentiment') == 'Bullish')
        bearish_count = sum(1 for a in analysis.values() if a.get('sentiment') == 'Bearish')
        
        if bullish_count > bearish_count:
            return f"Overall market sentiment is bullish ({bullish_count}/{len(analysis)} positive)"
        elif bearish_count > bullish_count:
            return f"Overall market sentiment is bearish ({bearish_count}/{len(analysis)} negative)"
        else:
            return f"Overall market sentiment is neutral"