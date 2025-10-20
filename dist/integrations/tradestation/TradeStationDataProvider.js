/**
 * TradeStation Data Provider
 * Fetches market data from TradeStation API
 * Note: Requires TradeStation account and API approval
 */
export class TradeStationDataProvider {
    name = 'TradeStation';
    config;
    accessToken = null;
    tokenExpiry = null;
    constructor(config) {
        this.config = {
            baseUrl: 'https://api.tradestation.com',
            dataUrl: 'https://api.tradestation.com/v3',
            ...config
        };
    }
    async getPriceData(symbol, startDate, endDate) {
        try {
            await this.ensureAuthenticated();
            const url = `${this.config.dataUrl}/marketdata/barcharts/${symbol}`;
            const params = new URLSearchParams({
                starttime: startDate.toISOString(),
                endtime: endDate.toISOString(),
                interval: 'Daily',
                unit: 'Minute'
            });
            const response = await fetch(`${url}?${params}`, {
                headers: {
                    'Authorization': `Bearer ${this.accessToken}`,
                    'Content-Type': 'application/json'
                }
            });
            if (!response.ok) {
                throw new Error(`TradeStation API error: ${response.status} ${response.statusText}`);
            }
            const data = await response.json();
            return this.convertTradeStationData(data.Bars || []);
        }
        catch (error) {
            console.error('Error fetching data from TradeStation:', error);
            // Fallback to mock data for development
            return this.generateMockData(symbol, startDate, endDate);
        }
    }
    async isAvailable() {
        try {
            await this.ensureAuthenticated();
            return this.accessToken !== null;
        }
        catch {
            return false;
        }
    }
    async ensureAuthenticated() {
        if (this.accessToken && this.tokenExpiry && new Date() < this.tokenExpiry) {
            return; // Token is still valid
        }
        await this.authenticate();
    }
    async authenticate() {
        try {
            const response = await fetch(`${this.config.baseUrl}/v2/security/authorize`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: new URLSearchParams({
                    grant_type: 'password',
                    client_id: this.config.clientId,
                    client_secret: this.config.clientSecret,
                    username: this.config.username,
                    password: this.config.password,
                    scope: 'read'
                })
            });
            if (!response.ok) {
                throw new Error(`Authentication failed: ${response.status} ${response.statusText}`);
            }
            const data = await response.json();
            this.accessToken = data.access_token;
            this.tokenExpiry = new Date(Date.now() + (data.expires_in * 1000) - 60000); // 1 minute buffer
        }
        catch (error) {
            console.error('TradeStation authentication failed:', error);
            throw error;
        }
    }
    convertTradeStationData(bars) {
        return bars.map(bar => ({
            symbol: bar.Symbol || 'UNKNOWN',
            timestamp: new Date(bar.Time),
            open: bar.Open,
            high: bar.High,
            low: bar.Low,
            close: bar.Close,
            volume: bar.Volume || 0
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
//# sourceMappingURL=TradeStationDataProvider.js.map