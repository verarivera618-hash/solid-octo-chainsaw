/**
 * Unit tests for Portfolio
 */

import { Portfolio } from '../../src/core/Portfolio.js';
import { Trade } from '../../src/types/index.js';

describe('Portfolio', () => {
  let portfolio: Portfolio;

  beforeEach(() => {
    portfolio = new Portfolio(100000);
  });

  describe('constructor', () => {
    it('should initialize with correct initial capital', () => {
      expect(portfolio.getCash()).toBe(100000);
      expect(portfolio.getTotalValue()).toBe(100000);
      expect(portfolio.getPositions()).toHaveLength(0);
    });
  });

  describe('updatePosition', () => {
    it('should create new position on buy trade', () => {
      const trade: Trade = {
        id: '1',
        symbol: 'AAPL',
        side: 'buy',
        quantity: 100,
        price: 150,
        timestamp: new Date(),
        fees: 15,
      };

      portfolio.updatePosition(trade);

      expect(portfolio.getCash()).toBe(100000 - 15000 - 15);
      expect(portfolio.getPositions()).toHaveLength(1);
      
      const position = portfolio.getPosition('AAPL');
      expect(position).toBeDefined();
      expect(position!.symbol).toBe('AAPL');
      expect(position!.quantity).toBe(100);
      expect(position!.averagePrice).toBe(150);
    });

    it('should update existing position on additional buy', () => {
      const trade1: Trade = {
        id: '1',
        symbol: 'AAPL',
        side: 'buy',
        quantity: 100,
        price: 150,
        timestamp: new Date(),
        fees: 15,
      };

      const trade2: Trade = {
        id: '2',
        symbol: 'AAPL',
        side: 'buy',
        quantity: 50,
        price: 160,
        timestamp: new Date(),
        fees: 8,
      };

      portfolio.updatePosition(trade1);
      portfolio.updatePosition(trade2);

      const position = portfolio.getPosition('AAPL');
      expect(position!.quantity).toBe(150);
      expect(position!.averagePrice).toBeCloseTo(153.33, 2); // (100*150 + 50*160) / 150
    });

    it('should close position on complete sell', () => {
      const buyTrade: Trade = {
        id: '1',
        symbol: 'AAPL',
        side: 'buy',
        quantity: 100,
        price: 150,
        timestamp: new Date(),
        fees: 15,
      };

      const sellTrade: Trade = {
        id: '2',
        symbol: 'AAPL',
        side: 'sell',
        quantity: 100,
        price: 160,
        timestamp: new Date(),
        fees: 16,
      };

      portfolio.updatePosition(buyTrade);
      portfolio.updatePosition(sellTrade);

      expect(portfolio.getPosition('AAPL')).toBeUndefined();
      expect(portfolio.getPositions()).toHaveLength(0);
    });

    it('should throw error on insufficient position for sell', () => {
      const sellTrade: Trade = {
        id: '1',
        symbol: 'AAPL',
        side: 'sell',
        quantity: 100,
        price: 160,
        timestamp: new Date(),
        fees: 16,
      };

      expect(() => portfolio.updatePosition(sellTrade))
        .toThrow('Insufficient position for sell trade: AAPL');
    });
  });

  describe('updateValue', () => {
    it('should update portfolio value based on current prices', () => {
      const buyTrade: Trade = {
        id: '1',
        symbol: 'AAPL',
        side: 'buy',
        quantity: 100,
        price: 150,
        timestamp: new Date(),
        fees: 15,
      };

      portfolio.updatePosition(buyTrade);

      const priceData = [{
        symbol: 'AAPL',
        timestamp: new Date(),
        open: 160,
        high: 165,
        low: 155,
        close: 160,
        volume: 1000000,
      }];

      portfolio.updateValue(priceData);

      const position = portfolio.getPosition('AAPL');
      expect(position!.unrealizedPnL).toBe(1000); // (160 - 150) * 100
    });
  });
});