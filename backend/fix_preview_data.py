#!/usr/bin/env python3
"""
Fix investments in PREVIEW database
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from bson.decimal128 import Decimal128

MONGO_URL = os.getenv("MONGO_URL")

async def fix_data():
    client = AsyncIOMotorClient(MONGO_URL)
    db_name = "fidus_production"
    db = client[db_name]
    
    print("\n" + "=" * 80)
    print("FIXING PREVIEW DATABASE")
    print("=" * 80)
    
    # IDs from our findings
    correct_client_id = "6909ed359244f3d04684ebc8"
    salvador_id = "6909ed359244f3d04684ebc7"
    
    # Step 1: Update investments with "client_alejandro" to correct client_id
    print("\n1️⃣ Updating investments with correct client_id...")
    result = await db.investments.update_many(
        {"client_id": "client_alejandro"},
        {
            "$set": {
                "client_id": correct_client_id,
                "referred_by": salvador_id,
                "referred_by_name": "Salvador Palma"
            }
        }
    )
    print(f"   ✅ Updated {result.modified_count} investments")
    
    # Step 2: Delete empty investments (principal_amount = 0)
    print("\n2️⃣ Deleting empty investments...")
    result = await db.investments.delete_many({
        "principal_amount": 0
    })
    print(f"   ✅ Deleted {result.deleted_count} empty investments")
    
    # Step 3: Calculate Salvador's totals
    print("\n3️⃣ Calculating Salvador's totals...")
    investments = await db.investments.find({
        "referred_by": salvador_id
    }).to_list(None)
    
    total_principal = sum(inv.get('principal_amount', 0) for inv in investments)
    print(f"   📊 Total from {len(investments)} investments: ${total_principal:,.2f}")
    
    # Step 4: Update Salvador's record
    print("\n4️⃣ Updating Salvador's record...")
    await db.salespeople.update_one(
        {"_id": salvador_id},
        {
            "$set": {
                "total_sales_volume": Decimal128(str(total_principal)),
                "active_clients": 1
            }
        }
    )
    print(f"   ✅ Updated Salvador's total_sales_volume to ${total_principal:,.2f}")
    
    # Verification
    print("\n5️⃣ VERIFICATION")
    print("-" * 80)
    
    salvador = await db.salespeople.find_one({"_id": salvador_id})
    sales_volume = salvador.get('total_sales_volume', 0)
    if hasattr(sales_volume, 'to_decimal'):
        sales_volume = float(sales_volume.to_decimal())
    
    print(f"✅ Salvador's total_sales_volume: ${sales_volume:,.2f}")
    
    investments_check = await db.investments.find({
        "referred_by": salvador_id
    }).to_list(None)
    
    print(f"✅ Investments linked to Salvador: {len(investments_check)}")
    for inv in investments_check:
        print(f"   - {inv.get('fund_code', 'N/A')}: ${inv.get('principal_amount', 0):,.2f}")
    
    print("\n" + "=" * 80)
    print("✅ FIX COMPLETE!")
    print("=" * 80)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_data())
