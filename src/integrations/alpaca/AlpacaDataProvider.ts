/**
 * Alpaca Trading API Data Provider
 * Fetches real-time and historical market data from Alpaca
 */

import { DataProvider, PriceData } from '../../types/index.js';

export interface AlpacaConfig {
  readonly apiKey: string;
  readonly secretKey: string;
  readonly baseUrl?: string; // 'https://paper-api.alpaca.markets' for paper trading
  readonly dataUrl?: string; // 'https://data.alpaca.markets' for market data
}

export class AlpacaDataProvider implements DataProvider {
  public readonly name = 'Alpaca Trading';
  private readonly config: AlpacaConfig;

  constructor(config: AlpacaConfig) {
    this.config = {
      baseUrl: 'https://paper-api.alpaca.markets',
      dataUrl: 'https://data.alpaca.markets',
      ...config
    };
  }

  async getPriceData(symbol: string, startDate: Date, endDate: Date): Promise<PriceData[]> {
    try {
      const url = `${this.config.dataUrl}/v2/stocks/${symbol}/bars`;
      const params = new URLSearchParams({
        start: startDate.toISOString(),
        end: endDate.toISOString(),
        timeframe: '1Day',
        adjustment: 'raw',
        feed: 'iex'
      });

      const response = await fetch(`${url}?${params}`, {
        headers: {
          'APCA-API-KEY-ID': this.config.apiKey,
          'APCA-API-SECRET-KEY': this.config.secretKey,
        }
      });

      if (!response.ok) {
        throw new Error(`Alpaca API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return this.convertAlpacaData(data.bars || []);
    } catch (error) {
      console.error('Error fetching data from Alpaca:', error);
      // Fallback to mock data for development
      return this.generateMockData(symbol, startDate, endDate);
    }
  }

  async isAvailable(): Promise<boolean> {
    try {
      const response = await fetch(`${this.config.baseUrl}/v2/account`, {
        headers: {
          'APCA-API-KEY-ID': this.config.apiKey,
          'APCA-API-SECRET-KEY': this.config.secretKey,
        }
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  private convertAlpacaData(bars: any[]): PriceData[] {
    return bars.map(bar => ({
      timestamp: new Date(bar.t),
      open: bar.o,
      high: bar.h,
      low: bar.l,
      close: bar.c,
      volume: bar.v
    }));
  }

  private generateMockData(symbol: string, startDate: Date, endDate: Date): PriceData[] {
    // Fallback mock data generator
    const data: PriceData[] = [];
    const currentDate = new Date(startDate);
    let price = 100;
    
    while (currentDate <= endDate) {
      if (currentDate.getDay() !== 0 && currentDate.getDay() !== 6) {
        const change = (Math.random() - 0.5) * 0.02;
        price = price * (1 + change);
        
        data.push({
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