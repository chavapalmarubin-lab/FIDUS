"""
Comprehensive verification before GitHub save
Tests MongoDB data integrity and calculations
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from services.three_tier_pnl_calculator import ThreeTierPnLCalculator
from services.trading_analytics_service import TradingAnalyticsService
import os
from dotenv import load_dotenv

load_dotenv()

def to_float(val):
    if hasattr(val, 'to_decimal'):
        return float(val.to_decimal())
    return float(val) if val else 0.0

async def verify_all():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client['fidus_production']
    
    print("="*80)
    print("COMPREHENSIVE VERIFICATION - MONGODB & CALCULATIONS")
    print("="*80)
    print()
    
    # TEST 1: Verify MongoDB capital_source tags
    print("TEST 1: MongoDB Capital Source Tags")
    print("-"*80)
    
    accounts = await db.mt5_accounts.find({}).sort('account', 1).to_list(None)
    
    expected_tags = {
        885822: 'client',
        886066: 'client',
        886557: 'client',
        886602: 'client',
        891234: 'client',
        886528: 'intermediary',
        891215: 'fidus',
        897589: 'reinvested_profit',
        897590: 'reinvested_profit',
        897591: 'separation',
        897599: 'separation',
    }
    
    tags_correct = 0
    tags_wrong = 0
    
    for acc in accounts:
        acc_num = acc.get('account')
        capital_source = acc.get('capital_source')
        expected = expected_tags.get(acc_num, 'unknown')
        
        if capital_source == expected:
            print(f"  ✅ Account {acc_num}: {capital_source}")
            tags_correct += 1
        else:
            print(f"  ❌ Account {acc_num}: {capital_source} (expected: {expected})")
            tags_wrong += 1
    
    print(f"\nCapital Source Tags: {tags_correct}/11 correct")
    
    # TEST 2: Verify initial_allocation values
    print("\nTEST 2: Initial Allocation Values")
    print("-"*80)
    
    expected_allocations = {
        885822: 18151.41,
        886066: 10000.00,
        886557: 80000.00,
        886602: 10000.00,
        891234: 0.00,
        886528: 0.00,
        891215: 14662.94,
        897589: 0.00,
        897590: 0.00,
        897591: 0.00,
        897599: 0.00,
    }
    
    alloc_correct = 0
    alloc_wrong = 0
    
    for acc in accounts:
        acc_num = acc.get('account')
        initial = to_float(acc.get('initial_allocation', 0))
        expected = expected_allocations.get(acc_num, 0)
        
        if abs(initial - expected) < 0.01:
            print(f"  ✅ Account {acc_num}: ${initial:,.2f}")
            alloc_correct += 1
        else:
            print(f"  ❌ Account {acc_num}: ${initial:,.2f} (expected: ${expected:,.2f})")
            alloc_wrong += 1
    
    print(f"\nAllocations: {alloc_correct}/11 correct")
    
    # TEST 3: Verify profit_withdrawals field exists
    print("\nTEST 3: Profit Withdrawals Field")
    print("-"*80)
    
    pw_exists = 0
    pw_missing = 0
    
    for acc in accounts:
        acc_num = acc.get('account')
        pw = acc.get('profit_withdrawals')
        
        if pw is not None:
            print(f"  ✅ Account {acc_num}: ${to_float(pw):,.2f}")
            pw_exists += 1
        else:
            print(f"  ❌ Account {acc_num}: MISSING")
            pw_missing += 1
    
    print(f"\nProfit Withdrawals: {pw_exists}/11 have field")
    
    # TEST 4: Three-Tier P&L Calculator
    print("\nTEST 4: Three-Tier P&L Calculator")
    print("-"*80)
    
    pnl_calc = ThreeTierPnLCalculator(db)
    admin_view = await pnl_calc.get_admin_view()
    
    print(f"  Client Investment: ${admin_view['client_pnl']['initial_allocation']:,.2f}")
    print(f"  Client P&L: ${admin_view['client_pnl']['true_pnl']:,.2f} ({admin_view['client_pnl']['return_percent']}%)")
    print(f"  FIDUS Investment: ${admin_view['fidus_pnl']['initial_allocation']:,.2f}")
    print(f"  FIDUS P&L: ${admin_view['fidus_pnl']['true_pnl']:,.2f} ({admin_view['fidus_pnl']['return_percent']}%)")
    print(f"  Total Fund P&L: ${admin_view['total_fund_pnl']['true_pnl']:,.2f} ({admin_view['total_fund_pnl']['return_percent']}%)")
    
    # Verify critical numbers
    client_inv_ok = abs(admin_view['client_pnl']['initial_allocation'] - 118151.41) < 1
    fidus_inv_ok = abs(admin_view['fidus_pnl']['initial_allocation'] - 14662.94) < 1
    total_inv_ok = abs(admin_view['total_fund_pnl']['initial_allocation'] - 132814.35) < 1
    
    print(f"\n  Client Investment Match: {'✅' if client_inv_ok else '❌'}")
    print(f"  FIDUS Investment Match: {'✅' if fidus_inv_ok else '❌'}")
    print(f"  Total Investment Match: {'✅' if total_inv_ok else '❌'}")
    
    # TEST 5: Trading Analytics Service
    print("\nTEST 5: Trading Analytics Service")
    print("-"*80)
    
    analytics = TradingAnalyticsService(db)
    
    balance_fund = await analytics.get_fund_analytics("BALANCE", 30)
    core_fund = await analytics.get_fund_analytics("CORE", 30)
    
    print(f"  BALANCE Fund:")
    print(f"    AUM: ${balance_fund['aum']:,.2f}")
    print(f"    Managers: {len(balance_fund['managers'])}")
    for mgr in balance_fund['managers']:
        print(f"      Account {mgr['account']}: ${mgr['initial_allocation']:,.2f} allocation")
    
    print(f"\n  CORE Fund:")
    print(f"    AUM: ${core_fund['aum']:,.2f}")
    print(f"    Managers: {len(core_fund['managers'])}")
    for mgr in core_fund['managers']:
        print(f"      Account {mgr['account']}: ${mgr['initial_allocation']:,.2f} allocation")
    
    # Verify BALANCE has 3 client accounts including 886066
    balance_accounts = [m['account'] for m in balance_fund['managers']]
    has_886066 = 886066 in balance_accounts
    has_886557 = 886557 in balance_accounts
    has_886602 = 886602 in balance_accounts
    
    print(f"\n  BALANCE has 886066: {'✅' if has_886066 else '❌'}")
    print(f"  BALANCE has 886557: {'✅' if has_886557 else '❌'}")
    print(f"  BALANCE has 886602: {'✅' if has_886602 else '❌'}")
    
    # SUMMARY
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    total_tests = 8
    passed_tests = 0
    
    if tags_wrong == 0: passed_tests += 1
    if alloc_wrong == 0: passed_tests += 1
    if pw_missing == 0: passed_tests += 1
    if client_inv_ok: passed_tests += 1
    if fidus_inv_ok: passed_tests += 1
    if total_inv_ok: passed_tests += 1
    if has_886066 and has_886557 and has_886602: passed_tests += 1
    if balance_fund['aum'] == 100000 and core_fund['aum'] == 18151.41: passed_tests += 1
    
    print(f"\n✅ Tests Passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED - READY FOR GITHUB SAVE!")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} tests failed - review issues above")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(verify_all())
