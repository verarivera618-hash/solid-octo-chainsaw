/**
 * Configuration management for the backtesting framework
 * Centralized configuration with environment-specific overrides
 */

import type { BacktestConfig } from '../types/index.js';

export interface AppConfig {
  readonly database: {
    readonly url: string;
    readonly maxConnections: number;
  };
  readonly dataProviders: {
    readonly primary: string;
    readonly fallback: string[];
  };
  readonly backtesting: {
    readonly defaultConfig: BacktestConfig;
    readonly maxConcurrent: number;
  };
  readonly alpaca: {
    readonly apiKey: string;
    readonly secretKey: string;
    readonly baseUrl: string;
    readonly dataUrl: string;
    readonly paperTrading: boolean;
  };
  readonly trading: {
    readonly enabled: boolean;
    readonly paperTrading: boolean;
    readonly maxPositionSize: number;
    readonly riskLimit: number;
  };
  readonly logging: {
    readonly level: 'debug' | 'info' | 'warn' | 'error';
    readonly file: string;
  };
}

const defaultConfig: AppConfig = {
  database: {
    url: process.env['DATABASE_URL'] || 'sqlite:./data/backtest.db',
    maxConnections: 10,
  },
  dataProviders: {
    primary: process.env['DATA_PROVIDER'] || 'yahoo',
    fallback: ['alpha-vantage', 'polygon', 'alpaca'],
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
  alpaca: {
    apiKey: process.env['ALPACA_API_KEY'] || '',
    secretKey: process.env['ALPACA_SECRET_KEY'] || '',
    baseUrl: process.env['ALPACA_BASE_URL'] || 'https://paper-api.alpaca.markets',
    dataUrl: process.env['ALPACA_DATA_URL'] || 'https://data.alpaca.markets',
    paperTrading: process.env['ALPACA_PAPER_TRADING'] !== 'false',
  },
  trading: {
    enabled: process.env['TRADING_ENABLED'] === 'true',
    paperTrading: process.env['ALPACA_PAPER_TRADING'] !== 'false',
    maxPositionSize: parseFloat(process.env['MAX_POSITION_SIZE'] || '10000'),
    riskLimit: parseFloat(process.env['RISK_LIMIT'] || '0.02'),
  },
  logging: {
    level: (process.env['LOG_LEVEL'] as any) || 'info',
    file: './logs/backtest.log',
  },
};

export const config: AppConfig = defaultConfig;

export const getConfig = (): AppConfig => config;