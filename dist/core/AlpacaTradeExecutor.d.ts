/**
 * Alpaca live trade execution engine
 * Handles real trade execution through Alpaca Markets API
 */
import type { Trade, Signal, Position } from '../types/index.js';
export interface AlpacaTradeConfig {
    readonly apiKey: string;
    readonly secretKey: string;
    readonly baseUrl?: string;
    readonly paperTrading?: boolean;
}
export declare class AlpacaTradeExecutor {
    private readonly client;
    private readonly commission;
    private readonly slippage;
    constructor(config: AlpacaTradeConfig, commission?: number, slippage?: number);
    /**
     * Execute a live trade through Alpaca
     */
    executeTrade(signal: Signal, currentPosition: Position | undefined, availableCash: number): Promise<Trade | null>;
    /**
     * Get current positions from Alpaca
     */
    getPositions(): Promise<Position[]>;
    /**
     * Get account information
     */
    getAccount(): Promise<any>;
    /**
     * Cancel all open orders
     */
    cancelAllOrders(): Promise<void>;
    /**
     * Get open orders
     */
    getOpenOrders(): Promise<any[]>;
    private getCurrentPrice;
    private calculateExecutionPrice;
    private calculateQuantity;
    private submitOrder;
    private calculateFees;
}
//# sourceMappingURL=AlpacaTradeExecutor.d.ts.map