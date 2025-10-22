/**
 * Portfolio management system
 * Tracks positions, cash, and portfolio value over time
 */

import type { Position, Trade, PriceData } from '../types/index.js';
import Decimal from 'decimal.js';

export class Portfolio {
  private cash: Decimal;
  private positions: Map<string, Position>;
  private equityCurve: Array<{ timestamp: Date; value: number }>;
  private readonly initialCapital: number;

  constructor(initialCapital: number) {
    this.initialCapital = initialCapital;
    this.cash = new Decimal(initialCapital);
    this.positions = new Map();
    this.equityCurve = [{ timestamp: new Date(), value: initialCapital }];
  }

  /**
   * Get current cash balance
   */
  getCash(): number {
    return this.cash.toNumber();
  }

  /**
   * Get position for a specific symbol
   */
  getPosition(symbol: string): Position | undefined {
    return this.positions.get(symbol);
  }

  /**
   * Get all current positions
   */
  getPositions(): Position[] {
    return Array.from(this.positions.values());
  }

  /**
   * Update position after a trade
   */
  updatePosition(trade: Trade): void {
    const currentPosition = this.positions.get(trade.symbol);
    
    if (trade.side === 'buy') {
      this.cash = this.cash.minus(trade.quantity * trade.price + trade.fees);
      
      if (currentPosition) {
        // Update existing position
        const newQuantity = currentPosition.quantity + trade.quantity;
        const newAveragePrice = this.calculateAveragePrice(
          currentPosition.quantity,
          currentPosition.averagePrice,
          trade.quantity,
          trade.price
        );
        
        this.positions.set(trade.symbol, {
          symbol: trade.symbol,
          quantity: newQuantity,
          averagePrice: newAveragePrice,
          unrealizedPnL: 0, // Will be updated in updateValue
          realizedPnL: currentPosition.realizedPnL,
        });
      } else {
        // Create new position
        this.positions.set(trade.symbol, {
          symbol: trade.symbol,
          quantity: trade.quantity,
          averagePrice: trade.price,
          unrealizedPnL: 0,
          realizedPnL: 0,
        });
      }
    } else {
      // Sell trade
      if (!currentPosition || currentPosition.quantity < trade.quantity) {
        throw new Error(`Insufficient position for sell trade: ${trade.symbol}`);
      }
      
      this.cash = this.cash.plus(trade.quantity * trade.price - trade.fees);
      
      const realizedPnL = (trade.price - currentPosition.averagePrice) * trade.quantity;
      const newQuantity = currentPosition.quantity - trade.quantity;
      
      if (newQuantity === 0) {
        // Close position
        this.positions.delete(trade.symbol);
      } else {
        // Update position
        this.positions.set(trade.symbol, {
          ...currentPosition,
          quantity: newQuantity,
          realizedPnL: currentPosition.realizedPnL + realizedPnL,
        });
      }
    }
  }

  /**
   * Update portfolio value based on current market prices
   */
  updateValue(priceData: PriceData[]): void {
    let totalValue = this.cash.toNumber();
    
    for (const position of this.positions.values()) {
      const currentPrice = priceData.find(p => p.symbol === position.symbol)?.close;
      if (currentPrice) {
        const unrealizedPnL = (currentPrice - position.averagePrice) * position.quantity;
        totalValue += position.quantity * currentPrice;
        
        // Update position with current unrealized PnL
        this.positions.set(position.symbol, {
          ...position,
          unrealizedPnL,
        });
      }
    }
    
    this.equityCurve.push({
      timestamp: new Date(),
      value: totalValue,
    });
  }

  /**
   * Get equity curve data
   */
  getEquityCurve(): Array<{ timestamp: Date; value: number }> {
    return [...this.equityCurve];
  }

  /**
   * Get total portfolio value
   */
  getTotalValue(): number {
    const latest = this.equityCurve[this.equityCurve.length - 1];
    return latest ? latest.value : this.initialCapital;
  }

  private calculateAveragePrice(
    currentQuantity: number,
    currentPrice: number,
    newQuantity: number,
    newPrice: number
  ): number {
    const totalQuantity = currentQuantity + newQuantity;
    const totalValue = (currentQuantity * currentPrice) + (newQuantity * newPrice);
    return totalValue / totalQuantity;
  }
}