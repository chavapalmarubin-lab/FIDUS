#!/usr/bin/env python3
"""
Check Salvador's data in PREVIEW database
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

# Use preview MongoDB
MONGO_URL = os.getenv("MONGO_URL")
print(f"Connecting to: {MONGO_URL}")

async def check_salvador():
    client = AsyncIOMotorClient(MONGO_URL)
    # Extract DB name from connection string or use default
    db_name = "fidus_production"  # Adjust if needed
    db = client[db_name]
    
    print("\n" + "=" * 80)
    print("CHECKING SALVADOR'S DATA IN PREVIEW")
    print("=" * 80)
    
    # Find Salvador
    salvador = await db.salespeople.find_one({"referral_code": "SP-2025"})
    
    if not salvador:
        print("❌ Salvador not found!")
        client.close()
        return
    
    print(f"\n✅ Salvador found:")
    print(f"   ID: {salvador['_id']}")
    print(f"   Name: {salvador['name']}")
    print(f"   Email: {salvador['email']}")
    
    sales_volume = salvador.get('total_sales_volume', 0)
    if hasattr(sales_volume, 'to_decimal'):
        sales_volume = float(sales_volume.to_decimal())
    
    print(f"   Total Sales Volume: ${sales_volume:,.2f}")
    print(f"   Active: {salvador.get('active', False)}")
    
    # Find investments referred by Salvador
    salvador_id = str(salvador['_id'])
    investments = await db.investments.find({
        "referred_by": salvador_id
    }).to_list(None)
    
    print(f"\n📊 Investments referred by Salvador: {len(investments)}")
    total_principal = 0
    for inv in investments:
        principal = inv.get('principal_amount', 0)
        total_principal += principal
        print(f"   - {inv.get('fund_code', 'N/A')}: ${principal:,.2f}")
    
    print(f"\n   Total: ${total_principal:,.2f}")
    
    if total_principal != sales_volume:
        print(f"\n⚠️  MISMATCH!")
        print(f"   DB shows: ${sales_volume:,.2f}")
        print(f"   Should be: ${total_principal:,.2f}")
    else:
        print(f"\n✅ Data matches!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_salvador())
