/**
 * Alpaca Markets data provider
 * Fetches real-time and historical market data from Alpaca API
 */
import fetch from 'node-fetch';
export class AlpacaDataProvider {
    name = 'Alpaca Markets';
    config;
    isConfigured = false;
    constructor() {
        this.config = this.loadConfig();
        this.isConfigured = this.validateConfig();
    }
    loadConfig() {
        const environment = process.env['ALPACA_ENVIRONMENT'] || 'paper';
        const isPaper = environment === 'paper';
        return {
            apiKey: process.env['ALPACA_API_KEY'] || '',
            secretKey: process.env['ALPACA_SECRET_KEY'] || '',
            baseUrl: isPaper
                ? 'https://paper-api.alpaca.markets'
                : 'https://api.alpaca.markets',
            dataBaseUrl: 'https://data.alpaca.markets',
        };
    }
    validateConfig() {
        if (!this.config.apiKey || !this.config.secretKey) {
            console.warn('Alpaca API credentials not configured. Please set ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables.');
            return false;
        }
        return true;
    }
    async getPriceData(symbol, startDate, endDate) {
        if (!this.isConfigured) {
            throw new Error('Alpaca API credentials not configured. Please check your environment variables.');
        }
        try {
            // Construct the API endpoint
            const endpoint = `${this.config.dataBaseUrl}/v2/stocks/${symbol}/bars`;
            // Format dates to RFC3339
            const start = this.formatDate(startDate);
            const end = this.formatDate(endDate);
            // Prepare request parameters
            const params = new URLSearchParams({
                start,
                end,
                timeframe: '1Day',
                adjustment: 'raw',
                feed: 'iex',
                limit: '10000',
                page_token: '',
            });
            const response = await fetch(`${endpoint}?${params}`, {
                method: 'GET',
                headers: {
                    'APCA-API-KEY-ID': this.config.apiKey,
                    'APCA-API-SECRET-KEY': this.config.secretKey,
                },
            });
            if (!response.ok) {
                throw new Error(`Alpaca API error: ${response.status} ${response.statusText}`);
            }
            const data = await response.json();
            // Transform Alpaca data format to our internal format
            return this.transformAlpacaData(data.bars || []);
        }
        catch (error) {
            console.error('Error fetching data from Alpaca:', error);
            throw error;
        }
    }
    async isAvailable() {
        if (!this.isConfigured) {
            return false;
        }
        try {
            // Test API connectivity by fetching account info
            const response = await fetch(`${this.config.baseUrl}/v2/account`, {
                method: 'GET',
                headers: {
                    'APCA-API-KEY-ID': this.config.apiKey,
                    'APCA-API-SECRET-KEY': this.config.secretKey,
                },
            });
            return response.ok;
        }
        catch (error) {
            console.error('Alpaca API availability check failed:', error);
            return false;
        }
    }
    async getAccountInfo() {
        if (!this.isConfigured) {
            throw new Error('Alpaca API credentials not configured');
        }
        const response = await fetch(`${this.config.baseUrl}/v2/account`, {
            method: 'GET',
            headers: {
                'APCA-API-KEY-ID': this.config.apiKey,
                'APCA-API-SECRET-KEY': this.config.secretKey,
            },
        });
        if (!response.ok) {
            throw new Error(`Failed to fetch account info: ${response.status}`);
        }
        return response.json();
    }
    async getPositions() {
        if (!this.isConfigured) {
            throw new Error('Alpaca API credentials not configured');
        }
        const response = await fetch(`${this.config.baseUrl}/v2/positions`, {
            method: 'GET',
            headers: {
                'APCA-API-KEY-ID': this.config.apiKey,
                'APCA-API-SECRET-KEY': this.config.secretKey,
            },
        });
        if (!response.ok) {
            throw new Error(`Failed to fetch positions: ${response.status}`);
        }
        return response.json();
    }
    transformAlpacaData(bars) {
        return bars.map(bar => ({
            timestamp: new Date(bar.t),
            open: bar.o,
            high: bar.h,
            low: bar.l,
            close: bar.c,
            volume: bar.v,
        }));
    }
    formatDate(date) {
        // Format date to RFC3339 format required by Alpaca
        return date.toISOString().split('.')[0] + 'Z';
    }
    /**
     * Place a trade order through Alpaca
     */
    async placeOrder(params) {
        if (!this.isConfigured) {
            throw new Error('Alpaca API credentials not configured');
        }
        const orderData = {
            symbol: params.symbol,
            qty: params.quantity,
            side: params.side,
            type: params.type || 'market',
            time_in_force: params.timeInForce || 'day',
            ...(params.limitPrice && { limit_price: params.limitPrice }),
        };
        const response = await fetch(`${this.config.baseUrl}/v2/orders`, {
            method: 'POST',
            headers: {
                'APCA-API-KEY-ID': this.config.apiKey,
                'APCA-API-SECRET-KEY': this.config.secretKey,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(orderData),
        });
        if (!response.ok) {
            const error = await response.text();
            throw new Error(`Failed to place order: ${response.status} - ${error}`);
        }
        return response.json();
    }
    /**
     * Get all orders
     */
    async getOrders(status) {
        if (!this.isConfigured) {
            throw new Error('Alpaca API credentials not configured');
        }
        const params = new URLSearchParams({
            status: status || 'all',
            limit: '500',
            direction: 'desc',
        });
        const response = await fetch(`${this.config.baseUrl}/v2/orders?${params}`, {
            method: 'GET',
            headers: {
                'APCA-API-KEY-ID': this.config.apiKey,
                'APCA-API-SECRET-KEY': this.config.secretKey,
            },
        });
        if (!response.ok) {
            throw new Error(`Failed to fetch orders: ${response.status}`);
        }
        return response.json();
    }
    /**
     * Cancel an order
     */
    async cancelOrder(orderId) {
        if (!this.isConfigured) {
            throw new Error('Alpaca API credentials not configured');
        }
        const response = await fetch(`${this.config.baseUrl}/v2/orders/${orderId}`, {
            method: 'DELETE',
            headers: {
                'APCA-API-KEY-ID': this.config.apiKey,
                'APCA-API-SECRET-KEY': this.config.secretKey,
            },
        });
        if (!response.ok) {
            throw new Error(`Failed to cancel order: ${response.status}`);
        }
    }
    /**
     * Get market hours for a specific date
     */
    async getMarketHours(date) {
        if (!this.isConfigured) {
            throw new Error('Alpaca API credentials not configured');
        }
        const dateStr = date.toISOString().split('T')[0];
        const response = await fetch(`${this.config.baseUrl}/v2/calendar?start=${dateStr}&end=${dateStr}`, {
            method: 'GET',
            headers: {
                'APCA-API-KEY-ID': this.config.apiKey,
                'APCA-API-SECRET-KEY': this.config.secretKey,
            },
        });
        if (!response.ok) {
            throw new Error(`Failed to fetch market hours: ${response.status}`);
        }
        const data = await response.json();
        return data[0] || null;
    }
}
//# sourceMappingURL=AlpacaDataProvider.js.map