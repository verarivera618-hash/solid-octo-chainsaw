/**
 * Core backtesting engine - the heart of the system
 * Handles strategy execution, trade simulation, and performance calculation
 */
import type { BacktestConfig, BacktestResult, Strategy, /* Position, */ PriceData } from '../types/index.js';
import { Portfolio } from './Portfolio.js';
export declare class BacktestEngine {
    private readonly portfolio;
    private readonly tradeExecutor;
    private readonly performanceAnalyzer;
    constructor(config: BacktestConfig);
    /**
     * Execute backtest with given strategy and market data
     */
    runBacktest(strategy: Strategy, marketData: Map<string, PriceData[]>): Promise<BacktestResult>;
    private getAllTimestamps;
    private getDataAtTimestamp;
    /**
     * Get current portfolio state
     */
    getPortfolio(): Portfolio;
}
//# sourceMappingURL=BacktestEngine.d.ts.map