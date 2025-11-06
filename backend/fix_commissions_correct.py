import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from bson import Decimal128, ObjectId
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

async def fix_commissions():
    """Delete all and recreate correct commissions"""
    
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    salvador_id = "sp_6909e8eaaaf69606babea151"
    
    # Delete all existing commissions
    result = await db.referral_commissions.delete_many({"salesperson_id": salvador_id})
    print(f"🗑️ Deleted {result.deleted_count} commission records")
    
    # Generate correct commissions
    # CORE: $18,151.41 × 1.5% = $272.27 per month → 10% = $27.23 commission
    # BALANCE: $100,000 × 2.5% = $2,500 per quarter → 10% = $250 commission
    
    core_monthly_interest = 18151.41 * 0.015  # $272.27
    core_monthly_commission = core_monthly_interest * 0.10  # $27.23
    
    balance_quarterly_interest = 100000 * 0.025  # $2,500
    balance_quarterly_commission = balance_quarterly_interest * 0.10  # $250
    
    print(f"\n✅ CORRECT CALCULATIONS:")
    print(f"CORE Monthly Interest: ${core_monthly_interest:,.2f}")
    print(f"CORE Monthly Commission (10%): ${core_monthly_commission:,.2f}")
    print(f"BALANCE Quarterly Interest: ${balance_quarterly_interest:,.2f}")
    print(f"BALANCE Quarterly Commission (10%): ${balance_quarterly_commission:,.2f}")
    
    commissions = []
    commission_id_counter = 1
    
    # CORE: 12 monthly commissions starting Dec 30, 2025
    core_start = datetime(2025, 10, 1)
    core_first_payment = core_start + timedelta(days=90)  # Dec 30, 2025
    
    for i in range(12):
        payment_date = core_first_payment + timedelta(days=30*i)
        period_start = core_first_payment + timedelta(days=30*i) - timedelta(days=30)
        period_end = payment_date
        
        commission = {
            "commission_id": f"comm_salvador_{commission_id_counter:03d}",
            "salesperson_id": salvador_id,
            "salesperson_name": "Salvador Palma",
            "client_id": "6909e8ebaaf69606babea152",
            "client_name": "Alejandro Mariscal Romero",
            "investment_id": "inv_alejandro_core_001",
            "fund_type": "FIDUS_CORE",
            "commission_amount": Decimal128(str(round(core_monthly_commission, 2))),
            "interest_amount": Decimal128(str(round(core_monthly_interest, 2))),
            "commission_rate": 0.10,
            "payment_date": payment_date,
            "status": "pending",
            "period_start": period_start,
            "period_end": period_end,
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
        period_start = balance_first_payment + timedelta(days=90*i) - timedelta(days=90)
        period_end = payment_date
        
        commission = {
            "commission_id": f"comm_salvador_{commission_id_counter:03d}",
            "salesperson_id": salvador_id,
            "salesperson_name": "Salvador Palma",
            "client_id": "6909e8ebaaf69606babea152",
            "client_name": "Alejandro Mariscal Romero",
            "investment_id": "inv_alejandro_balance_001",
            "fund_type": "FIDUS_BALANCE",
            "commission_amount": Decimal128(str(round(balance_quarterly_commission, 2))),
            "interest_amount": Decimal128(str(round(balance_quarterly_interest, 2))),
            "commission_rate": 0.10,
            "payment_date": payment_date,
            "status": "pending",
            "period_start": period_start,
            "period_end": period_end,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        commissions.append(commission)
        commission_id_counter += 1
    
    # Insert all commissions
    if commissions:
        result = await db.referral_commissions.insert_many(commissions)
        print(f"\n✅ Created {len(result.inserted_ids)} commission records")
    
    # Update Salvador's stats
    total_commissions = (core_monthly_commission * 12) + (balance_quarterly_commission * 4)
    
    await db.salespeople.update_one(
        {"_id": salvador_id},
        {
            "$set": {
                "total_commissions_earned": Decimal128(str(round(total_commissions, 2))),
                "total_sales_volume": Decimal128("118151.41"),
                "total_clients_referred": 1,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    print(f"\n{'='*60}")
    print(f"FINAL SUMMARY:")
    print(f"{'='*60}")
    print(f"CORE: 12 × ${core_monthly_commission:,.2f} = ${core_monthly_commission * 12:,.2f}")
    print(f"BALANCE: 4 × ${balance_quarterly_commission:,.2f} = ${balance_quarterly_commission * 4:,.2f}")
    print(f"TOTAL: ${total_commissions:,.2f}")
    
    print(f"\n✓ Expected from SYSTEM_MASTER.md: $1,326.73")
    
    if abs(total_commissions - 1326.73) < 1.0:
        print(f"✅ SUCCESS! Commissions match expected value")
    else:
        print(f"⚠️ Slight difference: ${abs(total_commissions - 1326.73):,.2f}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_commissions())
