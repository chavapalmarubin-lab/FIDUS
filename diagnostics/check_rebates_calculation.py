"""
Diagnostic script to check broker rebates calculation
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime

async def check_rebates():
    # Connect to MongoDB
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    print("=" * 70)
    print("BROKER REBATES DIAGNOSTIC")
    print("=" * 70)
    print()
    
    # Check mt5_deals_history collection
    deals_count = await db.mt5_deals_history.count_documents({})
    print(f"Total deals in database: {deals_count}")
    
    if deals_count > 0:
        # Calculate total volume
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_volume": {"$sum": "$volume"},
                    "deal_count": {"$sum": 1}
                }
            }
        ]
        
        result = await db.mt5_deals_history.aggregate(pipeline).to_list(length=1)
        
        if result:
            total_volume = result[0]["total_volume"]
            deal_count = result[0]["deal_count"]
            rebate_rate = 5.05
            total_rebates = total_volume * rebate_rate
            
            print(f"Total volume traded: {total_volume:.2f} lots")
            print(f"Rebate rate: ${rebate_rate} per lot")
            print(f"Total rebates earned: ${total_rebates:.2f}")
            print()
            
            # Show by account
            by_account_pipeline = [
                {
                    "$group": {
                        "_id": "$account_number",
                        "volume": {"$sum": "$volume"},
                        "deals": {"$sum": 1}
                    }
                },
                {"$sort": {"volume": -1}}
            ]
            
            by_account = await db.mt5_deals_history.aggregate(by_account_pipeline).to_list(length=None)
            
            print("Rebates by Account:")
            print("-" * 70)
            for item in by_account:
                account = item["_id"]
                volume = item["volume"]
                rebates = volume * rebate_rate
                deals = item["deals"]
                print(f"  Account {account}: {volume:.2f} lots ({deals} deals) = ${rebates:.2f}")
            print()
            
            # Show sample deals
            print("Sample deals (first 5):")
            print("-" * 70)
            sample_deals = await db.mt5_deals_history.find({}).limit(5).to_list(length=5)
            for deal in sample_deals:
                print(f"  Ticket: {deal.get('ticket')} | Account: {deal.get('account_number')} | Volume: {deal.get('volume')} | Symbol: {deal.get('symbol')}")
            
        else:
            print("ERROR: Could not aggregate volume data")
    else:
        print("WARNING: No deals found in mt5_deals_history collection!")
        print()
        print("This means:")
        print("- The VPS sync service hasn't synced trading history yet")
        print("- Or the collection name is different")
        print()
        print("Checking other collections...")
        collections = await db.list_collection_names()
        mt5_collections = [c for c in collections if 'mt5' in c.lower() or 'deal' in c.lower() or 'trade' in c.lower()]
        print(f"MT5-related collections: {mt5_collections}")
    
    print()
    print("=" * 70)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_rebates())
