# MT5 Windows VM Bridge Deployment Guide

## 🎯 OBJECTIVE
Deploy Windows VM with MetaTrader5 to provide MT5 connectivity for Linux application.

## 📋 WINDOWS VM SETUP

### Step 1: Create Windows VM
```bash
# Azure example
az vm create \
  --resource-group fidus-production \
  --name mt5-bridge-vm \
  --image Win2022Datacenter \
  --size Standard_D2s_v3 \
  --admin-username mt5admin \
  --admin-password [SECURE_PASSWORD]

# AWS example  
aws ec2 run-instances \
  --image-id ami-0c94855ba95b798c7 \
  --instance-type t3.medium \
  --key-name mt5-bridge-key \
  --security-groups mt5-bridge-sg
```

### Step 2: Install MetaTrader5 Terminal
1. **Download MetaTrader5** from official website
2. **Install** MetaTrader5 terminal on Windows VM
3. **Configure** DooTechnology and VT Markets server connections
4. **Test** manual login to both accounts

### Step 3: Install Python Environment
```powershell
# Download and install Python 3.11
# Install required packages
pip install fastapi uvicorn MetaTrader5 python-dotenv requests
```

### Step 4: Deploy Bridge Service
1. **Copy** `/app/mt5_windows_bridge_service.py` to Windows VM
2. **Configure** environment variables:
```powershell
set MT5_BRIDGE_PORT=8080
set BRIDGE_API_KEY=your_secure_api_key
```

3. **Start** the bridge service:
```powershell
python mt5_windows_bridge_service.py
```

### Step 5: Configure Network Access
```bash
# Open port 8080 for Linux application access
# Configure firewall rules
# Set up internal DNS (mt5-bridge.internal)
```

## 🔌 LINUX APPLICATION CONFIGURATION

### Step 1: Update Environment Variables
```bash
# Add to /app/backend/.env
MT5_BRIDGE_URL=http://mt5-bridge.internal:8080
```

### Step 2: Test Connection
```bash
cd /app
python connect_real_mt5_accounts.py
```

## 🧪 TESTING PROCEDURE

### Step 1: Test Bridge Service Health
```bash
curl http://mt5-bridge.internal:8080/
```
Expected response:
```json
{
  "service": "MT5 Windows Bridge",
  "status": "running",
  "mt5_initialized": true
}
```

### Step 2: Connect DooTechnology Account
```bash
curl -X POST http://mt5-bridge.internal:8080/api/mt5/connect \
  -H "Content-Type: application/json" \
  -d '{
    "mt5_login": 9928326,
    "password": "R1d567j!",
    "server": "DooTechnology-Live"
  }'
```

### Step 3: Connect VT Markets PAMM Account
```bash
curl -X POST http://mt5-bridge.internal:8080/api/mt5/connect \
  -H "Content-Type: application/json" \
  -d '{
    "mt5_login": 15759668,
    "password": "BggHyVTDQ5@",
    "server": "VTMarkets-PAMM"
  }'
```

### Step 4: Get Account Information
```bash
# DooTechnology account info
curl http://mt5-bridge.internal:8080/api/mt5/account/9928326/info

# VT Markets account info  
curl http://mt5-bridge.internal:8080/api/mt5/account/15759668/info
```

### Step 5: Get Deposit History
```bash
# DooTechnology deposits
curl http://mt5-bridge.internal:8080/api/mt5/account/9928326/deposits

# VT Markets deposits
curl http://mt5-bridge.internal:8080/api/mt5/account/15759668/deposits
```

## 🔄 LINUX APPLICATION INTEGRATION

The Linux application will automatically use the Windows bridge when:

1. **MT5_BRIDGE_URL** environment variable is set
2. **Bridge service** is running and accessible
3. **MT5 accounts** are connected on Windows VM

### Connection Flow:
```
Salvador Login → Linux App → Windows Bridge → MetaTrader5 → Real MT5 Data
```

## 📊 EXPECTED RESULTS

After successful deployment:

### Salvador Palma Dashboard:
- **BALANCE Fund**: Real amount from DooTechnology MT5 (9928326)
- **CORE Fund**: Real amount from VT Markets PAMM (15759668)
- **Historical Data**: Real deposit dates and amounts
- **Live Updates**: Current equity from MT5 accounts

### System Status:
```bash
# Check bridge status
curl http://mt5-bridge.internal:8080/api/mt5/status
```

Expected response:
```json
{
  "service": "MT5 Windows Bridge",
  "status": "running",
  "connected_accounts": {
    "9928326": {"server": "DooTechnology-Live"},
    "15759668": {"server": "VTMarkets-PAMM"}
  },
  "mt5_terminal_info": {...}
}
```

## 🚨 SECURITY CONSIDERATIONS

1. **Network Security**: Restrict bridge access to Linux application only
2. **Credential Storage**: Use environment variables, not hardcoded passwords
3. **API Authentication**: Implement API key authentication
4. **SSL/TLS**: Use HTTPS for production communication
5. **VM Security**: Keep Windows VM updated and secured

## 🔧 MONITORING & MAINTENANCE

### Health Checks:
- Bridge service uptime monitoring
- MT5 connection status monitoring
- Account balance update monitoring

### Automated Restart:
```powershell
# Windows service or scheduled task to restart bridge if needed
```

### Logging:
- Bridge service logs
- MT5 connection logs
- Error monitoring and alerts

## ⚡ DEPLOYMENT TIMELINE

- **Hour 1**: Create and configure Windows VM
- **Hour 2**: Install MetaTrader5 terminal and test manual connections
- **Hour 3**: Install Python and deploy bridge service
- **Hour 4**: Configure Linux application and test integration
- **Hour 5**: Verify Salvador Palma can see real investment data

## 🎉 SUCCESS CRITERIA

✅ Windows VM running with MetaTrader5 terminal
✅ Bridge service accessible from Linux application
✅ Both MT5 accounts connected (DooTechnology + VT Markets)
✅ Real deposit history retrieved from MT5
✅ Salvador sees correct BALANCE and CORE fund amounts
✅ Live balance updates working

---

**🚀 READY FOR IMMEDIATE DEPLOYMENT**