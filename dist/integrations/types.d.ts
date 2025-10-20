/**
 * Integration-specific type definitions
 * Extends core types for live trading and broker integrations
 */
import { Signal, Trade, Position, PriceData } from '../types/index.js';
export interface BrokerConfig {
    readonly name: string;
    readonly apiKey: string;
    readonly secretKey: string;
    readonly baseUrl: string;
    readonly paperTrading?: boolean;
}
export interface LiveTradingSignal extends Signal {
    readonly broker?: string;
    readonly priority?: number;
    readonly expiry?: Date;
}
export interface LiveTrade extends Trade {
    readonly broker: string;
    readonly orderId: string;
    readonly status: 'pending' | 'filled' | 'cancelled' | 'rejected';
    readonly filledQuantity?: number;
    readonly averagePrice?: number;
}
export interface BrokerAccount {
    readonly broker: string;
    readonly accountId: string;
    readonly buyingPower: number;
    readonly cash: number;
    readonly equity: number;
    readonly positions: Position[];
    readonly lastUpdated: Date;
}
export interface WebhookPayload {
    readonly source: string;
    readonly timestamp: string;
    readonly data: any;
    readonly signature?: string;
}
export interface RiskLimits {
    readonly maxPositionSize: number;
    readonly maxDailyLoss: number;
    readonly maxDrawdown: number;
    readonly stopLossPercentage: number;
    readonly maxOpenPositions: number;
}
export interface RiskMetrics {
    readonly currentDrawdown: number;
    readonly dailyPnL: number;
    readonly openPositions: number;
    readonly exposure: number;
}
export interface ExecutionContext {
    readonly strategy: string;
    readonly broker: string;
    readonly timestamp: Date;
    readonly marketData: PriceData[];
    readonly accountInfo: BrokerAccount;
    readonly riskMetrics: RiskMetrics;
}
export type OrderType = 'market' | 'limit' | 'stop' | 'stop_limit' | 'trailing_stop';
export type OrderSide = 'buy' | 'sell';
export type OrderStatus = 'new' | 'partially_filled' | 'filled' | 'cancelled' | 'rejected';
export interface OrderRequest {
    readonly symbol: string;
    readonly side: OrderSide;
    readonly quantity: number;
    readonly type: OrderType;
    readonly price?: number;
    readonly stopPrice?: number;
    readonly timeInForce?: 'day' | 'gtc' | 'ioc' | 'fok';
    readonly extendedHours?: boolean;
}
export interface BinaryOption {
    readonly symbol: string;
    readonly expiry: Date;
    readonly optionType: 'call' | 'put';
    readonly strikePrice: number;
    readonly payout: number;
    readonly currentPrice: number;
}
export interface BinaryOptionTrade extends Trade {
    readonly optionType: 'call' | 'put';
    readonly expiry: Date;
    readonly payout: number;
    readonly result?: 'win' | 'loss' | 'pending';
}
export interface DataProviderConfig {
    readonly name: string;
    readonly apiKey?: string;
    readonly baseUrl: string;
    readonly rateLimit?: number;
    readonly timeout?: number;
}
export interface RealTimeData extends PriceData {
    readonly bid: number;
    readonly ask: number;
    readonly spread: number;
    readonly lastUpdate: Date;
}
export interface NotificationConfig {
    readonly email?: {
        readonly enabled: boolean;
        readonly smtp: string;
        readonly to: string[];
    };
    readonly webhook?: {
        readonly enabled: boolean;
        readonly url: string;
        readonly secret?: string;
    };
    readonly discord?: {
        readonly enabled: boolean;
        readonly webhookUrl: string;
    };
}
export interface TradeNotification {
    readonly type: 'trade_executed' | 'trade_filled' | 'trade_cancelled' | 'error';
    readonly trade: LiveTrade;
    readonly message: string;
    readonly timestamp: Date;
}
//# sourceMappingURL=types.d.ts.map