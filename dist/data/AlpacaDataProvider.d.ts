/**
 * Local Mock Data Provider
 * Generates realistic historical price data locally without external API calls
 * Renamed from AlpacaDataProvider to LocalDataProvider for clarity
 */
import type { DataProvider, PriceData } from '../types/index.js';
export declare class AlpacaDataProvider implements DataProvider {
    readonly name = "Local Mock Data Provider";
    isAvailable(): Promise<boolean>;
    getPriceData(symbol: string, startDate: Date, endDate: Date): Promise<readonly PriceData[]>;
    private generateMockData;
}
//# sourceMappingURL=AlpacaDataProvider.d.ts.map