#!/usr/bin/env python3
"""
DETAILED INVESTIGATION OF CRITICAL ISSUES
=========================================

Based on initial test results, let me investigate the specific data returned
to understand the exact state of the system.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://mockdb-cleanup.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class DetailedInvestigationTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                if self.admin_token:
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    print("✅ Successfully authenticated as admin")
                    return True
            return False
        except Exception as e:
            print(f"❌ Authentication failed: {str(e)}")
            return False
    
    def investigate_clients_data(self):
        """Detailed investigation of clients data"""
        print("\n🔍 DETAILED CLIENTS INVESTIGATION")
        print("=" * 50)
        
        # Test /admin/clients
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            print(f"📊 /admin/clients - Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Response type: {type(data)}")
                print(f"Response data: {json.dumps(data, indent=2)}")
                
                # Look for Salvador specifically
                if isinstance(data, dict) and 'clients' in data:
                    clients = data['clients']
                    print(f"Found {len(clients)} clients in 'clients' key")
                    for client in clients:
                        if 'SALVADOR' in str(client.get('name', '')).upper():
                            print(f"✅ SALVADOR FOUND: {client}")
                elif isinstance(data, list):
                    print(f"Found {len(data)} clients in list")
                    for client in data:
                        if 'SALVADOR' in str(client.get('name', '')).upper():
                            print(f"✅ SALVADOR FOUND: {client}")
            else:
                print(f"❌ Error response: {response.text}")
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
        
        # Test /clients/all
        try:
            response = self.session.get(f"{BACKEND_URL}/clients/all")
            print(f"\n📊 /clients/all - Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Response type: {type(data)}")
                print(f"Response data: {json.dumps(data, indent=2)}")
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    def investigate_investments_data(self):
        """Detailed investigation of investment data"""
        print("\n🔍 DETAILED INVESTMENTS INVESTIGATION")
        print("=" * 50)
        
        # Test Salvador's investments
        try:
            response = self.session.get(f"{BACKEND_URL}/investments/client/client_003")
            print(f"📊 Salvador's investments - Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
                
                # Extract investment values
                if 'investments' in data:
                    investments = data['investments']
                    total_value = 0
                    print(f"\n💰 INVESTMENT ANALYSIS:")
                    for inv in investments:
                        principal = inv.get('principal_amount', 0)
                        current = inv.get('current_value', 0)
                        fund = inv.get('fund_code', 'Unknown')
                        total_value += current
                        print(f"   {fund}: Principal ${principal:,.2f}, Current ${current:,.2f}")
                    
                    print(f"   TOTAL VALUE: ${total_value:,.2f}")
                    
                    # Check if this matches expected $1,371,485.40
                    expected = 1371485.40
                    if abs(total_value - expected) < 1000:
                        print(f"✅ Investment values match expected amount!")
                    else:
                        print(f"❌ Investment values don't match expected ${expected:,.2f}")
            else:
                print(f"❌ Error response: {response.text}")
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
        
        # Test fund performance dashboard
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/fund-performance/dashboard")
            print(f"\n📊 Fund Performance Dashboard - Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)[:1000]}...")  # Truncate for readability
                
                # Look for investment values
                if 'dashboard' in data:
                    dashboard = data['dashboard']
                    if 'fund_commitments' in dashboard:
                        commitments = dashboard['fund_commitments']
                        print(f"\n💰 FUND COMMITMENTS ANALYSIS:")
                        for fund_code, fund_data in commitments.items():
                            if 'client_investment' in fund_data:
                                client_inv = fund_data['client_investment']
                                principal = client_inv.get('principal_amount', 0)
                                print(f"   {fund_code}: ${principal:,.2f}")
            else:
                print(f"❌ Error response: {response.text}")
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    def investigate_mt5_data(self):
        """Detailed investigation of MT5 data"""
        print("\n🔍 DETAILED MT5 INVESTIGATION")
        print("=" * 50)
        
        # Test MT5 admin accounts
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/admin/accounts")
            print(f"📊 MT5 Admin Accounts - Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
                
                # Analyze MT5 accounts
                if 'accounts' in data:
                    accounts = data['accounts']
                    print(f"\n🏦 MT5 ACCOUNTS ANALYSIS:")
                    print(f"   Total accounts: {len(accounts)}")
                    
                    doo_found = False
                    vt_found = False
                    
                    for account in accounts:
                        login = account.get('mt5_login', '')
                        broker = account.get('broker_name', '')
                        allocated = account.get('total_allocated', 0)
                        
                        print(f"   Account: {login} ({broker}) - ${allocated:,.2f}")
                        
                        if login == '9928326':
                            doo_found = True
                            print(f"   ✅ DooTechnology account found!")
                        
                        if login == '15759667':
                            vt_found = True
                            print(f"   ✅ VT Markets account found!")
                    
                    if not doo_found:
                        print(f"   ❌ DooTechnology account (9928326) not found")
                    if not vt_found:
                        print(f"   ❌ VT Markets account (15759667) not found")
                    
                    # Check summary
                    if 'summary' in data:
                        summary = data['summary']
                        total_allocated = summary.get('total_allocated', 0)
                        print(f"\n   TOTAL ALLOCATED: ${total_allocated:,.2f}")
                        
                        # Check if this matches expected amount
                        expected = 1371485.40
                        if abs(total_allocated - expected) < 1000:
                            print(f"   ✅ Total allocation matches expected amount!")
                        else:
                            print(f"   ❌ Total allocation doesn't match expected ${expected:,.2f}")
            else:
                print(f"❌ Error response: {response.text}")
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    def investigate_aml_kyc_endpoints(self):
        """Look for any AML/KYC related functionality"""
        print("\n🔍 AML/KYC ENDPOINTS INVESTIGATION")
        print("=" * 50)
        
        # Try to find any registration or prospect endpoints
        potential_endpoints = [
            "/admin/registration/applications",
            "/admin/prospects", 
            "/admin/leads",
            "/admin/clients/pending",
            "/registration/applications",
            "/prospects",
            "/leads"
        ]
        
        for endpoint in potential_endpoints:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                print(f"📊 {endpoint} - Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   Found data: {type(data)} with {len(data) if isinstance(data, (list, dict)) else 'unknown'} items")
                    
                    # Look for Lilian
                    if isinstance(data, list):
                        for item in data:
                            name = str(item.get('name', ''))
                            if 'LILIAN' in name.upper() or 'LIMON' in name.upper():
                                print(f"   ✅ LILIAN FOUND: {item}")
                elif response.status_code == 404:
                    print(f"   ❌ Endpoint not found")
                else:
                    print(f"   ❌ Error: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Exception: {str(e)}")
    
    def run_investigation(self):
        """Run detailed investigation"""
        print("🔍 DETAILED CRITICAL ISSUES INVESTIGATION")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Investigation Time: {datetime.now().isoformat()}")
        
        if not self.authenticate_admin():
            print("❌ Cannot proceed without authentication")
            return False
        
        self.investigate_clients_data()
        self.investigate_investments_data()
        self.investigate_mt5_data()
        self.investigate_aml_kyc_endpoints()
        
        print("\n" + "=" * 60)
        print("🎯 INVESTIGATION COMPLETE")
        print("=" * 60)
        
        return True

def main():
    """Main investigation execution"""
    investigator = DetailedInvestigationTest()
    investigator.run_investigation()

if __name__ == "__main__":
    main()