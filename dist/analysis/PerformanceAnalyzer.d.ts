/**
 * Performance analysis and metrics calculation
 * Provides comprehensive backtesting performance evaluation
 */
import { BacktestResult, Trade } from '../types/index.js';
export declare class PerformanceAnalyzer {
    /**
     * Analyze backtest results and calculate performance metrics
     */
    analyze(trades: Trade[], equityCurve: Array<{
        timestamp: Date;
        value: number;
    }>): BacktestResult;
    private calculateTotalReturn;
    private calculateAnnualizedReturn;
    private calculateMaxDrawdown;
    private calculateSharpeRatio;
    private calculateReturns;
    private calculateWinRate;
    private calculateTradeStats;
    private groupTradesBySymbol;
    private calculateSymbolTradeStats;
}
//# sourceMappingURL=PerformanceAnalyzer.d.ts.map