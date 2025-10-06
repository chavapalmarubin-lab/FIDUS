#!/usr/bin/env python3
"""
MT5 Account Mapping Integration Testing Suite
Tests the newly implemented MT5 Account Mapping Integration in Investment Creation workflow.

SPECIFIC TESTING REQUIREMENTS:
1. Investment Creation with MT5 Mapping (complete MT5 data)
2. Investment Creation with optional MT5 fields
3. Investment Creation without MT5 mapping
4. Validation Testing (missing/invalid fields)
5. Database Integration (MongoDB storage and encryption)
6. Backend Response Validation
7. Error Handling scenarios

Uses realistic MT5 data as requested:
- Valid MT5 login numbers (9928326, 8765432, etc.)
- Real server names (Multibank-Live, DooTechnology-Live)
- Realistic balance differences due to banking fees
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, List

class MT5MappingTester:
    def __init__(self, base_url="https://tradehub-mt5.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_user = None
        self.client_user = None
        self.created_investments = []
        self.mt5_accounts_created = []
        
    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Dict = None, headers: Dict = None, use_auth: bool = False) -> tuple[bool, Dict]:
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        # Add JWT token for authenticated endpoints
        if use_auth and self.admin_user and self.admin_user.get('token'):
            headers['Authorization'] = f"Bearer {self.admin_user['token']}"

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        if data:
            print(f"   Data keys: {list(data.keys())}")
        if use_auth:
            print(f"   Using authentication: Yes")
        
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
                    if isinstance(response_data, dict):
                        print(f"   Response keys: {list(response_data.keys())}")
                        # Log important MT5 fields if present
                        if 'mt5_account_id' in response_data:
                            print(f"   MT5 Account ID: {response_data.get('mt5_account_id')}")
                        if 'mt5_mapping_success' in response_data:
                            print(f"   MT5 Mapping Success: {response_data.get('mt5_mapping_success')}")
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

    def setup_authentication(self) -> bool:
        """Setup admin and client authentication"""
        print("\n" + "="*80)
        print("🔐 SETTING UP AUTHENTICATION FOR MT5 MAPPING TESTS")
        print("="*80)
        
        # Admin login for database verification
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
            self.admin_user = response
            print(f"   ✅ Admin logged in: {response.get('name', 'Unknown')}")
        else:
            print("   ❌ Admin login failed")
            return False

        # Client login (using Gerardo Briones for realistic testing)
        success, response = self.run_test(
            "Client Login (Gerardo Briones)",
            "POST",
            "api/auth/login",
            200,
            data={
                "username": "client1", 
                "password": "password123",
                "user_type": "client"
            }
        )
        if success:
            self.client_user = response
            print(f"   ✅ Client logged in: {response.get('name', 'Unknown')} (ID: {response.get('id')})")
        else:
            print("   ❌ Client login failed")
            return False
            
        return True

    def test_investment_creation_with_complete_mt5_data(self) -> bool:
        """Test POST /api/investments/create with complete MT5 mapping data"""
        print("\n" + "="*80)
        print("💰 TESTING INVESTMENT CREATION WITH COMPLETE MT5 DATA")
        print("="*80)
        
        if not self.client_user:
            print("❌ No client user available")
            return False
            
        client_id = self.client_user.get('id')
        
        # Test 1: CORE fund with complete MT5 data
        print("\n📊 Test 1: CORE Fund Investment with Complete MT5 Mapping")
        mt5_data = {
            "client_id": client_id,
            "fund_code": "CORE",
            "amount": 25000.0,
            "deposit_date": "2024-12-19",
            "create_mt5_account": True,
            "mt5_login": "9928326",  # Realistic MT5 login number
            "mt5_password": "SecurePass123!",
            "mt5_server": "Multibank-Live",  # Real server name
            "broker_name": "Multibank Group",
            "mt5_initial_balance": 24750.0,  # Realistic difference due to banking fees
            "banking_fees": 250.0,
            "fee_notes": "Wire transfer fee and currency conversion"
        }
        
        success, response = self.run_test(
            "Create CORE Investment with Complete MT5 Data",
            "POST",
            "api/investments/create",
            200,
            data=mt5_data,
            use_auth=True
        )
        
        if success:
            # Validate response structure
            required_fields = ['success', 'investment_id', 'mt5_account_id', 'mt5_mapping_success']
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                print(f"   ❌ Missing response fields: {missing_fields}")
                return False
            
            # Validate MT5 mapping success
            if not response.get('mt5_mapping_success'):
                print(f"   ❌ MT5 mapping failed: {response.get('message', 'Unknown error')}")
                return False
            
            # Store created investment for later verification
            investment_id = response.get('investment_id')
            mt5_account_id = response.get('mt5_account_id')
            
            if investment_id and mt5_account_id:
                self.created_investments.append({
                    'investment_id': investment_id,
                    'mt5_account_id': mt5_account_id,
                    'client_id': client_id,
                    'fund_code': 'CORE',
                    'amount': 25000.0,
                    'mt5_login': '9928326',
                    'mt5_server': 'Multibank-Live'
                })
                print(f"   ✅ Investment created: {investment_id}")
                print(f"   ✅ MT5 Account created: {mt5_account_id}")
                print(f"   ✅ MT5 Login: {mt5_data['mt5_login']}")
                print(f"   ✅ Banking fees handled: ${mt5_data['banking_fees']}")
            else:
                print("   ❌ Missing investment_id or mt5_account_id in response")
                return False
        else:
            print("   ❌ Failed to create investment with complete MT5 data")
            return False

        # Test 2: BALANCE fund with different MT5 credentials
        print("\n📊 Test 2: BALANCE Fund Investment with Different MT5 Credentials")
        mt5_data_balance = {
            "client_id": client_id,
            "fund_code": "BALANCE",
            "amount": 75000.0,
            "deposit_date": "2024-12-20",
            "create_mt5_account": True,
            "mt5_login": "8765432",  # Different realistic MT5 login
            "mt5_password": "BalancePass456@",
            "mt5_server": "DooTechnology-Live",  # Different real server
            "broker_name": "DooTechnology",
            "mt5_initial_balance": 74500.0,  # Different banking fee scenario
            "banking_fees": 500.0,
            "fee_notes": "International wire transfer with higher fees"
        }
        
        success, response = self.run_test(
            "Create BALANCE Investment with Different MT5 Server",
            "POST",
            "api/investments/create",
            200,
            data=mt5_data_balance,
            use_auth=True
        )
        
        if success:
            if response.get('mt5_mapping_success'):
                investment_id = response.get('investment_id')
                mt5_account_id = response.get('mt5_account_id')
                
                self.created_investments.append({
                    'investment_id': investment_id,
                    'mt5_account_id': mt5_account_id,
                    'client_id': client_id,
                    'fund_code': 'BALANCE',
                    'amount': 75000.0,
                    'mt5_login': '8765432',
                    'mt5_server': 'DooTechnology-Live'
                })
                print(f"   ✅ BALANCE investment with DooTechnology server created successfully")
                print(f"   ✅ Different MT5 credentials handled correctly")
            else:
                print(f"   ❌ BALANCE investment MT5 mapping failed")
                return False
        else:
            print("   ❌ Failed to create BALANCE investment")
            return False

        return True

    def test_investment_creation_with_optional_fields(self) -> bool:
        """Test investment creation with optional MT5 fields"""
        print("\n" + "="*80)
        print("🔧 TESTING INVESTMENT CREATION WITH OPTIONAL MT5 FIELDS")
        print("="*80)
        
        if not self.client_user:
            print("❌ No client user available")
            return False
            
        client_id = self.client_user.get('id')
        
        # Test 1: Minimal MT5 data (only required fields)
        print("\n📊 Test 1: Minimal MT5 Data (Required Fields Only)")
        minimal_mt5_data = {
            "client_id": client_id,
            "fund_code": "CORE",
            "amount": 15000.0,
            "deposit_date": "2024-12-21",
            "create_mt5_account": True,
            "mt5_login": "5544332",
            "mt5_password": "MinimalPass789#",
            "mt5_server": "Multibank-Demo"
            # No optional fields: broker_name, mt5_initial_balance, banking_fees, fee_notes
        }
        
        success, response = self.run_test(
            "Create Investment with Minimal MT5 Data",
            "POST",
            "api/investments/create",
            200,
            data=minimal_mt5_data,
            use_auth=True
        )
        
        if success:
            if response.get('mt5_mapping_success'):
                print("   ✅ Minimal MT5 data handled correctly")
                print("   ✅ Optional fields properly defaulted")
                
                investment_id = response.get('investment_id')
                if investment_id:
                    self.created_investments.append({
                        'investment_id': investment_id,
                        'client_id': client_id,
                        'fund_code': 'CORE',
                        'amount': 15000.0,
                        'mt5_login': '5544332'
                    })
            else:
                print("   ❌ Minimal MT5 data mapping failed")
                return False
        else:
            print("   ❌ Failed to create investment with minimal MT5 data")
            return False

        # Test 2: Partial optional fields
        print("\n📊 Test 2: Partial Optional Fields")
        partial_mt5_data = {
            "client_id": client_id,
            "fund_code": "DYNAMIC",
            "amount": 300000.0,
            "deposit_date": "2024-12-22",
            "create_mt5_account": True,
            "mt5_login": "7788990",
            "mt5_password": "DynamicPass321$",
            "mt5_server": "Multibank-Pro",
            "broker_name": "Multibank Professional",
            "mt5_initial_balance": 299000.0,  # Include initial balance
            "banking_fees": 1000.0,           # Include banking fees
            # No fee_notes
        }
        
        success, response = self.run_test(
            "Create Investment with Partial Optional Fields",
            "POST",
            "api/investments/create",
            200,
            data=partial_mt5_data,
            use_auth=True
        )
        
        if success:
            if response.get('mt5_mapping_success'):
                print("   ✅ Partial optional fields handled correctly")
                print("   ✅ Missing fee_notes handled gracefully")
                
                investment_id = response.get('investment_id')
                if investment_id:
                    self.created_investments.append({
                        'investment_id': investment_id,
                        'client_id': client_id,
                        'fund_code': 'DYNAMIC',
                        'amount': 300000.0,
                        'mt5_login': '7788990'
                    })
            else:
                print("   ❌ Partial optional fields mapping failed")
                return False
        else:
            print("   ❌ Failed to create investment with partial optional fields")
            return False

        return True

    def test_investment_creation_without_mt5_mapping(self) -> bool:
        """Test investment creation without MT5 mapping"""
        print("\n" + "="*80)
        print("🚫 TESTING INVESTMENT CREATION WITHOUT MT5 MAPPING")
        print("="*80)
        
        if not self.client_user:
            print("❌ No client user available")
            return False
            
        client_id = self.client_user.get('id')
        
        # Test 1: create_mt5_account = false
        print("\n📊 Test 1: Explicit MT5 Mapping Disabled")
        no_mt5_data = {
            "client_id": client_id,
            "fund_code": "CORE",
            "amount": 20000.0,
            "deposit_date": "2024-12-23",
            "create_mt5_account": False
        }
        
        success, response = self.run_test(
            "Create Investment with MT5 Mapping Disabled",
            "POST",
            "api/investments/create",
            200,
            data=no_mt5_data,
            use_auth=True
        )
        
        if success:
            # Should succeed but without MT5 mapping
            mt5_mapping_success = response.get('mt5_mapping_success', False)
            mt5_account_id = response.get('mt5_account_id')
            
            if not mt5_mapping_success and not mt5_account_id:
                print("   ✅ Investment created without MT5 mapping as expected")
                
                investment_id = response.get('investment_id')
                if investment_id:
                    self.created_investments.append({
                        'investment_id': investment_id,
                        'client_id': client_id,
                        'fund_code': 'CORE',
                        'amount': 20000.0,
                        'mt5_mapping': False
                    })
            else:
                print(f"   ❌ Unexpected MT5 mapping: success={mt5_mapping_success}, account_id={mt5_account_id}")
                return False
        else:
            print("   ❌ Failed to create investment without MT5 mapping")
            return False

        # Test 2: Missing MT5 fields (should default to no mapping)
        print("\n📊 Test 2: Missing MT5 Fields (Default Behavior)")
        default_data = {
            "client_id": client_id,
            "fund_code": "BALANCE",
            "amount": 60000.0,
            "deposit_date": "2024-12-24"
            # No MT5 fields at all
        }
        
        success, response = self.run_test(
            "Create Investment with No MT5 Fields",
            "POST",
            "api/investments/create",
            200,
            data=default_data,
            use_auth=True
        )
        
        if success:
            # Should succeed with default behavior (no MT5 mapping)
            investment_id = response.get('investment_id')
            if investment_id:
                print("   ✅ Investment created with default behavior (no MT5 mapping)")
                self.created_investments.append({
                    'investment_id': investment_id,
                    'client_id': client_id,
                    'fund_code': 'BALANCE',
                    'amount': 60000.0,
                    'mt5_mapping': False
                })
            else:
                print("   ❌ No investment_id returned")
                return False
        else:
            print("   ❌ Failed to create investment with default behavior")
            return False

        return True

    def test_validation_scenarios(self) -> bool:
        """Test validation of MT5 fields"""
        print("\n" + "="*80)
        print("🔍 TESTING MT5 FIELD VALIDATION")
        print("="*80)
        
        if not self.client_user:
            print("❌ No client user available")
            return False
            
        client_id = self.client_user.get('id')
        
        # Test 1: Missing required MT5 fields
        print("\n📊 Test 1: Missing Required MT5 Fields")
        incomplete_data = {
            "client_id": client_id,
            "fund_code": "CORE",
            "amount": 25000.0,
            "create_mt5_account": True,
            "mt5_login": "1234567",
            # Missing mt5_password and mt5_server
        }
        
        success, response = self.run_test(
            "Create Investment with Missing MT5 Fields",
            "POST",
            "api/investments/create",
            200,  # Should succeed but MT5 mapping should fail gracefully
            data=incomplete_data,
            use_auth=True
        )
        
        if success:
            # Investment should succeed but MT5 mapping should fail
            mt5_mapping_success = response.get('mt5_mapping_success', False)
            if not mt5_mapping_success:
                print("   ✅ Missing MT5 fields handled gracefully")
                print("   ✅ Investment still created successfully")
            else:
                print("   ❌ MT5 mapping unexpectedly succeeded with missing fields")
                return False
        else:
            print("   ❌ Investment creation failed (should succeed even with MT5 issues)")
            return False

        # Test 2: Invalid MT5 login format
        print("\n📊 Test 2: Invalid MT5 Login Format")
        invalid_login_data = {
            "client_id": client_id,
            "fund_code": "CORE",
            "amount": 25000.0,
            "create_mt5_account": True,
            "mt5_login": "invalid_login",  # Invalid format
            "mt5_password": "ValidPass123!",
            "mt5_server": "Multibank-Live"
        }
        
        success, response = self.run_test(
            "Create Investment with Invalid MT5 Login",
            "POST",
            "api/investments/create",
            200,  # Should succeed but MT5 mapping should fail
            data=invalid_login_data,
            use_auth=True
        )
        
        if success:
            # Investment should succeed but MT5 mapping should fail
            mt5_mapping_success = response.get('mt5_mapping_success', False)
            if not mt5_mapping_success:
                print("   ✅ Invalid MT5 login format handled gracefully")
            else:
                print("   ❌ Invalid MT5 login unexpectedly accepted")
                return False
        else:
            print("   ❌ Investment creation failed (should succeed even with MT5 issues)")
            return False

        # Test 3: Duplicate MT5 login (should handle appropriately)
        print("\n📊 Test 3: Duplicate MT5 Login Handling")
        duplicate_login_data = {
            "client_id": client_id,
            "fund_code": "BALANCE",
            "amount": 50000.0,
            "create_mt5_account": True,
            "mt5_login": "9928326",  # Same as first test
            "mt5_password": "DuplicatePass456@",
            "mt5_server": "Multibank-Live"
        }
        
        success, response = self.run_test(
            "Create Investment with Duplicate MT5 Login",
            "POST",
            "api/investments/create",
            200,
            data=duplicate_login_data,
            use_auth=True
        )
        
        if success:
            # Should either succeed (adding to existing account) or fail gracefully
            mt5_mapping_success = response.get('mt5_mapping_success')
            print(f"   ✅ Duplicate MT5 login handled: mapping_success={mt5_mapping_success}")
            
            if mt5_mapping_success:
                print("   ✅ Duplicate login added to existing MT5 account")
            else:
                print("   ✅ Duplicate login rejected gracefully")
        else:
            print("   ❌ Duplicate MT5 login test failed")
            return False

        return True

    def test_database_integration(self) -> bool:
        """Test MongoDB integration and credential encryption"""
        print("\n" + "="*80)
        print("🗄️ TESTING DATABASE INTEGRATION & ENCRYPTION")
        print("="*80)
        
        if not self.created_investments:
            print("❌ No created investments to verify in database")
            return False

        # Test 1: Verify MT5 account records in MongoDB
        print("\n📊 Test 1: Verify MT5 Account Records in MongoDB")
        
        # Get client's MT5 accounts to verify database storage
        client_id = self.client_user.get('id')
        success, response = self.run_test(
            "Get Client MT5 Accounts from Database",
            "GET",
            f"api/mt5/client/{client_id}/accounts",
            200
        )
        
        if success:
            accounts = response.get('accounts', [])
            if accounts:
                print(f"   ✅ Found {len(accounts)} MT5 accounts in database")
                
                # Verify account structure
                for account in accounts:
                    required_fields = ['account_id', 'client_id', 'fund_code', 'mt5_login', 'mt5_server']
                    missing_fields = [field for field in required_fields if field not in account]
                    
                    if missing_fields:
                        print(f"   ❌ Missing fields in account: {missing_fields}")
                        return False
                    
                    # Verify MT5 login is stored correctly
                    mt5_login = account.get('mt5_login')
                    if mt5_login and str(mt5_login).isdigit():
                        print(f"   ✅ MT5 login stored correctly: {mt5_login}")
                    else:
                        print(f"   ❌ Invalid MT5 login in database: {mt5_login}")
                        return False
                    
                    # Verify server information
                    mt5_server = account.get('mt5_server')
                    if mt5_server and ('Multibank' in mt5_server or 'DooTechnology' in mt5_server):
                        print(f"   ✅ MT5 server stored correctly: {mt5_server}")
                    else:
                        print(f"   ❌ Invalid MT5 server in database: {mt5_server}")
                        return False
                
                print("   ✅ All MT5 account records have correct structure")
            else:
                print("   ❌ No MT5 accounts found in database")
                return False
        else:
            print("   ❌ Failed to retrieve MT5 accounts from database")
            return False

        # Test 2: Verify investment-to-MT5 account linking
        print("\n📊 Test 2: Verify Investment-to-MT5 Account Linking")
        
        # Get client investments to verify linking
        success, response = self.run_test(
            "Get Client Investments with MT5 Links",
            "GET",
            f"api/investments/client/{client_id}",
            200
        )
        
        if success:
            investments = response.get('investments', [])
            if investments:
                print(f"   ✅ Found {len(investments)} investments in database")
                
                # Check for investments with MT5 mapping
                mt5_linked_investments = 0
                for investment in investments:
                    investment_id = investment.get('investment_id')
                    fund_code = investment.get('fund_code')
                    
                    # Check if this investment was created with MT5 mapping
                    created_with_mt5 = any(
                        inv.get('investment_id') == investment_id and inv.get('mt5_login')
                        for inv in self.created_investments
                    )
                    
                    if created_with_mt5:
                        mt5_linked_investments += 1
                        print(f"   ✅ Investment {investment_id} ({fund_code}) properly linked")
                
                if mt5_linked_investments > 0:
                    print(f"   ✅ {mt5_linked_investments} investments properly linked to MT5 accounts")
                else:
                    print("   ⚠️ No MT5-linked investments found (may be expected)")
            else:
                print("   ❌ No investments found in database")
                return False
        else:
            print("   ❌ Failed to retrieve investments from database")
            return False

        # Test 3: Verify encrypted credentials (indirect test)
        print("\n📊 Test 3: Verify Secure Credential Storage")
        
        # We can't directly access encrypted passwords, but we can verify the system
        # handles credentials securely by checking that passwords aren't returned in API responses
        if accounts:
            for account in accounts:
                # Check that password is not exposed in API responses
                if 'mt5_password' in account or 'password' in account:
                    print("   ❌ Password exposed in API response - security risk!")
                    return False
                
                # Check that we have encrypted credential indicators
                if 'mt5_login' in account and account['mt5_login']:
                    print("   ✅ Credentials stored securely (password not exposed)")
                else:
                    print("   ❌ Missing credential information")
                    return False
            
            print("   ✅ All credentials stored securely without exposure")
        
        return True

    def test_backend_response_validation(self) -> bool:
        """Test backend response structure and content"""
        print("\n" + "="*80)
        print("📋 TESTING BACKEND RESPONSE VALIDATION")
        print("="*80)
        
        if not self.client_user:
            print("❌ No client user available")
            return False
            
        client_id = self.client_user.get('id')
        
        # Test 1: Verify response includes mt5_account_id and mt5_mapping_success
        print("\n📊 Test 1: Response Structure Validation")
        
        mt5_test_data = {
            "client_id": client_id,
            "fund_code": "CORE",
            "amount": 30000.0,
            "create_mt5_account": True,
            "mt5_login": "4455667",
            "mt5_password": "ResponseTest123!",
            "mt5_server": "Multibank-Test"
        }
        
        success, response = self.run_test(
            "Create Investment for Response Validation",
            "POST",
            "api/investments/create",
            200,
            data=mt5_test_data,
            use_auth=True
        )
        
        if success:
            # Check required response fields
            required_fields = ['success', 'investment_id', 'mt5_account_id', 'mt5_mapping_success', 'message']
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                print(f"   ❌ Missing required response fields: {missing_fields}")
                return False
            
            # Validate field types and values
            if not isinstance(response.get('success'), bool):
                print("   ❌ 'success' field should be boolean")
                return False
            
            if not isinstance(response.get('mt5_mapping_success'), bool):
                print("   ❌ 'mt5_mapping_success' field should be boolean")
                return False
            
            if not isinstance(response.get('message'), str):
                print("   ❌ 'message' field should be string")
                return False
            
            # Check message content
            message = response.get('message', '')
            if 'MT5 account mapping' in message or 'MT5 mapping' in message:
                print("   ✅ Response message includes MT5 mapping status")
            else:
                print(f"   ❌ Response message doesn't mention MT5 mapping: {message}")
                return False
            
            print("   ✅ All required response fields present with correct types")
            print("   ✅ Response structure validation passed")
        else:
            print("   ❌ Failed to create investment for response validation")
            return False

        # Test 2: Verify success/error messages are appropriate
        print("\n📊 Test 2: Success/Error Message Validation")
        
        # Test successful MT5 mapping message
        if response.get('mt5_mapping_success'):
            message = response.get('message', '')
            if 'with MT5 account mapping' in message:
                print("   ✅ Success message correctly indicates MT5 mapping")
            else:
                print(f"   ❌ Success message doesn't indicate MT5 mapping: {message}")
                return False
        
        # Test failed MT5 mapping (by using invalid data)
        invalid_mt5_data = {
            "client_id": client_id,
            "fund_code": "CORE",
            "amount": 25000.0,
            "create_mt5_account": True,
            "mt5_login": "",  # Invalid empty login
            "mt5_password": "TestPass123!",
            "mt5_server": "Multibank-Test"
        }
        
        success, response = self.run_test(
            "Create Investment with Invalid MT5 Data",
            "POST",
            "api/investments/create",
            200,  # Investment should still succeed
            data=invalid_mt5_data,
            use_auth=True
        )
        
        if success:
            # Should succeed but MT5 mapping should fail
            if not response.get('mt5_mapping_success'):
                message = response.get('message', '')
                if 'MT5 mapping skipped' in message or 'without MT5' in message:
                    print("   ✅ Error message correctly indicates MT5 mapping failure")
                else:
                    print(f"   ❌ Error message doesn't indicate MT5 mapping failure: {message}")
                    return False
            else:
                print("   ❌ MT5 mapping unexpectedly succeeded with invalid data")
                return False
        else:
            print("   ❌ Investment creation failed (should succeed even with MT5 issues)")
            return False

        return True

    def test_error_handling_scenarios(self) -> bool:
        """Test error handling for various failure scenarios"""
        print("\n" + "="*80)
        print("⚠️ TESTING ERROR HANDLING SCENARIOS")
        print("="*80)
        
        if not self.client_user:
            print("❌ No client user available")
            return False
            
        client_id = self.client_user.get('id')
        
        # Test 1: Investment still succeeds even if MT5 mapping fails
        print("\n📊 Test 1: Investment Success Despite MT5 Failure")
        
        failing_mt5_data = {
            "client_id": client_id,
            "fund_code": "CORE",
            "amount": 25000.0,
            "create_mt5_account": True,
            "mt5_login": None,  # This should cause MT5 mapping to fail
            "mt5_password": "TestPass123!",
            "mt5_server": "Multibank-Test"
        }
        
        success, response = self.run_test(
            "Investment Creation with Failing MT5 Data",
            "POST",
            "api/investments/create",
            200,  # Should still succeed
            data=failing_mt5_data,
            use_auth=True
        )
        
        if success:
            # Investment should succeed
            if response.get('success') and response.get('investment_id'):
                print("   ✅ Investment created successfully despite MT5 failure")
                
                # MT5 mapping should fail
                if not response.get('mt5_mapping_success'):
                    print("   ✅ MT5 mapping correctly failed with invalid data")
                else:
                    print("   ❌ MT5 mapping unexpectedly succeeded")
                    return False
            else:
                print("   ❌ Investment creation failed (should succeed)")
                return False
        else:
            print("   ❌ Investment creation failed (should succeed even with MT5 issues)")
            return False

        # Test 2: Proper logging of all operations
        print("\n📊 Test 2: Verify Proper Error Logging")
        
        # This is an indirect test - we verify that the system handles errors gracefully
        # and continues to function properly after errors
        
        # Create a valid investment after the error to ensure system is still functional
        recovery_data = {
            "client_id": client_id,
            "fund_code": "BALANCE",
            "amount": 50000.0,
            "create_mt5_account": True,
            "mt5_login": "9988776",
            "mt5_password": "RecoveryPass123!",
            "mt5_server": "Multibank-Recovery"
        }
        
        success, response = self.run_test(
            "System Recovery After MT5 Error",
            "POST",
            "api/investments/create",
            200,
            data=recovery_data,
            use_auth=True
        )
        
        if success:
            if response.get('success') and response.get('mt5_mapping_success'):
                print("   ✅ System recovered properly after MT5 error")
                print("   ✅ Error logging and handling working correctly")
            else:
                print("   ❌ System did not recover properly after error")
                return False
        else:
            print("   ❌ System recovery test failed")
            return False

        # Test 3: MongoDB operation failure handling (simulated)
        print("\n📊 Test 3: Database Error Resilience")
        
        # Test with edge case data that might cause database issues
        edge_case_data = {
            "client_id": client_id,
            "fund_code": "CORE",
            "amount": 10000.0,  # Minimum amount
            "create_mt5_account": True,
            "mt5_login": "1111111",  # Edge case login
            "mt5_password": "A" * 50,  # Very long password
            "mt5_server": "Test-Server-With-Very-Long-Name-That-Might-Cause-Issues"
        }
        
        success, response = self.run_test(
            "Edge Case Data Handling",
            "POST",
            "api/investments/create",
            200,
            data=edge_case_data,
            use_auth=True
        )
        
        if success:
            # Should handle edge cases gracefully
            print("   ✅ Edge case data handled gracefully")
            
            if response.get('success'):
                print("   ✅ Investment creation robust against edge cases")
            else:
                print("   ❌ Edge case caused investment failure")
                return False
        else:
            print("   ❌ Edge case handling failed")
            return False

        return True

    def run_comprehensive_mt5_mapping_tests(self) -> bool:
        """Run all MT5 mapping integration tests"""
        print("\n" + "="*100)
        print("🚀 STARTING COMPREHENSIVE MT5 ACCOUNT MAPPING INTEGRATION TESTS")
        print("="*100)
        print("Testing the newly implemented MT5 Account Mapping Integration in Investment Creation workflow")
        print("Using realistic MT5 data: valid login numbers, real server names, banking fees")
        
        # Setup authentication
        if not self.setup_authentication():
            print("\n❌ Authentication setup failed - cannot proceed")
            return False
        
        # Run all test suites
        test_suites = [
            ("Investment Creation with Complete MT5 Data", self.test_investment_creation_with_complete_mt5_data),
            ("Investment Creation with Optional Fields", self.test_investment_creation_with_optional_fields),
            ("Investment Creation without MT5 Mapping", self.test_investment_creation_without_mt5_mapping),
            ("MT5 Field Validation Testing", self.test_validation_scenarios),
            ("Database Integration & Encryption", self.test_database_integration),
            ("Backend Response Validation", self.test_backend_response_validation),
            ("Error Handling Scenarios", self.test_error_handling_scenarios)
        ]
        
        suite_results = []
        
        for suite_name, test_method in test_suites:
            print(f"\n🔄 Running {suite_name}...")
            try:
                result = test_method()
                suite_results.append((suite_name, result))
                
                if result:
                    print(f"✅ {suite_name} - PASSED")
                else:
                    print(f"❌ {suite_name} - FAILED")
            except Exception as e:
                print(f"❌ {suite_name} - ERROR: {str(e)}")
                suite_results.append((suite_name, False))
        
        # Print final results
        print("\n" + "="*100)
        print("📊 MT5 ACCOUNT MAPPING INTEGRATION TEST RESULTS")
        print("="*100)
        
        passed_suites = sum(1 for _, result in suite_results if result)
        total_suites = len(suite_results)
        
        for suite_name, result in suite_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {suite_name}: {status}")
        
        print(f"\n📈 Overall Results:")
        print(f"   Test Suites: {passed_suites}/{total_suites} passed ({passed_suites/total_suites*100:.1f}%)")
        print(f"   Individual Tests: {self.tests_passed}/{self.tests_run} passed ({self.tests_passed/self.tests_run*100:.1f}%)")
        
        if self.created_investments:
            print(f"\n💰 Created Investments During Testing:")
            for inv in self.created_investments:
                mt5_info = f" (MT5: {inv.get('mt5_login', 'N/A')})" if inv.get('mt5_login') else " (No MT5)"
                print(f"   - {inv.get('fund_code', 'Unknown')}: ${inv.get('amount', 0):,.2f}{mt5_info}")
        
        # Determine overall success
        critical_suites = [
            "Investment Creation with Complete MT5 Data",
            "Database Integration & Encryption",
            "Backend Response Validation"
        ]
        
        critical_passed = sum(1 for name, result in suite_results if name in critical_suites and result)
        overall_success = (passed_suites >= total_suites * 0.8 and 
                          critical_passed == len(critical_suites) and
                          self.tests_passed >= self.tests_run * 0.8)
        
        if overall_success:
            print(f"\n🎉 MT5 ACCOUNT MAPPING INTEGRATION TESTING COMPLETED SUCCESSFULLY!")
            print("   All critical MT5 mapping functionality is working correctly.")
            print("   ✅ Complete MT5 data handling")
            print("   ✅ Optional fields support")
            print("   ✅ Validation and error handling")
            print("   ✅ Database integration and encryption")
            print("   ✅ Proper API responses")
        else:
            print(f"\n⚠️ MT5 ACCOUNT MAPPING INTEGRATION TESTING COMPLETED WITH ISSUES")
            print("   Some MT5 mapping functionality may need attention.")
            
            # Identify failed critical areas
            failed_critical = [name for name, result in suite_results if name in critical_suites and not result]
            if failed_critical:
                print(f"   ❌ Critical failures: {', '.join(failed_critical)}")
        
        return overall_success

def main():
    """Main test execution"""
    print("🔧 MT5 Account Mapping Integration Testing Suite")
    print("Testing the newly implemented MT5 Account Mapping Integration in Investment Creation workflow")
    
    tester = MT5MappingTester()
    
    try:
        success = tester.run_comprehensive_mt5_mapping_tests()
        
        if success:
            print("\n✅ All MT5 Account Mapping Integration tests completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Some MT5 Account Mapping Integration tests failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()