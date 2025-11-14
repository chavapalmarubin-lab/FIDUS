"""
Verification script to check if MT5 Bridge magic fix is deployed
"""
import httpx
import time
import json
from datetime import datetime

VPS_BRIDGE_URL = "http://92.118.45.135:8000"

print("="*80)
print("MT5 BRIDGE MAGIC FIX VERIFICATION")
print("="*80)
print(f"VPS Bridge URL: {VPS_BRIDGE_URL}")
print(f"Check Time: {datetime.now().isoformat()}")
print()

def check_health():
    """Check if bridge is healthy"""
    try:
        response = httpx.get(f"{VPS_BRIDGE_URL}/api/mt5/bridge/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ HEALTH CHECK: Bridge is responding")
            print(f"   Version: {data.get('version', 'unknown')}")
            print(f"   MT5 Initialized: {data.get('mt5', {}).get('initialized', False)}")
            print(f"   Accounts Cached: {data.get('cache', {}).get('accounts_cached', 0)}/7")
            return True
        else:
            print(f"⚠️  HEALTH CHECK: Returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ HEALTH CHECK: Error - {str(e)}")
        return False

def check_magic_field():
    """Check if trades include magic field"""
    accounts_to_test = [886557, 886066, 886602, 885822]
    magic_found = False
    
    print()
    print("CHECKING TRADES FOR MAGIC FIELD:")
    print("-"*80)
    
    for account in accounts_to_test:
        try:
            response = httpx.get(
                f"{VPS_BRIDGE_URL}/api/mt5/account/{account}/trades",
                params={"limit": 1},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("trades"):
                    trade = data["trades"][0]
                    has_magic = "magic" in trade
                    magic_value = trade.get("magic", "MISSING")
                    
                    if has_magic:
                        print(f"✅ Account {account}: magic = {magic_value}")
                        magic_found = True
                    else:
                        print(f"❌ Account {account}: magic field MISSING")
                else:
                    print(f"⚠️  Account {account}: No trades returned")
            else:
                print(f"⚠️  Account {account}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Account {account}: Error - {str(e)}")
    
    return magic_found

# Run checks
print("1. HEALTH CHECK:")
print("-"*80)
if not check_health():
    print("\n❌ Bridge is not responding. Deployment may not be complete.")
    print("   Wait 2-3 minutes and run this script again.")
    exit(1)

# Check for magic field
print()
print("2. MAGIC FIELD CHECK:")
magic_working = check_magic_field()

print()
print("="*80)
print("SUMMARY:")
print("="*80)

if magic_working:
    print("✅ SUCCESS: MT5 Bridge magic fix is DEPLOYED and WORKING!")
    print()
    print("Next steps:")
    print("  1. Wait 5-10 minutes for new trades to sync to MongoDB")
    print("  2. Trigger full re-sync of historical trades:")
    print("     curl -X POST https://advisor-dash-1.preview.emergentagent.com/api/admin/mt5-deals/sync-all")
    print("  3. Verify Money Managers Compare tab shows 4 managers")
else:
    print("❌ ISSUE: Magic field still missing from trades")
    print()
    print("Possible reasons:")
    print("  1. Deployment is still in progress (wait 2-3 minutes)")
    print("  2. Deployment failed (check GitHub Actions logs)")
    print("  3. Service needs manual restart on VPS")
    print()
    print("To check GitHub Actions:")
    print("  https://github.com/chavapalmarubin-lab/FIDUS/actions")

print("="*80)
