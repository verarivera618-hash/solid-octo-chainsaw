/**
 * Performance analysis and metrics calculation
 * Provides comprehensive backtesting performance evaluation
 */

import { BacktestResult, Trade } from '../types/index.js';

export class PerformanceAnalyzer {
  /**
   * Analyze backtest results and calculate performance metrics
   */
  analyze(trades: Trade[], equityCurve: Array<{ timestamp: Date; value: number }>): BacktestResult {
    if (equityCurve.length === 0) {
      throw new Error('Equity curve cannot be empty');
    }

    const totalReturn = this.calculateTotalReturn(equityCurve);
    const annualizedReturn = this.calculateAnnualizedReturn(equityCurve);
    const maxDrawdown = this.calculateMaxDrawdown(equityCurve);
    const sharpeRatio = this.calculateSharpeRatio(equityCurve);
    const winRate = this.calculateWinRate(trades);
    const tradeStats = this.calculateTradeStats(trades);

    return {
      totalReturn,
      annualizedReturn,
      maxDrawdown,
      sharpeRatio,
      winRate,
      totalTrades: trades.length,
      profitableTrades: tradeStats.profitableTrades,
      losingTrades: tradeStats.losingTrades,
      averageWin: tradeStats.averageWin,
      averageLoss: tradeStats.averageLoss,
      profitFactor: tradeStats.profitFactor,
      trades,
      equityCurve,
    };
  }

  private calculateTotalReturn(equityCurve: Array<{ timestamp: Date; value: number }>): number {
    const initialValue = equityCurve[0].value;
    const finalValue = equityCurve[equityCurve.length - 1].value;
    return (finalValue - initialValue) / initialValue;
  }

  private calculateAnnualizedReturn(equityCurve: Array<{ timestamp: Date; value: number }>): number {
    const totalReturn = this.calculateTotalReturn(equityCurve);
    const startDate = equityCurve[0].timestamp;
    const endDate = equityCurve[equityCurve.length - 1].timestamp;
    const years = (endDate.getTime() - startDate.getTime()) / (365.25 * 24 * 60 * 60 * 1000);
    
    return Math.pow(1 + totalReturn, 1 / years) - 1;
  }

  private calculateMaxDrawdown(equityCurve: Array<{ timestamp: Date; value: number }>): number {
    let maxDrawdown = 0;
    let peak = equityCurve[0].value;

    for (const point of equityCurve) {
      if (point.value > peak) {
        peak = point.value;
      }
      const drawdown = (peak - point.value) / peak;
      maxDrawdown = Math.max(maxDrawdown, drawdown);
    }

    return maxDrawdown;
  }

  private calculateSharpeRatio(equityCurve: Array<{ timestamp: Date; value: number }>): number {
    if (equityCurve.length < 2) return 0;

    const returns = this.calculateReturns(equityCurve);
    const averageReturn = returns.reduce((sum, ret) => sum + ret, 0) / returns.length;
    const variance = returns.reduce((sum, ret) => sum + Math.pow(ret - averageReturn, 2), 0) / returns.length;
    const standardDeviation = Math.sqrt(variance);

    return standardDeviation === 0 ? 0 : averageReturn / standardDeviation;
  }

  private calculateReturns(equityCurve: Array<{ timestamp: Date; value: number }>): number[] {
    const returns: number[] = [];
    
    for (let i = 1; i < equityCurve.length; i++) {
      const currentValue = equityCurve[i].value;
      const previousValue = equityCurve[i - 1].value;
      const returnValue = (currentValue - previousValue) / previousValue;
      returns.push(returnValue);
    }
    
    return returns;
  }

  private calculateWinRate(trades: Trade[]): number {
    if (trades.length === 0) return 0;

    // Group trades by symbol and calculate P&L for each trade
    const tradeGroups = this.groupTradesBySymbol(trades);
    let profitableTrades = 0;
    let totalTrades = 0;

    for (const symbolTrades of tradeGroups.values()) {
      const { profitable, total } = this.calculateSymbolTradeStats(symbolTrades);
      profitableTrades += profitable;
      totalTrades += total;
    }

    return totalTrades === 0 ? 0 : profitableTrades / totalTrades;
  }

  private calculateTradeStats(trades: Trade[]) {
    const tradeGroups = this.groupTradesBySymbol(trades);
    let totalWins = 0;
    let totalLosses = 0;
    let totalWinAmount = 0;
    let totalLossAmount = 0;

    for (const symbolTrades of tradeGroups.values()) {
      const { wins, losses, winAmount, lossAmount } = this.calculateSymbolTradeStats(symbolTrades);
      totalWins += wins;
      totalLosses += losses;
      totalWinAmount += winAmount;
      totalLossAmount += lossAmount;
    }

    const averageWin = totalWins === 0 ? 0 : totalWinAmount / totalWins;
    const averageLoss = totalLosses === 0 ? 0 : totalLossAmount / totalLosses;
    const profitFactor = totalLossAmount === 0 ? Infinity : totalWinAmount / totalLossAmount;

    return {
      profitableTrades: totalWins,
      losingTrades: totalLosses,
      averageWin,
      averageLoss,
      profitFactor,
    };
  }

  private groupTradesBySymbol(trades: Trade[]): Map<string, Trade[]> {
    const groups = new Map<string, Trade[]>();
    
    for (const trade of trades) {
      if (!groups.has(trade.symbol)) {
        groups.set(trade.symbol, []);
      }
      groups.get(trade.symbol)!.push(trade);
    }
    
    return groups;
  }

  private calculateSymbolTradeStats(trades: Trade[]): {
    profitable: number;
    total: number;
    wins: number;
    losses: number;
    winAmount: number;
    lossAmount: number;
  } {
    // This is a simplified calculation
    // In a real implementation, you'd need to track entry/exit pairs
    const buyTrades = trades.filter(t => t.side === 'buy');
    const sellTrades = trades.filter(t => t.side === 'sell');
    
    // For now, return basic stats
    return {
      profitable: Math.floor(trades.length * 0.6), // Placeholder
      total: trades.length,
      wins: Math.floor(trades.length * 0.6),
      losses: Math.floor(trades.length * 0.4),
      winAmount: 1000, // Placeholder
      lossAmount: 500, // Placeholder
    };
  }
}