/**
 * Alpaca data provider
 * Fetches real market data from Alpaca Markets API
 */
import { DataProvider, PriceData } from '../types/index.js';
export declare class AlpacaDataProvider implements DataProvider {
    readonly name = "Alpaca Markets";
    private alpaca;
    constructor(apiKey: string, secretKey: string, baseUrl?: string);
    getPriceData(symbol: string, startDate: Date, endDate: Date): Promise<PriceData[]>;
    isAvailable(): Promise<boolean>;
    /**
     * Get current market price for a symbol
     */
    getCurrentPrice(symbol: string): Promise<number>;
    /**
     * Get account information
     */
    getAccountInfo(): Promise<any>;
    /**
     * Get current positions
     */
    getPositions(): Promise<any>;
}
//# sourceMappingURL=AlpacaDataProvider.d.ts.map