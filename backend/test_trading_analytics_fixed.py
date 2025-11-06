import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from services.trading_analytics_service import TradingAnalyticsService
import os
import json
from dotenv import load_dotenv

load_dotenv()

async def test():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client['fidus_production']
    
    service = TradingAnalyticsService(db)
    
    print("="*80)
    print("TESTING FIXED TRADING ANALYTICS")
    print("="*80)
    print()
    
    # Test BALANCE fund
    print("BALANCE FUND:")
    balance_data = await service.get_fund_analytics("BALANCE", 30)
    print(f"  AUM: ${balance_data['aum']:,.2f}")
    print(f"  Total Equity: ${balance_data['total_equity']:,.2f}")
    print(f"  Total P&L: ${balance_data['total_pnl']:,.2f}")
    print(f"  Return: {balance_data['weighted_return']:.2f}%")
    print(f"\n  Managers:")
    for mgr in balance_data['managers']:
        print(f"    Account {mgr['account']}: Allocation ${mgr['initial_allocation']:,.2f}, P&L ${mgr['total_pnl']:,.2f}, Return {mgr['return_percentage']:.2f}%")
    
    print()
    
    # Test CORE fund
    print("CORE FUND:")
    core_data = await service.get_fund_analytics("CORE", 30)
    print(f"  AUM: ${core_data['aum']:,.2f}")
    print(f"  Total Equity: ${core_data['total_equity']:,.2f}")
    print(f"  Total P&L: ${core_data['total_pnl']:,.2f}")
    print(f"  Return: {core_data['weighted_return']:.2f}%")
    print(f"\n  Managers:")
    for mgr in core_data['managers']:
        print(f"    Account {mgr['account']}: Allocation ${mgr['initial_allocation']:,.2f}, P&L ${mgr['total_pnl']:,.2f}, Return {mgr['return_percentage']:.2f}%")
    
    print()
    print("="*80)
    print("VERIFICATION:")
    print("="*80)
    
    # Check if allocations match expected
    expected = {
        885822: 18151.41,
        886557: 80000.00,
        886602: 10000.00,
        886066: 10000.00,  # Should be in BALANCE but with $0 equity
        891215: 14662.94,
        897590: 0.00,
        897589: 0.00,
    }
    
    all_managers = balance_data['managers'] + core_data['managers']
    
    print("\nAllocation Verification:")
    for mgr in all_managers:
        acc = mgr['account']
        if acc in expected:
            exp_val = expected[acc]
            actual_val = mgr['initial_allocation']
            match = "✅" if abs(exp_val - actual_val) < 1 else "❌"
            print(f"  Account {acc}: Expected ${exp_val:,.2f}, Got ${actual_val:,.2f} {match}")
    
    client.close()

asyncio.run(test())
