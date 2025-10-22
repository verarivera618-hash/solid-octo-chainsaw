/**
 * Live Trading Orchestrator
 * Coordinates between different brokers and data providers for live trading
 */

import { Signal, Trade, Position, Strategy } from '../types/index.js';
import { AlpacaTradeExecutor, AlpacaTradeConfig } from './alpaca/AlpacaTradeExecutor.js';
import { AlpacaDataProvider, AlpacaConfig } from './alpaca/AlpacaDataProvider.js';
import { TradingViewSignalReceiver } from './tradingview/TradingViewSignalReceiver.js';
import { PocketOptionDataProvider, PocketOptionConfig } from './pocketoption/PocketOptionDataProvider.js';
import { TradeStationDataProvider, TradeStationConfig } from './tradestation/TradeStationDataProvider.js';

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

export class LiveTradingOrchestrator {
  private readonly config: LiveTradingConfig;
  private readonly strategies: Map<string, Strategy> = new Map();
  private readonly signalReceiver: TradingViewSignalReceiver;
  private readonly tradeExecutors: Map<string, any> = new Map();
  private readonly dataProviders: Map<string, any> = new Map();
  private isRunning: boolean = false;

  constructor(config: LiveTradingConfig) {
    this.config = config;
    this.signalReceiver = new TradingViewSignalReceiver(config.tradingview?.webhookSecret);

    this.initializeProviders();
    this.initializeExecutors();
  }

  private initializeProviders(): void {
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

  private initializeExecutors(): void {
    // Initialize Alpaca trade executor
    if (this.config.alpaca) {
      const alpacaExecutor = new AlpacaTradeExecutor(this.config.alpaca);
      this.tradeExecutors.set('alpaca', alpacaExecutor);
    }
  }

  /**
   * Register a trading strategy
   */
  registerStrategy(name: string, strategy: Strategy): void {
    this.strategies.set(name, strategy);
    this.signalReceiver.registerStrategy(name, strategy);
  }

  /**
   * Start live trading
   */
  async startTrading(): Promise<void> {
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
  async stopTrading(): Promise<void> {
    this.isRunning = false;
    console.log('🛑 Live trading orchestrator stopped');
  }

  /**
   * Process a trading signal
   */
  async processSignal(signal: Signal, broker: string = 'alpaca'): Promise<Trade | null> {
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
      const currentPositions: Position[] = [];
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
    } catch (error) {
      console.error('Error processing signal:', error);
      return null;
    }
  }

  private validateRiskManagement(signal: Signal, positions: Position[], availableCash: number): boolean {
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

  private async startWebhookServer(): Promise<void> {
    // This would typically use Express.js or similar
    // For now, just log that webhook server would start
    console.log(`📡 Webhook server would start on port ${this.config.tradingview?.webhookPort}`);
  }

  /**
   * Get current account status across all brokers
   */
  async getAccountStatus(): Promise<Record<string, any>> {
    const status: Record<string, any> = {};

    for (const [broker, executor] of this.tradeExecutors) {
      try {
        if (broker === 'alpaca' && executor.getAccountInfo) {
          status[broker] = await executor.getAccountInfo();
        }
    } catch (error: any) {
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