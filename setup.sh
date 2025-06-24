#!/bin/bash

echo "🚀 Setting up Bitcoin Address Classifier Project"

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

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL is not installed. You'll need to install it manually."
    echo "   Visit: https://www.postgresql.org/download/"
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
    cp env.example .env
    echo "✅ Created .env file. Please update it with your database credentials."
fi

cd ..

echo "📦 Setting up Svelte frontend..."

# Install Node.js dependencies
cd frontend
npm install

cd ..

echo "🗄️  Database Setup Instructions:"
echo "1. Create a PostgreSQL database:"
echo "   createdb bitcoin_classifier"
echo ""
echo "2. Run the schema:"
echo "   psql -d bitcoin_classifier -f database/schema.sql"
echo ""
echo "3. Update backend/.env with your database URL"
echo ""

echo "🎯 Next Steps:"
echo "1. Update backend/.env with your database credentials"
echo "2. Start the backend: cd backend && python run.py"
echo "3. Start the frontend: cd frontend && npm run dev"
echo "4. Open http://localhost:3000 in your browser"
echo ""

echo "✅ Setup complete!" 