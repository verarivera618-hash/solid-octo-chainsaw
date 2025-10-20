/**
 * Alpaca trade execution engine
 * Handles live trade execution through Alpaca Markets API
 */

import type { Trade, Signal, Position } from '../types/index.js';
import Alpaca from '@alpacahq/alpaca-trade-api';

export class AlpacaTradeExecutor {
  private alpaca: Alpaca;
  private readonly dryRun: boolean;

  constructor(apiKey: string, secretKey: string, baseUrl: string = 'https://paper-api.alpaca.markets', dryRun: boolean = true) {
    this.alpaca = new Alpaca({
      key: apiKey,
      secret: secretKey,
      baseUrl: baseUrl,
      usePolygon: false,
    });
    this.dryRun = dryRun;
  }

  /**
   * Execute a live trade based on signal
   */
  async executeTrade(
    signal: Signal,
    currentPosition: Position | undefined,
    availableCash: number
  ): Promise<Trade | null> {
    if (signal.action === 'hold') {
      return null;
    }

    try {
      // Get current market price
      const currentPrice = await this.getCurrentPrice(signal.symbol);
      
      // Calculate quantity based on available cash and signal strength
      const quantity = this.calculateQuantity(signal, currentPosition, availableCash, currentPrice);
      
      if (quantity <= 0) {
        console.log(`Cannot execute trade for ${signal.symbol}: insufficient quantity (${quantity})`);
        return null;
      }

      if (this.dryRun) {
        console.log(`DRY RUN: Would ${signal.action} ${quantity} shares of ${signal.symbol} at ~$${currentPrice}`);
        
        // Return simulated trade
        return {
          id: this.generateTradeId(),
          symbol: signal.symbol,
          side: signal.action,
          quantity,
          price: currentPrice,
          timestamp: signal.timestamp,
          fees: quantity * currentPrice * 0.001, // Estimated fees
        };
      }

      // Execute real trade
      const order = await this.alpaca.createOrder({
        symbol: signal.symbol,
        qty: quantity,
        side: signal.action,
        type: 'market',
        time_in_force: 'day',
      });

      console.log(`Executed ${signal.action} order for ${quantity} shares of ${signal.symbol}:`, order.id);

      // Wait for order to fill (simplified)
      const filledOrder = await this.waitForOrderFill(order.id);
      
      return {
        id: filledOrder.id,
        symbol: signal.symbol,
        side: signal.action,
        quantity: parseFloat(filledOrder.filled_qty),
        price: parseFloat(filledOrder.filled_avg_price || filledOrder.limit_price || currentPrice.toString()),
        timestamp: new Date(filledOrder.filled_at || signal.timestamp),
        fees: 0, // Alpaca doesn't charge commission for stocks
      };

    } catch (error) {
      console.error(`Error executing trade for ${signal.symbol}:`, error);
      throw error;
    }
  }

  /**
   * Get current market price for a symbol
   */
  private async getCurrentPrice(symbol: string): Promise<number> {
    try {
      const quote = await this.alpaca.getLatestQuote(symbol);
      return (quote.BidPrice + quote.AskPrice) / 2; // Mid price
    } catch (error) {
      console.error(`Error getting current price for ${symbol}:`, error);
      throw error;
    }
  }

  /**
   * Calculate quantity to trade based on signal and available capital
   */
  private calculateQuantity(
    signal: Signal,
    currentPosition: Position | undefined,
    availableCash: number,
    price: number
  ): number {
    if (signal.action === 'buy') {
      // For buy orders, use a percentage of available cash based on signal strength
      const maxInvestment = availableCash * signal.strength * 0.1; // Max 10% per trade
      return Math.floor(maxInvestment / price);
    } else {
      // For sell orders, sell based on current position and signal strength
      const currentQuantity = currentPosition?.quantity || 0;
      return Math.floor(currentQuantity * signal.strength);
    }
  }

  /**
   * Wait for order to fill (simplified implementation)
   */
  private async waitForOrderFill(orderId: string, maxWaitMs: number = 30000): Promise<any> {
    const startTime = Date.now();
    
    while (Date.now() - startTime < maxWaitMs) {
      try {
        const order = await this.alpaca.getOrder(orderId);
        
        if (order.status === 'filled') {
          return order;
        } else if (order.status === 'rejected' || order.status === 'canceled') {
          throw new Error(`Order ${orderId} was ${order.status}`);
        }
        
        // Wait 1 second before checking again
        await new Promise(resolve => setTimeout(resolve, 1000));
      } catch (error) {
        console.error(`Error checking order status:`, error);
        throw error;
      }
    }
    
    throw new Error(`Order ${orderId} did not fill within ${maxWaitMs}ms`);
  }

  /**
   * Get account information
   */
  async getAccount() {
    return await this.alpaca.getAccount();
  }

  /**
   * Get all positions
   */
  async getPositions() {
    return await this.alpaca.getPositions();
  }

  /**
   * Get all orders
   */
  async getOrders() {
    return await this.alpaca.getOrders({
      status: 'all',
      until: null,
      after: null,
      limit: 100,
      direction: null,
      nested: null,
      symbols: null,
    });
  }

  private generateTradeId(): string {
    return `alpaca_trade_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}