#!/usr/bin/env python3
"""
Fix the client_id mismatch
The investments use "client_alejandro" but should use the real client_id
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from bson.decimal128 import Decimal128

MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://chavapalmarubin_db_user:2170Tenoch!@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority")
DB_NAME = "fidus_production"

print("=" * 80)
print("🔧 FIXING CLIENT_ID MISMATCH")
print("=" * 80)

async def fix_client_id():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # The correct IDs
        correct_client_id = "6909e8ebaaf69606babea152"
        salvador_id = "6909e8eaaaf69606babea151"
        
        print(f"\n📋 Correct IDs:")
        print(f"   Alejandro's Real Client ID: {correct_client_id}")
        print(f"   Salvador's ID: {salvador_id}")
        
        # Step 1: Find investments with wrong client_id
        print(f"\n\n1️⃣ Finding investments with client_id='client_alejandro'...")
        print("-" * 80)
        
        wrong_investments = await db.investments.find({
            "client_id": "client_alejandro"
        }).to_list(None)
        
        print(f"✅ Found {len(wrong_investments)} investments with wrong client_id")
        
        total_principal = 0
        for inv in wrong_investments:
            principal = inv.get('principal_amount', 0)
            total_principal += principal
            print(f"\n   Investment ID: {inv['_id']}")
            print(f"   Principal: ${principal:,.2f}")
            print(f"   Fund Code: {inv.get('fund_code')}")
            print(f"   Current Client ID: {inv.get('client_id')} ❌")
        
        print(f"\n   📊 Total Principal: ${total_principal:,.2f}")
        
        # Step 2: Update these investments
        print(f"\n\n2️⃣ Updating investments to correct client_id...")
        print("-" * 80)
        
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
        print(f"      Changed client_id: 'client_alejandro' → '{correct_client_id}'")
        print(f"      Set referred_by: {salvador_id}")
        print(f"      Set referred_by_name: Salvador Palma")
        
        # Step 3: Delete the empty investment (ID: 6909e8ebaaf69606babea153)
        print(f"\n\n3️⃣ Removing empty investment...")
        print("-" * 80)
        
        empty_inv_id = "6909e8ebaaf69606babea153"
        delete_result = await db.investments.delete_one({"_id": empty_inv_id})
        
        if delete_result.deleted_count > 0:
            print(f"   ✅ Deleted empty investment {empty_inv_id}")
        else:
            print(f"   ℹ️  Empty investment not found or already deleted")
        
        # Step 4: Update Salvador's total_sales_volume
        print(f"\n\n4️⃣ Updating Salvador's total_sales_volume...")
        print("-" * 80)
        
        result = await db.salespeople.update_one(
            {"_id": salvador_id},
            {
                "$set": {
                    "total_sales_volume": Decimal128(str(total_principal)),
                    "active_clients": 1
                }
            }
        )
        
        if result.modified_count > 0:
            print(f"   ✅ Updated Salvador's stats")
            print(f"      Total Sales: ${total_principal:,.2f}")
            print(f"      Active Clients: 1")
        else:
            print(f"   ℹ️  Salvador's stats unchanged")
        
        # Step 5: Verify the fix
        print(f"\n\n5️⃣ VERIFICATION")
        print("-" * 80)
        
        # Check investments
        alejandro_investments = await db.investments.find({
            "client_id": correct_client_id
        }).to_list(None)
        
        print(f"\n✅ Alejandro's Investments: {len(alejandro_investments)}")
        verify_total = 0
        for inv in alejandro_investments:
            principal = inv.get('principal_amount', 0)
            verify_total += principal
            fund_code = inv.get('fund_code', 'N/A')
            print(f"   - {fund_code}: ${principal:,.2f}")
            print(f"     Referred By: {inv.get('referred_by')}")
        
        print(f"\n   📊 Total: ${verify_total:,.2f}")
        
        # Check Salvador
        salvador = await db.salespeople.find_one({"_id": salvador_id})
        if salvador:
            sales_volume = salvador.get('total_sales_volume', 0)
            if hasattr(sales_volume, 'to_decimal'):
                sales_volume = float(sales_volume.to_decimal())
            print(f"\n✅ Salvador Palma:")
            print(f"   Total Sales: ${sales_volume:,.2f}")
            print(f"   Active Clients: {salvador.get('active_clients', 0)}")
        
        print("\n" + "=" * 80)
        print("✅ FIX COMPLETE!")
        print("=" * 80)
        print(f"\n📊 Summary:")
        print(f"   - Investments fixed: {result.modified_count}")
        print(f"   - Total principal: ${total_principal:,.2f}")
        print(f"   - Expected: $118,151.41")
        print(f"   - Match: {'✅ YES' if abs(total_principal - 118151.41) < 1 else '❌ NO'}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(fix_client_id())
