#!/bin/bash
echo "Starting BotArmy POC..."

# Check if static files exist, if not build them
if [ ! -d "static" ] || [ ! -f "static/index.html" ]; then
    echo "Building frontend..."
    npm run build
fi

# Start the FastAPI server
echo "Starting backend server..."
python main.py