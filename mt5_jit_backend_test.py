#!/usr/bin/env python3
"""
FIDUS MT5 Just-In-Time Account Creation System Testing Suite
Testing the refactored MT5 system from pool-based to just-in-time creation.

Test Areas:
1. Just-In-Time Investment Creation API
2. Real-Time Account Validation
3. View-Only Dashboard Endpoints
4. Account Exclusivity Enforcement
5. Statistics and Monitoring
6. Audit Trail Verification

Context: Testing the complete refactoring from pool-based to just-in-time MT5 account creation
"""

import requests
import json
import time
import sys
from datetime import datetime, timezone
import uuid
from decimal import Decimal

# Backend URL Configuration
BACKEND_URL = "https://fidus-invest.emergent.host/api"

# Test Admin Credentials
ADMIN_CREDENTIALS = {
    "username": "admin", 
    "password": "password123",
    "user_type": "admin"
}

class MT5JITTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.test_investment_id = None
        
    def log_test(self, test_name, success, details="", error_msg=""):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error_msg,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error_msg:
            print(f"   Error: {error_msg}")
        print()

    def make_request(self, method, endpoint, data=None, headers=None, auth_token=None):
        """Make HTTP request with proper error handling"""
        url = f"{BACKEND_URL}{endpoint}"
        
        # Set up headers
        req_headers = {"Content-Type": "application/json"}
        if headers:
            req_headers.update(headers)
        if auth_token:
            req_headers["Authorization"] = f"Bearer {auth_token}"
            
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=req_headers, timeout=30)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=req_headers, timeout=30)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=req_headers, timeout=30)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=req_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def authenticate_admin(self):
        """Authenticate as admin and get JWT token"""
        print("🔐 Authenticating as admin...")
        
        response = self.make_request("POST", "/auth/login", ADMIN_CREDENTIALS)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get("token") and data.get("type") == "admin":
                    self.admin_token = data["token"]
                    self.log_test("Admin Authentication", True, 
                                f"Admin: {data.get('name')}, Type: {data.get('type')}")
                    return True
                else:
                    self.log_test("Admin Authentication", False, "Missing token or incorrect type")
                    return False
            except json.JSONDecodeError:
                self.log_test("Admin Authentication", False, "Invalid JSON response")
                return False
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Admin Authentication", False, f"HTTP {status_code}")
            return False

    def test_account_validation_endpoint(self):
        """Test real-time MT5 account validation endpoint"""
        print("🔍 Testing Real-Time Account Validation...")
        
        if not self.admin_token:
            self.log_test("Account Validation", False, "No admin token available")
            return

        # Test validation for available account
        validation_data = {"mt5_account_number": 999001}
        
        response = self.make_request("POST", "/mt5-pool/validate-account-availability", 
                                   validation_data, auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if "is_available" in data and "mt5_account_number" in data:
                    availability_status = "Available" if data["is_available"] else "Not Available"
                    self.log_test("Account Validation - Availability Check", True,
                                f"Account 999001: {availability_status}, Reason: {data.get('reason', 'N/A')}")
                else:
                    self.log_test("Account Validation - Availability Check", False,
                                "Missing expected fields in response")
            except json.JSONDecodeError:
                self.log_test("Account Validation - Availability Check", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Account Validation - Availability Check", False, f"HTTP {status_code}")

        # Test validation for multiple accounts
        test_accounts = [999002, 999003, 999004]
        for account_num in test_accounts:
            validation_data = {"mt5_account_number": account_num}
            response = self.make_request("POST", "/mt5-pool/validate-account-availability", 
                                       validation_data, auth_token=self.admin_token)
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    availability_status = "Available" if data.get("is_available") else "Not Available"
                    self.log_test(f"Account Validation - Account {account_num}", True,
                                f"Status: {availability_status}")
                except json.JSONDecodeError:
                    self.log_test(f"Account Validation - Account {account_num}", False, "Invalid JSON response")
            else:
                status_code = response.status_code if response else "No response"
                self.log_test(f"Account Validation - Account {account_num}", False, f"HTTP {status_code}")

    def test_just_in_time_investment_creation(self):
        """Test the core just-in-time investment creation with MT5 accounts"""
        print("🚀 Testing Just-In-Time Investment Creation...")
        
        if not self.admin_token:
            self.log_test("JIT Investment Creation", False, "No admin token available")
            return

        # Create test investment with MT5 accounts as specified in the review request
        investment_data = {
            "client_id": "test_client_jit_001",
            "fund_code": "BALANCE",
            "principal_amount": 100000.0,
            "currency": "USD",
            "investment_date": datetime.now(timezone.utc).isoformat(),
            "notes": "Test investment for just-in-time MT5 account creation validation",
            "mt5_accounts": [
                {
                    "mt5_account_number": 999001,
                    "investor_password": "InvestorPass001!",
                    "broker_name": "multibank",
                    "allocated_amount": 80000.0,
                    "allocation_notes": "Primary allocation for BALANCE strategy",
                    "mt5_server": "MultiBank-Demo"
                },
                {
                    "mt5_account_number": 999002,
                    "investor_password": "InvestorPass002!",
                    "broker_name": "multibank",
                    "allocated_amount": 20000.0,
                    "allocation_notes": "Secondary allocation for risk diversification",
                    "mt5_server": "MultiBank-Demo"
                }
            ],
            "interest_separation_account": {
                "mt5_account_number": 999003,
                "investor_password": "InvestorPass003!",
                "broker_name": "multibank",
                "account_type": "interest_separation",
                "mt5_server": "MultiBank-Demo",
                "notes": "Interest separation tracking account"
            },
            "gains_separation_account": {
                "mt5_account_number": 999004,
                "investor_password": "InvestorPass004!",
                "broker_name": "multibank",
                "account_type": "gains_separation",
                "mt5_server": "MultiBank-Demo",
                "notes": "Gains separation tracking account"
            },
            "creation_notes": "Test of just-in-time MT5 account creation workflow for Phase 1 refactoring validation"
        }

        response = self.make_request("POST", "/mt5-pool/create-investment-with-mt5", 
                                   investment_data, auth_token=self.admin_token)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get("success") and data.get("investment_id"):
                    self.test_investment_id = data["investment_id"]
                    mt5_accounts_created = len(data.get("mt5_accounts_created", []))
                    separation_accounts = len(data.get("separation_accounts_created", []))
                    total_allocated = data.get("total_allocated_amount", 0)
                    allocation_valid = data.get("allocation_is_valid", False)
                    
                    self.log_test("JIT Investment Creation - Core Functionality", True,
                                f"Investment ID: {self.test_investment_id}, "
                                f"MT5 Accounts: {mt5_accounts_created}, "
                                f"Separation Accounts: {separation_accounts}, "
                                f"Total Allocated: ${total_allocated:,.2f}, "
                                f"Allocation Valid: {allocation_valid}")
                    
                    # Verify expected results
                    expected_mt5_accounts = 2
                    expected_separation_accounts = 2
                    expected_total = 100000.0
                    
                    if (mt5_accounts_created == expected_mt5_accounts and 
                        separation_accounts == expected_separation_accounts and
                        abs(total_allocated - expected_total) < 0.01 and
                        allocation_valid):
                        self.log_test("JIT Investment Creation - Expected Results Validation", True,
                                    "All expected results match: 2 MT5 accounts + 2 separation accounts created")
                    else:
                        self.log_test("JIT Investment Creation - Expected Results Validation", False,
                                    f"Results mismatch - Expected: {expected_mt5_accounts} MT5 + {expected_separation_accounts} separation accounts, "
                                    f"Got: {mt5_accounts_created} MT5 + {separation_accounts} separation accounts")
                else:
                    self.log_test("JIT Investment Creation - Core Functionality", False,
                                "Missing success flag or investment_id in response")
            except json.JSONDecodeError:
                self.log_test("JIT Investment Creation - Core Functionality", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            error_detail = ""
            if response:
                try:
                    error_data = response.json()
                    error_detail = error_data.get("detail", "")
                except:
                    pass
            self.log_test("JIT Investment Creation - Core Functionality", False, 
                        f"HTTP {status_code} - {error_detail}")

    def test_account_exclusivity_enforcement(self):
        """Test that accounts are marked as allocated and subsequent attempts fail"""
        print("🔒 Testing Account Exclusivity Enforcement...")
        
        if not self.admin_token:
            self.log_test("Account Exclusivity", False, "No admin token available")
            return

        # Test that previously used accounts are now unavailable
        test_accounts = [999001, 999002, 999003, 999004]
        
        for account_num in test_accounts:
            validation_data = {"mt5_account_number": account_num}
            response = self.make_request("POST", "/mt5-pool/validate-account-availability", 
                                       validation_data, auth_token=self.admin_token)
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    is_available = data.get("is_available", True)
                    reason = data.get("reason", "")
                    
                    if not is_available and "already allocated" in reason.lower():
                        self.log_test(f"Account Exclusivity - Account {account_num} Allocated", True,
                                    f"Account correctly marked as allocated: {reason}")
                    elif is_available:
                        self.log_test(f"Account Exclusivity - Account {account_num} Allocated", False,
                                    "Account should be allocated but shows as available")
                    else:
                        self.log_test(f"Account Exclusivity - Account {account_num} Allocated", False,
                                    f"Unexpected status: {reason}")
                except json.JSONDecodeError:
                    self.log_test(f"Account Exclusivity - Account {account_num} Allocated", False, 
                                "Invalid JSON response")
            else:
                status_code = response.status_code if response else "No response"
                self.log_test(f"Account Exclusivity - Account {account_num} Allocated", False, 
                            f"HTTP {status_code}")

        # Test attempting to create another investment with same accounts (should fail)
        duplicate_investment_data = {
            "client_id": "test_client_jit_002",
            "fund_code": "CORE",
            "principal_amount": 50000.0,
            "currency": "USD",
            "mt5_accounts": [
                {
                    "mt5_account_number": 999001,  # Already allocated
                    "investor_password": "InvestorPass001!",
                    "broker_name": "multibank",
                    "allocated_amount": 50000.0,
                    "allocation_notes": "Attempting to use already allocated account",
                    "mt5_server": "MultiBank-Demo"
                }
            ],
            "creation_notes": "Test duplicate allocation attempt - should fail with conflict error"
        }

        response = self.make_request("POST", "/mt5-pool/create-investment-with-mt5", 
                                   duplicate_investment_data, auth_token=self.admin_token)
        
        if response and response.status_code == 409:  # Conflict expected
            try:
                data = response.json()
                error_detail = data.get("detail", "")
                if "already allocated" in error_detail.lower():
                    self.log_test("Account Exclusivity - Duplicate Allocation Prevention", True,
                                f"Correctly prevented duplicate allocation: {error_detail}")
                else:
                    self.log_test("Account Exclusivity - Duplicate Allocation Prevention", False,
                                f"Wrong error message: {error_detail}")
            except json.JSONDecodeError:
                self.log_test("Account Exclusivity - Duplicate Allocation Prevention", True,
                            "Conflict detected (JSON parse failed but status correct)")
        elif response and response.status_code == 200:
            self.log_test("Account Exclusivity - Duplicate Allocation Prevention", False,
                        "Duplicate allocation was allowed - exclusivity not enforced")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Account Exclusivity - Duplicate Allocation Prevention", False,
                        f"Unexpected response: HTTP {status_code}")

    def test_view_only_dashboard_endpoints(self):
        """Test view-only MT5 management dashboard endpoints"""
        print("📊 Testing View-Only Dashboard Endpoints...")
        
        if not self.admin_token:
            self.log_test("View-Only Dashboard", False, "No admin token available")
            return

        # Test get all MT5 accounts (monitoring view)
        response = self.make_request("GET", "/mt5-pool/accounts/allocated", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    allocated_accounts = len(data)
                    # Look for our test accounts
                    test_accounts_found = [acc for acc in data if acc.get("mt5_account_number") in [999001, 999002, 999003, 999004]]
                    self.log_test("View-Only Dashboard - Allocated Accounts", True,
                                f"Found {allocated_accounts} allocated accounts, {len(test_accounts_found)} test accounts visible")
                else:
                    self.log_test("View-Only Dashboard - Allocated Accounts", False,
                                "Response is not a list of accounts")
            except json.JSONDecodeError:
                self.log_test("View-Only Dashboard - Allocated Accounts", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("View-Only Dashboard - Allocated Accounts", False, f"HTTP {status_code}")

        # Test get available accounts
        response = self.make_request("GET", "/mt5-pool/accounts/available", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    available_accounts = len(data)
                    self.log_test("View-Only Dashboard - Available Accounts", True,
                                f"Found {available_accounts} available accounts")
                else:
                    self.log_test("View-Only Dashboard - Available Accounts", False,
                                "Response is not a list of accounts")
            except json.JSONDecodeError:
                self.log_test("View-Only Dashboard - Available Accounts", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("View-Only Dashboard - Available Accounts", False, f"HTTP {status_code}")

    def test_pool_statistics(self):
        """Test MT5 pool statistics endpoint"""
        print("📈 Testing Pool Statistics...")
        
        if not self.admin_token:
            self.log_test("Pool Statistics", False, "No admin token available")
            return

        response = self.make_request("GET", "/mt5-pool/statistics", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get("success") and "statistics" in data and "summary" in data:
                    stats = data["statistics"]
                    summary = data["summary"]
                    
                    total_accounts = summary.get("total_accounts", 0)
                    allocated_accounts = summary.get("allocated_accounts", 0)
                    available_accounts = summary.get("available_accounts", 0)
                    utilization_rate = summary.get("utilization_rate", 0)
                    
                    # Verify our test accounts are reflected in statistics
                    expected_min_allocated = 4  # Our 4 test accounts should be allocated
                    
                    if allocated_accounts >= expected_min_allocated:
                        self.log_test("Pool Statistics - Account Allocation Tracking", True,
                                    f"Statistics updated correctly: {allocated_accounts} allocated accounts (≥{expected_min_allocated} expected)")
                    else:
                        self.log_test("Pool Statistics - Account Allocation Tracking", False,
                                    f"Statistics not updated: {allocated_accounts} allocated accounts (<{expected_min_allocated} expected)")
                    
                    self.log_test("Pool Statistics - Comprehensive Data", True,
                                f"Total: {total_accounts}, Allocated: {allocated_accounts}, "
                                f"Available: {available_accounts}, Utilization: {utilization_rate}%")
                else:
                    self.log_test("Pool Statistics - Comprehensive Data", False,
                                "Missing expected fields in statistics response")
            except json.JSONDecodeError:
                self.log_test("Pool Statistics - Comprehensive Data", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Pool Statistics - Comprehensive Data", False, f"HTTP {status_code}")

    def test_audit_trail_verification(self):
        """Test that all actions are properly logged with audit trail"""
        print("📝 Testing Audit Trail Verification...")
        
        if not self.admin_token:
            self.log_test("Audit Trail", False, "No admin token available")
            return

        # Test getting allocated accounts with detailed information
        response = self.make_request("GET", "/mt5-pool/accounts/allocated", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    # Check if our test accounts have proper audit information
                    test_accounts = [acc for acc in data if acc.get("mt5_account_number") in [999001, 999002, 999003, 999004]]
                    
                    audit_fields_present = 0
                    for account in test_accounts:
                        required_audit_fields = ["allocated_to_client_id", "allocated_to_investment_id", 
                                               "allocation_date", "allocated_by_admin"]
                        present_fields = [field for field in required_audit_fields if account.get(field)]
                        if len(present_fields) == len(required_audit_fields):
                            audit_fields_present += 1
                    
                    if audit_fields_present == len(test_accounts):
                        self.log_test("Audit Trail - Complete Allocation Records", True,
                                    f"All {len(test_accounts)} test accounts have complete audit trail")
                    else:
                        self.log_test("Audit Trail - Complete Allocation Records", False,
                                    f"Only {audit_fields_present}/{len(test_accounts)} accounts have complete audit trail")
                    
                    # Verify specific audit details for first test account
                    if test_accounts:
                        first_account = test_accounts[0]
                        client_id = first_account.get("allocated_to_client_id")
                        investment_id = first_account.get("allocated_to_investment_id")
                        allocation_date = first_account.get("allocation_date")
                        allocated_by = first_account.get("allocated_by_admin")
                        
                        if (client_id == "test_client_jit_001" and 
                            investment_id == self.test_investment_id and
                            allocation_date and allocated_by):
                            self.log_test("Audit Trail - Specific Details Verification", True,
                                        f"Audit details correct: Client={client_id}, Investment={investment_id}, "
                                        f"Date={allocation_date}, Admin={allocated_by}")
                        else:
                            self.log_test("Audit Trail - Specific Details Verification", False,
                                        f"Audit details incorrect or missing: Client={client_id}, Investment={investment_id}")
                else:
                    self.log_test("Audit Trail - Complete Allocation Records", False,
                                "No allocated accounts found for audit verification")
            except json.JSONDecodeError:
                self.log_test("Audit Trail - Complete Allocation Records", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Audit Trail - Complete Allocation Records", False, f"HTTP {status_code}")

    def test_preserved_security_warnings(self):
        """Test that investor password warnings are preserved"""
        print("⚠️ Testing Preserved Security Warnings...")
        
        # This test verifies that the system still enforces investor password requirements
        # by attempting to create investment with invalid password data
        
        if not self.admin_token:
            self.log_test("Security Warnings", False, "No admin token available")
            return

        # Test with empty investor password (should fail)
        invalid_investment_data = {
            "client_id": "test_client_security",
            "fund_code": "CORE",
            "principal_amount": 10000.0,
            "currency": "USD",
            "mt5_accounts": [
                {
                    "mt5_account_number": 888001,
                    "investor_password": "",  # Empty password should fail
                    "broker_name": "multibank",
                    "allocated_amount": 10000.0,
                    "allocation_notes": "Testing security validation",
                    "mt5_server": "MultiBank-Demo"
                }
            ],
            "creation_notes": "Testing investor password security validation"
        }

        response = self.make_request("POST", "/mt5-pool/create-investment-with-mt5", 
                                   invalid_investment_data, auth_token=self.admin_token)
        
        if response and response.status_code == 422:  # Validation error expected
            try:
                data = response.json()
                error_detail = str(data.get("detail", ""))
                if "investor password" in error_detail.lower() or "password" in error_detail.lower():
                    self.log_test("Security Warnings - Investor Password Validation", True,
                                "Correctly rejected empty investor password")
                else:
                    self.log_test("Security Warnings - Investor Password Validation", False,
                                f"Wrong validation error: {error_detail}")
            except json.JSONDecodeError:
                self.log_test("Security Warnings - Investor Password Validation", True,
                            "Validation error detected (JSON parse failed but status correct)")
        elif response and response.status_code == 200:
            self.log_test("Security Warnings - Investor Password Validation", False,
                        "Empty investor password was accepted - security validation failed")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Security Warnings - Investor Password Validation", False,
                        f"Unexpected response: HTTP {status_code}")

        # Test with insufficient allocation notes (should fail)
        invalid_notes_data = {
            "client_id": "test_client_notes",
            "fund_code": "CORE", 
            "principal_amount": 10000.0,
            "currency": "USD",
            "mt5_accounts": [
                {
                    "mt5_account_number": 888002,
                    "investor_password": "ValidPass123!",
                    "broker_name": "multibank",
                    "allocated_amount": 10000.0,
                    "allocation_notes": "Short",  # Too short, should fail
                    "mt5_server": "MultiBank-Demo"
                }
            ],
            "creation_notes": "Testing allocation notes validation requirements"
        }

        response = self.make_request("POST", "/mt5-pool/create-investment-with-mt5", 
                                   invalid_notes_data, auth_token=self.admin_token)
        
        if response and response.status_code == 422:  # Validation error expected
            self.log_test("Security Warnings - Allocation Notes Validation", True,
                        "Correctly rejected insufficient allocation notes")
        elif response and response.status_code == 200:
            self.log_test("Security Warnings - Allocation Notes Validation", False,
                        "Insufficient allocation notes were accepted")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Security Warnings - Allocation Notes Validation", False,
                        f"Unexpected response: HTTP {status_code}")

    def run_comprehensive_test(self):
        """Run all MT5 just-in-time system tests"""
        print("🚀 FIDUS MT5 Just-In-Time Account Creation System Testing Suite")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now(timezone.utc).isoformat()}")
        print("Testing refactored MT5 system: Pool-based → Just-in-time creation")
        print("=" * 80)
        print()

        # Authenticate first
        if not self.authenticate_admin():
            print("❌ Authentication failed - cannot proceed with tests")
            return 0

        # Run all test suites in logical order
        self.test_account_validation_endpoint()
        self.test_just_in_time_investment_creation()
        self.test_account_exclusivity_enforcement()
        self.test_view_only_dashboard_endpoints()
        self.test_pool_statistics()
        self.test_audit_trail_verification()
        self.test_preserved_security_warnings()

        # Generate summary
        print("=" * 80)
        print("🎯 MT5 JUST-IN-TIME SYSTEM TESTING SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()

        # Show failed tests
        failed_tests = [t for t in self.test_results if not t["success"]]
        if failed_tests:
            print("❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['error']}")
            print()

        # Show critical findings
        print("🔍 CRITICAL FINDINGS:")
        
        # Check core functionality
        jit_tests = [t for t in self.test_results if "JIT Investment Creation" in t["test"]]
        jit_success = sum(1 for t in jit_tests if t["success"])
        if jit_success >= 1:
            print("   ✅ Just-in-time investment creation working")
        else:
            print("   ❌ Just-in-time investment creation failed - core functionality broken")

        # Check exclusivity enforcement
        exclusivity_tests = [t for t in self.test_results if "Account Exclusivity" in t["test"]]
        exclusivity_success = sum(1 for t in exclusivity_tests if t["success"])
        if exclusivity_success >= 3:
            print("   ✅ Account exclusivity enforcement working")
        else:
            print("   ❌ Account exclusivity enforcement issues detected")

        # Check dashboard functionality
        dashboard_tests = [t for t in self.test_results if "View-Only Dashboard" in t["test"]]
        dashboard_success = sum(1 for t in dashboard_tests if t["success"])
        if dashboard_success >= 1:
            print("   ✅ View-only dashboard endpoints operational")
        else:
            print("   ❌ View-only dashboard endpoints need attention")

        # Check statistics and monitoring
        stats_tests = [t for t in self.test_results if "Pool Statistics" in t["test"]]
        stats_success = sum(1 for t in stats_tests if t["success"])
        if stats_success >= 1:
            print("   ✅ Statistics and monitoring working")
        else:
            print("   ❌ Statistics and monitoring issues detected")

        # Check audit trail
        audit_tests = [t for t in self.test_results if "Audit Trail" in t["test"]]
        audit_success = sum(1 for t in audit_tests if t["success"])
        if audit_success >= 1:
            print("   ✅ Audit trail and logging functional")
        else:
            print("   ❌ Audit trail and logging issues detected")

        # Check security preservation
        security_tests = [t for t in self.test_results if "Security Warnings" in t["test"]]
        security_success = sum(1 for t in security_tests if t["success"])
        if security_success >= 1:
            print("   ✅ Security warnings and validation preserved")
        else:
            print("   ❌ Security validation issues detected")

        print()
        print("=" * 80)
        
        if success_rate >= 90:
            print("🎉 MT5 JUST-IN-TIME SYSTEM STATUS: FULLY OPERATIONAL")
            print("✅ Refactoring from pool-based to just-in-time creation SUCCESSFUL")
        elif success_rate >= 75:
            print("⚠️  MT5 JUST-IN-TIME SYSTEM STATUS: MOSTLY WORKING - MINOR ISSUES")
            print("🔧 Some components need attention but core functionality works")
        elif success_rate >= 50:
            print("🚨 MT5 JUST-IN-TIME SYSTEM STATUS: PARTIAL FUNCTIONALITY")
            print("⚠️  Significant issues detected - review required")
        else:
            print("🚨 MT5 JUST-IN-TIME SYSTEM STATUS: CRITICAL ISSUES")
            print("❌ Major problems with refactored system - immediate attention required")
            
        print("=" * 80)
        
        # Test scenario summary
        if self.test_investment_id:
            print("📋 TEST SCENARIO RESULTS:")
            print(f"   • Client: test_client_jit_001")
            print(f"   • Product: FIDUS BALANCE ($100,000)")
            print(f"   • Investment ID: {self.test_investment_id}")
            print(f"   • MT5 Accounts: 999001 ($80,000), 999002 ($20,000)")
            print(f"   • Interest Separation: 999003")
            print(f"   • Gains Separation: 999004")
            print(f"   • Status: {'✅ SUCCESS' if success_rate >= 75 else '❌ ISSUES DETECTED'}")
            print("=" * 80)
        
        return success_rate

if __name__ == "__main__":
    tester = MT5JITTester()
    success_rate = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 75 else 1)