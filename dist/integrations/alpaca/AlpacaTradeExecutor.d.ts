/**
 * Alpaca Trading API Trade Executor
 * Executes live trades through Alpaca Trading API
 */
import { Trade, Signal, Position } from '../../types/index.js';
export interface AlpacaTradeConfig {
    readonly apiKey: string;
    readonly secretKey: string;
    readonly baseUrl?: string;
    readonly paperTrading?: boolean;
}
export declare class AlpacaTradeExecutor {
    private readonly config;
    private readonly commission;
    private readonly slippage;
    constructor(config: AlpacaTradeConfig, commission?: number, slippage?: number);
    /**
     * Execute a live trade through Alpaca
     */
    executeTrade(signal: Signal, currentPosition: Position | undefined, availableCash: number): Promise<Trade | null>;
    private submitOrder;
    private calculateQuantity;
    private calculateFees;
    /**
     * Get current account information
     */
    getAccountInfo(): Promise<any>;
    /**
     * Get current positions
     */
    getPositions(): Promise<any>;
}
//# sourceMappingURL=AlpacaTradeExecutor.d.ts.map