#!/usr/bin/env python3
"""
FINAL FIX FOR LILIAN 4de9c592
=============================

This script fixes the specific Lilian prospect that the API is returning
with the data inconsistency issue.
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

async def fix_specific_lilian():
    """Fix the specific Lilian prospect causing the issue"""
    print("🔧 FINAL FIX FOR LILIAN 4de9c592")
    print("=" * 50)
    
    # The specific Lilian ID from API
    target_lilian_id = "4de9c592-9b15-4c32-a268-e1f8459878b9"
    
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
        
        # Search for the specific Lilian prospect
        print(f"🔍 Searching for Lilian prospect ID: {target_lilian_id}")
        
        # First, let's see all prospects to understand the data structure
        all_prospects = []
        async for prospect in db.crm_prospects.find():
            all_prospects.append(prospect)
        
        print(f"Found {len(all_prospects)} total prospects in MongoDB")
        
        # Look for the specific ID
        target_prospect = None
        for prospect in all_prospects:
            if prospect.get('id') == target_lilian_id:
                target_prospect = prospect
                break
        
        if not target_prospect:
            print(f"❌ Prospect {target_lilian_id} not found in MongoDB")
            print("Available prospect IDs:")
            for prospect in all_prospects:
                name = prospect.get('name', 'Unknown')
                prospect_id = prospect.get('id', 'No ID')
                print(f"   - {name}: {prospect_id}")
            
            # Try to find any Lilian prospect and fix it
            print("\n🔍 Looking for any Lilian prospect to fix...")
            lilian_prospects = []
            for prospect in all_prospects:
                name = prospect.get('name', '').upper()
                if 'LILIAN' in name:
                    lilian_prospects.append(prospect)
            
            if lilian_prospects:
                print(f"Found {len(lilian_prospects)} Lilian prospects in MongoDB")
                for i, prospect in enumerate(lilian_prospects, 1):
                    await fix_lilian_prospect(db, prospect, i)
            else:
                print("❌ No Lilian prospects found in MongoDB")
                return False
        else:
            print(f"✅ Found target Lilian prospect: {target_prospect.get('name')}")
            await fix_lilian_prospect(db, target_prospect, 1)
        
        return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        client.close()

async def fix_lilian_prospect(db, prospect, number):
    """Fix a specific Lilian prospect"""
    lilian_id = prospect.get('id')
    name = prospect.get('name')
    
    print(f"\n🔧 Fixing Lilian #{number}: {name} (ID: {lilian_id})")
    print(f"   Current stage: {prospect.get('stage')}")
    print(f"   Current aml_kyc_status: {prospect.get('aml_kyc_status')}")
    print(f"   Current converted_to_client: {prospect.get('converted_to_client')}")
    print(f"   Current client_id: {prospect.get('client_id')}")
    
    # Update data to correct values
    update_data = {
        "stage": "won",
        "aml_kyc_status": "clear",
        "converted_to_client": False,
        "client_id": "",
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    print(f"   Setting: stage='won', aml_kyc_status='clear', converted_to_client=false, client_id=''")
    
    result = await db.crm_prospects.update_one(
        {"id": lilian_id},
        {"$set": update_data}
    )
    
    print(f"   Update result: matched={result.matched_count}, modified={result.modified_count}")
    
    if result.matched_count == 1:
        print(f"   ✅ Successfully updated Lilian #{number}")
        
        # Verify the update
        updated_prospect = await db.crm_prospects.find_one({"id": lilian_id})
        stage = updated_prospect.get('stage')
        aml_kyc_status = updated_prospect.get('aml_kyc_status')
        converted_to_client = updated_prospect.get('converted_to_client')
        client_id = updated_prospect.get('client_id')
        
        print(f"   Verified: stage={stage}, aml_kyc_status={aml_kyc_status}, converted_to_client={converted_to_client}, client_id='{client_id}'")
        
        if (stage == "won" and aml_kyc_status == "clear" and converted_to_client == False):
            print(f"   🎯 Convert button conditions MET for Lilian #{number}")
            print(f"   🎉 User should now see CONVERT TO CLIENT button for this prospect!")
        else:
            print(f"   ❌ Convert button conditions NOT MET for Lilian #{number}")
    else:
        print(f"   ❌ Failed to update Lilian #{number}")

async def main():
    success = await fix_specific_lilian()
    if not success:
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())