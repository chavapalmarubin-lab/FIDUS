import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def update():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client['fidus_production']
    
    # Update accounts without profit_withdrawals field
    accounts_to_update = [891215, 891234, 897590, 897589, 897591, 897599]
    
    for account_num in accounts_to_update:
        result = await db.mt5_accounts.update_one(
            {"account": account_num},
            {"$set": {"profit_withdrawals": 0}}
        )
        print(f"Updated account {account_num}: {result.modified_count} modified")
    
    client.close()

asyncio.run(update())
