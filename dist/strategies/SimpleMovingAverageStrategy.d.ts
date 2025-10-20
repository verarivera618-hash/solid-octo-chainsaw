/**
 * Simple Moving Average Crossover Strategy
 * Example strategy implementation demonstrating proper structure
 */
import { Strategy, Signal, PriceData } from '../types/index.js';
export declare class SimpleMovingAverageStrategy implements Strategy {
    private readonly shortPeriod;
    private readonly longPeriod;
    private readonly symbols;
    readonly name = "Simple Moving Average Crossover";
    readonly description = "Buy when short MA crosses above long MA, sell when short MA crosses below long MA";
    readonly parameters: Record<string, unknown>;
    constructor(shortPeriod?: number, longPeriod?: number, symbols?: string[]);
    generateSignals(data: PriceData[]): Signal[];
    validate(): boolean;
    private calculateSMA;
    private calculateSignalStrength;
}
//# sourceMappingURL=SimpleMovingAverageStrategy.d.ts.map