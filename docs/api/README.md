# API Reference

## Core Classes

### BacktestEngine

The main orchestrator for running backtests.

```typescript
class BacktestEngine {
  constructor(config: BacktestConfig)
  async runBacktest(strategy: Strategy, marketData: Map<string, PriceData[]>): Promise<BacktestResult>
  getPortfolio(): Portfolio
}
```

**Methods:**

- `runBacktest(strategy, marketData)` - Execute a backtest with the given strategy and market data
- `getPortfolio()` - Get the current portfolio state

### Portfolio

Manages positions, cash, and portfolio value over time.

```typescript
class Portfolio {
  constructor(initialCapital: number)
  getCash(): number
  getPosition(symbol: string): Position | undefined
  getPositions(): Position[]
  updatePosition(trade: Trade): void
  updateValue(priceData: PriceData[]): void
  getEquityCurve(): Array<{ timestamp: Date; value: number }>
  getTotalValue(): number
}
```

### TradeExecutor

Handles trade simulation with commission and slippage.

```typescript
class TradeExecutor {
  constructor(commission: number, slippage: number)
  async executeTrade(signal: Signal, position: Position | undefined, cash: number): Promise<Trade | null>
}
```

### PerformanceAnalyzer

Calculates comprehensive performance metrics.

```typescript
class PerformanceAnalyzer {
  analyze(trades: Trade[], equityCurve: Array<{ timestamp: Date; value: number }>): BacktestResult
}
```

## Strategy Interface

All trading strategies must implement the Strategy interface:

```typescript
interface Strategy {
  readonly name: string;
  readonly description: string;
  readonly parameters: Record<string, unknown>;
  generateSignals(data: PriceData[]): Signal[];
  validate(): boolean;
}
```

## Data Types

### PriceData

```typescript
interface PriceData {
  readonly timestamp: Date;
  readonly open: number;
  readonly high: number;
  readonly low: number;
  readonly close: number;
  readonly volume: number;
}
```

### Trade

```typescript
interface Trade {
  readonly id: string;
  readonly symbol: string;
  readonly side: 'buy' | 'sell';
  readonly quantity: number;
  readonly price: number;
  readonly timestamp: Date;
  readonly fees: number;
}
```

### BacktestResult

```typescript
interface BacktestResult {
  readonly totalReturn: number;
  readonly annualizedReturn: number;
  readonly maxDrawdown: number;
  readonly sharpeRatio: number;
  readonly winRate: number;
  readonly totalTrades: number;
  readonly profitableTrades: number;
  readonly losingTrades: number;
  readonly averageWin: number;
  readonly averageLoss: number;
  readonly profitFactor: number;
  readonly trades: readonly Trade[];
  readonly equityCurve: readonly { timestamp: Date; value: number }[];
}
```

## Configuration

### BacktestConfig

```typescript
interface BacktestConfig {
  readonly startDate: Date;
  readonly endDate: Date;
  readonly initialCapital: number;
  readonly commission: number;
  readonly slippage: number;
  readonly symbols: readonly string[];
}
```