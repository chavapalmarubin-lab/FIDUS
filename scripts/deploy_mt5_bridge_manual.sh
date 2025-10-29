#!/bin/bash
#
# MANUAL DEPLOYMENT SCRIPT FOR MT5 BRIDGE COMPLETE
# Use this if GitHub Actions is not available
#
# Prerequisites:
# 1. SSH key file with access to VPS
# 2. VPS accessible at 92.118.45.135:22
#

set -e

VPS_HOST="92.118.45.135"
VPS_USER="Administrator"
SSH_KEY_PATH="${1:-~/.ssh/vps_key}"

echo "=========================================="
echo "🚀 MT5 BRIDGE COMPLETE - MANUAL DEPLOYMENT"
echo "=========================================="
echo "VPS: ${VPS_HOST}"
echo "SSH Key: ${SSH_KEY_PATH}"
echo ""

# Check if SSH key exists
if [ ! -f "${SSH_KEY_PATH}" ]; then
    echo "❌ ERROR: SSH key not found at ${SSH_KEY_PATH}"
    echo ""
    echo "Usage: $0 [path_to_ssh_key]"
    echo "Example: $0 ~/.ssh/vps_private_key"
    exit 1
fi

# Check if bridge script exists
if [ ! -f "/app/vps-scripts/mt5_bridge_complete.py" ]; then
    echo "❌ ERROR: Bridge script not found at /app/vps-scripts/mt5_bridge_complete.py"
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Test SSH connection
echo "🔌 Testing SSH connection..."
ssh -i "${SSH_KEY_PATH}" -o ConnectTimeout=10 -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_HOST} "echo 'SSH OK'" || {
    echo "❌ SSH connection failed"
    echo "Verify:"
    echo "  1. SSH key has correct permissions (chmod 600)"
    echo "  2. VPS is accessible"
    echo "  3. SSH key is authorized on VPS"
    exit 1
}
echo "✅ SSH connection successful"
echo ""

# Stop MT5 Bridge service
echo "⏹️  Stopping MT5 Bridge service..."
ssh -i "${SSH_KEY_PATH}" ${VPS_USER}@${VPS_HOST} "
    schtasks /End /TN MT5BridgeService 2>nul
    timeout /t 3 /nobreak >nul 2>&1
    taskkill /F /IM python.exe /FI \"WINDOWTITLE eq mt5*\" 2>nul
    exit 0
" || echo "Service stop attempted"
sleep 5
echo "✅ Service stopped"
echo ""

# Create backup
echo "📦 Creating backup of current script..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ssh -i "${SSH_KEY_PATH}" ${VPS_USER}@${VPS_HOST} "
    powershell -Command \"
        if (Test-Path 'C:\\mt5_bridge_service\\mt5_bridge_api_service.py') {
            Copy-Item 'C:\\mt5_bridge_service\\mt5_bridge_api_service.py' 'C:\\mt5_bridge_service\\mt5_bridge_api_service.py.backup.${TIMESTAMP}'
            Write-Host 'Backup created'
        }
    \"
" || echo "No existing file to backup"
echo "✅ Backup complete"
echo ""

# Deploy new bridge script
echo "📤 Uploading complete bridge script..."
scp -i "${SSH_KEY_PATH}" -o StrictHostKeyChecking=no /app/vps-scripts/mt5_bridge_complete.py ${VPS_USER}@${VPS_HOST}:C:/mt5_bridge_service/mt5_bridge_api_service.py || {
    echo "❌ File upload failed"
    exit 1
}
echo "✅ File uploaded"
echo ""

# Verify upload
echo "🔍 Verifying file on VPS..."
ssh -i "${SSH_KEY_PATH}" ${VPS_USER}@${VPS_HOST} "
    powershell -Command \"
        if (Test-Path 'C:\\mt5_bridge_service\\mt5_bridge_api_service.py') {
            Write-Host 'File exists:'
            (Get-Content 'C:\\mt5_bridge_service\\mt5_bridge_api_service.py' | Select-Object -First 5)
        } else {
            Write-Host 'ERROR: File not found'
            exit 1
        }
    \"
