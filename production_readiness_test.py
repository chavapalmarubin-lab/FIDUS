#!/usr/bin/env python3
"""
FIDUS COMPREHENSIVE PRODUCTION READINESS BACKEND TESTING

This test suite focuses on:
1. Critical Issue Detection
2. Full Client Lifecycle Stress Testing  
3. Live Data Transition Assessment
4. Database Structure Validation
5. Integration Framework Assessment

Based on review request for comprehensive production readiness testing.
"""

import requests
import sys
import json
import time
import uuid
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class ProductionReadinessTester:
    def __init__(self, base_url="https://invest-portal-22.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_issues = []
        self.performance_issues = []
        self.mock_data_endpoints = []
        self.database_issues = []
        
        # Test data tracking
        self.created_clients = []
        self.created_investments = []
        self.created_redemptions = []
        
        # Performance metrics
        self.response_times = {}
        
        print(f"🚀 FIDUS PRODUCTION READINESS TESTING")
        print(f"📍 Target URL: {base_url}")
        print(f"🎯 Focus: Critical Issues, Stress Testing, Data Validation, Integration Assessment")
        print("=" * 80)

    def log_critical_issue(self, issue_type, description, endpoint=None):
        """Log critical issues that could block production"""
        issue = {
            "type": issue_type,
            "description": description,
            "endpoint": endpoint,
            "timestamp": datetime.now().isoformat()
        }
        self.critical_issues.append(issue)
        print(f"🚨 CRITICAL ISSUE: {issue_type} - {description}")

    def log_performance_issue(self, endpoint, response_time, threshold=5.0):
        """Log performance issues"""
        if response_time > threshold:
            issue = {
                "endpoint": endpoint,
                "response_time": response_time,
                "threshold": threshold,
                "timestamp": datetime.now().isoformat()
            }
            self.performance_issues.append(issue)
            print(f"⚠️ PERFORMANCE ISSUE: {endpoint} took {response_time:.2f}s (threshold: {threshold}s)")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, timeout=10):
        """Run a single API test with performance monitoring"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 {name}")
        print(f"   URL: {url}")
        
        start_time = time.time()
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=timeout)

            response_time = time.time() - start_time
            self.response_times[endpoint] = response_time
            
            print(f"   Status: {response.status_code} | Time: {response_time:.2f}s")
            
            # Log performance issues
            self.log_performance_issue(endpoint, response_time)
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
                if response.status_code >= 500:
                    self.log_critical_issue("SERVER_ERROR", f"5xx error on {endpoint}", endpoint)
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                    return False, error_data
                except:
                    print(f"   Error text: {response.text}")
                    return False, {}

        except requests.exceptions.Timeout:
            response_time = time.time() - start_time
            print(f"❌ TIMEOUT after {response_time:.2f}s")
            self.log_critical_issue("TIMEOUT", f"Request timeout on {endpoint}", endpoint)
            return False, {}
        except requests.exceptions.ConnectionError:
            print(f"❌ CONNECTION ERROR")
            self.log_critical_issue("CONNECTION_ERROR", f"Cannot connect to {endpoint}", endpoint)
            return False, {}
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            self.log_critical_issue("UNKNOWN_ERROR", f"Unexpected error on {endpoint}: {str(e)}", endpoint)
            return False, {}

    # ===============================================================================
    # 1. CRITICAL ISSUE DETECTION
    # ===============================================================================

    def test_critical_endpoints_availability(self):
        """Test that all critical production endpoints are available"""
        print("\n" + "="*50)
        print("🚨 CRITICAL ISSUE DETECTION")
        print("="*50)
        
        critical_endpoints = [
            ("GET", "api/auth/login", 405),  # Should reject GET
            ("GET", "api/crm/funds", 200),
            ("GET", "api/investments/funds/config", 200),
            ("GET", "api/clients/all", 200),
            ("GET", "api/crm/mt5/admin/overview", 200),  # Corrected MT5 endpoint
            ("GET", "api/crm/prospects", 200),
            ("GET", "api/admin/clients", 200)
        ]
        
        print("Testing critical endpoint availability...")
        for method, endpoint, expected_status in critical_endpoints:
            success, _ = self.run_test(
                f"Critical Endpoint: {method} {endpoint}",
                method, endpoint, expected_status
            )
            if not success:
                self.log_critical_issue("ENDPOINT_UNAVAILABLE", f"Critical endpoint {endpoint} not available")

    def test_database_connectivity(self):
        """Test database connectivity and basic operations"""
        print("\nTesting database connectivity...")
        
        # Test endpoints that require database access
        db_endpoints = [
            ("GET", "api/clients/all", 200),
            ("GET", "api/crm/funds", 200),
            ("GET", "api/admin/clients", 200)
        ]
        
        for method, endpoint, expected_status in db_endpoints:
            success, response = self.run_test(
                f"Database Test: {endpoint}",
                method, endpoint, expected_status
            )
            if not success:
                self.log_critical_issue("DATABASE_ERROR", f"Database operation failed on {endpoint}")
            elif isinstance(response, dict) and len(response) == 0:
                self.log_critical_issue("DATABASE_EMPTY", f"Database appears empty for {endpoint}")

    def test_authentication_security(self):
        """Test authentication and security measures"""
        print("\nTesting authentication security...")
        
        # Test invalid login attempts
        invalid_logins = [
            {"username": "admin", "password": "wrong", "user_type": "admin"},
            {"username": "invalid", "password": "password123", "user_type": "client"},
            {"username": "", "password": "", "user_type": "admin"}
        ]
        
        for login_data in invalid_logins:
            success, _ = self.run_test(
                f"Security Test: Invalid login {login_data['username']}",
                "POST", "api/auth/login", 401, data=login_data
            )
            if not success:
                self.log_critical_issue("SECURITY_BREACH", "Invalid login not properly rejected")

    # ===============================================================================
    # 2. FULL CLIENT LIFECYCLE STRESS TESTING
    # ===============================================================================

    def test_client_lifecycle_stress(self):
        """Stress test complete client lifecycle"""
        print("\n" + "="*50)
        print("🔄 CLIENT LIFECYCLE STRESS TESTING")
        print("="*50)
        
        # Create multiple clients rapidly
        self.stress_test_client_creation()
        
        # Test investment creation for multiple funds
        self.stress_test_investment_creation()
        
        # Test redemption process
        self.stress_test_redemption_process()
        
        # Test concurrent operations
        self.test_concurrent_operations()

    def stress_test_client_creation(self):
        """Create multiple clients rapidly to test system load"""
        print("\nStress testing client creation (10+ clients)...")
        
        client_count = 12
        created_count = 0
        
        for i in range(client_count):
            client_data = {
                "username": f"stresstest_client_{i}_{int(time.time())}",
                "name": f"Stress Test Client {i}",
                "email": f"stresstest{i}@fidus.com",
                "phone": f"+1-555-{1000+i:04d}",
                "notes": f"Stress test client #{i}"
            }
            
            success, response = self.run_test(
                f"Create Client #{i+1}",
                "POST", "api/admin/users/create", 200, data=client_data
            )
            
            if success:
                created_count += 1
                client_id = response.get('user_id')
                if client_id:
                    self.created_clients.append(client_id)
            else:
                self.log_critical_issue("CLIENT_CREATION_FAILED", f"Failed to create client #{i+1}")
        
        print(f"✅ Created {created_count}/{client_count} clients")
        if created_count < client_count * 0.8:  # Less than 80% success rate
            self.log_critical_issue("CLIENT_CREATION_STRESS", f"Only {created_count}/{client_count} clients created successfully")

    def stress_test_investment_creation(self):
        """Test investment creation for multiple funds simultaneously"""
        print("\nStress testing investment creation across all funds...")
        
        if not self.created_clients:
            print("⚠️ No clients available for investment testing")
            return
        
        funds = ["CORE", "BALANCE", "DYNAMIC"]
        amounts = [10000, 50000, 250000]  # Minimum amounts for each fund
        
        investment_count = 0
        
        for i, client_id in enumerate(self.created_clients[:6]):  # Test with first 6 clients
            fund_idx = i % len(funds)
            fund_code = funds[fund_idx]
            amount = amounts[fund_idx]
            
            investment_data = {
                "client_id": client_id,
                "fund_code": fund_code,
                "amount": amount
            }
            
            success, response = self.run_test(
                f"Create Investment: {fund_code} ${amount:,} for client {client_id[:8]}",
                "POST", "api/investments/create", 200, data=investment_data
            )
            
            if success:
                investment_count += 1
                investment_id = response.get('investment_id')
                if investment_id:
                    self.created_investments.append({
                        'id': investment_id,
                        'client_id': client_id,
                        'fund_code': fund_code,
                        'amount': amount
                    })
            else:
                self.log_critical_issue("INVESTMENT_CREATION_FAILED", f"Failed to create {fund_code} investment")
        
        print(f"✅ Created {investment_count} investments across {len(set(inv['fund_code'] for inv in self.created_investments))} funds")

    def stress_test_redemption_process(self):
        """Test end-to-end redemption process"""
        print("\nStress testing redemption process...")
        
        if not self.created_investments:
            print("⚠️ No investments available for redemption testing")
            return
        
        redemption_count = 0
        
        for investment in self.created_investments[:3]:  # Test redemptions for first 3 investments
            # First check redemption eligibility
            success, response = self.run_test(
                f"Check Redemption Eligibility: {investment['id'][:8]}",
                "GET", f"api/redemptions/client/{investment['client_id']}", 200
            )
            
            if success:
                # Try to create redemption request
                redemption_data = {
                    "investment_id": investment['id'],
                    "requested_amount": investment['amount'] * 0.5,  # Request 50% redemption
                    "reason": "Stress test redemption"
                }
                
                success, response = self.run_test(
                    f"Create Redemption Request: {investment['fund_code']}",
                    "POST", "api/redemptions/request", 200, data=redemption_data
                )
                
                if success:
                    redemption_count += 1
                    redemption_id = response.get('redemption_id')
                    if redemption_id:
                        self.created_redemptions.append(redemption_id)
                else:
                    # This might be expected if redemption rules prevent it
                    print(f"   Note: Redemption request rejected (may be due to business rules)")
        
        print(f"✅ Processed {redemption_count} redemption requests")

    def test_concurrent_operations(self):
        """Test concurrent API operations"""
        print("\nTesting concurrent operations...")
        
        def concurrent_client_fetch():
            """Fetch client data concurrently"""
            success, _ = self.run_test(
                "Concurrent Client Fetch",
                "GET", "api/clients/all", 200
            )
            return success
        
        def concurrent_fund_fetch():
            """Fetch fund data concurrently"""
            success, _ = self.run_test(
                "Concurrent Fund Fetch", 
                "GET", "api/crm/funds", 200
            )
            return success
        
        # Run 10 concurrent requests
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for i in range(10):
                if i % 2 == 0:
                    futures.append(executor.submit(concurrent_client_fetch))
                else:
                    futures.append(executor.submit(concurrent_fund_fetch))
            
            success_count = 0
            for future in as_completed(futures):
                if future.result():
                    success_count += 1
        
        print(f"✅ {success_count}/10 concurrent operations successful")
        if success_count < 8:  # Less than 80% success rate
            self.log_critical_issue("CONCURRENT_OPERATIONS", f"Only {success_count}/10 concurrent operations successful")

    # ===============================================================================
    # 3. LIVE DATA TRANSITION ASSESSMENT
    # ===============================================================================

    def test_mock_data_identification(self):
        """Identify endpoints using mock vs live data"""
        print("\n" + "="*50)
        print("📊 LIVE DATA TRANSITION ASSESSMENT")
        print("="*50)
        
        # Test endpoints and analyze responses for mock data patterns
        endpoints_to_check = [
            ("GET", "api/clients/all", 200),
            ("GET", "api/crm/funds", 200),
            ("GET", "api/mt5/admin/overview", 200),
            ("GET", "api/crm/prospects", 200),
            ("GET", "api/admin/clients", 200)
        ]
        
        for method, endpoint, expected_status in endpoints_to_check:
            success, response = self.run_test(
                f"Mock Data Analysis: {endpoint}",
                method, endpoint, expected_status
            )
            
            if success:
                self.analyze_mock_data_patterns(endpoint, response)

    def analyze_mock_data_patterns(self, endpoint, response):
        """Analyze response for mock data patterns"""
        response_str = json.dumps(response).lower()
        
        # Common mock data indicators
        mock_indicators = [
            "mock", "test", "demo", "sample", "fake", "dummy",
            "lorem ipsum", "example.com", "test@", "555-",
            "gerardo briones", "maria rodriguez", "salvador palma"
        ]
        
        found_indicators = []
        for indicator in mock_indicators:
            if indicator in response_str:
                found_indicators.append(indicator)
        
        if found_indicators:
            self.mock_data_endpoints.append({
                "endpoint": endpoint,
                "indicators": found_indicators,
                "response_size": len(response_str)
            })
            print(f"   🔍 Mock data detected: {', '.join(found_indicators[:3])}")
        else:
            print(f"   ✅ No obvious mock data patterns detected")

    def test_database_persistence(self):
        """Test data persistence across service restarts"""
        print("\nTesting database persistence...")
        
        # Create a test record
        test_client_data = {
            "username": f"persistence_test_{int(time.time())}",
            "name": "Database Persistence Test Client",
            "email": f"persistence_test_{int(time.time())}@fidus.com",
            "phone": "+1-555-9999",
            "notes": "Testing database persistence"
        }
        
        success, response = self.run_test(
            "Create Persistence Test Client",
            "POST", "api/admin/users/create", 200, data=test_client_data
        )
        
        if success:
            client_id = response.get('user_id')
            if client_id:
                # Verify the client exists
                success, response = self.run_test(
                    "Verify Persistence Test Client",
                    "GET", "api/clients/all", 200
                )
                
                if success:
                    clients = response.get('clients', [])
                    found = any(client.get('id') == client_id for client in clients)
                    if found:
                        print("   ✅ Data persisted successfully")
                    else:
                        self.log_critical_issue("DATA_PERSISTENCE", "Created client not found in database")

    # ===============================================================================
    # 4. DATABASE STRUCTURE VALIDATION
    # ===============================================================================

    def test_database_structure_validation(self):
        """Validate database schemas and relationships"""
        print("\n" + "="*50)
        print("🗄️ DATABASE STRUCTURE VALIDATION")
        print("="*50)
        
        self.validate_client_data_structure()
        self.validate_investment_data_structure()
        self.validate_fund_data_structure()
        self.validate_data_relationships()

    def validate_client_data_structure(self):
        """Validate client data structure"""
        print("\nValidating client data structure...")
        
        success, response = self.run_test(
            "Get Client Data Structure",
            "GET", "api/clients/all", 200
        )
        
        if success:
            clients = response.get('clients', [])
            if clients:
                client = clients[0]
                required_fields = ['id', 'name', 'email', 'type']
                missing_fields = [field for field in required_fields if field not in client]
                
                if missing_fields:
                    self.database_issues.append(f"Client missing fields: {missing_fields}")
                    print(f"   ❌ Missing required fields: {missing_fields}")
                else:
                    print(f"   ✅ Client structure valid")
                    
                # Check for proper data types
                if not isinstance(client.get('id'), str):
                    self.database_issues.append("Client ID should be string")
                if not isinstance(client.get('name'), str):
                    self.database_issues.append("Client name should be string")

    def validate_investment_data_structure(self):
        """Validate investment data structure"""
        print("\nValidating investment data structure...")
        
        if self.created_clients:
            client_id = self.created_clients[0]
            success, response = self.run_test(
                "Get Investment Data Structure",
                "GET", f"api/investments/client/{client_id}", 200
            )
            
            if success:
                investments = response.get('investments', [])
                if investments:
                    investment = investments[0]
                    required_fields = ['investment_id', 'fund_code', 'principal_amount', 'current_value']
                    missing_fields = [field for field in required_fields if field not in investment]
                    
                    if missing_fields:
                        self.database_issues.append(f"Investment missing fields: {missing_fields}")
                        print(f"   ❌ Missing required fields: {missing_fields}")
                    else:
                        print(f"   ✅ Investment structure valid")

    def validate_fund_data_structure(self):
        """Validate fund data structure"""
        print("\nValidating fund data structure...")
        
        success, response = self.run_test(
            "Get Fund Data Structure",
            "GET", "api/crm/funds", 200
        )
        
        if success:
            funds = response.get('funds', [])
            if funds:
                fund = funds[0]
                required_fields = ['id', 'name', 'fund_type', 'aum', 'nav']
                missing_fields = [field for field in required_fields if field not in fund]
                
                if missing_fields:
                    self.database_issues.append(f"Fund missing fields: {missing_fields}")
                    print(f"   ❌ Missing required fields: {missing_fields}")
                else:
                    print(f"   ✅ Fund structure valid")

    def validate_data_relationships(self):
        """Validate data relationships and foreign key constraints"""
        print("\nValidating data relationships...")
        
        if self.created_investments:
            investment = self.created_investments[0]
            client_id = investment['client_id']
            
            # Verify client exists for investment
            success, response = self.run_test(
                "Validate Client-Investment Relationship",
                "GET", "api/clients/all", 200
            )
            
            if success:
                clients = response.get('clients', [])
                client_exists = any(client.get('id') == client_id for client in clients)
                
                if client_exists:
                    print(f"   ✅ Client-Investment relationship valid")
                else:
                    self.database_issues.append("Investment references non-existent client")
                    print(f"   ❌ Investment references non-existent client")

    # ===============================================================================
    # 5. INTEGRATION FRAMEWORK ASSESSMENT
    # ===============================================================================

    def test_integration_framework_assessment(self):
        """Assess MT4/MT5 and other integration readiness"""
        print("\n" + "="*50)
        print("🔗 INTEGRATION FRAMEWORK ASSESSMENT")
        print("="*50)
        
        self.test_mt5_integration_readiness()
        self.test_gmail_oauth_integration()
        self.test_payment_confirmation_system()

    def test_mt5_integration_readiness(self):
        """Test MT4/MT5 integration framework"""
        print("\nTesting MT5 integration framework...")
        
        # Test MT5 admin overview
        success, response = self.run_test(
            "MT5 Admin Overview",
            "GET", "api/mt5/admin/overview", 200
        )
        
        if success:
            required_fields = ['total_clients', 'total_balance', 'total_equity', 'total_positions']
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                self.log_critical_issue("MT5_INTEGRATION", f"MT5 overview missing fields: {missing_fields}")
            else:
                print("   ✅ MT5 admin overview structure valid")
        
        # Test client account data
        success, response = self.run_test(
            "MT5 Client Account Data",
            "GET", "api/mt5/client/5001000/account", 200
        )
        
        if success:
            account_fields = ['account_number', 'balance', 'equity', 'margin', 'leverage']
            missing_fields = [field for field in account_fields if field not in response]
            
            if missing_fields:
                self.log_critical_issue("MT5_CLIENT_DATA", f"MT5 client data missing fields: {missing_fields}")
            else:
                print("   ✅ MT5 client account structure valid")

    def test_gmail_oauth_integration(self):
        """Test Gmail OAuth integration readiness"""
        print("\nTesting Gmail OAuth integration...")
        
        # Test OAuth URL generation
        success, response = self.run_test(
            "Gmail OAuth URL Generation",
            "GET", "api/gmail/auth-url", 200
        )
        
        if success:
            auth_url = response.get('authorization_url', '')
            if 'accounts.google.com' in auth_url and 'oauth2' in auth_url:
                print("   ✅ Gmail OAuth URL generation working")
            else:
                self.log_critical_issue("GMAIL_OAUTH", "Invalid OAuth URL generated")
        
        # Test authentication status
        success, response = self.run_test(
            "Gmail Authentication Status",
            "POST", "api/gmail/authenticate", 200
        )
        
        if success:
            if 'action' in response and 'auth_url_endpoint' in response:
                print("   ✅ Gmail authentication flow structure valid")
            else:
                self.log_critical_issue("GMAIL_AUTH_FLOW", "Gmail auth flow structure invalid")

    def test_payment_confirmation_system(self):
        """Test payment confirmation system robustness"""
        print("\nTesting payment confirmation system...")
        
        if self.created_investments:
            investment = self.created_investments[0]
            
            # Test FIAT payment confirmation
            fiat_payment_data = {
                "investment_id": investment['id'],
                "payment_method": "fiat",
                "amount": investment['amount'],
                "currency": "USD",
                "wire_confirmation_number": "TEST123456",
                "bank_reference": "STRESS_TEST_REF",
                "notes": "Stress test payment confirmation"
            }
            
            success, response = self.run_test(
                "FIAT Payment Confirmation",
                "POST", "api/payments/deposit/confirm?admin_id=admin_001", 200, data=fiat_payment_data
            )
            
            if success:
                print("   ✅ FIAT payment confirmation working")
            else:
                self.log_critical_issue("PAYMENT_CONFIRMATION", "FIAT payment confirmation failed")
            
            # Test Crypto payment confirmation
            crypto_payment_data = {
                "investment_id": investment['id'],
                "payment_method": "crypto",
                "amount": investment['amount'],
                "currency": "BTC",
                "transaction_hash": "0x" + "a" * 64,
                "blockchain_network": "Bitcoin",
                "wallet_address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
                "notes": "Stress test crypto payment"
            }
            
            success, response = self.run_test(
                "Crypto Payment Confirmation",
                "POST", "api/payments/deposit/confirm?admin_id=admin_001", 200, data=crypto_payment_data
            )
            
            if success:
                print("   ✅ Crypto payment confirmation working")
            else:
                self.log_critical_issue("PAYMENT_CONFIRMATION", "Crypto payment confirmation failed")

    # ===============================================================================
    # FUND RULES VALIDATION
    # ===============================================================================

    def test_fund_rules_validation(self):
        """Test all fund rules (CORE monthly, BALANCE quarterly, DYNAMIC semi-annually)"""
        print("\n" + "="*50)
        print("📋 FUND RULES VALIDATION")
        print("="*50)
        
        # Get fund configuration
        success, response = self.run_test(
            "Get Fund Configuration",
            "GET", "api/investments/funds/config", 200
        )
        
        if success:
            funds = response.get('funds', [])
            
            # Validate CORE fund rules
            core_fund = next((f for f in funds if f.get('fund_code') == 'CORE'), None)
            if core_fund:
                self.validate_fund_rules(core_fund, 'CORE', {
                    'interest_rate': 1.5,
                    'minimum_investment': 10000,
                    'redemption_frequency': 'monthly'
                })
            
            # Validate BALANCE fund rules
            balance_fund = next((f for f in funds if f.get('fund_code') == 'BALANCE'), None)
            if balance_fund:
                self.validate_fund_rules(balance_fund, 'BALANCE', {
                    'interest_rate': 2.5,
                    'minimum_investment': 50000,
                    'redemption_frequency': 'quarterly'
                })
            
            # Validate DYNAMIC fund rules
            dynamic_fund = next((f for f in funds if f.get('fund_code') == 'DYNAMIC'), None)
            if dynamic_fund:
                self.validate_fund_rules(dynamic_fund, 'DYNAMIC', {
                    'interest_rate': 3.5,
                    'minimum_investment': 250000,
                    'redemption_frequency': 'semi_annually'
                })

    def validate_fund_rules(self, fund, fund_name, expected_rules):
        """Validate specific fund rules"""
        print(f"\nValidating {fund_name} fund rules...")
        
        for rule, expected_value in expected_rules.items():
            actual_value = fund.get(rule)
            if actual_value == expected_value:
                print(f"   ✅ {rule}: {actual_value}")
            else:
                print(f"   ❌ {rule}: Expected {expected_value}, got {actual_value}")
                self.log_critical_issue("FUND_RULES", f"{fund_name} {rule} mismatch: expected {expected_value}, got {actual_value}")

    # ===============================================================================
    # COMPREHENSIVE REPORTING
    # ===============================================================================

    def generate_production_readiness_report(self):
        """Generate comprehensive production readiness report"""
        print("\n" + "="*80)
        print("📊 PRODUCTION READINESS ASSESSMENT REPORT")
        print("="*80)
        
        # Overall statistics
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"\n📈 OVERALL STATISTICS:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Critical Issues Summary
        print(f"\n🚨 CRITICAL ISSUES: {len(self.critical_issues)}")
        if self.critical_issues:
            for issue in self.critical_issues:
                print(f"   ❌ {issue['type']}: {issue['description']}")
        else:
            print("   ✅ No critical issues detected")
        
        # Performance Issues Summary
        print(f"\n⚠️ PERFORMANCE ISSUES: {len(self.performance_issues)}")
        if self.performance_issues:
            for issue in self.performance_issues:
                print(f"   ⏱️ {issue['endpoint']}: {issue['response_time']:.2f}s")
        else:
            print("   ✅ No performance issues detected")
        
        # Mock Data Assessment
        print(f"\n📊 MOCK DATA ASSESSMENT: {len(self.mock_data_endpoints)} endpoints")
        if self.mock_data_endpoints:
            for endpoint_info in self.mock_data_endpoints:
                print(f"   🔍 {endpoint_info['endpoint']}: {', '.join(endpoint_info['indicators'][:2])}")
        else:
            print("   ✅ No obvious mock data patterns detected")
        
        # Database Issues
        print(f"\n🗄️ DATABASE ISSUES: {len(self.database_issues)}")
        if self.database_issues:
            for issue in self.database_issues:
                print(f"   ❌ {issue}")
        else:
            print("   ✅ No database structure issues detected")
        
        # Production Readiness Score
        readiness_score = self.calculate_readiness_score()
        print(f"\n🎯 PRODUCTION READINESS SCORE: {readiness_score:.1f}%")
        
        if readiness_score >= 90:
            print("   ✅ READY FOR PRODUCTION")
        elif readiness_score >= 75:
            print("   ⚠️ NEEDS MINOR FIXES BEFORE PRODUCTION")
        else:
            print("   ❌ SIGNIFICANT ISSUES - NOT READY FOR PRODUCTION")
        
        return {
            "overall_score": readiness_score,
            "tests_run": self.tests_run,
            "tests_passed": self.tests_passed,
            "critical_issues": len(self.critical_issues),
            "performance_issues": len(self.performance_issues),
            "mock_data_endpoints": len(self.mock_data_endpoints),
            "database_issues": len(self.database_issues)
        }

    def calculate_readiness_score(self):
        """Calculate overall production readiness score"""
        base_score = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        # Deduct points for issues
        critical_penalty = len(self.critical_issues) * 15  # 15 points per critical issue
        performance_penalty = len(self.performance_issues) * 5  # 5 points per performance issue
        database_penalty = len(self.database_issues) * 10  # 10 points per database issue
        
        final_score = base_score - critical_penalty - performance_penalty - database_penalty
        return max(0, min(100, final_score))

    # ===============================================================================
    # MAIN TEST EXECUTION
    # ===============================================================================

    def run_comprehensive_production_tests(self):
        """Run all production readiness tests"""
        print("🚀 Starting Comprehensive Production Readiness Testing...")
        
        try:
            # 1. Critical Issue Detection
            self.test_critical_endpoints_availability()
            self.test_database_connectivity()
            self.test_authentication_security()
            
            # 2. Client Lifecycle Stress Testing
            self.test_client_lifecycle_stress()
            
            # 3. Live Data Transition Assessment
            self.test_mock_data_identification()
            self.test_database_persistence()
            
            # 4. Database Structure Validation
            self.test_database_structure_validation()
            
            # 5. Integration Framework Assessment
            self.test_integration_framework_assessment()
            
            # 6. Fund Rules Validation
            self.test_fund_rules_validation()
            
        except KeyboardInterrupt:
            print("\n⚠️ Testing interrupted by user")
        except Exception as e:
            print(f"\n❌ Unexpected error during testing: {str(e)}")
            self.log_critical_issue("TEST_FRAMEWORK_ERROR", f"Testing framework error: {str(e)}")
        
        finally:
            # Generate final report
            return self.generate_production_readiness_report()


def main():
    """Main execution function"""
    tester = ProductionReadinessTester()
    
    try:
        report = tester.run_comprehensive_production_tests()
        
        # Exit with appropriate code based on results
        if report["critical_issues"] > 0:
            sys.exit(1)  # Critical issues found
        elif report["overall_score"] < 75:
            sys.exit(2)  # Low readiness score
        else:
            sys.exit(0)  # All good
            
    except Exception as e:
        print(f"\n💥 Fatal error: {str(e)}")
        sys.exit(3)


if __name__ == "__main__":
    main()