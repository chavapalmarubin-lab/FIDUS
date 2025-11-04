#!/usr/bin/env python3
"""
Comprehensive Referral System Deployment Verification
Tests MongoDB data and backend API endpoints
"""

import os
import sys
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import requests
from bson import ObjectId

# MongoDB Configuration
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "fidus_db")

# Backend URL
BACKEND_URL = os.getenv("REACT_APP_BACKEND_URL", "http://localhost:8001")

print("=" * 80)
print("🔍 REFERRAL SYSTEM DEPLOYMENT VERIFICATION")
print("=" * 80)
print(f"MongoDB URL: {MONGO_URL}")
print(f"Database: {DB_NAME}")
print(f"Backend URL: {BACKEND_URL}")
print("=" * 80)

async def verify_mongodb_data():
    """Verify MongoDB collections and data"""
    print("\n📊 MONGODB DATA VERIFICATION\n")
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # 1. Check salespeople collection
        print("1️⃣ Checking 'salespeople' collection...")
        salespeople_count = await db.salespeople.count_documents({})
        print(f"   ✅ Salespeople count: {salespeople_count}")
        
        if salespeople_count > 0:
            salespeople = await db.salespeople.find().to_list(length=100)
            for sp in salespeople:
                print(f"   👤 {sp.get('name')} (Code: {sp.get('referral_code')})")
                print(f"      Email: {sp.get('email')}")
                print(f"      Active: {sp.get('active')}")
                print(f"      Total Sales: ${sp.get('total_sales_volume', 0):,.2f}")
                print(f"      Total Commissions: ${sp.get('total_commissions_earned', 0):,.2f}")
        else:
            print("   ⚠️  No salespeople found!")
        
        # 2. Check referral_commissions collection
        print("\n2️⃣ Checking 'referral_commissions' collection...")
        commissions_count = await db.referral_commissions.count_documents({})
        print(f"   ✅ Commissions count: {commissions_count}")
        
        if commissions_count > 0:
            # Group by status
            pending = await db.referral_commissions.count_documents({"status": "pending"})
            approved = await db.referral_commissions.count_documents({"status": "approved"})
            paid = await db.referral_commissions.count_documents({"status": "paid"})
            
            print(f"   📋 Pending: {pending}")
            print(f"   ✅ Approved: {approved}")
            print(f"   💰 Paid: {paid}")
            
            # Show sample commissions
            sample_commissions = await db.referral_commissions.find().limit(3).to_list(length=3)
            for comm in sample_commissions:
                print(f"   💵 ${comm.get('amount', 0):,.2f} - {comm.get('status')} - Due: {comm.get('payment_date')}")
        else:
            print("   ⚠️  No commissions found!")
        
        # 3. Check clients with referral data
        print("\n3️⃣ Checking 'clients' collection for referral data...")
        clients_with_referrals = await db.clients.count_documents({"referred_by_salesperson_id": {"$exists": True, "$ne": None}})
        print(f"   ✅ Clients with referrals: {clients_with_referrals}")
        
        if clients_with_referrals > 0:
            referred_clients = await db.clients.find({"referred_by_salesperson_id": {"$exists": True, "$ne": None}}).to_list(length=10)
            for client in referred_clients:
                print(f"   👥 {client.get('name')} - Referred by: {client.get('referred_by_salesperson_id')}")
        
        # 4. Check investments with referral tracking
        print("\n4️⃣ Checking 'investments' collection for referral tracking...")
        investments_with_referrals = await db.investments.count_documents({"referred_by_salesperson_id": {"$exists": True, "$ne": None}})
        print(f"   ✅ Investments with referral tracking: {investments_with_referrals}")
        
        if investments_with_referrals > 0:
            referred_investments = await db.investments.find({"referred_by_salesperson_id": {"$exists": True, "$ne": None}}).to_list(length=5)
            total_referred_amount = 0
            for inv in referred_investments:
                amount = float(inv.get('amount', 0))
                total_referred_amount += amount
                print(f"   💼 ${amount:,.2f} - Fund: {inv.get('fund_type')} - Status: {inv.get('status')}")
            print(f"   📊 Total referred investment amount: ${total_referred_amount:,.2f}")
        
        print("\n" + "=" * 80)
        print("✅ MongoDB verification complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ MongoDB verification failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        client.close()

def test_backend_api():
    """Test backend API endpoints"""
    print("\n🔌 BACKEND API VERIFICATION\n")
    
    try:
        # 1. Test health endpoint
        print("1️⃣ Testing health endpoint...")
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=10)
        if response.status_code == 200:
            print(f"   ✅ Health check passed: {response.json()}")
        else:
            print(f"   ⚠️  Health check status: {response.status_code}")
        
        # 2. Test admin login
        print("\n2️⃣ Testing admin login...")
        login_response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json={"username": "admin", "password": "password123"},
            timeout=10
        )
        
        if login_response.status_code == 200:
            token = login_response.json().get('token')
            print(f"   ✅ Admin login successful")
            print(f"   🔑 Token received: {token[:20]}...")
            
            # 3. Test referral endpoints with auth
            headers = {"Authorization": f"Bearer {token}"}
            
            print("\n3️⃣ Testing GET /api/admin/referrals/salespeople...")
            salespeople_response = requests.get(
                f"{BACKEND_URL}/api/admin/referrals/salespeople",
                headers=headers,
                timeout=10
            )
            
            if salespeople_response.status_code == 200:
                data = salespeople_response.json()
                print(f"   ✅ Salespeople endpoint working")
                print(f"   📊 Salespeople found: {len(data.get('salespeople', []))}")
                
                for sp in data.get('salespeople', []):
                    print(f"   👤 {sp.get('name')} - Code: {sp.get('referral_code')}")
                    print(f"      Sales: ${sp.get('total_sales_volume', 0):,.2f}")
                    print(f"      Commissions: ${sp.get('total_commissions_earned', 0):,.2f}")
            else:
                print(f"   ⚠️  Salespeople endpoint status: {salespeople_response.status_code}")
                print(f"   Response: {salespeople_response.text[:200]}")
            
            print("\n4️⃣ Testing GET /api/admin/referrals/commissions/pending...")
            commissions_response = requests.get(
                f"{BACKEND_URL}/api/admin/referrals/commissions/pending",
                headers=headers,
                timeout=10
            )
            
            if commissions_response.status_code == 200:
                data = commissions_response.json()
                print(f"   ✅ Commissions endpoint working")
                print(f"   📊 Pending commissions: {len(data.get('commissions', []))}")
            else:
                print(f"   ⚠️  Commissions endpoint status: {commissions_response.status_code}")
        else:
            print(f"   ❌ Admin login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return False
        
        # 5. Test public endpoint (no auth needed)
        print("\n5️⃣ Testing GET /api/public/salespeople (no auth)...")
        public_response = requests.get(
            f"{BACKEND_URL}/api/public/salespeople",
            timeout=10
        )
        
        if public_response.status_code == 200:
            data = public_response.json()
            print(f"   ✅ Public salespeople endpoint working")
            print(f"   📊 Active salespeople: {len(data.get('salespeople', []))}")
        else:
            print(f"   ⚠️  Public endpoint status: {public_response.status_code}")
        
        print("\n" + "=" * 80)
        print("✅ Backend API verification complete!")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Backend API verification failed: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all verifications"""
    print(f"\n⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Test MongoDB
    mongodb_ok = await verify_mongodb_data()
    
    # Test Backend APIs
    backend_ok = test_backend_api()
    
    # Summary
    print("\n" + "=" * 80)
    print("📋 VERIFICATION SUMMARY")
    print("=" * 80)
    print(f"MongoDB Data: {'✅ PASS' if mongodb_ok else '❌ FAIL'}")
    print(f"Backend APIs: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    
    if mongodb_ok and backend_ok:
        print("\n🎉 ALL VERIFICATIONS PASSED - REFERRAL SYSTEM READY!")
    else:
        print("\n⚠️  SOME VERIFICATIONS FAILED - REVIEW ABOVE")
    
    print("=" * 80)
    print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

if __name__ == "__main__":
    asyncio.run(main())
