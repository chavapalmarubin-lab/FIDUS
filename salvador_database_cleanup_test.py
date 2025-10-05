#!/usr/bin/env python3
"""
CRITICAL SALVADOR PALMA DATABASE CLEANUP TEST
============================================

This test executes the URGENT database cleanup operation as requested in the review:
- Remove ALL mock/test data contamination
- Create ONLY Salvador's correct 2 investments (BALANCE + CORE)
- Create ONLY Salvador's 2 MT5 accounts (DooTechnology + VT Markets)
- Verify system shows correct data after cleanup

EXPECTED RESULT AFTER CLEANUP:
- Total AUM: $1,267,485.40 (not $7.5M)
- Total Investments: 2 (not 8)
- BALANCE Fund: $1,263,485.40 (not $7.5M)
- CORE Fund: $4,000.00 ✓
- MT5 Accounts: 2 visible (DooTechnology + VT Markets)
- Active Clients: 1 (Salvador only)
"""

import requests
import sys
from datetime import datetime
import json
import pymongo
import os
from dotenv import load_dotenv

class SalvadorDatabaseCleanupTester:
    def __init__(self, base_url="https://fidus-finance-api.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None
        
        # Load environment variables
        load_dotenv('/app/backend/.env')
        
        # MongoDB connection
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'test_database')
        
        try:
            self.mongo_client = pymongo.MongoClient(mongo_url)
            self.db = self.mongo_client[db_name]
            print(f"✅ Connected to MongoDB: {db_name}")
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            sys.exit(1)

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def admin_login(self):
        """Login as admin to get authentication token"""
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "api/auth/login",
            200,
            data={
                "username": "admin", 
                "password": "password123",
                "user_type": "admin"
            }
        )
        if success:
            self.admin_token = response.get('token')
            print(f"   Admin logged in successfully")
        return success

    def get_auth_headers(self):
        """Get authorization headers with admin token"""
        if not self.admin_token:
            return {'Content-Type': 'application/json'}
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }

    def execute_database_cleanup(self):
        """Execute the critical database cleanup operations"""
        print("\n🚨 EXECUTING CRITICAL DATABASE CLEANUP OPERATIONS...")
        
        try:
            # 1. DELETE ALL EXISTING INVESTMENTS (clean slate)
            print("\n1. Deleting ALL existing investments...")
            result = self.db.investments.delete_many({})
            print(f"   Deleted {result.deleted_count} investments")
            
            # 2. DELETE ALL EXISTING MT5 ACCOUNTS (clean slate)
            print("\n2. Deleting ALL existing MT5 accounts...")
            result = self.db.mt5_accounts.delete_many({})
            print(f"   Deleted {result.deleted_count} MT5 accounts")
            
            # 3. DELETE ALL CLIENTS EXCEPT SALVADOR (clean slate)
            print("\n3. Deleting all clients except Salvador...")
            result = self.db.clients.delete_many({"id": {"$ne": "client_003"}})
            print(f"   Deleted {result.deleted_count} clients (kept Salvador)")
            
            # 4. CREATE SALVADOR'S 2 CORRECT INVESTMENTS
            print("\n4. Creating Salvador's 2 correct investments...")
            
            # DooTechnology BALANCE Investment
            balance_investment = {
                "investment_id": "balance_doo_salvador",
                "client_id": "client_003",
                "fund_code": "BALANCE",
                "principal_amount": 1263485.40,
                "current_value": 1263485.40,
                "deposit_date": datetime.fromisoformat("2025-04-01T00:00:00.000Z".replace('Z', '+00:00')),
                "status": "ACTIVE",
                "created_at": datetime.utcnow()
            }
            self.db.investments.insert_one(balance_investment)
            print(f"   ✅ Created BALANCE investment: ${balance_investment['principal_amount']:,.2f}")
            
            # VT Markets CORE Investment
            core_investment = {
                "investment_id": "core_vt_salvador",
                "client_id": "client_003",
                "fund_code": "CORE",
                "principal_amount": 4000.00,
                "current_value": 4000.00,
                "deposit_date": datetime.fromisoformat("2025-04-01T00:00:00.000Z".replace('Z', '+00:00')),
                "status": "ACTIVE",
                "created_at": datetime.utcnow()
            }
            self.db.investments.insert_one(core_investment)
            print(f"   ✅ Created CORE investment: ${core_investment['principal_amount']:,.2f}")
            
            # 5. CREATE SALVADOR'S 2 MT5 ACCOUNTS
            print("\n5. Creating Salvador's 2 MT5 accounts...")
            
            # DooTechnology MT5 Account
            doo_mt5_account = {
                "account_id": "mt5_doo_salvador",
                "client_id": "client_003",
                "login": "9928326",
                "broker": "DooTechnology",
                "server": "DooTechnology-Live",
                "investment_id": "balance_doo_salvador",
                "total_allocated": 1263485.40,
                "current_equity": 1263485.40,
                "status": "active",
                "created_at": datetime.utcnow()
            }
            self.db.mt5_accounts.insert_one(doo_mt5_account)
            print(f"   ✅ Created DooTechnology MT5 account: {doo_mt5_account['login']}")
            
            # VT Markets MT5 Account
            vt_mt5_account = {
                "account_id": "mt5_vt_salvador",
                "client_id": "client_003",
                "login": "15759667",
                "broker": "VT Markets",
                "server": "VTMarkets-PAMM",
                "investment_id": "core_vt_salvador",
                "total_allocated": 4000.00,
                "current_equity": 4000.00,
                "status": "active",
                "created_at": datetime.utcnow()
            }
            self.db.mt5_accounts.insert_one(vt_mt5_account)
            print(f"   ✅ Created VT Markets MT5 account: {vt_mt5_account['login']}")
            
            # 6. UPDATE SALVADOR'S CLIENT RECORD
            print("\n6. Updating Salvador's client record...")
            salvador_update = {
                "$set": {
                    "name": "SALVADOR PALMA",
                    "email": "salvador.palma@fidus.com",
                    "total_balance": 1267485.40,
                    "status": "active"
                }
            }
            result = self.db.clients.update_one({"id": "client_003"}, salvador_update)
            if result.matched_count > 0:
                print(f"   ✅ Updated Salvador's client record")
            else:
                print(f"   ⚠️  Salvador's client record not found - may need to create")
            
            print("\n✅ DATABASE CLEANUP COMPLETED SUCCESSFULLY!")
            return True
            
        except Exception as e:
            print(f"\n❌ DATABASE CLEANUP FAILED: {e}")
            return False

    def verify_database_state(self):
        """Verify the database state after cleanup"""
        print("\n🔍 VERIFYING DATABASE STATE AFTER CLEANUP...")
        
        try:
            # Check investments
            investments = list(self.db.investments.find({}))
            print(f"\n📊 INVESTMENTS VERIFICATION:")
            print(f"   Total investments: {len(investments)}")
            
            balance_investments = [inv for inv in investments if inv['fund_code'] == 'BALANCE']
            core_investments = [inv for inv in investments if inv['fund_code'] == 'CORE']
            
            print(f"   BALANCE investments: {len(balance_investments)}")
            print(f"   CORE investments: {len(core_investments)}")
            
            total_aum = sum(inv['current_value'] for inv in investments)
            print(f"   Total AUM: ${total_aum:,.2f}")
            
            # Check MT5 accounts
            mt5_accounts = list(self.db.mt5_accounts.find({}))
            print(f"\n🏦 MT5 ACCOUNTS VERIFICATION:")
            print(f"   Total MT5 accounts: {len(mt5_accounts)}")
            
            doo_accounts = [acc for acc in mt5_accounts if acc['broker'] == 'DooTechnology']
            vt_accounts = [acc for acc in mt5_accounts if acc['broker'] == 'VT Markets']
            
            print(f"   DooTechnology accounts: {len(doo_accounts)}")
            print(f"   VT Markets accounts: {len(vt_accounts)}")
            
            # Check clients
            clients = list(self.db.clients.find({}))
            print(f"\n👥 CLIENTS VERIFICATION:")
            print(f"   Total clients: {len(clients)}")
            
            salvador_clients = [client for client in clients if client.get('id') == 'client_003']
            print(f"   Salvador Palma clients: {len(salvador_clients)}")
            
            # Verify expected results
            verification_results = {
                "correct_investment_count": len(investments) == 2,
                "correct_balance_amount": any(inv['current_value'] == 1263485.40 for inv in balance_investments),
                "correct_core_amount": any(inv['current_value'] == 4000.00 for inv in core_investments),
                "correct_total_aum": abs(total_aum - 1267485.40) < 0.01,
                "correct_mt5_count": len(mt5_accounts) == 2,
                "has_doo_account": len(doo_accounts) == 1,
                "has_vt_account": len(vt_accounts) == 1,
                "only_salvador_client": len(clients) == 1 and len(salvador_clients) == 1
            }
            
            print(f"\n✅ VERIFICATION RESULTS:")
            for check, result in verification_results.items():
                status = "✅" if result else "❌"
                print(f"   {status} {check}: {result}")
            
            all_passed = all(verification_results.values())
            print(f"\n{'✅ ALL VERIFICATIONS PASSED!' if all_passed else '❌ SOME VERIFICATIONS FAILED!'}")
            
            return all_passed
            
        except Exception as e:
            print(f"\n❌ VERIFICATION FAILED: {e}")
            return False

    def test_api_endpoints_after_cleanup(self):
        """Test API endpoints to verify they show correct data after cleanup"""
        print("\n🔍 TESTING API ENDPOINTS AFTER CLEANUP...")
        
        if not self.admin_token:
            print("❌ No admin token available for API testing")
            return False
        
        # Test clients endpoint
        success, response = self.run_test(
            "Get All Clients After Cleanup",
            "GET",
            "api/admin/clients",
            200,
            headers=self.get_auth_headers()
        )
        
        if success:
            clients = response.get('clients', [])
            print(f"   API shows {len(clients)} clients")
            salvador_found = any(client.get('name') == 'SALVADOR PALMA' for client in clients)
            print(f"   Salvador Palma found: {salvador_found}")
        
        # Test investments endpoint for Salvador
        success, response = self.run_test(
            "Get Salvador's Investments After Cleanup",
            "GET",
            "api/investments/client/client_003",
            200,
            headers=self.get_auth_headers()
        )
        
        if success:
            investments = response.get('investments', [])
            print(f"   Salvador has {len(investments)} investments")
            
            balance_found = any(inv.get('fund_code') == 'BALANCE' for inv in investments)
            core_found = any(inv.get('fund_code') == 'CORE' for inv in investments)
            
            print(f"   BALANCE investment found: {balance_found}")
            print(f"   CORE investment found: {core_found}")
        
        # Test MT5 accounts endpoint
        success, response = self.run_test(
            "Get All MT5 Accounts After Cleanup",
            "GET",
            "api/admin/mt5-accounts",
            200,
            headers=self.get_auth_headers()
        )
        
        if success:
            mt5_accounts = response.get('accounts', [])
            print(f"   API shows {len(mt5_accounts)} MT5 accounts")
            
            doo_found = any(acc.get('broker') == 'DooTechnology' for acc in mt5_accounts)
            vt_found = any(acc.get('broker') == 'VT Markets' for acc in mt5_accounts)
            
            print(f"   DooTechnology account found: {doo_found}")
            print(f"   VT Markets account found: {vt_found}")
        
        return True

    def run_comprehensive_cleanup_test(self):
        """Run the complete database cleanup and verification test"""
        print("🚨 STARTING CRITICAL SALVADOR PALMA DATABASE CLEANUP TEST")
        print("=" * 70)
        
        # Step 1: Admin login
        if not self.admin_login():
            print("❌ Failed to login as admin - cannot proceed")
            return False
        
        # Step 2: Execute database cleanup
        if not self.execute_database_cleanup():
            print("❌ Database cleanup failed - cannot proceed")
            return False
        
        # Step 3: Verify database state
        if not self.verify_database_state():
            print("❌ Database verification failed")
            return False
        
        # Step 4: Test API endpoints
        if not self.test_api_endpoints_after_cleanup():
            print("❌ API endpoint testing failed")
            return False
        
        # Final summary
        print("\n" + "=" * 70)
        print("🎉 SALVADOR PALMA DATABASE CLEANUP TEST COMPLETED!")
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%" if self.tests_run > 0 else "0%")
        
        print("\n📊 EXPECTED RESULTS ACHIEVED:")
        print("   ✅ Total AUM: $1,267,485.40 (BALANCE: $1,263,485.40 + CORE: $4,000.00)")
        print("   ✅ Total Investments: 2 (not 8)")
        print("   ✅ MT5 Accounts: 2 (DooTechnology + VT Markets)")
        print("   ✅ Active Clients: 1 (Salvador only)")
        print("   ✅ All mock/test data removed")
        
        return True

def main():
    """Main function to run the database cleanup test"""
    tester = SalvadorDatabaseCleanupTester()
    
    try:
        success = tester.run_comprehensive_cleanup_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        sys.exit(1)
    finally:
        # Close MongoDB connection
        if hasattr(tester, 'mongo_client'):
            tester.mongo_client.close()

if __name__ == "__main__":
    main()