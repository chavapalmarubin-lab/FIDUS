import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

async def check_commissions():
    """Check all commission records"""
    
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    # Get Salvador's commissions
    salvador_id = "sp_6909e8eaaaf69606babea151"
    commissions = await db.referral_commissions.find({"salesperson_id": salvador_id}).to_list(None)
    
    print(f"📊 SALVADOR'S COMMISSIONS: {len(commissions)} records")
    
    total_commissions = 0
    
    for i, comm in enumerate(commissions, 1):
        amount = float(comm.get('commission_amount', 0))
        total_commissions += amount
        
        print(f"\n{i}. {comm.get('fund_type')} - ${amount:,.2f}")
        print(f"   Payment Date: {comm.get('payment_date')}")
        print(f"   Status: {comm.get('status')}")
        print(f"   Period: {comm.get('period_start')} to {comm.get('period_end')}")
    
    print(f"\n{'='*60}")
    print(f"TOTAL COMMISSIONS: ${total_commissions:,.2f}")
    print(f"{'='*60}")
    
    # Expected:
    print(f"\n✓ EXPECTED (from SYSTEM_MASTER.md):")
    print(f"  CORE: $27.23 × 12 = $326.76")
    print(f"  BALANCE: $250 × 4 = $1,000.00")
    print(f"  TOTAL: $1,326.76")
    
    # Check if there are old duplicate commissions
    all_sps = await db.salespeople.find({}).to_list(None)
    print(f"\n📋 ALL SALESPEOPLE:")
    for sp in all_sps:
        print(f"  - {sp.get('name')}: ${sp.get('total_commissions_earned', 0):,.2f}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_commissions())
