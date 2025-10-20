/**
 * Alpaca Broker Integration
 * Handles live trading execution through Alpaca Markets API
 */

import Alpaca from '@alpacahq/alpaca-trade-api';
import type { Position } from '../types/index.js';

export interface AlpacaConfig {
  apiKey: string;
  apiSecret: string;
  paper: boolean; // true for paper trading, false for live
  baseUrl?: string | undefined;
}

export class AlpacaBroker {
  private client: Alpaca;
  private readonly paper: boolean;

  constructor(config: AlpacaConfig) {
    this.paper = config.paper;
    
    // Validate credentials
    if (!config.apiKey || !config.apiSecret) {
      throw new Error('Alpaca API credentials are required. Please set ALPACA_API_KEY and ALPACA_API_SECRET environment variables.');
    }

    // Initialize Alpaca client
    this.client = new Alpaca({
      keyId: config.apiKey,
      secretKey: config.apiSecret,
      paper: config.paper,
      baseUrl: config.baseUrl,
    });
  }

  /**
   * Test connection and validate credentials
   */
  async validateCredentials(): Promise<boolean> {
    try {
      const account = await this.client.getAccount();
      console.log(`✓ Alpaca credentials validated successfully`);
      console.log(`  Account ID: ${account.id}`);
      console.log(`  Status: ${account.status}`);
      console.log(`  Trading Mode: ${this.paper ? 'PAPER' : 'LIVE'}`);
      console.log(`  Equity: $${parseFloat(account.equity).toFixed(2)}`);
      console.log(`  Buying Power: $${parseFloat(account.buying_power).toFixed(2)}`);
      return true;
    } catch (error) {
      console.error('✗ Alpaca credential validation failed:', error);
      throw new Error(`Failed to validate Alpaca credentials: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get account information
   */
  async getAccount() {
    return await this.client.getAccount();
  }

  /**
   * Get current positions
   */
  async getPositions(): Promise<Position[]> {
    const alpacaPositions = await this.client.getPositions();
    
    return alpacaPositions.map((pos: any) => ({
      symbol: pos.symbol,
      quantity: parseFloat(pos.qty),
      averagePrice: parseFloat(pos.avg_entry_price),
      currentPrice: parseFloat(pos.current_price),
      marketValue: parseFloat(pos.market_value),
      unrealizedPnL: parseFloat(pos.unrealized_pl),
      realizedPnL: 0,
      unrealizedPLPercent: parseFloat(pos.unrealized_plpc),
    }));
  }

  /**
   * Get a specific position
   */
  async getPosition(symbol: string): Promise<Position | null> {
    try {
      const pos = await this.client.getPosition(symbol);
      return {
        symbol: pos.symbol,
        quantity: parseFloat(pos.qty),
        averagePrice: parseFloat(pos.avg_entry_price),
        currentPrice: parseFloat(pos.current_price),
        marketValue: parseFloat(pos.market_value),
        unrealizedPnL: parseFloat(pos.unrealized_pl),
        realizedPnL: 0,
        unrealizedPLPercent: parseFloat(pos.unrealized_plpc),
      };
    } catch (error) {
      return null; // Position doesn't exist
    }
  }

  /**
   * Execute a market order
   */
  async executeMarketOrder(
    symbol: string,
    quantity: number,
    side: 'buy' | 'sell'
  ): Promise<any> {
    try {
      const order = await this.client.createOrder({
        symbol,
        qty: quantity,
        side,
        type: 'market',
        time_in_force: 'day',
      });

      console.log(`✓ ${side.toUpperCase()} order executed: ${quantity} shares of ${symbol}`);
      return order;
    } catch (error) {
      console.error(`✗ Failed to execute ${side} order for ${symbol}:`, error);
      throw error;
    }
  }

  /**
   * Execute a limit order
   */
  async executeLimitOrder(
    symbol: string,
    quantity: number,
    side: 'buy' | 'sell',
    limitPrice: number
  ): Promise<any> {
    try {
      const order = await this.client.createOrder({
        symbol,
        qty: quantity,
        side,
        type: 'limit',
        time_in_force: 'day',
        limit_price: limitPrice,
      });

      console.log(`✓ ${side.toUpperCase()} limit order placed: ${quantity} shares of ${symbol} at $${limitPrice}`);
      return order;
    } catch (error) {
      console.error(`✗ Failed to execute ${side} limit order for ${symbol}:`, error);
      throw error;
    }
  }

  /**
   * Cancel an order
   */
  async cancelOrder(orderId: string): Promise<void> {
    await this.client.cancelOrder(orderId);
  }

  /**
   * Get all open orders
   */
  async getOrders(status: 'open' | 'closed' | 'all' = 'open') {
    return await this.client.getOrders({
      status,
      limit: 100,
      nested: true,
    } as any);
  }

  /**
   * Get latest market data for a symbol
   */
  async getLatestQuote(symbol: string) {
    return await this.client.getLatestQuote(symbol);
  }

  /**
   * Get latest trade for a symbol
   */
  async getLatestTrade(symbol: string) {
    return await this.client.getLatestTrade(symbol);
  }

  /**
   * Check if market is open
   */
  async isMarketOpen(): Promise<boolean> {
    const clock = await this.client.getClock();
    return clock.is_open;
  }

  /**
   * Get market calendar
   */
  async getCalendar(start?: string, end?: string) {
    return await this.client.getCalendar({ start, end });
  }

  /**
   * Close all positions (use with caution!)
   */
  async closeAllPositions(): Promise<void> {
    if (!this.paper) {
      console.warn('⚠️  WARNING: Closing all positions in LIVE trading mode!');
    }
    await this.client.closeAllPositions();
  }

  /**
   * Close a specific position
   */
  async closePosition(symbol: string): Promise<void> {
    await this.client.closePosition(symbol);
    console.log(`✓ Closed position for ${symbol}`);
  }
}
