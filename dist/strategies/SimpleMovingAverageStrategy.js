/**
 * Simple Moving Average Crossover Strategy
 * Example strategy implementation demonstrating proper structure
 */
export class SimpleMovingAverageStrategy {
    shortPeriod;
    longPeriod;
    symbols;
    name = 'Simple Moving Average Crossover';
    description = 'Buy when short MA crosses above long MA, sell when short MA crosses below long MA';
    parameters;
    constructor(shortPeriod = 20, longPeriod = 50, symbols = ['AAPL', 'GOOGL']) {
        this.shortPeriod = shortPeriod;
        this.longPeriod = longPeriod;
        this.symbols = symbols;
        this.parameters = {
            shortPeriod,
            longPeriod,
            symbols,
        };
    }
    generateSignals(data) {
        const signals = [];
        // For now, process all data as if it's for the first symbol
        // In a real implementation, you'd need to group by symbol
        const symbolData = data.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
        if (symbolData.length < this.longPeriod) {
            return signals; // Not enough data
        }
        const shortMA = this.calculateSMA(symbolData, this.shortPeriod);
        const longMA = this.calculateSMA(symbolData, this.longPeriod);
        if (shortMA.length < 2 || longMA.length < 2) {
            return signals;
        }
        const currentShort = shortMA[shortMA.length - 1];
        const previousShort = shortMA[shortMA.length - 2];
        const currentLong = longMA[longMA.length - 1];
        const previousLong = longMA[longMA.length - 2];
        // Check for crossover
        if (previousShort <= previousLong && currentShort > currentLong) {
            // Bullish crossover - buy signal
            signals.push({
                symbol: this.symbols[0],
                action: 'buy',
                strength: this.calculateSignalStrength(currentShort, currentLong),
                timestamp: symbolData[symbolData.length - 1].timestamp,
                reason: `Short MA (${currentShort.toFixed(2)}) crossed above Long MA (${currentLong.toFixed(2)})`,
            });
        }
        else if (previousShort >= previousLong && currentShort < currentLong) {
            // Bearish crossover - sell signal
            signals.push({
                symbol: this.symbols[0],
                action: 'sell',
                strength: this.calculateSignalStrength(currentLong, currentShort),
                timestamp: symbolData[symbolData.length - 1].timestamp,
                reason: `Short MA (${currentShort.toFixed(2)}) crossed below Long MA (${currentLong.toFixed(2)})`,
            });
        }
        return signals;
    }
    validate() {
        return (this.shortPeriod > 0 &&
            this.longPeriod > 0 &&
            this.shortPeriod < this.longPeriod &&
            this.symbols.length > 0);
    }
    calculateSMA(data, period) {
        const sma = [];
        for (let i = period - 1; i < data.length; i++) {
            const slice = data.slice(i - period + 1, i + 1);
            const average = slice.reduce((sum, d) => sum + d.close, 0) / period;
            sma.push(average);
        }
        return sma;
    }
    calculateSignalStrength(shortMA, longMA) {
        const difference = Math.abs(shortMA - longMA);
        const average = (shortMA + longMA) / 2;
        const strength = Math.min(difference / average, 1);
        return Math.max(strength, 0.1); // Minimum strength of 0.1
    }
}
//# sourceMappingURL=SimpleMovingAverageStrategy.js.map