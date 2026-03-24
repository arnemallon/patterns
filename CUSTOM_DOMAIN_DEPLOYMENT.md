# 🌐 Custom Domain Deployment Guide

## 🎯 **Deploy Your Bitcoin Classifier to Your Own Domain**

Choose the deployment method that best fits your needs:

## **Option 1: Railway + Custom Domain (Easiest)** ⭐

### Step 1: Deploy to Railway
```bash
# Push your code to GitHub
git add .
git commit -m "Ready for custom domain deployment"
git push origin main
```

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Create new project → Deploy from GitHub
4. Select your repository
5. Add PostgreSQL database

### Step 2: Add Custom Domain
1. In Railway dashboard → Settings → Domains
2. Click "Add Domain"
3. Enter your domain (e.g., `bitcoin-analyzer.yourdomain.com`)
4. Railway provides DNS instructions

### Step 3: Configure DNS
```
Type: CNAME
Name: bitcoin-analyzer (or your subdomain)
Value: your-app.railway.app
TTL: 300
```

**Cost:** ~$10-20/month + domain cost
**SSL:** Automatic
**Setup Time:** 10 minutes

---

## **Option 2: DigitalOcean + Custom Domain** 🐙

### Step 1: Deploy to DigitalOcean
1. Go to [digitalocean.com](https://digitalocean.com)
2. Create App Platform project
3. Connect GitHub repository
4. Add PostgreSQL database
5. Deploy

### Step 2: Add Custom Domain
1. In App Platform → Settings → Domains
2. Add your domain
3. DigitalOcean handles SSL automatically

### Step 3: Configure DNS
```
Type: A
Name: @ (or subdomain)
Value: [DigitalOcean IP provided]
TTL: 300
```

**Cost:** ~$15-30/month + domain cost
**SSL:** Automatic
**Setup Time:** 15 minutes

---

## **Option 3: VPS + Custom Domain (Full Control)** 🖥️

### Prerequisites
- VPS with Ubuntu 20.04+ (DigitalOcean, Linode, Vultr)
- Domain name
- SSH access

### Step 1: Server Setup
```bash
# Connect to your VPS
ssh root@your-vps-ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Nginx and Certbot
apt install nginx certbot python3-certbot-nginx -y
```

### Step 2: Deploy Application
```bash
# Clone your repository
git clone https://github.com/yourusername/BlockChainAnalysis.git
cd BlockChainAnalysis

# Configure environment
cp production.env.template .env.production
nano .env.production  # Edit with your values

# Deploy with custom domain
./deploy-custom-domain.sh yourdomain.com
```

### Step 3: Configure Nginx
```bash
# Create Nginx configuration
nano /etc/nginx/sites-available/bitcoin-classifier
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://localhost:5001/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Step 4: Enable Site and SSL
```bash
# Enable the site
ln -s /etc/nginx/sites-available/bitcoin-classifier /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# Get SSL certificate
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Configure firewall
ufw allow ssh
ufw allow 'Nginx Full'
ufw enable
```

**Cost:** ~$5-20/month + domain cost
**SSL:** Let's Encrypt (free)
**Setup Time:** 30 minutes

---

## **Option 4: Google Cloud Run + Custom Domain** ☁️

### Step 1: Deploy to Cloud Run
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/YOUR-PROJECT-ID/bitcoin-classifier
gcloud run deploy --image gcr.io/YOUR-PROJECT-ID/bitcoin-classifier --platform managed --allow-unauthenticated
```

### Step 2: Add Custom Domain
1. Go to Cloud Run → Manage Custom Domains
2. Add your domain
3. Google handles SSL automatically

### Step 3: Configure DNS
```
Type: CNAME
Name: your-subdomain
Value: ghs.googlehosted.com
TTL: 300
```

**Cost:** Pay-per-request + domain cost
**SSL:** Automatic
**Setup Time:** 20 minutes

---

## 🔧 **Environment Variables for Production**

Create `.env.production` file:
```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-super-secure-secret-key-here
DEBUG=False

# Database Configuration
DATABASE_URL=postgresql://postgres:password@db:5432/bitcoin_classifier_prod
POSTGRES_PASSWORD=your-secure-postgres-password

# API Configuration
BLOCKCYPHER_API_TOKEN=your-blockcypher-api-token

# ML Model Paths
MODEL_PATH=ml-models/with_structural_features/og_bitcoin_classifier.joblib
SCALER_PATH=ml-models/with_structural_features/og_scaler.joblib
```

---

## 🌐 **DNS Configuration Examples**

### For Railway/DigitalOcean (CNAME)
```
Type: CNAME
Name: bitcoin-analyzer
Value: your-app.railway.app
TTL: 300
```

### For VPS (A Record)
```
Type: A
Name: @
Value: 192.168.1.100 (your VPS IP)
TTL: 300
```

### For Google Cloud (CNAME)
```
Type: CNAME
Name: bitcoin-analyzer
Value: ghs.googlehosted.com
TTL: 300
```

---

## 🧪 **Testing Your Deployment**

### Health Check
```bash
curl https://yourdomain.com/api/health
```

### Login Test
```bash
curl -X POST https://yourdomain.com/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Frontend Test
```bash
curl https://yourdomain.com
```

---

## 🔒 **Security Checklist**

- [ ] Change default passwords
- [ ] Set up SSL/HTTPS
- [ ] Configure firewall
- [ ] Set up database backups
- [ ] Monitor logs
- [ ] Keep system updated
- [ ] Use strong environment variables

---

## 📊 **Cost Comparison**

| Platform | Monthly Cost | Setup Time | SSL | Control |
|----------|-------------|------------|-----|---------|
| Railway | $10-20 | 10 min | Auto | Medium |
| DigitalOcean | $15-30 | 15 min | Auto | Medium |
| VPS | $5-20 | 30 min | Manual | High |
| Google Cloud | Pay-per-use | 20 min | Auto | Medium |

---

## 🎯 **Recommendation**

**For most users:** Railway + Custom Domain
- ✅ Easiest setup
- ✅ Automatic SSL
- ✅ Good performance
- ✅ Handles ML workloads well

**For full control:** VPS + Custom Domain
- ✅ Complete control
- ✅ Lower cost
- ✅ Custom configurations
- ❌ More setup required

---

## 🆘 **Troubleshooting**

### Common Issues

1. **DNS not propagating**
   - Wait 24-48 hours
   - Check DNS with `dig yourdomain.com`

2. **SSL certificate issues**
   - Ensure domain points to server
   - Check firewall settings
   - Verify Nginx configuration

3. **Application not loading**
   - Check Docker containers: `docker ps`
   - View logs: `docker-compose logs -f`
   - Verify environment variables

### Support Commands
```bash
# Check DNS
dig yourdomain.com

# Test SSL
curl -I https://yourdomain.com

# View application logs
docker-compose logs -f backend

# Check Nginx status
systemctl status nginx
```

---

**🎉 Your Bitcoin Classifier will be live at https://yourdomain.com!**












