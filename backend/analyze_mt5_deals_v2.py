"""
MT5 Deal History Analysis Script - CORRECTED DATABASE
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
    db = client['fidus_production']  # CORRECTED DATABASE NAME
    
    print("=" * 80)
    print("PHASE 1: MT5 DEAL HISTORY ANALYSIS")
    print("Connected to: fidus_production database")
    print("=" * 80)
    print()
    
    # Step 1: Understand collection structure
    print("STEP 1: Collection Structure Analysis")
    print("-" * 80)
    
    total_count = await db.mt5_deals_history.count_documents({})
    print(f"Total deals in collection: {total_count:,}")
    
    sample_deal = await db.mt5_deals_history.find_one()
    if sample_deal:
        print("\nSample Deal Document Fields:")
        for key, value in sample_deal.items():
            if hasattr(value, 'to_decimal'):
                value = float(value.to_decimal())
            value_str = str(value)[:80] if len(str(value)) > 80 else str(value)
            print(f"  {key}: {value_str}")
    print()
    
    # Step 2: Get all unique deal types & actions
    print("STEP 2: Deal Type & Action Analysis")
    print("-" * 80)
    
    deal_types = await db.mt5_deals_history.distinct("type")
    print(f"Unique Deal Types: {deal_types}")
    
    deal_actions = await db.mt5_deals_history.distinct("action")
    print(f"Unique Deal Actions: {deal_actions}")
    print()
    
    # Count by type
    print("Deal counts by Type:")
    for deal_type in deal_types:
        count = await db.mt5_deals_history.count_documents({"type": deal_type})
        print(f"  {deal_type}: {count:,} deals")
    print()
    
    # Count by action
    print("Deal counts by Action:")
    for action in deal_actions:
        count = await db.mt5_deals_history.count_documents({"action": action})
        print(f"  {action}: {count:,} deals")
    print()
    
    # Step 3: Priority Accounts Analysis
    print("STEP 3: Priority Accounts - Transaction History")
    print("=" * 80)
    
    priority_accounts = [
        (885822, "CORE - $18k deposit"),
        (886557, "BALANCE - Part of $100k"),
        (886602, "BALANCE - Part of $100k"),
        (891215, "BALANCE - Part of $100k"),
        (897589, "BALANCE - The $5k problem"),
        (886066, "BALANCE - The $10k now $0"),
        (891234, "CORE"),
        (897590, "CORE"),
        (897591, "SEPARATION"),
        (897599, "SEPARATION"),
    ]
    
    for account_id, description in priority_accounts:
        deals = await db.mt5_deals_history.find(
            {"account_id": account_id}
        ).sort("time", 1).to_list(length=None)
        
        print(f"\n{'=' * 80}")
        print(f"📊 ACCOUNT {account_id} - {description}")
        print(f"{'=' * 80}")
        
        if deals:
            print(f"Total Deals: {len(deals)}\n")
            
            running_balance = 0
            for idx, deal in enumerate(deals, 1):
                deal_time = deal.get('time', 'N/A')
                deal_type = deal.get('type', 'N/A')
                action = deal.get('action', 'N/A')
                profit = deal.get('profit', 0)
                volume = deal.get('volume', 0)
                comment = deal.get('comment', '')
                
                # Convert Decimal128 to float if needed
                if hasattr(profit, 'to_decimal'):
                    profit = float(profit.to_decimal())
                if hasattr(volume, 'to_decimal'):
                    volume = float(volume.to_decimal())
                
                running_balance += profit
                
                print(f"{idx:3}. {deal_time} | Type: {deal_type:10} | Action: {action:8} | ")
                print(f"     Profit: ${profit:12,.2f} | Volume: {volume:10,.2f} | Balance: ${running_balance:12,.2f}")
                print(f"     Comment: '{comment}'")
                print()
        else:
            print("❌ No deals found for this account")
    
    print()
    print("=" * 80)
    print("Initial Analysis Complete!")
    print("=" * 80)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(analyze_mt5_deals())
