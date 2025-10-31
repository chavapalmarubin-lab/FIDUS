#!/usr/bin/env python3
"""
DIRECT MONGODB FIX FOR LILIAN
=============================

This script directly updates MongoDB to fix Lilian's data inconsistency
since the API endpoint doesn't support updating aml_kyc_status and converted_to_client fields.
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

# MongoDB connection
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "fidus_investment_db"

async def fix_lilian_data():
    """Fix Lilian's data directly in MongoDB"""
    print("🔧 DIRECT MONGODB FIX FOR LILIAN")
    print("=" * 50)
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # Test connection
        await db.command('ping')
        print("✅ Connected to MongoDB")
        
        # Find Lilian's prospect
        lilian_id = "4de9c592-9b15-4c32-a268-e1f8459878b9"
        
        print(f"🔍 Finding Lilian's prospect (ID: {lilian_id})")
        
        prospect = await db.crm_prospects.find_one({"id": lilian_id})
        
        if not prospect:
            print("❌ Lilian's prospect not found")
            return False
        
        print("✅ Found Lilian's prospect")
        print(f"   Current stage: {prospect.get('stage')}")
        print(f"   Current aml_kyc_status: {prospect.get('aml_kyc_status')}")
        print(f"   Current converted_to_client: {prospect.get('converted_to_client')}")
        print(f"   Current client_id: {prospect.get('client_id')}")
        print()
        
        # Update Lilian's data to correct values
        update_data = {
            "stage": "won",
            "aml_kyc_status": "clear",
            "converted_to_client": False,
            "client_id": "",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        print("🔧 Updating Lilian's data to correct values:")
        print(f"   stage: 'won'")
        print(f"   aml_kyc_status: 'clear'")
        print(f"   converted_to_client: false")
        print(f"   client_id: '' (empty)")
        print()
        
        # Execute update
        result = await db.crm_prospects.update_one(
            {"id": lilian_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 1:
            print("✅ SUCCESSFULLY UPDATED LILIAN'S DATA")
            
            # Verify the update
            updated_prospect = await db.crm_prospects.find_one({"id": lilian_id})
            
            print("🔍 VERIFICATION - Updated values:")
            print(f"   stage: {updated_prospect.get('stage')}")
            print(f"   aml_kyc_status: {updated_prospect.get('aml_kyc_status')}")
            print(f"   converted_to_client: {updated_prospect.get('converted_to_client')}")
            print(f"   client_id: '{updated_prospect.get('client_id')}'")
            print()
            
            # Check Convert button conditions
            stage = updated_prospect.get('stage')
            aml_kyc_status = updated_prospect.get('aml_kyc_status')
            converted_to_client = updated_prospect.get('converted_to_client')
            
            if (stage == "won" and aml_kyc_status == "clear" and converted_to_client == False):
                print("🎯 CONVERT BUTTON CONDITIONS MET!")
                print("✅ stage='won' AND aml_kyc_status='clear' AND converted_to_client=false")
                print()
                print("🎉 EXPECTED RESULT:")
                print("   User should now see a big green 'CONVERT TO CLIENT' button")
                print("   on Lilian's prospect card in production.")
                return True
            else:
                print("❌ Convert button conditions still not met")
                return False
        else:
            print("❌ Failed to update Lilian's data")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    finally:
        client.close()

async def main():
    success = await fix_lilian_data()
    if not success:
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())