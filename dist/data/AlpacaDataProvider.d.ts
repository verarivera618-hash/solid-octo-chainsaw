/**
 * Alpaca Markets data provider
 * Fetches real-time and historical market data from Alpaca API
 */
import type { DataProvider, PriceData } from '../types/index.js';
export interface AlpacaConfig {
    apiKey: string;
    secretKey: string;
    baseUrl: string;
    dataBaseUrl: string;
}
export declare class AlpacaDataProvider implements DataProvider {
    readonly name = "Alpaca Markets";
    private config;
    private isConfigured;
    constructor();
    private loadConfig;
    private validateConfig;
    getPriceData(symbol: string, startDate: Date, endDate: Date): Promise<PriceData[]>;
    isAvailable(): Promise<boolean>;
    getAccountInfo(): Promise<any>;
    getPositions(): Promise<any[]>;
    private transformAlpacaData;
    private formatDate;
    /**
     * Place a trade order through Alpaca
     */
    placeOrder(params: {
        symbol: string;
        quantity: number;
        side: 'buy' | 'sell';
        type?: 'market' | 'limit';
        limitPrice?: number;
        timeInForce?: 'day' | 'gtc' | 'opg' | 'cls' | 'ioc' | 'fok';
    }): Promise<any>;
    /**
     * Get all orders
     */
    getOrders(status?: 'open' | 'closed' | 'all'): Promise<any[]>;
    /**
     * Cancel an order
     */
    cancelOrder(orderId: string): Promise<void>;
    /**
     * Get market hours for a specific date
     */
    getMarketHours(date: Date): Promise<any>;
}
//# sourceMappingURL=AlpacaDataProvider.d.ts.map