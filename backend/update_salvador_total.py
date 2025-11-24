#!/usr/bin/env python3
"""
Update Salvador's total_sales_volume based on his actual referred investments
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from bson.decimal128 import Decimal128

MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://YOUR_MONGODB_URL_HERE")
DB_NAME = "fidus_production"

print("=" * 80)
print("🔧 UPDATING SALVADOR'S TOTAL SALES VOLUME")
print("=" * 80)

async def update_salvador():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        salvador_id = "6909e8eaaaf69606babea151"
        
        print(f"\n📋 Salvador ID: {salvador_id}")
        
        # Step 1: Find ALL investments referred by Salvador
        print(f"\n1️⃣ Finding investments referred by Salvador...")
        print("-" * 80)
        
        salvador_investments = await db.investments.find({
            "referred_by": salvador_id
        }).to_list(None)
        
        print(f"✅ Found {len(salvador_investments)} investments")
        
        total_principal = 0
        for inv in salvador_investments:
            principal = inv.get('principal_amount', 0)
            total_principal += principal
            fund_code = inv.get('fund_code', 'N/A')
            print(f"\n   Investment ID: {inv['_id']}")
            print(f"   Fund: {fund_code}")
            print(f"   Principal: ${principal:,.2f}")
            print(f"   Client ID: {inv.get('client_id')}")
        
        print(f"\n   📊 Total Principal: ${total_principal:,.2f}")
        
        # Step 2: Count unique clients
        unique_clients = set()
        for inv in salvador_investments:
            client_id = inv.get('client_id')
            if client_id:
                unique_clients.add(str(client_id))
        
        active_clients = len(unique_clients)
        print(f"   📊 Active Clients: {active_clients}")
        
        # Step 3: Update Salvador's record
        print(f"\n\n2️⃣ Updating Salvador's salespeople record...")
        print("-" * 80)
        
        result = await db.salespeople.update_one(
            {"_id": salvador_id},
            {
                "$set": {
                    "total_sales_volume": Decimal128(str(total_principal)),
                    "active_clients": active_clients
                }
            }
        )
        
        if result.modified_count > 0:
            print(f"   ✅ Updated Salvador's record")
        else:
            print(f"   ℹ️  Record already up to date")
        
        print(f"      Total Sales Volume: ${total_principal:,.2f}")
        print(f"      Active Clients: {active_clients}")
        
        # Step 4: Verify
        print(f"\n\n3️⃣ VERIFICATION")
        print("-" * 80)
        
        salvador = await db.salespeople.find_one({"_id": salvador_id})
        if salvador:
            sales_volume = salvador.get('total_sales_volume', 0)
            if hasattr(sales_volume, 'to_decimal'):
                sales_volume = float(sales_volume.to_decimal())
            
            print(f"\n✅ Salvador Palma:")
            print(f"   Email: {salvador.get('email')}")
            print(f"   Referral Code: {salvador.get('referral_code')}")
            print(f"   Total Sales Volume: ${sales_volume:,.2f}")
            print(f"   Active Clients: {salvador.get('active_clients', 0)}")
            print(f"   Status: {salvador.get('is_active', 'N/A')}")
        
        print("\n" + "=" * 80)
        print("✅ UPDATE COMPLETE!")
        print("=" * 80)
        print(f"\n📊 Summary:")
        print(f"   Total Sales Volume: ${total_principal:,.2f}")
        print(f"   Expected: $118,151.41")
        print(f"   Match: {'✅ YES' if abs(total_principal - 118151.41) < 1 else '❌ NO'}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(update_salvador())
