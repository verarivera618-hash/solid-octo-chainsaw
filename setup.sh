#!/bin/bash

# Setup script for Perplexity-Alpaca Trading Integration

echo "Setting up Perplexity-Alpaca Trading Integration..."

# Create necessary directories
mkdir -p cursor_tasks
mkdir -p logs
mkdir -p data
mkdir -p tests

# Set up environment
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file with your API keys"
fi

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Set permissions
chmod +x setup.sh

echo "Setup complete! Please configure your API keys in .env file"