import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

async def fix_balance_date():
    """Fix Alejandro's BALANCE first payment date"""
    
    # Connect to MongoDB
    mongo_url = os.getenv('MONGO_URL')
    print(f"Connecting to MongoDB...")
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    # Find Alejandro's BALANCE investment
    balance_investment = await db.investments.find_one({
        "client_name": "Alejandro Mariscal Romero",
        "fund_type": "BALANCE"
    })
    
    if not balance_investment:
        print("❌ BALANCE investment not found!")
        return
    
    print(f"\n📊 CURRENT DATA:")
    print(f"Start Date: {balance_investment.get('start_date')}")
    print(f"First Payment Date: {balance_investment.get('first_payment_date')}")
    print(f"Investment Date: {balance_investment.get('investment_date')}")
    
    # Calculate correct first payment date
    # October 1, 2025 + 150 days = February 28, 2026
    start_date = datetime(2025, 10, 1)
    correct_first_payment = start_date + timedelta(days=150)
    incubation_end = start_date + timedelta(days=60)
    
    print(f"\n✅ CORRECT CALCULATION:")
    print(f"Start Date: October 1, 2025")
    print(f"Incubation (60 days): Ends November 30, 2025")
    print(f"First Payment (+ 90 days): February 28, 2026")
    print(f"Total: 150 days from start")
    
    # Update the database
    result = await db.investments.update_one(
        {
            "client_name": "Alejandro Mariscal Romero",
            "fund_type": "BALANCE"
        },
        {
            "$set": {
                "start_date": start_date,
                "investment_date": start_date,
                "first_payment_date": correct_first_payment,
                "incubation_end_date": incubation_end
            }
        }
    )
    
    print(f"\n🔧 UPDATE RESULT:")
    print(f"Matched: {result.matched_count}")
    print(f"Modified: {result.modified_count}")
    
    # Verify the update
    updated = await db.investments.find_one({
        "client_name": "Alejandro Mariscal Romero",
        "fund_type": "BALANCE"
    })
    
    print(f"\n✓ VERIFICATION:")
    print(f"Start Date: {updated.get('start_date')}")
    print(f"Incubation End: {updated.get('incubation_end_date')}")
    print(f"First Payment: {updated.get('first_payment_date')}")
    
    if updated.get('first_payment_date') == correct_first_payment:
        print("\n✅ SUCCESS! First payment date is now correct: February 28, 2026")
    else:
        print(f"\n❌ FAILED! Date is: {updated.get('first_payment_date')}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_balance_date())
