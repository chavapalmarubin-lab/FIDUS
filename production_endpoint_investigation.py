#!/usr/bin/env python3
"""
PRODUCTION ENDPOINT INVESTIGATION
=================================

This test investigates the exact API endpoints and data flow to understand
why Salvador's data exists in MongoDB but may not be appearing correctly
in the API responses.
"""

import requests
import sys
from datetime import datetime
import json
import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv

class ProductionEndpointInvestigation:
    def __init__(self, base_url="https://fidus-invest.emergent.host"):
        self.base_url = base_url
        self.admin_token = None
        
        # Load environment variables
        load_dotenv('/app/backend/.env')
        
        # MongoDB connection
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        
        print(f"🔍 PRODUCTION ENDPOINT INVESTIGATION")
        print(f"   Production URL: {self.base_url}")
        print(f"   MongoDB URL: {self.mongo_url}")
        print(f"   Database: {self.db_name}")

    def connect_to_mongodb(self):
        """Connect to MongoDB database"""
        try:
            self.mongo_client = MongoClient(self.mongo_url)
            self.db = self.mongo_client[self.db_name]
            
            # Test connection
            self.db.command('ping')
            print("✅ MongoDB connection successful")
            return True
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            return False

    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={
                    "username": "admin",
                    "password": "password123",
                    "user_type": "admin"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                print(f"✅ Admin authenticated: {data.get('name')}")
                return True
            else:
                print(f"❌ Admin authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Admin authentication error: {e}")
            return False

    def investigate_database_state(self):
        """Investigate the current state of MongoDB database"""
        print("\n🔍 INVESTIGATING DATABASE STATE")
        print("-" * 40)
        
        try:
            # Check clients collection
            clients_collection = self.db.clients
            clients = list(clients_collection.find())
            print(f"📊 Clients in database: {len(clients)}")
            
            for client in clients:
                print(f"   - {client.get('name', 'Unknown')} (ID: {client.get('id', 'Unknown')})")
            
            # Check investments collection
            investments_collection = self.db.investments
            investments = list(investments_collection.find())
            print(f"📊 Investments in database: {len(investments)}")
            
            salvador_investments = [i for i in investments if i.get('client_id') == 'client_003']
            print(f"📊 Salvador's investments: {len(salvador_investments)}")
            
            for inv in salvador_investments:
                print(f"   - {inv.get('fund_code')} ${inv.get('principal_amount')} (ID: {inv.get('investment_id')})")
            
            # Check MT5 accounts collection
            mt5_collection = self.db.mt5_accounts
            mt5_accounts = list(mt5_collection.find())
            print(f"📊 MT5 accounts in database: {len(mt5_accounts)}")
            
            salvador_mt5 = [m for m in mt5_accounts if m.get('client_id') == 'client_003']
            print(f"📊 Salvador's MT5 accounts: {len(salvador_mt5)}")
            
            for mt5 in salvador_mt5:
                print(f"   - {mt5.get('broker')} Login: {mt5.get('login')} (ID: {mt5.get('account_id')})")
            
            return True
            
        except Exception as e:
            print(f"❌ Database investigation failed: {e}")
            return False

    def test_api_endpoint(self, name, endpoint, expected_keys=None):
        """Test a specific API endpoint"""
        if not self.admin_token:
            print(f"❌ No admin token for {name}")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }
        
        try:
            url = f"{self.base_url}/{endpoint}"
            print(f"\n🔍 Testing {name}")
            print(f"   URL: {url}")
            
            response = requests.get(url, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ Success - Response keys: {list(data.keys())}")
                    
                    if expected_keys:
                        for key in expected_keys:
                            if key in data:
                                value = data[key]
                                if isinstance(value, list):
                                    print(f"   {key}: {len(value)} items")
                                else:
                                    print(f"   {key}: {value}")
                            else:
                                print(f"   ❌ Missing key: {key}")
                    
                    return True, data
                except Exception as e:
                    print(f"   ❌ JSON parsing error: {e}")
                    print(f"   Raw response: {response.text[:200]}...")
                    return False, {}
            else:
                print(f"   ❌ Failed - Status: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error text: {response.text[:200]}...")
                return False, {}
                
        except Exception as e:
            print(f"   ❌ Request error: {e}")
            return False, {}

    def investigate_all_endpoints(self):
        """Test all relevant API endpoints"""
        print("\n🔍 INVESTIGATING ALL RELEVANT ENDPOINTS")
        print("-" * 50)
        
        endpoints_to_test = [
            ("Health Check", "api/health", ["status"]),
            ("Admin Clients", "api/admin/clients", ["clients"]),
            ("Salvador Investments", "api/investments/client/client_003", ["investments"]),
            ("MT5 Admin Accounts", "api/mt5/admin/accounts", ["accounts"]),
            ("Fund Performance Dashboard", "api/admin/fund-performance/dashboard", ["total_aum"]),
            ("Cash Flow Overview", "api/admin/cashflow/overview", ["mt5_trading_profits"]),
            ("Salvador MT5 Accounts", "api/mt5/client/client_003/accounts", ["accounts"]),
        ]
        
        results = {}
        
        for name, endpoint, expected_keys in endpoints_to_test:
            success, data = self.test_api_endpoint(name, endpoint, expected_keys)
            results[name] = {
                'success': success,
                'data': data
            }
        
        return results

    def analyze_data_flow(self, api_results):
        """Analyze the data flow between database and API"""
        print("\n🔍 ANALYZING DATA FLOW")
        print("-" * 30)
        
        # Check if Salvador appears in clients endpoint
        clients_data = api_results.get('Admin Clients', {}).get('data', {})
        clients = clients_data.get('clients', [])
        salvador_in_clients = any(c.get('name') == 'SALVADOR PALMA' for c in clients)
        print(f"Salvador in clients endpoint: {'✅' if salvador_in_clients else '❌'}")
        
        # Check Salvador's investments
        investments_data = api_results.get('Salvador Investments', {}).get('data', {})
        investments = investments_data.get('investments', [])
        print(f"Salvador's investments via API: {len(investments)}")
        
        if investments:
            for inv in investments:
                print(f"   - {inv.get('fund_code')} ${inv.get('principal_amount', inv.get('current_value'))}")
        
        # Check MT5 accounts
        mt5_data = api_results.get('MT5 Admin Accounts', {}).get('data', {})
        mt5_accounts = mt5_data.get('accounts', [])
        salvador_mt5_accounts = [a for a in mt5_accounts if a.get('client_id') == 'client_003']
        print(f"Salvador's MT5 accounts via API: {len(salvador_mt5_accounts)}")
        
        if salvador_mt5_accounts:
            for mt5 in salvador_mt5_accounts:
                print(f"   - {mt5.get('broker')} Login: {mt5.get('login')}")
        
        # Check fund performance
        fund_data = api_results.get('Fund Performance Dashboard', {}).get('data', {})
        total_aum = fund_data.get('total_aum', 0)
        print(f"Total AUM in fund performance: ${total_aum}")
        
        # Check cash flow
        cashflow_data = api_results.get('Cash Flow Overview', {}).get('data', {})
        mt5_profits = cashflow_data.get('mt5_trading_profits', 0)
        print(f"MT5 trading profits in cash flow: ${mt5_profits}")

    def run_investigation(self):
        """Run complete investigation"""
        print("🚀 STARTING PRODUCTION ENDPOINT INVESTIGATION")
        print("=" * 60)
        
        # Connect to MongoDB
        if not self.connect_to_mongodb():
            return False
        
        # Authenticate
        if not self.authenticate_admin():
            return False
        
        # Investigate database state
        if not self.investigate_database_state():
            return False
        
        # Test all API endpoints
        api_results = self.investigate_all_endpoints()
        
        # Analyze data flow
        self.analyze_data_flow(api_results)
        
        # Summary
        successful_endpoints = sum(1 for result in api_results.values() if result['success'])
        total_endpoints = len(api_results)
        
        print(f"\n📊 INVESTIGATION SUMMARY")
        print(f"   API Endpoints tested: {successful_endpoints}/{total_endpoints}")
        print(f"   Database connection: ✅")
        print(f"   Authentication: ✅")
        
        return True

def main():
    """Main execution function"""
    investigator = ProductionEndpointInvestigation()
    success = investigator.run_investigation()
    
    if success:
        print("\n🎉 Investigation completed successfully!")
    else:
        print("\n❌ Investigation failed!")
    
    return success

if __name__ == "__main__":
    main()