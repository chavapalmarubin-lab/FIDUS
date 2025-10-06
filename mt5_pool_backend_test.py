#!/usr/bin/env python3
"""
FIDUS MT5 Account Pool Management System Testing Suite - CORRECTED ROUTING
Testing the corrected MT5 pool endpoints after fixing the routing issue.

ISSUE FIXED: MT5 pool router was included with prefix `/mt5pool` instead of `/mt5/pool`
CORRECTED ENDPOINTS TO TEST:
1. `/api/mt5/pool/test` - Simple test endpoint to verify router is working
2. `/api/mt5/pool/validate-account-availability` - Check if MT5 account is available
3. `/api/mt5/pool/create-investment-with-mt5` - Create investment with MT5 accounts
4. `/api/mt5/pool/accounts` - Get all MT5 accounts (monitoring view)
5. `/api/mt5/pool/statistics` - Get pool statistics

Test Scenario: Just-In-Time Investment Creation workflow
Expected: All endpoints accessible with HTTP 200 instead of 404
"""

import requests
import json
import time
import sys
from datetime import datetime, timezone
import uuid

# Backend URL Configuration - Use from frontend .env
BACKEND_URL = "https://fidus-finance-api.preview.emergentagent.com/api"

# Admin Authentication
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "password123", 
    "user_type": "admin"
}

