#!/usr/bin/env python3
"""
Update Salvador Palma's statistics to include BOTH investments:
- FIDUS CORE: $18,151.41
- FIDUS BALANCE: $100,000
Total: $118,151.41
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "fidus_db").strip('"').strip("'")

print("=" * 80)
print("🔧 UPDATING SALVADOR PALMA STATISTICS")
print("=" * 80)
print(f"MongoDB: {MONGO_URL}")
print(f"Database: {DB_NAME}")
print("=" * 80)

async def update_stats():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # Find Salvador Palma
        salvador = await db.salespeople.find_one({"referral_code": "SP-2025"})
        
        if not salvador:
            print("❌ Salvador Palma not found!")
            return
        
        salvador_id = salvador["_id"]
        print(f"\n✅ Found Salvador Palma")
        print(f"   ID: {salvador_id}")
        print(f"   Current Sales: ${salvador.get('total_sales_volume', 0):,.2f}")
        print(f"   Current Commissions: ${salvador.get('total_commissions_earned', 0):,.2f}")
        
        # Find Alejandro
        alejandro = await db.clients.find_one({"name": {"$regex": "Alejandro", "$options": "i"}})
        
        if not alejandro:
            print("❌ Alejandro not found!")
            return
        
        print(f"\n✅ Found Alejandro Mariscal")
        print(f"   ID: {alejandro['_id']}")
        
        # Find all investments
        investments = await db.investments.find({
            "client_id": str(alejandro["_id"])
        }).to_list(None)
        
        print(f"\n📊 Alejandro's Investments: {len(investments)}")
        total_investment = 0
        
        for inv in investments:
            amount = float(inv.get("amount", 0))
            fund = inv.get("fund_type")
            total_investment += amount
            print(f"   - {fund}: ${amount:,.2f}")
        
        print(f"   TOTAL: ${total_investment:,.2f}")
        
        # Check if investments are linked to Salvador
        investments_with_referral = await db.investments.find({
            "client_id": str(alejandro["_id"]),
            "referred_by": salvador_id
        }).to_list(None)
        
        print(f"\n🔗 Investments linked to Salvador: {len(investments_with_referral)}")
        
        if len(investments_with_referral) < len(investments):
            print(f"\n⚠️  ISSUE: Not all investments linked to Salvador!")
            print(f"   Updating investments to link to Salvador...")
            
            # Update all Alejandro's investments to reference Salvador
            result = await db.investments.update_many(
                {"client_id": str(alejandro["_id"])},
                {
                    "$set": {
                        "referred_by": salvador_id,
                        "referred_by_name": "Salvador Palma",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            print(f"   ✅ Updated {result.modified_count} investments")
        
        # Recalculate totals
        all_commissions = await db.referral_commissions.find({
            "salesperson_id": str(salvador_id)
        }).to_list(None)
        
        total_commissions = sum(float(c.get("amount", 0)) for c in all_commissions)
        commissions_paid = sum(float(c.get("amount", 0)) for c in all_commissions if c.get("status") == "paid")
        commissions_pending = sum(float(c.get("amount", 0)) for c in all_commissions if c.get("status") != "paid")
        
        print(f"\n💰 Commission Summary:")
        print(f"   Total Commissions: ${total_commissions:,.2f}")
        print(f"   Paid: ${commissions_paid:,.2f}")
        print(f"   Pending: ${commissions_pending:,.2f}")
        
        # Update Salvador's stats
        update_data = {
            "total_sales_volume": total_investment,
            "total_commissions_earned": total_commissions,
            "commissions_paid_to_date": commissions_paid,
            "commissions_pending": commissions_pending,
            "updated_at": datetime.utcnow()
        }
        
        await db.salespeople.update_one(
            {"_id": salvador_id},
            {"$set": update_data}
        )
        
        print(f"\n✅ UPDATED Salvador's Statistics:")
        print(f"   Total Sales Volume: ${total_investment:,.2f}")
        print(f"   Total Commissions: ${total_commissions:,.2f}")
        print(f"   Commissions Paid: ${commissions_paid:,.2f}")
        print(f"   Commissions Pending: ${commissions_pending:,.2f}")
        
        # Verify update
        updated_salvador = await db.salespeople.find_one({"_id": salvador_id})
        print(f"\n✅ Verification:")
        print(f"   Sales Volume in DB: ${updated_salvador.get('total_sales_volume', 0):,.2f}")
        print(f"   Commissions in DB: ${updated_salvador.get('total_commissions_earned', 0):,.2f}")
        
        print("\n" + "=" * 80)
        print("✅ UPDATE COMPLETE!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(update_stats())
