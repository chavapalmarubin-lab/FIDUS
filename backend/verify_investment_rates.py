import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

async def verify_and_update():
    """Verify investment interest rates are correct"""
    
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    print("📊 VERIFYING INVESTMENT INTEREST RATES:")
    print("="*60)
    
    # Check BALANCE investment
    balance_inv = await db.investments.find_one({"investment_id": "inv_alejandro_balance_001"})
    print(f"\nBALANCE Investment:")
    print(f"  Current interest_rate in DB: {balance_inv.get('interest_rate')}")
    print(f"  Correct rate: 0.025 (2.5% monthly)")
    
    if balance_inv.get('interest_rate') != 0.025:
        await db.investments.update_one(
            {"investment_id": "inv_alejandro_balance_001"},
            {"$set": {"interest_rate": 0.025}}
        )
        print(f"  ✅ Updated to 0.025")
    else:
        print(f"  ✅ Already correct")
    
    # Check CORE investment
    core_inv = await db.investments.find_one({"investment_id": "inv_alejandro_core_001"})
    print(f"\nCORE Investment:")
    print(f"  Current interest_rate in DB: {core_inv.get('interest_rate')}")
    print(f"  Correct rate: 0.015 (1.5% monthly)")
    
    if core_inv.get('interest_rate') != 0.015:
        await db.investments.update_one(
            {"investment_id": "inv_alejandro_core_001"},
            {"$set": {"interest_rate": 0.015}}
        )
        print(f"  ✅ Updated to 0.015")
    else:
        print(f"  ✅ Already correct")
    
    print("\n" + "="*60)
    print("CORRECT INTEREST CALCULATIONS:")
    print("="*60)
    print(f"\nCORE:")
    print(f"  Principal: $18,151.41")
    print(f"  Rate: 1.5% monthly")
    print(f"  Monthly Interest: $18,151.41 × 0.015 = $272.27")
    print(f"  Commission (10%): $27.23")
    
    print(f"\nBALANCE:")
    print(f"  Principal: $100,000")
    print(f"  Rate: 2.5% monthly")
    print(f"  Monthly Interest: $100,000 × 0.025 = $2,500")
    print(f"  Quarterly Interest: $2,500 × 3 = $7,500")
    print(f"  Commission (10%): $750")
    
    print(f"\nTOTAL COMMISSIONS:")
    print(f"  CORE: $27.23 × 12 = $326.73")
    print(f"  BALANCE: $750 × 4 = $3,000.00")
    print(f"  TOTAL: $3,326.73 ✅")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(verify_and_update())
