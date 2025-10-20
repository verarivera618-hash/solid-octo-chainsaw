# Alpaca Markets Integration

This backtesting framework now supports integration with Alpaca Markets for both data fetching and live trading execution.

## Features

- **Real-time Data**: Fetch historical and real-time market data from Alpaca
- **Live Trading**: Execute trades through Alpaca's paper trading or live trading APIs
- **Account Management**: Monitor account status, positions, and orders
- **Market Status**: Check if markets are open and get trading hours
- **Risk Management**: Built-in position sizing and risk controls

## Setup

### 1. Get Alpaca Credentials

1. Sign up for an Alpaca account at [https://alpaca.markets](https://alpaca.markets)
2. Go to your dashboard and generate API keys
3. **Important**: Start with paper trading for testing!

### 2. Configure Environment Variables

Copy the example environment file and add your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your Alpaca credentials:

```env
# Alpaca Markets API Configuration
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here

# Use paper trading for testing (recommended)
ALPACA_PAPER_TRADING=true
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Enable trading (set to true when ready)
TRADING_ENABLED=false
```

### 3. Install Dependencies

```bash
npm install
```

### 4. Build the Project

```bash
npm run build
```

## Usage

### Basic Data Fetching

```typescript
import { AlpacaDataProvider } from './src/data/AlpacaDataProvider.js';

const dataProvider = new AlpacaDataProvider({
  apiKey: 'your_api_key',
  secretKey: 'your_secret_key',
  baseUrl: 'https://paper-api.alpaca.markets',
  dataUrl: 'https://data.alpaca.markets',
});

// Fetch historical data
const data = await dataProvider.getPriceData('AAPL', startDate, endDate);

// Get real-time quote
const quote = await dataProvider.getQuote('AAPL');

// Check market status
const status = await dataProvider.getMarketStatus();
```

### Live Trading

```typescript
import { AlpacaTradeExecutor } from './src/core/AlpacaTradeExecutor.js';

const tradeExecutor = new AlpacaTradeExecutor({
  apiKey: 'your_api_key',
  secretKey: 'your_secret_key',
  baseUrl: 'https://paper-api.alpaca.markets',
  paperTrading: true,
});

// Execute a trade
const trade = await tradeExecutor.executeTrade(signal, currentPosition, availableCash);

// Get current positions
const positions = await tradeExecutor.getPositions();

// Get account info
const account = await tradeExecutor.getAccount();
```

### Running the Example

```bash
# Test the Alpaca integration
node test-alpaca.js
```

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ALPACA_API_KEY` | Your Alpaca API key | Required |
| `ALPACA_SECRET_KEY` | Your Alpaca secret key | Required |
| `ALPACA_BASE_URL` | API base URL | `https://paper-api.alpaca.markets` |
| `ALPACA_DATA_URL` | Data API URL | `https://data.alpaca.markets` |
| `ALPACA_PAPER_TRADING` | Use paper trading | `true` |
| `TRADING_ENABLED` | Enable live trading | `false` |
| `MAX_POSITION_SIZE` | Maximum position size | `10000` |
| `RISK_LIMIT` | Risk limit (as decimal) | `0.02` |

### Paper Trading vs Live Trading

- **Paper Trading** (Recommended for testing):
  - Uses `https://paper-api.alpaca.markets`
  - No real money at risk
  - Same API as live trading
  - Perfect for strategy development

- **Live Trading** (Use with caution):
  - Uses `https://api.alpaca.markets`
  - Real money at risk
  - Requires careful testing
  - Start with small amounts

## Safety Features

1. **Paper Trading by Default**: The system defaults to paper trading
2. **Explicit Trading Enable**: Live trading must be explicitly enabled
3. **Position Limits**: Configurable maximum position sizes
4. **Risk Controls**: Built-in risk management
5. **Error Handling**: Comprehensive error handling and logging

## API Rate Limits

Alpaca has rate limits on their API:
- **Data API**: 200 requests per minute
- **Trading API**: 200 requests per minute

The integration includes rate limiting to stay within these limits.

## Troubleshooting

### Common Issues

1. **"API not available"**: Check your credentials and network connection
2. **"Invalid credentials"**: Verify your API key and secret key
3. **"Market closed"**: Check market hours (9:30 AM - 4:00 PM ET)
4. **"Insufficient buying power"**: Check your account balance

### Debug Mode

Enable debug logging:

```env
LOG_LEVEL=debug
```

### Testing

Always test with paper trading first:

```env
ALPACA_PAPER_TRADING=true
TRADING_ENABLED=false
```

## Security Best Practices

1. **Never commit credentials**: Keep your `.env` file in `.gitignore`
2. **Use paper trading first**: Test thoroughly before live trading
3. **Start small**: Begin with small position sizes
4. **Monitor closely**: Watch your trades and positions
5. **Set limits**: Use position and risk limits

## Support

- [Alpaca Documentation](https://alpaca.markets/docs/)
- [Alpaca API Reference](https://alpaca.markets/docs/api-documentation/)
- [Alpaca Support](https://alpaca.markets/support/)

## Disclaimer

This software is for educational and research purposes. Trading involves risk, and you should never trade with money you cannot afford to lose. Always test thoroughly with paper trading before using real money.