/**
 * Local Mock Data Provider
 * Generates realistic historical price data locally without external API calls
 * Renamed from AlpacaDataProvider to LocalDataProvider for clarity
 */

import type { DataProvider, PriceData } from '../types/index.js';

export class AlpacaDataProvider implements DataProvider {
  public readonly name = 'Local Mock Data Provider';

  async isAvailable(): Promise<boolean> {
    // Always available - no external dependencies
    return true;
  }

  async getPriceData(symbol: string, startDate: Date, endDate: Date): Promise<readonly PriceData[]> {
    console.log(`[LOCAL] Generating mock data for ${symbol} from ${startDate.toISOString()} to ${endDate.toISOString()}`);
    
    // Generate realistic mock data locally
    return this.generateMockData(symbol, startDate, endDate);
  }

  private generateMockData(symbol: string, startDate: Date, endDate: Date): PriceData[] {
    const data: PriceData[] = [];
    const currentDate = new Date(startDate);
    
    // Seed price based on symbol for consistency
    let price = 100 + (symbol.charCodeAt(0) % 50);
    
    while (currentDate <= endDate) {
      // Skip weekends
      if (currentDate.getDay() !== 0 && currentDate.getDay() !== 6) {
        // Generate realistic price movement with some volatility
        const volatility = 0.02; // 2% daily volatility
        const change = (Math.random() - 0.5) * volatility;
        price = price * (1 + change);
        
        // Generate OHLC data
        const dailyRange = price * 0.015; // 1.5% intraday range
        const high = price + (Math.random() * dailyRange);
        const low = price - (Math.random() * dailyRange);
        const open = low + (Math.random() * (high - low));
        const close = low + (Math.random() * (high - low));
        
        // Generate realistic volume
        const baseVolume = 1000000;
        const volume = Math.floor(baseVolume * (0.5 + Math.random()));
        
        data.push({
          symbol,
          timestamp: new Date(currentDate),
          open: Math.round(open * 100) / 100,
          high: Math.round(high * 100) / 100,
          low: Math.round(low * 100) / 100,
          close: Math.round(close * 100) / 100,
          volume,
        });
        
        // Update price for next day
        price = close;
      }
      
      currentDate.setDate(currentDate.getDate() + 1);
    }
    
    return data;
  }
}
