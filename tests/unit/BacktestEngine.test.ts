/**
 * Unit tests for BacktestEngine
 */

import { BacktestEngine } from '../../src/core/BacktestEngine.js';
import { SimpleMovingAverageStrategy } from '../../src/strategies/SimpleMovingAverageStrategy.js';
import { BacktestConfig, PriceData } from '../../src/types/index.js';

describe('BacktestEngine', () => {
  let engine: BacktestEngine;
  let config: BacktestConfig;

  beforeEach(() => {
    config = {
      startDate: new Date('2023-01-01'),
      endDate: new Date('2023-12-31'),
      initialCapital: 100000,
      commission: 0.001,
      slippage: 0.0005,
      symbols: ['AAPL', 'GOOGL'],
    };
    engine = new BacktestEngine(config);
  });

  describe('constructor', () => {
    it('should initialize with correct configuration', () => {
      expect(engine).toBeDefined();
      expect(engine.getPortfolio().getCash()).toBe(100000);
    });
  });

  describe('runBacktest', () => {
    it('should throw error for invalid strategy', async () => {
      const invalidStrategy = {
        name: 'Invalid',
        description: 'Invalid strategy',
        parameters: {},
        generateSignals: () => [],
        validate: () => false,
      } as any;

      const marketData = new Map();
      
      await expect(engine.runBacktest(invalidStrategy, marketData))
        .rejects.toThrow('Invalid strategy: Invalid');
    });

    it('should run backtest successfully with valid strategy', async () => {
      const strategy = new SimpleMovingAverageStrategy(5, 10, ['AAPL']);
      const marketData = createMockMarketData();
      
      const result = await engine.runBacktest(strategy, marketData);
      
      expect(result).toBeDefined();
      expect(result.totalTrades).toBeGreaterThanOrEqual(0);
      expect(result.equityCurve).toBeDefined();
      expect(result.equityCurve.length).toBeGreaterThan(0);
    });
  });
});

function createMockMarketData(): Map<string, PriceData[]> {
  const data: PriceData[] = [];
  const startDate = new Date('2023-01-01');
  
  for (let i = 0; i < 100; i++) {
    const date = new Date(startDate);
    date.setDate(date.getDate() + i);
    
    data.push({
      timestamp: date,
      open: 100 + i,
      high: 105 + i,
      low: 95 + i,
      close: 102 + i,
      volume: 1000000,
    });
  }
  
  const marketData = new Map();
  marketData.set('AAPL', data);
  return marketData;
}