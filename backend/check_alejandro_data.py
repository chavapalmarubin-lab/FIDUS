import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

async def check_data():
    """Check Alejandro's actual data in database"""
    
    mongo_url = os.getenv('MONGO_URL')
    print(f"MongoDB URL: {mongo_url[:50]}...")
    
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    # Find all Alejandro investments
    print("\n🔍 SEARCHING FOR ALEJANDRO'S INVESTMENTS...")
    investments = await db.investments.find({"client_name": {"$regex": "Alejandro", "$options": "i"}}).to_list(None)
    
    print(f"Found {len(investments)} investments")
    
    for inv in investments:
        print(f"\n📊 Investment:")
        print(f"  Fund Type: {inv.get('fund_type')}")
        print(f"  Principal: ${inv.get('principal_amount', 0):,.2f}")
        print(f"  Start Date: {inv.get('start_date')}")
        print(f"  First Payment: {inv.get('first_payment_date')}")
        print(f"  Interest Rate: {inv.get('interest_rate')}")
    
    # Also check with different field names
    print("\n🔍 CHECKING ALL INVESTMENTS...")
    all_investments = await db.investments.find({}).to_list(None)
    print(f"Total investments in database: {len(all_investments)}")
    
    for inv in all_investments:
        print(f"\n  Fund: {inv.get('fund_type')} - ${inv.get('principal_amount', 0)}")
        print(f"  Client: {inv.get('client_name', 'N/A')}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_data())
