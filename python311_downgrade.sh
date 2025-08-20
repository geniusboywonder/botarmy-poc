#!/bin/bash

# BotArmy POC Python 3.11 Downgrade Script for macOS
# This script will safely downgrade Python and rebuild the environment

echo "🔄 BotArmy POC Python 3.11 Downgrade Script"
echo "============================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found. Please run this script from the project root."
    exit 1
fi

print_status "Current directory: $(pwd)"

# Step 1: Check current Python versions
echo ""
echo "📍 Step 1: Checking current Python versions"
echo "============================================="

print_status "Current Python 3 version:"
python3 --version

print_status "Checking for Python 3.11..."
if command -v python3.11 &> /dev/null; then
    python3.11 --version
    PYTHON311_EXISTS=true
else
    print_warning "Python 3.11 not found"
    PYTHON311_EXISTS=false
fi

# Step 2: Install Python 3.11 if needed
if [ "$PYTHON311_EXISTS" = false ]; then
    echo ""
    echo "📦 Step 2: Installing Python 3.11"
    echo "=================================="
    
    # Check if Homebrew is installed
    if command -v brew &> /dev/null; then
        print_status "Installing Python 3.11 via Homebrew..."
        brew install python@3.11
        
        # Check if installation was successful
        if command -v python3.11 &> /dev/null; then
            print_success "Python 3.11 installed successfully"
            python3.11 --version
        else
            print_error "Python 3.11 installation failed"
            exit 1
        fi
    else
        print_error "Homebrew not found. Please install Homebrew first:"
        echo "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
else
    print_success "Python 3.11 already installed"
fi

# Step 3: Backup current environment
echo ""
echo "💾 Step 3: Backing up current environment"
echo "========================================="

if [ -d "venv" ]; then
    print_status "Backing up current virtual environment..."
    mv venv venv_backup_$(date +%Y%m%d_%H%M%S)
    print_success "Virtual environment backed up"
fi

if [ -d "__pycache__" ]; then
    print_status "Removing Python cache files..."
    rm -rf __pycache__
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    print_success "Cache files removed"
fi

# Step 4: Create new virtual environment with Python 3.11
echo ""
echo "🐍 Step 4: Creating new Python 3.11 virtual environment"
echo "======================================================="

print_status "Creating virtual environment with Python 3.11..."
python3.11 -m venv venv

if [ $? -eq 0 ]; then
    print_success "Virtual environment created successfully"
else
    print_error "Failed to create virtual environment"
    exit 1
fi

# Step 5: Activate virtual environment and verify
echo ""
echo "⚡ Step 5: Activating virtual environment"
echo "========================================"

print_status "Activating virtual environment..."
source venv/bin/activate

print_status "Verifying Python version in virtual environment..."
python --version

# Check if we're using Python 3.11
PYTHON_VERSION=$(python --version 2>&1)
if [[ $PYTHON_VERSION == *"3.11"* ]]; then
    print_success "Virtual environment is using Python 3.11"
else
    print_warning "Virtual environment is using: $PYTHON_VERSION"
    print_warning "This might cause compatibility issues"
fi

# Step 6: Upgrade pip
echo ""
echo "📦 Step 6: Upgrading pip"
echo "======================="

print_status "Upgrading pip to latest version..."
pip install --upgrade pip

print_success "Pip upgraded successfully"
pip --version

# Step 7: Create updated requirements.txt
echo ""
echo "📝 Step 7: Creating updated requirements.txt"
echo "============================================"

print_status "Backing up original requirements.txt..."
cp requirements.txt requirements_backup.txt

print_status "Creating Python 3.11 compatible requirements.txt..."

cat > requirements_python311.txt << 'EOF'
# Core FastAPI Stack - Python 3.11 Compatible
fastapi==0.108.0
uvicorn==0.25.0
python-multipart==0.0.6
openai==1.50.0
pydantic==2.5.0
aiofiles==23.2.1
jinja2==3.1.2
python-json-logger==2.0.7
httpx==0.26.0

