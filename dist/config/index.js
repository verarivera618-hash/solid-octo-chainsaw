/**
 * Configuration management for the backtesting framework
 * Centralized configuration with environment-specific overrides
 */
import { BacktestConfig } from '../types/index.js';
import dotenv from 'dotenv';
// Load environment variables
dotenv.config();
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
    alpaca: {
        apiKey: process.env.ALPACA_API_KEY || '',
        secretKey: process.env.ALPACA_SECRET_KEY || '',
        baseUrl: process.env.ALPACA_BASE_URL || 'https://paper-api.alpaca.markets',
        dryRun: process.env.ALPACA_DRY_RUN !== 'false', // Default to true for safety
    },
};
export const config = defaultConfig;
export const getConfig = () => config;
//# sourceMappingURL=index.js.map