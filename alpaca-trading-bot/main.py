#!/usr/bin/env python3
"""
Main orchestrator for Perplexity-Alpaca trading integration
"""

import asyncio
import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import signal
import json
from loguru import logger
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import config
from src.perplexity_client import (
    PerplexityFinanceClient, 
    QueryType,
    FinancialDataAggregator
)
from src.prompt_generator import CursorPromptGenerator, StrategyType
from src.data_handler import DataHandler
from src.strategy import StrategyManager, TradingSignal
from src.executor import OrderExecutor, RiskManager
from alpaca.data.timeframe import TimeFrame


class AlpacaTradingBot:
    """Main trading bot orchestrator"""
    
    def __init__(self, config_path: Optional[str] = None):
        # Load environment variables
        load_dotenv()
        
        # Validate configuration
        if not config.validate():
            logger.error("Invalid configuration - please check your .env file")
            sys.exit(1)
        
        # Initialize components
        self.perplexity = PerplexityFinanceClient(
            api_key=config.perplexity.api_key,
            timeout=config.perplexity.timeout
        )
        
        self.data_aggregator = FinancialDataAggregator(self.perplexity)
        
        self.prompt_generator = CursorPromptGenerator(
            output_dir="cursor_tasks"
        )
        
        self.data_handler = DataHandler(
            api_key=config.alpaca.api_key,
            secret_key=config.alpaca.secret_key,
            feed=config.alpaca.market_data_feed
        )
        
        self.strategy_manager = StrategyManager({
            "strategies": {
                "momentum": {"enabled": True},
                "mean_reversion": {"enabled": True},
                "sentiment": {"enabled": True}
            },
            "strategy_weights": {
                "momentum": 0.3,
                "mean_reversion": 0.3,
                "sentiment": 0.4
            }
        })
        
        self.executor = OrderExecutor(
            api_key=config.alpaca.api_key,
            secret_key=config.alpaca.secret_key,
            paper=config.alpaca.paper_trading
        )
        
        self.risk_manager = RiskManager({
            "max_position_size": config.trading.max_position_size,
            "max_daily_loss": 0.02,
            "max_drawdown": 0.1,
            "max_positions": 5,
            "min_cash_reserve": config.trading.min_cash_reserve
        })
        
        # Trading state
        self.is_running = False
        self.watchlist = []
        self.positions = {}
        self.last_analysis_time = {}
        self.analysis_interval = timedelta(minutes=15)
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        
        log_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
        
        # Console logging
        logger.add(
            sys.stdout,
            format=log_format,
            level=config.system.log_level,
            colorize=True
        )
        
        # File logging
        if config.system.log_file:
            logger.add(
                config.system.log_file,
                format=log_format,
                level=config.system.log_level,
                rotation="500 MB",
                retention="7 days"
            )
    
    async def analyze_and_trade(self, symbols: List[str]):
        """Main analysis and trading loop for given symbols"""
        
        logger.info(f"Starting analysis for {symbols}")
        
        for symbol in symbols:
            try:
                # Check if we need to analyze (rate limiting)
                if symbol in self.last_analysis_time:
                    time_since_last = datetime.now() - self.last_analysis_time[symbol]
                    if time_since_last < self.analysis_interval:
                        logger.debug(f"Skipping {symbol} - analyzed {time_since_last.seconds}s ago")
                        continue
                
                # 1. Fetch comprehensive financial data from Perplexity
                logger.info(f"Fetching financial data for {symbol}")
                
                financial_analysis = await self.perplexity.get_comprehensive_analysis(
                    [symbol],
                    include_types=[
                        QueryType.MARKET_NEWS,
                        QueryType.SENTIMENT,
                        QueryType.FUNDAMENTALS
                    ]
                )
                
                # 2. Get market data from Alpaca
                logger.info(f"Fetching market data for {symbol}")
                
                market_data = self.data_handler.get_historical_bars(
                    symbols=[symbol],
                    timeframe=TimeFrame.Hour,
                    start=datetime.now() - timedelta(days=30)
                )
                
                if market_data.empty:
                    logger.warning(f"No market data available for {symbol}")
                    continue
                
                # Calculate indicators
                market_data = self.data_handler.calculate_indicators(
                    market_data,
                    indicators=['SMA_20', 'SMA_50', 'RSI', 'MACD', 'BB', 'ATR', 'VWAP']
                )
                
                # 3. Extract sentiment from Perplexity analysis
                sentiment_data = self._extract_sentiment(financial_analysis)
                
                # 4. Get trading signals from strategies
                signal = self.strategy_manager.get_combined_signal(
                    symbol=symbol,
                    market_data=market_data[market_data.index.get_level_values('symbol') == symbol] if 'symbol' in market_data.index.names else market_data,
                    sentiment_data=sentiment_data
                )
                
                if signal:
                    logger.info(f"Signal generated for {symbol}: {signal.signal.name} (confidence: {signal.confidence:.2f})")
                    
                    # 5. Validate with risk manager
                    account = self.executor.trading_client.get_account()
                    portfolio_value = float(account.portfolio_value)
                    cash_available = float(account.cash)
                    current_positions = self.executor.get_positions()
                    
                    is_valid, violations = self.risk_manager.validate_trade(
                        signal=signal,
                        portfolio_value=portfolio_value,
                        cash_available=cash_available,
                        current_positions=current_positions
                    )
                    
                    if is_valid:
                        # 6. Execute trade
                        order = self.executor.execute_signal(signal)
                        
                        if order:
                            logger.success(f"✅ Order placed for {symbol}: {order.id}")
                            self.positions[symbol] = {
                                "order_id": order.id,
                                "signal": signal,
                                "entry_time": datetime.now()
                            }
                    else:
                        logger.warning(f"❌ Trade rejected due to risk violations: {violations}")
                else:
                    logger.info(f"No trading signal for {symbol}")
                
                # Update last analysis time
                self.last_analysis_time[symbol] = datetime.now()
                
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
                continue
    
    def _extract_sentiment(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract sentiment data from Perplexity analysis"""
        
        sentiment_data = {
            "sentiment_score": 0.5,  # Neutral default
            "news_sentiment": "Neutral",
            "social_mentions_trend": 1.0
        }
        
        try:
            # Parse sentiment from analysis
            if "analysis" in analysis:
                for query_type, content in analysis["analysis"].items():
                    if content and "content" in content:
                        text = content["content"].lower()
                        
                        # Simple sentiment extraction (in practice, use NLP)
                        bullish_words = ["bullish", "positive", "strong", "growth", "beat", "upgrade"]
                        bearish_words = ["bearish", "negative", "weak", "decline", "miss", "downgrade"]
                        
                        bullish_count = sum(1 for word in bullish_words if word in text)
                        bearish_count = sum(1 for word in bearish_words if word in text)
                        
                        if bullish_count > bearish_count:
                            sentiment_data["sentiment_score"] = min(0.5 + (bullish_count * 0.1), 1.0)
                            sentiment_data["news_sentiment"] = "Bullish"
                        elif bearish_count > bullish_count:
                            sentiment_data["sentiment_score"] = max(0.5 - (bearish_count * 0.1), 0.0)
                            sentiment_data["news_sentiment"] = "Bearish"
        
        except Exception as e:
            logger.warning(f"Error extracting sentiment: {e}")
        
        return sentiment_data
    
    async def monitor_positions(self):
        """Monitor existing positions for exit signals"""
        
        positions = self.executor.get_positions()
        
        for position in positions:
            symbol = position.symbol
            
            try:
                # Get current price
                market_data = self.data_handler.get_historical_bars(
                    symbols=[symbol],
                    timeframe=TimeFrame.Minute,
                    start=datetime.now() - timedelta(minutes=5)
                )
                
                if not market_data.empty:
                    current_price = market_data['close'].iloc[-1]
                    
                    # Check if we should exit
                    position_data = self.positions.get(symbol, {})
                    
                    if position_data and "signal" in position_data:
                        signal = position_data["signal"]
                        
                        # Check stop loss and take profit
                        if current_price <= signal.stop_loss or current_price >= signal.take_profit:
                            logger.info(f"Exit signal for {symbol} at ${current_price:.2f}")
                            self.executor.close_position(symbol)
                            del self.positions[symbol]
                
            except Exception as e:
                logger.error(f"Error monitoring position {symbol}: {e}")
    
    async def run(self, symbols: List[str], interval_minutes: int = 5):
        """Main bot execution loop"""
        
        self.watchlist = symbols
        self.is_running = True
        
        logger.info(f"🚀 Starting trading bot for {symbols}")
        logger.info(f"Paper trading: {config.alpaca.paper_trading}")
        logger.info(f"Analysis interval: {interval_minutes} minutes")
        
        # Start data streaming in background
        asyncio.create_task(self._start_data_stream())
        
        while self.is_running:
            try:
                # Check if market is open
                clock = self.executor.trading_client.get_clock()
                
                if clock.is_open:
                    # Update risk metrics
                    account = self.executor.trading_client.get_account()
                    portfolio_value = float(account.portfolio_value)
                    daily_pnl = float(account.equity) - float(account.last_equity)
                    
                    self.risk_manager.update_portfolio_metrics(portfolio_value, daily_pnl)
                    
                    # Check if we should stop trading
                    if self.risk_manager.should_stop_trading():
                        logger.warning("Risk limits reached - stopping trading for today")
                        await self.stop()
                        break
                    
                    # Analyze and trade
                    await self.analyze_and_trade(symbols)
                    
                    # Monitor existing positions
                    await self.monitor_positions()
                    
                    # Update order status
                    self.executor.update_order_status()
                    
                else:
                    logger.info("Market is closed - waiting...")
                
                # Wait for next iteration
                await asyncio.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
                await self.stop()
                break
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _start_data_stream(self):
        """Start real-time data streaming"""
        
        try:
            # Subscribe to data streams
            await self.data_handler.stream_bars(
                self.watchlist,
                callback=self._handle_bar_update
            )
            
            # Start streaming
            await self.data_handler.start_streaming()
            
        except Exception as e:
            logger.error(f"Error starting data stream: {e}")
    
    async def _handle_bar_update(self, bar):
        """Handle real-time bar updates"""
        logger.debug(f"Bar update: {bar.symbol} - ${bar.close:.2f}")
    
    async def stop(self):
        """Stop the trading bot"""
        
        logger.info("Stopping trading bot...")
        self.is_running = False
        
        # Stop data streaming
        await self.data_handler.stop_streaming()
        
        # Cancel all open orders
        self.executor.cancel_all_orders()
        
        # Generate reports
        self.generate_reports()
    
    def generate_reports(self):
        """Generate trading reports"""
        
        logger.info("Generating reports...")
        
        # Execution report
        execution_report = self.executor.get_execution_report()
        logger.info(f"Execution Report: {json.dumps(execution_report, indent=2)}")
        
        # Risk report
        risk_report = self.risk_manager.get_risk_report()
        logger.info(f"Risk Report: {json.dumps(risk_report, indent=2)}")
        
        # Strategy performance
        strategy_report = self.strategy_manager.get_performance_report()
        logger.info(f"Strategy Report: {json.dumps(strategy_report, indent=2)}")
        
        # Data handler statistics
        data_stats = self.data_handler.get_statistics()
        logger.info(f"Data Statistics: {json.dumps(data_stats, indent=2)}")
    
    def generate_cursor_prompt(
        self,
        symbols: List[str],
        strategy_type: StrategyType
    ):
        """Generate a Cursor background agent prompt"""
        
        logger.info(f"Generating Cursor prompt for {strategy_type.value} strategy")
        
        try:
            # Fetch comprehensive data
            loop = asyncio.get_event_loop()
            financial_data = loop.run_until_complete(
                self.perplexity.get_comprehensive_analysis(symbols)
            )
            
            # Generate and save prompt
            prompt_file = self.prompt_generator.generate_and_save(
                financial_data=financial_data,
                strategy_type=strategy_type,
                tickers=symbols,
                additional_requirements="Focus on risk-adjusted returns and implement comprehensive backtesting."
            )
            
            logger.success(f"✅ Cursor prompt saved to: {prompt_file}")
            logger.info("\nNext steps:")
            logger.info("1. Open Cursor and press Ctrl+Shift+B (or ⌘B on Mac)")
            logger.info("2. Click 'New Background Agent'")
            logger.info(f"3. Copy the contents of {prompt_file} into the agent prompt")
            logger.info("4. The agent will create a new branch and implement the strategy")
            
            return prompt_file
            
        except Exception as e:
            logger.error(f"Error generating Cursor prompt: {e}")
            return None


def main():
    """Main entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Alpaca Trading Bot with Perplexity Integration")
    parser.add_argument(
        "--symbols",
        type=str,
        nargs="+",
        default=["AAPL", "MSFT", "GOOGL"],
        help="Stock symbols to trade"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["trade", "generate", "backtest"],
        default="trade",
        help="Execution mode"
    )
    parser.add_argument(
        "--strategy",
        type=str,
        choices=["momentum", "mean_reversion", "sentiment", "pairs_trading"],
        default="momentum",
        help="Trading strategy for prompt generation"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Analysis interval in minutes"
    )
    
    args = parser.parse_args()
    
    # Create bot instance
    bot = AlpacaTradingBot()
    
    if args.mode == "generate":
        # Generate Cursor prompt
        strategy_map = {
            "momentum": StrategyType.MOMENTUM,
            "mean_reversion": StrategyType.MEAN_REVERSION,
            "sentiment": StrategyType.SENTIMENT_BASED,
            "pairs_trading": StrategyType.PAIRS_TRADING
        }
        
        bot.generate_cursor_prompt(
            symbols=args.symbols,
            strategy_type=strategy_map[args.strategy]
        )
        
    elif args.mode == "trade":
        # Run trading bot
        loop = asyncio.get_event_loop()
        
        # Handle signals
        def signal_handler(sig, frame):
            logger.info("Shutdown signal received")
            loop.create_task(bot.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            loop.run_until_complete(
                bot.run(
                    symbols=args.symbols,
                    interval_minutes=args.interval
                )
            )
        finally:
            loop.close()
    
    else:
        logger.info("Backtest mode not yet implemented")


if __name__ == "__main__":
    main()