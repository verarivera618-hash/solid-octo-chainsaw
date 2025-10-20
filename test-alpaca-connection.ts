#!/usr/bin/env node
/**
 * Test script to verify Alpaca API connection
 * Run this to ensure your credentials are properly configured
 */

import { AlpacaDataProvider } from './src/data/AlpacaDataProvider.js';
import { config } from './src/config/index.js';

async function testAlpacaConnection() {
  console.log('🔍 Testing Alpaca API Connection...\n');
  
  // Check environment configuration
  console.log('📋 Configuration Status:');
  console.log(`- Environment: ${config.alpaca.environment}`);
  console.log(`- API Key: ${config.alpaca.apiKey ? '✅ Configured' : '❌ Not configured'}`);
  console.log(`- Secret Key: ${config.alpaca.secretKey ? '✅ Configured' : '❌ Not configured'}`);
  console.log(`- Enabled: ${config.alpaca.enabled ? '✅' : '❌'}\n`);

  if (!config.alpaca.enabled) {
    console.error('❌ Alpaca credentials are not configured!');
    console.log('\n📝 To configure Alpaca:');
    console.log('1. Copy .env.example to .env:');
    console.log('   cp .env.example .env');
    console.log('2. Edit .env and add your Alpaca API credentials');
    console.log('3. Get your API keys from: https://app.alpaca.markets/');
    console.log('4. Run this test again\n');
    return;
  }

  const alpaca = new AlpacaDataProvider();

  // Test 1: Check API availability
  console.log('🔌 Testing API availability...');
  try {
    const isAvailable = await alpaca.isAvailable();
    if (isAvailable) {
      console.log('✅ Alpaca API is available and credentials are valid!\n');
    } else {
      console.log('❌ Alpaca API is not available\n');
      return;
    }
  } catch (error) {
    console.error('❌ Error checking API availability:', error);
    return;
  }

  // Test 2: Get account information
  console.log('👤 Fetching account information...');
  try {
    const account = await alpaca.getAccountInfo();
    console.log('✅ Account Information:');
    console.log(`- Account Number: ${account.account_number}`);
    console.log(`- Status: ${account.status}`);
    console.log(`- Buying Power: $${parseFloat(account.buying_power).toLocaleString()}`);
    console.log(`- Cash: $${parseFloat(account.cash).toLocaleString()}`);
    console.log(`- Portfolio Value: $${parseFloat(account.portfolio_value).toLocaleString()}`);
    console.log(`- Pattern Day Trader: ${account.pattern_day_trader ? 'Yes' : 'No'}`);
    console.log(`- Trading Blocked: ${account.trading_blocked ? 'Yes' : 'No'}\n`);
  } catch (error) {
    console.error('❌ Error fetching account info:', error);
  }

  // Test 3: Get current positions
  console.log('📊 Fetching current positions...');
  try {
    const positions = await alpaca.getPositions();
    if (positions.length > 0) {
      console.log(`✅ Found ${positions.length} position(s):`);
      positions.forEach(pos => {
        console.log(`- ${pos.symbol}: ${pos.qty} shares @ $${pos.avg_entry_price} (P&L: $${pos.unrealized_pl})`);
      });
    } else {
      console.log('📝 No open positions');
    }
    console.log();
  } catch (error) {
    console.error('❌ Error fetching positions:', error);
  }

  // Test 4: Get recent orders
  console.log('📋 Fetching recent orders...');
  try {
    const orders = await alpaca.getOrders('all');
    const recentOrders = orders.slice(0, 5);
    if (recentOrders.length > 0) {
      console.log(`✅ Recent orders (showing up to 5):`);
      recentOrders.forEach(order => {
        console.log(`- ${order.symbol}: ${order.side} ${order.qty} @ ${order.order_type} (Status: ${order.status})`);
      });
    } else {
      console.log('📝 No orders found');
    }
    console.log();
  } catch (error) {
    console.error('❌ Error fetching orders:', error);
  }

  // Test 5: Fetch sample market data
  console.log('📈 Testing market data fetch...');
  try {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 7); // Last 7 days

    const priceData = await alpaca.getPriceData('AAPL', startDate, endDate);
    if (priceData.length > 0) {
      console.log(`✅ Successfully fetched ${priceData.length} days of AAPL price data`);
      const latest = priceData[priceData.length - 1];
      console.log(`- Latest close: $${latest.close}`);
      console.log(`- Date: ${latest.timestamp.toISOString().split('T')[0]}`);
    } else {
      console.log('⚠️ No price data returned');
    }
    console.log();
  } catch (error) {
    console.error('❌ Error fetching market data:', error);
  }

  // Test 6: Check market hours
  console.log('🕐 Checking market hours...');
  try {
    const marketHours = await alpaca.getMarketHours(new Date());
    if (marketHours) {
      console.log('✅ Market hours for today:');
      console.log(`- Date: ${marketHours.date}`);
      console.log(`- Open: ${marketHours.open}`);
      console.log(`- Close: ${marketHours.close}`);
    } else {
      console.log('📝 Market is closed today');
    }
  } catch (error) {
    console.error('❌ Error checking market hours:', error);
  }

  console.log('\n✨ Alpaca connection test complete!');
}

// Run the test
testAlpacaConnection().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});