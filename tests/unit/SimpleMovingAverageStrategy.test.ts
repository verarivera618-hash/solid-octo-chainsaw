/**
 * Unit tests for SimpleMovingAverageStrategy
 */

import { SimpleMovingAverageStrategy } from '../../src/strategies/SimpleMovingAverageStrategy.js';
import { PriceData } from '../../src/types/index.js';

describe('SimpleMovingAverageStrategy', () => {
  let strategy: SimpleMovingAverageStrategy;

  beforeEach(() => {
    strategy = new SimpleMovingAverageStrategy(5, 10, ['AAPL']);
  });

  describe('constructor', () => {
    it('should initialize with correct parameters', () => {
      expect(strategy.name).toBe('Simple Moving Average Crossover');
      expect(strategy.parameters.shortPeriod).toBe(5);
      expect(strategy.parameters.longPeriod).toBe(10);
      expect(strategy.parameters.symbols).toEqual(['AAPL']);
    });
  });

  describe('validate', () => {
    it('should return true for valid strategy', () => {
      expect(strategy.validate()).toBe(true);
    });

    it('should return false for invalid short period', () => {
      const invalidStrategy = new SimpleMovingAverageStrategy(0, 10, ['AAPL']);
      expect(invalidStrategy.validate()).toBe(false);
    });

    it('should return false for invalid long period', () => {
      const invalidStrategy = new SimpleMovingAverageStrategy(5, 0, ['AAPL']);
      expect(invalidStrategy.validate()).toBe(false);
    });

    it('should return false when short period >= long period', () => {
      const invalidStrategy = new SimpleMovingAverageStrategy(10, 5, ['AAPL']);
      expect(invalidStrategy.validate()).toBe(false);
    });

    it('should return false for empty symbols array', () => {
      const invalidStrategy = new SimpleMovingAverageStrategy(5, 10, []);
      expect(invalidStrategy.validate()).toBe(false);
    });
  });

  describe('generateSignals', () => {
    it('should return empty array for insufficient data', () => {
      const data = createMockData(5); // Less than long period
      const signals = strategy.generateSignals(data);
      expect(signals).toHaveLength(0);
    });

    it('should generate buy signal on bullish crossover', () => {
      const data = createMockDataWithCrossover('bullish');
      const signals = strategy.generateSignals(data);
      
      expect(signals).toHaveLength(1);
      expect(signals[0].action).toBe('buy');
      expect(signals[0].symbol).toBe('AAPL');
      expect(signals[0].strength).toBeGreaterThan(0);
    });

    it('should generate sell signal on bearish crossover', () => {
      const data = createMockDataWithCrossover('bearish');
      const signals = strategy.generateSignals(data);
      
      expect(signals).toHaveLength(1);
      expect(signals[0].action).toBe('sell');
      expect(signals[0].symbol).toBe('AAPL');
      expect(signals[0].strength).toBeGreaterThan(0);
    });

    it('should not generate signals when no crossover occurs', () => {
      const data = createMockData(20);
      const signals = strategy.generateSignals(data);
      expect(signals).toHaveLength(0);
    });
  });
});

function createMockData(length: number): PriceData[] {
  const data: PriceData[] = [];
  const basePrice = 100;
  
  for (let i = 0; i < length; i++) {
    data.push({
      timestamp: new Date(2023, 0, i + 1),
      symbol: 'AAPL',
      open: basePrice + i,
      high: basePrice + i + 2,
      low: basePrice + i - 2,
      close: basePrice + i + 1,
      volume: 1000000,
    });
  }
  
  return data;
}

function createMockDataWithCrossover(type: 'bullish' | 'bearish'): PriceData[] {
  const data: PriceData[] = [];
  const basePrice = 100;
  
  // Create data that will result in a crossover
  for (let i = 0; i < 15; i++) {
    let price = basePrice + i;
    
    if (type === 'bullish') {
      // Create upward trend that will cause short MA to cross above long MA
      if (i > 10) {
        price += 5; // Sharp increase
      }
    } else {
      // Create downward trend that will cause short MA to cross below long MA
      if (i > 10) {
        price -= 5; // Sharp decrease
      }
    }
    
    data.push({
      timestamp: new Date(2023, 0, i + 1),
      symbol: 'AAPL',
      open: price,
      high: price + 2,
      low: price - 2,
      close: price + 1,
      volume: 1000000,
    });
  }
  
  return data;
}