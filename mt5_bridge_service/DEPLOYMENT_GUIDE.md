# FIDUS MT5 Bridge Service - VPS Deployment Guide

## 🖥️ VPS Information
- **IP Address**: 217.197.163.11
- **Username**: chavapalmarubin@gmail.com
- **Password**: 2170Tenoch!
- **OS**: Windows Server
- **Service Port**: 8000

## 📋 Prerequisites Checklist

### 1. Remote Desktop Connection
```bash
# Connect to VPS using RDP
# Windows: Remote Desktop Connection
# Mac: Microsoft Remote Desktop from App Store
# Linux: Remmina or similar RDP client

Host: 217.197.163.11
Username: chavapalmarubin@gmail.com
Password: 2170Tenoch!
```

### 2. Install Python (if not already installed)
1. Download Python 3.11+ from https://python.org
2. **IMPORTANT**: Check "Add to PATH" during installation
3. Verify installation: `python --version`

### 3. Install MetaTrader 5 Terminal
1. Download MT5 from your broker's website
2. Install and login with your trading account
3. Ensure MT5 terminal stays running for API access

## 🚀 Deployment Steps

### Step 1: Upload Files to VPS
Upload these files to `C:\mt5_bridge_service\`:
- `main_production.py`
- `requirements.txt`
- `setup_vps.bat`
- `generate_keys.py`
- `configure_firewall.bat`
- `.env.template`

### Step 2: Run Setup Script
```cmd
# On VPS, open Command Prompt as Administrator
cd C:\mt5_bridge_service
setup_vps.bat
```

### Step 3: Generate Security Keys
```cmd
python generate_keys.py
```
Copy the generated keys to your `.env` file.

### Step 4: Configure Environment
1. Copy `.env.template` to `.env`
2. Edit `.env` with generated keys:
```env
MT5_BRIDGE_API_KEY=your_generated_api_key
MT5_ENCRYPTION_KEY=your_generated_encryption_key
ENVIRONMENT=prod
PORT=8000
LOG_LEVEL=info
```

### Step 5: Configure Firewall
```cmd
# Run as Administrator
configure_firewall.bat
```

### Step 6: Start Service
```cmd
# Test run first
python main_production.py

# If successful, use service scripts:
start_service.bat
```

### Step 7: Verify Service
Open browser on VPS: http://localhost:8000/health

Expected response:
```json
{
  "status": "healthy",
  "mt5_available": true,
  "mt5_initialized": true,
  "timestamp": "2025-01-04T..."
}
```

## 🔧 FIDUS Backend Configuration

Update FIDUS backend `.env` file:
```env
MT5_BRIDGE_URL=http://217.197.163.11:8000
MT5_BRIDGE_API_KEY=same_key_as_vps
MT5_BRIDGE_TIMEOUT=30
MT5_ENCRYPTION_KEY=same_encryption_key_as_vps
```

## 🧪 Testing Integration

### 1. Test from FIDUS Backend
```python
# In FIDUS backend, run:
from mt5_bridge_client import mt5_bridge
health = await mt5_bridge.health_check()
print(health)
```

### 2. Test MT5 Connection
Use FIDUS admin dashboard:
1. Go to MT5 Management
2. Click "Test Connection"
3. Enter MT5 credentials
4. Verify connection success

## 🔍 Troubleshooting

### Common Issues:

**1. Service won't start**
- Check Python installation: `python --version`
- Verify dependencies: `pip list`
- Check logs in service directory

**2. Connection refused from FIDUS**
- Verify firewall settings (port 8000 open)
- Check VPS IP address is correct
- Ensure service is running: `netstat -an | find ":8000"`

**3. MT5 not connecting**
- Ensure MT5 terminal is running and logged in
- Verify MetaTrader5 package: `pip show MetaTrader5`
- Check MT5 account credentials

**4. API key errors**
- Ensure same API key in both VPS `.env` and FIDUS backend `.env`
- Regenerate keys if needed: `python generate_keys.py`

### Service Logs
Check logs in: `C:\mt5_bridge_service\logs\`

### Network Testing
```cmd
# Test port from VPS
netstat -an | find ":8000"

# Test external access (if needed)
telnet 217.197.163.11 8000
```

## 🔒 Security Best Practices

1. **Change default API key** - Never use example keys
2. **Use strong encryption key** - Generate with script
3. **Limit network access** - Whitelist FIDUS backend IP only
4. **Regular updates** - Keep Python and packages updated
5. **Monitor logs** - Check for suspicious activity
6. **Backup configuration** - Save `.env` file securely

## 📊 Monitoring

### Health Endpoints:
- `GET /health` - Basic health check
- `GET /api/mt5/status` - Detailed MT5 status
- `GET /api/mt5/terminal/info` - MT5 terminal information

### Service Management:
- Start: `start_service.bat`
- Stop: `stop_service.bat` 
- Logs: Check `logs/` directory

## 🆘 Support

If you encounter issues:
1. Check this documentation first
2. Review service logs
3. Test basic connectivity
4. Verify MT5 terminal is running
5. Contact FIDUS technical support with log files

---
**Deployment Date**: 2025-10-04 15:41:17
**Version**: 1.0.0
