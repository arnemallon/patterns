# 🚀 Bitcoin Classifier Production Deployment Guide

## ✅ Production Setup Complete!

Your Bitcoin Classifier is now ready for production deployment with PostgreSQL database and proper user isolation.

## 🏗️ Production Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   PostgreSQL    │
│   (Svelte)      │◄──►│   (Flask)       │◄──►│   Database      │
│   Port: 3000    │    │   Port: 5001    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Production Deploy

### Option 1: Local Production (Recommended for Testing)
```bash
# Start production server with PostgreSQL
./start-production.sh
```

### Option 2: Docker Production
```bash
# Deploy with Docker Compose
./deploy-production.sh
```

### Option 3: Cloud Deployment
Choose your platform and follow the deployment guide below.

## 🔧 Production Configuration

### Environment Variables
```bash
# Copy template and configure
cp production.env.template production.env

# Required settings:
SECRET_KEY=your-super-secure-production-secret-key
DATABASE_URL=postgresql://user:pass@localhost:5432/bitcoin_classifier_prod
BLOCKCYPHER_API_TOKEN=your-blockcypher-api-token
POSTGRES_PASSWORD=your-secure-database-password
```

### Database Setup
- **Production Database:** `bitcoin_classifier_prod`
- **Users:** Auto-created (admin/demo)
- **Tables:** Auto-migrated from models
- **Indexes:** Optimized for performance

## 🌐 Cloud Deployment Options

### 1. Railway (Recommended)
**Best for:** ML applications with moderate traffic
- **Cost:** $10-20/month
- **Setup:** Connect GitHub → Deploy
- **Features:** Auto-scaling, PostgreSQL, HTTPS

```bash
# Deploy to Railway
git add .
git commit -m "Production ready"
git push origin main
# Connect repo at railway.app
```

### 2. Google Cloud Run
**Best for:** High-traffic, serverless deployment
- **Cost:** Pay-per-request
- **Setup:** Docker containerization
- **Features:** Auto-scaling, global CDN

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT-ID/bitcoin-classifier
gcloud run deploy --image gcr.io/PROJECT-ID/bitcoin-classifier
```

### 3. DigitalOcean App Platform
**Best for:** Simple, cost-effective deployment
- **Cost:** $15-30/month
- **Setup:** Connect GitHub → Deploy
- **Features:** Managed database, auto-scaling

### 4. AWS App Runner
**Best for:** Enterprise-grade deployment
- **Cost:** $25-50/month
- **Setup:** Docker containerization
- **Features:** AWS ecosystem integration

## 🔒 Security Checklist

### ✅ Completed
- [x] User authentication with session tokens
- [x] User data isolation (multi-tenant)
- [x] PostgreSQL database (production-ready)
- [x] Environment variable configuration
- [x] Non-root Docker containers
- [x] Health checks and monitoring

### 🔧 Production Security
- [ ] Change default passwords
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure firewall rules
- [ ] Set up database backups
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerts

## 📊 Performance Specifications

### ML Model Requirements
- **TensorFlow:** 2.16.2
- **Memory:** ~1GB per worker
- **CPU:** High during classification
- **Response Time:** 2-5 seconds per address

### Database Performance
- **PostgreSQL:** Optimized with indexes
- **Connection Pooling:** Gunicorn workers
- **Query Optimization:** User-filtered queries

### Scaling Recommendations
- **Small:** 1-2 workers, 1GB RAM
- **Medium:** 2-4 workers, 2-4GB RAM
- **Large:** 4-8 workers, 4-8GB RAM

## 🧪 Testing Production Setup

### Health Checks
```bash
# Backend health
curl http://localhost:5001/api/health

# Database connection
psql -d bitcoin_classifier_prod -c "SELECT COUNT(*) FROM users;"

# User authentication
curl -X POST http://localhost:5001/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### User Isolation Test
```bash
# Login as admin
ADMIN_TOKEN=$(curl -s -X POST http://localhost:5001/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | jq -r '.session_token')

# Login as demo
DEMO_TOKEN=$(curl -s -X POST http://localhost:5001/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demo"}' | jq -r '.session_token')

# Test user-specific data
curl -H "Authorization: Bearer $ADMIN_TOKEN" http://localhost:5001/api/stats
curl -H "Authorization: Bearer $DEMO_TOKEN" http://localhost:5001/api/stats
```

## 📈 Monitoring & Maintenance

### Logs
```bash
# View application logs
docker-compose -f docker-compose.prod.yml logs -f backend

# View database logs
docker-compose -f docker-compose.prod.yml logs -f db
```

### Database Maintenance
```bash
# Backup database
pg_dump bitcoin_classifier_prod > backup_$(date +%Y%m%d).sql

# Restore database
psql bitcoin_classifier_prod < backup_20250903.sql
```

### Performance Monitoring
- **Response Times:** Monitor API endpoints
- **Database Queries:** Check slow query log
- **Memory Usage:** Monitor worker processes
- **Error Rates:** Track failed requests

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check PostgreSQL status
   brew services list | grep postgresql
   
   # Restart PostgreSQL
   brew services restart postgresql
   ```

2. **ML Model Loading Errors**
   ```bash
   # Check model files exist
   ls -la ml-models/with_structural_features/
   
   # Verify TensorFlow installation
   python -c "import tensorflow as tf; print(tf.__version__)"
   ```

3. **Port Already in Use**
   ```bash
   # Find process using port
   lsof -i :5001
   
   # Kill process
   kill -9 <PID>
   ```

### Support Commands
```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# View resource usage
docker stats

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

## 🎯 Next Steps

1. **Deploy to Cloud Platform** (Railway recommended)
2. **Set up Domain and HTTPS**
3. **Configure Monitoring and Alerts**
4. **Set up Automated Backups**
5. **Performance Testing and Optimization**

## 📞 Support

- **Documentation:** See `DEPLOYMENT.md` for detailed setup
- **Issues:** Check logs and health endpoints
- **Performance:** Monitor resource usage and response times

---

**🎉 Your Bitcoin Classifier is production-ready!**

**Default Login Credentials:**
- Admin: `admin` / `admin123`
- Demo: `demo` / `demo`

**Remember to change these passwords in production!**












