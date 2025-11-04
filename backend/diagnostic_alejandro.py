#!/usr/bin/env python3
"""
Comprehensive Diagnostic for Alejandro's Data
Finds where data exists and provides exact fix recommendations
"""

import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from bson import ObjectId

# Support both Motor (async) and PyMongo (sync) for GitHub Actions
try:
    from motor.motor_asyncio import AsyncIOMotorClient
    USE_ASYNC = True
except ImportError:
    from pymongo import MongoClient
    USE_ASYNC = False

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "fidus_db").strip('"').strip("'")

print("=" * 80)
print("🔍 ALEJANDRO DATA DIAGNOSTIC")
print("=" * 80)
print(f"MongoDB: {MONGO_URL}")
print(f"Database: {DB_NAME}")
print("=" * 80)

async def run_diagnostic():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        results = {}
        
        # 1. Find Salvador Palma
        print("\n1️⃣ Searching for Salvador Palma...")
        salvador = await db.salespeople.find_one({"referral_code": "SP-2025"})
        if salvador:
            print(f"✅ Found Salvador")
            print(f"   ID: {salvador['_id']}")
            print(f"   Email: {salvador.get('email')}")
            total_sales = salvador.get('total_sales_volume', 0)
            if hasattr(total_sales, 'to_decimal'):
                total_sales = float(total_sales.to_decimal())
            print(f"   Current Sales: ${total_sales:,.2f}")
            results['salvador_id'] = str(salvador['_id'])
        else:
            print("❌ Salvador not found!")
            return
        
        # 2. Search for Alejandro in USERS
        print("\n2️⃣ Searching for Alejandro in 'users' collection...")
        alejandro_user = await db.users.find_one({
            "$or": [
                {"name": {"$regex": "Alejandro", "$options": "i"}},
                {"email": {"$regex": "alejandro", "$options": "i"}},
                {"email": {"$regex": "mariscal", "$options": "i"}}
            ]
        })
        
        if alejandro_user:
            print(f"✅ Found in USERS")
            print(f"   ID: {alejandro_user['_id']}")
            print(f"   Name: {alejandro_user.get('name')}")
            print(f"   Email: {alejandro_user.get('email')}")
            print(f"   User Type: {alejandro_user.get('user_type')}")
            results['user_id'] = str(alejandro_user['_id'])
            results['user_found'] = True
        else:
            print("⚠️  NOT found in users")
            results['user_found'] = False
        
        # 3. Search for Alejandro in CLIENTS
        print("\n3️⃣ Searching for Alejandro in 'clients' collection...")
        alejandro_client = await db.clients.find_one({
            "$or": [
                {"name": {"$regex": "Alejandro", "$options": "i"}},
                {"email": {"$regex": "alejandro", "$options": "i"}},
                {"email": {"$regex": "mariscal", "$options": "i"}}
            ]
        })
        
        if alejandro_client:
            print(f"✅ Found in CLIENTS")
            print(f"   ID: {alejandro_client['_id']}")
            print(f"   Name: {alejandro_client.get('name')}")
            print(f"   Email: {alejandro_client.get('email')}")
            print(f"   User ID: {alejandro_client.get('user_id')}")
            print(f"   Referred By: {alejandro_client.get('referred_by')}")
            print(f"   Referred By Name: {alejandro_client.get('referred_by_name')}")
            results['client_id'] = str(alejandro_client['_id'])
            results['client_found'] = True
        else:
            print("⚠️  NOT found in clients")
            results['client_found'] = False
        
        # 4. Search for INVESTMENTS - try multiple approaches
        print("\n4️⃣ Searching for Alejandro's investments...")
        
        queries = []
        if results.get('client_id'):
            queries.append({"client_id": results['client_id']})
        if results.get('user_id'):
            queries.append({"user_id": results['user_id']})
        queries.extend([
            {"client_name": {"$regex": "Alejandro", "$options": "i"}},
            {"investor_name": {"$regex": "Alejandro", "$options": "i"}},
            {"email": {"$regex": "alejandro", "$options": "i"}},
            {"email": {"$regex": "mariscal", "$options": "i"}}
        ])
        
        all_investments = []
        seen_ids = set()
        
        for query in queries:
            invs = await db.investments.find(query).to_list(None)
            for inv in invs:
                inv_id = str(inv['_id'])
                if inv_id not in seen_ids:
                    seen_ids.add(inv_id)
                    # USE STANDARD FIELD: principal_amount
                    principal = inv.get('principal_amount', 0)
                    if hasattr(principal, 'to_decimal'):
                        principal = float(principal.to_decimal())
                    all_investments.append({
                        'id': inv_id,
                        'fund_type': inv.get('fund_type'),  # STANDARD FIELD
                        'principal_amount': principal,       # STANDARD FIELD
                        'status': inv.get('status'),
                        'client_id': str(inv.get('client_id')) if inv.get('client_id') else None,
                        'referred_by': str(inv.get('referred_by')) if inv.get('referred_by') else None
                    })
        
        print(f"✅ Found {len(all_investments)} investments")
        total_principal = 0
        for inv in all_investments:
            total_principal += inv['principal_amount']  # STANDARD FIELD
            print(f"   - {inv['fund_type']}: ${inv['principal_amount']:,.2f}")  # STANDARD FIELDS
            print(f"     ID: {inv['id']}")
            print(f"     Client ID: {inv['client_id']}")
            print(f"     Referred By: {inv['referred_by']}")
        print(f"   TOTAL: ${total_principal:,.2f}")
        
        # 5. Check existing commissions
        print("\n5️⃣ Checking existing commissions for Salvador...")
        commissions = await db.referral_commissions.find({
            "salesperson_id": results['salvador_id']
        }).to_list(None)
        
        print(f"✅ Found {len(commissions)} commission records")
        total_comm = 0
        for comm in commissions:
            amount = comm.get('amount', 0)
            if hasattr(amount, 'to_decimal'):
                amount = float(amount.to_decimal())
            total_comm += amount
        print(f"   Total Commission Amount: ${total_comm:,.2f}")
        
        # 6. Generate Recommendations
        print("\n" + "=" * 80)
        print("💡 RECOMMENDATIONS:")
        print("=" * 80)
        
        if not results.get('client_found'):
            print("\n🔧 ACTION 1: CREATE CLIENT RECORD")
            if results.get('user_found'):
                print(f"   Alejandro exists as user but needs client record")
                print(f"   Run: db.clients.insertOne({{")
                print(f"     user_id: ObjectId('{results['user_id']}'),")
                print(f"     name: 'Alejandro Mariscal Romero',")
                print(f"     email: '[email]',")
                print(f"     referred_by: ObjectId('{results['salvador_id']}'),")
                print(f"     referred_by_name: 'Salvador Palma',")
                print(f"     created_at: new Date()")
                print(f"   }})")
            else:
                print(f"   Need to create both USER and CLIENT records")
        
        if all_investments:
            needs_linking = []
            needs_referral = []
            
            for inv in all_investments:
                if results.get('client_id') and inv['client_id'] != results['client_id']:
                    needs_linking.append(inv['id'])
                if inv['referred_by'] != results['salvador_id']:
                    needs_referral.append(inv['id'])
            
            if needs_linking:
                print(f"\n🔧 ACTION 2: LINK INVESTMENTS TO CLIENT")
                print(f"   {len(needs_linking)} investments need client_id updated")
                print(f"   Run: db.investments.updateMany(")
                print(f"     {{_id: {{$in: [ObjectId('...'), ...]}}  }},")
                print(f"     {{$set: {{client_id: '{results.get('client_id')}'}} }}")
                print(f"   )")
            
            if needs_referral:
                print(f"\n🔧 ACTION 3: LINK INVESTMENTS TO SALVADOR")
                print(f"   {len(needs_referral)} investments need referred_by updated")
                print(f"   Run: db.investments.updateMany(")
                print(f"     {{_id: {{$in: [ObjectId('...'), ...]}} }},")
                print(f"     {{$set: {{")
                print(f"       referred_by: ObjectId('{results['salvador_id']}'),")
                print(f"       referred_by_name: 'Salvador Palma'")
                print(f"     }} }}")
                print(f"   )")
        else:
            print("\n❌ CRITICAL: NO INVESTMENTS FOUND")
            print("   Need to manually locate:")
            print("   - FIDUS CORE: $18,151.41")
            print("   - FIDUS BALANCE: $100,000")
        
        if total_amount > 0 and len(commissions) == 0:
            print(f"\n🔧 ACTION 4: GENERATE COMMISSIONS")
            print(f"   Found ${total_amount:,.2f} in investments but 0 commissions")
            print(f"   Need to run commission generation script")
        
        print("\n" + "=" * 80)
        print("📊 SUMMARY")
        print("=" * 80)
        print(f"Salvador Found: ✅")
        print(f"User Found: {'✅' if results.get('user_found') else '❌'}")
        print(f"Client Found: {'✅' if results.get('client_found') else '❌'}")
        print(f"Investments Found: {len(all_investments)} (${total_amount:,.2f})")
        print(f"Commissions Found: {len(commissions)} (${total_comm:,.2f})")
        print(f"Expected Total: $118,151.41")
        print(f"Gap: ${118151.41 - total_amount:,.2f}")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

