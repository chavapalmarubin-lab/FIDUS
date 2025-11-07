import asyncio
import sys
sys.path.append('/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
from services.trading_analytics_service import TradingAnalyticsService
import os
from dotenv import load_dotenv
import json

load_dotenv('/app/backend/.env')

async def test_api():
    """Test the money managers API endpoint logic"""
    
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    print("="*80)
    print("TESTING MONEY MANAGERS API")
    print("="*80)
    
    service = TradingAnalyticsService(db)
    
    try:
        # Call the same method the API uses
        ranking = await service.get_managers_ranking(period_days=30)
        
        print(f"\nTotal Managers: {ranking['total_managers']}")
        print(f"Total P&L: ${ranking['total_pnl']:,.2f}")
        print(f"Average Return: {ranking['average_return']:.2f}%")
        
        print(f"\n{'='*80}")
        print("MANAGER DETAILS:")
        print(f"{'='*80}")
        
        for i, mgr in enumerate(ranking['managers'], 1):
            print(f"\n{i}. {mgr['manager_name']}")
            print(f"   Manager ID: {mgr.get('manager_id', 'N/A')}")
            print(f"   Status: {mgr.get('status', 'N/A')}")
            print(f"   Fund Type: {mgr.get('fund_type', 'N/A')}")
            print(f"   Assigned Accounts: {mgr.get('assigned_accounts', [])}")
            print(f"   Initial Allocation: ${mgr.get('initial_allocation', 0):,.2f}")
            print(f"   Current Equity: ${mgr.get('current_equity', 0):,.2f}")
            print(f"   Total P&L: ${mgr.get('total_pnl', 0):,.2f}")
            print(f"   Return %: {mgr.get('return_percentage', 0):.2f}%")
            print(f"   Total Trades: {mgr.get('total_trades', 0)}")
        
        # Check if any manager has zero initial_allocation
        zero_allocation = [m for m in ranking['managers'] if m.get('initial_allocation', 0) == 0]
        if zero_allocation:
            print(f"\n{'='*80}")
            print(f"⚠️  WARNING: {len(zero_allocation)} managers have $0 initial allocation:")
            print(f"{'='*80}")
            for m in zero_allocation:
                print(f"  - {m['manager_name']}: Accounts {m.get('assigned_accounts', [])}")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    client.close()

if __name__ == "__main__":
    asyncio.run(test_api())
