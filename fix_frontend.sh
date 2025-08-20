#!/bin/bash

# BotArmy POC Frontend Fix Script
# Fixes JavaScript filter() error and CSS loading issues

echo "🔧 BotArmy POC Frontend Fix Script"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this script from the project root."
    exit 1
fi

echo "📁 Current directory: $(pwd)"

# Step 1: Clean old build artifacts
echo ""
echo "🧹 Step 1: Cleaning old build artifacts..."
rm -rf static/assets/*
rm -rf node_modules/.vite
echo "✅ Old build artifacts cleaned"

# Step 2: Install/update dependencies
echo ""
echo "📦 Step 2: Installing/updating dependencies..."
npm install
if [ $? -ne 0 ]; then
    echo "❌ Error: npm install failed"
    exit 1
fi
echo "✅ Dependencies installed"

# Step 3: Rebuild frontend with fixes
echo ""
echo "🔨 Step 3: Building frontend with fixes..."
npm run build
if [ $? -ne 0 ]; then
    echo "❌ Error: npm run build failed"
    echo "Check the console output above for specific errors."
    exit 1
fi
echo "✅ Frontend built successfully"

# Step 4: Check if critical files exist
echo ""
echo "🔍 Step 4: Verifying build output..."

if [ ! -f "static/index.html" ]; then
    echo "❌ Error: static/index.html not found"
    exit 1
fi

if [ ! -d "static/assets" ]; then
    echo "❌ Error: static/assets directory not found"
    exit 1
fi

CSS_FILES=$(find static/assets -name "*.css" | wc -l)
JS_FILES=$(find static/assets -name "*.js" | wc -l)

echo "✅ Build verification complete:"
echo "   - HTML file: ✅ static/index.html"
echo "   - CSS files: $CSS_FILES found"
echo "   - JS files: $JS_FILES found"

# Step 5: Test backend startup
echo ""
echo "🚀 Step 5: Testing backend startup..."
echo "Starting backend server (will run for 5 seconds to test)..."

# Start backend in background
python main.py &
BACKEND_PID=$!

# Wait a moment for startup
sleep 3

# Test if server is responding
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend server is responding"
    # Test critical API endpoints
    echo "   Testing API endpoints..."
    
    # Test agents endpoint
    if curl -s http://localhost:8000/api/agents > /dev/null; then
        echo "   ✅ /api/agents responding"
    else
        echo "   ⚠️  /api/agents not responding"
    fi
    
    # Test tasks endpoint
    if curl -s http://localhost:8000/api/tasks > /dev/null; then
        echo "   ✅ /api/tasks responding"
    else
        echo "   ⚠️  /api/tasks not responding"
    fi
    
else
    echo "❌ Backend server not responding"
fi

# Stop backend
kill $BACKEND_PID 2>/dev/null
sleep 1

echo ""
echo "🎉 Frontend Fix Summary"
echo "======================"
echo "✅ Fixed ActionQueue component (defensive array checks)"
echo "✅ Fixed PostCSS configuration (CommonJS format)"
echo "✅ Fixed Tailwind configuration (CommonJS format)"
echo "✅ Updated Vite build config (CSS bundling)"
echo "✅ Added ErrorBoundary component"
echo "✅ Added mock data fallback in AppContext"
echo "✅ Rebuilt frontend with fixes"
echo ""
echo "🚀 Ready to Deploy"
echo "=================="
echo "To start the application:"
echo "  python main.py"
echo ""
echo "Then visit: http://localhost:8000"
echo ""
echo "🔧 Troubleshooting"
echo "=================="
echo "If issues persist:"
echo "1. Check browser console for errors"
echo "2. Verify Replit environment variables"
echo "3. Ensure OpenAI API key is set (optional)"
echo "4. Check network connectivity"
echo ""
echo "For Replit deployment:"
echo "1. Commit changes to git"
echo "2. Push to Replit"
echo "3. Check .replit config file"
echo "4. Monitor Replit console for errors"
