#!/usr/bin/env python3
"""
Fix Alejandro's setup for testing
1. Update email to alexmar7609@gmail.com if needed
2. Create client_readiness record
"""

import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment variables
load_dotenv('/app/backend/.env')

async def fix_alejandro_setup():
    """Fix Alejandro's setup for testing"""
    
    print("🔧 FIXING ALEJANDRO'S SETUP FOR TESTING")
    print("="*80)
    
    try:
        # Connect to MongoDB
        mongo_url = os.environ.get('MONGO_URL')
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ.get('DB_NAME', 'fidus_production')]
        
        print(f"✅ Connected to database: {db.name}")
        
        # 1. Update Alejandro's email if needed
        print(f"\n📧 UPDATING ALEJANDRO'S EMAIL")
        print("-" * 40)
        
        current_user = await db.users.find_one({"id": "client_alejandro"})
        if current_user:
            current_email = current_user.get('email')
            target_email = 'alexmar7609@gmail.com'
            
            if current_email != target_email:
                print(f"📧 Current email: {current_email}")
                print(f"📧 Target email: {target_email}")
                print(f"🔄 Updating email...")
                
                result = await db.users.update_one(
                    {"id": "client_alejandro"},
                    {"$set": {"email": target_email}}
                )
                
                if result.modified_count > 0:
                    print(f"✅ Email updated successfully")
                else:
                    print(f"❌ Failed to update email")
            else:
                print(f"✅ Email already correct: {current_email}")
        else:
            print(f"❌ Alejandro user not found")
            return
        
        # 2. Create client_readiness record
        print(f"\n📋 CREATING CLIENT_READINESS RECORD")
        print("-" * 40)
        
        existing_readiness = await db.client_readiness.find_one({"client_id": "client_alejandro"})
        
        if existing_readiness:
            print(f"✅ Client readiness record already exists")
            print(f"   Investment Ready: {existing_readiness.get('investment_ready')}")
            print(f"   Override: {existing_readiness.get('readiness_override')}")
        else:
            print(f"🔄 Creating new client_readiness record...")
            
            readiness_record = {
                "client_id": "client_alejandro",
                "aml_kyc_completed": True,
                "agreement_signed": True,
                "account_creation_date": datetime.now(timezone.utc),
                "investment_ready": True,
                "notes": "Created for testing - Alejandro Mariscal Romero",
                "updated_at": datetime.now(timezone.utc),
                "updated_by": "system_setup",
                "readiness_override": False,
                "readiness_override_reason": "",
                "readiness_override_by": "",
                "readiness_override_date": None
            }
            
            result = await db.client_readiness.insert_one(readiness_record)
            
            if result.inserted_id:
                print(f"✅ Client readiness record created successfully")
                print(f"   ID: {result.inserted_id}")
                print(f"   Investment Ready: True")
            else:
                print(f"❌ Failed to create client readiness record")
        
        # 3. Verify the setup
        print(f"\n🔍 VERIFYING SETUP")
        print("-" * 40)
        
        # Check user record
        updated_user = await db.users.find_one({"id": "client_alejandro"})
        if updated_user:
            print(f"✅ User record verified:")
            print(f"   ID: {updated_user.get('id')}")
            print(f"   Email: {updated_user.get('email')}")
            print(f"   Name: {updated_user.get('name')}")
        
        # Check readiness record
        readiness = await db.client_readiness.find_one({"client_id": "client_alejandro"})
        if readiness:
            print(f"✅ Readiness record verified:")
            print(f"   Client ID: {readiness.get('client_id')}")
            print(f"   Investment Ready: {readiness.get('investment_ready')}")
            print(f"   AML/KYC: {readiness.get('aml_kyc_completed')}")
            print(f"   Agreement: {readiness.get('agreement_signed')}")
        
        # Check investments
        investment_count = await db.investments.count_documents({"client_id": "client_alejandro"})
        print(f"✅ Investments found: {investment_count}")
        
        # 4. Summary
        print(f"\n" + "="*80)
        print("📊 ALEJANDRO SETUP SUMMARY")
        print("="*80)
        
        print(f"🎯 CLIENT ID: client_alejandro")
        print(f"📧 EMAIL: {updated_user.get('email') if updated_user else 'ERROR'}")
        print(f"📛 NAME: {updated_user.get('name') if updated_user else 'ERROR'}")
        print(f"✅ READINESS RECORD: {'Created/Exists' if readiness else 'Missing'}")
        print(f"💰 INVESTMENTS: {investment_count} found")
        
        print(f"\n📋 READY FOR TESTING:")
        print(f"   - Use client_id: 'client_alejandro'")
        print(f"   - Use email: '{updated_user.get('email') if updated_user else 'ERROR'}'")
        print(f"   - Investment ready: {readiness.get('investment_ready') if readiness else False}")
        
    except Exception as e:
        print(f"❌ Error during setup: {str(e)}")

if __name__ == "__main__":
    asyncio.run(fix_alejandro_setup())