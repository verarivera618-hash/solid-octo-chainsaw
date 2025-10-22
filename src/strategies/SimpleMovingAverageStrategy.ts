/**
 * Simple Moving Average Crossover Strategy
 * Example strategy implementation demonstrating proper structure
 */

import type { Strategy, Signal, PriceData } from '../types/index.js';

export class SimpleMovingAverageStrategy implements Strategy {
  public readonly name = 'Simple Moving Average Crossover';
  public readonly description = 'Buy when short MA crosses above long MA, sell when short MA crosses below long MA';
  public readonly parameters: Record<string, unknown>;

  constructor(
    private readonly shortPeriod: number = 20,
    private readonly longPeriod: number = 50,
    private readonly symbols: string[] = ['AAPL', 'GOOGL']
  ) {
    this.parameters = {
      shortPeriod,
      longPeriod,
      symbols,
    };
  }

  generateSignals(data: PriceData[]): Signal[] {
    const signals: Signal[] = [];
    
    for (const symbol of this.symbols) {
      const symbolData = data.filter(d => (d as any).symbol === symbol).sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
      
      if (symbolData.length < this.longPeriod) {
        continue; // Not enough data
      }

      const shortMA = this.calculateSMA(symbolData, this.shortPeriod);
      const longMA = this.calculateSMA(symbolData, this.longPeriod);
      
      if (shortMA.length < 2 || longMA.length < 2) {
        continue;
      }

      const currentShort = shortMA[shortMA.length - 1]!;
      const previousShort = shortMA[shortMA.length - 2]!;
      const currentLong = longMA[longMA.length - 1]!;
      const previousLong = longMA[longMA.length - 2]!;

      // Check for crossover
      if (previousShort <= previousLong && currentShort > currentLong) {
        // Bullish crossover - buy signal
        signals.push({
          symbol,
          action: 'buy',
          strength: this.calculateSignalStrength(currentShort, currentLong),
          timestamp: symbolData[symbolData.length - 1]!.timestamp,
          reason: `Short MA (${currentShort.toFixed(2)}) crossed above Long MA (${currentLong.toFixed(2)})`,
        });
      } else if (previousShort >= previousLong && currentShort < currentLong) {
        // Bearish crossover - sell signal
        signals.push({
          symbol,
          action: 'sell',
          strength: this.calculateSignalStrength(currentLong, currentShort),
          timestamp: symbolData[symbolData.length - 1]!.timestamp,
          reason: `Short MA (${currentShort.toFixed(2)}) crossed below Long MA (${currentLong.toFixed(2)})`,
        });
      }
    }

    return signals;
  }

  validate(): boolean {
    return (
      this.shortPeriod > 0 &&
      this.longPeriod > 0 &&
      this.shortPeriod < this.longPeriod &&
      this.symbols.length > 0
    );
  }

  private calculateSMA(data: PriceData[], period: number): number[] {
    const sma: number[] = [];
    
    for (let i = period - 1; i < data.length; i++) {
      const slice = data.slice(i - period + 1, i + 1);
      const average = slice.reduce((sum, d) => sum + d.close, 0) / period;
      sma.push(average);
    }
    
    return sma;
  }

  private calculateSignalStrength(shortMA: number, longMA: number): number {
    const difference = Math.abs(shortMA - longMA);
    const average = (shortMA + longMA) / 2;
    const strength = Math.min(difference / average, 1);
    return Math.max(strength, 0.1); // Minimum strength of 0.1
  }
}