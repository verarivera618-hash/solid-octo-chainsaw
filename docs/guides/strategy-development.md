# Strategy Development Guide

This guide explains how to create custom trading strategies for the backtesting framework.

## Strategy Interface

All strategies must implement the `Strategy` interface:

```typescript
interface Strategy {
  readonly name: string;
  readonly description: string;
  readonly parameters: Record<string, unknown>;
  generateSignals(data: PriceData[]): Signal[];
  validate(): boolean;
}
```

## Creating a Custom Strategy

### 1. Basic Structure

```typescript
import { Strategy, Signal, PriceData } from '../types/index.js';

export class MyCustomStrategy implements Strategy {
  public readonly name = 'My Custom Strategy';
  public readonly description = 'Description of what this strategy does';
  public readonly parameters: Record<string, unknown>;

  constructor(
    private readonly param1: number,
    private readonly param2: string,
    private readonly symbols: string[]
  ) {
    this.parameters = {
      param1,
      param2,
      symbols,
    };
  }

  generateSignals(data: PriceData[]): Signal[] {
    const signals: Signal[] = [];
    
    // Your strategy logic here
    
    return signals;
  }

  validate(): boolean {
    // Validate your parameters
    return this.param1 > 0 && this.param2.length > 0;
  }
}
```

### 2. Signal Generation

Signals are the core output of your strategy. Each signal represents a trading decision:

```typescript
const signal: Signal = {
  symbol: 'AAPL',
  action: 'buy', // 'buy', 'sell', or 'hold'
  strength: 0.8, // Confidence level (0-1)
  timestamp: new Date(),
  reason: 'Price broke above resistance level',
};
```

### 3. Data Processing

Process historical price data to identify trading opportunities:

```typescript
generateSignals(data: PriceData[]): Signal[] {
  const signals: Signal[] = [];
  
  // Filter data for specific symbols
  const symbolData = data.filter(d => this.symbols.includes(d.symbol));
  
  // Sort by timestamp
  const sortedData = symbolData.sort((a, b) => 
    a.timestamp.getTime() - b.timestamp.getTime()
  );
  
  // Process data in windows or sequentially
  for (let i = this.lookbackPeriod; i < sortedData.length; i++) {
    const window = sortedData.slice(i - this.lookbackPeriod, i);
    const current = sortedData[i];
    
    // Your analysis logic here
    if (this.shouldBuy(window, current)) {
      signals.push({
        symbol: current.symbol,
        action: 'buy',
        strength: this.calculateStrength(window, current),
        timestamp: current.timestamp,
        reason: 'Custom buy condition met',
      });
    }
  }
  
  return signals;
}
```

### 4. Parameter Validation

Always validate your strategy parameters:

```typescript
validate(): boolean {
  return (
    this.param1 > 0 &&
    this.param2.length > 0 &&
    this.symbols.length > 0 &&
    this.lookbackPeriod > 0
  );
}
```

## Example: RSI Strategy

Here's a complete example of a Relative Strength Index (RSI) strategy:

```typescript
export class RSIStrategy implements Strategy {
  public readonly name = 'RSI Mean Reversion';
  public readonly description = 'Buy when RSI < 30, sell when RSI > 70';
  public readonly parameters: Record<string, unknown>;

  constructor(
    private readonly period: number = 14,
    private readonly oversoldLevel: number = 30,
    private readonly overboughtLevel: number = 70,
    private readonly symbols: string[] = ['AAPL']
  ) {
    this.parameters = {
      period,
      oversoldLevel,
      overboughtLevel,
      symbols,
    };
  }

  generateSignals(data: PriceData[]): Signal[] {
    const signals: Signal[] = [];
    
    for (const symbol of this.symbols) {
      const symbolData = data
        .filter(d => d.symbol === symbol)
        .sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
      
      if (symbolData.length < this.period + 1) continue;
      
      const rsiValues = this.calculateRSI(symbolData, this.period);
      
      for (let i = 1; i < rsiValues.length; i++) {
        const currentRSI = rsiValues[i];
        const previousRSI = rsiValues[i - 1];
        const currentPrice = symbolData[i + this.period];
        
        if (previousRSI <= this.oversoldLevel && currentRSI > this.oversoldLevel) {
          // RSI crossed above oversold level - buy signal
          signals.push({
            symbol,
            action: 'buy',
            strength: this.calculateStrength(currentRSI, this.oversoldLevel),
            timestamp: currentPrice.timestamp,
            reason: `RSI crossed above oversold level: ${currentRSI.toFixed(2)}`,
          });
        } else if (previousRSI >= this.overboughtLevel && currentRSI < this.overboughtLevel) {
          // RSI crossed below overbought level - sell signal
          signals.push({
            symbol,
            action: 'sell',
            strength: this.calculateStrength(this.overboughtLevel, currentRSI),
            timestamp: currentPrice.timestamp,
            reason: `RSI crossed below overbought level: ${currentRSI.toFixed(2)}`,
          });
        }
      }
    }
    
    return signals;
  }

  validate(): boolean {
    return (
      this.period > 0 &&
      this.oversoldLevel > 0 &&
      this.overboughtLevel > 100 &&
      this.oversoldLevel < this.overboughtLevel &&
      this.symbols.length > 0
    );
  }

  private calculateRSI(data: PriceData[], period: number): number[] {
    const rsi: number[] = [];
    const gains: number[] = [];
    const losses: number[] = [];
    
    // Calculate price changes
    for (let i = 1; i < data.length; i++) {
      const change = data[i].close - data[i - 1].close;
      gains.push(change > 0 ? change : 0);
      losses.push(change < 0 ? -change : 0);
    }
    
    // Calculate RSI
    for (let i = period - 1; i < gains.length; i++) {
      const avgGain = gains.slice(i - period + 1, i + 1).reduce((sum, gain) => sum + gain, 0) / period;
      const avgLoss = losses.slice(i - period + 1, i + 1).reduce((sum, loss) => sum + loss, 0) / period;
      
      if (avgLoss === 0) {
        rsi.push(100);
      } else {
        const rs = avgGain / avgLoss;
        const rsiValue = 100 - (100 / (1 + rs));
        rsi.push(rsiValue);
      }
    }
    
    return rsi;
  }

  private calculateStrength(rsi: number, threshold: number): number {
    const distance = Math.abs(rsi - threshold);
    return Math.min(distance / 50, 1); // Normalize to 0-1
  }
}
```

## Best Practices

1. **Clear Naming**: Use descriptive names for strategies and parameters
2. **Parameter Validation**: Always validate input parameters
3. **Error Handling**: Handle edge cases and insufficient data
4. **Performance**: Consider computational efficiency for large datasets
5. **Documentation**: Document your strategy logic and parameters
6. **Testing**: Write unit tests for your strategies
7. **Signal Quality**: Ensure signals have meaningful strength values
8. **Reason Codes**: Provide clear reasons for each signal

## Testing Your Strategy

```typescript
import { MyCustomStrategy } from './MyCustomStrategy.js';

describe('MyCustomStrategy', () => {
  let strategy: MyCustomStrategy;

  beforeEach(() => {
    strategy = new MyCustomStrategy(10, 'test', ['AAPL']);
  });

  it('should validate correctly', () => {
    expect(strategy.validate()).toBe(true);
  });

  it('should generate signals', () => {
    const data = createMockData();
    const signals = strategy.generateSignals(data);
    expect(signals).toBeDefined();
  });
});
```