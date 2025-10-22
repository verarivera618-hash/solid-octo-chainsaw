/**
 * Trade execution engine
 * Handles trade simulation with commission and slippage
 */
import { Trade, Signal, Position } from '../types/index.js';
export declare class TradeExecutor {
    private readonly commission;
    private readonly slippage;
    constructor(commission: number, slippage: number);
    /**
     * Execute a trade based on signal
     */
    executeTrade(signal: Signal, currentPosition: Position | undefined, availableCash: number): Promise<Trade | null>;
    private calculateExecutionPrice;
    private calculateQuantity;
    private calculateFees;
    private generateTradeId;
}
//# sourceMappingURL=TradeExecutor.d.ts.map