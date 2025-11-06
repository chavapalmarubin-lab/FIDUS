import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def test():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client['fidus_production']
    
    # Simulate the fixed endpoint logic
    all_investments = await db.investments.find({}).to_list(None)
    
    print("Testing Fund Portfolio Fix:")
    print()
    
    for fund_type in ['CORE', 'BALANCE']:
        fund_investments = [inv for inv in all_investments if inv.get('fund_type') == fund_type]
        fund_aum = sum(float(inv.get('principal_amount', 0)) for inv in fund_investments)
        total_investors = len(set(inv.get('client_id') for inv in fund_investments))
        
        print(f"{fund_type} Fund:")
        print(f"  Investments found: {len(fund_investments)}")
        print(f"  Total AUM: ${fund_aum:,.2f}")
        print(f"  Total Investors: {total_investors}")
        print()
    
    total_aum = sum(float(inv.get('principal_amount', 0)) for inv in all_investments)
    print(f"TOTAL AUM: ${total_aum:,.2f}")
    
    if abs(total_aum - 118151.41) < 1:
        print("✅ CORRECT!")
    else:
        print(f"❌ WRONG - Expected $118,151.41")
    
    client.close()

asyncio.run(test())
