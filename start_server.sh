#!/bin/bash

# Start the Store Monitoring API server
echo "Starting Store Monitoring API server..."

# Create necessary directories
mkdir -p reports
mkdir -p data

# Install dependencies if needed
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the server
echo "Starting FastAPI server on http://localhost:8000"
python run_server.py
