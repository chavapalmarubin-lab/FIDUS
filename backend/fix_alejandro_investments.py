"""
Fix Alejandro's Investments Collection
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def fix():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client['fidus_production']
    
    print("="*80)
    print("FIXING ALEJANDRO'S INVESTMENTS")
    print("="*80)
    print()
    
    # Delete old investments with wrong client_id
    print("Step 1: Cleaning old investments...")
    result = await db.investments.delete_many({
        "client_id": "6909e8ebaaf69606babea152"
    })
    print(f"  Deleted {result.deleted_count} old investments")
    print()
    
    # Create correct investments
    print("Step 2: Creating correct investments...")
    
    core_investment = {
        "investment_id": "inv_alejandro_core_001",
        "client_id": "client_alejandro",  # FIXED: Use string not ObjectId
        "fund_type": "CORE",
        "amount": 18151.41,  # FIXED: Correct amount
        "initial_amount": 18151.41,
        "status": "active",
        "start_date": "2025-09-30",
        "interest_rate": 0.015,  # 1.5% monthly
        "payment_frequency": "monthly"
    }
    
    balance_investment = {
        "investment_id": "inv_alejandro_balance_001",
        "client_id": "client_alejandro",  # FIXED: Use string not ObjectId
        "fund_type": "BALANCE",
        "amount": 100000.00,  # FIXED: Correct amount
        "initial_amount": 100000.00,
        "status": "active",
        "start_date": "2025-09-30",
        "interest_rate": 0.025,  # 2.5% monthly
        "payment_frequency": "quarterly"
    }
    
    await db.investments.insert_one(core_investment)
    print(f"  ✅ Created CORE investment: $18,151.41")
    
    await db.investments.insert_one(balance_investment)
    print(f"  ✅ Created BALANCE investment: $100,000.00")
    
    print()
    
    # Verify
    print("Step 3: Verifying...")
    investments = await db.investments.find({"client_id": "client_alejandro"}).to_list(None)
    
    total = sum([float(inv.get('amount', 0)) for inv in investments])
    print(f"  Found {len(investments)} investments")
    print(f"  Total: ${total:,.2f}")
    
    for inv in investments:
        print(f"    - {inv['fund_type']}: ${float(inv['amount']):,.2f}")
    
    if abs(total - 118151.41) < 1:
        print(f"\n  ✅ CORRECT! Total matches $118,151.41")
    else:
        print(f"\n  ❌ WRONG! Total should be $118,151.41")
    
    client.close()

asyncio.run(fix())
