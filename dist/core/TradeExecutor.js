/**
 * Trade execution engine
 * Handles trade simulation with commission and slippage
 */
import { Trade, Signal, Position } from '../types/index.js';
import Decimal from 'decimal.js';
export class TradeExecutor {
    commission;
    slippage;
    constructor(commission, slippage) {
        this.commission = commission;
        this.slippage = slippage;
    }
    /**
     * Execute a trade based on signal
     */
    async executeTrade(signal, currentPosition, availableCash) {
        if (signal.action === 'hold') {
            return null;
        }
        const executionPrice = this.calculateExecutionPrice(signal);
        const quantity = this.calculateQuantity(signal, currentPosition, availableCash, executionPrice);
        if (quantity <= 0) {
            return null; // Cannot execute trade
        }
        const fees = this.calculateFees(quantity, executionPrice);
        return {
            id: this.generateTradeId(),
            symbol: signal.symbol,
            side: signal.action,
            quantity,
            price: executionPrice,
            timestamp: signal.timestamp,
            fees,
        };
    }
    calculateExecutionPrice(signal) {
        // In a real implementation, this would fetch current market price
        // For backtesting, we'll use a simplified model
        const basePrice = 100; // This should come from market data
        const slippageAmount = basePrice * this.slippage;
        return signal.action === 'buy'
            ? basePrice + slippageAmount
            : basePrice - slippageAmount;
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
    calculateFees(quantity, price) {
        return quantity * price * this.commission;
    }
    generateTradeId() {
        return `trade_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
}
//# sourceMappingURL=TradeExecutor.js.map