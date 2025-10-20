/**
 * Alpaca Markets data provider
 * Fetches historical and real-time price data from Alpaca Markets API
 */
import type { DataProvider, PriceData } from '../types/index.js';
export interface AlpacaConfig {
    readonly apiKey: string;
    readonly secretKey: string;
    readonly baseUrl?: string;
    readonly dataUrl?: string;
}
export declare class AlpacaDataProvider implements DataProvider {
    readonly name = "Alpaca Markets";
    private readonly client;
    constructor(config: AlpacaConfig);
    getPriceData(symbol: string, startDate: Date, endDate: Date): Promise<PriceData[]>;
    isAvailable(): Promise<boolean>;
    /**
     * Get real-time quote for a symbol
     */
    getQuote(symbol: string): Promise<{
        bid: number;
        ask: number;
        last: number;
    } | null>;
    /**
     * Get current market status
     */
    getMarketStatus(): Promise<{
        isOpen: boolean;
        nextOpen?: Date;
        nextClose?: Date;
    }>;
    /**
     * Get account information
     */
    getAccount(): Promise<any>;
}
//# sourceMappingURL=AlpacaDataProvider.d.ts.map