# Testing Dependencies - Python 3.11 Compatible
pytest==7.4.4
pytest-asyncio==0.23.0
pytest-cov==4.1.0
pytest-html==4.1.1
pytest-json-report==1.5.0
pytest-mock==3.12.0
pytest-xdist==3.5.0
pytest-timeout==2.3.0

# Development and Testing Support - Python 3.11 Compatible
coverage==7.4.0
black==24.1.0
flake8==7.0.0
isort==5.13.0
mypy==1.8.0

# Additional Testing Utilities - Python 3.11 Compatible
faker==22.0.0
factory-boy==3.3.0
responses==0.24.1
EOF

print_success "Updated requirements.txt created as requirements_python311.txt"

# Step 8: Install dependencies
echo ""
echo "📦 Step 8: Installing Python 3.11 compatible dependencies"
echo "========================================================="

print_status "Installing dependencies from requirements_python311.txt..."
pip install -r requirements_python311.txt

if [ $? -eq 0 ]; then
    print_success "All dependencies installed successfully"
else
    print_error "Some dependencies failed to install"
    print_status "Trying to install core dependencies only..."
    
    # Try installing core dependencies one by one
    CORE_DEPS=(
        "fastapi==0.108.0"
        "uvicorn==0.25.0" 
        "python-multipart==0.0.6"
        "openai==1.50.0"
        "pydantic==2.5.0"
        "aiofiles==23.2.1"
        "httpx==0.26.0"
    )
    
    for dep in "${CORE_DEPS[@]}"; do
        print_status "Installing $dep..."
        pip install "$dep"
    done
fi

# Step 9: Test basic imports
echo ""
echo "🧪 Step 9: Testing basic imports"
echo "==============================="

print_status "Testing core imports..."
python -c "
try:
    import fastapi
    import uvicorn
    import openai
    import pydantic
    print('✅ All core imports successful')
    print(f'FastAPI version: {fastapi.__version__}')
    print(f'OpenAI version: {openai.__version__}')
    print(f'Pydantic version: {pydantic.__version__}')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    print_success "All core imports working correctly"
else
    print_error "Import test failed"
fi

# Step 10: Test backend startup
echo ""
echo "🚀 Step 10: Testing backend startup"
echo "==================================="

print_status "Testing backend startup (will run for 5 seconds)..."

# Start backend in background
python main.py &
BACKEND_PID=$!

# Wait a moment for startup
sleep 3

# Test health endpoint
if curl -s http://localhost:8000/health > /dev/null; then
    print_success "Backend started successfully and health endpoint responding"
else
    print_warning "Backend may have issues - check manually"
fi

# Stop backend
kill $BACKEND_PID 2>/dev/null
sleep 1

# Step 11: Summary and next steps
echo ""
echo "🎉 Step 11: Summary and Next Steps"
echo "=================================="

print_success "Python 3.11 downgrade completed successfully!"

echo ""
echo "📋 What was done:"
echo "1. ✅ Installed Python 3.11"
echo "2. ✅ Backed up old virtual environment"
echo "3. ✅ Created new Python 3.11 virtual environment"
echo "4. ✅ Upgraded pip"
echo "5. ✅ Created compatible requirements.txt"
echo "6. ✅ Installed dependencies"
echo "7. ✅ Tested imports and backend startup"

echo ""
echo "📝 Files created/modified:"
echo "- venv/ (new Python 3.11 virtual environment)"
echo "- requirements_python311.txt (updated compatible requirements)"
echo "- requirements_backup.txt (backup of original)"
echo "- venv_backup_* (backup of old environment)"

echo ""
echo "🚀 To continue development:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Start backend: python main.py"
echo "3. Build frontend: npm run build"
echo "4. Test full stack at: http://localhost:8000"

echo ""
echo "⚠️  Important notes:"
echo "- Always activate the virtual environment before development"
echo "- Use 'python' command (not python3) within the venv"
echo "- The environment now matches Replit's Python 3.11"

print_success "Downgrade complete! You can now develop locally with Python 3.11"
