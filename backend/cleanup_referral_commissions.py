#!/usr/bin/env python3
"""
Referral Commission Cleanup & Regeneration Script
==================================================

PURPOSE:
This script cleans up corrupted referral commission data and regenerates 
accurate commissions for Salvador Palma's referrals.

CURRENT ISSUES IDENTIFIED:
1. 16 commission records exist with incorrect data:
   - 12 records for investment 6909ed359244f3d04684ebca ($27.23 each) - CORE
   - 4 records for investment 6909ed359244f3d04684ebcc ($750.00 each) - BALANCE
2. All commissions missing critical fields:
   - No commission_id (showing as "NO_ID")
   - No fund_type (showing as "UNKNOWN")
   - No payment_month (showing as "UNKNOWN")
   - Principal amount is $0.00
3. Investment data issues:
   - 4 total investments found (2 appear to be duplicates)
   - Missing fund_type on all investments
   - Missing start_date on all investments
   - None have referral_salesperson_id set

CLEANUP ACTIONS:
1. Delete ALL existing commission records (16 total)
2. Fix investment data (add missing fields, link to Salvador)
3. Regenerate accurate commissions based on correct investment data

EXPECTED OUTCOME:
- Alejandro has 2 investments (CORE: $18,151.41, BALANCE: $100,000)
- Each investment linked to Salvador Palma as referrer
- Accurate commission schedules generated:
  * CORE: 12 monthly payments at 15% annual (starts day 90)
  * BALANCE: 4 quarterly payments at 30% annual (starts day 150)
"""

import os
from pymongo import MongoClient
from bson import ObjectId, Decimal128
from datetime import datetime, timedelta
from decimal import Decimal
import sys

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
if not mongo_url:
    print("❌ ERROR: MONGO_URL environment variable not set")
    sys.exit(1)

client = MongoClient(mongo_url)
db = client['fidus_production']

# Collections
commissions_collection = db.referral_commissions
investments_collection = db.investments
salespeople_collection = db.salespeople

def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def get_salvador_palma():
    """Get Salvador Palma's salesperson record"""
    salvador = salespeople_collection.find_one({"name": "Salvador Palma"})
    if not salvador:
        print("❌ ERROR: Salvador Palma not found in salespeople collection")
        sys.exit(1)
    
    # Ensure he has a salesperson_id
    if not salvador.get('salesperson_id'):
        salesperson_id = f"sp_{str(salvador['_id'])}"
        salespeople_collection.update_one(
            {"_id": salvador['_id']},
            {"$set": {"salesperson_id": salesperson_id}}
        )
        print(f"✅ Created salesperson_id for Salvador: {salesperson_id}")
        salvador['salesperson_id'] = salesperson_id
    
    return salvador

def cleanup_corrupted_commissions():
    """Delete all existing corrupted commission records"""
    print_section("STEP 1: DELETE CORRUPTED COMMISSION RECORDS")
    
    # Count existing commissions
    count = commissions_collection.count_documents({})
    print(f"📊 Current commission records: {count}")
    
    if count == 0:
        print("✅ No commissions to delete")
        return 0
    
    # Show what will be deleted
    commissions = list(commissions_collection.find({}))
    print(f"\n🗑️  WILL DELETE {count} COMMISSION RECORDS:")
    for i, comm in enumerate(commissions, 1):
        investment_id = comm.get('investment_id', 'NO_ID')
        commission_amt = comm.get('commission_amount')
        if isinstance(commission_amt, Decimal128):
            commission_amt = float(commission_amt.to_decimal())
        else:
            commission_amt = float(commission_amt) if commission_amt else 0
        print(f"  {i}. Investment: {investment_id}, Amount: ${commission_amt:.2f}")
    
    # Confirm deletion
    print(f"\n⚠️  This will DELETE ALL {count} commission records")
    confirmation = input("Type 'DELETE' to confirm: ")
    
    if confirmation != 'DELETE':
        print("❌ Deletion cancelled by user")
        sys.exit(0)
    
    # Delete all commissions
    result = commissions_collection.delete_many({})
    print(f"\n✅ DELETED {result.deleted_count} commission records")
    
    return result.deleted_count