" || {
    echo "❌ File verification failed"
    exit 1
}
echo "✅ File verified"
echo ""

# Start service
echo "▶️  Starting MT5 Bridge service..."
ssh -i "${SSH_KEY_PATH}" ${VPS_USER}@${VPS_HOST} "schtasks /Run /TN MT5BridgeService"
sleep 15
echo "✅ Service start command issued"
echo ""

# Verify service is running
echo "🔍 Checking if service is running..."
ssh -i "${SSH_KEY_PATH}" ${VPS_USER}@${VPS_HOST} "
    powershell -Command \"
        Get-Process python -ErrorAction SilentlyContinue | Where-Object { \\\$_.CommandLine -like '*mt5_bridge*' } | Format-List Id, ProcessName
    \"
" || echo "⚠️  Could not verify process"
echo ""

# Wait for service to initialize
echo "⏳ Waiting for service to initialize..."
sleep 10
echo ""

# Test endpoints
echo "🧪 TESTING ENDPOINTS"
echo "=========================================="
echo ""

echo "1️⃣  Testing /api/mt5/bridge/health..."
HEALTH=$(curl -s -w "\n%{http_code}" http://${VPS_HOST}:8000/api/mt5/bridge/health)
HTTP_CODE=$(echo "$HEALTH" | tail -n1)
RESPONSE=$(echo "$HEALTH" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Health endpoint OK"
    echo "$RESPONSE" | python3 -m json.tool | grep -E "status|version|initialized"
else
    echo "❌ Health endpoint failed (HTTP $HTTP_CODE)"
fi
echo ""

echo "2️⃣  Testing /api/mt5/accounts/summary (NEW)..."
SUMMARY=$(curl -s -w "\n%{http_code}" http://${VPS_HOST}:8000/api/mt5/accounts/summary)
HTTP_CODE=$(echo "$SUMMARY" | tail -n1)
RESPONSE=$(echo "$SUMMARY" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Accounts summary endpoint OK"
    ACCOUNT_COUNT=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['count'])")
    echo "   Accounts returned: $ACCOUNT_COUNT"
else
    echo "❌ Accounts summary endpoint failed (HTTP $HTTP_CODE)"
    echo "   Response: $RESPONSE"
fi
echo ""

echo "3️⃣  Testing /api/mt5/account/886557/info..."
INFO=$(curl -s -w "\n%{http_code}" http://${VPS_HOST}:8000/api/mt5/account/886557/info)
HTTP_CODE=$(echo "$INFO" | tail -n1)
RESPONSE=$(echo "$INFO" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Account info endpoint OK"
    echo "$RESPONSE" | python3 -m json.tool | grep -E "account_id|name|balance"
else
    echo "❌ Account info endpoint failed (HTTP $HTTP_CODE)"
fi
echo ""

echo "4️⃣  Testing /api/mt5/account/886557/trades (NEW)..."
TRADES=$(curl -s -w "\n%{http_code}" "http://${VPS_HOST}:8000/api/mt5/account/886557/trades?limit=5")
HTTP_CODE=$(echo "$TRADES" | tail -n1)
RESPONSE=$(echo "$TRADES" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Account trades endpoint OK"
    TRADE_COUNT=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['count'])")
    echo "   Trades returned: $TRADE_COUNT"
else
    echo "❌ Account trades endpoint failed (HTTP $HTTP_CODE)"
    echo "   Response: $RESPONSE"
fi
echo ""

echo "=========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "Next Steps:"
echo "1. Verify backend sync succeeds"
echo "2. Check mt5_deals_history MongoDB collection"
echo "3. Test broker rebates calculation"
echo ""
echo "Logs available at:"
echo "  ssh ${VPS_USER}@${VPS_HOST} 'type C:\\mt5_bridge_service\\logs\\api_service.log'"
echo "=========================================="
