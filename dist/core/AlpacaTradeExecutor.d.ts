/**
 * Alpaca Trade Executor
 * Handles live trade execution through Alpaca API
 */
import type { Trade, Signal, Position } from '../types/index.js';
import { TradeExecutor } from './TradeExecutor.js';
export declare class AlpacaTradeExecutor extends TradeExecutor {
    private alpacaProvider;
    private isLive;
    constructor(commission: number, slippage: number);
    /**
     * Execute a live trade through Alpaca
     */
    executeLiveTrade(signal: Signal, currentPosition: Position | undefined, availableCash: number): Promise<Trade | null>;
    /**
     * Get current positions from Alpaca
     */
    getCurrentPositions(): Promise<Map<string, Position>>;
    /**
     * Get recent orders from Alpaca
     */
    getRecentOrders(status?: 'open' | 'closed' | 'all'): Promise<any[]>;
    /**
     * Cancel a pending order
     */
    cancelOrder(orderId: string): Promise<void>;
    /**
     * Check if market is open
     */
    isMarketOpen(): Promise<boolean>;
}
//# sourceMappingURL=AlpacaTradeExecutor.d.ts.map