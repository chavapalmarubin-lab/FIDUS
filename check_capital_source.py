import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

async def check():
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    # Get the accounts we need
    account_numbers = [886557, 886602, 891215, 897589, 885822, 897590]
    
    for acc_num in account_numbers:
        acc = await db.mt5_accounts.find_one({'account': acc_num})
        if acc:
            print(f"Account {acc_num}:")
            print(f"  capital_source: {acc.get('capital_source', 'NOT SET')}")
            print(f"  fund_type: {acc.get('fund_type', 'NOT SET')}")
            print(f"  equity: ${acc.get('equity', 0):,.2f}")
            print(f"  initial_allocation: ${acc.get('initial_allocation', 0):,.2f}")
            print()
    
    client.close()

asyncio.run(check())
