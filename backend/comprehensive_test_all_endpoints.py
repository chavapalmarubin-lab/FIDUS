"""
Comprehensive test of ALL critical endpoints before claiming fix
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from services.trading_analytics_service import TradingAnalyticsService
from services.three_tier_pnl_calculator import ThreeTierPnLCalculator
import os
from dotenv import load_dotenv

load_dotenv()

async def test_all():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client['fidus_production']
    
    print("="*80)
    print("COMPREHENSIVE ENDPOINT TESTING")
    print("="*80)
    print()
    
    tests_passed = 0
    tests_failed = 0
    
    # TEST 1: Three-Tier P&L
    print("TEST 1: Three-Tier P&L Calculator")
    print("-"*80)
    try:
        calc = ThreeTierPnLCalculator(db)
        result = await calc.get_admin_view()
        
        client_inv = result['client_pnl']['initial_allocation']
        fidus_inv = result['fidus_pnl']['initial_allocation']
        
        if abs(client_inv - 118151.41) < 1 and abs(fidus_inv - 14662.94) < 1:
            print("✅ PASS: P&L calculator correct")
            tests_passed += 1
        else:
            print(f"❌ FAIL: Client={client_inv}, FIDUS={fidus_inv}")
            tests_failed += 1
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        tests_failed += 1
    print()
    
    # TEST 2: Trading Analytics Portfolio
    print("TEST 2: Trading Analytics Portfolio")
    print("-"*80)
    try:
        service = TradingAnalyticsService(db)
        portfolio = await service.get_portfolio_analytics(30)
        
        client_aum = portfolio.get('client_aum', 0)
        total_aum = portfolio.get('total_aum', 0)
        
        if abs(client_aum - 118151.41) < 1 and abs(total_aum - 132814.35) < 1:
            print(f"✅ PASS: Portfolio correct (Client: ${client_aum:,.2f}, Total: ${total_aum:,.2f})")
            tests_passed += 1
        else:
            print(f"❌ FAIL: Client AUM=${client_aum:,.2f}, Total AUM=${total_aum:,.2f}")
            tests_failed += 1
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        tests_failed += 1
    print()
    
    # TEST 3: Manager Rankings
    print("TEST 3: Manager Rankings")
    print("-"*80)
    try:
        service = TradingAnalyticsService(db)
        ranking = await service.get_managers_ranking(30)
        
        total_mgrs = ranking.get('total_managers', 0)
        
        if total_mgrs >= 4:
            print(f"✅ PASS: {total_mgrs} managers found")
            tests_passed += 1
        else:
            print(f"❌ FAIL: Only {total_mgrs} managers")
            tests_failed += 1
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        tests_failed += 1
    print()
    
    # TEST 4: Alejandro's Investments
    print("TEST 4: Alejandro's Investments")
    print("-"*80)
    try:
        investments = await db.investments.find({"client_id": "client_alejandro"}).to_list(None)
        total_inv = sum([float(inv.get('amount', 0)) for inv in investments])
        
        if abs(total_inv - 118151.41) < 1:
            print(f"✅ PASS: Alejandro has ${total_inv:,.2f} invested")
            tests_passed += 1
        else:
            print(f"❌ FAIL: Investment total=${total_inv:,.2f}")
            tests_failed += 1
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        tests_failed += 1
    print()
    
    # TEST 5: Alejandro's MT5 Accounts
    print("TEST 5: Alejandro's MT5 Accounts")
    print("-"*80)
    try:
        accounts = await db.mt5_accounts.find({
            "client_id": "client_alejandro",
            "capital_source": "client"
        }).to_list(None)
        
        if len(accounts) == 5:
            total_equity = sum([float(acc.get('equity', 0)) for acc in accounts])
            print(f"✅ PASS: 5 accounts with ${total_equity:,.2f} equity")
            tests_passed += 1
        else:
            print(f"❌ FAIL: Found {len(accounts)} accounts (expected 5)")
            tests_failed += 1
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        tests_failed += 1
    print()
    
    # TEST 6: User Login Data
    print("TEST 6: User Login Data")
    print("-"*80)
    try:
        user = await db.users.find_one({"username": "alejandro_mariscal"})
        
        if user and user.get('id') == 'client_alejandro':
            print(f"✅ PASS: User ID is 'client_alejandro'")
            tests_passed += 1
        else:
            print(f"❌ FAIL: User ID is '{user.get('id') if user else 'NOT FOUND'}'")
            tests_failed += 1
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        tests_failed += 1
    print()
    
    # SUMMARY
    print("="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Passed: {tests_passed}/6")
    print(f"Failed: {tests_failed}/6")
    print()
    
    if tests_failed == 0:
        print("🎉 ALL TESTS PASSED - SYSTEM IS WORKING!")
    else:
        print(f"⚠️  {tests_failed} TEST(S) FAILED - NEEDS FIXING")
    
    client.close()

asyncio.run(test_all())
