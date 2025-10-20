/**
 * Yahoo Finance data provider
 * Fetches historical price data from Yahoo Finance API
 */
import { DataProvider, PriceData } from '../types/index.js';
export declare class YahooDataProvider implements DataProvider {
    readonly name = "Yahoo Finance";
    getPriceData(symbol: string, startDate: Date, endDate: Date): Promise<PriceData[]>;
    isAvailable(): Promise<boolean>;
    private generateMockData;
}
//# sourceMappingURL=YahooDataProvider.d.ts.map