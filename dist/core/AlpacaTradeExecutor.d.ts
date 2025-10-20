/**
 * Alpaca trade execution engine
 * Handles live trade execution through Alpaca Markets API
 */
import { Trade, Signal, Position } from '../types/index.js';
export declare class AlpacaTradeExecutor {
    private alpaca;
    private readonly dryRun;
    constructor(apiKey: string, secretKey: string, baseUrl?: string, dryRun?: boolean);
    /**
     * Execute a live trade based on signal
     */
    executeTrade(signal: Signal, currentPosition: Position | undefined, availableCash: number): Promise<Trade | null>;
    /**
     * Get current market price for a symbol
     */
    private getCurrentPrice;
    /**
     * Calculate quantity to trade based on signal and available capital
     */
    private calculateQuantity;
    /**
     * Wait for order to fill (simplified implementation)
     */
    private waitForOrderFill;
    /**
     * Get account information
     */
    getAccount(): Promise<any>;
    /**
     * Get all positions
     */
    getPositions(): Promise<any>;
    /**
     * Get all orders
     */
    getOrders(): Promise<any>;
    private generateTradeId;
}
//# sourceMappingURL=AlpacaTradeExecutor.d.ts.map