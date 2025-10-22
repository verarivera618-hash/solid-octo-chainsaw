#!/bin/bash

# Local Trading System Setup Script
# No external dependencies or API keys required!

echo "=========================================="
echo "Setting up Local Trading System"
echo "No API keys or subscriptions needed!"
echo "=========================================="

# Create necessary directories
echo "Creating directory structure..."
mkdir -p local_data
mkdir -p logs
mkdir -p data
mkdir -p cache
mkdir -p cursor_tasks
mkdir -p reports

# Check Python installation
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "Error: Python is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "Using Python: $PYTHON_CMD"

# Install Python dependencies
echo "Installing Python dependencies (local libraries only)..."
$PYTHON_CMD -m pip install --quiet pandas numpy scipy 2>/dev/null || {
    echo "Installing core dependencies..."
    $PYTHON_CMD -m pip install pandas numpy
}

# Create initial database
echo "Initializing local database..."
$PYTHON_CMD -c "
from src.local_data_client import LocalDataClient
from src.local_trading_client import LocalTradingClient
print('Creating database tables...')
data_client = LocalDataClient()
trading_client = LocalTradingClient()
print('Database initialized successfully!')
" 2>/dev/null || echo "Database will be created on first run"

# Generate initial sample data
echo "Generating sample market data..."
$PYTHON_CMD -c "
from src.local_data_client import LocalDataClient
client = LocalDataClient()
symbols = ['AAPL', 'GOOGL', 'MSFT', 'NVDA', 'AMD']
print(f'Generating sample data for {symbols}...')
client.generate_sample_data(symbols, days=365)
print('Sample data generated successfully!')
" 2>/dev/null || echo "Sample data will be generated on first run"

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To start the trading system, run:"
echo "  python src/local_main.py"
echo ""
echo "Features available:"
echo "  ✓ Paper trading simulation"
echo "  ✓ Backtesting strategies"
echo "  ✓ Technical analysis"
echo "  ✓ Risk management"
echo "  ✓ Portfolio tracking"
echo ""
echo "No API keys required!"
echo "No external subscriptions needed!"
echo "Everything runs locally on your machine!"
echo "=========================================="