def fix_investment_data(salvador):
    """Fix and standardize investment data"""
    print_section("STEP 2: FIX INVESTMENT DATA")
    
    # Get all investments
    all_investments = list(investments_collection.find({}))
    print(f"📊 Total investments in database: {len(all_investments)}")
    
    # Identify the correct 2 investments for Alejandro
    # Based on the data, we have:
    # - inv_alejandro_balance_001: $100,000
    # - inv_alejandro_core_001: $18,151.41
    
    core_investment_id = "inv_alejandro_core_001"
    balance_investment_id = "inv_alejandro_balance_001"
    
    # Investment start date (October 1, 2025 as per product requirements)
    start_date = datetime(2025, 10, 1, 0, 0, 0)
    
    # Fix CORE investment
    print(f"\n🔧 Fixing CORE investment ({core_investment_id})...")
    core_result = investments_collection.update_one(
        {"investment_id": core_investment_id},
        {
            "$set": {
                "fund_type": "FIDUS_CORE",
                "start_date": start_date,
                "referral_salesperson_id": salvador['salesperson_id'],
                "updated_at": datetime.now()
            }
        }
    )
    
    if core_result.matched_count > 0:
        print(f"  ✅ CORE investment updated")
    else:
        print(f"  ❌ CORE investment not found")
    
    # Fix BALANCE investment
    print(f"\n🔧 Fixing BALANCE investment ({balance_investment_id})...")
    balance_result = investments_collection.update_one(
        {"investment_id": balance_investment_id},
        {
            "$set": {
                "fund_type": "FIDUS_BALANCE",
                "start_date": start_date,
                "referral_salesperson_id": salvador['salesperson_id'],
                "updated_at": datetime.now()
            }
        }
    )
    
    if balance_result.matched_count > 0:
        print(f"  ✅ BALANCE investment updated")
    else:
        print(f"  ❌ BALANCE investment not found")
    
    # Delete duplicate investments (the ones using ObjectId as investment_id)
    print(f"\n🗑️  Removing duplicate investments...")
    duplicate_ids = ["6909ed359244f3d04684ebc9", "6909ed359244f3d04684ebcb"]
    for dup_id in duplicate_ids:
        dup_result = investments_collection.delete_one({"investment_id": dup_id})
        if dup_result.deleted_count > 0:
            print(f"  ✅ Deleted duplicate: {dup_id}")
    
    # Verify final state
    print(f"\n📊 Final investment count:")
    final_count = investments_collection.count_documents({})
    print(f"  Total investments: {final_count}")
    
    return {
        "core_id": core_investment_id,
        "balance_id": balance_investment_id
    }

