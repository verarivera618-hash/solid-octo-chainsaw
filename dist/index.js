/**
 * Main entry point for the backtesting framework
 * Exports all public APIs and provides high-level usage examples
 */
export { BacktestEngine } from './core/BacktestEngine.js';
export { Portfolio } from './core/Portfolio.js';
export { TradeExecutor } from './core/TradeExecutor.js';
export { AlpacaTradeExecutor } from './core/AlpacaTradeExecutor.js';
export { PerformanceAnalyzer } from './analysis/PerformanceAnalyzer.js';
export { SimpleMovingAverageStrategy } from './strategies/SimpleMovingAverageStrategy.js';
export { YahooDataProvider } from './data/YahooDataProvider.js';
export { AlpacaDataProvider } from './data/AlpacaDataProvider.js';
export { config, getConfig } from './config/index.js';
// Re-export all types
export * from './types/index.js';
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
// Example function for Alpaca live trading
export async function runAlpacaExample() {
    const { AlpacaDataProvider } = await import('./data/AlpacaDataProvider.js');
    const { AlpacaTradeExecutor } = await import('./core/AlpacaTradeExecutor.js');
    const { SimpleMovingAverageStrategy } = await import('./strategies/SimpleMovingAverageStrategy.js');
    const { getConfig } = await import('./config/index.js');
    const config = getConfig();
    // Check if Alpaca credentials are configured
    if (!config.alpaca.apiKey || !config.alpaca.secretKey) {
        console.error('Alpaca credentials not configured. Please set ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables.');
        return;
    }
    // Initialize Alpaca components
    const dataProvider = new AlpacaDataProvider({
        apiKey: config.alpaca.apiKey,
        secretKey: config.alpaca.secretKey,
        baseUrl: config.alpaca.baseUrl,
        dataUrl: config.alpaca.dataUrl,
    });
    const tradeExecutor = new AlpacaTradeExecutor({
        apiKey: config.alpaca.apiKey,
        secretKey: config.alpaca.secretKey,
        baseUrl: config.alpaca.baseUrl,
        paperTrading: config.alpaca.paperTrading,
    });
    // Check if Alpaca API is available
    const isAvailable = await dataProvider.isAvailable();
    if (!isAvailable) {
        console.error('Alpaca API is not available. Please check your credentials and network connection.');
        return;
    }
    console.log('Alpaca API is available!');
    // Get account information
    try {
        const account = await tradeExecutor.getAccount();
        console.log(`Account Status: ${account.status}`);
        console.log(`Buying Power: $${account.buying_power}`);
        console.log(`Paper Trading: ${config.alpaca.paperTrading ? 'Yes' : 'No'}`);
    }
    catch (error) {
        console.error('Error fetching account info:', error);
        return;
    }
    // Get market status
    const marketStatus = await dataProvider.getMarketStatus();
    console.log(`Market is ${marketStatus.isOpen ? 'OPEN' : 'CLOSED'}`);
    if (marketStatus.nextOpen) {
        console.log(`Next open: ${marketStatus.nextOpen.toISOString()}`);
    }
    // Example: Fetch recent data for AAPL
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 30); // Last 30 days
    try {
        const data = await dataProvider.getPriceData('AAPL', startDate, endDate);
        console.log(`Fetched ${data.length} data points for AAPL`);
        if (data.length > 0) {
            const latest = data[data.length - 1];
            console.log(`Latest AAPL price: $${latest.close} (${latest.timestamp.toISOString()})`);
        }
    }
    catch (error) {
        console.error('Error fetching data:', error);
    }
    // Example: Get current quote
    try {
        const quote = await dataProvider.getQuote('AAPL');
        if (quote) {
            console.log(`Current AAPL quote - Bid: $${quote.bid}, Ask: $${quote.ask}, Last: $${quote.last}`);
        }
    }
    catch (error) {
        console.error('Error fetching quote:', error);
    }
    console.log('\nAlpaca integration example completed successfully!');
    console.log('To enable live trading, set TRADING_ENABLED=true in your environment variables.');
}
//# sourceMappingURL=index.js.map