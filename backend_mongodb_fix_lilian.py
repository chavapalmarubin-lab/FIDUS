#!/usr/bin/env python3
"""
BACKEND MONGODB FIX FOR LILIAN
==============================

This script uses the same MongoDB connection as the backend to fix Lilian's data.
"""

import sys
import os
sys.path.append('/app/backend')

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path('/app/backend')
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection (same as backend)
mongo_url = os.environ['MONGO_URL']
db_name = os.environ.get('DB_NAME', 'fidus_investment_db')

async def fix_lilian_data():
    """Fix Lilian's data using backend MongoDB connection"""
    print("🔧 BACKEND MONGODB FIX FOR LILIAN")
    print("=" * 50)
    print(f"MongoDB URL: {mongo_url}")
    print(f"Database: {db_name}")
    print()
    
    # Connect to MongoDB (same as backend)
    client = AsyncIOMotorClient(
        mongo_url,
        minPoolSize=5,
        maxPoolSize=100,
        maxIdleTimeMS=30000,
        serverSelectionTimeoutMS=5000,
        socketTimeoutMS=10000,
        connectTimeoutMS=10000,
        retryWrites=True
    )
    db = client[db_name]
    
    try:
        # Test connection
        await db.command('ping')
        print("✅ Connected to MongoDB")
        
        # List all prospects to find Lilian
        print("🔍 Searching for all prospects...")
        prospects = []
        async for prospect in db.crm_prospects.find():
            prospects.append(prospect)
        
        print(f"Found {len(prospects)} prospects total")
        
        # Find Lilian
        lilian_prospect = None
        for prospect in prospects:
            name = prospect.get('name', '').upper()
            if 'LILIAN' in name:
                lilian_prospect = prospect
                break
        
        if not lilian_prospect:
            print("❌ Lilian not found in MongoDB")
            print("Available prospects:")
            for prospect in prospects:
                print(f"   - {prospect.get('name')} (ID: {prospect.get('id')})")
            return False
        
        print(f"✅ Found Lilian: {lilian_prospect.get('name')}")
        print(f"   ID: {lilian_prospect.get('id')}")
        print(f"   Current stage: {lilian_prospect.get('stage')}")
        print(f"   Current aml_kyc_status: {lilian_prospect.get('aml_kyc_status')}")
        print(f"   Current converted_to_client: {lilian_prospect.get('converted_to_client')}")
        print(f"   Current client_id: {lilian_prospect.get('client_id')}")
        print()
        
        # Update Lilian's data to correct values
        lilian_id = lilian_prospect.get('id')
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
        
        print(f"Update result: matched={result.matched_count}, modified={result.modified_count}")
        
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
        import traceback
        traceback.print_exc()
        return False
    finally:
        client.close()

async def main():
    success = await fix_lilian_data()
    if not success:
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())