def run_diagnostic_sync():
    """Synchronous version for GitHub Actions using PyMongo"""
    from pymongo import MongoClient
    
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        results = {}
        
        # 1. Find Salvador Palma
        print("\n1️⃣ Searching for Salvador Palma...")
        salvador = db.salespeople.find_one({"referral_code": "SP-2025"})
        if salvador:
            print(f"✅ Found Salvador")
            print(f"   ID: {salvador['_id']}")
            print(f"   Email: {salvador.get('email')}")
            total_sales = salvador.get('total_sales_volume', 0)
            if hasattr(total_sales, 'to_decimal'):
                total_sales = float(total_sales.to_decimal())
            print(f"   Current Sales: ${total_sales:,.2f}")
            results['salvador_id'] = str(salvador['_id'])
        else:
            print("❌ Salvador not found!")
            return
        
        # 2. Search for Alejandro in USERS
        print("\n2️⃣ Searching for Alejandro in 'users' collection...")
        alejandro_user = db.users.find_one({
            "$or": [
                {"name": {"$regex": "Alejandro", "$options": "i"}},
                {"email": {"$regex": "alejandro", "$options": "i"}},
                {"email": {"$regex": "mariscal", "$options": "i"}}
            ]
        })
        
        if alejandro_user:
            print(f"✅ Found in USERS")
            print(f"   ID: {alejandro_user['_id']}")
            print(f"   Name: {alejandro_user.get('name')}")
            print(f"   Email: {alejandro_user.get('email')}")
            print(f"   User Type: {alejandro_user.get('user_type')}")
            results['user_id'] = str(alejandro_user['_id'])
            results['user_found'] = True
        else:
            print("⚠️  NOT found in users")
            results['user_found'] = False
        
        # 3. Search for Alejandro in CLIENTS
        print("\n3️⃣ Searching for Alejandro in 'clients' collection...")
        alejandro_client = db.clients.find_one({
            "$or": [
                {"name": {"$regex": "Alejandro", "$options": "i"}},
                {"email": {"$regex": "alejandro", "$options": "i"}},
                {"email": {"$regex": "mariscal", "$options": "i"}}
            ]
        })
        
        if alejandro_client:
            print(f"✅ Found in CLIENTS")
            print(f"   ID: {alejandro_client['_id']}")
            print(f"   Name: {alejandro_client.get('name')}")
            print(f"   Email: {alejandro_client.get('email')}")
            print(f"   User ID: {alejandro_client.get('user_id')}")
            print(f"   Referred By: {alejandro_client.get('referred_by')}")
            results['client_id'] = str(alejandro_client['_id'])
            results['client_found'] = True
        else:
            print("⚠️  NOT found in clients")
            results['client_found'] = False
        
        # 4. Search for INVESTMENTS
        print("\n4️⃣ Searching for Alejandro's investments...")
        
        queries = []
        if results.get('client_id'):
            queries.append({"client_id": results['client_id']})
        if results.get('user_id'):
            queries.append({"user_id": results['user_id']})
        queries.extend([
            {"client_name": {"$regex": "Alejandro", "$options": "i"}},
            {"investor_name": {"$regex": "Alejandro", "$options": "i"}},
            {"email": {"$regex": "alejandro", "$options": "i"}},
            {"email": {"$regex": "mariscal", "$options": "i"}}
        ])
        
        all_investments = []
        seen_ids = set()
        
        for query in queries:
            invs = list(db.investments.find(query))
            for inv in invs:
                inv_id = str(inv['_id'])
                if inv_id not in seen_ids:
                    seen_ids.add(inv_id)
                    amount = inv.get('amount', 0)
                    if hasattr(amount, 'to_decimal'):
                        amount = float(amount.to_decimal())
                    all_investments.append({
                        'id': inv_id,
                        'fund_type': inv.get('fund_type'),  # STANDARD FIELD
                        'principal_amount': amount,         # STANDARD FIELD
                        'status': inv.get('status'),
                        'client_id': str(inv.get('client_id')) if inv.get('client_id') else None,
                        'referred_by': str(inv.get('referred_by')) if inv.get('referred_by') else None
                    })
        
        print(f"✅ Found {len(all_investments)} investments")
        total_principal = 0
        for inv in all_investments:
            total_principal += inv['principal_amount']  # STANDARD FIELD
            print(f"   - {inv['fund_type']}: ${inv['principal_amount']:,.2f}")  # STANDARD FIELDS
            print(f"     ID: {inv['id']}")
            print(f"     Client ID: {inv['client_id']}")
            print(f"     Referred By: {inv['referred_by']}")
        print(f"   TOTAL: ${total_principal:,.2f}")
        
        # 5. Check commissions
        print("\n5️⃣ Checking existing commissions for Salvador...")
        commissions = list(db.referral_commissions.find({"salesperson_id": results['salvador_id']}))
        
        print(f"✅ Found {len(commissions)} commission records")
        total_comm = 0
        for comm in commissions:
            amount = comm.get('amount', 0)
            if hasattr(amount, 'to_decimal'):
                amount = float(amount.to_decimal())
            total_comm += amount
        print(f"   Total Commission Amount: ${total_comm:,.2f}")
        
        # 6. Generate Recommendations
        print("\n" + "=" * 80)
        print("💡 RECOMMENDATIONS:")
        print("=" * 80)
        
        if not results.get('client_found'):
            print("\n🔧 ACTION 1: CREATE CLIENT RECORD")
            if results.get('user_found'):
                print(f"   Alejandro exists as user but needs client record")
                print(f"   Run in MongoDB:")
                print(f"   db.clients.insertOne({{")
                print(f"     user_id: ObjectId('{results['user_id']}'),")
                print(f"     name: 'Alejandro Mariscal Romero',")
                print(f"     referred_by: ObjectId('{results['salvador_id']}'),")
                print(f"     referred_by_name: 'Salvador Palma',")
                print(f"     created_at: new Date()")
                print(f"   }})")
        
        if all_investments:
            needs_referral = [inv for inv in all_investments if inv['referred_by'] != results['salvador_id']]
            if needs_referral:
                print(f"\n🔧 ACTION 2: LINK INVESTMENTS TO SALVADOR")
                print(f"   {len(needs_referral)} investments need referred_by updated")
                for inv in needs_referral:
                    print(f"   db.investments.updateOne(")
                    print(f"     {{_id: ObjectId('{inv['id']}')}},")
                    print(f"     {{$set: {{")
                    print(f"       referred_by: ObjectId('{results['salvador_id']}'),")
                    print(f"       referred_by_name: 'Salvador Palma'")
                    print(f"     }}}}")
                    print(f"   )")
        
        print("\n" + "=" * 80)
        print("📊 SUMMARY")
        print("=" * 80)
        print(f"Salvador Found: {'✅' if results.get('salvador_id') else '❌'}")
        print(f"User Found: {'✅' if results.get('user_found') else '❌'}")
        print(f"Client Found: {'✅' if results.get('client_found') else '❌'}")
        print(f"Investments Found: {len(all_investments)} (${total_amount:,.2f})")
        print(f"Commissions Found: {len(commissions)} (${total_comm:,.2f})")
        print(f"Expected Total: $118,151.41")
        print(f"Gap: ${118151.41 - total_amount:,.2f}")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    # Use sync version if motor not available (GitHub Actions)
    if not USE_ASYNC:
        print("Running synchronous version (PyMongo)")
        run_diagnostic_sync()
    else:
        print("Running async version (Motor)")
        asyncio.run(run_diagnostic())
