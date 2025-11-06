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

async def check_commissions():
    """Check all commission records"""
    
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    # Get Salvador's commissions
    salvador_id = "sp_6909e8eaaaf69606babea151"
    commissions = await db.referral_commissions.find({"salesperson_id": salvador_id}).sort("payment_date", 1).to_list(None)
    
    print(f"📊 SALVADOR'S COMMISSIONS: {len(commissions)} records")
    
    total_commissions = 0
    core_commissions = []
    balance_commissions = []
    
    for i, comm in enumerate(commissions, 1):
        amount = safe_decimal(comm.get('commission_amount', 0))
        total_commissions += amount
        
        fund_type = comm.get('fund_type', 'UNKNOWN')
        payment_date = comm.get('payment_date')
        
        if 'CORE' in fund_type.upper():
            core_commissions.append(amount)
        elif 'BALANCE' in fund_type.upper():
            balance_commissions.append(amount)
        
        print(f"\n{i}. {fund_type} - ${amount:,.2f}")
        print(f"   Payment Date: {payment_date}")
        print(f"   Status: {comm.get('status')}")
    
    print(f"\n{'='*60}")
    print(f"COMMISSION BREAKDOWN:")
    print(f"{'='*60}")
    print(f"CORE Commissions: {len(core_commissions)} payments, Total: ${sum(core_commissions):,.2f}")
    if core_commissions:
        print(f"  Average per payment: ${sum(core_commissions)/len(core_commissions):,.2f}")
    
    print(f"\nBALANCE Commissions: {len(balance_commissions)} payments, Total: ${sum(balance_commissions):,.2f}")
    if balance_commissions:
        print(f"  Average per payment: ${sum(balance_commissions)/len(balance_commissions):,.2f}")
    
    print(f"\nTOTAL COMMISSIONS: ${total_commissions:,.2f}")
    
    # Expected:
    print(f"\n{'='*60}")
    print(f"EXPECTED (from SYSTEM_MASTER.md):")
    print(f"{'='*60}")
    print(f"CORE: $27.23 × 12 = $326.76")
    print(f"BALANCE: $250 × 4 = $1,000.00")
    print(f"TOTAL: $1,326.76")
    
    print(f"\n{'='*60}")
    print(f"DISCREPANCY ANALYSIS:")
    print(f"{'='*60}")
    if total_commissions > 1326.76:
        print(f"❌ OVER by ${total_commissions - 1326.76:,.2f}")
        print(f"   Possible reasons:")
        print(f"   - Duplicate commission records")
        print(f"   - Incorrect commission rate (using more than 10%)")
        print(f"   - Commissions for full 14 months instead of 12 months")
    
    # Check Salvador's data
    salvador = await db.salespeople.find_one({"_id": salvador_id})
    if salvador:
        print(f"\n📋 SALVADOR'S STATS:")
        print(f"  Total Sales: ${safe_decimal(salvador.get('total_sales_volume', 0)):,.2f}")
        print(f"  Total Commissions: ${safe_decimal(salvador.get('total_commissions_earned', 0)):,.2f}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_commissions())
