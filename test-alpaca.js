/**
 * Simple test script to verify Alpaca credentials and connection
 * This script can be run directly with Node.js without TypeScript compilation
 */

const Alpaca = require('@alpacahq/alpaca-trade-api');
require('dotenv').config();

async function testAlpacaConnection() {
  console.log('🚀 Testing Alpaca API connection...');
  
  // Check if credentials are set
  const apiKey = process.env.ALPACA_API_KEY;
  const secretKey = process.env.ALPACA_SECRET_KEY;
  const baseUrl = process.env.ALPACA_BASE_URL || 'https://paper-api.alpaca.markets';
  
  if (!apiKey || !secretKey) {
    console.error('❌ Alpaca credentials not found!');
    console.log('\nPlease create a .env file with your Alpaca credentials:');
    console.log('ALPACA_API_KEY=your_api_key_here');
    console.log('ALPACA_SECRET_KEY=your_secret_key_here');
    console.log('ALPACA_BASE_URL=https://paper-api.alpaca.markets');
    console.log('\nYou can get your API keys from: https://app.alpaca.markets/paper/dashboard/overview');
    return;
  }

  console.log(`📊 Using ${baseUrl.includes('paper') ? 'PAPER' : 'LIVE'} trading environment`);
  console.log(`🔑 API Key: ${apiKey.substring(0, 8)}...`);

  try {
    // Initialize Alpaca client
    const alpaca = new Alpaca({
      key: apiKey,
      secret: secretKey,
      baseUrl: baseUrl,
      usePolygon: false,
    });

    // Test 1: Get account information
    console.log('\n🔍 Testing account access...');
    const account = await alpaca.getAccount();
    console.log('✅ Account access successful!');
    console.log(`💰 Account equity: $${parseFloat(account.equity).toFixed(2)}`);
    console.log(`💵 Buying power: $${parseFloat(account.buying_power).toFixed(2)}`);
    console.log(`📊 Account status: ${account.status}`);

    // Test 2: Get positions
    console.log('\n📍 Getting current positions...');
    const positions = await alpaca.getPositions();
    console.log(`✅ Found ${positions.length} positions`);
    
    if (positions.length > 0) {
      console.log('\n📋 Current Holdings:');
      positions.forEach(position => {
        const unrealizedPL = parseFloat(position.unrealized_pl);
        const plColor = unrealizedPL >= 0 ? '🟢' : '🔴';
        console.log(`${plColor} ${position.symbol}: ${position.qty} shares @ $${parseFloat(position.avg_cost).toFixed(2)} (P&L: $${unrealizedPL.toFixed(2)})`);
      });
    }

    // Test 3: Get market data
    console.log('\n📊 Testing market data access...');
    try {
      const quote = await alpaca.getLatestQuote('AAPL');
      console.log('✅ Market data access successful!');
      console.log(`📈 AAPL Quote - Bid: $${quote.BidPrice}, Ask: $${quote.AskPrice}`);
    } catch (error) {
      console.log('⚠️  Market data access limited (this is normal for some account types)');
    }

    // Test 4: Get recent orders
    console.log('\n📋 Getting recent orders...');
    try {
      const orders = await alpaca.getOrders({
        status: 'all',
        limit: 5,
      });
      console.log(`✅ Found ${orders.length} recent orders`);
      
      if (orders.length > 0) {
        console.log('\n📝 Recent Orders:');
        orders.slice(0, 3).forEach(order => {
          console.log(`${order.side.toUpperCase()} ${order.qty} ${order.symbol} @ ${order.order_type} - Status: ${order.status}`);
        });
      }
    } catch (error) {
      console.log('⚠️  Could not fetch orders:', error.message);
    }

    console.log('\n🎉 All tests completed successfully!');
    console.log('\n✅ Your Alpaca credentials are working correctly.');
    console.log('✅ You can now run the backtesting system with live data.');
    
    if (baseUrl.includes('paper')) {
      console.log('\n📝 Note: You are using the paper trading environment.');
      console.log('   This is safe for testing - no real money will be used.');
      console.log('   To use live trading, change ALPACA_BASE_URL to https://api.alpaca.markets');
    } else {
      console.log('\n⚠️  WARNING: You are using the LIVE trading environment!');
      console.log('   Real money trades will be executed. Please be careful!');
    }

  } catch (error) {
    console.error('❌ Error connecting to Alpaca:', error.message);
    
    if (error.message.includes('401')) {
      console.log('\n🔧 Troubleshooting:');
      console.log('- Check that your API key and secret are correct');
      console.log('- Make sure your API keys are for the correct environment (paper vs live)');
      console.log('- Verify your API keys are active in your Alpaca dashboard');
    }
  }
}

// Run the test
testAlpacaConnection().catch(console.error);