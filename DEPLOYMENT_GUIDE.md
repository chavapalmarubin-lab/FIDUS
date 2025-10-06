# FIDUS Investment Platform - Deployment Guide

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **Node.js**: 18.x or higher
- **Python**: 3.9+ with pip
- **Database**: MongoDB Atlas connection
- **Container**: Docker & Kubernetes (for production)
- **Memory**: 4GB RAM minimum
- **Storage**: 20GB available disk space

### Required Services
- MongoDB Atlas database (configured and accessible)
- Kubernetes cluster (for production deployment)
- SSL certificate for HTTPS (production)

---

## Environment Configuration

### Backend Environment Variables
Create `/app/backend/.env` with the following variables:

```env
# Database Configuration
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/fidus_investment_db?retryWrites=true&w=majority

# MT5 Bridge Service (Windows VPS)
MT5_BRIDGE_URL=http://your-windows-vps:8002
MT5_BRIDGE_API_KEY=your-mt5-bridge-api-key  
MT5_BRIDGE_TIMEOUT=30

# Authentication
JWT_SECRET_KEY=your-secure-jwt-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Google OAuth (Optional)
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret

# Frontend URL for CORS
FRONTEND_URL=https://your-domain.com

# Admin Configuration
ADMIN_EMAIL=admin@yourcompany.com
```

### Frontend Environment Variables  
Create `/app/frontend/.env` with:

```env
# Backend API URL
REACT_APP_BACKEND_URL=https://your-domain.com

# Application Configuration
REACT_APP_NAME=FIDUS Investment Platform
REACT_APP_VERSION=1.0.0

# Google OAuth (if enabled)
REACT_APP_GOOGLE_CLIENT_ID=your-google-oauth-client-id
```

---

## Database Setup

### MongoDB Atlas Configuration

1. **Create MongoDB Atlas Account**
   - Sign up at mongodb.com/atlas
   - Create new cluster (M0 free tier acceptable for testing)

2. **Database Setup**
   ```javascript
   Database Name: fidus_investment_db
   
   Collections to create:
   - users
   - client_readiness  
   - investments
   - mt5_accounts
   - mt5_account_pool (optional)
   ```

3. **Initial Admin User**
   Insert admin user into `users` collection:
   ```javascript
   {
     "id": "admin",
     "username": "admin", 
     "password_hash": "$2b$12$hashed_password_here",
     "name": "Admin User",
     "email": "admin@yourcompany.com",
     "type": "admin",
     "status": "active",
     "created_at": new Date()
   }
   ```

4. **Test Client Data** 
   Insert Alejandro client for testing:
   ```javascript
   {
     "id": "client_alejandro",
     "username": "alejandro_mariscal",
     "name": "Alejandro Mariscal Romero",
     "email": "alexmar7609@gmail.com", 
     "type": "client",
     "status": "active",
     "created_at": new Date()
   }
   ```

5. **Client Readiness Override**
   Insert readiness record:
   ```javascript
   {
     "client_id": "client_alejandro",
     "aml_kyc_completed": true,
     "agreement_signed": true, 
     "investment_ready": true,
     "readiness_override": true,
     "readiness_override_reason": "Initial system setup - client verified offline",
     "updated_at": new Date(),
     "updated_by": "admin"
   }
   ```

---

## Local Development Setup

### Backend Setup
```bash
# Navigate to backend directory
cd /app/backend

# Install Python dependencies
pip install -r requirements.txt

# Start backend service 
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd /app/frontend

# Install Node dependencies
yarn install

# Start development server
yarn dev
```

### Verify Local Setup
- Backend: http://localhost:8001/docs (FastAPI documentation)
- Frontend: http://localhost:3000 
- Admin Login: admin / password123

---

## Production Deployment

### Using Supervisor (Current Setup)
The application is configured to run with Supervisor for process management:

```ini
# /etc/supervisor/conf.d/fidus.conf
[program:backend]
command=python -m uvicorn server:app --host 0.0.0.0 --port 8001
directory=/app/backend
autostart=true
autorestart=true
user=www-data
redirect_stderr=true
stdout_logfile=/var/log/supervisor/backend.out.log

[program:frontend] 
command=yarn preview --host 0.0.0.0 --port 3000
directory=/app/frontend
autostart=true
autorestart=true
user=www-data
redirect_stderr=true
stdout_logfile=/var/log/supervisor/frontend.out.log
```

### Service Management Commands
```bash
# Start all services
sudo supervisorctl start all

# Restart all services  
sudo supervisorctl restart all

# Check service status
sudo supervisorctl status

# View logs
tail -f /var/log/supervisor/backend.out.log
tail -f /var/log/supervisor/frontend.out.log
```

### Kubernetes Deployment (Recommended for Production)

