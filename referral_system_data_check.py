#!/usr/bin/env python3
"""
FIDUS Referral System Data Check
Check what data exists in the database and create test data if needed
"""

import requests
import json
import sys
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

class ReferralDataChecker:
    def __init__(self):
        self.base_url = "https://allocation-hub-1.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.admin_token = None
        
    def authenticate_admin(self) -> bool:
        """Authenticate as admin user"""
        try:
            print("🔐 Authenticating as admin...")
            
            login_data = {
                "username": "admin",
                "password": "password123",
                "user_type": "admin"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                if self.admin_token:
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}'
                    })
                    print("✅ Successfully authenticated as admin")
                    return True
                else:
                    print("❌ No token received in response")
                    return False
            else:
                print(f"❌ Authentication failed: HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception during authentication: {str(e)}")
            return False
    
    def check_public_endpoints(self):
        """Check public endpoints"""
        print("\n🌐 CHECKING PUBLIC ENDPOINTS")
        print("=" * 50)
        
        # Test public salespeople list
        try:
            response = requests.get(f"{self.base_url}/public/salespeople")
            print(f"GET /api/public/salespeople: HTTP {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                salespeople = data.get("salespeople", [])
                print(f"   Found {len(salespeople)} active salespeople")
                for sp in salespeople:
                    print(f"   - {sp.get('name')} ({sp.get('referral_code')})")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Exception: {e}")
        
        # Test specific salesperson by code
        try:
            response = requests.get(f"{self.base_url}/public/salespeople/SP-2025")
            print(f"GET /api/public/salespeople/SP-2025: HTTP {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Found: {data.get('name')} ({data.get('referral_code')})")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Exception: {e}")
    
    def check_admin_endpoints(self):
        """Check admin endpoints"""
        print("\n🔐 CHECKING ADMIN ENDPOINTS")
        print("=" * 50)
        
        # Test admin salespeople list
        try:
            response = self.session.get(f"{self.base_url}/admin/referrals/salespeople")
            print(f"GET /api/admin/referrals/salespeople: HTTP {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                salespeople = data.get("salespeople", [])
                print(f"   Found {len(salespeople)} salespeople")
                for sp in salespeople:
                    print(f"   - {sp.get('name')} ({sp.get('referral_code')}) - ID: {sp.get('id')}")
                    print(f"     Clients: {sp.get('total_clients_referred', 0)}, Sales: ${sp.get('total_sales_volume', 0)}")
                    print(f"     Commissions: ${sp.get('total_commissions_earned', 0)}")
                return salespeople
            else:
                print(f"   Error: {response.text}")
                return []
        except Exception as e:
            print(f"   Exception: {e}")
            return []
    
    def check_commission_endpoints(self, salesperson_id: str = None):
        """Check commission-related endpoints"""
        print("\n💰 CHECKING COMMISSION ENDPOINTS")
        print("=" * 50)
        
        # Test commission calendar
        try:
            params = {
                "start_date": "2025-01-01",
                "end_date": "2026-12-31"
            }
            response = self.session.get(f"{self.base_url}/admin/referrals/commissions/calendar", params=params)
            print(f"GET /api/admin/referrals/commissions/calendar: HTTP {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                calendar = data.get("calendar", [])
                print(f"   Found {len(calendar)} months with commissions")
                for month in calendar[:3]:  # Show first 3 months
                    print(f"   - {month.get('month_display')}: ${month.get('total_commissions', 0):.2f} ({len(month.get('payments', []))} payments)")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Exception: {e}")
        
        # Test pending commissions
        try:
            params = {
                "status_filter": "all",
                "overdue": "false"
            }
            response = self.session.get(f"{self.base_url}/admin/referrals/commissions/pending", params=params)
            print(f"GET /api/admin/referrals/commissions/pending: HTTP {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Response keys: {list(data.keys())}")
                if "by_salesperson" in data:
                    by_sp = data["by_salesperson"]
                    print(f"   Found pending commissions for {len(by_sp)} salespeople")
                    for sp_name, commissions in by_sp.items():
                        total = sum(c.get("amount", 0) for c in commissions)
                        print(f"   - {sp_name}: {len(commissions)} commissions, ${total:.2f}")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Exception: {e}")
        
        # Test salesperson dashboard if ID provided
        if salesperson_id:
            try:
                response = self.session.get(f"{self.base_url}/admin/referrals/salespeople/{salesperson_id}")
                print(f"GET /api/admin/referrals/salespeople/{salesperson_id}: HTTP {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    summary = data.get("summary", {})
                    print(f"   Dashboard Summary:")
                    print(f"   - Total Clients: {summary.get('total_clients', 0)}")
                    print(f"   - Total Sales: ${summary.get('total_sales_volume', 0):.2f}")
                    print(f"   - Total Commissions: ${summary.get('total_commissions_earned', 0):.2f}")
                    print(f"   - Pending: ${summary.get('commissions_pending', 0):.2f}")
                    
                    commissions = data.get("commissions", {}).get("all", [])
                    print(f"   - Commission Records: {len(commissions)}")
                else:
                    print(f"   Error: {response.text}")
            except Exception as e:
                print(f"   Exception: {e}")
    
    def create_test_data(self):
        """Create test data if none exists"""
        print("\n➕ CREATING TEST DATA")
        print("=" * 50)
        
        # Create Salvador Palma if not exists
        try:
            salvador_data = {
                "name": "Salvador Palma",
                "email": "salvador.palma@fidus.com",
                "phone": "+525551234567",
                "wallet_details": {
                    "crypto_wallet": "0xSalvadorWallet123",
                    "preferred_method": "crypto"
                },
                "notes": "Test salesperson for referral system"
            }
            
            response = self.session.post(f"{self.base_url}/admin/referrals/salespeople", json=salvador_data)
            print(f"POST /api/admin/referrals/salespeople: HTTP {response.status_code}")
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"   Created Salvador Palma with code: {data.get('referral_code')}")
                print(f"   Salesperson ID: {data.get('salesperson_id')}")
                return data.get('salesperson_id')
            else:
                print(f"   Error: {response.text}")
                return None
        except Exception as e:
            print(f"   Exception: {e}")
            return None
    
    def run_complete_check(self):
        """Run complete data check"""
        print("🚀 FIDUS Referral System Data Check")
        print("=" * 80)
        
        # Check public endpoints first
        self.check_public_endpoints()
        
        # Authenticate for admin endpoints
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return
        
        # Check admin endpoints
        salespeople = self.check_admin_endpoints()
        
        # If no salespeople found, create test data
        if not salespeople:
            print("\n⚠️ No salespeople found, creating test data...")
            salvador_id = self.create_test_data()
            if salvador_id:
                # Re-check after creating data
                salespeople = self.check_admin_endpoints()
        
        # Check commission endpoints
        if salespeople:
            first_sp = salespeople[0]
            sp_id = first_sp.get('id')
            if sp_id:
                self.check_commission_endpoints(sp_id)
        
        print("\n" + "=" * 80)
        print("📊 DATA CHECK COMPLETE")
        
        if salespeople:
            print(f"✅ Found {len(salespeople)} salespeople in system")
            print("✅ Referral system appears to be functional")
        else:
            print("❌ No salespeople found - referral system may need setup")

def main():
    """Main execution"""
    checker = ReferralDataChecker()
    checker.run_complete_check()

if __name__ == "__main__":
    main()