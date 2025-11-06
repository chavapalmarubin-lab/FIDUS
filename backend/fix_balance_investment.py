import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

async def fix_balance():
    """Fix BALANCE investment dates"""
    
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    # Correct dates per SYSTEM_MASTER.md
    start_date = datetime(2025, 10, 1)  # October 1, 2025
    first_payment = start_date + timedelta(days=150)  # February 28, 2026
    incubation_end = start_date + timedelta(days=60)  # November 30, 2025
    contract_end = start_date + timedelta(days=426)  # December 1, 2026
    
    print(f"📅 CORRECT DATES FOR BALANCE FUND:")
    print(f"Investment Date: {start_date.date()}")
    print(f"Incubation End (60 days): {incubation_end.date()}")
    print(f"First Payment (150 days): {first_payment.date()}")
    print(f"Contract End (426 days): {contract_end.date()}")
    
    # Update the BALANCE investment
    result = await db.investments.update_one(
        {
            "investment_id": "inv_alejandro_balance_001",
            "fund_type": "BALANCE"
        },
        {
            "$set": {
                "start_date": start_date,
                "investment_date": start_date,
                "first_payment_date": first_payment,
                "incubation_end_date": incubation_end,
                "contract_end_date": contract_end,
                "interest_rate": 0.025,  # 2.5% per quarter
                "salesperson_id": "sp_6909e8eaaaf69606babea151",
                "referral_salesperson_id": "sp_6909e8eaaaf69606babea151"
            }
        }
    )
    
    print(f"\n✅ UPDATE RESULT:")
    print(f"Matched: {result.matched_count}")
    print(f"Modified: {result.modified_count}")
    
    # Also fix the CORE investment
    core_start = datetime(2025, 10, 1)
    core_first_payment = core_start + timedelta(days=90)  # December 30, 2025
    core_incubation_end = core_start + timedelta(days=60)  # November 30, 2025
    core_contract_end = core_start + timedelta(days=426)  # December 1, 2026
    
    print(f"\n📅 CORRECT DATES FOR CORE FUND:")
    print(f"Investment Date: {core_start.date()}")
    print(f"Incubation End (60 days): {core_incubation_end.date()}")
    print(f"First Payment (90 days): {core_first_payment.date()}")
    print(f"Contract End (426 days): {core_contract_end.date()}")
    
    result2 = await db.investments.update_one(
        {
            "investment_id": "inv_alejandro_core_001",
            "fund_type": "CORE"
        },
        {
            "$set": {
                "start_date": core_start,
                "investment_date": core_start,
                "first_payment_date": core_first_payment,
                "incubation_end_date": core_incubation_end,
                "contract_end_date": core_contract_end,
                "interest_rate": 0.015,  # 1.5% per month
                "salesperson_id": "sp_6909e8eaaaf69606babea151",
                "referral_salesperson_id": "sp_6909e8eaaaf69606babea151"
            }
        }
    )
    
    print(f"\n✅ CORE UPDATE RESULT:")
    print(f"Matched: {result2.matched_count}")
    print(f"Modified: {result2.modified_count}")
    
    # Delete the duplicate CORE investment with $0
    result3 = await db.investments.delete_one({
        "fund_type": "CORE",
        "principal_amount": 0
    })
    
    print(f"\n🗑️ DELETED DUPLICATE:")
    print(f"Deleted: {result3.deleted_count} records")
    
    # Verify
    print(f"\n{'='*60}")
    print(f"VERIFICATION")
    print(f"{'='*60}")
    
    balance_inv = await db.investments.find_one({"investment_id": "inv_alejandro_balance_001"})
    core_inv = await db.investments.find_one({"investment_id": "inv_alejandro_core_001"})
    
    print(f"\n✓ BALANCE FUND:")
    print(f"  Start: {balance_inv.get('start_date')}")
    print(f"  First Payment: {balance_inv.get('first_payment_date')}")
    print(f"  Interest Rate: {balance_inv.get('interest_rate')}")
    
    print(f"\n✓ CORE FUND:")
    print(f"  Start: {core_inv.get('start_date')}")
    print(f"  First Payment: {core_inv.get('first_payment_date')}")
    print(f"  Interest Rate: {core_inv.get('interest_rate')}")
    
    # Check if dates are correct
    if balance_inv.get('first_payment_date') == first_payment:
        print(f"\n✅ SUCCESS! BALANCE first payment = February 28, 2026")
    else:
        print(f"\n❌ FAILED! BALANCE first payment = {balance_inv.get('first_payment_date')}")
    
    if core_inv.get('first_payment_date') == core_first_payment:
        print(f"✅ SUCCESS! CORE first payment = December 30, 2025")
    else:
        print(f"❌ FAILED! CORE first payment = {core_inv.get('first_payment_date')}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_balance())
