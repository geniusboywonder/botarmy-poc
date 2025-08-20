#!/bin/bash

# Emergency build script for BotArmy POC
# This script manually builds the React app without complex configurations

echo "🚨 Emergency Build Script - BotArmy POC"
echo "======================================="

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this script from the project root."
    exit 1
fi

echo "📁 Current directory: $(pwd)"

# Step 1: Clean everything
echo "🧹 Cleaning build artifacts and dependencies..."
rm -rf static/assets/*
rm -rf node_modules
rm -rf package-lock.json
rm -f *.backup

# Step 2: Create minimal package.json for emergency build
echo "📦 Creating emergency package.json..."
cat > package.json << 'EOF'
{
  "name": "botarmy-poc-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "@heroicons/react": "^2.2.0",
    "classnames": "^2.5.1",
    "lucide-react": "^0.539.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.0.0",
    "autoprefixer": "^10.4.21",
    "postcss": "^8.5.6",
    "tailwindcss": "^3.4.0",
    "vite": "^5.0.0"
  }
}
EOF

# Step 3: Create minimal vite config
echo "⚙️  Creating minimal vite.config.js..."
cat > vite.config.js << 'EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'static',
    emptyOutDir: true,
  },
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
EOF

# Step 4: Create minimal tailwind config
echo "🎨 Creating minimal tailwind.config.js..."
cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{js,jsx,ts,tsx}", "./index.html"],
  darkMode: 'class',
  theme: { extend: {} },
  plugins: [],
}
EOF

# Step 5: Create minimal postcss config
echo "🔧 Creating minimal postcss.config.js..."
cat > postcss.config.js << 'EOF'
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF

# Step 6: Install dependencies
echo "📥 Installing dependencies..."
npm install
if [ $? -ne 0 ]; then
    echo "❌ npm install failed. Trying with --legacy-peer-deps..."
    npm install --legacy-peer-deps
    if [ $? -ne 0 ]; then
        echo "❌ Installation failed completely. Please check npm/node versions."
        exit 1
    fi
fi

# Step 7: Build
echo "🔨 Building application..."
npm run build
if [ $? -ne 0 ]; then
    echo "❌ Build failed."
    exit 1
fi

# Step 8: Verify
echo "✅ Build completed successfully!"
echo "📁 Files created:"
ls -la static/

echo ""
echo "🚀 Ready to start backend:"
echo "python main.py"
