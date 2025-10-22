/**
 * Core type definitions for the backtesting framework
 * This file contains all fundamental types and interfaces used throughout the system
 */
export interface PriceData {
    readonly timestamp: Date;
    readonly open: number;
    readonly high: number;
    readonly low: number;
    readonly close: number;
    readonly volume: number;
}
export interface Trade {
    readonly id: string;
    readonly symbol: string;
    readonly side: 'buy' | 'sell';
    readonly quantity: number;
    readonly price: number;
    readonly timestamp: Date;
    readonly fees: number;
}
export interface Position {
    readonly symbol: string;
    readonly quantity: number;
    readonly averagePrice?: number;
    readonly unrealizedPnL: number;
    readonly realizedPnL?: number;
    readonly currentValue?: number;
}
export interface BacktestConfig {
    readonly startDate: Date;
    readonly endDate: Date;
    readonly initialCapital: number;
    readonly commission: number;
    readonly slippage: number;
    readonly symbols: readonly string[];
}
export interface BacktestResult {
    readonly totalReturn: number;
    readonly annualizedReturn: number;
    readonly maxDrawdown: number;
    readonly sharpeRatio: number;
    readonly winRate: number;
    readonly totalTrades: number;
    readonly profitableTrades: number;
    readonly losingTrades: number;
    readonly averageWin: number;
    readonly averageLoss: number;
    readonly profitFactor: number;
    readonly trades: readonly Trade[];
    readonly equityCurve: readonly {
        timestamp: Date;
        value: number;
    }[];
}
export interface Strategy {
    readonly name: string;
    readonly description: string;
    readonly parameters: Record<string, unknown>;
    generateSignals(data: readonly PriceData[]): readonly Signal[];
    validate(): boolean;
}
export interface Signal {
    readonly symbol: string;
    readonly action: 'buy' | 'sell' | 'hold';
    readonly strength: number;
    readonly timestamp: Date;
    readonly reason: string;
}
export interface DataProvider {
    readonly name: string;
    getPriceData(symbol: string, startDate: Date, endDate: Date): Promise<readonly PriceData[]>;
    isAvailable(): Promise<boolean>;
}
export interface RiskManager {
    readonly name: string;
    validateTrade(trade: Trade, portfolio: readonly Position[]): boolean;
    calculatePositionSize(capital: number, risk: number, price: number): number;
}
export type Timeframe = '1m' | '5m' | '15m' | '30m' | '1h' | '4h' | '1d' | '1w' | '1M';
export interface MarketData {
    readonly symbol: string;
    readonly timeframe: Timeframe;
    readonly data: readonly PriceData[];
}
//# sourceMappingURL=index.d.ts.map