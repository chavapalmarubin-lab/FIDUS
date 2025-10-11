#!/usr/bin/env python3
"""
MT5 DATA INVESTIGATION TEST
Deep dive into MT5 endpoints to understand data structure and missing allocations

The critical test showed:
- MT5 Admin Overview: 0 accounts (expected 4 MEXAtlantic)
- Client MT5 Accounts: 4 accounts with $0 allocation (expected $118,151.41 total)

This suggests MT5 accounts exist but allocation/balance data is missing.
"""

import requests
import json
from datetime import datetime
import sys

# Configuration
BACKEND_URL = "https://mt5-data-bridge.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class MT5DataInvestigation:
    def __init__(self):
        self.session = requests.Session()
        self.jwt_token = None
        
    def authenticate_admin(self):
        """Authenticate as admin and get JWT token"""
        try:
            login_data = {
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.jwt_token = data.get("token")
                self.session.headers.update({"Authorization": f"Bearer {self.jwt_token}"})
                print("✅ Admin authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def investigate_mt5_admin_accounts(self):
        """Investigate MT5 admin accounts endpoint"""
        print("\n🔍 INVESTIGATING MT5 ADMIN ACCOUNTS")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/admin/accounts")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response Keys: {list(data.keys())}")
                
                accounts = data.get("accounts", [])
                print(f"Number of accounts: {len(accounts)}")
                
                if accounts:
                    print("\nAccount Details:")
                    for i, account in enumerate(accounts):
                        print(f"  Account {i+1}:")
                        for key, value in account.items():
                            print(f"    {key}: {value}")
                        print()
                else:
                    print("No accounts found in response")
                    
                # Check for other data in response
                for key, value in data.items():
                    if key != "accounts":
                        print(f"{key}: {value}")
                        
            else:
                print(f"Error Response: {response.text}")
                
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def investigate_client_mt5_accounts(self):
        """Investigate client MT5 accounts endpoint"""
        print("\n🔍 INVESTIGATING CLIENT MT5 ACCOUNTS")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/accounts/client_alejandro")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response Keys: {list(data.keys())}")
                
                accounts = data.get("accounts", [])
                print(f"Number of accounts: {len(accounts)}")
                
                if accounts:
                    print("\nAccount Details:")
                    total_allocation = 0
                    for i, account in enumerate(accounts):
                        print(f"  Account {i+1}:")
                        for key, value in account.items():
                            print(f"    {key}: {value}")
                            if key == "allocated_amount":
                                total_allocation += float(value or 0)
                        print()
                    
                    print(f"Total Allocation: ${total_allocation}")
                else:
                    print("No accounts found in response")
                    
                # Check for other data in response
                for key, value in data.items():
                    if key != "accounts":
                        print(f"{key}: {value}")
                        
            else:
                print(f"Error Response: {response.text}")
                
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def investigate_mt5_status(self):
        """Investigate MT5 status endpoint"""
        print("\n🔍 INVESTIGATING MT5 STATUS")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/status")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("MT5 Status Response:")
                print(json.dumps(data, indent=2))
            else:
                print(f"Error Response: {response.text}")
                
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def investigate_mt5_pool_endpoints(self):
        """Investigate MT5 pool endpoints"""
        print("\n🔍 INVESTIGATING MT5 POOL ENDPOINTS")
        print("=" * 50)
        
        # Test MT5 pool statistics
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/pool/statistics")
            print(f"Pool Statistics Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("Pool Statistics:")
                print(json.dumps(data, indent=2))
            else:
                print(f"Pool Statistics Error: {response.text}")
                
        except Exception as e:
            print(f"Pool Statistics Error: {str(e)}")
        
        print()
        
        # Test MT5 pool accounts
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/pool/accounts")
            print(f"Pool Accounts Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("Pool Accounts:")
                print(json.dumps(data, indent=2))
            else:
                print(f"Pool Accounts Error: {response.text}")
                
        except Exception as e:
            print(f"Pool Accounts Error: {str(e)}")
    
    def investigate_investment_data(self):
        """Investigate investment data to understand MT5 mapping"""
        print("\n🔍 INVESTIGATING INVESTMENT DATA")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/investments/client/client_alejandro")
            print(f"Client Investments Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                investments = data.get("investments", [])
                
                print(f"Number of investments: {len(investments)}")
                
                for i, investment in enumerate(investments):
                    print(f"\nInvestment {i+1}:")
                    for key, value in investment.items():
                        print(f"  {key}: {value}")
                    
                    # Look for MT5 related fields
                    mt5_fields = [k for k in investment.keys() if 'mt5' in k.lower()]
                    if mt5_fields:
                        print(f"  MT5 Fields: {mt5_fields}")
                        
            else:
                print(f"Error Response: {response.text}")
                
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def run_investigation(self):
        """Run complete MT5 data investigation"""
        print("🔍 MT5 DATA INVESTIGATION")
        print("=" * 60)
        print("Investigating why MT5 accounts show $0 allocation")
        print("=" * 60)
        
        if not self.authenticate_admin():
            print("❌ Authentication failed - cannot proceed")
            return False
        
        # Run all investigations
        self.investigate_mt5_admin_accounts()
        self.investigate_client_mt5_accounts()
        self.investigate_mt5_status()
        self.investigate_mt5_pool_endpoints()
        self.investigate_investment_data()
        
        print("\n" + "=" * 60)
        print("INVESTIGATION COMPLETE")
        print("=" * 60)
        print("Key findings will help identify why MT5 allocations are $0")

if __name__ == "__main__":
    investigator = MT5DataInvestigation()
    investigator.run_investigation()