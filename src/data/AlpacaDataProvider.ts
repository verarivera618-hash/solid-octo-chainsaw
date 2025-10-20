/**
 * Alpaca data provider
 * Fetches real market data from Alpaca Markets API
 */

import type { DataProvider, PriceData } from '../types/index.js';
import Alpaca from '@alpacahq/alpaca-trade-api';

export class AlpacaDataProvider implements DataProvider {
  public readonly name = 'Alpaca Markets';
  private alpaca: Alpaca;

  constructor(apiKey: string, secretKey: string, baseUrl: string = 'https://paper-api.alpaca.markets') {
    this.alpaca = new Alpaca({
      key: apiKey,
      secret: secretKey,
      baseUrl: baseUrl,
      usePolygon: false, // Use Alpaca's data feed
    });
  }

  async getPriceData(symbol: string, startDate: Date, endDate: Date): Promise<PriceData[]> {
    try {
      console.log(`Fetching Alpaca data for ${symbol} from ${startDate.toISOString()} to ${endDate.toISOString()}`);
      
      // Get historical bars from Alpaca
      const bars = await this.alpaca.getBarsV2(symbol, {
        start: startDate.toISOString(),
        end: endDate.toISOString(),
        timeframe: '1Day',
        adjustment: 'raw',
      });

      const priceData: PriceData[] = [];
      
      for await (const bar of bars) {
        priceData.push({
          timestamp: new Date(bar.Timestamp),
          open: bar.OpenPrice,
          high: bar.HighPrice,
          low: bar.LowPrice,
          close: bar.ClosePrice,
          volume: bar.Volume,
        });
      }

      console.log(`Retrieved ${priceData.length} data points for ${symbol}`);
      return priceData;
    } catch (error) {
      console.error(`Error fetching data for ${symbol}:`, error);
      throw new Error(`Failed to fetch data for ${symbol}: ${error}`);
    }
  }

  async isAvailable(): Promise<boolean> {
    try {
      // Test API connection by getting account info
      await this.alpaca.getAccount();
      return true;
    } catch (error) {
      console.error('Alpaca API not available:', error);
      return false;
    }
  }

  /**
   * Get current market price for a symbol
   */
  async getCurrentPrice(symbol: string): Promise<number> {
    try {
      const quote = await this.alpaca.getLatestQuote(symbol);
      return (quote.BidPrice + quote.AskPrice) / 2; // Mid price
    } catch (error) {
      console.error(`Error getting current price for ${symbol}:`, error);
      throw error;
    }
  }

  /**
   * Get account information
   */
  async getAccountInfo() {
    try {
      return await this.alpaca.getAccount();
    } catch (error) {
      console.error('Error getting account info:', error);
      throw error;
    }
  }

  /**
   * Get current positions
   */
  async getPositions() {
    try {
      return await this.alpaca.getPositions();
    } catch (error) {
      console.error('Error getting positions:', error);
      throw error;
    }
  }
}