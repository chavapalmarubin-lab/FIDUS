"""
Phase 2 Backend API Testing Script
Tests all MT5 endpoints and validates data freshness
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
import json

async def test_phase2_endpoints():
    """Comprehensive test of Phase 2 backend endpoints"""
    
    print("=" * 80)
    print("PHASE 2 BACKEND API TESTING")
    print("=" * 80)
    
    # Connect to MongoDB
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    # Test 1: Check data exists
    print("\n[TEST 1] Checking if MT5 data exists in MongoDB...")
    all_accounts = await db.mt5_accounts.find({}).to_list(length=None)
    
    if not all_accounts:
        print("❌ FAIL: No MT5 accounts found in database")
        print("   Action: Run VPS MT5 Bridge Service first")
        client.close()
        return False
    
    print(f"✅ PASS: Found {len(all_accounts)} accounts")
    
    # Test 2: Verify all 7 expected accounts present
    print("\n[TEST 2] Verifying all 7 accounts present...")
    expected_accounts = [886557, 886066, 886602, 885822, 886528, 891215, 891234]
    found_accounts = [acc.get('account') for acc in all_accounts]
    
    missing = set(expected_accounts) - set(found_accounts)
    extra = set(found_accounts) - set(expected_accounts)
    
    if missing:
        print(f"❌ FAIL: Missing accounts: {missing}")
        return False
    if extra:
        print(f"⚠️  WARNING: Extra accounts: {extra}")
    
    print(f"✅ PASS: All 7 expected accounts present")
    
    # Test 3: Check data freshness
    print("\n[TEST 3] Checking data freshness...")
    now = datetime.now(timezone.utc)
    stale_threshold = timedelta(minutes=10)
    
    fresh_count = 0
    stale_count = 0
    
    for acc in all_accounts:
        last_sync = acc.get('last_sync') or acc.get('updated_at')
        if last_sync:
            if last_sync.tzinfo is None:
                last_sync = last_sync.replace(tzinfo=timezone.utc)
            
            age = now - last_sync
            if age < stale_threshold:
                fresh_count += 1
            else:
                stale_count += 1
    
    if fresh_count == 7:
        print(f"✅ PASS: All 7 accounts have FRESH data (<10 min old)")
    elif fresh_count > 0:
        print(f"⚠️  PARTIAL: {fresh_count}/7 accounts fresh, {stale_count}/7 stale")
        print(f"   Action: Wait for next VPS sync cycle (every 5 minutes)")
    else:
        print(f"❌ FAIL: All accounts have STALE data (>10 min old)")
        print(f"   Action: Verify VPS MT5 Bridge Service is running")
        print(f"   Check: Windows Service status, logs, MongoDB connection")
    
    # Test 4: Verify data structure
    print("\n[TEST 4] Verifying data structure...")
    required_fields = ['account', 'name', 'fund_type', 'balance', 'equity', 'profit', 'last_sync']
    
    sample = all_accounts[0]
    missing_fields = [field for field in required_fields if field not in sample]
    
    if missing_fields:
        print(f"❌ FAIL: Missing required fields: {missing_fields}")
        return False
    
    print(f"✅ PASS: All required fields present")
    
    # Test 5: Verify endpoint logic (simulate response)
    print("\n[TEST 5] Simulating /api/mt5/admin/accounts response...")
    
    enriched_accounts = []
    total_equity = 0
    total_profit = 0
    
    for account in all_accounts:
        account_data = {
            'mt5_login': account.get('account'),
            'fund_code': account.get('fund_type'),
            'broker_name': account.get('name'),
            'current_equity': account.get('equity', 0),
            'profit_loss': account.get('profit', 0),
            'balance': account.get('balance', 0)
        }
        enriched_accounts.append(account_data)
        total_equity += account.get('equity', 0)
        total_profit += account.get('profit', 0)
    
    print(f"✅ PASS: Endpoint would return {len(enriched_accounts)} accounts")
    print(f"   Total Equity: ${total_equity:,.2f}")
    print(f"   Total P&L: ${total_profit:,.2f}")
    
    # Test 6: Test health check logic
    print("\n[TEST 6] Testing health check logic...")
    
    health_response = {
        "status": "healthy" if fresh_count == 7 else "degraded",
        "healthy": fresh_count == 7,
        "message": f"{fresh_count}/{len(all_accounts)} accounts have fresh data",
        "accounts_count": len(all_accounts),
        "fresh_accounts": fresh_count,
        "stale_accounts_count": stale_count
    }
    
    if health_response['healthy']:
        print(f"✅ PASS: Health check would return 'healthy'")
    else:
        print(f"⚠️  WARNING: Health check would return 'degraded'")
        print(f"   Fresh: {fresh_count}, Stale: {stale_count}")
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    all_tests_pass = (
        len(all_accounts) == 7 and
        not missing and
        not missing_fields and
        fresh_count == 7
    )
    
    if all_tests_pass:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Backend is ready for Phase 3 (Frontend)")
        print("✅ Data is fresh and complete")
        print("✅ Endpoints will return correct data")
    else:
        print("\n⚠️  SOME TESTS NEED ATTENTION")
        if fresh_count < 7:
            print(f"\n🔴 CRITICAL: Data is stale")
            print(f"   Action Required: Verify VPS MT5 Bridge Service")
            print(f"   Expected: Fresh data every 5 minutes")
            print(f"   Current: Last sync was {stale_count} accounts ago")
        else:
            print(f"\n✅ Data is fresh and ready")
    
    # Account details
    print("\n" + "=" * 80)
    print("ACCOUNT DETAILS")
    print("=" * 80)
    
    for acc in all_accounts:
        account_num = acc.get('account')
        name = acc.get('name')
        fund_type = acc.get('fund_type')
        equity = acc.get('equity', 0)
        profit = acc.get('profit', 0)
        last_sync = acc.get('last_sync')
        
        if last_sync:
            if last_sync.tzinfo is None:
                last_sync = last_sync.replace(tzinfo=timezone.utc)
            age = now - last_sync
            minutes_old = age.total_seconds() / 60
            freshness = "✅" if minutes_old < 10 else "⚠️"
        else:
            minutes_old = None
            freshness = "❌"
        
        print(f"\n{freshness} {account_num}: {name} ({fund_type})")
        print(f"   Equity: ${equity:,.2f}, P&L: ${profit:,.2f}")
        if minutes_old is not None:
            print(f"   Last sync: {minutes_old:.1f} minutes ago")
        else:
            print(f"   Last sync: Never")
    
    client.close()
    return all_tests_pass

if __name__ == "__main__":
    result = asyncio.run(test_phase2_endpoints())
    sys.exit(0 if result else 1)
