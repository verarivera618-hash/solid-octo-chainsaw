/**
 * Live Trading Orchestrator
 * Coordinates between different brokers and data providers for live trading
 */
import { Signal, Trade, Strategy } from '../types/index.js';
import { AlpacaConfig } from './alpaca/AlpacaDataProvider.js';
import { PocketOptionConfig } from './pocketoption/PocketOptionDataProvider.js';
import { TradeStationConfig } from './tradestation/TradeStationDataProvider.js';
export interface LiveTradingConfig {
    readonly alpaca?: AlpacaConfig;
    readonly tradestation?: TradeStationConfig;
    readonly pocketoption?: PocketOptionConfig;
    readonly tradingview?: {
        readonly webhookSecret?: string;
        readonly webhookPort?: number;
    };
    readonly riskManagement?: {
        readonly maxPositionSize: number;
        readonly maxDailyLoss: number;
        readonly stopLossPercentage: number;
    };
}
export declare class LiveTradingOrchestrator {
    private readonly config;
    private readonly strategies;
    private readonly signalReceiver;
    private readonly tradeExecutors;
    private readonly dataProviders;
    private isRunning;
    constructor(config: LiveTradingConfig);
    private initializeProviders;
    private initializeExecutors;
    /**
     * Register a trading strategy
     */
    registerStrategy(name: string, strategy: Strategy): void;
    /**
     * Start live trading
     */
    startTrading(): Promise<void>;
    /**
     * Stop live trading
     */
    stopTrading(): Promise<void>;
    /**
     * Process a trading signal
     */
    processSignal(signal: Signal, broker?: string): Promise<Trade | null>;
    private validateRiskManagement;
    private startWebhookServer;
    /**
     * Get current account status across all brokers
     */
    getAccountStatus(): Promise<Record<string, any>>;
    /**
     * Get webhook handler for TradingView signals
     */
    getWebhookHandler(): (req: any, res: any) => Promise<void>;
}
//# sourceMappingURL=LiveTradingOrchestrator.d.ts.map