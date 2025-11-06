"""
Test the Fund Portfolio endpoint that's showing $0
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from services.trading_analytics_service import TradingAnalyticsService
import os
from dotenv import load_dotenv

load_dotenv()

async def test():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client['fidus_production']
    
    print("="*80)
    print("TESTING FUND PORTFOLIO ENDPOINT")
    print("="*80)
    print()
    
    # Test the service directly
    service = TradingAnalyticsService(db)
    
    try:
        portfolio = await service.get_portfolio_analytics(30)
        
        print("Portfolio Analytics Result:")
        print(f"  Client AUM: ${portfolio.get('client_aum', 0):,.2f}")
        print(f"  Total AUM: ${portfolio.get('total_aum', 0):,.2f}")
        print(f"  Client P&L: ${portfolio.get('client_pnl', 0):,.2f}")
        print(f"  Total P&L: ${portfolio.get('total_pnl', 0):,.2f}")
        print(f"  Total Managers: {portfolio.get('total_managers', 0)}")
        print(f"  Active Managers: {portfolio.get('active_managers', 0)}")
        
        if portfolio.get('client_aum', 0) == 0:
            print("\n❌ CLIENT AUM IS $0 - THIS IS THE PROBLEM!")
        else:
            print("\n✅ Client AUM is correct")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    client.close()

asyncio.run(test())
