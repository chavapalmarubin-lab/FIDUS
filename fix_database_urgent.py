#!/usr/bin/env python3
"""
URGENT DATABASE FIX SCRIPT
==========================

Fixes critical database issues found in production:
1. Sets fund_type for all investments (currently None)
2. Updates Salvador Palma's totals
3. Cleans up incomplete investment records

Run this IMMEDIATELY to fix production data.
"""

import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

async def fix_database():
    # Connect to production database
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    print("═══════════════════════════════════════════════════════════════")
    print("URGENT DATABASE FIX SCRIPT")
    print("Starting:", datetime.utcnow().isoformat())
    print("═══════════════════════════════════════════════════════════════\n")
    
    # FIX 1: Update fund_type for Alejandro's investments
    print("FIX 1: Setting fund_type for investments...")
    print("-" * 70)
    
    # Find Alejandro's CORE investment ($18,151.41)
    core_result = await db.investments.update_one(
        {
            "client_name": {"$in": ["Alejandro Mariscal", "Alejandro Mariscal Romero"]},
            "principal_amount": 18151.41,
            "fund_type": None
        },
        {
            "$set": {
                "fund_type": "CORE",
                "updated_at": datetime.utcnow()
            }
        }
    )
    print(f"  CORE fund: Updated {core_result.modified_count} record(s)")
    
    # Find Alejandro's BALANCE investment ($100,000)
    balance_result = await db.investments.update_one(
        {
            "client_name": {"$in": ["Alejandro Mariscal", "Alejandro Mariscal Romero"]},
            "principal_amount": 100000.00,
            "fund_type": None
        },
        {
            "$set": {
                "fund_type": "BALANCE",
                "updated_at": datetime.utcnow()
            }
        }
    )
    print(f"  BALANCE fund: Updated {balance_result.modified_count} record(s)")
    
    # Verify the updates
    core_check = await db.investments.find_one(
        {"fund_type": "CORE", "principal_amount": 18151.41}
    )
    balance_check = await db.investments.find_one(
        {"fund_type": "BALANCE", "principal_amount": 100000.00}
    )
    
    print(f"\n  Verification:")
    print(f"    CORE investment: {'✅ FIXED' if core_check else '❌ NOT FOUND'}")
    print(f"    BALANCE investment: {'✅ FIXED' if balance_check else '❌ NOT FOUND'}")
    
    # FIX 2: Update Salvador Palma's totals
    print("\n" + "="*70)
    print("FIX 2: Updating Salvador Palma's totals...")
    print("-" * 70)
    
    # Calculate total sales from investments
    investments_pipeline = [
        {"$match": {"salesperson_name": "Salvador Palma"}},
        {"$group": {"_id": None, "total": {"$sum": "$principal_amount"}}}
    ]
    sales_result = await db.investments.aggregate(investments_pipeline).to_list(length=1)
    total_sales = sales_result[0]['total'] if sales_result else 0
    
    # Calculate total commissions
    commissions_pipeline = [
        {"$match": {"salesperson_name": "Salvador Palma"}},
        {"$group": {"_id": None, "total": {"$sum": "$commission_amount"}}}
    ]
    comm_result = await db.referral_commissions.aggregate(commissions_pipeline).to_list(length=1)
    total_commissions = comm_result[0]['total'] if comm_result else 0
    
    print(f"  Calculated totals:")
    print(f"    Total Sales: ${total_sales:,.2f}")
    print(f"    Total Commissions: ${total_commissions:,.2f}")
    
    # Update Salvador's record
    salvador_result = await db.salespeople.update_one(
        {"name": "Salvador Palma"},
        {
            "$set": {
                "total_sales": total_sales,
                "total_commissions": total_commissions,
                "updated_at": datetime.utcnow()
            }
        }
    )
    print(f"\n  Updated Salvador's record: {salvador_result.modified_count} record(s)")
    
    # Verify Salvador's totals
    salvador = await db.salespeople.find_one({"name": "Salvador Palma"})
    if salvador:
        print(f"\n  Verification:")
        print(f"    Total Sales: ${salvador.get('total_sales', 0):,.2f} ✅")
        print(f"    Total Commissions: ${salvador.get('total_commissions', 0):,.2f} ✅")
    
    # FIX 3: Handle incomplete investment records
    print("\n" + "="*70)
    print("FIX 3: Checking incomplete investment records...")
    print("-" * 70)
    
    # Find records with no client name and $0 principal
    incomplete = await db.investments.find({
        "$or": [
            {"client_name": None},
            {"client_name": ""},
            {"principal_amount": 0}
        ]
    }).to_list(length=None)
    
    print(f"  Found {len(incomplete)} incomplete record(s)")
    
    if incomplete:
        print(f"\n  These records should be reviewed:")
        for record in incomplete:
            print(f"    - ID: {record.get('_id')}, Client: {record.get('client_name')}, Amount: ${record.get('principal_amount', 0)}")
        
        # Option to mark as inactive or delete
        print(f"\n  Marking incomplete records as 'inactive'...")
        inactive_result = await db.investments.update_many(
            {
                "$or": [
                    {"client_name": None, "principal_amount": 0},
                    {"client_name": "", "principal_amount": 0}
                ]
            },
            {
                "$set": {
                    "status": "inactive",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        print(f"  Marked {inactive_result.modified_count} record(s) as inactive")
    
    # FINAL VERIFICATION
    print("\n" + "="*70)
    print("FINAL VERIFICATION")
    print("="*70)
    
    # Check all investments
    all_investments = await db.investments.find({"status": "active"}).to_list(length=None)
    print(f"\n  Active Investments: {len(all_investments)}")
    
    total_aum = 0
    funds_breakdown = {}
    
    for inv in all_investments:
        fund_type = inv.get('fund_type', 'None')
        principal = float(inv.get('principal_amount', 0))
        total_aum += principal
        
        if fund_type not in funds_breakdown:
            funds_breakdown[fund_type] = {'count': 0, 'amount': 0}
        
        funds_breakdown[fund_type]['count'] += 1
        funds_breakdown[fund_type]['amount'] += principal
    
    print(f"\n  Breakdown by Fund Type:")
    for fund_type, data in funds_breakdown.items():
        print(f"    {fund_type}: {data['count']} investment(s), ${data['amount']:,.2f}")
    
    print(f"\n  Total AUM: ${total_aum:,.2f}")
    print(f"  Expected: $118,151.41")
    print(f"  Match: {'✅ YES' if abs(total_aum - 118151.41) < 1 else '❌ NO'}")
    
    # Check Salvador
    salvador_final = await db.salespeople.find_one({"name": "Salvador Palma"})
    if salvador_final:
        print(f"\n  Salvador Palma:")
        print(f"    Total Sales: ${salvador_final.get('total_sales', 0):,.2f}")
        print(f"    Total Commissions: ${salvador_final.get('total_commissions', 0):,.2f}")
        
        sales_match = abs(salvador_final.get('total_sales', 0) - 118151.41) < 1
        comm_match = abs(salvador_final.get('total_commissions', 0) - 3326.73) < 1
        
        print(f"    Sales Match: {'✅ YES' if sales_match else '❌ NO'}")
        print(f"    Commissions Match: {'✅ YES' if comm_match else '❌ NO'}")
    
    print("\n" + "="*70)
    print("DATABASE FIX COMPLETE")
    print("Completed:", datetime.utcnow().isoformat())
    print("="*70)
    
    client.close()

if __name__ == "__main__":
    print("\n⚠️  WARNING: This script will modify the production database!")
    print("   Database: fidus_production")
    print("   Changes: Set fund_type, update totals, mark incomplete records as inactive")
    print("\n")
    
    response = input("Do you want to proceed? (yes/no): ").strip().lower()
    
    if response == 'yes':
        print("\n✅ Proceeding with database fixes...\n")
        asyncio.run(fix_database())
    else:
        print("\n❌ Aborted. No changes made to database.")
