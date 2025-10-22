/**
 * Alpaca Trading API Data Provider
 * Fetches real-time and historical market data from Alpaca
 */
import { DataProvider, PriceData } from '../../types/index.js';
export interface AlpacaConfig {
    readonly apiKey: string;
    readonly secretKey: string;
    readonly baseUrl?: string;
    readonly dataUrl?: string;
}
export declare class AlpacaDataProvider implements DataProvider {
    readonly name = "Alpaca Trading";
    private readonly config;
    constructor(config: AlpacaConfig);
    getPriceData(symbol: string, startDate: Date, endDate: Date): Promise<PriceData[]>;
    isAvailable(): Promise<boolean>;
    private convertAlpacaData;
    private generateMockData;
}
//# sourceMappingURL=AlpacaDataProvider.d.ts.map