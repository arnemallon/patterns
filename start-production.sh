#!/bin/bash

# Bitcoin Classifier Production Startup Script
set -e

echo "🚀 Starting Bitcoin Classifier in Production Mode"
echo "=================================================="

# Check if PostgreSQL is running
if ! pg_isready -q; then
    echo "❌ PostgreSQL is not running. Please start PostgreSQL first."
    echo "   On macOS: brew services start postgresql"
    echo "   On Ubuntu: sudo systemctl start postgresql"
    exit 1
fi

echo "✅ PostgreSQL is running"

# Check if production database exists
if ! psql -lqt | cut -d \| -f 1 | grep -qw bitcoin_classifier_prod; then
    echo "📊 Creating production database..."
    createdb bitcoin_classifier_prod
    echo "✅ Production database created"
else
    echo "✅ Production database exists"
fi

# Set production environment variables
export FLASK_ENV=production
export DATABASE_URL="postgresql://$(whoami)@localhost/bitcoin_classifier_prod"
export SECRET_KEY="production-secret-key-$(date +%s)-$(openssl rand -hex 16)"

# Check if BlockCypher API token is set
if [ -z "$BLOCKCYPHER_API_TOKEN" ]; then
    echo "⚠️  BLOCKCYPHER_API_TOKEN not set. Some features may not work."
    echo "   Set it with: export BLOCKCYPHER_API_TOKEN=your-token"
fi

# Install production dependencies
echo "📦 Installing production dependencies..."
cd backend
source venv/bin/activate
pip install -r requirements-production.txt

# Initialize database
echo "🗄️  Initializing database..."
python -c "
from app import create_app, db
from app.models.user import User
from app.models.classification import Classification
from app.models.alert import Alert
from app.models.case import Case, CaseAddress
import hashlib

app = create_app()
with app.app_context():
    # Create all tables
    db.create_all()
    
    # Create default users if they don't exist
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@blockchainanalysis.com',
            password='admin123',
            first_name='System',
            last_name='Administrator',
            role='admin'
        )
        db.session.add(admin_user)
        print('✅ Created admin user')
    
    demo_user = User.query.filter_by(username='demo').first()
    if not demo_user:
        demo_user = User(
            username='demo',
            email='demo@blockchainanalysis.com',
            password='demo',
            first_name='Demo',
            last_name='User',
            role='investigator'
        )
        db.session.add(demo_user)
        print('✅ Created demo user')
    
    db.session.commit()
    print('✅ Database initialized successfully')
"

# Start the production server
echo "🌐 Starting production server..."
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:5001/api"
echo "   Database: PostgreSQL (bitcoin_classifier_prod)"
echo ""
echo "🔐 Default login credentials:"
echo "   Admin: admin / admin123"
echo "   Demo: demo / demo"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================================="

# Start with gunicorn for production
gunicorn --bind 0.0.0.0:5001 --workers 2 --timeout 120 --access-logfile - --error-logfile - run:app
