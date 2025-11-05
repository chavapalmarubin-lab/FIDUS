#!/usr/bin/env python3
"""
CLEANUP SCRIPT: Fix corrupted commission records
- Delete all 39 duplicate/corrupt commissions
- Regenerate correct commissions for both investments
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from bson.decimal128 import Decimal128

MONGO_URL = "mongodb+srv://chavapalmarubin_db_user:2170Tenoch!@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority"

async def cleanup_and_regenerate():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client['fidus_production']
    
    print("\n" + "=" * 80)
    print("COMMISSION CLEANUP & REGENERATION")
    print("=" * 80)
    
    # Get Salvador's data
    salvador = await db.salespeople.find_one({"referral_code": "SP-2025"})
    salvador_id = str(salvador['_id'])
    
    print(f"\nSalvador ID: {salvador_id}")
    print(f"Salvador Name: {salvador['name']}")
    
    # STEP 1: Delete ALL corrupt commissions
    print(f"\n" + "-" * 80)
    print("STEP 1: Deleting corrupt commissions")
    print("-" * 80)
    
    before_count = await db.referral_commissions.count_documents({"salesperson_id": salvador_id})
    print(f"Commissions before cleanup: {before_count}")
    
    delete_result = await db.referral_commissions.delete_many({"salesperson_id": salvador_id})
    print(f"✅ Deleted {delete_result.deleted_count} corrupt commission records")
    
    after_count = await db.referral_commissions.count_documents({"salesperson_id": salvador_id})
    print(f"Commissions after cleanup: {after_count}")
    
    # STEP 2: Get real investments
    print(f"\n" + "-" * 80)
    print("STEP 2: Finding real investments")
    print("-" * 80)
    
    investments = await db.investments.find({
        "referred_by": salvador_id
    }).to_list(None)
    
    print(f"Found {len(investments)} investments:")
    for inv in investments:
        print(f"  - ID: {inv['_id']}")
        print(f"    Fund: {inv.get('fund_code')}")
        print(f"    Principal: ${inv.get('principal_amount'):,.2f}")
        print(f"    Client: {inv.get('client_id')}")
    
    # STEP 3: Regenerate commissions for each investment
    print(f"\n" + "-" * 80)
    print("STEP 3: Regenerating commissions")
    print("-" * 80)
    
    COMMISSION_RATE = 0.10  # 10%
    total_commissions_created = 0
    
    for investment in investments:
        investment_id = str(investment['_id'])
        principal = float(investment.get('principal_amount', 0))
        fund_code = investment.get('fund_code', '')
        client_id = investment.get('client_id', '')
        
        # Get client name
        client = await db.clients.find_one({"_id": client_id})
        client_name = client.get('name', 'Unknown') if client else 'Unknown'
        
        print(f"\nGenerating commissions for {fund_code} investment (${principal:,.2f}):")
        
        # Determine payment schedule based on fund type
        if 'CORE' in fund_code:
            interest_rate = 0.015  # 1.5% monthly
            payment_frequency = "monthly"
            contract_months = 14
        elif 'BALANCE' in fund_code:
            interest_rate = 0.025  # 2.5% quarterly
            payment_frequency = "quarterly"
            contract_months = 14
        else:
            print(f"  ⚠️ Unknown fund type, skipping")
            continue
        
        # Calculate interest payments
        monthly_interest = principal * interest_rate
        
        # Generate commission schedule
        start_date = datetime(2025, 11, 1, tzinfo=timezone.utc)  # November 2025
        commissions_to_create = []
        
        if payment_frequency == "monthly":
            # Monthly payments for 14 months
            for month in range(contract_months):
                payment_date = start_date + timedelta(days=30 * (month + 1))
                commission_amount = monthly_interest * COMMISSION_RATE
                
                commission = {
                    "salesperson_id": salvador_id,
                    "salesperson_name": salvador['name'],
                    "client_id": client_id,
                    "client_name": client_name,
                    "investment_id": investment_id,
                    "product_type": fund_code,
                    "commission_amount": Decimal128(str(commission_amount)),
                    "commission_rate": COMMISSION_RATE,
                    "payment_number": month + 1,
                    "total_payments": contract_months,
                    "commission_due_date": payment_date,
                    "status": "pending",
                    "created_at": datetime.now(timezone.utc)
                }
                commissions_to_create.append(commission)
        
        elif payment_frequency == "quarterly":
            # Quarterly payments for 14 months = ~5 quarters (12 months / 3 = 4, but contract is 14 months)
            # Interest accrues monthly but paid quarterly
            total_quarters = (contract_months // 3) + 1 if contract_months % 3 > 0 else contract_months // 3
            
            for quarter in range(total_quarters):
                # Each quarter has 3 months of interest
                months_in_payment = 3 if quarter < total_quarters - 1 else (contract_months % 3 or 3)
                quarterly_interest = monthly_interest * months_in_payment
                payment_date = start_date + timedelta(days=90 * (quarter + 1))
                commission_amount = quarterly_interest * COMMISSION_RATE
                
                commission = {
                    "salesperson_id": salvador_id,
                    "salesperson_name": salvador['name'],
                    "client_id": client_id,
                    "client_name": client_name,
                    "investment_id": investment_id,
                    "product_type": fund_code,
                    "commission_amount": Decimal128(str(commission_amount)),
                    "commission_rate": COMMISSION_RATE,
                    "payment_number": quarter + 1,
                    "total_payments": total_quarters,
                    "commission_due_date": payment_date,
                    "status": "pending",
                    "created_at": datetime.now(timezone.utc)
                }
                commissions_to_create.append(commission)
        
        # Insert commissions
        if commissions_to_create:
            result = await db.referral_commissions.insert_many(commissions_to_create)
            print(f"  ✅ Created {len(result.inserted_ids)} commission records")
            total_commissions_created += len(result.inserted_ids)
            
            # Show first and last payment
            print(f"     First payment: {commissions_to_create[0]['commission_due_date'].strftime('%Y-%m-%d')} - ${float(commissions_to_create[0]['commission_amount'].to_decimal()):,.2f}")
            print(f"     Last payment: {commissions_to_create[-1]['commission_due_date'].strftime('%Y-%m-%d')} - ${float(commissions_to_create[-1]['commission_amount'].to_decimal()):,.2f}")
    
    # STEP 4: Verify
    print(f"\n" + "-" * 80)
    print("STEP 4: VERIFICATION")
    print("-" * 80)
    
    final_count = await db.referral_commissions.count_documents({"salesperson_id": salvador_id})
    print(f"\n✅ Total commissions created: {total_commissions_created}")
    print(f"✅ Final commission count: {final_count}")
    
    # Calculate totals by product
    commissions = await db.referral_commissions.find({"salesperson_id": salvador_id}).to_list(None)
    
    by_product = {}
    total_amount = 0
    
    for comm in commissions:
        product = comm.get('product_type', 'Unknown')
        amount = float(comm.get('commission_amount').to_decimal())
        
        if product not in by_product:
            by_product[product] = {"count": 0, "total": 0}
        
        by_product[product]["count"] += 1
        by_product[product]["total"] += amount
        total_amount += amount
    
    print(f"\nCommissions by product:")
    for product, data in by_product.items():
        print(f"  {product}: {data['count']} payments, ${data['total']:,.2f} total")
    
    print(f"\n💰 Grand Total Expected Commissions: ${total_amount:,.2f}")
    
    # Update Salvador's totals
    print(f"\n" + "-" * 80)
    print("STEP 5: Updating Salvador's totals")
    print("-" * 80)
    
    await db.salespeople.update_one(
        {"_id": salvador['_id']},
        {"$set": {
            "total_commissions_earned": Decimal128(str(total_amount)),
            "commissions_pending": Decimal128(str(total_amount)),
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    print(f"✅ Updated Salvador's commission totals")
    
    print("\n" + "=" * 80)
    print("✅ CLEANUP COMPLETE!")
    print("=" * 80)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(cleanup_and_regenerate())
