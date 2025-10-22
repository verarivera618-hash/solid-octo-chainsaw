/**
 * Alpaca Market Data provider
 * Fetches historical price data from Alpaca's Market Data v2 API
 */
import type { DataProvider, PriceData } from '../types/index.js';
export declare class AlpacaDataProvider implements DataProvider {
    readonly name = "Alpaca Market Data";
    private readonly apiBaseUrl;
    private readonly apiKeyId;
    private readonly apiSecretKey;
    constructor(apiBaseUrl?: string);
    isAvailable(): Promise<boolean>;
    getPriceData(symbol: string, startDate: Date, endDate: Date): Promise<readonly PriceData[]>;
}
//# sourceMappingURL=AlpacaDataProvider.d.ts.map