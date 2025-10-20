/**
 * Configuration management for the backtesting framework
 * Centralized configuration with environment-specific overrides
 */
const defaultConfig = {
    database: {
        url: process.env['DATABASE_URL'] || 'sqlite:./data/backtest.db',
        maxConnections: 10,
    },
    dataProviders: {
        primary: process.env['ALPACA_API_KEY'] ? 'alpaca' : 'yahoo',
        fallback: ['alpha-vantage', 'polygon', 'yahoo'],
    },
    backtesting: {
        defaultConfig: {
            startDate: new Date('2020-01-01'),
            endDate: new Date('2023-12-31'),
            initialCapital: 100000,
            commission: 0.001,
            slippage: 0.0005,
            symbols: ['AAPL', 'GOOGL', 'MSFT', 'TSLA'],
        },
        maxConcurrent: 4,
    },
    logging: {
        level: process.env['LOG_LEVEL'] || 'info',
        file: './logs/backtest.log',
    },
    alpaca: {
        apiKey: process.env['ALPACA_API_KEY'] || '',
        secretKey: process.env['ALPACA_SECRET_KEY'] || '',
        environment: process.env['ALPACA_ENVIRONMENT'] || 'paper',
        enabled: Boolean(process.env['ALPACA_API_KEY'] && process.env['ALPACA_SECRET_KEY']),
    },
};
export const config = defaultConfig;
export const getConfig = () => config;
//# sourceMappingURL=index.js.map