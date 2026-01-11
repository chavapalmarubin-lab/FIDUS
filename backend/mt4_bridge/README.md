# VIKING MT4 Bridge

## Overview
This is a **completely separate** MT4 bridge for VIKING trading operations (account 33627673).
It is isolated from the FIDUS MT5 bridge to ensure data separation.

## Architecture

```
MT4 Terminal (33627673)
    │
    ▼ (HTTP POST to localhost:8001)
VIKING_MT4_Bridge.mq4 (EA)
    │
    ▼
viking_mt4_bridge_service.py (Port 8001)
    │
    ▼ (Direct MongoDB writes)
MongoDB Collections:
├── viking_accounts
└── viking_deals_history
    │
    ▼ (Frontend reads via API)
FIDUS Backend (/api/viking/*)
    │
    ▼
VIKING Dashboard UI
```

## Files

| File | Description |
|------|-------------|
| `VIKING_MT4_Bridge.mq4` | MT4 Expert Advisor that sends account data |
| `viking_mt4_bridge_service.py` | Python service that receives data and writes to MongoDB |
| `start_viking_bridge.bat` | Windows startup script |
| `start_viking_bridge.sh` | Linux/Mac startup script |
| `requirements_viking.txt` | Python dependencies |

## Configuration

### Port: 8001
This is different from FIDUS (port 8000) to allow both bridges to run simultaneously.

### MongoDB Collections
- `viking_accounts` - Account balance, equity, margin data
- `viking_deals_history` - Trade history

### Document IDs
- Account: `_id: "VIKING_33627673"`
- Strategy field: `"CORE"`

## Deployment Steps

### 1. Deploy Python Service to VPS

```bash
# SSH into VPS
ssh user@your-vps

# Create directory
mkdir -p /opt/viking_bridge
cd /opt/viking_bridge

# Copy files (or use GitHub Actions)
# ... copy viking_mt4_bridge_service.py, requirements_viking.txt

# Create .env file
cat > .env << EOF
MONGO_URL=mongodb+srv://...your_connection_string...
DB_NAME=fidus_production
VIKING_BRIDGE_PORT=8001
EOF

# Install dependencies
pip3 install -r requirements_viking.txt

# Start service
python3 viking_mt4_bridge_service.py
```

### 2. Deploy EA to MT4 Terminal

1. Copy `VIKING_MT4_Bridge.mq4` to `MQL4\Experts\` folder
2. Open MetaEditor and compile the EA
3. In MT4: Tools > Options > Expert Advisors
4. Enable "Allow WebRequest for listed URL" and add: `http://localhost:8001`
5. Attach EA to any chart on account 33627673
6. Verify sync in Experts tab

## Verification

### Check service health:
```bash
curl http://localhost:8001/api/viking/health
```

### Check sync status:
```bash
curl http://localhost:8001/api/viking/status
```

### Check MongoDB directly:
```javascript
db.viking_accounts.find({account: 33627673})
db.viking_deals_history.find({account: 33627673}).limit(10)
```

## Troubleshooting

### EA shows "WebRequest error"
- Ensure service is running: `pgrep -f viking_mt4_bridge`
- Ensure URL is added to allowed list in MT4 Options
- Check firewall allows localhost:8001

### No data in MongoDB
- Check `viking_bridge.log` for errors
- Verify MONGO_URL in .env is correct
- Test MongoDB connection with health endpoint

### Service won't start
- Check port 8001 is not in use: `netstat -an | grep 8001`
- Verify Python 3.8+ is installed
- Check .env file has correct MONGO_URL

## Separation from FIDUS

| Aspect | FIDUS | VIKING |
|--------|-------|--------|
| Port | 8000 | 8001 |
| Collections | mt5_accounts, mt5_deals | viking_accounts, viking_deals_history |
| Platform | MT5 | MT4 |
| Document IDs | Various | VIKING_* prefix |
| EA File | MT4_Python_Bridge.mq4 | VIKING_MT4_Bridge.mq4 |

Both bridges can run simultaneously without interference.
