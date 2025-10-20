/**
 * Live Trade Executor
 * Executes real trades through a broker (e.g., Alpaca)
 * This replaces the simulated TradeExecutor for live trading
 */

import { AlpacaBroker } from '../brokers/AlpacaBroker.js';
import type { Trade, Signal, Position } from '../types/index.js';

export class LiveTradeExecutor {
  private broker: AlpacaBroker;
  private readonly enableTrading: boolean;

  constructor(broker: AlpacaBroker, enableTrading: boolean = false) {
    this.broker = broker;
    this.enableTrading = enableTrading;

    if (!enableTrading) {
      console.warn('⚠️  LiveTradeExecutor initialized in READ-ONLY mode. Set enableTrading=true to execute real trades.');
    }
  }

  /**
   * Validate broker credentials
   */
  async validateConnection(): Promise<boolean> {
    return await this.broker.validateCredentials();
  }

  /**
   * Execute a trade based on signal
   */
  async executeTrade(
    signal: Signal,
    riskAmount?: number
  ): Promise<Trade | null> {
    if (signal.action === 'hold') {
      console.log(`Signal for ${signal.symbol}: HOLD`);
      return null;
    }

    if (!this.enableTrading) {
      console.log(`🔒 READ-ONLY MODE: Would ${signal.action} ${signal.symbol} (strength: ${signal.strength})`);
      return null;
    }

    try {
      // Check if market is open
      const isOpen = await this.broker.isMarketOpen();
      if (!isOpen) {
        console.warn(`⚠️  Market is closed. Cannot execute trade for ${signal.symbol}.`);
        return null;
      }

      // Get current position (if any)
      const currentPosition = await this.broker.getPosition(signal.symbol);

      // Calculate quantity based on signal strength and available capital
      const account = await this.broker.getAccount();
      const availableCash = parseFloat(account.buying_power);
      
      // Get current market price
      const latestTrade = await this.broker.getLatestTrade(signal.symbol);
      const currentPrice = parseFloat(String(latestTrade.Price));

      let quantity: number;

      if (signal.action === 'buy') {
        // Calculate buy quantity
        const maxInvestment = riskAmount || availableCash * 0.1; // Default to 10% of buying power
        const maxShares = Math.floor(maxInvestment / currentPrice);
        quantity = Math.min(maxShares, Math.floor(signal.strength * 100));

        if (quantity <= 0) {
          console.warn(`⚠️  Insufficient funds to buy ${signal.symbol}`);
          return null;
        }

        // Execute market buy order
        const order = await this.broker.executeMarketOrder(
          signal.symbol,
          quantity,
          'buy'
        );

        return {
          id: order.id,
          symbol: signal.symbol,
          side: 'buy',
          quantity,
          price: currentPrice,
          timestamp: signal.timestamp,
          fees: 0, // Alpaca commission-free trading
        };

      } else if (signal.action === 'sell') {
        // Calculate sell quantity
        if (!currentPosition || currentPosition.quantity <= 0) {
          console.warn(`⚠️  No position to sell for ${signal.symbol}`);
          return null;
        }

        quantity = Math.floor(currentPosition.quantity * signal.strength);

        if (quantity <= 0) {
          console.warn(`⚠️  Calculated sell quantity is 0 for ${signal.symbol}`);
          return null;
        }

        // Execute market sell order
        const order = await this.broker.executeMarketOrder(
          signal.symbol,
          quantity,
          'sell'
        );

        return {
          id: order.id,
          symbol: signal.symbol,
          side: 'sell',
          quantity,
          price: currentPrice,
          timestamp: signal.timestamp,
          fees: 0, // Alpaca commission-free trading
        };
      }

      return null;

    } catch (error) {
      console.error(`✗ Failed to execute trade for ${signal.symbol}:`, error);
      throw error;
    }
  }

  /**
   * Execute a limit order trade
   */
  async executeLimitTrade(
    signal: Signal,
    limitPrice: number,
    riskAmount?: number
  ): Promise<any | null> {
    if (signal.action === 'hold') {
      return null;
    }

    if (!this.enableTrading) {
      console.log(`🔒 READ-ONLY MODE: Would ${signal.action} ${signal.symbol} at limit price $${limitPrice}`);
      return null;
    }

    try {
      const isOpen = await this.broker.isMarketOpen();
      if (!isOpen) {
        console.warn(`⚠️  Market is closed. Cannot execute trade for ${signal.symbol}.`);
        return null;
      }

      const currentPosition = await this.broker.getPosition(signal.symbol);
      const account = await this.broker.getAccount();
      const availableCash = parseFloat(account.buying_power);

      let quantity: number;

      if (signal.action === 'buy') {
        const maxInvestment = riskAmount || availableCash * 0.1;
        const maxShares = Math.floor(maxInvestment / limitPrice);
        quantity = Math.min(maxShares, Math.floor(signal.strength * 100));

        if (quantity <= 0) {
          console.warn(`⚠️  Insufficient funds to buy ${signal.symbol}`);
          return null;
        }

        return await this.broker.executeLimitOrder(
          signal.symbol,
          quantity,
          'buy',
          limitPrice
        );

      } else if (signal.action === 'sell') {
        if (!currentPosition || currentPosition.quantity <= 0) {
          console.warn(`⚠️  No position to sell for ${signal.symbol}`);
          return null;
        }

        quantity = Math.floor(currentPosition.quantity * signal.strength);

        if (quantity <= 0) {
          return null;
        }

        return await this.broker.executeLimitOrder(
          signal.symbol,
          quantity,
          'sell',
          limitPrice
        );
      }

      return null;

    } catch (error) {
      console.error(`✗ Failed to execute limit trade for ${signal.symbol}:`, error);
      throw error;
    }
  }

  /**
   * Get all current positions
   */
  async getPositions(): Promise<Position[]> {
    return await this.broker.getPositions();
  }

  /**
   * Get account information
   */
  async getAccountInfo() {
    return await this.broker.getAccount();
  }

  /**
   * Close a specific position
   */
  async closePosition(symbol: string): Promise<void> {
    if (!this.enableTrading) {
      console.log(`🔒 READ-ONLY MODE: Would close position for ${symbol}`);
      return;
    }

    await this.broker.closePosition(symbol);
  }

  /**
   * Close all positions (use with extreme caution!)
   */
  async closeAllPositions(): Promise<void> {
    if (!this.enableTrading) {
      console.log(`🔒 READ-ONLY MODE: Would close all positions`);
      return;
    }

    console.warn('⚠️  Closing ALL positions...');
    await this.broker.closeAllPositions();
  }

  /**
   * Get open orders
   */
  async getOpenOrders() {
    return await this.broker.getOrders('open');
  }

  /**
   * Cancel an order
   */
  async cancelOrder(orderId: string): Promise<void> {
    if (!this.enableTrading) {
      console.log(`🔒 READ-ONLY MODE: Would cancel order ${orderId}`);
      return;
    }

    await this.broker.cancelOrder(orderId);
  }
}
