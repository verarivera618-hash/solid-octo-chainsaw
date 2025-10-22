/**
 * Core backtesting engine - the heart of the system
 * Handles strategy execution, trade simulation, and performance calculation
 */
import { Portfolio } from './Portfolio.js';
import { TradeExecutor } from './TradeExecutor.js';
import { PerformanceAnalyzer } from '../analysis/PerformanceAnalyzer.js';
export class BacktestEngine {
    portfolio;
    tradeExecutor;
    performanceAnalyzer;
    constructor(config) {
        this.portfolio = new Portfolio(config.initialCapital);
        this.tradeExecutor = new TradeExecutor(config.commission, config.slippage);
        this.performanceAnalyzer = new PerformanceAnalyzer();
    }
    /**
     * Execute backtest with given strategy and market data
     */
    async runBacktest(strategy, marketData) {
        if (!strategy.validate()) {
            throw new Error(`Invalid strategy: ${strategy.name}`);
        }
        // Get all unique timestamps across all symbols
        const allTimestamps = this.getAllTimestamps(marketData);
        const trades = [];
        // Process each timestamp
        for (const timestamp of allTimestamps) {
            const currentData = this.getDataAtTimestamp(marketData, timestamp);
            // Generate signals for all symbols at this timestamp
            const signals = strategy.generateSignals(currentData);
            // Execute trades based on signals
            for (const signal of signals) {
                if (signal.action !== 'hold') {
                    const trade = await this.tradeExecutor.executeTrade(signal, this.portfolio.getPosition(signal.symbol), this.portfolio.getCash());
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
    getAllTimestamps(marketData) {
        const timestamps = new Set();
        for (const data of marketData.values()) {
            for (const price of data) {
                timestamps.add(price.timestamp.getTime());
            }
        }
        return Array.from(timestamps)
            .map(time => new Date(time))
            .sort((a, b) => a.getTime() - b.getTime());
    }
    getDataAtTimestamp(marketData, timestamp) {
        const result = [];
        for (const [, data] of marketData.entries()) {
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
    getPortfolio() {
        return this.portfolio;
    }
}
//# sourceMappingURL=BacktestEngine.js.map