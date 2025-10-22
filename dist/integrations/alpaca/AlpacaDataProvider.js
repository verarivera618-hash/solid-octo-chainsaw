/**
 * Alpaca Trading API Data Provider
 * Fetches real-time and historical market data from Alpaca
 */
export class AlpacaDataProvider {
    name = 'Alpaca Trading';
    config;
    constructor(config) {
        this.config = {
            baseUrl: 'https://paper-api.alpaca.markets',
            dataUrl: 'https://data.alpaca.markets',
            ...config
        };
    }
    async getPriceData(symbol, startDate, endDate) {
        try {
            const url = `${this.config.dataUrl}/v2/stocks/${symbol}/bars`;
            const params = new URLSearchParams({
                start: startDate.toISOString(),
                end: endDate.toISOString(),
                timeframe: '1Day',
                adjustment: 'raw',
                feed: 'iex'
            });
            const response = await fetch(`${url}?${params}`, {
                headers: {
                    'APCA-API-KEY-ID': this.config.apiKey,
                    'APCA-API-SECRET-KEY': this.config.secretKey,
                }
            });
            if (!response.ok) {
                throw new Error(`Alpaca API error: ${response.status} ${response.statusText}`);
            }
            const data = await response.json();
            return this.convertAlpacaData(data.bars || []);
        }
        catch (error) {
            console.error('Error fetching data from Alpaca:', error);
            // Fallback to mock data for development
            return this.generateMockData(symbol, startDate, endDate);
        }
    }
    async isAvailable() {
        try {
            const response = await fetch(`${this.config.baseUrl}/v2/account`, {
                headers: {
                    'APCA-API-KEY-ID': this.config.apiKey,
                    'APCA-API-SECRET-KEY': this.config.secretKey,
                }
            });
            return response.ok;
        }
        catch {
            return false;
        }
    }
    convertAlpacaData(bars) {
        return bars.map(bar => ({
            symbol: bar.S || 'UNKNOWN', // Symbol from Alpaca response
            timestamp: new Date(bar.t),
            open: bar.o,
            high: bar.h,
            low: bar.l,
            close: bar.c,
            volume: bar.v
        }));
    }
    generateMockData(symbol, startDate, endDate) {
        // Fallback mock data generator
        const data = [];
        const currentDate = new Date(startDate);
        let price = 100;
        while (currentDate <= endDate) {
            if (currentDate.getDay() !== 0 && currentDate.getDay() !== 6) {
                const change = (Math.random() - 0.5) * 0.02;
                price = price * (1 + change);
                data.push({
                    symbol,
                    timestamp: new Date(currentDate),
                    open: Math.round(price * 0.99 * 100) / 100,
                    high: Math.round(price * 1.01 * 100) / 100,
                    low: Math.round(price * 0.98 * 100) / 100,
                    close: Math.round(price * 100) / 100,
                    volume: Math.floor(Math.random() * 1000000) + 100000,
                });
            }
            currentDate.setDate(currentDate.getDate() + 1);
        }
        return data;
    }
}
//# sourceMappingURL=AlpacaDataProvider.js.map