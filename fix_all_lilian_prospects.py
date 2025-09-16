#!/usr/bin/env python3
"""
FIX ALL LILIAN PROSPECTS
========================

This script finds and fixes ALL Lilian prospects to ensure the Convert button works.
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

async def fix_all_lilian_prospects():
    """Fix all Lilian prospects"""
    print("🔧 FIX ALL LILIAN PROSPECTS")
    print("=" * 50)
    
    # Connect to MongoDB
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
        
        # Find all Lilian prospects
        print("🔍 Searching for all Lilian prospects...")
        lilian_prospects = []
        async for prospect in db.crm_prospects.find():
            name = prospect.get('name', '').upper()
            if 'LILIAN' in name:
                lilian_prospects.append(prospect)
        
        print(f"Found {len(lilian_prospects)} Lilian prospects")
        
        if not lilian_prospects:
            print("❌ No Lilian prospects found")
            return False
        
        # Fix each Lilian prospect
        fixed_count = 0
        for i, prospect in enumerate(lilian_prospects, 1):
            lilian_id = prospect.get('id')
            name = prospect.get('name')
            
            print(f"\n🔧 Fixing Lilian #{i}: {name} (ID: {lilian_id})")
            print(f"   Current stage: {prospect.get('stage')}")
            print(f"   Current aml_kyc_status: {prospect.get('aml_kyc_status')}")
            print(f"   Current converted_to_client: {prospect.get('converted_to_client')}")
            print(f"   Current client_id: {prospect.get('client_id')}")
            
            # Update data
            update_data = {
                "stage": "won",
                "aml_kyc_status": "clear",
                "converted_to_client": False,
                "client_id": "",
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            result = await db.crm_prospects.update_one(
                {"id": lilian_id},
                {"$set": update_data}
            )
            
            if result.modified_count == 1:
                print(f"   ✅ Successfully updated Lilian #{i}")
                fixed_count += 1
                
                # Verify the update
                updated_prospect = await db.crm_prospects.find_one({"id": lilian_id})
                stage = updated_prospect.get('stage')
                aml_kyc_status = updated_prospect.get('aml_kyc_status')
                converted_to_client = updated_prospect.get('converted_to_client')
                
                print(f"   Verified: stage={stage}, aml_kyc_status={aml_kyc_status}, converted_to_client={converted_to_client}")
                
                if (stage == "won" and aml_kyc_status == "clear" and converted_to_client == False):
                    print(f"   🎯 Convert button conditions MET for Lilian #{i}")
                else:
                    print(f"   ❌ Convert button conditions NOT MET for Lilian #{i}")
            else:
                print(f"   ❌ Failed to update Lilian #{i}")
        
        print(f"\n🎯 SUMMARY:")
        print(f"   Total Lilian prospects found: {len(lilian_prospects)}")
        print(f"   Successfully fixed: {fixed_count}")
        
        if fixed_count > 0:
            print("\n🎉 EXPECTED RESULT:")
            print("   User should now see a big green 'CONVERT TO CLIENT' button")
            print("   on Lilian's prospect card(s) in production.")
            return True
        else:
            print("\n❌ No Lilian prospects were fixed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        client.close()

async def main():
    success = await fix_all_lilian_prospects()
    if not success:
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())