/**
 * Main entry point for the backtesting framework
 * Exports all public APIs and provides high-level usage examples
 */
export { BacktestEngine } from './core/BacktestEngine.js';
export { Portfolio } from './core/Portfolio.js';
export { TradeExecutor } from './core/TradeExecutor.js';
export { PerformanceAnalyzer } from './analysis/PerformanceAnalyzer.js';
export { SimpleMovingAverageStrategy } from './strategies/SimpleMovingAverageStrategy.js';
export { YahooDataProvider } from './data/YahooDataProvider.js';
export { config, getConfig } from './config/index.js';
export * from './types/index.js';
export declare function runExampleBacktest(): Promise<void>;
//# sourceMappingURL=index.d.ts.map