/**
 * Configuration management for the backtesting framework
 * Centralized configuration with environment-specific overrides
 */
import type { BacktestConfig } from '../types/index.js';
export interface AppConfig {
    readonly database: {
        readonly url: string;
        readonly maxConnections: number;
    };
    readonly dataProviders: {
        readonly primary: string;
        readonly fallback: string[];
    };
    readonly backtesting: {
        readonly defaultConfig: BacktestConfig;
        readonly maxConcurrent: number;
    };
    readonly alpaca: {
        readonly apiKey: string;
        readonly secretKey: string;
        readonly baseUrl: string;
        readonly dataUrl: string;
        readonly paperTrading: boolean;
    };
    readonly trading: {
        readonly enabled: boolean;
        readonly paperTrading: boolean;
        readonly maxPositionSize: number;
        readonly riskLimit: number;
    };
    readonly logging: {
        readonly level: 'debug' | 'info' | 'warn' | 'error';
        readonly file: string;
    };
}
export declare const config: AppConfig;
export declare const getConfig: () => AppConfig;
//# sourceMappingURL=index.d.ts.map