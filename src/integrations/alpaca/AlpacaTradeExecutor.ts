/**
 * Alpaca Trading API Trade Executor
 * Executes live trades through Alpaca Trading API
 */

import { Trade, Signal, Position } from '../../types/index.js';
import Decimal from 'decimal.js';

export interface AlpacaTradeConfig {
  readonly apiKey: string;
  readonly secretKey: string;
  readonly baseUrl?: string;
  readonly paperTrading?: boolean;
}

export class AlpacaTradeExecutor {
  private readonly config: AlpacaTradeConfig;
  private readonly commission: number;
  private readonly slippage: number;

  constructor(config: AlpacaTradeConfig, commission: number = 0.001, slippage: number = 0.001) {
    this.config = {
      baseUrl: 'https://paper-api.alpaca.markets',
      paperTrading: true,
      ...config
    };
    this.commission = commission;
    this.slippage = slippage;
  }

  /**
   * Execute a live trade through Alpaca
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
      const order = await this.submitOrder(signal, currentPosition, availableCash);
      
      if (!order) {
        return null;
      }

      return {
        id: order.id,
        symbol: signal.symbol,
        side: signal.action,
        quantity: Math.abs(parseInt(order.qty)),
        price: parseFloat(order.filled_avg_price || order.limit_price || '0'),
        timestamp: new Date(order.created_at),
        fees: this.calculateFees(Math.abs(parseInt(order.qty)), parseFloat(order.filled_avg_price || '0')),
      };
    } catch (error) {
      console.error('Error executing trade with Alpaca:', error);
      return null;
    }
  }

  private async submitOrder(signal: Signal, currentPosition: Position | undefined, availableCash: number) {
    const quantity = this.calculateQuantity(signal, currentPosition, availableCash);
    
    if (quantity <= 0) {
      return null;
    }

    const orderData = {
      symbol: signal.symbol,
      qty: signal.action === 'buy' ? quantity.toString() : (-quantity).toString(),
      side: signal.action,
      type: 'market', // Could be 'limit', 'stop', etc.
      time_in_force: 'day',
      extended_hours: false
    };

    const response = await fetch(`${this.config.baseUrl}/v2/orders`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'APCA-API-KEY-ID': this.config.apiKey,
        'APCA-API-SECRET-KEY': this.config.secretKey,
      },
      body: JSON.stringify(orderData)
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Alpaca order submission failed: ${error}`);
    }

    return await response.json();
  }

  private calculateQuantity(
    signal: Signal,
    currentPosition: Position | undefined,
    availableCash: number
  ): number {
    if (signal.action === 'buy') {
      // Calculate position size based on available cash and signal strength
      const maxQuantity = Math.floor(availableCash / 100); // Assuming $100 per share
      return Math.min(maxQuantity, Math.floor(signal.strength * 100));
    } else {
      // Sell - use current position or signal strength
      const currentQuantity = currentPosition?.quantity || 0;
      return Math.floor(currentQuantity * signal.strength);
    }
  }

  private calculateFees(quantity: number, price: number): number {
    return quantity * price * this.commission;
  }

  /**
   * Get current account information
   */
  async getAccountInfo() {
    const response = await fetch(`${this.config.baseUrl}/v2/account`, {
      headers: {
        'APCA-API-KEY-ID': this.config.apiKey,
        'APCA-API-SECRET-KEY': this.config.secretKey,
      }
    });

    if (!response.ok) {
      throw new Error('Failed to fetch account info');
    }

    return await response.json();
  }

  /**
   * Get current positions
   */
  async getPositions() {
    const response = await fetch(`${this.config.baseUrl}/v2/positions`, {
      headers: {
        'APCA-API-KEY-ID': this.config.apiKey,
        'APCA-API-SECRET-KEY': this.config.secretKey,
      }
    });

    if (!response.ok) {
      throw new Error('Failed to fetch positions');
    }

    return await response.json();
  }
}