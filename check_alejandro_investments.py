#!/usr/bin/env python3

import os
import sys
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

async def check_and_update_alejandro_investments():
    """Check Alejandro's investment dates and update if needed"""
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'fidus_production')]
    
    try:
        # Find all investments for Alejandro
        investments = await db.investments.find({'client_id': 'client_alejandro'}).to_list(length=None)
        
        print(f'Found {len(investments)} investments for Alejandro:')
        
        target_date = datetime(2025, 10, 1, 0, 0, 0, tzinfo=timezone.utc)
        
        for inv in investments:
            print(f"\nInvestment {inv['investment_id']}:")
            print(f"  Fund: {inv['fund_code']}")
            print(f"  Amount: ${inv['principal_amount']:,.2f}")
            print(f"  Current date: {inv.get('created_at', 'Unknown')}")
            
            # Update the investment date to October 1, 2025
            if inv.get('created_at') != target_date:
                print(f"  -> Updating to October 1, 2025")
                
                result = await db.investments.update_one(
                    {'investment_id': inv['investment_id']},
                    {
                        '$set': {
                            'created_at': target_date,
                            'updated_at': datetime.now(timezone.utc)
                        }
                    }
                )
                
                if result.modified_count > 0:
                    print(f"  ✅ Successfully updated investment {inv['investment_id']}")
                else:
                    print(f"  ❌ Failed to update investment {inv['investment_id']}")
            else:
                print(f"  ✅ Already has correct date")
        
        # Verify the updates
        print("\n" + "="*50)
        print("VERIFICATION - Updated investments:")
        updated_investments = await db.investments.find({'client_id': 'client_alejandro'}).to_list(length=None)
        
        for inv in updated_investments:
            print(f"  {inv['fund_code']}: ${inv['principal_amount']:,.2f} -> {inv.get('created_at')}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(check_and_update_alejandro_investments())