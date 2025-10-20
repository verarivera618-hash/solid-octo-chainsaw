/**
 * Alpaca Market Data provider
 * Fetches historical price data from Alpaca's Market Data v2 API
 */
export class AlpacaDataProvider {
    name = 'Alpaca Market Data';
    apiBaseUrl;
    apiKeyId;
    apiSecretKey;
    constructor(apiBaseUrl = 'https://data.alpaca.markets') {
        this.apiBaseUrl = apiBaseUrl.replace(/\/$/, '');
        this.apiKeyId = process.env['APCA_API_KEY_ID'];
        this.apiSecretKey = process.env['APCA_API_SECRET_KEY'];
    }
    async isAvailable() {
        return Boolean(this.apiKeyId && this.apiSecretKey);
    }
    async getPriceData(symbol, startDate, endDate) {
        if (!this.apiKeyId || !this.apiSecretKey) {
            throw new Error('Alpaca credentials are missing. Set APCA_API_KEY_ID and APCA_API_SECRET_KEY.');
        }
        const timeframe = '1Day';
        const priceData = [];
        let pageToken = undefined;
        // Alpaca expects RFC3339 timestamps
        const startIso = startDate.toISOString();
        const endIso = endDate.toISOString();
        // Paginate until no more data
        // Limit defaults to 1000; keep default for fewer params
        // See: https://alpaca.markets/docs/api-references/market-data-api/stock-pricing-data/bars/
        while (true) {
            const url = new URL(`${this.apiBaseUrl}/v2/stocks/${encodeURIComponent(symbol)}/bars`);
            url.searchParams.set('timeframe', timeframe);
            url.searchParams.set('start', startIso);
            url.searchParams.set('end', endIso);
            url.searchParams.set('adjustment', 'raw');
            url.searchParams.set('limit', '1000');
            if (pageToken) {
                url.searchParams.set('page_token', pageToken);
            }
            const response = await fetch(url.toString(), {
                method: 'GET',
                headers: {
                    'APCA-API-KEY-ID': this.apiKeyId,
                    'APCA-API-SECRET-KEY': this.apiSecretKey,
                },
            });
            if (!response.ok) {
                const text = await response.text();
                throw new Error(`Alpaca API error (${response.status}): ${text}`);
            }
            const json = (await response.json());
            for (const bar of json.bars) {
                priceData.push({
                    symbol,
                    timestamp: new Date(bar.t),
                    open: bar.o,
                    high: bar.h,
                    low: bar.l,
                    close: bar.c,
                    volume: bar.v,
                });
            }
            if (!json.next_page_token) {
                break;
            }
            pageToken = json.next_page_token;
        }
        // Ensure sorted ascending by timestamp
        priceData.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
        return priceData;
    }
}
//# sourceMappingURL=AlpacaDataProvider.js.map