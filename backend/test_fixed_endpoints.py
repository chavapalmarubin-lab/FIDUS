import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from services.trading_analytics_service import TradingAnalyticsService
import os
from dotenv import load_dotenv
import json

load_dotenv()

async def test():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client['fidus_production']
    
    service = TradingAnalyticsService(db)
    
    print("="*80)
    print("TESTING FIXED ENDPOINTS")
    print("="*80)
    print()
    
    # Test 1: Portfolio Analytics (was broken)
    print("TEST 1: Portfolio Analytics (Fixed balance_fund error)")
    print("-"*80)
    
    try:
        portfolio = await service.get_portfolio_analytics(30)
        print(f"✅ Portfolio Analytics working!")
        print(f"   Client AUM: ${portfolio['client_aum']:,.2f}")
        print(f"   Total AUM: ${portfolio['total_aum']:,.2f}")
        print(f"   Total Managers: {portfolio['total_managers']}")
        print(f"   Active Managers: {portfolio['active_managers']}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print()
    
    # Test 2: Managers Ranking (for Money Managers page)
    print("TEST 2: Managers Ranking (for Money Managers page)")
    print("-"*80)
    
    try:
        ranking = await service.get_managers_ranking(30)
        print(f"✅ Managers Ranking working!")
        print(f"   Total Managers: {ranking['total_managers']}")
        print(f"\n   Managers List:")
        for mgr in ranking['managers']:
            print(f"     {mgr['rank']}. {mgr['manager_name']}")
            print(f"        Account: {mgr['account']}")
            print(f"        Allocation: ${mgr['initial_allocation']:,.2f}")
            print(f"        P&L: ${mgr['total_pnl']:,.2f} ({mgr['return_percentage']:.2f}%)")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print()
    
    # Test 3: BALANCE Fund (should have 3 managers)
    print("TEST 3: BALANCE Fund Structure")
    print("-"*80)
    
    try:
        balance = await service.get_fund_analytics("BALANCE", 30)
        print(f"✅ BALANCE Fund working!")
        print(f"   AUM: ${balance['aum']:,.2f}")
        print(f"   Managers: {len(balance['managers'])}")
        for mgr in balance['managers']:
            print(f"     - Account {mgr['account']}: ${mgr['initial_allocation']:,.2f}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print()
    
    # Test 4: CORE Fund (should have 1 manager)
    print("TEST 4: CORE Fund Structure")
    print("-"*80)
    
    try:
        core = await service.get_fund_analytics("CORE", 30)
        print(f"✅ CORE Fund working!")
        print(f"   AUM: ${core['aum']:,.2f}")
        print(f"   Managers: {len(core['managers'])}")
        for mgr in core['managers']:
            print(f"     - Account {mgr['account']}: ${mgr['initial_allocation']:,.2f}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print()
    print("="*80)
    print("ALL TESTS COMPLETE")
    print("="*80)
    
    client.close()

asyncio.run(test())
