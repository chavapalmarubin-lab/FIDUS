import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def fix():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client['fidus_production']
    
    # Update BALANCE investment to have principal_amount
    result = await db.investments.update_one(
        {"client_id": "client_alejandro", "fund_type": "BALANCE"},
        {"$set": {"principal_amount": 100000.00}}
    )
    
    print(f"✅ Updated BALANCE investment: {result.modified_count} document(s)")
    
    # Verify
    inv = await db.investments.find_one({"client_id": "client_alejandro", "fund_type": "BALANCE"})
    print(f"   Principal amount now: ${float(inv.get('principal_amount', 0)):,.2f}")
    
    client.close()

asyncio.run(fix())
