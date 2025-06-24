#!/bin/bash

echo "🚀 Quick Start - Bitcoin Address Classifier (SQLite Mode)"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

echo "📦 Setting up Python backend..."

# Create virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "SECRET_KEY=dev-secret-key-change-in-production" > .env
    echo "FLASK_ENV=development" >> .env
    echo "✅ Created .env file with default settings (using SQLite)"
fi

cd ..

echo "📦 Setting up Svelte frontend..."

# Install Node.js dependencies
cd frontend
npm install

cd ..

echo "🎯 Ready to start!"
echo ""
echo "To start the application:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python run.py"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then open http://localhost:3000 in your browser"
echo ""
echo "✅ Quick setup complete! The app will use SQLite for development." 