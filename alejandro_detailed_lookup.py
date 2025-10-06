#!/usr/bin/env python3
"""
Detailed Alejandro Client ID and Readiness Lookup
"""

import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

async def detailed_alejandro_lookup():
    """Detailed lookup for Alejandro's records"""
    
    print("🔍 DETAILED ALEJANDRO LOOKUP")
    print("="*80)
    
    try:
        # Connect to MongoDB
        mongo_url = os.environ.get('MONGO_URL')
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ.get('DB_NAME', 'fidus_production')]
        
        print(f"✅ Connected to database: {db.name}")
        
        # 1. Find Alejandro in users collection
        print(f"\n📋 SEARCHING USERS COLLECTION")
        print("-" * 40)
        
        user_queries = [
            {"email": "alexmar7609@gmail.com"},
            {"email": "alejandro.mariscal@email.com"},
            {"id": "client_alejandro"},
            {"username": "alejandro_mariscal"},
            {"name": {"$regex": "Alejandro", "$options": "i"}}
        ]
        
        alejandro_user = None
        for query in user_queries:
            user = await db.users.find_one(query)
            if user:
                alejandro_user = user
                print(f"✅ Found Alejandro in users collection:")
                print(f"   ID: {user.get('id')}")
                print(f"   Username: {user.get('username')}")
                print(f"   Name: {user.get('name')}")
                print(f"   Email: {user.get('email')}")
                print(f"   Type: {user.get('type')}")
                print(f"   Status: {user.get('status')}")
                print(f"   Phone: {user.get('phone')}")
                print(f"   Created: {user.get('created_at')}")
                break
        
        if not alejandro_user:
            print("❌ Alejandro not found in users collection")
            return
        
        alejandro_id = alejandro_user.get('id')
        
        # 2. Check client_readiness collection
        print(f"\n📋 SEARCHING CLIENT_READINESS COLLECTION")
        print("-" * 40)
        
        readiness_queries = [
            {"client_id": alejandro_id},
            {"client_id": "client_alejandro"},
            {"client_id": {"$regex": "alejandro", "$options": "i"}}
        ]
        
        alejandro_readiness = None
        for query in readiness_queries:
            readiness = await db.client_readiness.find_one(query)
            if readiness:
                alejandro_readiness = readiness
                print(f"✅ Found Alejandro in client_readiness collection:")
                print(f"   Client ID: {readiness.get('client_id')}")
                print(f"   Investment Ready: {readiness.get('investment_ready')}")
                print(f"   AML/KYC Completed: {readiness.get('aml_kyc_completed')}")
                print(f"   Agreement Signed: {readiness.get('agreement_signed')}")
                print(f"   Override: {readiness.get('readiness_override')}")
                print(f"   Override Reason: {readiness.get('readiness_override_reason')}")
                print(f"   Updated At: {readiness.get('updated_at')}")
                print(f"   Updated By: {readiness.get('updated_by')}")
                break
        
        if not alejandro_readiness:
            print("❌ Alejandro not found in client_readiness collection")
            
            # Check all readiness records to see what's there
            print(f"\n📋 ALL CLIENT_READINESS RECORDS:")
            print("-" * 40)
            
            async for readiness in db.client_readiness.find():
                print(f"   Client ID: {readiness.get('client_id')}")
                print(f"   Investment Ready: {readiness.get('investment_ready')}")
                print(f"   Override: {readiness.get('readiness_override')}")
                print(f"   ---")
        
        # 3. Check investments collection
        print(f"\n📋 SEARCHING INVESTMENTS COLLECTION")
        print("-" * 40)
        
        investment_queries = [
            {"client_id": alejandro_id},
            {"client_id": "client_alejandro"}
        ]
        
        alejandro_investments = []
        for query in investment_queries:
            async for investment in db.investments.find(query):
                alejandro_investments.append(investment)
        
        if alejandro_investments:
            print(f"✅ Found {len(alejandro_investments)} investment(s) for Alejandro:")
            for inv in alejandro_investments:
                print(f"   Investment ID: {inv.get('investment_id')}")
                print(f"   Fund Code: {inv.get('fund_code')}")
                print(f"   Amount: ${inv.get('principal_amount', 0):,.2f}")
                print(f"   Status: {inv.get('status')}")
                print(f"   Created: {inv.get('created_at')}")
                print(f"   ---")
        else:
            print("❌ No investments found for Alejandro")
        
        # 4. Check prospects collection (CRM)
        print(f"\n📋 SEARCHING CRM_PROSPECTS COLLECTION")
        print("-" * 40)
        
        prospect_queries = [
            {"email": "alexmar7609@gmail.com"},
            {"email": "alejandro.mariscal@email.com"},
            {"name": {"$regex": "Alejandro", "$options": "i"}},
            {"client_id": alejandro_id}
        ]
        
        alejandro_prospects = []
        for query in prospect_queries:
            async for prospect in db.crm_prospects.find(query):
                alejandro_prospects.append(prospect)
        
        if alejandro_prospects:
            print(f"✅ Found {len(alejandro_prospects)} prospect record(s) for Alejandro:")
            for prospect in alejandro_prospects:
                print(f"   Prospect ID: {prospect.get('prospect_id')}")
                print(f"   Name: {prospect.get('name')}")
                print(f"   Email: {prospect.get('email')}")
                print(f"   Stage: {prospect.get('stage')}")
                print(f"   Converted to Client: {prospect.get('converted_to_client')}")
                print(f"   Client ID: {prospect.get('client_id')}")
                print(f"   ---")
        else:
            print("❌ No prospect records found for Alejandro")
        
        # 5. Summary
        print(f"\n" + "="*80)
        print("📊 ALEJANDRO LOOKUP SUMMARY")
        print("="*80)
        
        print(f"🎯 CONFIRMED CLIENT ID: {alejandro_id}")
        print(f"📧 EMAIL IN DATABASE: {alejandro_user.get('email')}")
        print(f"📧 REQUESTED EMAIL: alexmar7609@gmail.com")
        print(f"👤 USERNAME: {alejandro_user.get('username')}")
        print(f"📛 FULL NAME: {alejandro_user.get('name')}")
        
        if alejandro_user.get('email') != 'alexmar7609@gmail.com':
            print(f"⚠️  EMAIL MISMATCH DETECTED!")
            print(f"   Database has: {alejandro_user.get('email')}")
            print(f"   Test expects: alexmar7609@gmail.com")
        
        if alejandro_readiness:
            print(f"✅ READINESS STATUS: Found")
            print(f"   Investment Ready: {alejandro_readiness.get('investment_ready')}")
            print(f"   Override Active: {alejandro_readiness.get('readiness_override')}")
        else:
            print(f"❌ READINESS STATUS: Not Found")
        
        print(f"💰 INVESTMENTS: {len(alejandro_investments)} found")
        print(f"🏢 CRM PROSPECTS: {len(alejandro_prospects)} found")
        
        # 6. Recommendations
        print(f"\n📋 RECOMMENDATIONS FOR TESTING:")
        print("-" * 40)
        print(f"1. Use client ID: '{alejandro_id}' in tests")
        print(f"2. Use email: '{alejandro_user.get('email')}' (not alexmar7609@gmail.com)")
        print(f"3. Use username: '{alejandro_user.get('username')}'")
        
        if not alejandro_readiness:
            print(f"4. ⚠️  Create client_readiness record for testing")
        
        if alejandro_user.get('email') != 'alexmar7609@gmail.com':
            print(f"5. ⚠️  Update email to alexmar7609@gmail.com if required by tests")
        
    except Exception as e:
        print(f"❌ Error during lookup: {str(e)}")

if __name__ == "__main__":
    asyncio.run(detailed_alejandro_lookup())