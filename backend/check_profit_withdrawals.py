import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def check():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client['fidus_production']
    
    accounts = await db.mt5_accounts.find({}).to_list(None)
    
    print("Checking profit_withdrawals field:")
    for acc in accounts:
        acc_num = acc.get('account')
        pw = acc.get('profit_withdrawals', 'NOT FOUND')
        print(f"  Account {acc_num}: {pw}")
    
    client.close()

asyncio.run(check())
