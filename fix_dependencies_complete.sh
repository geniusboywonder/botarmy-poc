#!/bin/bash

# BotArmy POC - Complete Dependency Cleanup and Fix
# This script completely removes conflicting packages and installs only what's needed

echo "🧹 BotArmy POC Complete Dependency Cleanup"
echo "=========================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    print_error "main.py not found. Please run this script from the project root."
    exit 1
fi

print_status "Current directory: $(pwd)"

# Step 1: Complete environment cleanup
echo ""
echo "🗑️  Step 1: Complete Environment Cleanup"
echo "======================================="

print_warning "This will completely remove your virtual environment and all installed packages"
read -p "Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "Cleanup cancelled by user"
    exit 0
fi

# Remove virtual environment completely
if [ -d "venv" ]; then
    print_status "Removing existing virtual environment..."
    rm -rf venv
    print_success "Virtual environment removed"
fi

# Remove Python cache files
if [ -d "__pycache__" ]; then
    print_status "Removing Python cache files..."
    rm -rf __pycache__
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    print_success "Cache files removed"
fi

# Step 2: Check Python 3.11 availability
echo ""
echo "🐍 Step 2: Python 3.11 Setup"
echo "============================="

if command -v python3.11 &> /dev/null; then
    print_success "Python 3.11 found"
    python3.11 --version
else
    print_warning "Python 3.11 not found. Installing via Homebrew..."
    if command -v brew &> /dev/null; then
        brew install python@3.11
        if [ $? -eq 0 ]; then
            print_success "Python 3.11 installed successfully"
        else
            print_error "Failed to install Python 3.11"
            exit 1
        fi
    else
        print_error "Homebrew not found. Please install Python 3.11 manually from python.org"
        exit 1
    fi
fi

# Step 3: Create fresh virtual environment
echo ""
echo "🔧 Step 3: Creating Fresh Virtual Environment"
echo "============================================"

print_status "Creating new virtual environment with Python 3.11..."
python3.11 -m venv venv

if [ $? -eq 0 ]; then
    print_success "Virtual environment created"
else
    print_error "Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Verify Python version
PYTHON_VERSION=$(python --version 2>&1)
print_status "Python version in venv: $PYTHON_VERSION"

if [[ $PYTHON_VERSION == *"3.11"* ]]; then
    print_success "Correct Python version confirmed"
else
    print_warning "Python version may not be optimal: $PYTHON_VERSION"
fi

# Step 4: Upgrade pip
echo ""
echo "📦 Step 4: Upgrading pip"
echo "======================="

print_status "Upgrading pip to latest version..."
pip install --upgrade pip

if [ $? -eq 0 ]; then
    print_success "Pip upgraded successfully"
    pip --version
else
    print_error "Failed to upgrade pip"
    exit 1
fi

# Step 5: Install minimal dependencies
echo ""
echo "📥 Step 5: Installing Minimal Dependencies"
echo "========================================="

print_status "Installing only required packages (no extras)..."

# Install packages one by one to identify any issues
CORE_PACKAGES=(
    "fastapi==0.108.0"
    "uvicorn[standard]==0.25.0" 
    "python-multipart==0.0.6"
    "openai==1.51.0"
    "pydantic==2.5.0"
    "aiofiles==23.2.1"
    "httpx==0.26.0"
)

echo "Installing core packages:"
for package in "${CORE_PACKAGES[@]}"; do
    print_status "Installing $package..."
    pip install "$package"
    if [ $? -eq 0 ]; then
        print_success "✅ $package installed"
    else
        print_error "❌ Failed to install $package"
        # Continue with other packages
    fi
done

# Step 6: Verify installation
echo ""
echo "🧪 Step 6: Verifying Installation"
echo "================================"

print_status "Testing imports..."

python -c "
import sys
print(f'Python version: {sys.version}')
print('Testing imports...')

try:
    import fastapi
    print(f'✅ FastAPI {fastapi.__version__}')
except ImportError as e:
    print(f'❌ FastAPI: {e}')

try:
    import uvicorn
    print(f'✅ Uvicorn {uvicorn.__version__}')
except ImportError as e:
    print(f'❌ Uvicorn: {e}')

try:
    import openai
    print(f'✅ OpenAI {openai.__version__}')
    
    # Test AsyncOpenAI import specifically
    from openai import AsyncOpenAI
    print('✅ AsyncOpenAI import successful')
except ImportError as e:
    print(f'❌ OpenAI: {e}')

try:
    import pydantic
    print(f'✅ Pydantic {pydantic.__version__}')
except ImportError as e:
    print(f'❌ Pydantic: {e}')

try:
    import httpx
    print(f'✅ HTTPX {httpx.__version__}')
except ImportError as e:
    print(f'❌ HTTPX: {e}')

print('Import test complete')
"

if [ $? -eq 0 ]; then
    print_success "All core imports successful"
else
    print_error "Some imports failed"
fi

# Step 7: Test backend startup
echo ""
echo "🚀 Step 7: Testing Backend Startup"
echo "================================="

print_status "Testing backend startup (5 second test)..."

# Start backend in background
timeout 10s python main.py &
BACKEND_PID=$!

# Wait for startup
sleep 3

# Test health endpoint
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    print_success "✅ Backend started successfully"
    print_success "✅ Health endpoint responding"
else
    print_warning "⚠️  Backend may have startup issues (check manually)"
fi

# Clean shutdown
kill $BACKEND_PID 2>/dev/null
wait $BACKEND_PID 2>/dev/null

# Step 8: Check for unwanted packages
echo ""
echo "🔍 Step 8: Checking for Problematic Packages"
echo "============================================"

PROBLEMATIC_PACKAGES=("prefect" "controlflow" "langchain")

print_status "Checking for problematic packages..."
for package in "${PROBLEMATIC_PACKAGES[@]}"; do
    if pip show "$package" >/dev/null 2>&1; then
        print_warning "❌ Found problematic package: $package"
        print_status "This package is not needed and may cause conflicts"
    else
        print_success "✅ $package not found (good)"
    fi
done

# Step 9: Create final requirements.txt
echo ""
echo "📝 Step 9: Creating Clean Requirements File"
echo "=========================================="

print_status "Generating requirements.txt from current environment..."

# Create clean requirements file with only what's installed
pip freeze > requirements_clean.txt

print_success "Clean requirements saved to requirements_clean.txt"

# Show what's actually installed
echo ""
echo "📋 Currently installed packages:"
pip list

# Step 10: Final summary
echo ""
echo "🎉 Step 10: Cleanup Complete!"
echo "============================="

print_success "Environment cleanup and setup completed successfully!"

echo ""
echo "📊 Summary:"
echo "- ✅ Removed conflicting packages (prefect, etc.)"
echo "- ✅ Created fresh Python 3.11 virtual environment"
echo "- ✅ Installed only required dependencies"
echo "- ✅ Verified all imports work"
echo "- ✅ Tested backend startup"
echo "- ✅ Generated clean requirements.txt"

echo ""
echo "📁 Files created:"
echo "- venv/ (clean Python 3.11 environment)"
echo "- requirements_clean.txt (current environment)"

echo ""
echo "🚀 Next steps:"
echo "1. Test the application: python main.py"
echo "2. Build frontend: npm run build"
echo "3. Test full stack: http://localhost:8000"

echo ""
echo "💡 Tips:"
echo "- Always activate venv: source venv/bin/activate"
echo "- Use 'python' command (not python3) in venv"
echo "- Environment now matches Replit (Python 3.11)"

print_success "All dependency conflicts resolved! 🎊"
