import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

async def test_cash_flow():
    """Test cash flow calculation after fix"""
    
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    # Get all investments
    investments = await db.investments.find({"status": "active"}).to_list(None)
    
    print(f"📊 ACTIVE INVESTMENTS: {len(investments)}")
    
    total_obligations = 0
    
    for inv in investments:
        fund_type = inv.get('fund_type')
        principal = float(inv.get('principal_amount', 0))
        interest_rate = float(inv.get('interest_rate', 0))
        first_payment = inv.get('first_payment_date')
        
        print(f"\n{'='*60}")
        print(f"Fund: {fund_type}")
        print(f"Principal: ${principal:,.2f}")
        print(f"Interest Rate: {interest_rate*100:.2f}%")
        print(f"First Payment: {first_payment}")
        
        if fund_type == "CORE":
            # Monthly: 1.5% per month, 12 payments
            monthly_interest = principal * interest_rate
            total_interest = monthly_interest * 12
            commission_per_month = monthly_interest * 0.10
            total_commission = commission_per_month * 12
            
            print(f"Monthly Interest: ${monthly_interest:,.2f}")
            print(f"Total Interest (12 months): ${total_interest:,.2f}")
            print(f"Commission per Month: ${commission_per_month:,.2f}")
            print(f"Total Commission: ${total_commission:,.2f}")
            
            total_obligations += total_interest
            
        elif fund_type == "BALANCE":
            # Quarterly: 2.5% per quarter (3 months), 4 payments
            quarterly_interest = principal * interest_rate
            total_interest = quarterly_interest * 4
            commission_per_quarter = quarterly_interest * 0.10
            total_commission = commission_per_quarter * 4
            
            print(f"Quarterly Interest: ${quarterly_interest:,.2f}")
            print(f"Total Interest (4 quarters): ${total_interest:,.2f}")
            print(f"Commission per Quarter: ${commission_per_quarter:,.2f}")
            print(f"Total Commission: ${total_commission:,.2f}")
            
            total_obligations += total_interest
    
    print(f"\n{'='*60}")
    print(f"TOTAL CLIENT OBLIGATIONS (Interest Only): ${total_obligations:,.2f}")
    print(f"{'='*60}")
    
    # Expected values from SYSTEM_MASTER.md
    print(f"\n✓ EXPECTED VALUES:")
    print(f"  CORE Interest: $272.27 × 12 = $3,267.24")
    print(f"  BALANCE Interest: $2,500 × 4 = $10,000.00")
    print(f"  TOTAL: $13,267.24")
    
    print(f"\n✓ COMMISSION VALUES (10%):")
    print(f"  CORE: $27.23 × 12 = $326.72")
    print(f"  BALANCE: $250 × 4 = $1,000.00")
    print(f"  TOTAL: $1,326.72")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(test_cash_flow())
