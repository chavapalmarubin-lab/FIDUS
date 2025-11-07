import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from bson import Decimal128
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

def safe_decimal(value):
    if isinstance(value, Decimal128):
        return float(value.to_decimal())
    return float(value) if value else 0.0

async def check():
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    salvador_id = "sp_6909e8eaaaf69606babea151"
    
    print("="*80)
    print("CHECKING COMMISSION RECORDS FOR CALENDAR")
    print("="*80)
    print()
    
    # Get all commissions
    commissions = await db.referral_commissions.find({
        "salesperson_id": salvador_id
    }).sort("payment_date", 1).to_list(None)
    
    print(f"Total commission records: {len(commissions)}")
    print()
    
    if len(commissions) == 0:
        print("❌ NO COMMISSION RECORDS FOUND!")
        print("This is why the calendar is empty.")
        return
    
    # Check first few
    print("First 5 commission records:")
    print("-"*80)
    for i, comm in enumerate(commissions[:5], 1):
        amount = safe_decimal(comm.get('commission_amount', 0))
        payment_date = comm.get('payment_date')
        status = comm.get('status')
        fund = comm.get('fund_type', 'N/A')
        client = comm.get('client_name', 'N/A')
        
        print(f"{i}. {fund} - {client}")
        print(f"   Date: {payment_date}")
        print(f"   Amount: ${amount:,.2f}")
        print(f"   Status: {status}")
        print()
    
    # Check by status
    pending = [c for c in commissions if c.get('status') == 'pending']
    paid = [c for c in commissions if c.get('status') == 'paid']
    
    print(f"Pending: {len(pending)}")
    print(f"Paid: {len(paid)}")
    print()
    
    # Check date range
    if commissions:
        first_date = commissions[0].get('payment_date')
        last_date = commissions[-1].get('payment_date')
        print(f"Date range: {first_date} to {last_date}")
    
    client.close()

asyncio.run(check())
