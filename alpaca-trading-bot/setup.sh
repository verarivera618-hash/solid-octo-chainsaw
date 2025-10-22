#!/bin/bash

# Setup script for Alpaca Trading Bot

echo "🚀 Setting up Alpaca Trading Bot with Perplexity Integration..."

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $REQUIRED_VERSION or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python version: $PYTHON_VERSION"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p logs
mkdir -p data_cache
mkdir -p cursor_tasks
mkdir -p notebooks
mkdir -p tests

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys"
fi

# Run basic tests
echo "Running basic configuration test..."
python -c "from src.config import config; config.validate()" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Configuration is valid"
else
    echo "⚠️  Configuration needs to be updated with valid API keys"
fi

# Set executable permissions
chmod +x main.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys:"
echo "   - PERPLEXITY_API_KEY"
echo "   - ALPACA_API_KEY"
echo "   - ALPACA_SECRET_KEY"
echo ""
echo "2. Generate a Cursor prompt:"
echo "   python main.py --mode generate --symbols AAPL MSFT --strategy momentum"
echo ""
echo "3. Run the trading bot (paper trading):"
echo "   python main.py --mode trade --symbols AAPL MSFT GOOGL"
echo ""
echo "For more information, see README.md"