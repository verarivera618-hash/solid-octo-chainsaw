/**
 * Alpaca Connection Test
 * Quick test to verify your Alpaca credentials work
 */
import { AlpacaDataProvider } from '../integrations/alpaca/AlpacaDataProvider.js';
import { AlpacaTradeExecutor } from '../integrations/alpaca/AlpacaTradeExecutor.js';
const config = {
    apiKey: 'PKOZCMCMINNVRSCFHDBNDYHL7E',
    secretKey: 'Dh9WfTuXBybXGbqMdS376woQLKQV6LBLMAtnt5qf1N7K',
    baseUrl: 'https://paper-api.alpaca.markets',
    dataUrl: 'https://data.alpaca.markets',
    paperTrading: true
};
async function testConnection() {
    console.log('🔍 Testing Alpaca API Connection...\n');
    try {
        // Test data provider
        console.log('📊 Testing data provider...');
        const dataProvider = new AlpacaDataProvider(config);
        const isDataAvailable = await dataProvider.isAvailable();
        console.log(`Data provider available: ${isDataAvailable ? '✅' : '❌'}`);
        // Test trade executor
        console.log('💰 Testing trade executor...');
        const tradeExecutor = new AlpacaTradeExecutor(config);
        const accountInfo = await tradeExecutor.getAccountInfo();
        console.log('Account info:', {
            accountNumber: accountInfo.account_number,
            buyingPower: accountInfo.buying_power,
            cash: accountInfo.cash,
            equity: accountInfo.equity,
            status: accountInfo.status
        });
        // Test getting some data
        console.log('\n📈 Testing data fetch...');
        const endDate = new Date();
        const startDate = new Date(endDate.getTime() - 7 * 24 * 60 * 60 * 1000); // 7 days ago
        const priceData = await dataProvider.getPriceData('AAPL', startDate, endDate);
        console.log(`Fetched ${priceData.length} data points for AAPL`);
        if (priceData.length > 0) {
            console.log('Latest data point:', priceData[priceData.length - 1]);
        }
        console.log('\n✅ All tests passed! Your Alpaca integration is working correctly.');
    }
    catch (error) {
        console.error('❌ Connection test failed:', error);
        if (error.message?.includes('401')) {
            console.log('\n💡 This might be an authentication issue. Check your API keys.');
        }
        else if (error.message?.includes('403')) {
            console.log('\n💡 This might be a permissions issue. Make sure your account has trading permissions.');
        }
        else if (error.message?.includes('429')) {
            console.log('\n💡 Rate limit exceeded. Wait a moment and try again.');
        }
    }
}
testConnection();
//# sourceMappingURL=alpaca-test-connection.js.map