class MT5PoolTestSuite:
    def __init__(self):
        self.admin_token = None
        self.test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        
    def log_test(self, test_name, success, details=""):
        """Log test result"""
        self.test_results["total_tests"] += 1
        if success:
            self.test_results["passed"] += 1
            print(f"✅ {test_name}: PASSED {details}")
        else:
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {details}")
            print(f"❌ {test_name}: FAILED {details}")
    
    def authenticate_admin(self):
        """Authenticate as admin and get JWT token"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                self.log_test("Admin Authentication", True, f"Token obtained: {self.admin_token[:20]}...")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_auth_headers(self):
        """Get authorization headers with JWT token"""
        if not self.admin_token:
            return {}
        return {"Authorization": f"Bearer {self.admin_token}"}
    
    def test_mt5_pool_health(self):
        """Test MT5 pool health check endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/mt5-pool/health")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify health check response structure
                required_fields = ["status", "service", "timestamp", "version", "features"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("MT5 Pool Health Check", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Verify Phase 1 features
                expected_features = [
                    "MT5 Account Pool Management",
                    "Multiple Account Mapping Support",
                    "Allocation/Deallocation Workflow", 
                    "Account Exclusivity Enforcement",
                    "Comprehensive Audit Trail",
                    "⚠️ INVESTOR PASSWORD ONLY System"
                ]
                
                features = data.get("features", [])
                missing_features = [f for f in expected_features if f not in features]
                
                if missing_features:
                    self.log_test("MT5 Pool Health Check", False, f"Missing features: {missing_features}")
                    return False
                
                # Verify service details
                if data.get("service") != "MT5 Account Pool Management":
                    self.log_test("MT5 Pool Health Check", False, f"Wrong service name: {data.get('service')}")
                    return False
                
                if "Phase 1" not in data.get("version", ""):
                    self.log_test("MT5 Pool Health Check", False, f"Version doesn't indicate Phase 1: {data.get('version')}")
                    return False
                
                self.log_test("MT5 Pool Health Check", True, f"Status: {data.get('status')}, Version: {data.get('version')}")
                return True
                
            else:
                self.log_test("MT5 Pool Health Check", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("MT5 Pool Health Check", False, f"Exception: {str(e)}")
            return False
    
    def test_pool_statistics(self):
        """Test MT5 pool statistics endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/mt5-pool/statistics", headers=self.get_auth_headers())
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if not data.get("success"):
                    self.log_test("Pool Statistics", False, f"Success flag is false: {data}")
                    return False
                
                statistics = data.get("statistics", {})
                summary = data.get("summary", {})
                
                # Verify expected statistics fields
                required_stats = ["total_accounts", "available", "allocated", "pending_deallocation"]
                missing_stats = [field for field in required_stats if field not in statistics]
                
                if missing_stats:
                    self.log_test("Pool Statistics", False, f"Missing statistics: {missing_stats}")
                    return False
                
                # Verify summary fields
                required_summary = ["total_accounts", "utilization_rate", "available_accounts", "allocated_accounts"]
                missing_summary = [field for field in required_summary if field not in summary]
                
                if missing_summary:
                    self.log_test("Pool Statistics", False, f"Missing summary fields: {missing_summary}")
                    return False
                
                # Check for expected 10 MT5 accounts (8 MULTIBANK + 2 DOOTECHNOLOGY)
                total_accounts = statistics.get("total_accounts", 0)
                if total_accounts != 10:
                    self.log_test("Pool Statistics", False, f"Expected 10 accounts, got {total_accounts}")
                    return False
                
                # Verify utilization calculation
                available = statistics.get("available", 0)
                allocated = statistics.get("allocated", 0)
                
                if available + allocated != total_accounts:
                    self.log_test("Pool Statistics", False, f"Account counts don't add up: {available} + {allocated} != {total_accounts}")
                    return False
                
                self.log_test("Pool Statistics", True, f"Total: {total_accounts}, Available: {available}, Allocated: {allocated}")
                return True
                
            else:
                self.log_test("Pool Statistics", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Pool Statistics", False, f"Exception: {str(e)}")
            return False
    
    def test_available_accounts(self):
        """Test available MT5 accounts endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/mt5-pool/accounts/available", headers=self.get_auth_headers())
            
            if response.status_code == 200:
                accounts = response.json()
                
                if not isinstance(accounts, list):
                    self.log_test("Available Accounts", False, f"Expected list, got {type(accounts)}")
                    return False
                
                # Verify account structure
                if len(accounts) > 0:
                    account = accounts[0]
                    required_fields = ["pool_id", "mt5_account_number", "broker_name", "account_type", "status"]
                    missing_fields = [field for field in required_fields if field not in account]
                    
                    if missing_fields:
                        self.log_test("Available Accounts", False, f"Missing account fields: {missing_fields}")
                        return False
                    
                    # Verify account is not allocated
                    if account.get("is_allocated", True):
                        self.log_test("Available Accounts", False, f"Available account shows as allocated: {account}")
                        return False
                
                # Check for expected brokers (multibank and dootechnology)
                brokers = set(account.get("broker_name", "") for account in accounts)
                expected_brokers = {"multibank", "dootechnology"}
                
                if not expected_brokers.issubset(brokers):
                    missing_brokers = expected_brokers - brokers
                    self.log_test("Available Accounts", False, f"Missing expected brokers: {missing_brokers}, Found: {brokers}")
                    return False
                
                self.log_test("Available Accounts", True, f"Found {len(accounts)} available accounts from brokers: {brokers}")
                return True
                
            else:
                self.log_test("Available Accounts", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Available Accounts", False, f"Exception: {str(e)}")
            return False
    
    def test_allocated_accounts(self):
        """Test allocated MT5 accounts endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/mt5-pool/accounts/allocated", headers=self.get_auth_headers())
            
            if response.status_code == 200:
                accounts = response.json()
                
                if not isinstance(accounts, list):
                    self.log_test("Allocated Accounts", False, f"Expected list, got {type(accounts)}")
                    return False
                
                # Verify account structure if any allocated accounts exist
                if len(accounts) > 0:
                    account = accounts[0]
                    required_fields = ["pool_id", "mt5_account_number", "broker_name", "allocated_to_client_id", "allocation_date"]
                    missing_fields = [field for field in required_fields if field not in account]
                    
                    if missing_fields:
                        self.log_test("Allocated Accounts", False, f"Missing allocated account fields: {missing_fields}")
                        return False
                    
                    # Verify allocation data is present
                    if not account.get("allocated_to_client_id"):
                        self.log_test("Allocated Accounts", False, f"Allocated account missing client_id: {account}")
                        return False
                
                self.log_test("Allocated Accounts", True, f"Found {len(accounts)} allocated accounts")
                return True
                
            else:
                self.log_test("Allocated Accounts", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Allocated Accounts", False, f"Exception: {str(e)}")
            return False
    
    def test_account_exclusivity_check(self):
        """Test MT5 account exclusivity check"""
        try:
            # First get an available account to test
            available_response = requests.get(f"{BACKEND_URL}/mt5-pool/accounts/available", headers=self.get_auth_headers())
            
            if available_response.status_code != 200:
                self.log_test("Account Exclusivity Check", False, "Could not get available accounts for testing")
                return False
            
            available_accounts = available_response.json()
            if not available_accounts:
                self.log_test("Account Exclusivity Check", False, "No available accounts to test exclusivity")
                return False
            
            # Test exclusivity check on first available account
            test_account = available_accounts[0]
            account_number = test_account["mt5_account_number"]
            
            response = requests.get(f"{BACKEND_URL}/mt5-pool/accounts/{account_number}/exclusivity-check", headers=self.get_auth_headers())
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if not data.get("success"):
                    self.log_test("Account Exclusivity Check", False, f"Success flag is false: {data}")
                    return False
                
                exclusivity_check = data.get("exclusivity_check", {})
                
                # Verify exclusivity check structure
                required_fields = ["is_available", "reason"]
                missing_fields = [field for field in required_fields if field not in exclusivity_check]
                
                if missing_fields:
                    self.log_test("Account Exclusivity Check", False, f"Missing exclusivity fields: {missing_fields}")
                    return False
                
                # For available account, should be available for allocation
                if not exclusivity_check.get("is_available"):
                    self.log_test("Account Exclusivity Check", False, f"Available account shows as not available: {exclusivity_check}")
                    return False
                
                # Verify message indicates availability
                message = data.get("message", "")
                if "Available for allocation" not in message:
                    self.log_test("Account Exclusivity Check", False, f"Message doesn't indicate availability: {message}")
                    return False
                
                self.log_test("Account Exclusivity Check", True, f"Account {account_number}: {message}")
                return True
                
            else:
                self.log_test("Account Exclusivity Check", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Account Exclusivity Check", False, f"Exception: {str(e)}")
            return False
    
    def test_add_account_to_pool(self):
        """Test adding MT5 account to pool with INVESTOR PASSWORD warnings"""
        try:
            # Create test account data
            test_account = {
                "mt5_account_number": 99999999,  # Test account number (within valid range)
                "broker_name": "multibank",
                "account_type": "investment",
                "mt5_server": "TestServer-Demo",
                "investor_password": "TestInvestorPass123",
                "notes": "Test account for MT5 pool testing"
            }
            
            response = requests.post(f"{BACKEND_URL}/mt5-pool/accounts", json=test_account, headers=self.get_auth_headers())
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if not data.get("success"):
                    self.log_test("Add Account to Pool", False, f"Success flag is false: {data}")
                    return False
                
                # Verify success message
                message = data.get("message", "")
                if "added to pool successfully" not in message:
                    self.log_test("Add Account to Pool", False, f"Success message missing: {message}")
                    return False
                
                # Verify INVESTOR PASSWORD warning is present
                warning = data.get("warning", "")
                if "INVESTOR password" not in warning:
                    self.log_test("Add Account to Pool", False, f"INVESTOR PASSWORD warning missing: {warning}")
                    return False
                
                # Verify account details in response
                account = data.get("account", {})
                if account.get("mt5_account_number") != test_account["mt5_account_number"]:
                    self.log_test("Add Account to Pool", False, f"Account number mismatch: {account}")
                    return False
                
                self.log_test("Add Account to Pool", True, f"Account {test_account['mt5_account_number']} added with INVESTOR PASSWORD warning")
                return True
                
            elif response.status_code == 400:
                # Account might already exist or validation error
                error_detail = response.json().get("detail", response.text)
                if "already exists" in error_detail:
                    self.log_test("Add Account to Pool", True, f"Account already exists (expected): {error_detail}")
                    return True
                else:
                    self.log_test("Add Account to Pool", False, f"Validation error: {error_detail}")
                    return False
                    
            else:
                self.log_test("Add Account to Pool", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Add Account to Pool", False, f"Exception: {str(e)}")
            return False
    
    def test_validate_mappings(self):
        """Test investment mapping validation"""
        try:
            # Create test validation data
            validation_data = {
                "investment_id": f"test_investment_{uuid.uuid4()}",
                "total_investment_amount": 100000.00
            }
            
            response = requests.post(f"{BACKEND_URL}/mt5-pool/validate-mappings", json=validation_data, headers=self.get_auth_headers())
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if not data.get("success"):
                    self.log_test("Validate Mappings", False, f"Success flag is false: {data}")
                    return False
                
                validation_result = data.get("validation_result", {})
                
                # Verify validation result structure
                required_fields = ["is_valid", "total_investment_amount", "total_mapped_amount", "difference", "mappings_count"]
                missing_fields = [field for field in required_fields if field not in validation_result]
                
                if missing_fields:
                    self.log_test("Validate Mappings", False, f"Missing validation fields: {missing_fields}")
                    return False
                
                # Verify summary structure
                summary = data.get("summary", {})
                required_summary = ["total_investment", "total_mapped", "difference", "mappings_count"]
                missing_summary = [field for field in required_summary if field not in summary]
                
                if missing_summary:
                    self.log_test("Validate Mappings", False, f"Missing summary fields: {missing_summary}")
                    return False
                
                # For new investment with no mappings, should be invalid (0 mapped vs investment amount)
                is_valid = validation_result.get("is_valid")
                mappings_count = validation_result.get("mappings_count", 0)
                
                if mappings_count == 0 and is_valid:
                    self.log_test("Validate Mappings", False, f"Empty mappings should be invalid but shows valid: {validation_result}")
                    return False
                
                self.log_test("Validate Mappings", True, f"Validation working: Valid={is_valid}, Mappings={mappings_count}")
                return True
                
            else:
                self.log_test("Validate Mappings", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Validate Mappings", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all MT5 pool management tests"""
        print("🚀 Starting MT5 Account Pool Management System Testing - Phase 1")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print(f"⏰ Test Start Time: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Run all tests
        tests = [
            self.test_mt5_pool_health,
            self.test_pool_statistics,
            self.test_available_accounts,
            self.test_allocated_accounts,
            self.test_account_exclusivity_check,
            self.test_add_account_to_pool,
            self.test_validate_mappings
        ]
        
        for test in tests:
            try:
                test()
                time.sleep(0.5)  # Brief pause between tests
            except Exception as e:
                self.log_test(test.__name__, False, f"Test execution error: {str(e)}")
        
        # Print summary
        print("=" * 80)
        print("🎯 MT5 ACCOUNT POOL MANAGEMENT TESTING SUMMARY")
        print(f"📊 Total Tests: {self.test_results['total_tests']}")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        
        if self.test_results['failed'] > 0:
            print("\n🚨 FAILED TESTS:")
            for error in self.test_results['errors']:
                print(f"   • {error}")
        
        success_rate = (self.test_results['passed'] / self.test_results['total_tests']) * 100 if self.test_results['total_tests'] > 0 else 0
        print(f"\n📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 85:
            print("🎉 MT5 ACCOUNT POOL MANAGEMENT SYSTEM: PHASE 1 OPERATIONAL")
        elif success_rate >= 70:
            print("⚠️ MT5 ACCOUNT POOL MANAGEMENT SYSTEM: MOSTLY FUNCTIONAL WITH MINOR ISSUES")
        else:
            print("🚨 MT5 ACCOUNT POOL MANAGEMENT SYSTEM: CRITICAL ISSUES DETECTED")
        
        print(f"⏰ Test End Time: {datetime.now(timezone.utc).isoformat()}")
        
        return success_rate >= 70

if __name__ == "__main__":
    tester = MT5PoolTestSuite()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)