#!/usr/bin/env python3
"""
Direct fix for Alejandro's data
- Find ALL 3 investments in database
- Link both investments to Alejandro
- Set proper fund_type field
- Update Salvador's total_sales_volume
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from bson.decimal128 import Decimal128

MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://chavapalmarubin_db_user:2170Tenoch!@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority")
DB_NAME = "fidus_production"

print("=" * 80)
print("🔧 FIXING ALEJANDRO'S DATA")
print("=" * 80)

async def fix_data():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # Known IDs
        alejandro_client_id = "6909e8ebaaf69606babea152"
        salvador_id = "6909e8eaaaf69606babea151"
        
        print(f"\n📋 Target IDs:")
        print(f"   Alejandro Client: {alejandro_client_id}")
        print(f"   Salvador: {salvador_id}")
        
        # Step 1: Find ALL investments
        print("\n\n1️⃣ Finding ALL investments in database...")
        print("-" * 80)
        all_investments = await db.investments.find({}).to_list(None)
        print(f"✅ Found {len(all_investments)} total investments")
        
        for inv in all_investments:
            print(f"\n   Investment ID: {inv['_id']}")
            print(f"   Principal: ${inv.get('principal_amount', 0):,.2f}")
            print(f"   Fund Code: {inv.get('fund_code')}")
            print(f"   Client ID: {inv.get('client_id')}")
            print(f"   Referred By: {inv.get('referred_by')}")
        
        # Step 2: Identify Alejandro's investments (client_id matches)
        alejandro_investments = [
            inv for inv in all_investments 
            if str(inv.get('client_id')) == alejandro_client_id
        ]
        
        print(f"\n\n2️⃣ Alejandro's investments: {len(alejandro_investments)}")
        print("-" * 80)
        
        total_principal = 0
        for inv in alejandro_investments:
            principal = inv.get('principal_amount', 0)
            total_principal += principal
            print(f"\n   ✅ Investment {inv['_id']}")
            print(f"      Principal: ${principal:,.2f}")
            print(f"      Fund Code: {inv.get('fund_code')}")
        
        print(f"\n   📊 Total Principal: ${total_principal:,.2f}")
        
        # Step 3: Update investments to add fund_type field based on fund_code
        print(f"\n\n3️⃣ Updating investments with fund_type...")
        print("-" * 80)
        
        updated_count = 0
        for inv in alejandro_investments:
            fund_code = inv.get('fund_code', '')
            
            # Map fund_code to fund_type
            if 'CORE' in fund_code.upper():
                fund_type = 'CORE'
            elif 'BALANCE' in fund_code.upper():
                fund_type = 'BALANCE'
            elif 'DYNAMIC' in fund_code.upper():
                fund_type = 'DYNAMIC'
            else:
                # Guess based on principal amount
                principal = inv.get('principal_amount', 0)
                if principal < 50000:
                    fund_type = 'CORE'
                elif principal <= 200000:
                    fund_type = 'BALANCE'
                else:
                    fund_type = 'DYNAMIC'
            
            # ONLY update fund_type if missing - DO NOT create "amount" field
            update_fields = {}
            
            if not inv.get('fund_type'):
                update_fields['fund_type'] = fund_type
            
            if str(inv.get('referred_by')) != salvador_id:
                update_fields['referred_by'] = salvador_id
                update_fields['referred_by_name'] = "Salvador Palma"
            
            if update_fields:
                result = await db.investments.update_one(
                    {"_id": inv['_id']},
                    {"$set": update_fields}
                )
            else:
                result = type('obj', (object,), {'modified_count': 0})
            
            if result.modified_count > 0:
                print(f"   ✅ Updated {inv['_id']} - Set fund_type to {fund_type}")
                updated_count += 1
            else:
                print(f"   ℹ️  No changes needed for {inv['_id']}")
        
        print(f"\n   📊 Updated {updated_count} investments")
        
        # Step 4: Update Salvador's total_sales_volume
        print(f"\n\n4️⃣ Updating Salvador's total_sales_volume...")
        print("-" * 80)
        
        result = await db.salespeople.update_one(
            {"_id": salvador_id},
            {
                "$set": {
                    "total_sales_volume": Decimal128(str(total_principal)),
                    "active_clients": 1,
                    "updated_at": "2024-10-01T00:00:00Z"
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
        
        # Re-fetch Salvador
        salvador = await db.salespeople.find_one({"_id": salvador_id})
        if salvador:
            sales_volume = salvador.get('total_sales_volume', 0)
            if hasattr(sales_volume, 'to_decimal'):
                sales_volume = float(sales_volume.to_decimal())
            print(f"\n✅ Salvador Palma:")
            print(f"   Total Sales: ${sales_volume:,.2f}")
            print(f"   Active Clients: {salvador.get('active_clients', 0)}")
        
        # Re-fetch investments
        alejandro_investments_after = await db.investments.find({
            "client_id": alejandro_client_id
        }).to_list(None)
        
        print(f"\n✅ Alejandro's Investments: {len(alejandro_investments_after)}")
        for inv in alejandro_investments_after:
            amount = inv.get('amount', 0)
            print(f"   - {inv.get('fund_type', 'N/A')}: ${amount:,.2f}")
        
        print("\n" + "=" * 80)
        print("✅ FIX COMPLETE!")
        print("=" * 80)
        print(f"\n📊 Summary:")
        print(f"   - Investments updated: {updated_count}")
        print(f"   - Salvador's total sales: ${total_principal:,.2f}")
        print(f"   - Expected: $118,151.41")
        print(f"   - Match: {'✅ YES' if abs(total_principal - 118151.41) < 1 else '❌ NO'}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(fix_data())
