"""
Perplexity-Alpaca Trading Integration - Main Orchestrator
Combines financial insights from Perplexity with Alpaca trading automation
"""

import os
import sys
import asyncio
import argparse
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from alpaca.data.timeframe import TimeFrame

from src.config import config
from src.perplexity_client import PerplexityFinanceClient
from src.prompt_generator import PromptGenerator
from src.data_handler import AlpacaDataHandler
from src.strategy import get_strategy
from src.executor import OrderExecutor


# Setup logging
def setup_logging(log_level: str = "INFO"):
    """Configure logging"""
    os.makedirs("logs", exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"logs/trading_{datetime.now().strftime('%Y%m%d')}.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )


logger = logging.getLogger(__name__)


class PerplexityAlpacaIntegration:
    """
    Main integration class that orchestrates:
    1. Financial data retrieval from Perplexity
    2. Prompt generation for Cursor background agents
    3. Alpaca trading automation
    """
    
    def __init__(
        self,
        perplexity_key: Optional[str] = None,
        alpaca_key: Optional[str] = None,
        alpaca_secret: Optional[str] = None
    ):
        self.perplexity_client = PerplexityFinanceClient(perplexity_key)
        self.prompt_generator = PromptGenerator()
        self.data_handler = AlpacaDataHandler(alpaca_key, alpaca_secret)
        self.executor = OrderExecutor(alpaca_key, alpaca_secret)
        
        logger.info("PerplexityAlpacaIntegration initialized")
    
    def analyze_and_generate_task(
        self,
        tickers: List[str],
        strategy_type: str = "momentum",
        include_sec: bool = True,
        include_news: bool = True,
        include_earnings: bool = False,
        include_sector: bool = False,
        custom_instructions: Optional[str] = None
    ) -> str:
        """
        Complete pipeline: Fetch data → Analyze → Generate Cursor prompt
        
        Args:
            tickers: List of stock symbols
            strategy_type: Type of trading strategy
            include_sec: Fetch SEC filings analysis
            include_news: Fetch market news
            include_earnings: Fetch earnings analysis
            include_sector: Fetch sector analysis
            custom_instructions: Additional requirements
        
        Returns:
            Path to generated prompt file
        """
        logger.info(f"Starting analysis for {tickers} with {strategy_type} strategy")
        
        # Fetch financial insights
        sec_insights = None
        news_insights = None
        earnings_insights = None
        sector_insights = None
        
        if include_sec:
            logger.info("Fetching SEC filings analysis...")
            try:
                sec_insights = self.perplexity_client.get_sec_filings_analysis(
                    tickers=tickers,
                    filing_types=["10-Q", "10-K", "8-K"]
                )
                logger.info(f"SEC analysis completed ({len(sec_insights.sources)} sources)")
            except Exception as e:
                logger.warning(f"SEC analysis failed: {e}")
        
        if include_news:
            logger.info("Fetching market news and sentiment...")
            try:
                news_insights = self.perplexity_client.get_market_news(
                    tickers=tickers,
                    include_sentiment=True
                )
                logger.info(f"News analysis completed ({len(news_insights.sources)} sources)")
            except Exception as e:
                logger.warning(f"News analysis failed: {e}")
        
        if include_earnings:
            logger.info("Fetching earnings analysis...")
            try:
                earnings_insights = self.perplexity_client.get_earnings_analysis(
                    tickers=tickers,
                    include_transcripts=True
                )
                logger.info("Earnings analysis completed")
            except Exception as e:
                logger.warning(f"Earnings analysis failed: {e}")
        
        if include_sector and tickers:
            logger.info("Fetching sector analysis...")
            try:
                # Determine sector from first ticker (simplified)
                sector_insights = self.perplexity_client.get_sector_analysis(
                    sector="technology",  # Could be auto-detected
                    key_tickers=tickers
                )
                logger.info("Sector analysis completed")
            except Exception as e:
                logger.warning(f"Sector analysis failed: {e}")
        
        # Fetch recent price data from Alpaca
        logger.info("Fetching historical price data from Alpaca...")
        try:
            bars = self.data_handler.get_historical_bars(
                symbols=tickers,
                timeframe=TimeFrame.Day,
                start=datetime.now() - timedelta(days=30)
            )
            price_summary = self.data_handler.format_price_data_summary(tickers)
            logger.info(f"Price data fetched for {len(bars)} symbols")
        except Exception as e:
            logger.warning(f"Price data fetch failed: {e}")
            price_summary = None
        
        # Generate Cursor prompt
        logger.info("Generating Cursor background agent prompt...")
        cursor_prompt = self.prompt_generator.generate_trading_strategy_prompt(
            sec_insights=sec_insights,
            news_insights=news_insights,
            earnings_insights=earnings_insights,
            sector_insights=sector_insights,
            price_data_summary=price_summary,
            strategy_type=strategy_type,
            tickers=tickers,
            custom_instructions=custom_instructions
        )
        
        logger.info(f"✅ Cursor prompt generated: {cursor_prompt.file_path}")
        
        # Print next steps
        print("\n" + "="*80)
        print("🎯 CURSOR BACKGROUND AGENT PROMPT GENERATED")
        print("="*80)
        print(f"\n📄 Prompt file: {cursor_prompt.file_path}")
        print(f"📊 Strategy: {cursor_prompt.title}")
        print(f"📈 Tickers: {', '.join(cursor_prompt.tickers)}")
        print(f"⏰ Generated: {cursor_prompt.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n" + "="*80)
        print("NEXT STEPS:")
        print("="*80)
        print("1. Open Cursor and press Ctrl+Shift+B (or ⌘B on Mac)")
        print("2. Click 'New Background Agent'")
        print(f"3. Copy the contents of {cursor_prompt.file_path}")
        print("4. The agent will create a new branch and implement the strategy")
        print("5. Review, test, and merge the implementation")
        print("="*80 + "\n")
        
        return cursor_prompt.file_path
    
    async def run_live_strategy(
        self,
        tickers: List[str],
        strategy_type: str = "momentum",
        dry_run: bool = True
    ):
        """
        Run live trading strategy (use with caution!)
        
        Args:
            tickers: List of symbols to trade
            strategy_type: Type of strategy to use
            dry_run: If True, only simulate trades
        """
        logger.info(f"Starting live strategy: {strategy_type}")
        logger.info(f"Tickers: {tickers}")
        logger.info(f"Dry run: {dry_run}")
        
        if not dry_run:
            response = input("\n⚠️  WARNING: Live trading enabled! Type 'CONFIRM' to proceed: ")
            if response != "CONFIRM":
                logger.info("Live trading cancelled by user")
                return
        
        # Get account info
        account = self.executor.get_account()
        logger.info(f"Account equity: ${account['equity']:.2f}")
        
        # Load strategy
        strategy = get_strategy(strategy_type)
        
        # Fetch initial data and calculate indicators
        bars_dict = self.data_handler.get_historical_bars(
            symbols=tickers,
            timeframe=TimeFrame.Minute,
            start=datetime.now() - timedelta(hours=2),
            limit=200
        )
        
        for symbol in tickers:
            if symbol in bars_dict:
                df = self.data_handler.calculate_indicators(
                    symbol,
                    indicators=['SMA_20', 'SMA_50', 'RSI', 'MACD', 'BBANDS', 'Volume_SMA']
                )
                logger.info(f"Indicators calculated for {symbol}")
        
        # Define callback for real-time bars
        async def on_bar_update(bar):
            symbol = bar.symbol
            logger.debug(f"Bar update: {symbol} @ ${bar.close}")
            
            # Update cached data
            cached_df = self.data_handler.get_cached_bars(symbol)
            if cached_df is not None and len(cached_df) > 50:
                # Recalculate indicators
                df = self.data_handler.calculate_indicators(symbol)
                
                # Get trading signal
                signal = strategy.analyze(symbol, df)
                
                if signal.action != 'HOLD' and signal.strength >= 0.6:
                    logger.info(f"🎯 Signal: {signal.action} {symbol} (strength: {signal.strength:.2f})")
                    logger.info(f"   Reason: {signal.reason}")
                    
                    if not dry_run:
                        # Execute trade
                        try:
                            order = self.executor.submit_signal_order(
                                signal=signal,
                                account_value=account['equity'],
                                use_bracket=True
                            )
                            if order:
                                logger.info(f"✅ Order submitted: {order.id}")
                        except Exception as e:
                            logger.error(f"❌ Order failed: {e}")
                    else:
                        logger.info("   [DRY RUN - No order submitted]")
        
        # Start streaming
        logger.info("Starting real-time data stream...")
        await self.data_handler.stream_bars(tickers, callback=on_bar_update)
        
        # Run the stream
        try:
            await self.data_handler.start_streaming()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            await self.data_handler.stop_streaming()
    
    def generate_simple_task(self, description: str, context: Optional[str] = None) -> str:
        """Generate a simple custom task prompt"""
        cursor_prompt = self.prompt_generator.generate_simple_prompt(description, context)
        logger.info(f"Simple prompt generated: {cursor_prompt.file_path}")
        return cursor_prompt.file_path


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Perplexity-Alpaca Trading Integration"
    )
    
    parser.add_argument(
        'mode',
        choices=['analyze', 'trade', 'test'],
        help='Operation mode'
    )
    
    parser.add_argument(
        '--tickers',
        nargs='+',
        required=True,
        help='Stock symbols to analyze/trade'
    )
    
    parser.add_argument(
        '--strategy',
        default='momentum',
        choices=['momentum', 'mean_reversion', 'breakout'],
        help='Trading strategy type'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate trades without execution (for trade mode)'
    )
    
    parser.add_argument(
        '--no-sec',
        action='store_true',
        help='Skip SEC filings analysis'
    )
    
    parser.add_argument(
        '--no-news',
        action='store_true',
        help='Skip market news analysis'
    )
    
    parser.add_argument(
        '--include-earnings',
        action='store_true',
        help='Include earnings analysis'
    )
    
    parser.add_argument(
        '--include-sector',
        action='store_true',
        help='Include sector analysis'
    )
    
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Validate config
    if not config.validate():
        logger.error("Configuration validation failed")
        sys.exit(1)
    
    # Initialize integration
    integration = PerplexityAlpacaIntegration()
    
    try:
        if args.mode == 'analyze':
            # Generate Cursor prompt
            integration.analyze_and_generate_task(
                tickers=args.tickers,
                strategy_type=args.strategy,
                include_sec=not args.no_sec,
                include_news=not args.no_news,
                include_earnings=args.include_earnings,
                include_sector=args.include_sector
            )
        
        elif args.mode == 'trade':
            # Run live trading
            asyncio.run(integration.run_live_strategy(
                tickers=args.tickers,
                strategy_type=args.strategy,
                dry_run=args.dry_run
            ))
        
        elif args.mode == 'test':
            # Test mode - validate connections
            logger.info("Testing connections...")
            
            # Test Alpaca connection
            account = integration.executor.get_account()
            logger.info(f"✅ Alpaca connected - Account equity: ${account['equity']:.2f}")
            
            # Test data fetch
            bars = integration.data_handler.get_historical_bars(
                symbols=args.tickers[:1],
                timeframe=TimeFrame.Day,
                limit=10
            )
            logger.info(f"✅ Data fetch successful - {len(bars[args.tickers[0]])} bars")
            
            # Test Perplexity (optional - costs money)
            # insights = integration.perplexity_client.get_market_news(args.tickers[:1])
            # logger.info(f"✅ Perplexity connected")
            
            logger.info("✅ All tests passed!")
    
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
