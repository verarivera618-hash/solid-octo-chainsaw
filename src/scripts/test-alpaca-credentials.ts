/**
 * Test script to validate Alpaca API credentials
 * Run this to verify your credentials are working correctly
 */

import { AlpacaBroker } from '../brokers/AlpacaBroker.js';
import { getConfig } from '../config/index.js';

async function testAlpacaCredentials() {
  console.log('='.repeat(60));
  console.log('🔍 Testing Alpaca API Credentials');
  console.log('='.repeat(60));
  console.log();

  const config = getConfig();
  
  // Check if credentials are configured
  if (!config.alpaca.apiKey || !config.alpaca.apiSecret) {
    console.error('❌ ERROR: Alpaca credentials not configured!');
    console.error();
    console.error('Please set the following environment variables:');
    console.error('  - ALPACA_API_KEY');
    console.error('  - ALPACA_API_SECRET');
    console.error();
    console.error('You can set these in a .env file or export them in your shell.');
    console.error('See .env.example for the template.');
    process.exit(1);
  }

  try {
    // Initialize broker
    const broker = new AlpacaBroker({
      apiKey: config.alpaca.apiKey,
      apiSecret: config.alpaca.apiSecret,
      paper: config.alpaca.paper,
      baseUrl: config.alpaca.baseUrl,
    });

    // Validate credentials
    console.log('Testing connection...');
    console.log();
    await broker.validateCredentials();
    console.log();

    // Get account details
    const account = await broker.getAccount();
    console.log('📊 Account Details:');
    console.log(`  Portfolio Value: $${parseFloat(account.portfolio_value).toFixed(2)}`);
    console.log(`  Cash: $${parseFloat(account.cash).toFixed(2)}`);
    console.log(`  Pattern Day Trader: ${account.pattern_day_trader ? 'Yes' : 'No'}`);
    console.log(`  Day Trade Count: ${account.daytrade_count}`);
    console.log();

    // Check market status
    const isOpen = await broker.isMarketOpen();
    console.log(`📈 Market Status: ${isOpen ? '🟢 OPEN' : '🔴 CLOSED'}`);
    console.log();

    // Get positions
    const positions = await broker.getPositions();
    console.log(`📦 Current Positions: ${positions.length}`);
    if (positions.length > 0) {
      positions.forEach(pos => {
        const plColor = pos.unrealizedPnL >= 0 ? '🟢' : '🔴';
        console.log(`  ${plColor} ${pos.symbol}: ${pos.quantity} shares @ $${pos.averagePrice.toFixed(2)} (Current: $${pos.currentPrice?.toFixed(2) || 'N/A'}, P/L: $${pos.unrealizedPnL.toFixed(2)})`);
      });
    }
    console.log();

    // Get open orders
    const orders = await broker.getOrders('open');
    console.log(`📋 Open Orders: ${orders.length}`);
    console.log();

    console.log('='.repeat(60));
    console.log('✅ Alpaca credentials are valid and working!');
    console.log('='.repeat(60));
    console.log();
    
    if (config.alpaca.paper) {
      console.log('ℹ️  You are using PAPER TRADING mode (safe for testing)');
    } else {
      console.log('⚠️  WARNING: You are using LIVE TRADING mode!');
    }
    console.log();

  } catch (error) {
    console.error();
    console.error('='.repeat(60));
    console.error('❌ Credential Test Failed');
    console.error('='.repeat(60));
    console.error();
    console.error('Error:', error instanceof Error ? error.message : error);
    console.error();
    console.error('Troubleshooting:');
    console.error('1. Verify your API key and secret are correct');
    console.error('2. Check if your API keys are for paper or live trading');
    console.error('3. Ensure your Alpaca account is active and approved');
    console.error('4. Visit https://alpaca.markets/docs/trading/getting-started/ for help');
    console.error();
    process.exit(1);
  }
}

// Run the test
testAlpacaCredentials().catch(error => {
  console.error('Unexpected error:', error);
  process.exit(1);
});
