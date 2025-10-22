#!/bin/bash

# Setup script for Perplexity-Alpaca integration

echo "Setting up Perplexity-Alpaca Trading Integration..."

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# Perplexity API Configuration
PERPLEXITY_API_KEY=your_perplexity_api_key_here

# Alpaca API Configuration (Paper Trading)
ALPACA_API_KEY=your_alpaca_api_key_here
ALPACA_SECRET_KEY=your_alpaca_secret_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Trading Configuration
PORTFOLIO_SIZE=100000
MAX_POSITION_SIZE=0.1
RISK_PER_TRADE=0.02

# Logging Configuration
LOG_LEVEL=INFO
EOF
    echo "Please update .env file with your actual API keys"
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

# Set permissions
chmod +x setup.sh

echo "Setup complete! Please update your .env file with actual API keys."
echo "Run 'python main.py --test' to start in test mode."