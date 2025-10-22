#!/usr/bin/env bash
set -euo pipefail
python -m pip install --upgrade pip
pip install -r requirements.txt
#!/bin/bash
# Setup script for Perplexity-Alpaca Trading Integration

set -e

echo "🚀 Setting up Perplexity-Alpaca Trading Integration..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs cursor_tasks tests

# Copy .env.example to .env if .env doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys!"
fi

# Create __init__.py files for Python packages
echo "📝 Creating package files..."
touch src/__init__.py
touch tests/__init__.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run tests: python main.py test --tickers AAPL"
echo "4. Generate strategy: python main.py analyze --tickers AAPL MSFT --strategy momentum"
echo ""
