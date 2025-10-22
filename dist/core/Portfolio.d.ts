/**
 * Portfolio management system
 * Tracks positions, cash, and portfolio value over time
 */
import type { Position, Trade, PriceData } from '../types/index.js';
export declare class Portfolio {
    private cash;
    private positions;
    private equityCurve;
    private readonly initialCapital;
    constructor(initialCapital: number);
    /**
     * Get current cash balance
     */
    getCash(): number;
    /**
     * Get position for a specific symbol
     */
    getPosition(symbol: string): Position | undefined;
    /**
     * Get all current positions
     */
    getPositions(): Position[];
    /**
     * Update position after a trade
     */
    updatePosition(trade: Trade): void;
    /**
     * Update portfolio value based on current market prices
     */
    updateValue(priceData: PriceData[]): void;
    /**
     * Get equity curve data
     */
    getEquityCurve(): Array<{
        timestamp: Date;
        value: number;
    }>;
    /**
     * Get total portfolio value
     */
    getTotalValue(): number;
    private calculateAveragePrice;
}
//# sourceMappingURL=Portfolio.d.ts.map