1. **Build Docker Images**
   ```dockerfile
   # Backend Dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
   
   # Frontend Dockerfile  
   FROM node:18-alpine
   WORKDIR /app
   COPY package*.json .
   RUN yarn install
   COPY . .
   RUN yarn build
   CMD ["yarn", "preview", "--host", "0.0.0.0", "--port", "3000"]
   ```

2. **Kubernetes Manifests**
   ```yaml
   # backend-deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: fidus-backend
   spec:
     replicas: 2
     selector:
       matchLabels:
         app: fidus-backend
     template:
       metadata:
         labels:
           app: fidus-backend
       spec:
         containers:
         - name: backend
           image: fidus-backend:latest
           ports:
           - containerPort: 8001
           env:
           - name: MONGO_URL
             valueFrom:
               secretKeyRef:
                 name: fidus-secrets
                 key: mongo-url
   ```

3. **Ingress Configuration**
   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: fidus-ingress
   spec:
     rules:
     - host: your-domain.com
       http:
         paths:
         - path: /api
           pathType: Prefix
           backend:
             service:
               name: fidus-backend-service
               port:
                 number: 8001
         - path: /
           pathType: Prefix  
           backend:
             service:
               name: fidus-frontend-service
               port:
                 number: 3000
   ```

---

## SSL Certificate Setup

### Using Let's Encrypt
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Generate certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
0 12 * * * /usr/bin/certbot renew --quiet
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # API routes to backend
    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Frontend routes
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Health Checks and Monitoring

### Application Health Endpoints
```bash
# Backend health
curl https://your-domain.com/api/mt5/pool/test

# Frontend health  
curl https://your-domain.com/

# Database connectivity
curl -H "Authorization: Bearer {token}" https://your-domain.com/api/clients/ready-for-investment
```

### Log Monitoring
```bash
# Backend API logs
tail -f /var/log/supervisor/backend.out.log

# Frontend logs
tail -f /var/log/supervisor/frontend.out.log

# System logs
journalctl -f -u supervisor
```

### Performance Monitoring
Monitor these key metrics:
- API response times (< 2 seconds for investment creation)
- Database connection count
- Memory usage (< 80% of available RAM)
- Active user sessions
- Investment creation success rate

---

## Backup and Recovery

### Database Backup
```bash
# MongoDB Atlas automatic backups enabled
# Manual backup using mongodump
mongodump --uri="mongodb+srv://user:pass@cluster.mongodb.net/fidus_investment_db" --out=/backup/$(date +%Y%m%d)

# Restore from backup
mongorestore --uri="mongodb+srv://user:pass@cluster.mongodb.net/fidus_investment_db" /backup/20251006/fidus_investment_db
```

### Application Backup
```bash
# Backup application files
tar -czf fidus-backup-$(date +%Y%m%d).tar.gz /app

# Backup configuration
cp /app/backend/.env /backup/backend-env-$(date +%Y%m%d)
cp /app/frontend/.env /backup/frontend-env-$(date +%Y%m%d)
```

### Recovery Procedures
1. Stop application services
2. Restore database from backup
3. Restore application files 
4. Update environment variables if needed
5. Restart services
6. Verify system functionality

---

## Security Configuration

### Firewall Setup
```bash
# Allow necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP  
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### Security Headers
Add to Nginx configuration:
```nginx
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
```

### Regular Security Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Update Node.js dependencies
cd /app/frontend && yarn upgrade

# Update Python packages  
cd /app/backend && pip install -r requirements.txt --upgrade
```

---

## Troubleshooting

### Common Issues

**Service Won't Start**
```bash
# Check supervisor status
sudo supervisorctl status

# Check logs for errors
tail -f /var/log/supervisor/backend.out.log

# Restart services
sudo supervisorctl restart all
```

**Database Connection Error**
- Verify MONGO_URL in environment variables
- Check MongoDB Atlas IP whitelist
- Test connection: `mongo "mongodb+srv://..."`

**API Authentication Failures**
- Verify JWT_SECRET_KEY matches between sessions
- Check token expiration settings
- Clear browser localStorage and re-login

**Frontend Build Errors**
```bash
# Clear cache and rebuild
cd /app/frontend
rm -rf node_modules yarn.lock
yarn install
yarn build
```

### Getting Support
1. Check application logs for specific error messages
2. Verify all environment variables are properly set
3. Test individual components (database, backend API, frontend)
4. Document exact steps to reproduce issues
5. Include relevant log entries when requesting support

---

## Maintenance Tasks

### Regular Maintenance (Weekly)
- Review application logs for errors
- Monitor database storage usage
- Check SSL certificate expiration dates
- Verify backup completeness

### Monthly Tasks
- Update system packages
- Review investment data for consistency
- Audit user access and permissions
- Performance testing and optimization

### Quarterly Tasks  
- Security audit and penetration testing
- Database performance optimization
- Disaster recovery testing
- Documentation updates