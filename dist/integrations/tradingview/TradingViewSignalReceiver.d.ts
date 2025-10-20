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
export declare class TradingViewSignalReceiver {
    private readonly webhookSecret?;
    private readonly strategies;
    constructor(webhookSecret?: string);
    /**
     * Register a strategy to receive signals
     */
    registerStrategy(strategyName: string, strategy: Strategy): void;
    /**
     * Process incoming webhook from TradingView
     */
    processWebhook(payload: TradingViewWebhookPayload): Promise<Signal | null>;
    /**
     * Create webhook endpoint handler for Express.js
     */
    createWebhookHandler(): (req: any, res: any) => Promise<void>;
    private validateWebhook;
    /**
     * Generate Pine Script alert message format
     */
    static generateAlertMessage(signal: Signal): string;
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
//# sourceMappingURL=TradingViewSignalReceiver.d.ts.map