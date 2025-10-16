#!/usr/bin/env python3
"""Create Alejandro's missing investments in database"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

async def create_alejandro_investments():
    # Get MongoDB URL from environment
    mongo_url = os.environ.get('MONGO_URL')
    if not mongo_url:
        print("❌ MONGO_URL not found in environment")
        return
    
    client = AsyncIOMotorClient(mongo_url)
    db = client['fidus_production']
    
    # Alejandro's client ID
    client_id = "client_alejandro"
    
    # Investment 1: CORE Fund - $18,151.41
    core_deposit_date = datetime(2025, 10, 1, tzinfo=timezone.utc)
    core_investment = {
        "investment_id": "inv_alejandro_core_001",
        "client_id": client_id,
        "fund_code": "CORE",
        "principal_amount": 18151.41,
        "deposit_date": core_deposit_date,
        "incubation_end_date": core_deposit_date + relativedelta(months=2),
        "interest_start_date": core_deposit_date + relativedelta(months=2),
        "minimum_hold_end_date": core_deposit_date + relativedelta(months=14),
        "current_value": 18151.41,
        "total_interest_earned": 0.0,
        "status": "active",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    # Investment 2: BALANCE Fund - $100,000
    balance_deposit_date = datetime(2025, 10, 1, tzinfo=timezone.utc)
    balance_investment = {
        "investment_id": "inv_alejandro_balance_001",
        "client_id": client_id,
        "fund_code": "BALANCE",
        "principal_amount": 100000.00,
        "deposit_date": balance_deposit_date,
        "incubation_end_date": balance_deposit_date + relativedelta(months=2),
        "interest_start_date": balance_deposit_date + relativedelta(months=2),
        "minimum_hold_end_date": balance_deposit_date + relativedelta(months=14),
        "current_value": 100000.00,
        "total_interest_earned": 0.0,
        "status": "active",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    # Insert investments
    try:
        result1 = await db.investments.update_one(
            {"investment_id": core_investment["investment_id"]},
            {"$set": core_investment},
            upsert=True
        )
        print(f"✅ Created CORE investment: ${core_investment['principal_amount']:,.2f}")
        
        result2 = await db.investments.update_one(
            {"investment_id": balance_investment["investment_id"]},
            {"$set": balance_investment},
            upsert=True
        )
        print(f"✅ Created BALANCE investment: ${balance_investment['principal_amount']:,.2f}")
        
        # Verify
        count = await db.investments.count_documents({"client_id": client_id})
        print(f"\n✅ Total investments for Alejandro: {count}")
        
        # Show investments
        investments = await db.investments.find({"client_id": client_id}).to_list(length=10)
        print("\n📊 Alejandro's Investments:")
        for inv in investments:
            print(f"  - {inv['fund_code']}: ${inv['principal_amount']:,.2f} (current: ${inv['current_value']:,.2f})")
        
    except Exception as e:
        print(f"❌ Error creating investments: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(create_alejandro_investments())
