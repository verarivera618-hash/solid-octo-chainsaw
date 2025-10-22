/**
 * TradingView Signal Receiver
 * Receives trading signals from TradingView Pine Script alerts via webhooks
 */

import { Signal } from '../../types/index.js';
import { Strategy } from '../../types/index.js';

export interface TradingViewWebhookPayload {
  readonly symbol: string;
  readonly action: 'buy' | 'sell' | 'hold';
  readonly strength: number;
  readonly timestamp: string;
  readonly reason: string;
  readonly price?: number;
  readonly timeframe?: string;
  readonly strategy_name?: string;
}

export class TradingViewSignalReceiver {
  private readonly webhookSecret?: string;
  private readonly strategies: Map<string, Strategy> = new Map();

  constructor(webhookSecret?: string) {
    this.webhookSecret = webhookSecret;
  }

  /**
   * Register a strategy to receive signals
   */
  registerStrategy(strategyName: string, strategy: Strategy): void {
    this.strategies.set(strategyName, strategy);
  }

  /**
   * Process incoming webhook from TradingView
   */
  async processWebhook(payload: TradingViewWebhookPayload): Promise<Signal | null> {
    try {
      // Validate webhook (optional security check)
      if (this.webhookSecret && !this.validateWebhook(payload)) {
        throw new Error('Invalid webhook signature');
      }

      // Convert TradingView payload to internal Signal format
      const signal: Signal = {
        symbol: payload.symbol,
        action: payload.action,
        strength: Math.max(0, Math.min(1, payload.strength || 0.5)),
        timestamp: new Date(payload.timestamp),
        reason: payload.reason || `TradingView signal for ${payload.symbol}`
      };

      // Log the received signal
      console.log(`Received TradingView signal:`, {
        symbol: signal.symbol,
        action: signal.action,
        strength: signal.strength,
        timestamp: signal.timestamp.toISOString(),
        reason: signal.reason
      });

      return signal;
    } catch (error) {
      console.error('Error processing TradingView webhook:', error);
      return null;
    }
  }

  /**
   * Create webhook endpoint handler for Express.js
   */
  createWebhookHandler() {
    return async (req: any, res: any) => {
      try {
        const payload: TradingViewWebhookPayload = req.body;
        const signal = await this.processWebhook(payload);

        if (signal) {
          res.status(200).json({ 
            success: true, 
            message: 'Signal processed successfully',
            signal: {
              symbol: signal.symbol,
              action: signal.action,
              timestamp: signal.timestamp.toISOString()
            }
          });
        } else {
          res.status(400).json({ 
            success: false, 
            message: 'Failed to process signal' 
          });
        }
      } catch (error) {
        console.error('Webhook handler error:', error);
        res.status(500).json({ 
          success: false, 
          message: 'Internal server error' 
        });
      }
    };
  }

  private validateWebhook(payload: TradingViewWebhookPayload): boolean {
    // Implement webhook signature validation if needed
    // This is a placeholder - implement based on your security requirements
    return true;
  }

  /**
   * Generate Pine Script alert message format
   */
  static generateAlertMessage(signal: Signal): string {
    return JSON.stringify({
      symbol: signal.symbol,
      action: signal.action,
      strength: signal.strength,
      timestamp: signal.timestamp.toISOString(),
      reason: signal.reason
    });
  }
}

/**
 * Example Pine Script alert setup:
 * 
 * // In your Pine Script strategy:
 * if (buy_condition)
 *     alert("{\"symbol\":\"" + syminfo.ticker + "\",\"action\":\"buy\",\"strength\":0.8,\"timestamp\":\"" + str.tostring(time) + "\",\"reason\":\"Price broke above resistance\"}", alert.freq_once_per_bar)
 * 
 * if (sell_condition)
 *     alert("{\"symbol\":\"" + syminfo.ticker + "\",\"action\":\"sell\",\"strength\":0.9,\"timestamp\":\"" + str.tostring(time) + "\",\"reason\":\"RSI overbought\"}", alert.freq_once_per_bar)
 */