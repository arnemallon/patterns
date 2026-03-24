#!/bin/bash

# Bitcoin Classifier Production Deployment Script
set -e

echo "🚀 Bitcoin Classifier Production Deployment"
echo "==========================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Check if production environment file exists
if [ ! -f production.env ]; then
    echo "📝 Creating production environment file..."
    cp production.env.template production.env
    echo "⚠️  Please edit production.env file with your actual values before deploying!"
    echo "   - SECRET_KEY: Generate a secure random key"
    echo "   - POSTGRES_PASSWORD: Set a secure database password"
    echo "   - BLOCKCYPHER_API_TOKEN: Your BlockCypher API token"
    echo "   - DATABASE_URL: Your PostgreSQL connection string"
    read -p "Press Enter to continue after editing production.env file..."
fi

# Load environment variables
export $(cat production.env | grep -v '^#' | xargs)

# Build and start production services
echo "🔨 Building and starting production services..."
docker-compose -f docker-compose.prod.yml down --remove-orphans
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 15

# Check if services are running
echo "🔍 Checking service health..."

# Check database health
if docker-compose -f docker-compose.prod.yml exec -T db pg_isready -U postgres > /dev/null 2>&1; then
    echo "✅ Database is healthy"
else
    echo "❌ Database health check failed"
    echo "📋 Database logs:"
    docker-compose -f docker-compose.prod.yml logs db
    exit 1
fi

# Check backend health
if curl -f http://localhost:5001/api/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    echo "📋 Backend logs:"
    docker-compose -f docker-compose.prod.yml logs backend
    exit 1
fi

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend is not accessible"
    echo "📋 Frontend logs:"
    docker-compose -f docker-compose.prod.yml logs frontend
    exit 1
fi

echo ""
echo "🎉 Production deployment successful!"
echo "==================================="
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:5001/api"
echo "📊 Database: PostgreSQL (bitcoin_classifier_prod)"
echo ""
echo "📋 Useful commands:"
echo "   View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "   Stop services: docker-compose -f docker-compose.prod.yml down"
echo "   Restart: docker-compose -f docker-compose.prod.yml restart"
echo "   Update: docker-compose -f docker-compose.prod.yml pull && docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "🔐 Default login credentials:"
echo "   Admin: admin / admin123"
echo "   Demo: demo / demo"
echo ""
echo "🔒 Security Notes:"
echo "   - Change default passwords in production"
echo "   - Use HTTPS in production"
echo "   - Set up proper firewall rules"
echo "   - Regular database backups recommended"












