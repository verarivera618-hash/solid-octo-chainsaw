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
    level: (process.env['LOG_LEVEL'] as any) || 'info',
    file: './logs/backtest.log',
  },
};

export const config: AppConfig = defaultConfig;

export const getConfig = (): AppConfig => config;