# 🖥️ VPS Deployment Guide for Custom Domain

## Prerequisites
- VPS with Ubuntu 20.04+ (DigitalOcean, Linode, Vultr, etc.)
- Domain name pointing to your VPS IP
- SSH access to your VPS

## Step 1: Server Setup

### Connect to your VPS
```bash
ssh root@your-vps-ip
```

### Update system
```bash
apt update && apt upgrade -y
```

### Install Docker and Docker Compose
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Add user to docker group
usermod -aG docker $USER
```

### Install Nginx (for reverse proxy and SSL)
```bash
apt install nginx certbot python3-certbot-nginx -y
```

## Step 2: Deploy Application

### Clone your repository
```bash
git clone https://github.com/yourusername/BlockChainAnalysis.git
cd BlockChainAnalysis
```

### Create production environment file
```bash
cp production.env.template .env.production
nano .env.production
```

### Configure environment variables
```bash
# .env.production
FLASK_ENV=production
SECRET_KEY=your-super-secure-secret-key-here
DATABASE_URL=postgresql://postgres:your-secure-password@db:5432/bitcoin_classifier_prod
BLOCKCYPHER_API_TOKEN=your-blockcypher-token
POSTGRES_PASSWORD=your-secure-postgres-password
MODEL_PATH=ml-models/with_structural_features/og_bitcoin_classifier.joblib
SCALER_PATH=ml-models/with_structural_features/og_scaler.joblib
```

### Deploy with Docker Compose
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Step 3: Configure Nginx

### Create Nginx configuration
```bash
nano /etc/nginx/sites-available/bitcoin-classifier
```

### Add this configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:5001/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Enable the site
```bash
ln -s /etc/nginx/sites-available/bitcoin-classifier /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

## Step 4: SSL Certificate

### Get SSL certificate with Let's Encrypt
```bash
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Auto-renewal
```bash
crontab -e
# Add this line:
0 12 * * * /usr/bin/certbot renew --quiet
```

## Step 5: Firewall Configuration

```bash
# Allow SSH, HTTP, and HTTPS
ufw allow ssh
ufw allow 'Nginx Full'
ufw enable
```

## Step 6: Monitoring and Maintenance

### View logs
```bash
# Application logs
docker-compose -f docker-compose.prod.yml logs -f

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Backup database
```bash
# Create backup script
nano /root/backup-db.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose -f /root/BlockChainAnalysis/docker-compose.prod.yml exec -T db pg_dump -U postgres bitcoin_classifier_prod > /root/backups/backup_$DATE.sql
```

### Set up automated backups
```bash
mkdir -p /root/backups
chmod +x /root/backup-db.sh
crontab -e
# Add: 0 2 * * * /root/backup-db.sh
```

## Cost Breakdown
- VPS: $5-20/month (depending on size)
- Domain: $10-15/year
- SSL: Free (Let's Encrypt)
- **Total: ~$5-20/month**

## Security Checklist
- [ ] Change default passwords
- [ ] Set up firewall
- [ ] Enable SSL/HTTPS
- [ ] Regular backups
- [ ] Monitor logs
- [ ] Keep system updated












