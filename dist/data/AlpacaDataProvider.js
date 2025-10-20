/**
 * Alpaca Markets data provider
 * Fetches historical and real-time price data from Alpaca Markets API
 */
import AlpacaClient from '@alpacahq/alpaca-trade-api';
export class AlpacaDataProvider {
    name = 'Alpaca Markets';
    client;
    constructor(config) {
        this.client = new AlpacaClient({
            credentials: {
                key: config.apiKey,
                secret: config.secretKey,
            },
            rate_limit: true,
        });
    }
    async getPriceData(symbol, startDate, endDate) {
        try {
            console.log(`Fetching Alpaca data for ${symbol} from ${startDate.toISOString()} to ${endDate.toISOString()}`);
            // Convert dates to ISO strings for Alpaca API
            const start = startDate.toISOString().split('T')[0];
            const end = endDate.toISOString().split('T')[0];
            // Fetch historical bars from Alpaca
            const bars = await this.client.getBarsV2(symbol, {
                start,
                end,
                timeframe: '1Day', // Daily bars
                asof: undefined,
                feed: 'iex', // Use IEX feed for free data
                adjustment: 'raw',
                page_token: undefined,
                limit: 10000, // Max limit
                sort: 'asc',
            });
            // Convert Alpaca bars to our PriceData format
            const result = [];
            for await (const bar of bars) {
                result.push({
                    timestamp: new Date(bar.Timestamp),
                    open: bar.OpenPrice,
                    high: bar.HighPrice,
                    low: bar.LowPrice,
                    close: bar.ClosePrice,
                    volume: bar.Volume,
                });
            }
            return result;
        }
        catch (error) {
            console.error(`Error fetching data for ${symbol}:`, error);
            throw new Error(`Failed to fetch Alpaca data for ${symbol}: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
    }
    async isAvailable() {
        try {
            // Test API connectivity by fetching account info
            await this.client.getAccount();
            return true;
        }
        catch (error) {
            console.error('Alpaca API not available:', error);
            return false;
        }
    }
    /**
     * Get real-time quote for a symbol
     */
    async getQuote(symbol) {
        try {
            const quote = await this.client.getLatestQuote(symbol);
            return {
                bid: quote.BidPrice,
                ask: quote.AskPrice,
                last: quote.AskPrice, // Use ask price as last price
            };
        }
        catch (error) {
            console.error(`Error fetching quote for ${symbol}:`, error);
            return null;
        }
    }
    /**
     * Get current market status
     */
    async getMarketStatus() {
        try {
            const clock = await this.client.getClock();
            return {
                isOpen: clock.is_open,
                nextOpen: clock.next_open ? new Date(clock.next_open) : undefined,
                nextClose: clock.next_close ? new Date(clock.next_close) : undefined,
            };
        }
        catch (error) {
            console.error('Error fetching market status:', error);
            return { isOpen: false };
        }
    }
    /**
     * Get account information
     */
    async getAccount() {
        try {
            return await this.client.getAccount();
        }
        catch (error) {
            console.error('Error fetching account info:', error);
            throw error;
        }
    }
}
//# sourceMappingURL=AlpacaDataProvider.js.map