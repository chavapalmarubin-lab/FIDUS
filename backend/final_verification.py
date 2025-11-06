import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import Decimal128
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

def safe_decimal(value):
    """Safely convert Decimal128 to float"""
    if isinstance(value, Decimal128):
        return float(value.to_decimal())
    return float(value) if value else 0.0

async def verify():
    """Final verification of all data"""
    
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    salvador_id = "sp_6909e8eaaaf69606babea151"
    
    # Get all commissions
    commissions = await db.referral_commissions.find({"salesperson_id": salvador_id}).sort("payment_date", 1).to_list(None)
    
    print("="*60)
    print("FINAL COMMISSION VERIFICATION")
    print("="*60)
    
    core_total = 0
    balance_total = 0
    
    print("\nCORE COMMISSIONS (Monthly):")
    for i, comm in enumerate([c for c in commissions if 'CORE' in c.get('fund_type', '')], 1):
        amount = safe_decimal(comm.get('commission_amount'))
        interest = safe_decimal(comm.get('client_interest_amount'))
        date = comm.get('payment_date')
        core_total += amount
        print(f"  {i}. {date.strftime('%b %d, %Y')}: Interest ${interest:,.2f} → Commission ${amount:,.2f}")
    
    print(f"\n  CORE TOTAL: ${core_total:,.2f}")
    
    print("\nBALANCE COMMISSIONS (Quarterly):")
    for i, comm in enumerate([c for c in commissions if 'BALANCE' in c.get('fund_type', '')], 1):
        amount = safe_decimal(comm.get('commission_amount'))
        interest = safe_decimal(comm.get('client_interest_amount'))
        date = comm.get('payment_date')
        balance_total += amount
        print(f"  {i}. {date.strftime('%b %d, %Y')}: Interest ${interest:,.2f} → Commission ${amount:,.2f}")
    
    print(f"\n  BALANCE TOTAL: ${balance_total:,.2f}")
    
    total = core_total + balance_total
    
    print("\n" + "="*60)
    print(f"TOTAL COMMISSIONS: ${total:,.2f}")
    print("="*60)
    
    print("\n✓ EXPECTED VALUES:")
    print(f"  CORE: $326.73")
    print(f"  BALANCE: $3,000.00")
    print(f"  TOTAL: $3,326.73")
    
    if abs(core_total - 326.73) < 0.10:
        print(f"\n✅ CORE commissions CORRECT")
    else:
        print(f"\n❌ CORE commissions WRONG (off by ${abs(core_total - 326.73):,.2f})")
    
    if abs(balance_total - 3000.00) < 0.10:
        print(f"✅ BALANCE commissions CORRECT")
    else:
        print(f"❌ BALANCE commissions WRONG (off by ${abs(balance_total - 3000.00):,.2f})")
    
    if abs(total - 3326.73) < 0.10:
        print(f"✅ TOTAL commissions CORRECT")
    else:
        print(f"❌ TOTAL commissions WRONG (off by ${abs(total - 3326.73):,.2f})")
    
    # Check Salvador's record
    salvador = await db.salespeople.find_one({"_id": salvador_id})
    if salvador:
        salvador_total = safe_decimal(salvador.get('total_commissions', 0))
        print(f"\n📋 SALVADOR'S RECORD:")
        print(f"  Total Commissions: ${salvador_total:,.2f}")
        if abs(salvador_total - 3326.73) < 0.10:
            print(f"  ✅ Matches commission records")
        else:
            print(f"  ❌ Does not match (off by ${abs(salvador_total - 3326.73):,.2f})")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(verify())
