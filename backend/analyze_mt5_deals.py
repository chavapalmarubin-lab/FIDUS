"""
MT5 Deal History Analysis Script
Purpose: Extract complete transaction history from mt5_deals_history
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from decimal import Decimal
import os
from dotenv import load_dotenv

load_dotenv()

async def analyze_mt5_deals():
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client['fidus_investment']
    
    print("=" * 80)
    print("PHASE 1: MT5 DEAL HISTORY ANALYSIS")
    print("=" * 80)
    print()
    
    # Step 1: Understand collection structure
    print("STEP 1: Collection Structure Analysis")
    print("-" * 80)
    
    sample_deal = await db.mt5_deals_history.find_one()
    if sample_deal:
        print("Sample Deal Document Fields:")
        for key, value in sample_deal.items():
            print(f"  {key}: {type(value).__name__} = {value}")
    print()
    
    # Get total count
    total_count = await db.mt5_deals_history.count_documents({})
    print(f"Total deals in collection: {total_count}")
    print()
    
    # Step 2: Get all unique deal types
    print("STEP 2: Deal Type Analysis")
    print("-" * 80)
    
    deal_types = await db.mt5_deals_history.distinct("type")
    print(f"Unique Deal Types: {deal_types}")
    print()
    
    # Count by type
    for deal_type in deal_types:
        count = await db.mt5_deals_history.count_documents({"type": deal_type})
        print(f"  {deal_type}: {count} deals")
    print()
    
    # Step 3: Priority Accounts Analysis
    print("STEP 3: Priority Accounts - Deal Summary")
    print("-" * 80)
    
    priority_accounts = [
        885822,  # CORE - $18k deposit
        886557,  # BALANCE - Part of $100k
        886602,  # BALANCE - Part of $100k
        891215,  # BALANCE - Part of $100k
        897589,  # BALANCE - The $5k problem
        886066,  # BALANCE - The $10k now $0
        891234,  # CORE
        897590,  # CORE
        897591,  # SEPARATION
        897599,  # SEPARATION
    ]
    
    for account_id in priority_accounts:
        deals = await db.mt5_deals_history.find(
            {"account_id": account_id}
        ).sort("time", 1).to_list(length=None)
        
        if deals:
            print(f"\n📊 ACCOUNT {account_id}:")
            print(f"   Total Deals: {len(deals)}")
            
            for deal in deals:
                deal_time = deal.get('time', 'N/A')
                deal_type = deal.get('type', 'N/A')
                profit = deal.get('profit', 0)
                comment = deal.get('comment', '')
                
                # Convert Decimal128 to float if needed
                if hasattr(profit, 'to_decimal'):
                    profit = float(profit.to_decimal())
                
                print(f"   - {deal_time} | Type: {deal_type:15} | Profit: ${profit:12,.2f} | Comment: {comment}")
        else:
            print(f"\n📊 ACCOUNT {account_id}: No deals found")
    
    print()
    print("=" * 80)
    print("Analysis Complete!")
    print("=" * 80)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(analyze_mt5_deals())
