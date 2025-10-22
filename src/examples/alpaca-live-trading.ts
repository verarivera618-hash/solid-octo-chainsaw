/**
 * Alpaca Live Trading Example
 * Complete working example with your Alpaca credentials
 */

import { LiveTradingOrchestrator } from '../integrations/LiveTradingOrchestrator.js';
import { SimpleMovingAverageStrategy } from '../strategies/SimpleMovingAverageStrategy.js';

// Your Alpaca configuration
const alpacaConfig = {
  apiKey: process.env['ALPACA_API_KEY'] || 'PKOZCMCMINNVRSCFHDBNDYHL7E',
  secretKey: process.env['ALPACA_SECRET_KEY'] || 'Dh9WfTuXBybXGbqMdS376woQLKQV6LBLMAtnt5qf1N7K',
  baseUrl: 'https://paper-api.alpaca.markets',
  dataUrl: 'https://data.alpaca.markets',
  paperTrading: true
};

// Live trading configuration
const liveTradingConfig = {
  alpaca: alpacaConfig,
  riskManagement: {
    maxPositionSize: 1000,
    maxDailyLoss: 500,
    stopLossPercentage: 0.02,
    maxOpenPositions: 5
  }
};

async function main() {
  console.log('🚀 Starting Alpaca Live Trading System...');
  
  try {
    // Initialize the orchestrator
    const orchestrator = new LiveTradingOrchestrator(liveTradingConfig);
    
    // Create and register a simple moving average strategy
    const smaStrategy = new SimpleMovingAverageStrategy(10, 20, ['AAPL', 'GOOGL']);
    
    orchestrator.registerStrategy('sma_crossover', smaStrategy);
    
    // Test the connection
    console.log('🔍 Testing Alpaca connection...');
    const isConnected = await orchestrator.getAccountStatus();
    console.log('✅ Connection status:', isConnected);
    
    // Start live trading
    await orchestrator.startTrading();
    
    // Example: Process a test signal
    console.log('📊 Processing test signal...');
    const testSignal = {
      symbol: 'AAPL',
      action: 'buy' as const,
      strength: 0.8,
      timestamp: new Date(),
      reason: 'Test signal for live trading'
    };
    
    const trade = await orchestrator.processSignal(testSignal, 'alpaca');
    if (trade) {
      console.log('✅ Test trade executed:', trade);
    } else {
      console.log('❌ Test trade failed or was rejected');
    }
    
    // Keep the system running
    console.log('🔄 Live trading system is running...');
    console.log('Press Ctrl+C to stop');
    
    // Handle graceful shutdown
    process.on('SIGINT', async () => {
      console.log('\n🛑 Shutting down live trading system...');
      await orchestrator.stopTrading();
      process.exit(0);
    });
    
  } catch (error) {
    console.error('❌ Error starting live trading system:', error);
    process.exit(1);
  }
}

// Run the main function
main().catch(console.error);