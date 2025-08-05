#!/bin/bash

echo "Starting Workik AI Test Case Generator Backend..."
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo
    echo "IMPORTANT: Please edit .env file with your GitHub OAuth credentials!"
    echo
    read -p "Press enter to continue..."
fi

# Start the server
echo "Starting FastAPI server..."
python server.py
