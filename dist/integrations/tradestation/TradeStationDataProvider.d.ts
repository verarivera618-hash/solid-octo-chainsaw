/**
 * TradeStation Data Provider
 * Fetches market data from TradeStation API
 * Note: Requires TradeStation account and API approval
 */
import { DataProvider, PriceData } from '../../types/index.js';
export interface TradeStationConfig {
    readonly clientId: string;
    readonly clientSecret: string;
    readonly username: string;
    readonly password: string;
    readonly baseUrl?: string;
    readonly dataUrl?: string;
}
export declare class TradeStationDataProvider implements DataProvider {
    readonly name = "TradeStation";
    private readonly config;
    private accessToken;
    private tokenExpiry;
    constructor(config: TradeStationConfig);
    getPriceData(symbol: string, startDate: Date, endDate: Date): Promise<PriceData[]>;
    isAvailable(): Promise<boolean>;
    private ensureAuthenticated;
    private authenticate;
    private convertTradeStationData;
    private generateMockData;
}
//# sourceMappingURL=TradeStationDataProvider.d.ts.map