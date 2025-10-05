/**
 * Core backtesting engine - the heart of the system
 * Handles strategy execution, trade simulation, and performance calculation
 */

import { BacktestConfig, BacktestResult, Strategy, Trade, Position, PriceData } from '../types/index.js';
import { Portfolio } from './Portfolio.js';
import { TradeExecutor } from './TradeExecutor.js';
import { PerformanceAnalyzer } from '../analysis/PerformanceAnalyzer.js';

export class BacktestEngine {
  private readonly config: BacktestConfig;
  private readonly portfolio: Portfolio;
  private readonly tradeExecutor: TradeExecutor;
  private readonly performanceAnalyzer: PerformanceAnalyzer;

  constructor(config: BacktestConfig) {
    this.config = config;
    this.portfolio = new Portfolio(config.initialCapital);
    this.tradeExecutor = new TradeExecutor(config.commission, config.slippage);
    this.performanceAnalyzer = new PerformanceAnalyzer();
  }

  /**
   * Execute backtest with given strategy and market data
   */
  async runBacktest(strategy: Strategy, marketData: Map<string, PriceData[]>): Promise<BacktestResult> {
    if (!strategy.validate()) {
      throw new Error(`Invalid strategy: ${strategy.name}`);
    }

    // Get all unique timestamps across all symbols
    const allTimestamps = this.getAllTimestamps(marketData);
    const trades: Trade[] = [];

    // Process each timestamp
    for (const timestamp of allTimestamps) {
      const currentData = this.getDataAtTimestamp(marketData, timestamp);
      
      // Generate signals for all symbols at this timestamp
      const signals = strategy.generateSignals(currentData);
      
      // Execute trades based on signals
      for (const signal of signals) {
        if (signal.action !== 'hold') {
          const trade = await this.tradeExecutor.executeTrade(
            signal,
            this.portfolio.getPosition(signal.symbol),
            this.portfolio.getCash()
          );
          
          if (trade) {
            trades.push(trade);
            this.portfolio.updatePosition(trade);
          }
        }
      }

      // Update portfolio value
      this.portfolio.updateValue(currentData);
    }

    // Calculate performance metrics
    return this.performanceAnalyzer.analyze(trades, this.portfolio.getEquityCurve());
  }

  private getAllTimestamps(marketData: Map<string, PriceData[]>): Date[] {
    const timestamps = new Set<number>();
    
    for (const data of marketData.values()) {
      for (const price of data) {
        timestamps.add(price.timestamp.getTime());
      }
    }
    
    return Array.from(timestamps)
      .map(time => new Date(time))
      .sort((a, b) => a.getTime() - b.getTime());
  }

  private getDataAtTimestamp(marketData: Map<string, PriceData[]>, timestamp: Date): PriceData[] {
    const result: PriceData[] = [];
    
    for (const [symbol, data] of marketData.entries()) {
      const priceAtTime = data.find(p => p.timestamp.getTime() === timestamp.getTime());
      if (priceAtTime) {
        result.push(priceAtTime);
      }
    }
    
    return result;
  }

  /**
   * Get current portfolio state
   */
  getPortfolio(): Portfolio {
    return this.portfolio;
  }
}