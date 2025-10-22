/**
 * Main entry point with environment configuration
 */
import 'dotenv/config';
import { LiveTradingOrchestrator } from './integrations/LiveTradingOrchestrator.js';
import { SimpleMovingAverageStrategy } from './strategies/SimpleMovingAverageStrategy.js';
// Load configuration from environment variables
const alpacaConfig = {
    apiKey: process.env['ALPACA_API_KEY'],
    secretKey: process.env['ALPACA_SECRET_KEY'],
    baseUrl: process.env['ALPACA_BASE_URL'] || 'https://paper-api.alpaca.markets',
    dataUrl: process.env['ALPACA_DATA_URL'] || 'https://data.alpaca.markets',
    paperTrading: process.env['ALPACA_PAPER_TRADING'] === 'true'
};
const liveTradingConfig = {
    alpaca: alpacaConfig,
    riskManagement: {
        maxPositionSize: parseInt(process.env['MAX_POSITION_SIZE'] || '1000'),
        maxDailyLoss: parseInt(process.env['MAX_DAILY_LOSS'] || '500'),
        stopLossPercentage: parseFloat(process.env['STOP_LOSS_PERCENTAGE'] || '0.02'),
        maxOpenPositions: 5
    }
};
async function main() {
    console.log('🚀 Starting Trading System...');
    console.log(`📊 Paper Trading: ${alpacaConfig.paperTrading ? 'ON' : 'OFF'}`);
    try {
        const orchestrator = new LiveTradingOrchestrator(liveTradingConfig);
        // Register strategies
        const smaStrategy = new SimpleMovingAverageStrategy(10, 20, ['AAPL', 'GOOGL']);
        orchestrator.registerStrategy('sma_crossover', smaStrategy);
        // Test connection
        const accountStatus = await orchestrator.getAccountStatus();
        console.log('✅ Account Status:', accountStatus);
        // Start trading
        await orchestrator.startTrading();
        console.log('🔄 Trading system is running...');
        console.log('Press Ctrl+C to stop');
        // Keep running
        process.on('SIGINT', async () => {
            console.log('\n🛑 Shutting down...');
            await orchestrator.stopTrading();
            process.exit(0);
        });
    }
    catch (error) {
        console.error('❌ Error:', error);
        process.exit(1);
    }
}
main().catch(console.error);
//# sourceMappingURL=index.js.map