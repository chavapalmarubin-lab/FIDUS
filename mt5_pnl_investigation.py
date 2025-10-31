#!/usr/bin/env python3
"""
MT5 P&L Investigation - Find the TRUE P&L Data

The money_managers collection shows $0 P&L for all managers, but we need to find where 
the actual P&L data is stored and how it should be connected to the managers.

Investigation Steps:
1. Check MT5 accounts collection for actual P&L data
2. Check if there's a separate trading results collection
3. Verify the backend API endpoints that return P&L data
4. Identify the disconnect between money_managers and actual P&L
"""

import requests
import json
import sys
from datetime import datetime
import pymongo
from pymongo import MongoClient
import os

# Backend URL from environment
BACKEND_URL = "https://fidus-pnl-fix.preview.emergentagent.com"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# MongoDB connection
MONGO_URL = "mongodb+srv://chavapalmarubin_db_user:2170Tenoch!@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority"

class MT5PnLInvestigation:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.mongo_client = None
        self.db = None
        
    def connect_to_mongodb(self):
        """Connect to MongoDB"""
        try:
            self.mongo_client = MongoClient(MONGO_URL)
            self.db = self.mongo_client['fidus_production']
            
            # Test connection
            self.mongo_client.admin.command('ping')
            print("✅ Successfully connected to MongoDB")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {str(e)}")
            return False
    
    def authenticate_admin(self):
        """Authenticate as admin"""
        try:
            auth_url = f"{BACKEND_URL}/api/auth/login"
            payload = {
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            }
            
            response = self.session.post(auth_url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                if self.token:
                    self.session.headers.update({'Authorization': f'Bearer {self.token}'})
                    print("✅ Successfully authenticated as admin")
                    return True
            
            print(f"❌ Authentication failed: HTTP {response.status_code}")
            return False
                
        except Exception as e:
            print(f"❌ Authentication exception: {str(e)}")
            return False
    
    def investigate_mt5_accounts_pnl(self):
        """Check MT5 accounts collection for actual P&L data"""
        print("\n🔍 INVESTIGATING MT5 ACCOUNTS P&L DATA")
        print("=" * 60)
        
        try:
            # Get all MT5 accounts
            mt5_accounts = list(self.db.mt5_accounts.find({}))
            
            if not mt5_accounts:
                print("❌ No MT5 accounts found in database")
                return {}
            
            print(f"✅ Found {len(mt5_accounts)} MT5 accounts")
            
            account_pnl_data = {}
            
            for account in mt5_accounts:
                account_num = str(account.get('account', account.get('mt5_login', 'Unknown')))
                
                # Check various P&L fields
                pnl_fields = [
                    'profit_loss', 'profit', 'pnl', 'true_pnl', 'current_profit',
                    'balance', 'equity', 'current_equity', 'floating_profit'
                ]
                
                pnl_data = {}
                for field in pnl_fields:
                    value = account.get(field)
                    if value is not None:
                        pnl_data[field] = value
                
                account_pnl_data[account_num] = {
                    'fund_code': account.get('fund_code', account.get('fund_type', 'Unknown')),
                    'broker_name': account.get('broker_name', 'Unknown'),
                    'pnl_fields': pnl_data
                }
                
                print(f"\nAccount {account_num} ({account_pnl_data[account_num]['fund_code']}):")
                for field, value in pnl_data.items():
                    if isinstance(value, (int, float)) and value != 0:
                        print(f"  {field}: ${value:,.2f}")
                    elif value == 0:
                        print(f"  {field}: $0.00")
            
            return account_pnl_data
            
        except Exception as e:
            print(f"❌ Error investigating MT5 accounts: {str(e)}")
            return {}
    
    def check_backend_api_pnl(self):
        """Check backend API endpoints for P&L data"""
        print("\n🔍 CHECKING BACKEND API P&L DATA")
        print("=" * 60)
        
        api_endpoints = [
            "/api/mt5/admin/accounts",
            "/api/admin/money-managers",
            "/api/mt5/dashboard/overview",
            "/api/admin/fund-performance/dashboard"
        ]
        
        api_pnl_data = {}
        
        for endpoint in api_endpoints:
            try:
                url = f"{BACKEND_URL}{endpoint}"
                response = self.session.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"\n✅ {endpoint} - HTTP 200")
                    
                    # Extract P&L data from response
                    if 'accounts' in data:
                        accounts = data['accounts']
                        for account in accounts:
                            account_id = str(account.get('account_id', account.get('mt5_login', account.get('account', 'Unknown'))))
                            profit = account.get('profit_loss', account.get('profit', account.get('pnl', 0)))
                            if profit != 0:
                                print(f"  Account {account_id}: ${profit:,.2f}")
                                api_pnl_data[account_id] = profit
                    
                    elif 'managers' in data:
                        managers = data['managers']
                        for manager in managers:
                            name = manager.get('name', 'Unknown')
                            pnl = manager.get('current_month_profit', manager.get('total_pnl', manager.get('performance', {}).get('total_pnl', 0)))
                            if pnl != 0:
                                print(f"  Manager {name}: ${pnl:,.2f}")
                    
                    elif 'total_profit_loss' in data:
                        total_pnl = data['total_profit_loss']
                        print(f"  Total P&L: ${total_pnl:,.2f}")
                    
                    # Check for any non-zero P&L values in the response
                    response_str = str(data)
                    if any(keyword in response_str for keyword in ['profit', 'pnl', 'loss']):
                        # Look for numeric values that might be P&L
                        import re
                        numbers = re.findall(r'-?\d+\.?\d*', response_str)
                        non_zero_numbers = [float(n) for n in numbers if float(n) != 0 and abs(float(n)) > 1]
                        if non_zero_numbers:
                            print(f"  Non-zero values found: {non_zero_numbers[:10]}")  # Show first 10
                
                else:
                    print(f"❌ {endpoint} - HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error checking {endpoint}: {str(e)}")
        
        return api_pnl_data
    
    def check_other_collections(self):
        """Check other collections that might contain P&L data"""
        print("\n🔍 CHECKING OTHER COLLECTIONS FOR P&L DATA")
        print("=" * 60)
        
        collections_to_check = [
            'mt5_deals', 'mt5_positions', 'trading_results', 'performance_data',
            'mt5_history', 'account_performance', 'manager_performance'
        ]
        
        found_collections = []
        
        for collection_name in collections_to_check:
            try:
                collection = self.db[collection_name]
                count = collection.count_documents({})
                
                if count > 0:
                    found_collections.append(collection_name)
                    print(f"✅ {collection_name}: {count} documents")
                    
                    # Sample a few documents to see structure
                    sample_docs = list(collection.find({}).limit(3))
                    for i, doc in enumerate(sample_docs):
                        print(f"  Sample {i+1}: {list(doc.keys())}")
                        
                        # Look for P&L related fields
                        pnl_fields = []
                        for key, value in doc.items():
                            if any(keyword in key.lower() for keyword in ['profit', 'pnl', 'loss', 'gain']):
                                if isinstance(value, (int, float)) and value != 0:
                                    pnl_fields.append(f"{key}: {value}")
                        
                        if pnl_fields:
                            print(f"    P&L fields: {', '.join(pnl_fields)}")
                
            except Exception as e:
                # Collection doesn't exist or error accessing it
                continue
        
        if not found_collections:
            print("❌ No additional collections with P&L data found")
        
        return found_collections
    
    def investigate_manager_pnl_calculation(self):
        """Investigate how manager P&L should be calculated"""
        print("\n🔍 INVESTIGATING MANAGER P&L CALCULATION")
        print("=" * 60)
        
        # Get the expected account-to-manager mapping
        expected_mapping = {
            '885822': {'manager': 'CP Strategy', 'expected_pnl': 101.23},
            '886557': {'manager': 'TradingHub Gold', 'expected_pnl': 4973.56},
            '886066': {'manager': 'GoldenTrade', 'expected_pnl': 692.22},
            '886602': {'manager': 'UNO14 MAM', 'expected_pnl': 1136.10}
        }
        
        print("Expected Manager P&L:")
        for account, info in expected_mapping.items():
            print(f"  Account {account} → {info['manager']}: ${info['expected_pnl']:,.2f}")
        
        # Check if we can find this data in any backend endpoint
        try:
            # Try the money managers endpoint
            url = f"{BACKEND_URL}/api/admin/money-managers"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ Money Managers API Response:")
                
                managers = data.get('managers', [])
                total_api_pnl = 0
                
                for manager in managers:
                    name = manager.get('name', 'Unknown')
                    
                    # Check multiple P&L fields
                    pnl_fields = ['current_month_profit', 'total_pnl', 'profit_loss', 'performance']
                    actual_pnl = 0
                    
                    for field in pnl_fields:
                        value = manager.get(field)
                        if isinstance(value, dict):
                            # If it's a dict, look for total_pnl inside
                            actual_pnl = value.get('total_pnl', 0)
                        elif isinstance(value, (int, float)):
                            actual_pnl = value
                        
                        if actual_pnl != 0:
                            break
                    
                    total_api_pnl += actual_pnl
                    print(f"  {name}: ${actual_pnl:,.2f}")
                
                print(f"\nTotal API P&L: ${total_api_pnl:,.2f}")
                print(f"Expected Total: $6,903.11")
                
                if total_api_pnl == 0:
                    print("❌ All managers show $0 P&L - data not being populated correctly")
                else:
                    print("✅ Managers have P&L data")
            
        except Exception as e:
            print(f"❌ Error checking money managers API: {str(e)}")
    
    def run_investigation(self):
        """Run complete P&L investigation"""
        print("🔍 MT5 P&L INVESTIGATION")
        print("=" * 80)
        print(f"Investigation Time: {datetime.now().isoformat()}")
        
        # Connect to MongoDB
        if not self.connect_to_mongodb():
            return False
        
        # Authenticate
        if not self.authenticate_admin():
            return False
        
        # Run investigations
        account_pnl = self.investigate_mt5_accounts_pnl()
        api_pnl = self.check_backend_api_pnl()
        other_collections = self.check_other_collections()
        self.investigate_manager_pnl_calculation()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 INVESTIGATION SUMMARY")
        print("=" * 80)
        
        print("\n🔍 KEY FINDINGS:")
        
        # Check if MT5 accounts have P&L data
        has_mt5_pnl = any(
            any(isinstance(v, (int, float)) and v != 0 for v in data['pnl_fields'].values())
            for data in account_pnl.values()
        )
        
        if has_mt5_pnl:
            print("✅ MT5 accounts collection contains P&L data")
        else:
            print("❌ MT5 accounts collection shows $0 P&L for all accounts")
        
        # Check if API returns P&L data
        if api_pnl:
            print("✅ Backend APIs return some P&L data")
        else:
            print("❌ Backend APIs return $0 P&L for all accounts/managers")
        
        # Check if other collections exist
        if other_collections:
            print(f"✅ Found additional collections: {', '.join(other_collections)}")
        else:
            print("❌ No additional P&L collections found")
        
        print("\n🎯 RECOMMENDATIONS:")
        
        if not has_mt5_pnl and not api_pnl:
            print("1. ❌ CRITICAL: No P&L data found anywhere")
            print("   - Check if MT5 bridge is updating account data")
            print("   - Verify VPS connection and data sync")
            print("   - Check if P&L calculation service is running")
        
        print("2. 🔧 Update money_managers collection with actual P&L")
        print("3. 🔧 Verify MT5 bridge data synchronization")
        print("4. 🔧 Check if P&L calculation needs to be triggered manually")
        
        return True

def main():
    """Main investigation execution"""
    investigator = MT5PnLInvestigation()
    investigator.run_investigation()

if __name__ == "__main__":
    main()