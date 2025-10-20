# Trading Platform Integrations

This directory contains integrations for various trading platforms and data providers.

## Supported Platforms

### 1. Alpaca Trading ✅
- **Best for**: Stock trading, paper trading, live execution
- **Features**: Real-time data, live trading, paper trading
- **Setup**: Requires Alpaca account and API keys

### 2. TradeStation ⚠️
- **Best for**: Professional trading, advanced order types
- **Features**: Professional-grade data, advanced order management
- **Setup**: Requires TradeStation account and API approval

### 3. TradingView 🔄
- **Best for**: Strategy signals, chart analysis
- **Features**: Pine Script alerts, webhook integration
- **Setup**: Configure webhook in TradingView alerts

### 4. Pocket Option ⚠️
- **Best for**: Binary options trading
- **Features**: Binary options data and execution
- **Setup**: Limited public API access

## Quick Start

### 1. Alpaca Integration (Recommended for beginners)

```typescript
import { LiveTradingOrchestrator } from './LiveTradingOrchestrator.js';

const config = {
  alpaca: {
    apiKey: 'your_api_key',
    secretKey: 'your_secret_key',
    paperTrading: true // Start with paper trading
  }
};

const orchestrator = new LiveTradingOrchestrator(config);
await orchestrator.startTrading();
```

### 2. TradingView Signal Integration

```typescript
// Register a strategy
orchestrator.registerStrategy('my_strategy', myStrategy);

// Get webhook handler for Express.js
app.post('/webhook/tradingview', orchestrator.getWebhookHandler());
```

### 3. Pine Script Alert Setup

In your TradingView Pine Script:

```pinescript
// Buy signal
if (buy_condition)
    alert("{\"symbol\":\"" + syminfo.ticker + "\",\"action\":\"buy\",\"strength\":0.8,\"timestamp\":\"" + str.tostring(time) + "\",\"reason\":\"Price broke above resistance\"}", alert.freq_once_per_bar)

// Sell signal  
if (sell_condition)
    alert("{\"symbol\":\"" + syminfo.ticker + "\",\"action\":\"sell\",\"strength\":0.9,\"timestamp\":\"" + str.tostring(time) + "\",\"reason\":\"RSI overbought\"}", alert.freq_once_per_bar)
```

## Configuration

### Environment Variables

Create a `.env` file:

```env
# Alpaca
ALPACA_API_KEY=your_api_key
ALPACA_SECRET_KEY=your_secret_key
ALPACA_PAPER_TRADING=true

# TradeStation
TRADESTATION_CLIENT_ID=your_client_id
TRADESTATION_CLIENT_SECRET=your_client_secret
TRADESTATION_USERNAME=your_username
TRADESTATION_PASSWORD=your_password

# TradingView
TRADINGVIEW_WEBHOOK_SECRET=your_webhook_secret
TRADINGVIEW_WEBHOOK_PORT=3000

# Pocket Option
POCKETOPTION_API_KEY=your_api_key
```

## Risk Management

The orchestrator includes built-in risk management:

```typescript
const config = {
  riskManagement: {
    maxPositionSize: 1000,      // Max $ per position
    maxDailyLoss: 500,          // Max daily loss
    stopLossPercentage: 0.02,   // 2% stop loss
    maxOpenPositions: 5         // Max concurrent positions
  }
};
```

## Error Handling

All integrations include comprehensive error handling:
- API failures fall back to mock data
- Network timeouts are handled gracefully
- Invalid signals are logged and rejected
- Risk management prevents dangerous trades

## Security

- API keys are stored in environment variables
- Webhook signatures are validated (when configured)
- All trades are logged with timestamps
- Paper trading mode for safe testing

## Monitoring

The orchestrator provides monitoring capabilities:

```typescript
// Get account status
const status = await orchestrator.getAccountStatus();

// Process signals manually
const trade = await orchestrator.processSignal(signal, 'alpaca');
```

## Development

### Adding New Brokers

1. Create a new data provider implementing `DataProvider` interface
2. Create a new trade executor for the broker
3. Add configuration types
4. Update the orchestrator to include the new broker

### Testing

```bash
# Run integration tests
npm test -- --grep "integration"

# Test with paper trading
ALPACA_PAPER_TRADING=true npm run dev
```

## Troubleshooting

### Common Issues

1. **API Key Errors**: Verify your API keys are correct and have proper permissions
2. **Rate Limiting**: Implement proper rate limiting for API calls
3. **Webhook Failures**: Check webhook URL is accessible and signature validation
4. **Paper Trading**: Always test with paper trading first

### Logs

All integrations log important events:
- Signal reception
- Trade execution
- API errors
- Risk management decisions

Check console output for detailed logs.