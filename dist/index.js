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
export { AlpacaDataProvider } from './data/AlpacaDataProvider.js';
export { AlpacaTradeExecutor } from './core/AlpacaTradeExecutor.js';
export { config, getConfig } from './config/index.js';
// Re-export all types
export * from './types/index.js';
// Export examples
export { runAlpacaExample } from './examples/alpaca-example.js';
// Example usage function
export async function runExampleBacktest() {
    const { BacktestEngine } = await import('./core/BacktestEngine.js');
    const { SimpleMovingAverageStrategy } = await import('./strategies/SimpleMovingAverageStrategy.js');
    const { YahooDataProvider } = await import('./data/YahooDataProvider.js');
    const { getConfig } = await import('./config/index.js');
    const config = getConfig();
    const engine = new BacktestEngine(config.backtesting.defaultConfig);
    const strategy = new SimpleMovingAverageStrategy(20, 50, ['AAPL', 'GOOGL']);
    const dataProvider = new YahooDataProvider();
    // Fetch data
    const marketData = new Map();
    for (const symbol of config.backtesting.defaultConfig.symbols) {
        const data = await dataProvider.getPriceData(symbol, config.backtesting.defaultConfig.startDate, config.backtesting.defaultConfig.endDate);
        marketData.set(symbol, data);
    }
    // Run backtest
    const result = await engine.runBacktest(strategy, marketData);
    console.log('Backtest Results:');
    console.log(`Total Return: ${(result.totalReturn * 100).toFixed(2)}%`);
    console.log(`Annualized Return: ${(result.annualizedReturn * 100).toFixed(2)}%`);
    console.log(`Max Drawdown: ${(result.maxDrawdown * 100).toFixed(2)}%`);
    console.log(`Sharpe Ratio: ${result.sharpeRatio.toFixed(2)}`);
    console.log(`Win Rate: ${(result.winRate * 100).toFixed(2)}%`);
    console.log(`Total Trades: ${result.totalTrades}`);
}
//# sourceMappingURL=index.js.map