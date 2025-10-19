#!/bin/bash
# Verification script to confirm all MT5 Bridge fixes are in place

echo "=========================================="
echo "MT5 BRIDGE FIX VERIFICATION"
echo "=========================================="
echo ""

# Check 1: UTF-8 encoding declaration
echo "✓ Check 1: UTF-8 encoding declaration"
if head -1 /app/vps/mt5_bridge_api_service.py | grep -q "# -*- coding: utf-8 -*-"; then
    echo "  PASS: UTF-8 encoding declared at line 1"
else
    echo "  FAIL: UTF-8 encoding not found"
    exit 1
fi
echo ""

# Check 2: UTF-8 reconfiguration code
echo "✓ Check 2: UTF-8 reconfiguration for Windows"
if grep -q "sys.stdout.reconfigure(encoding='utf-8')" /app/vps/mt5_bridge_api_service.py; then
    echo "  PASS: UTF-8 reconfiguration code present"
else
    echo "  FAIL: UTF-8 reconfiguration not found"
    exit 1
fi
echo ""

# Check 3: No emoji characters
echo "✓ Check 3: No emoji characters in service file"
if grep -qE "✅|❌|🚀|📊|🔍|⚠️|💾|✓" /app/vps/mt5_bridge_api_service.py; then
    echo "  FAIL: Emoji characters still present"
    exit 1
else
    echo "  PASS: No emoji characters found"
fi
echo ""

# Check 4: MongoDB truth value check fixed
echo "✓ Check 4: MongoDB connection check"
if grep -q "if db is not None:" /app/vps/mt5_bridge_api_service.py; then
    echo "  PASS: MongoDB check uses 'if db is not None'"
else
    echo "  FAIL: MongoDB check not fixed"
    exit 1
fi
echo ""

# Check 5: Emergency deployment workflow exists
echo "✓ Check 5: Emergency deployment workflow"
if [ -f /app/.github/workflows/deploy-mt5-bridge-emergency.yml ]; then
    echo "  PASS: Emergency deployment workflow created"
else
    echo "  FAIL: Workflow file not found"
    exit 1
fi
echo ""

# Check 6: Service start script exists
echo "✓ Check 6: Service startup script"
if [ -f /app/vps/start_service.bat ]; then
    echo "  PASS: Start service batch file created"
else
    echo "  FAIL: Start script not found"
    exit 1
fi
echo ""

# Check 7: All changes committed
echo "✓ Check 7: Git status"
cd /app
if [ -z "$(git status --porcelain)" ]; then
    echo "  PASS: All changes committed"
else
    echo "  WARNING: Uncommitted changes exist"
    git status --short
fi
echo ""

echo "=========================================="
echo "VERIFICATION COMPLETE"
echo "=========================================="
echo ""
echo "✅ All critical fixes are in place"
echo "✅ Emergency deployment workflow ready"
echo "✅ Service startup script created"
echo ""
echo "READY FOR DEPLOYMENT"
echo ""
echo "Next step: User must click 'Save to GitHub' to push changes"
echo "Then either workflow will auto-trigger or can be manually triggered at:"
echo "https://github.com/chavapalmarubin-lab/FIDUS/actions"
echo ""
