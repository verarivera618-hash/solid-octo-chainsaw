/**
 * Live Trading Orchestrator
 * Coordinates between different brokers and data providers for live trading
 */
import { AlpacaTradeExecutor } from './alpaca/AlpacaTradeExecutor.js';
import { AlpacaDataProvider } from './alpaca/AlpacaDataProvider.js';
import { TradingViewSignalReceiver } from './tradingview/TradingViewSignalReceiver.js';
import { PocketOptionDataProvider } from './pocketoption/PocketOptionDataProvider.js';
import { TradeStationDataProvider } from './tradestation/TradeStationDataProvider.js';
export class LiveTradingOrchestrator {
    config;
    strategies = new Map();
    signalReceiver;
    tradeExecutors = new Map();
    dataProviders = new Map();
    isRunning = false;
    constructor(config) {
        this.config = config;
        this.signalReceiver = new TradingViewSignalReceiver(config.tradingview?.webhookSecret);
        this.initializeProviders();
        this.initializeExecutors();
    }
    initializeProviders() {
        // Initialize Alpaca data provider
        if (this.config.alpaca) {
            const alpacaProvider = new AlpacaDataProvider(this.config.alpaca);
            this.dataProviders.set('alpaca', alpacaProvider);
        }
        // Initialize TradeStation data provider
        if (this.config.tradestation) {
            const tsProvider = new TradeStationDataProvider(this.config.tradestation);
            this.dataProviders.set('tradestation', tsProvider);
        }
        // Initialize Pocket Option data provider
        if (this.config.pocketoption) {
            const poProvider = new PocketOptionDataProvider(this.config.pocketoption);
            this.dataProviders.set('pocketoption', poProvider);
        }
    }
    initializeExecutors() {
        // Initialize Alpaca trade executor
        if (this.config.alpaca) {
            const alpacaExecutor = new AlpacaTradeExecutor(this.config.alpaca);
            this.tradeExecutors.set('alpaca', alpacaExecutor);
        }
    }
    /**
     * Register a trading strategy
     */
    registerStrategy(name, strategy) {
        this.strategies.set(name, strategy);
        this.signalReceiver.registerStrategy(name, strategy);
    }
    /**
     * Start live trading
     */
    async startTrading() {
        if (this.isRunning) {
            throw new Error('Trading is already running');
        }
        this.isRunning = true;
        console.log('🚀 Starting live trading orchestrator...');
        // Start webhook server for TradingView signals
        if (this.config.tradingview?.webhookPort) {
            await this.startWebhookServer();
        }
        console.log('✅ Live trading orchestrator started successfully');
    }
    /**
     * Stop live trading
     */
    async stopTrading() {
        this.isRunning = false;
        console.log('🛑 Live trading orchestrator stopped');
    }
    /**
     * Process a trading signal
     */
    async processSignal(signal, broker = 'alpaca') {
        if (!this.isRunning) {
            console.warn('Trading is not running, ignoring signal');
            return null;
        }
        try {
            const executor = this.tradeExecutors.get(broker);
            if (!executor) {
                throw new Error(`No executor found for broker: ${broker}`);
            }
            // Get current positions (simplified - in production, you'd track this properly)
            const currentPositions = [];
            const availableCash = 10000; // This should come from account info
            // Apply risk management
            if (!this.validateRiskManagement(signal, currentPositions, availableCash)) {
                console.warn('Signal rejected by risk management:', signal);
                return null;
            }
            // Execute the trade
            const trade = await executor.executeTrade(signal, undefined, availableCash);
            if (trade) {
                console.log(`✅ Trade executed: ${trade.side} ${trade.quantity} ${trade.symbol} @ $${trade.price}`);
            }
            return trade;
        }
        catch (error) {
            console.error('Error processing signal:', error);
            return null;
        }
    }
    validateRiskManagement(signal, positions, availableCash) {
        if (!this.config.riskManagement) {
            return true; // No risk management configured
        }
        const { maxPositionSize, maxDailyLoss, stopLossPercentage } = this.config.riskManagement;
        // Check position size
        if (signal.action === 'buy') {
            const estimatedCost = 100 * signal.strength; // Simplified calculation
            if (estimatedCost > maxPositionSize) {
                console.warn('Position size exceeds maximum allowed');
                return false;
            }
        }
        // Add more risk management rules as needed
        return true;
    }
    async startWebhookServer() {
        // This would typically use Express.js or similar
        // For now, just log that webhook server would start
        console.log(`📡 Webhook server would start on port ${this.config.tradingview?.webhookPort}`);
    }
    /**
     * Get current account status across all brokers
     */
    async getAccountStatus() {
        const status = {};
        for (const [broker, executor] of this.tradeExecutors) {
            try {
                if (broker === 'alpaca' && executor.getAccountInfo) {
                    status[broker] = await executor.getAccountInfo();
                }
            }
            catch (error) {
                console.error(`Error getting account status for ${broker}:`, error);
                status[broker] = { error: error.message };
            }
        }
        return status;
    }
    /**
     * Get webhook handler for TradingView signals
     */
    getWebhookHandler() {
        return this.signalReceiver.createWebhookHandler();
    }
}
//# sourceMappingURL=LiveTradingOrchestrator.js.map