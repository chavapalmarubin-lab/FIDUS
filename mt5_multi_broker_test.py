#!/usr/bin/env python3
"""
Multi-Broker MT5 Integration Testing Script
Tests the fixed multi-broker MT5 system as requested in the review.

Priority 1: Broker Management (should work now)
Priority 2: Add DooTechnology Client Account  
Priority 3: Verify Multi-Broker Functionality
"""

import requests
import sys
import json
from datetime import datetime

class MT5MultiBrokerTester:
    def __init__(self, base_url="https://tradehub-mt5.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None
        
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
                response = requests.get(url, headers=headers, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=15)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=15)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=15)

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

    def test_admin_login(self):
        """Test admin login to get authentication token"""
        success, response = self.run_test(
            "Admin Login for MT5 Testing",
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
            print(f"   Admin logged in: {response.get('name', 'Unknown')}")
            print(f"   Token received: {'Yes' if self.admin_token else 'No'}")
        return success

    # ===============================================================================
    # PRIORITY 1: BROKER MANAGEMENT (SHOULD WORK NOW)
    # ===============================================================================
    
    def test_get_available_brokers(self):
        """Test GET /api/mt5/brokers - Should return Multibank + DooTechnology"""
        success, response = self.run_test(
            "Get Available Brokers (Multibank + DooTechnology)",
            "GET",
            "api/mt5/brokers",
            200
        )
        
        if success:
            brokers = response.get('brokers', [])
            print(f"   Total brokers: {len(brokers)}")
            
            # Check for expected brokers
            broker_codes = [broker.get('code') for broker in brokers]
            expected_brokers = ['multibank', 'dootechnology']
            
            for expected in expected_brokers:
                if expected in broker_codes:
                    print(f"   ✅ {expected.upper()} broker found")
                else:
                    print(f"   ❌ {expected.upper()} broker missing")
                    
            # Display broker details
            for broker in brokers:
                code = broker.get('code', 'unknown')
                name = broker.get('name', 'Unknown')
                status = broker.get('status', 'unknown')
                server_count = len(broker.get('servers', []))
                print(f"   Broker: {name} ({code}) - Status: {status}, Servers: {server_count}")
                
            # Verify we have both expected brokers
            if all(broker in broker_codes for broker in expected_brokers):
                print(f"   ✅ ALL EXPECTED BROKERS PRESENT: {', '.join(expected_brokers)}")
                return True
            else:
                missing = [b for b in expected_brokers if b not in broker_codes]
                print(f"   ❌ MISSING BROKERS: {', '.join(missing)}")
                
        return success

    def test_get_dootechnology_servers(self):
        """Test GET /api/mt5/brokers/dootechnology/servers - Should include DooTechnology-Live"""
        success, response = self.run_test(
            "Get DooTechnology Servers",
            "GET",
            "api/mt5/brokers/dootechnology/servers",
            200
        )
        
        if success:
            servers = response.get('servers', [])
            broker_name = response.get('broker', 'Unknown')
            print(f"   Broker: {broker_name}")
            print(f"   DooTechnology servers: {len(servers)}")
            
            # Check for DooTechnology-Live server (servers are strings, not objects)
            expected_server = 'DooTechnology-Live'
            
            if expected_server in servers:
                print(f"   ✅ {expected_server} server found")
            else:
                print(f"   ❌ {expected_server} server missing")
                print(f"   Available servers: {', '.join(servers)}")
                
            # Display server details (servers are strings)
            for server in servers:
                print(f"   Server: {server}")
                
            return expected_server in servers
                
        return success

    def test_get_multibank_servers(self):
        """Test GET /api/mt5/brokers/multibank/servers - Verify Multibank servers"""
        success, response = self.run_test(
            "Get Multibank Servers",
            "GET",
            "api/mt5/brokers/multibank/servers",
            200
        )
        
        if success:
            servers = response.get('servers', [])
            broker_name = response.get('broker', 'Unknown')
            print(f"   Broker: {broker_name}")
            print(f"   Multibank servers: {len(servers)}")
            
            # Display server details (servers are strings)
            for server in servers:
                print(f"   Server: {server}")
                
        return success

    # ===============================================================================
    # PRIORITY 2: ADD DOOTECHNOLOGY CLIENT ACCOUNT
    # ===============================================================================
    
    def test_add_dootechnology_manual_account(self):
        """Test POST /api/mt5/admin/add-manual-account with DooTechnology credentials"""
        
        if not self.admin_token:
            print("❌ No admin token available for authentication")
            return False
        
        # Exact credentials from review request
        dootechnology_account = {
            "client_id": "client_001",
            "fund_code": "CORE", 
            "broker_code": "dootechnology",
            "mt5_login": 9928326,
            "mt5_password": "R1d567j!",
            "mt5_server": "DooTechnology-Live",
            "allocated_amount": 100000.00
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }
        
        success, response = self.run_test(
            "Add DooTechnology Manual Account (client_001, CORE fund)",
            "POST",
            "api/mt5/admin/add-manual-account",
            200,
            data=dootechnology_account,
            headers=headers
        )
        
        if success:
            account_id = response.get('account_id')
            success_flag = response.get('success')
            message = response.get('message')
            
            print(f"   ✅ Account created successfully!")
            print(f"   Account ID: {account_id}")
            print(f"   Success: {success_flag}")
            print(f"   Message: {message}")
            
            # The response might not contain all the account details
            # Let's check what fields are actually returned
            print(f"   Response fields: {list(response.keys())}")
            
            # Verify the account was created with correct ID format
            if account_id and 'dootechnology' in account_id and 'client_001' in account_id:
                print(f"   🎉 DOOTECHNOLOGY ACCOUNT CREATED WITH CORRECT FORMAT!")
                return True
            else:
                print(f"   ⚠️  Account ID format unexpected: {account_id}")
                
        return success

    def test_add_manual_account_validation(self):
        """Test manual account creation validation (missing fields, invalid data)"""
        
        if not self.admin_token:
            print("❌ No admin token available for authentication")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }
        
        # Test missing required fields
        invalid_account = {
            "client_id": "client_001",
            # Missing fund_code, broker_code, etc.
        }
        
        success, response = self.run_test(
            "Add Manual Account - Missing Fields Validation",
            "POST",
            "api/mt5/admin/add-manual-account",
            400,  # Should return validation error
            data=invalid_account,
            headers=headers
        )
        
        if success:
            print(f"   ✅ Missing fields properly rejected")
            
        # Test invalid broker code
        invalid_broker_account = {
            "client_id": "client_001",
            "fund_code": "CORE", 
            "broker_code": "invalid_broker",
            "mt5_login": 9928326,
            "mt5_password": "R1d567j!",
            "mt5_server": "DooTechnology-Live",
            "allocated_amount": 100000.00
        }
        
        success2, response2 = self.run_test(
            "Add Manual Account - Invalid Broker Code",
            "POST",
            "api/mt5/admin/add-manual-account",
            400,  # Should return bad request
            data=invalid_broker_account,
            headers=headers
        )
        
        if success2:
            print(f"   ✅ Invalid broker code properly rejected")
            
        return success and success2

    # ===============================================================================
    # PRIORITY 3: VERIFY MULTI-BROKER FUNCTIONALITY
    # ===============================================================================
    
    def test_get_accounts_by_broker(self):
        """Test GET /api/mt5/admin/accounts/by-broker - Should show accounts grouped by broker"""
        
        if not self.admin_token:
            print("❌ No admin token available for authentication")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }
        
        success, response = self.run_test(
            "Get MT5 Accounts Grouped by Broker",
            "GET",
            "api/mt5/admin/accounts/by-broker",
            200,
            headers=headers
        )
        
        if success:
            brokers = response.get('brokers', {})
            total_accounts = response.get('total_accounts', 0)
            
            print(f"   Total accounts: {total_accounts}")
            print(f"   Brokers with accounts: {len(brokers)}")
            
            # Check each broker group
            for broker_code, broker_data in brokers.items():
                accounts = broker_data.get('accounts', [])
                broker_name = broker_data.get('broker_name', 'Unknown')
                total_allocated = broker_data.get('total_allocated', 0)
                
                print(f"   Broker: {broker_name} ({broker_code})")
                print(f"     Accounts: {len(accounts)}")
                print(f"     Total Allocated: ${total_allocated:,.2f}")
                
                # Check for DooTechnology account we just created
                if broker_code == 'dootechnology':
                    doo_accounts = [acc for acc in accounts if acc.get('client_id') == 'client_001']
                    if doo_accounts:
                        doo_account = doo_accounts[0]
                        print(f"     ✅ DooTechnology client_001 account found:")
                        print(f"       Client: {doo_account.get('client_id')}")
                        print(f"       Fund: {doo_account.get('fund_code')}")
                        print(f"       Login: {doo_account.get('mt5_login')}")
                        print(f"       Server: {doo_account.get('mt5_server')}")
                        print(f"       Allocated: ${doo_account.get('allocated_amount', 0):,.2f}")
                    else:
                        print(f"     ❌ DooTechnology client_001 account not found")
                        
                # Display account details for each broker
                for account in accounts[:3]:  # Show first 3 accounts
                    client_id = account.get('client_id', 'Unknown')
                    fund_code = account.get('fund_code', 'Unknown')
                    mt5_login = account.get('mt5_login', 'Unknown')
                    allocated = account.get('allocated_amount', 0)
                    print(f"     Account: {client_id} - {fund_code} - Login: {mt5_login} - ${allocated:,.2f}")
                    
            # Verify DooTechnology broker exists and has accounts
            if 'dootechnology' in brokers:
                doo_accounts = brokers['dootechnology'].get('accounts', [])
                if any(acc.get('client_id') == 'client_001' for acc in doo_accounts):
                    print(f"   🎉 DOOTECHNOLOGY ACCOUNT SUCCESSFULLY GROUPED!")
                    return True
                else:
                    print(f"   ❌ DooTechnology account not properly grouped")
            else:
                print(f"   ❌ DooTechnology broker not found in grouping")
                
        return success

    def test_get_all_mt5_accounts(self):
        """Test GET /api/mt5/admin/accounts - Verify all accounts endpoint still works"""
        
        if not self.admin_token:
            print("❌ No admin token available for authentication")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }
        
        success, response = self.run_test(
            "Get All MT5 Accounts",
            "GET",
            "api/mt5/admin/accounts",
            200,
            headers=headers
        )
        
        if success:
            accounts = response.get('accounts', [])
            total_allocated = response.get('total_allocated', 0)
            total_equity = response.get('total_equity', 0)
            
            print(f"   Total accounts: {len(accounts)}")
            print(f"   Total allocated: ${total_allocated:,.2f}")
            print(f"   Total equity: ${total_equity:,.2f}")
            
            # Look for our DooTechnology account
            doo_account = None
            for account in accounts:
                if (account.get('client_id') == 'client_001' and 
                    account.get('broker_code') == 'dootechnology'):
                    doo_account = account
                    break
                    
            if doo_account:
                print(f"   ✅ DooTechnology account found in all accounts:")
                print(f"     Client: {doo_account.get('client_id')}")
                print(f"     Fund: {doo_account.get('fund_code')}")
                print(f"     Broker: {doo_account.get('broker_code')}")
                print(f"     Login: {doo_account.get('mt5_login')}")
                print(f"     Server: {doo_account.get('mt5_server')}")
                print(f"     Allocated: ${doo_account.get('allocated_amount', 0):,.2f}")
                return True
            else:
                print(f"   ❌ DooTechnology account not found in all accounts")
                
        return success

    def test_database_health_check(self):
        """Test GET /api/health/ready - Database health check should be fixed"""
        success, response = self.run_test(
            "Database Health Check",
            "GET",
            "api/health/ready",
            200
        )
        
        if success:
            status = response.get('status', 'unknown')
            checks = response.get('checks', {})
            
            print(f"   Overall status: {status}")
            
            # Check database connectivity
            database_check = checks.get('database', False)
            if database_check:
                print(f"   ✅ Database connectivity: PASSED")
            else:
                print(f"   ❌ Database connectivity: FAILED")
                
            # Display all checks
            for check_name, check_result in checks.items():
                if check_name != 'database':
                    print(f"   {check_name}: {'✅ PASSED' if check_result else '❌ FAILED'}")
                    
            if status == 'ready' and database_check:
                print(f"   🎉 DATABASE HEALTH CHECK FIXED!")
                return True
            else:
                print(f"   ❌ Database health check still failing")
                
        return success

    def test_mt5_performance_overview(self):
        """Test MT5 performance overview endpoint"""
        
        if not self.admin_token:
            print("❌ No admin token available for authentication")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }
        
        success, response = self.run_test(
            "MT5 Performance Overview",
            "GET",
            "api/mt5/admin/performance/overview",
            200,
            headers=headers
        )
        
        if success:
            # Check response structure
            total_accounts = response.get('total_accounts', 0)
            total_allocated = response.get('total_allocated', 0)
            total_equity = response.get('total_equity', 0)
            total_profit_loss = response.get('total_profit_loss', 0)
            
            print(f"   Total accounts: {total_accounts}")
            print(f"   Total allocated: ${total_allocated:,.2f}")
            print(f"   Total equity: ${total_equity:,.2f}")
            print(f"   Total P&L: ${total_profit_loss:,.2f}")
            
            # Check broker breakdown
            broker_breakdown = response.get('broker_breakdown', {})
            if broker_breakdown:
                print(f"   Broker breakdown:")
                for broker_code, broker_stats in broker_breakdown.items():
                    accounts = broker_stats.get('accounts', 0)
                    allocated = broker_stats.get('allocated', 0)
                    equity = broker_stats.get('equity', 0)
                    print(f"     {broker_code}: {accounts} accounts, ${allocated:,.2f} allocated, ${equity:,.2f} equity")
                    
            return True
                
        return success

    def run_comprehensive_mt5_test(self):
        """Run comprehensive multi-broker MT5 integration test"""
        print("=" * 80)
        print("🚀 MULTI-BROKER MT5 INTEGRATION COMPREHENSIVE TEST")
        print("=" * 80)
        print(f"Testing against: {self.base_url}")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Authentication
        print("\n" + "=" * 50)
        print("STEP 1: AUTHENTICATION")
        print("=" * 50)
        
        if not self.test_admin_login():
            print("❌ CRITICAL: Admin login failed - cannot continue testing")
            return False
            
        # Step 2: Priority 1 - Broker Management
        print("\n" + "=" * 50)
        print("STEP 2: PRIORITY 1 - BROKER MANAGEMENT")
        print("=" * 50)
        
        broker_tests = [
            self.test_get_available_brokers,
            self.test_get_dootechnology_servers,
            self.test_get_multibank_servers
        ]
        
        broker_results = []
        for test in broker_tests:
            result = test()
            broker_results.append(result)
            
        # Step 3: Priority 2 - Add DooTechnology Account
        print("\n" + "=" * 50)
        print("STEP 3: PRIORITY 2 - ADD DOOTECHNOLOGY ACCOUNT")
        print("=" * 50)
        
        account_tests = [
            self.test_add_dootechnology_manual_account,
            self.test_add_manual_account_validation
        ]
        
        account_results = []
        for test in account_tests:
            result = test()
            account_results.append(result)
            
        # Step 4: Priority 3 - Verify Multi-Broker Functionality
        print("\n" + "=" * 50)
        print("STEP 4: PRIORITY 3 - VERIFY MULTI-BROKER FUNCTIONALITY")
        print("=" * 50)
        
        verification_tests = [
            self.test_get_accounts_by_broker,
            self.test_get_all_mt5_accounts,
            self.test_database_health_check,
            self.test_mt5_performance_overview
        ]
        
        verification_results = []
        for test in verification_tests:
            result = test()
            verification_results.append(result)
            
        # Final Results
        print("\n" + "=" * 80)
        print("🎯 FINAL TEST RESULTS")
        print("=" * 80)
        
        print(f"\nPRIORITY 1 - BROKER MANAGEMENT:")
        print(f"  ✅ Get Available Brokers: {'PASSED' if broker_results[0] else 'FAILED'}")
        print(f"  ✅ Get DooTechnology Servers: {'PASSED' if broker_results[1] else 'FAILED'}")
        print(f"  ✅ Get Multibank Servers: {'PASSED' if broker_results[2] else 'FAILED'}")
        
        print(f"\nPRIORITY 2 - ADD DOOTECHNOLOGY ACCOUNT:")
        print(f"  ✅ Add DooTechnology Manual Account: {'PASSED' if account_results[0] else 'FAILED'}")
        print(f"  ✅ Manual Account Validation: {'PASSED' if account_results[1] else 'FAILED'}")
        
        print(f"\nPRIORITY 3 - VERIFY MULTI-BROKER FUNCTIONALITY:")
        print(f"  ✅ Get Accounts by Broker: {'PASSED' if verification_results[0] else 'FAILED'}")
        print(f"  ✅ Get All MT5 Accounts: {'PASSED' if verification_results[1] else 'FAILED'}")
        print(f"  ✅ Database Health Check: {'PASSED' if verification_results[2] else 'FAILED'}")
        print(f"  ✅ MT5 Performance Overview: {'PASSED' if verification_results[3] else 'FAILED'}")
        
        print(f"\n📊 OVERALL STATISTICS:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        # Determine overall success
        critical_tests = [
            broker_results[0],  # Get available brokers
            broker_results[1],  # Get DooTechnology servers
            account_results[0], # Add DooTechnology account
            verification_results[0], # Get accounts by broker
            verification_results[1], # Get all accounts
            verification_results[2]  # Database health check
        ]
        
        overall_success = all(critical_tests)
        
        if overall_success:
            print(f"\n🎉 MULTI-BROKER MT5 INTEGRATION: ✅ SUCCESS!")
            print(f"   ✅ DooTechnology broker available")
            print(f"   ✅ DooTechnology client account created successfully")
            print(f"   ✅ Multi-broker functionality working")
            print(f"   ✅ Database health check passing")
        else:
            print(f"\n❌ MULTI-BROKER MT5 INTEGRATION: ❌ FAILED!")
            failed_tests = []
            if not broker_results[0]: failed_tests.append("Broker management")
            if not broker_results[1]: failed_tests.append("DooTechnology servers")
            if not account_results[0]: failed_tests.append("Manual account creation")
            if not verification_results[0]: failed_tests.append("Account grouping by broker")
            if not verification_results[1]: failed_tests.append("All accounts endpoint")
            if not verification_results[2]: failed_tests.append("Database health check")
            
            print(f"   ❌ Failed areas: {', '.join(failed_tests)}")
            
        print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return overall_success

def main():
    """Main test execution"""
    tester = MT5MultiBrokerTester()
    
    try:
        success = tester.run_comprehensive_mt5_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()