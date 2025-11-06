import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def check():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client['fidus_production']
    
    balance_invs = await db.investments.find({"fund_type": "BALANCE"}).to_list(None)
    
    print("BALANCE Investments:")
    for inv in balance_invs:
        print(f"\n  Investment ID: {inv.get('_id')}")
        print(f"  Client ID: {inv.get('client_id')}")
        print(f"  Principal Amount: {inv.get('principal_amount')}")
        print(f"  Product: {inv.get('product')}")
        print(f"  Status: {inv.get('status')}")
    
    # Check what we set earlier
    correct_inv = await db.investments.find_one({"client_id": "client_alejandro", "fund_type": "BALANCE"})
    if correct_inv:
        print("\n✅ Found correct investment with client_id='client_alejandro':")
        print(f"  Amount: ${float(correct_inv.get('amount', 0)):,.2f}")
        print(f"  Principal: ${float(correct_inv.get('principal_amount', 0) if correct_inv.get('principal_amount') else 0):,.2f}")
    
    client.close()

asyncio.run(check())
