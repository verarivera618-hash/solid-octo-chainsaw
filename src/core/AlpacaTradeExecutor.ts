/**
 * Alpaca Trade Executor
 * Handles live trade execution through Alpaca API
 */

import type { Trade, Signal, Position } from '../types/index.js';
import { AlpacaDataProvider } from '../data/AlpacaDataProvider.js';
import { TradeExecutor } from './TradeExecutor.js';

export class AlpacaTradeExecutor extends TradeExecutor {
  private alpacaProvider: AlpacaDataProvider;
  private isLive: boolean;

  constructor(commission: number, slippage: number) {
    super(commission, slippage);
    this.alpacaProvider = new AlpacaDataProvider();
    this.isLive = process.env['ALPACA_ENVIRONMENT'] === 'live';
  }

  /**
   * Execute a live trade through Alpaca
   */
  async executeLiveTrade(
    signal: Signal,
    currentPosition: Position | undefined,
    availableCash: number
  ): Promise<Trade | null> {
    // First, simulate the trade locally
    const simulatedTrade = await super.executeTrade(signal, currentPosition, availableCash);
    
    if (!simulatedTrade) {
      return null;
    }

    try {
      // Check if Alpaca is available
      const isAvailable = await this.alpacaProvider.isAvailable();
      if (!isAvailable) {
        console.error('Alpaca API is not available');
        return null;
      }

      // Get account info to check buying power
      const accountInfo = await this.alpacaProvider.getAccountInfo();
      const buyingPower = parseFloat(accountInfo.buying_power);

      if (signal.action === 'buy' && buyingPower < simulatedTrade.price * simulatedTrade.quantity) {
        console.error('Insufficient buying power for trade');
        return null;
      }

      // Place the order
      const orderResponse = await this.alpacaProvider.placeOrder({
        symbol: signal.symbol,
        quantity: simulatedTrade.quantity,
        side: signal.action as 'buy' | 'sell',
        type: 'market', // Using market orders for simplicity
        timeInForce: 'day',
      });

      console.log(`Order placed successfully: ${orderResponse.id}`);
      
      // Update trade with actual order details
      return {
        ...simulatedTrade,
        id: orderResponse.id,
        price: parseFloat(orderResponse.filled_avg_price || simulatedTrade.price),
        timestamp: new Date(orderResponse.created_at),
      };
    } catch (error) {
      console.error('Error executing live trade:', error);
      return null;
    }
  }

  /**
   * Get current positions from Alpaca
   */
  async getCurrentPositions(): Promise<Map<string, Position>> {
    try {
      const alpacaPositions = await this.alpacaProvider.getPositions();
      const positions = new Map<string, Position>();

      for (const pos of alpacaPositions) {
        positions.set(pos.symbol, {
          symbol: pos.symbol,
          quantity: parseInt(pos.qty),
          currentValue: parseFloat(pos.market_value),
          unrealizedPnL: parseFloat(pos.unrealized_pl),
        });
      }

      return positions;
    } catch (error) {
      console.error('Error fetching positions:', error);
      return new Map();
    }
  }

  /**
   * Get recent orders from Alpaca
   */
  async getRecentOrders(status: 'open' | 'closed' | 'all' = 'all'): Promise<any[]> {
    try {
      return await this.alpacaProvider.getOrders(status);
    } catch (error) {
      console.error('Error fetching orders:', error);
      return [];
    }
  }

  /**
   * Cancel a pending order
   */
  async cancelOrder(orderId: string): Promise<void> {
    try {
      await this.alpacaProvider.cancelOrder(orderId);
      console.log(`Order ${orderId} cancelled successfully`);
    } catch (error) {
      console.error(`Error cancelling order ${orderId}:`, error);
      throw error;
    }
  }

  /**
   * Check if market is open
   */
  async isMarketOpen(): Promise<boolean> {
    try {
      const today = new Date();
      const marketHours = await this.alpacaProvider.getMarketHours(today);
      
      if (!marketHours) {
        return false;
      }

      const now = new Date();
      const openTime = new Date(`${marketHours.date}T${marketHours.open}`);
      const closeTime = new Date(`${marketHours.date}T${marketHours.close}`);

      return now >= openTime && now <= closeTime;
    } catch (error) {
      console.error('Error checking market hours:', error);
      return false;
    }
  }
}