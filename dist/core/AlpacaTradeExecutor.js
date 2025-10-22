/**
 * Alpaca live trade execution engine
 * Handles real trade execution through Alpaca Markets API
 */
import AlpacaClient from '@alpacahq/alpaca-trade-api';
export class AlpacaTradeExecutor {
    client;
    commission;
    slippage;
    constructor(config, commission = 0.0, slippage = 0.0) {
        this.commission = commission; // Alpaca has no commission for most trades
        this.slippage = slippage;
        this.client = new AlpacaClient({
            credentials: {
                key: config.apiKey,
                secret: config.secretKey,
            },
            rate_limit: true,
        });
    }
    /**
     * Execute a live trade through Alpaca
     */
    async executeTrade(signal, currentPosition, availableCash) {
        if (signal.action === 'hold') {
            return null;
        }
        try {
            // Get current market price
            const marketPrice = await this.getCurrentPrice(signal.symbol);
            if (!marketPrice) {
                console.error(`Could not get market price for ${signal.symbol}`);
                return null;
            }
            const executionPrice = this.calculateExecutionPrice(marketPrice, signal);
            const quantity = this.calculateQuantity(signal, currentPosition, availableCash, executionPrice);
            if (quantity <= 0) {
                console.log(`Cannot execute trade for ${signal.symbol}: insufficient funds or invalid quantity`);
                return null;
            }
            // Execute the trade through Alpaca
            const alpacaOrder = await this.submitOrder(signal, quantity, executionPrice);
            if (!alpacaOrder) {
                return null;
            }
            const fees = this.calculateFees(quantity, executionPrice);
            return {
                id: alpacaOrder.id,
                symbol: signal.symbol,
                side: signal.action,
                quantity,
                price: executionPrice,
                timestamp: signal.timestamp,
                fees,
            };
        }
        catch (error) {
            console.error(`Error executing trade for ${signal.symbol}:`, error);
            return null;
        }
    }
    /**
     * Get current positions from Alpaca
     */
    async getPositions() {
        try {
            const positions = await this.client.getPositions();
            return positions.map((pos) => ({
                symbol: pos.symbol,
                quantity: parseFloat(pos.qty),
                averagePrice: parseFloat(pos.avg_entry_price),
                unrealizedPnL: parseFloat(pos.unrealized_pl),
                realizedPnL: parseFloat(pos.realized_pl),
            }));
        }
        catch (error) {
            console.error('Error fetching positions:', error);
            return [];
        }
    }
    /**
     * Get account information
     */
    async getAccount() {
        try {
            return await this.client.getAccount();
        }
        catch (error) {
            console.error('Error fetching account info:', error);
            throw error;
        }
    }
    /**
     * Cancel all open orders
     */
    async cancelAllOrders() {
        try {
            await this.client.cancelAllOrders();
            console.log('All orders cancelled');
        }
        catch (error) {
            console.error('Error cancelling orders:', error);
        }
    }
    /**
     * Get open orders
     */
    async getOpenOrders() {
        try {
            return await this.client.getOrders();
        }
        catch (error) {
            console.error('Error fetching open orders:', error);
            return [];
        }
    }
    async getCurrentPrice(symbol) {
        try {
            const quote = await this.client.getLatestQuote(symbol);
            return quote.AskPrice;
        }
        catch (error) {
            console.error(`Error getting current price for ${symbol}:`, error);
            return null;
        }
    }
    calculateExecutionPrice(marketPrice, signal) {
        const slippageAmount = marketPrice * this.slippage;
        return signal.action === 'buy'
            ? marketPrice + slippageAmount
            : marketPrice - slippageAmount;
    }
    calculateQuantity(signal, currentPosition, availableCash, price) {
        if (signal.action === 'buy') {
            const maxQuantity = Math.floor(availableCash / (price * (1 + this.commission)));
            return Math.min(maxQuantity, Math.floor(signal.strength * 1000)); // Scale by signal strength
        }
        else {
            // Sell - use current position or signal strength
            const currentQuantity = currentPosition?.quantity || 0;
            return Math.floor(currentQuantity * signal.strength);
        }
    }
    async submitOrder(signal, quantity, price) {
        try {
            const orderRequest = {
                symbol: signal.symbol,
                qty: quantity.toString(),
                side: signal.action,
                type: 'market', // Use market orders for immediate execution
                time_in_force: 'day',
            };
            console.log(`Submitting ${signal.action} order for ${quantity} shares of ${signal.symbol} at $${price}`);
            const order = await this.client.createOrder(orderRequest);
            console.log(`Order submitted: ${order.id}`);
            return order;
        }
        catch (error) {
            console.error(`Error submitting order for ${signal.symbol}:`, error);
            return null;
        }
    }
    calculateFees(quantity, price) {
        return quantity * price * this.commission;
    }
}
//# sourceMappingURL=AlpacaTradeExecutor.js.map