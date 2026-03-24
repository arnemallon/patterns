#!/bin/bash

# Bitcoin Classifier Custom Domain Deployment Script
set -e

echo "🌐 Bitcoin Classifier Custom Domain Deployment"
echo "=============================================="

# Check if domain is provided
if [ -z "$1" ]; then
    echo "❌ Please provide your domain name"
    echo "Usage: ./deploy-custom-domain.sh yourdomain.com"
    exit 1
fi

DOMAIN=$1
echo "🎯 Deploying to domain: $DOMAIN"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "✅ Docker is installed"

# Create production environment file
if [ ! -f .env.production ]; then
    echo "📝 Creating production environment file..."
    cp production.env.template .env.production
    echo "⚠️  Please edit .env.production file with your actual values!"
    echo "   - SECRET_KEY: Generate a secure random key"
    echo "   - POSTGRES_PASSWORD: Set a secure database password"
    echo "   - BLOCKCYPHER_API_TOKEN: Your BlockCypher API token"
    read -p "Press Enter to continue after editing .env.production file..."
fi

# Update nginx configuration with your domain
echo "🔧 Configuring Nginx for domain: $DOMAIN"
sed "s/yourdomain.com/$DOMAIN/g" frontend/nginx-custom-domain.conf > frontend/nginx.conf

# Load environment variables
export $(cat .env.production | grep -v '^#' | xargs)

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
    docker-compose -f docker-compose.prod.yml logs db
    exit 1
fi

# Check backend health
if curl -f http://localhost:5001/api/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    docker-compose -f docker-compose.prod.yml logs backend
    exit 1
fi

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend is not accessible"
    docker-compose -f docker-compose.prod.yml logs frontend
    exit 1
fi

echo ""
echo "🎉 Custom domain deployment successful!"
echo "======================================"
echo "🌐 Your app is running on:"
echo "   Local: http://localhost:3000"
echo "   Backend: http://localhost:5001/api"
echo ""
echo "🔧 Next steps for custom domain:"
echo "1. Point your domain DNS to this server's IP"
echo "2. Set up Nginx reverse proxy (see VPS_DEPLOYMENT.md)"
echo "3. Get SSL certificate: certbot --nginx -d $DOMAIN"
echo "4. Configure firewall: ufw allow 'Nginx Full'"
echo ""
echo "📋 Useful commands:"
echo "   View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "   Stop services: docker-compose -f docker-compose.prod.yml down"
echo "   Restart: docker-compose -f docker-compose.prod.yml restart"
echo ""
echo "🔐 Default login credentials:"
echo "   Admin: admin / admin123"
echo "   Demo: demo / demo"
echo ""
echo "🔒 Security Notes:"
echo "   - Change default passwords in production"
echo "   - Set up SSL/HTTPS for your domain"
echo "   - Configure firewall rules"
echo "   - Set up regular database backups"












