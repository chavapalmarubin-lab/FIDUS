#!/usr/bin/env python3
"""
Investigate magic numbers in mt5_deals_history collection to understand manager-level data
"""
from pymongo import MongoClient
import os
import sys

def investigate_magic_numbers():
    """Investigate magic numbers in mt5_deals_history collection"""
    # Read MONGO_URL directly from .env file
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('MONGO_URL='):
                mongo_url = line.strip().split('=', 1)[1]
                break
    
    client = MongoClient(mongo_url)
    db = client.fidus_investment_management
    
    print("=" * 80)
    print("🔍 MAGIC NUMBER INVESTIGATION REPORT")
    print("=" * 80)
    
    # Check if collection exists
    collections = db.list_collection_names()
    print(f"\nAvailable collections: {collections}\n")
    
    # Count total deals
    total_count = db.mt5_deals_history.count_documents({})
    print(f"Total deals in mt5_deals_history: {total_count:,}\n")
    
    if total_count == 0:
        print("❌ No deals found in mt5_deals_history collection!")
        client.close()
        return
    
    # 1. Get deals grouped by magic number
    print("📊 AGGREGATING DEALS BY MAGIC NUMBER...\n")
    
    pipeline = [
        {
            '$group': {
                '_id': '$magic',
                'count': {'$sum': 1},
                'total_profit': {'$sum': '$profit'},
                'accounts': {'$addToSet': '$account'}
            }
        },
        {'$sort': {'count': -1}}
    ]
    
    magic_groups = list(db.mt5_deals_history.aggregate(pipeline))
    
    print(f"DEALS GROUPED BY MAGIC NUMBER:\n")
    
    total_deals = 0
    total_profit = 0
    
    for group in magic_groups:
        magic = group['_id']
        count = group['count']
        profit = group['total_profit']
        accounts = sorted(group['accounts'])
        
        total_deals += count
        total_profit += profit
        
        print(f"Magic #{magic}:")
        print(f"  - Trades: {count:,}")
        print(f"  - Total P&L: ${profit:,.2f}")
        print(f"  - Accounts: {accounts}")
        print()
    
    print("=" * 80)
    print(f"TOTAL DEALS: {total_deals:,}")
    print(f"TOTAL P&L: ${total_profit:,.2f}")
    print(f"Does total ≈ $10,000? {abs(total_profit - 10000) < 2000}")
    print("=" * 80)
    
    # 2. Check for BALANCE ADJUSTMENT deals
    print(f"\n🔍 CHECKING FOR BALANCE ADJUSTMENTS:\n")
    
    balance_adjustments = list(db.mt5_deals_history.find({
        'comment': {'$regex': 'BALANCE|DEPOSIT|WITHDRAWAL|ADJUSTMENT', '$options': 'i'}
    }).limit(10))
    
    if balance_adjustments:
        print(f"Found {len(balance_adjustments)} balance adjustment deals (showing first 10):\n")
        for deal in balance_adjustments:
            print(f"Deal ID: {deal.get('deal')}")
            print(f"  - Account: {deal.get('account')}")
            print(f"  - Magic: {deal.get('magic')}")
            print(f"  - Profit: ${deal.get('profit', 0):,.2f}")
            print(f"  - Comment: {deal.get('comment')}")
            print()
    else:
        print("No balance adjustment deals found.")
    
    # 3. Sample deals for each magic number
    print(f"\n📋 SAMPLE DEALS PER MAGIC NUMBER:\n")
    
    for group in magic_groups[:5]:  # First 5 magic numbers
        magic = group['_id']
        sample_deals = list(db.mt5_deals_history.find({'magic': magic}).limit(3))
        
        print(f"Magic #{magic} - Sample Deals:")
        for deal in sample_deals:
            print(f"  - Deal {deal.get('deal')}: {deal.get('symbol', 'N/A')} | "
                  f"Profit: ${deal.get('profit', 0):,.2f} | "
                  f"Comment: {deal.get('comment', 'N/A')}")
        print()
    
    # 4. Check deal types/actions
    print(f"\n🔍 CHECKING DEAL TYPES:\n")
    
    type_pipeline = [
        {
            '$group': {
                '_id': '$entry',
                'count': {'$sum': 1},
                'total_profit': {'$sum': '$profit'}
            }
        }
    ]
    
    deal_types = []
    async for doc in db.mt5_deals_history.aggregate(type_pipeline):
        deal_types.append(doc)
    
    for dtype in deal_types:
        print(f"Entry Type: {dtype['_id']}")
        print(f"  - Count: {dtype['count']:,}")
        print(f"  - Total Profit: ${dtype['total_profit']:,.2f}")
        print()
    
    await client.close()
    
    print("\n✅ INVESTIGATION COMPLETE!")

if __name__ == "__main__":
    asyncio.run(investigate_magic_numbers())
