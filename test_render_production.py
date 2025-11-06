#!/usr/bin/env python3
"""
Test Production Render Deployment
Tests the live Render backend with referral system endpoints
"""

import requests
import sys
from datetime import datetime

# Production Backend URL
PROD_BACKEND_URL = "https://fidus-restore.preview.emergentagent.com"

print("=" * 80)
print("🌐 TESTING PRODUCTION RENDER DEPLOYMENT")
print("=" * 80)
print(f"Production URL: {PROD_BACKEND_URL}")
print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

def test_production():
    """Test production backend endpoints"""
    try:
        # 1. Test health endpoint
        print("\n1️⃣ Testing production health endpoint...")
        try:
            response = requests.get(f"{PROD_BACKEND_URL}/api/health", timeout=15)
            if response.status_code == 200:
                health_data = response.json()
                print(f"   ✅ Health check passed")
                print(f"   📊 Status: {health_data.get('status')}")
                print(f"   🗄️  MongoDB: {health_data.get('services', {}).get('mongodb', 'unknown')}")
            else:
                print(f"   ⚠️  Health check returned: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Health check failed: {str(e)}")
            print(f"   ⚠️  Is Render still deploying? Check: https://dashboard.render.com")
            return False
        
        # 2. Test admin login
        print("\n2️⃣ Testing production admin login...")
        login_response = requests.post(
            f"{PROD_BACKEND_URL}/api/auth/login",
            json={"username": "admin", "password": "password123", "user_type": "admin"},
            timeout=15
        )
        
        if login_response.status_code == 200:
            token = login_response.json().get('token')
            print(f"   ✅ Admin login successful")
            print(f"   🔑 Token received: {token[:30]}...")
        else:
            print(f"   ❌ Admin login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text[:200]}")
            return False
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Test referral salespeople endpoint
        print("\n3️⃣ Testing GET /api/admin/referrals/salespeople...")
        salespeople_response = requests.get(
            f"{PROD_BACKEND_URL}/api/admin/referrals/salespeople",
            headers=headers,
            timeout=15
        )
        
        if salespeople_response.status_code == 200:
            data = salespeople_response.json()
            salespeople_list = data.get('salespeople', [])
            print(f"   ✅ Salespeople endpoint working")
            print(f"   📊 Salespeople found: {len(salespeople_list)}")
            
            if len(salespeople_list) > 0:
                for sp in salespeople_list:
                    print(f"\n   👤 {sp.get('name')}")
                    print(f"      Code: {sp.get('referral_code')}")
                    print(f"      Email: {sp.get('email')}")
                    print(f"      Active: {sp.get('active')}")
                    print(f"      Sales Volume: ${sp.get('total_sales_volume', 0):,.2f}")
                    print(f"      Commissions Earned: ${sp.get('total_commissions_earned', 0):,.2f}")
                    print(f"      Commissions Pending: ${sp.get('commissions_pending', 0):,.2f}")
                    print(f"      Commissions Paid: ${sp.get('commissions_paid_to_date', 0):,.2f}")
                    print(f"      Clients Referred: {sp.get('total_clients_referred', 0)}")
            else:
                print("   ⚠️  No salespeople found - migration might not have run on production")
        else:
            print(f"   ❌ Salespeople endpoint failed: {salespeople_response.status_code}")
            print(f"   Response: {salespeople_response.text[:300]}")
            return False
        
        # 4. Test get salesperson by ID (Salvador Palma)
        if len(salespeople_list) > 0:
            salvador_id = salespeople_list[0].get('id')
            print(f"\n4️⃣ Testing GET /api/admin/referrals/salespeople/{salvador_id}...")
            detail_response = requests.get(
                f"{PROD_BACKEND_URL}/api/admin/referrals/salespeople/{salvador_id}",
                headers=headers,
                timeout=15
            )
            
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                print(f"   ✅ Salesperson detail endpoint working")
                print(f"   👤 Name: {detail_data.get('salesperson', {}).get('name')}")
                print(f"   📊 Clients: {len(detail_data.get('clients', []))}")
                print(f"   💼 Investments: {len(detail_data.get('investments', []))}")
                print(f"   💰 Commissions: {len(detail_data.get('commissions', []))}")
            else:
                print(f"   ⚠️  Detail endpoint status: {detail_response.status_code}")
        
        # 5. Test commissions pending endpoint
        print("\n5️⃣ Testing GET /api/admin/referrals/commissions/pending...")
        commissions_response = requests.get(
            f"{PROD_BACKEND_URL}/api/admin/referrals/commissions/pending",
            headers=headers,
            timeout=15
        )
        
        if commissions_response.status_code == 200:
            data = commissions_response.json()
            commissions_list = data.get('commissions', [])
            print(f"   ✅ Commissions endpoint working")
            print(f"   📊 Pending commissions: {len(commissions_list)}")
            
            if len(commissions_list) > 0:
                print(f"\n   Sample commissions:")
                for i, comm in enumerate(commissions_list[:3]):
                    print(f"   💵 ${comm.get('amount', 0):,.2f} - Status: {comm.get('status')} - Due: {comm.get('payment_date')}")
        else:
            print(f"   ⚠️  Commissions endpoint status: {commissions_response.status_code}")
        
        # 6. Test public endpoint (no auth)
        print("\n6️⃣ Testing GET /api/public/salespeople (no auth)...")
        public_response = requests.get(
            f"{PROD_BACKEND_URL}/api/public/salespeople",
            timeout=15
        )
        
        if public_response.status_code == 200:
            data = public_response.json()
            print(f"   ✅ Public salespeople endpoint working")
            print(f"   📊 Active salespeople: {len(data.get('salespeople', []))}")
            
            if len(data.get('salespeople', [])) > 0:
                print(f"\n   🌐 Public accessible salespeople:")
                for sp in data.get('salespeople', []):
                    print(f"   - {sp.get('name')} (Code: {sp.get('referral_code')})")
        else:
            print(f"   ⚠️  Public endpoint status: {public_response.status_code}")
        
        print("\n" + "=" * 80)
        print("✅ PRODUCTION VERIFICATION COMPLETE!")
        print("=" * 80)
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Production test failed: {str(e)}")
        print(f"\n💡 Possible reasons:")
        print(f"   - Render is still deploying (check dashboard)")
        print(f"   - Network/firewall issues")
        print(f"   - Backend service not running")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_production()
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    sys.exit(0 if success else 1)