def generate_commissions(salvador, investment_ids):
    """Generate accurate commission schedules"""
    print_section("STEP 3: GENERATE ACCURATE COMMISSIONS")
    
    # Get the investments
    core_inv = investments_collection.find_one({"investment_id": investment_ids["core_id"]})
    balance_inv = investments_collection.find_one({"investment_id": investment_ids["balance_id"]})
    
    if not core_inv or not balance_inv:
        print("❌ ERROR: Could not find investments")
        sys.exit(1)
    
    # Extract amounts
    core_amount = core_inv.get('amount') or core_inv.get('principal_amount')
    if isinstance(core_amount, Decimal128):
        core_amount = float(core_amount.to_decimal())
    else:
        core_amount = float(core_amount) if core_amount else 0
    
    balance_amount = balance_inv.get('amount') or balance_inv.get('principal_amount')
    if isinstance(balance_amount, Decimal128):
        balance_amount = float(balance_amount.to_decimal())
    else:
        balance_amount = float(balance_amount) if balance_amount else 0
    
    start_date = core_inv.get('start_date')
    client_id = str(core_inv.get('client_id'))
    
    print(f"📊 Investment Details:")
    print(f"  CORE: ${core_amount:,.2f}")
    print(f"  BALANCE: ${balance_amount:,.2f}")
    print(f"  Start Date: {start_date}")
    print(f"  Client ID: {client_id}")
    
    commissions_to_create = []
    
    # CORE: 15% annual = 1.25% monthly, 12 payments, starts day 90
    print(f"\n💰 Generating CORE commissions...")
    core_monthly_rate = Decimal('0.0125')  # 1.25%
    core_interest = Decimal(str(core_amount)) * core_monthly_rate
    core_commission = core_interest * Decimal('0.10')  # 10% commission
    
    core_first_payment = start_date + timedelta(days=90)
    
    for month in range(1, 13):
        payment_date = core_first_payment + timedelta(days=30 * (month - 1))
        
        commission = {
            "commission_id": f"comm_{salvador['salesperson_id']}_{investment_ids['core_id']}_m{month}",
            "salesperson_id": salvador['salesperson_id'],
            "investment_id": investment_ids['core_id'],
            "client_id": client_id,
            "fund_type": "FIDUS_CORE",
            "principal_amount": Decimal128(Decimal(str(core_amount))),
            "interest_amount": Decimal128(core_interest),
            "commission_amount": Decimal128(core_commission),
            "payment_month": f"Month {month}",
            "payment_date": payment_date,
            "status": "pending",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        commissions_to_create.append(commission)
        print(f"  Month {month}: ${float(core_commission):.2f} (payment: {payment_date.strftime('%Y-%m-%d')})")
    
    # BALANCE: 30% annual = 7.5% quarterly, 4 payments, starts day 150
    print(f"\n💰 Generating BALANCE commissions...")
    balance_quarterly_rate = Decimal('0.075')  # 7.5%
    balance_interest = Decimal(str(balance_amount)) * balance_quarterly_rate
    balance_commission = balance_interest * Decimal('0.10')  # 10% commission
    
    balance_first_payment = start_date + timedelta(days=150)
    
    for quarter in range(1, 5):
        payment_date = balance_first_payment + timedelta(days=90 * (quarter - 1))
        
        commission = {
            "commission_id": f"comm_{salvador['salesperson_id']}_{investment_ids['balance_id']}_q{quarter}",
            "salesperson_id": salvador['salesperson_id'],
            "investment_id": investment_ids['balance_id'],
            "client_id": client_id,
            "fund_type": "FIDUS_BALANCE",
            "principal_amount": Decimal128(Decimal(str(balance_amount))),
            "interest_amount": Decimal128(balance_interest),
            "commission_amount": Decimal128(balance_commission),
            "payment_month": f"Quarter {quarter}",
            "payment_date": payment_date,
            "status": "pending",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        commissions_to_create.append(commission)
        print(f"  Quarter {quarter}: ${float(balance_commission):.2f} (payment: {payment_date.strftime('%Y-%m-%d')})")
    
    # Insert all commissions
    print(f"\n💾 Inserting {len(commissions_to_create)} commission records...")
    result = commissions_collection.insert_many(commissions_to_create)
    print(f"✅ Successfully created {len(result.inserted_ids)} commission records")
    
    return len(result.inserted_ids)

def verify_results(salvador):
    """Verify the cleanup and regeneration was successful"""
    print_section("STEP 4: VERIFICATION")
    
    # Count commissions
    total_commissions = commissions_collection.count_documents({})
    core_commissions = commissions_collection.count_documents({"fund_type": "FIDUS_CORE"})
    balance_commissions = commissions_collection.count_documents({"fund_type": "FIDUS_BALANCE"})
    
    print(f"📊 Commission Counts:")
    print(f"  Total: {total_commissions}")
    print(f"  CORE: {core_commissions}")
    print(f"  BALANCE: {balance_commissions}")
    
    # Calculate total commission amounts
    core_total = 0
    balance_total = 0
    
    for comm in commissions_collection.find({"fund_type": "FIDUS_CORE"}):
        amt = comm.get('commission_amount')
        if isinstance(amt, Decimal128):
            core_total += float(amt.to_decimal())
    
    for comm in commissions_collection.find({"fund_type": "FIDUS_BALANCE"}):
        amt = comm.get('commission_amount')
        if isinstance(amt, Decimal128):
            balance_total += float(amt.to_decimal())
    
    grand_total = core_total + balance_total
    
    print(f"\n💰 Commission Amounts:")
    print(f"  CORE Total: ${core_total:.2f}")
    print(f"  BALANCE Total: ${balance_total:.2f}")
    print(f"  Grand Total: ${grand_total:.2f}")
    
    # Check investments
    investments = list(investments_collection.find({"referral_salesperson_id": salvador['salesperson_id']}))
    print(f"\n📊 Investments Linked to Salvador:")
    print(f"  Count: {len(investments)}")
    for inv in investments:
        print(f"  - {inv.get('investment_id')}: {inv.get('fund_type')}")
    
    # Expected values
    print(f"\n✅ VERIFICATION SUMMARY:")
    print(f"  Expected commission count: 16 (12 CORE + 4 BALANCE)")
    print(f"  Actual commission count: {total_commissions}")
    print(f"  Expected CORE commissions: 12")
    print(f"  Actual CORE commissions: {core_commissions}")
    print(f"  Expected BALANCE commissions: 4")
    print(f"  Actual BALANCE commissions: {balance_commissions}")
    
    if total_commissions == 16 and core_commissions == 12 and balance_commissions == 4:
        print(f"\n✅ ✅ ✅ ALL VERIFICATIONS PASSED! ✅ ✅ ✅")
        return True
    else:
        print(f"\n⚠️  WARNING: Commission counts don't match expected values")
        return False

def main():
    """Main execution function"""
    print_section("REFERRAL COMMISSION CLEANUP & REGENERATION")
    print("This script will:")
    print("1. Delete all existing corrupted commission records")
    print("2. Fix investment data (add fund_type, start_date, link to Salvador)")
    print("3. Generate accurate commission schedules")
    print("4. Verify the results")
    
    print(f"\n⚠️  WARNING: This operation will DELETE and RECREATE all commission data")
    proceed = input("\nType 'PROCEED' to continue: ")
    
    if proceed != 'PROCEED':
        print("❌ Operation cancelled by user")
        sys.exit(0)
    
    # Get Salvador
    salvador = get_salvador_palma()
    
    # Step 1: Cleanup
    deleted_count = cleanup_corrupted_commissions()
    
    # Step 2: Fix investments
    investment_ids = fix_investment_data(salvador)
    
    # Step 3: Generate commissions
    created_count = generate_commissions(salvador, investment_ids)
    
    # Step 4: Verify
    success = verify_results(salvador)
    
    # Final summary
    print_section("CLEANUP & REGENERATION COMPLETE")
    print(f"✅ Deleted: {deleted_count} corrupted commission records")
    print(f"✅ Created: {created_count} new accurate commission records")
    print(f"✅ Status: {'SUCCESS' if success else 'PARTIAL - NEEDS REVIEW'}")
    
    if success:
        print(f"\n🎉 Salvador Palma's referral commissions are now accurate!")
        print(f"   - 12 CORE monthly commissions (15% annual)")
        print(f"   - 4 BALANCE quarterly commissions (30% annual)")
        print(f"   - All linked to Alejandro's investments")

if __name__ == "__main__":
    main()
