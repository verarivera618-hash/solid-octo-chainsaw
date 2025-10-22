# Setting Up Alpaca Integration

This backtesting system now supports integration with Alpaca Markets for live trading and real market data.

## Quick Start

### 1. Get Your Alpaca API Credentials

1. Sign up for a free Alpaca account at https://app.alpaca.markets/
2. For paper trading (recommended for testing):
   - Navigate to the Paper Trading section
   - Generate your API keys
3. For live trading (use with caution):
   - Complete account verification
   - Navigate to the Live Trading section
   - Generate your API keys

### 2. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your credentials
nano .env  # or use your preferred editor
```

Add your Alpaca credentials to the `.env` file:
```env
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
ALPACA_ENVIRONMENT=paper  # Use 'paper' for testing or 'live' for real trading
```

### 3. Install Dependencies and Build

```bash
# Install Node.js dependencies
npm install

# Add node-fetch for API calls (if not already installed)
npm install node-fetch

# Build the TypeScript code
npm run build
```

### 4. Test Your Connection

```bash
# Run the connection test script
npx tsx test-alpaca-connection.ts
```

This will verify:
- API credentials are valid
- Connection to Alpaca is working
- Account information can be retrieved
- Market data can be fetched

## Features Available with Alpaca

### Data Provider
- Real-time and historical market data
- Accurate price information directly from exchanges
- Support for stocks, ETFs, and crypto

### Live Trading Capabilities
- Place market and limit orders
- Manage positions and portfolios
- Track order status and execution
- Cancel pending orders
- Check market hours and trading calendar

### Backtesting with Real Data
- Use actual historical data for more accurate backtests
- Seamless transition from backtesting to paper trading
- Same code works for both simulation and live execution

## Using Alpaca in Your Strategies

### Example: Fetching Real Market Data

```typescript
import { AlpacaDataProvider } from './src/data/AlpacaDataProvider.js';

const alpaca = new AlpacaDataProvider();
const endDate = new Date();
const startDate = new Date();
startDate.setMonth(startDate.getMonth() - 1);

const data = await alpaca.getPriceData('AAPL', startDate, endDate);
```

### Example: Executing Trades

```typescript
import { AlpacaTradeExecutor } from './src/core/AlpacaTradeExecutor.js';

const executor = new AlpacaTradeExecutor(0.001, 0.0005);
const signal = {
  symbol: 'AAPL',
  action: 'buy',
  strength: 0.8,
  timestamp: new Date()
};

const trade = await executor.executeLiveTrade(signal, undefined, 10000);
```

## Safety Features

1. **Paper Trading Mode**: Test strategies with simulated money before going live
2. **Environment Separation**: Clear distinction between paper and live trading
3. **Credential Security**: API keys stored in environment variables, never in code
4. **Error Handling**: Comprehensive error handling for API failures
5. **Market Hours Checking**: Verify market is open before placing orders

## Switching Between Paper and Live Trading

Simply change the `ALPACA_ENVIRONMENT` variable in your `.env` file:
- `ALPACA_ENVIRONMENT=paper` - For paper trading (recommended)
- `ALPACA_ENVIRONMENT=live` - For live trading (use with extreme caution)

## Important Notes

⚠️ **Live Trading Warning**: When using live trading mode, real money is at risk. Always test your strategies thoroughly in paper trading mode first.

📝 **API Rate Limits**: Alpaca has rate limits on API calls. The system handles this gracefully, but be aware of limits when running high-frequency strategies.

🔒 **Security**: Never commit your `.env` file to version control. Keep your API credentials secure.

## Troubleshooting

### Connection Test Fails
- Verify your API keys are correct
- Check your internet connection
- Ensure you're using the right environment (paper vs live)

### No Market Data
- Check if the market is open
- Verify the symbol exists and is tradeable
- Check your Alpaca subscription level for data access

### Order Rejections
- Verify sufficient buying power
- Check if the symbol is tradeable
- Ensure market is open for trading
- Review Alpaca's pattern day trader rules if applicable

## Next Steps

1. Run the connection test to verify setup
2. Try backtesting with real Alpaca data
3. Test strategies in paper trading mode
4. Monitor performance and refine strategies
5. Consider live trading only after extensive testing

For more information, visit the [Alpaca Documentation](https://docs.alpaca.markets/).