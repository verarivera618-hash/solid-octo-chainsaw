# solid-octo-chainsaw
Back tester for predicting trades

## Features
- **Backtesting Framework**: Test trading strategies against historical data
- **Live Trading Integration**: Execute real trades through Alpaca Markets
- **Paper Trading Support**: Test strategies with simulated money
- **Performance Analytics**: Detailed metrics including Sharpe ratio, drawdown, win rate, etc.
- **Multiple Strategies**: Extensible strategy framework

## Quick Start

### 1. Installation
```bash
npm install
npm run build
```

### 2. Alpaca Trading Setup (Optional)

To enable live or paper trading with Alpaca:

1. **Get Alpaca API credentials**:
   - Sign up at https://alpaca.markets/
   - Generate API keys from your dashboard

2. **Configure credentials**:
   ```bash
   cp .env.example .env
   # Edit .env and add your credentials
   ```

3. **Test your connection**:
   ```bash
   npm run alpaca:test
   ```

See the [Alpaca Integration Guide](./docs/guides/alpaca-integration.md) for detailed instructions.

### 3. Run a Backtest
```bash
npm start
```

## Documentation
- [Alpaca Trading Integration Guide](./docs/guides/alpaca-integration.md)
- [Strategy Development Guide](./docs/guides/strategy-development.md)
- [API Documentation](./docs/api/README.md)

## Usage Examples

### Backtesting
```typescript
import { BacktestEngine, SimpleMovingAverageStrategy } from './src/index.js';

const engine = new BacktestEngine(config);
const strategy = new SimpleMovingAverageStrategy(20, 50, ['AAPL', 'GOOGL']);
const result = await engine.runBacktest(strategy, marketData);
```

### Live Trading (Alpaca)
```typescript
import { AlpacaBroker, LiveTradeExecutor } from './src/index.js';

const broker = new AlpacaBroker({
  apiKey: process.env.ALPACA_API_KEY,
  apiSecret: process.env.ALPACA_API_SECRET,
  paper: true, // Use paper trading
});

const executor = new LiveTradeExecutor(broker, false); // Read-only mode
await executor.validateConnection();
```

## Scripts
- `npm run build` - Compile TypeScript
- `npm test` - Run tests
- `npm run alpaca:test` - Test Alpaca credentials
- `npm start` - Run the application

## Safety & Compliance

This project follows strict safety and operational standards:

✓ **Credentials Security**: All API keys stored in environment variables  
✓ **Paper Trading First**: Default to simulated trading  
✓ **Read-Only Mode**: Prevents accidental trades  
✓ **Comprehensive Logging**: All actions timestamped and tracked  
✓ **Transparent Operations**: No hidden processes  

See [Global Ruleset] for full compliance guidelines.

## License
MIT 
