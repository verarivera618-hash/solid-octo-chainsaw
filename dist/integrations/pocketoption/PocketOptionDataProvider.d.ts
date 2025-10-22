/**
 * Pocket Option Data Provider
 * Fetches binary options data from Pocket Option
 * Note: Pocket Option has limited public API access
 */
import { DataProvider, PriceData } from '../../types/index.js';
export interface PocketOptionConfig {
    readonly apiKey?: string;
    readonly baseUrl?: string;
    readonly timeout?: number;
}
export interface BinaryOptionData extends PriceData {
    readonly expiry: Date;
    readonly optionType: 'call' | 'put';
    readonly strikePrice: number;
    readonly payout: number;
}
export declare class PocketOptionDataProvider implements DataProvider {
    readonly name = "Pocket Option";
    private readonly config;
    constructor(config?: PocketOptionConfig);
    getPriceData(symbol: string, startDate: Date, endDate: Date): Promise<PriceData[]>;
    isAvailable(): Promise<boolean>;
    private generateMockBinaryData;
    /**
     * Get binary options specific data
     */
    getBinaryOptionData(symbol: string, expiryMinutes?: number): Promise<BinaryOptionData[]>;
}
//# sourceMappingURL=PocketOptionDataProvider.d.ts.map