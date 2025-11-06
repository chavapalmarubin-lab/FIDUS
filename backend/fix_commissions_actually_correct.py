import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from bson import Decimal128
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

async def fix_commissions_actually_correct():
    """
    Generate CORRECT commissions per SYSTEM_MASTER.md
    
    BALANCE Fund:
    - Monthly interest RATE: 2.5%
    - Monthly interest AMOUNT: $100,000 × 2.5% = $2,500
    - Quarterly interest: $2,500 × 3 = $7,500
    - Commission: $7,500 × 10% = $750 per quarter
    
    CORE Fund:
    - Monthly interest: $18,151.41 × 1.5% = $272.27
    - Commission: $272.27 × 10% = $27.23 per month
    """
    
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    salvador_id = "sp_6909e8eaaaf69606babea151"
    
    # Delete ALL existing commissions
    result = await db.referral_commissions.delete_many({"salesperson_id": salvador_id})
    print(f"🗑️ Deleted {result.deleted_count} old commission records")
    
    # CORRECT CALCULATIONS
    core_monthly_interest = 18151.41 * 0.015  # $272.27
    core_monthly_commission = core_monthly_interest * 0.10  # $27.23
    
    # BALANCE: 2.5% MONTHLY rate, but pays QUARTERLY
    balance_monthly_rate = 0.025
    balance_monthly_interest = 100000 * balance_monthly_rate  # $2,500 per month
    balance_quarterly_interest = balance_monthly_interest * 3  # $7,500 per quarter
    balance_quarterly_commission = balance_quarterly_interest * 0.10  # $750 per quarter
    
    print(f"\n{'='*60}")
    print(f"CORRECT INTEREST CALCULATIONS:")
    print(f"{'='*60}")
    print(f"CORE:")
    print(f"  Monthly Interest: ${core_monthly_interest:,.2f}")
    print(f"  Monthly Commission (10%): ${core_monthly_commission:,.2f}")
    print(f"\nBALANCE:")
    print(f"  Monthly Rate: 2.5%")
    print(f"  Monthly Interest: ${balance_monthly_interest:,.2f}")
    print(f"  Quarterly Interest (3 months): ${balance_quarterly_interest:,.2f}")
    print(f"  Quarterly Commission (10%): ${balance_quarterly_commission:,.2f}")
    
    commissions = []
    commission_id_counter = 1
    
    # CORE: 12 monthly commissions starting Dec 30, 2025
    core_start = datetime(2025, 10, 1)
    core_first_payment = core_start + timedelta(days=90)  # Dec 30, 2025
    
    for i in range(12):
        payment_date = core_first_payment + timedelta(days=30*i)
        
        commission = {
            "commission_id": f"comm_salvador_{commission_id_counter:03d}",
            "salesperson_id": salvador_id,
            "salesperson_name": "Salvador Palma",
            "client_id": "6909e8ebaaf69606babea152",
            "client_name": "Alejandro Mariscal Romero",
            "investment_id": "inv_alejandro_core_001",
            "fund_type": "CORE",
            "commission_amount": Decimal128(str(round(core_monthly_commission, 2))),
            "client_interest_amount": Decimal128(str(round(core_monthly_interest, 2))),
            "commission_rate": 0.10,
            "payment_date": payment_date,
            "status": "pending",
            "payment_number": i + 1,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        commissions.append(commission)
        commission_id_counter += 1
    
    # BALANCE: 4 quarterly commissions starting Feb 28, 2026
    balance_start = datetime(2025, 10, 1)
    balance_first_payment = balance_start + timedelta(days=150)  # Feb 28, 2026
    
    for i in range(4):
        payment_date = balance_first_payment + timedelta(days=90*i)
        
        commission = {
            "commission_id": f"comm_salvador_{commission_id_counter:03d}",
            "salesperson_id": salvador_id,
            "salesperson_name": "Salvador Palma",
            "client_id": "6909e8ebaaf69606babea152",
            "client_name": "Alejandro Mariscal Romero",
            "investment_id": "inv_alejandro_balance_001",
            "fund_type": "BALANCE",
            "commission_amount": Decimal128(str(round(balance_quarterly_commission, 2))),
            "client_interest_amount": Decimal128(str(round(balance_quarterly_interest, 2))),
            "commission_rate": 0.10,
            "payment_date": payment_date,
            "status": "pending",
            "payment_number": i + 1,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        commissions.append(commission)
        commission_id_counter += 1
    
    # Insert all commissions
    if commissions:
        result = await db.referral_commissions.insert_many(commissions)
        print(f"\n✅ Created {len(result.inserted_ids)} commission records")
    
    # Calculate totals
    total_core_commissions = core_monthly_commission * 12
    total_balance_commissions = balance_quarterly_commission * 4
    total_commissions = total_core_commissions + total_balance_commissions
    
    # Update Salvador's stats
    await db.salespeople.update_one(
        {"_id": salvador_id},
        {
            "$set": {
                "total_sales": Decimal128("118151.41"),
                "total_commissions": Decimal128(str(round(total_commissions, 2))),
                "pending_commissions": Decimal128(str(round(total_commissions, 2))),
                "active_clients": 1,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    print(f"\n{'='*60}")
    print(f"FINAL COMMISSION SUMMARY:")
    print(f"{'='*60}")
    print(f"CORE: 12 payments × ${core_monthly_commission:,.2f} = ${total_core_commissions:,.2f}")
    print(f"BALANCE: 4 payments × ${balance_quarterly_commission:,.2f} = ${total_balance_commissions:,.2f}")
    print(f"{'='*60}")
    print(f"TOTAL COMMISSIONS: ${total_commissions:,.2f}")
    print(f"{'='*60}")
    print(f"\nExpected per SYSTEM_MASTER.md Section 7.3: $3,326.76")
    
    if abs(total_commissions - 3326.76) < 1.0:
        print(f"✅ SUCCESS! Matches expected value!")
    else:
        print(f"❌ ERROR: Difference of ${abs(total_commissions - 3326.76):,.2f}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_commissions_actually_correct())
