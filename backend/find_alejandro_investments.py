#!/usr/bin/env python3
"""
Find Alejandro's investments in the database
Search broadly across all investments to locate the missing $118,151.41
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from decimal import Decimal

# Use production MongoDB
MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://chavapalmarubin_db_user:2170Tenoch!@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority")
DB_NAME = "fidus_production"

print("=" * 80)
print("🔍 SEARCHING FOR ALEJANDRO'S INVESTMENTS")
print("=" * 80)

async def find_investments():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # Known IDs from diagnostic
        alejandro_client_id = "6909e8ebaaf69606babea152"
        alejandro_user_id = "68e137f2272c6a55ec3edd7d"
        salvador_id = "6909e8eaaaf69606babea151"
        
        print(f"\n📋 Known IDs:")
        print(f"   Alejandro Client ID: {alejandro_client_id}")
        print(f"   Alejandro User ID: {alejandro_user_id}")
        print(f"   Salvador ID: {salvador_id}")
        
        # Strategy 1: Find all investments with amount ~$18,151 or ~$100,000
        print("\n\n1️⃣ Searching by AMOUNT (CORE $18,151 and BALANCE $100,000)...")
        print("-" * 80)
        
        # Search for CORE investment
        core_investments = await db.investments.find({
            "$or": [
                {"amount": {"$gte": 18000, "$lte": 18500}},
                {"amount": 18151.41},
            ]
        }).to_list(None)
        
        print(f"\n🔍 Found {len(core_investments)} investments matching CORE amount ($18,151):")
        for inv in core_investments:
            amount = inv.get('amount', 0)
            if hasattr(amount, 'to_decimal'):
                amount = float(amount.to_decimal())
            print(f"\n   ID: {inv['_id']}")
            print(f"   Amount: ${amount:,.2f}")
            print(f"   Fund: {inv.get('fund_type')}")
            print(f"   Status: {inv.get('status')}")
            print(f"   Client ID: {inv.get('client_id')}")
            print(f"   User ID: {inv.get('user_id')}")
            print(f"   Client Name: {inv.get('client_name')}")
            print(f"   Investor Name: {inv.get('investor_name')}")
            print(f"   Email: {inv.get('email')}")
            print(f"   Referred By: {inv.get('referred_by')}")
            print(f"   Referred By Name: {inv.get('referred_by_name')}")
        
        # Search for BALANCE investment
        balance_investments = await db.investments.find({
            "$or": [
                {"amount": {"$gte": 99000, "$lte": 101000}},
                {"amount": 100000},
            ]
        }).to_list(None)
        
        print(f"\n\n🔍 Found {len(balance_investments)} investments matching BALANCE amount ($100,000):")
        for inv in balance_investments:
            amount = inv.get('amount', 0)
            if hasattr(amount, 'to_decimal'):
                amount = float(amount.to_decimal())
            print(f"\n   ID: {inv['_id']}")
            print(f"   Amount: ${amount:,.2f}")
            print(f"   Fund: {inv.get('fund_type')}")
            print(f"   Status: {inv.get('status')}")
            print(f"   Client ID: {inv.get('client_id')}")
            print(f"   User ID: {inv.get('user_id')}")
            print(f"   Client Name: {inv.get('client_name')}")
            print(f"   Investor Name: {inv.get('investor_name')}")
            print(f"   Email: {inv.get('email')}")
            print(f"   Referred By: {inv.get('referred_by')}")
            print(f"   Referred By Name: {inv.get('referred_by_name')}")
        
        # Strategy 2: Check all investments fields to understand schema
        print("\n\n2️⃣ Analyzing Investment Schema...")
        print("-" * 80)
        sample_inv = await db.investments.find_one()
        if sample_inv:
            print("\n📝 Sample Investment Fields:")
            for key in sample_inv.keys():
                print(f"   - {key}: {type(sample_inv[key]).__name__}")
        
        # Strategy 3: Get total investment count
        total_count = await db.investments.count_documents({})
        print(f"\n\n📊 Total investments in database: {total_count}")
        
        # Strategy 4: Find investments created around the same time as Alejandro's client record
        print("\n\n3️⃣ Searching by Creation Time...")
        print("-" * 80)
        
        alejandro_client = await db.clients.find_one({"_id": alejandro_client_id})
        if alejandro_client and 'created_at' in alejandro_client:
            created_at = alejandro_client['created_at']
            print(f"\nAlejandro's client record created: {created_at}")
            
            # Find investments created within 1 day of client record
            from datetime import timedelta
            recent_investments = await db.investments.find({
                "created_at": {
                    "$gte": created_at - timedelta(days=1),
                    "$lte": created_at + timedelta(days=1)
                }
            }).to_list(None)
            
            print(f"\n🔍 Found {len(recent_investments)} investments created around same time:")
            for inv in recent_investments:
                amount = inv.get('amount', 0)
                if hasattr(amount, 'to_decimal'):
                    amount = float(amount.to_decimal())
                print(f"\n   ID: {inv['_id']}")
                print(f"   Amount: ${amount:,.2f}")
                print(f"   Fund: {inv.get('fund_type')}")
                print(f"   Client Name: {inv.get('client_name')}")
        
        print("\n" + "=" * 80)
        print("✅ SEARCH COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(find_investments())
