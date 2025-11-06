import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def check():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client['fidus_production']
    
    inv = await db.investments.find_one({})
    print("Investment document fields:")
    for key in inv.keys():
        print(f"  {key}: {inv[key]}")
    
    client.close()

asyncio.run(check())
