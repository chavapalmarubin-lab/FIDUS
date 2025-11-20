#!/usr/bin/env python3
"""
MT4 File Monitor Status Checker
Run this script to check the current status of MT4 account 33200931
"""

import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json

# Load environment
load_dotenv('/app/backend/.env')
mongo_url = os.getenv('MONGO_URL')

if not mongo_url:
    print("❌ Error: MONGO_URL not found in environment")
    sys.exit(1)

try:
    client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("✅ MongoDB Connection: OK")
except Exception as e:
    print(f"❌ MongoDB Connection: FAILED - {e}")
    sys.exit(1)

db = client.get_database()

print("\n" + "=" * 80)
print("MT4 FILE MONITOR STATUS CHECK")
print("=" * 80)
print(f"Checking Account: 33200931 (Spain Equities CFD)")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# Get account data
account = db.mt5_accounts.find_one({"account": 33200931})

if not account:
    print("\n❌ CRITICAL: Account 33200931 NOT FOUND in database")
    print("\nThis account should exist. Something went wrong.")
    print("Run this to recreate it:")
    print('  python3 -c "from create_pending_accounts import create_mt4_account; create_mt4_account()"')
    sys.exit(1)

print("\n✅ Account Found in Database")
print("-" * 80)

# Check basic info
print(f"\n📋 ACCOUNT INFORMATION:")
print(f"   Manager: {account.get('manager_name', 'N/A')}")
print(f"   Platform: {account.get('platform', 'N/A')}")
print(f"   Broker: {account.get('broker', 'N/A')}")
print(f"   Server: {account.get('server', 'N/A')}")

# Check financial data
print(f"\n💰 FINANCIAL DATA:")
print(f"   Balance: ${account.get('balance', 0):,.2f}")
print(f"   Equity: ${account.get('equity', 0):,.2f}")
print(f"   Profit: ${account.get('profit', 0):,.2f}")
print(f"   Margin: ${account.get('margin', 0):,.2f}")
print(f"   Free Margin: ${account.get('free_margin', 0):,.2f}")

# Check integration status
print(f"\n🔌 INTEGRATION STATUS:")
status = account.get('status', 'unknown')
data_source = account.get('data_source', 'unknown')
synced = account.get('synced_from_vps', False)
connection_status = account.get('connection_status', 'unknown')

if status == 'active':
    print(f"   Status: ✅ {status}")
elif status == 'pending_real_time_data':
    print(f"   Status: ⏳ {status}")
else:
    print(f"   Status: ❌ {status}")

if data_source == 'MT4_FILE_MONITOR' or data_source == 'VPS_LIVE_MT4':
    print(f"   Data Source: ✅ {data_source}")
elif data_source == 'MANUAL_ENTRY':
    print(f"   Data Source: ⏳ {data_source} (waiting for file monitor)")
else:
    print(f"   Data Source: ❓ {data_source}")

print(f"   Synced from VPS: {'✅ Yes' if synced else '❌ No'}")
print(f"   Connection Status: {connection_status}")

# Check timestamps
print(f"\n⏰ TIMESTAMP INFORMATION:")
updated_at = account.get('updated_at')
last_sync = account.get('last_sync_timestamp')

if updated_at:
    try:
        if isinstance(updated_at, str):
            update_time = datetime.strptime(updated_at, '%Y-%m-%d %H:%M:%S.%f')
        else:
            update_time = updated_at
        
        time_since_update = datetime.now() - update_time
        print(f"   Last Update: {update_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Time Since: {time_since_update}")
        
        if time_since_update < timedelta(minutes=10):
            print(f"   Freshness: ✅ Recent (< 10 minutes)")
        elif time_since_update < timedelta(hours=1):
            print(f"   Freshness: ⚠️  Stale (< 1 hour)")
        else:
            print(f"   Freshness: ❌ Very Stale (> 1 hour)")
    except Exception as e:
        print(f"   Last Update: {updated_at} (could not parse)")
else:
    print(f"   Last Update: ❌ Never")

if last_sync:
    print(f"   Last Sync: {last_sync}")
else:
    print(f"   Last Sync: ❌ Never")

# Overall status
print("\n" + "=" * 80)
print("OVERALL STATUS:")
print("=" * 80)

issues = []
recommendations = []

if status != 'active':
    issues.append("Account status is not 'active'")
    recommendations.append("Wait for file monitor to upload data, then update status")

if data_source == 'MANUAL_ENTRY':
    issues.append("Data source is still MANUAL_ENTRY")
    recommendations.append("Deploy MT4 File Monitor service on VPS")
    recommendations.append("Ensure EA is running and writing account_data.json")

if not synced:
    issues.append("Account not synced from VPS")
    recommendations.append("Check if Python file monitor service is running")

if not last_sync:
    issues.append("No sync timestamp recorded")
    recommendations.append("Verify file monitor can connect to MongoDB")

if issues:
    print("\n⚠️  ISSUES FOUND:")
    for i, issue in enumerate(issues, 1):
        print(f"   {i}. {issue}")
    
    print("\n📋 RECOMMENDATIONS:")
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")
    
    print("\n📖 See detailed guide: /app/MT4_FILE_MONITOR_SETUP_GUIDE.md")
else:
    print("\n✅ ALL SYSTEMS OPERATIONAL")
    print("   MT4 File Monitor is working correctly!")
    print("   Real-time data is flowing to MongoDB.")

print("\n" + "=" * 80)

# Check if GitHub Action workflow exists
import os.path
workflow_path = '/app/.github/workflows/deploy-mt4-file-monitor.yml'
if os.path.exists(workflow_path):
    print("✅ GitHub Action workflow exists: deploy-mt4-file-monitor.yml")
else:
    print("❌ GitHub Action workflow NOT found")

# Check if Python service file exists
service_path = '/app/vps-scripts/mt4_file_monitor.py'
if os.path.exists(service_path):
    print("✅ Python service file exists: mt4_file_monitor.py")
else:
    print("❌ Python service file NOT found")

# Check if EA file exists
ea_path = '/app/vps-scripts/MT4_Python_Bridge_FileBased.mq4'
if os.path.exists(ea_path):
    print("✅ MT4 EA file exists: MT4_Python_Bridge_FileBased.mq4")
else:
    print("❌ MT4 EA file NOT found")

print("\n" + "=" * 80)
print("Next Steps:")
print("=" * 80)

if data_source == 'MANUAL_ENTRY':
    print("\n1. Deploy Python File Monitor to VPS")
    print("   Option A: Run GitHub Action 'Deploy MT4 File Monitor Service'")
    print("   Option B: Manually run setup on VPS (see guide)")
    print("\n2. Verify EA is running in MT4")
    print("   - Check MT4 Journal for 'Data written' messages")
    print("   - EA should write every 5 minutes (300 seconds)")
    print("\n3. Wait 5-10 minutes for first data upload")
    print("\n4. Run this script again to verify")
else:
    print("\n✅ Data is flowing! Verify in Investment Committee dashboard.")

client.close()
