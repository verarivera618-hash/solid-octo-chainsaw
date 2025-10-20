/**
 * Example of running the backtesting system with Alpaca integration
 * This example shows both backtesting with real data and live trading capabilities
 */
import { BacktestEngine } from '../core/BacktestEngine.js';
import { SimpleMovingAverageStrategy } from '../strategies/SimpleMovingAverageStrategy.js';
import { AlpacaDataProvider } from '../data/AlpacaDataProvider.js';
import { AlpacaTradeExecutor } from '../core/AlpacaTradeExecutor.js';
import { getConfig } from '../config/index.js';
export async function runAlpacaExample() {
    const config = getConfig();
    // Check if Alpaca credentials are configured
    if (!config.alpaca.apiKey || !config.alpaca.secretKey) {
        console.error('❌ Alpaca credentials not configured!');
        console.log('Please set the following environment variables:');
        console.log('- ALPACA_API_KEY=your_api_key');
        console.log('- ALPACA_SECRET_KEY=your_secret_key');
        console.log('- ALPACA_BASE_URL=https://paper-api.alpaca.markets (for paper trading)');
        console.log('\nYou can get your API keys from: https://app.alpaca.markets/paper/dashboard/overview');
        return;
    }
    console.log('🚀 Starting Alpaca integration example...');
    console.log(`📊 Using ${config.alpaca.baseUrl.includes('paper') ? 'PAPER' : 'LIVE'} trading environment`);
    console.log(`🔒 Dry run mode: ${config.alpaca.dryRun ? 'ENABLED' : 'DISABLED'}`);
    try {
        // Initialize Alpaca data provider
        const dataProvider = new AlpacaDataProvider(config.alpaca.apiKey, config.alpaca.secretKey, config.alpaca.baseUrl);
        // Test API connection
        console.log('\n🔍 Testing Alpaca API connection...');
        const isAvailable = await dataProvider.isAvailable();
        if (!isAvailable) {
            throw new Error('Alpaca API is not available. Please check your credentials.');
        }
        console.log('✅ Alpaca API connection successful!');
        // Get account information
        const accountInfo = await dataProvider.getAccountInfo();
        console.log(`💰 Account equity: $${parseFloat(accountInfo.equity).toFixed(2)}`);
        console.log(`💵 Buying power: $${parseFloat(accountInfo.buying_power).toFixed(2)}`);
        // Example 1: Backtest with real Alpaca data
        console.log('\n📈 Running backtest with real Alpaca data...');
        await runBacktestWithAlpacaData(dataProvider);
        // Example 2: Live trading simulation (if enabled)
        if (!config.alpaca.dryRun) {
            console.log('\n⚠️  WARNING: Live trading is enabled!');
            console.log('This will execute real trades with real money.');
            console.log('Make sure you understand the risks before proceeding.');
        }
        console.log('\n🤖 Setting up live trading executor...');
        await setupLiveTrading(config);
    }
    catch (error) {
        console.error('❌ Error in Alpaca example:', error);
        throw error;
    }
}
async function runBacktestWithAlpacaData(dataProvider) {
    const config = getConfig();
    // Create backtest engine
    const engine = new BacktestEngine(config.backtesting.defaultConfig);
    // Create strategy
    const strategy = new SimpleMovingAverageStrategy(20, 50, ['AAPL', 'GOOGL']);
    // Fetch real market data from Alpaca
    const marketData = new Map();
    const symbols = ['AAPL', 'GOOGL', 'MSFT']; // Reduced set for example
    for (const symbol of symbols) {
        console.log(`📊 Fetching data for ${symbol}...`);
        try {
            const data = await dataProvider.getPriceData(symbol, new Date('2023-01-01'), // Last year
            new Date('2023-12-31'));
            marketData.set(symbol, data);
            console.log(`✅ Retrieved ${data.length} data points for ${symbol}`);
        }
        catch (error) {
            console.error(`❌ Failed to fetch data for ${symbol}:`, error);
        }
    }
    if (marketData.size === 0) {
        console.log('❌ No market data available for backtesting');
        return;
    }
    // Run backtest
    console.log('\n🔄 Running backtest...');
    const result = await engine.runBacktest(strategy, marketData);
    // Display results
    console.log('\n📊 Backtest Results:');
    console.log(`📈 Total Return: ${(result.totalReturn * 100).toFixed(2)}%`);
    console.log(`📊 Annualized Return: ${(result.annualizedReturn * 100).toFixed(2)}%`);
    console.log(`📉 Max Drawdown: ${(result.maxDrawdown * 100).toFixed(2)}%`);
    console.log(`📐 Sharpe Ratio: ${result.sharpeRatio.toFixed(2)}`);
    console.log(`🎯 Win Rate: ${(result.winRate * 100).toFixed(2)}%`);
    console.log(`🔢 Total Trades: ${result.totalTrades}`);
    console.log(`✅ Profitable Trades: ${result.profitableTrades}`);
    console.log(`❌ Losing Trades: ${result.losingTrades}`);
}
async function setupLiveTrading(config) {
    // Initialize trade executor
    const tradeExecutor = new AlpacaTradeExecutor(config.alpaca.apiKey, config.alpaca.secretKey, config.alpaca.baseUrl, config.alpaca.dryRun);
    // Get current account status
    const account = await tradeExecutor.getAccount();
    console.log(`📊 Account Status: ${account.status}`);
    console.log(`💰 Portfolio Value: $${parseFloat(account.portfolio_value).toFixed(2)}`);
    // Get current positions
    const positions = await tradeExecutor.getPositions();
    console.log(`📍 Current Positions: ${positions.length}`);
    if (positions.length > 0) {
        console.log('\n📋 Current Holdings:');
        positions.forEach((position) => {
            const unrealizedPL = parseFloat(position.unrealized_pl);
            const plColor = unrealizedPL >= 0 ? '🟢' : '🔴';
            console.log(`${plColor} ${position.symbol}: ${position.qty} shares @ $${parseFloat(position.avg_cost).toFixed(2)} (P&L: $${unrealizedPL.toFixed(2)})`);
        });
    }
    // Example: Generate a simple signal and execute (in dry run mode)
    console.log('\n🎯 Example signal generation and execution...');
    const exampleSignal = {
        symbol: 'AAPL',
        action: 'buy',
        strength: 0.5, // 50% confidence
        timestamp: new Date(),
        reason: 'Example signal for demonstration'
    };
    try {
        const trade = await tradeExecutor.executeTrade(exampleSignal, undefined, // No current position
        parseFloat(account.buying_power) // Available cash
        );
        if (trade) {
            console.log(`✅ Trade executed: ${trade.side} ${trade.quantity} shares of ${trade.symbol} at $${trade.price.toFixed(2)}`);
        }
        else {
            console.log('❌ Trade not executed (insufficient funds or other constraints)');
        }
    }
    catch (error) {
        console.error('❌ Error executing example trade:', error);
    }
}
// Run the example if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
    runAlpacaExample().catch(console.error);
}
//# sourceMappingURL=alpaca-example.js.map