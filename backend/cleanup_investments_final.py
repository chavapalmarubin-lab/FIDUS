import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv('/app/backend/.env')

async def cleanup():
    """Final cleanup of investments"""
    
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    print("🔍 BEFORE CLEANUP:")
    investments = await db.investments.find({}).to_list(None)
    for i, inv in enumerate(investments, 1):
        print(f"  {i}. {inv.get('fund_type')} - ${inv.get('principal_amount', inv.get('amount', 0))} - Interest: {inv.get('interest_rate', 0)}")
    
    # Delete ALL existing investments
    result = await db.investments.delete_many({})
    print(f"\n🗑️ Deleted {result.deleted_count} investments")
    
    # Create ONLY TWO correct investments
    start_date = datetime(2025, 10, 1)
    
    # CORE Investment
    core_investment = {
        "investment_id": "inv_alejandro_core_001",
        "client_id": "6909e8ebaaf69606babea152",
        "client_name": "Alejandro Mariscal Romero",
        "fund_type": "CORE",
        "product": "FIDUS_CORE",
        "principal_amount": 18151.41,
        "amount": 18151.41,
        "initial_amount": 18151.41,
        "interest_rate": 0.015,  # 1.5% monthly
        "payment_frequency": "monthly",
        "start_date": start_date,
        "investment_date": start_date,
        "first_payment_date": start_date + timedelta(days=90),  # Dec 30, 2025
        "incubation_end_date": start_date + timedelta(days=60),  # Nov 30, 2025
        "contract_end_date": start_date + timedelta(days=426),  # Dec 1, 2026
        "contract_months": 14,
        "status": "active",
        "salesperson_id": "sp_6909e8eaaaf69606babea151",
        "referral_salesperson_id": "sp_6909e8eaaaf69606babea151",
        "referred_by_name": "Salvador Palma",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # BALANCE Investment
    balance_investment = {
        "investment_id": "inv_alejandro_balance_001",
        "client_id": "6909e8ebaaf69606babea152",
        "client_name": "Alejandro Mariscal Romero",
        "fund_type": "BALANCE",
        "product": "FIDUS_BALANCE",
        "principal_amount": 100000.00,
        "amount": 100000.00,
        "initial_amount": 100000.00,
        "interest_rate": 0.025,  # 2.5% quarterly
        "payment_frequency": "quarterly",
        "start_date": start_date,
        "investment_date": start_date,
        "first_payment_date": start_date + timedelta(days=150),  # Feb 28, 2026
        "incubation_end_date": start_date + timedelta(days=60),  # Nov 30, 2025
        "contract_end_date": start_date + timedelta(days=426),  # Dec 1, 2026
        "contract_months": 14,
        "status": "active",
        "salesperson_id": "sp_6909e8eaaaf69606babea151",
        "referral_salesperson_id": "sp_6909e8eaaaf69606babea151",
        "referred_by_name": "Salvador Palma",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert both
    result = await db.investments.insert_many([core_investment, balance_investment])
    print(f"\n✅ Created {len(result.inserted_ids)} investments")
    
    # Verify
    print(f"\n{'='*60}")
    print(f"AFTER CLEANUP:")
    print(f"{'='*60}")
    
    investments = await db.investments.find({}).to_list(None)
    
    for inv in investments:
        print(f"\n✓ {inv['fund_type']} FUND:")
        print(f"  Principal: ${inv['principal_amount']:,.2f}")
        print(f"  Interest Rate: {inv['interest_rate']*100:.2f}%")
        print(f"  Start: {inv['start_date'].date()}")
        print(f"  First Payment: {inv['first_payment_date'].date()}")
        print(f"  Salesperson ID: {inv.get('salesperson_id')}")
    
    # Calculate totals
    print(f"\n{'='*60}")
    print(f"FINANCIAL SUMMARY:")
    print(f"{'='*60}")
    
    core_monthly = 18151.41 * 0.015
    core_total = core_monthly * 12
    core_commission = core_monthly * 0.10 * 12
    
    balance_quarterly = 100000 * 0.025
    balance_total = balance_quarterly * 4
    balance_commission = balance_quarterly * 0.10 * 4
    
    print(f"\nCORE Fund:")
    print(f"  Monthly Interest: ${core_monthly:,.2f}")
    print(f"  Total Interest (12 months): ${core_total:,.2f}")
    print(f"  Total Commission (10%): ${core_commission:,.2f}")
    
    print(f"\nBALANCE Fund:")
    print(f"  Quarterly Interest: ${balance_quarterly:,.2f}")
    print(f"  Total Interest (4 quarters): ${balance_total:,.2f}")
    print(f"  Total Commission (10%): ${balance_commission:,.2f}")
    
    print(f"\nTOTALS:")
    print(f"  Total Investment: $118,151.41")
    print(f"  Total Interest: ${core_total + balance_total:,.2f}")
    print(f"  Total Commission: ${core_commission + balance_commission:,.2f}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(cleanup())
