/**
 * Configuration management for the backtesting framework
 * Centralized configuration with environment-specific overrides
 */
const defaultConfig = {
    database: {
        url: process.env.DATABASE_URL || 'sqlite:./data/backtest.db',
        maxConnections: 10,
    },
    dataProviders: {
        primary: 'yahoo',
        fallback: ['alpha-vantage', 'polygon'],
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
        level: process.env.LOG_LEVEL || 'info',
        file: './logs/backtest.log',
    },
};
export const config = defaultConfig;
export const getConfig = () => config;
//# sourceMappingURL=index.js.map