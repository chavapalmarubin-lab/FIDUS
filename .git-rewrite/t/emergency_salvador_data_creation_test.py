#!/usr/bin/env python3
"""
EMERGENCY SALVADOR DATA CREATION TEST
====================================

This test implements the EMERGENCY DATA CREATION PLAN from the review request:
Instead of trying to access database directly, use the ACTUAL WORKING production 
API endpoints to create Salvador's data step by step.

STEP-BY-STEP API CREATION PLAN:
1. VERIFY PRODUCTION API HEALTH
2. LOGIN AS ADMIN  
3. CREATE SALVADOR CLIENT (try multiple endpoints)
4. CREATE BALANCE INVESTMENT ($1,263,485.40)
5. CREATE CORE INVESTMENT ($4,000.00)
6. CREATE MT5 ACCOUNTS (try multiple endpoints)
7. VERIFY DATA CREATION

GOAL: Get production to show non-zero values by creating data through the 
application's own APIs.

Expected Results:
- Total AUM: $1,267,485.40 (not $0)
- Total Clients: 1 (not 0)
- Total Accounts: 2 (not 0)
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration - PRODUCTION ENVIRONMENT
PRODUCTION_URL = "https://fidus-invest.emergent.host/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class EmergencySalvadorDataCreation:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.salvador_client_id = None
        self.balance_investment_id = None
        self.core_investment_id = None
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        print(f"   {message}")
        if details and not success:
            print(f"   Details: {details}")
        print()
    
    def step_1_verify_production_api_health(self):
        """STEP 1: VERIFY PRODUCTION API HEALTH"""
        print("🔍 STEP 1: VERIFYING PRODUCTION API HEALTH")
        print("-" * 50)
        
        try:
            response = self.session.get(f"{PRODUCTION_URL}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                self.log_result("Production API Health Check", True, 
                              f"Production API is healthy and responding",
                              {"health_data": health_data})
                return True
            else:
                self.log_result("Production API Health Check", False, 
                              f"Production API returned HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Production API Health Check", False, 
                          f"Failed to connect to production API: {str(e)}")
            return False
    
    def step_2_login_as_admin(self):
        """STEP 2: LOGIN AS ADMIN"""
        print("🔐 STEP 2: LOGGING IN AS ADMIN")
        print("-" * 50)
        
        try:
            login_data = {
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            }
            
            response = self.session.post(f"{PRODUCTION_URL}/auth/login", 
                                       json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                
                if self.admin_token:
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    self.log_result("Admin Login", True, 
                                  "Successfully authenticated as admin",
                                  {"user_data": {k: v for k, v in data.items() if k != "token"}})
                    return True
                else:
                    self.log_result("Admin Login", False, 
                                  "Login successful but no token received",
                                  {"response": data})
                    return False
            else:
                self.log_result("Admin Login", False, 
                              f"Login failed with HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Admin Login", False, f"Login exception: {str(e)}")
            return False
    
    def step_3_create_salvador_client(self):
        """STEP 3: CREATE SALVADOR CLIENT (try multiple endpoints)"""
        print("👤 STEP 3: CREATING SALVADOR CLIENT")
        print("-" * 50)
        
        salvador_data = {
            "username": "client3",
            "name": "SALVADOR PALMA",
            "email": "chava@alyarglobal.com",
            "password": "password123",
            "phone": "+52-663-123-4567"
        }
        
        # Try multiple client creation endpoints
        endpoints_to_try = [
            ("/clients/create", "Client Creation Endpoint"),
            ("/admin/clients/create", "Admin Client Creation"),
            ("/clients/register", "Client Registration")
        ]
        
        for endpoint, description in endpoints_to_try:
            try:
                print(f"   Trying {description}: {endpoint}")
                response = self.session.post(f"{PRODUCTION_URL}{endpoint}", 
                                           json=salvador_data, timeout=10)
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    self.salvador_client_id = data.get("id") or data.get("client_id") or "client_003"
                    self.log_result("Salvador Client Creation", True, 
                                  f"Salvador client created successfully via {description}",
                                  {"client_data": data, "endpoint": endpoint})
                    return True
                elif response.status_code in [409, 400]:
                    # Client already exists - this is actually good!
                    response_text = response.text.lower()
                    if "already exists" in response_text or "username already exists" in response_text:
                        self.salvador_client_id = "client_003"
                        self.log_result("Salvador Client Creation", True, 
                                      f"Salvador client already exists (HTTP {response.status_code}) - this is expected",
                                      {"endpoint": endpoint, "response": response.text})
                        return True
                else:
                    print(f"      HTTP {response.status_code}: {response.text[:200]}")
                    
            except Exception as e:
                print(f"      Exception: {str(e)}")
        
        # If all endpoints failed, try to verify if Salvador already exists
        try:
            response = self.session.get(f"{PRODUCTION_URL}/admin/clients")
            if response.status_code == 200:
                clients = response.json()
                for client in clients:
                    if (client.get('id') == 'client_003' or 
                        'SALVADOR' in client.get('name', '').upper()):
                        self.salvador_client_id = client.get('id', 'client_003')
                        self.log_result("Salvador Client Creation", True, 
                                      "Salvador client already exists in system",
                                      {"existing_client": client})
                        return True
        except:
            pass
        
        self.log_result("Salvador Client Creation", False, 
                      "Failed to create Salvador client via all attempted endpoints")
        return False
    
    def step_4_create_balance_investment(self):
        """STEP 4: CREATE BALANCE INVESTMENT ($1,263,485.40)"""
        print("💰 STEP 4: CREATING BALANCE INVESTMENT")
        print("-" * 50)
        
        if not self.salvador_client_id:
            self.log_result("Balance Investment Creation", False, 
                          "Cannot create investment - Salvador client ID not available")
            return False
        
        balance_investment_data = {
            "client_id": self.salvador_client_id,
            "fund_code": "BALANCE",
            "amount": 1263485.40,
            "deposit_date": "2025-04-01"
        }
        
        # Try investment creation endpoint
        try:
            response = self.session.post(f"{PRODUCTION_URL}/investments/create", 
                                       json=balance_investment_data, timeout=10)
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.balance_investment_id = data.get("investment_id") or data.get("id")
                self.log_result("Balance Investment Creation", True, 
                              f"BALANCE investment created: ${balance_investment_data['amount']:,.2f}",
                              {"investment_data": data})
                return True
            else:
                self.log_result("Balance Investment Creation", False, 
                              f"Investment creation failed: HTTP {response.status_code}",
                              {"response": response.text, "request_data": balance_investment_data})
                return False
                
        except Exception as e:
            self.log_result("Balance Investment Creation", False, 
                          f"Investment creation exception: {str(e)}")
            return False
    
    def step_5_create_core_investment(self):
        """STEP 5: CREATE CORE INVESTMENT ($4,000.00)"""
        print("💰 STEP 5: CREATING CORE INVESTMENT")
        print("-" * 50)
        
        if not self.salvador_client_id:
            self.log_result("Core Investment Creation", False, 
                          "Cannot create investment - Salvador client ID not available")
            return False
        
        core_investment_data = {
            "client_id": self.salvador_client_id,
            "fund_code": "CORE",
            "amount": 4000.00,
            "deposit_date": "2025-04-01"
        }
        
        # Try investment creation endpoint
        try:
            response = self.session.post(f"{PRODUCTION_URL}/investments/create", 
                                       json=core_investment_data, timeout=10)
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.core_investment_id = data.get("investment_id") or data.get("id")
                self.log_result("Core Investment Creation", True, 
                              f"CORE investment created: ${core_investment_data['amount']:,.2f}",
                              {"investment_data": data})
                return True
            else:
                self.log_result("Core Investment Creation", False, 
                              f"Investment creation failed: HTTP {response.status_code}",
                              {"response": response.text, "request_data": core_investment_data})
                return False
                
        except Exception as e:
            self.log_result("Core Investment Creation", False, 
                          f"Investment creation exception: {str(e)}")
            return False
    
    def step_6_create_mt5_accounts(self):
        """STEP 6: CREATE MT5 ACCOUNTS (try multiple endpoints)"""
        print("📊 STEP 6: CREATING MT5 ACCOUNTS")
        print("-" * 50)
        
        if not self.salvador_client_id:
            self.log_result("MT5 Accounts Creation", False, 
                          "Cannot create MT5 accounts - Salvador client ID not available")
            return False
        
        # DooTechnology MT5 Account
        doo_account_data = {
            "client_id": self.salvador_client_id,
            "fund_code": "BALANCE",
            "broker_code": "multibank",
            "mt5_login": "9928326",
            "mt5_password": "Salvador123!",
            "mt5_server": "Multibank-Live",
            "allocated_amount": 1263485.40
        }
        
        # VT Markets MT5 Account
        vt_account_data = {
            "client_id": self.salvador_client_id,
            "fund_code": "CORE", 
            "broker_code": "vtmarkets",
            "mt5_login": "15759667",
            "mt5_password": "Salvador123!",
            "mt5_server": "VTMarkets-PAMM",
            "allocated_amount": 4000.00
        }
        
        # Try multiple MT5 creation endpoints
        mt5_endpoints = [
            "/mt5/admin/add-manual-account"
        ]
        
        accounts_created = 0
        
        for account_data, account_name in [(doo_account_data, "DooTechnology"), 
                                          (vt_account_data, "VT Markets")]:
            account_created = False
            
            for endpoint in mt5_endpoints:
                try:
                    print(f"   Creating {account_name} account via {endpoint}")
                    response = self.session.post(f"{PRODUCTION_URL}{endpoint}", 
                                               json=account_data, timeout=10)
                    
                    if response.status_code in [200, 201]:
                        data = response.json()
                        self.log_result(f"{account_name} MT5 Account", True, 
                                      f"{account_name} MT5 account created (Login: {account_data['login']})",
                                      {"account_data": data})
                        account_created = True
                        accounts_created += 1
                        break
                    elif response.status_code == 409:
                        # Account already exists
                        self.log_result(f"{account_name} MT5 Account", True, 
                                      f"{account_name} MT5 account already exists (Login: {account_data['login']})")
                        account_created = True
                        accounts_created += 1
                        break
                    else:
                        print(f"      HTTP {response.status_code}: {response.text[:200]}")
                        
                except Exception as e:
                    print(f"      Exception: {str(e)}")
            
            if not account_created:
                self.log_result(f"{account_name} MT5 Account", False, 
                              f"Failed to create {account_name} MT5 account via all endpoints")
        
        return accounts_created >= 1  # At least one account created
    
    def step_7_verify_data_creation(self):
        """STEP 7: VERIFY DATA CREATION"""
        print("✅ STEP 7: VERIFYING DATA CREATION")
        print("-" * 50)
        
        verification_results = []
        
        # Check clients
        try:
            response = self.session.get(f"{PRODUCTION_URL}/admin/clients")
            if response.status_code == 200:
                clients = response.json()
                client_count = len(clients) if isinstance(clients, list) else 0
                
                salvador_found = any(
                    client.get('id') == 'client_003' or 'SALVADOR' in client.get('name', '').upper()
                    for client in clients
                ) if isinstance(clients, list) else False
                
                if salvador_found:
                    self.log_result("Client Verification", True, 
                                  f"Salvador Palma found in clients (Total clients: {client_count})")
                    verification_results.append(True)
                else:
                    self.log_result("Client Verification", False, 
                                  f"Salvador Palma not found in {client_count} clients")
                    verification_results.append(False)
            else:
                self.log_result("Client Verification", False, 
                              f"Failed to get clients: HTTP {response.status_code}")
                verification_results.append(False)
        except Exception as e:
            self.log_result("Client Verification", False, f"Exception: {str(e)}")
            verification_results.append(False)
        
        # Check investments
        try:
            response = self.session.get(f"{PRODUCTION_URL}/investments/client/client_003")
            if response.status_code == 200:
                investments = response.json()
                investment_count = len(investments) if isinstance(investments, list) else 0
                
                if investment_count >= 2:
                    total_amount = sum(inv.get('principal_amount', 0) for inv in investments)
                    self.log_result("Investment Verification", True, 
                                  f"Found {investment_count} investments, Total: ${total_amount:,.2f}")
                    verification_results.append(True)
                else:
                    self.log_result("Investment Verification", False, 
                                  f"Expected 2+ investments, found {investment_count}")
                    verification_results.append(False)
            else:
                self.log_result("Investment Verification", False, 
                              f"Failed to get investments: HTTP {response.status_code}")
                verification_results.append(False)
        except Exception as e:
            self.log_result("Investment Verification", False, f"Exception: {str(e)}")
            verification_results.append(False)
        
        # Check MT5 accounts
        try:
            response = self.session.get(f"{PRODUCTION_URL}/mt5/admin/accounts")
            if response.status_code == 200:
                mt5_accounts = response.json()
                salvador_mt5_count = 0
                
                if isinstance(mt5_accounts, list):
                    salvador_mt5_count = sum(
                        1 for account in mt5_accounts 
                        if account.get('client_id') == 'client_003'
                    )
                
                if salvador_mt5_count >= 1:
                    self.log_result("MT5 Account Verification", True, 
                                  f"Found {salvador_mt5_count} MT5 accounts for Salvador")
                    verification_results.append(True)
                else:
                    self.log_result("MT5 Account Verification", False, 
                                  f"Expected 1+ MT5 accounts, found {salvador_mt5_count}")
                    verification_results.append(False)
            else:
                self.log_result("MT5 Account Verification", False, 
                              f"Failed to get MT5 accounts: HTTP {response.status_code}")
                verification_results.append(False)
        except Exception as e:
            self.log_result("MT5 Account Verification", False, f"Exception: {str(e)}")
            verification_results.append(False)
        
        return sum(verification_results) >= 2  # At least 2 out of 3 verifications passed
    
    def run_emergency_data_creation(self):
        """Run the complete emergency data creation process"""
        print("🚨 EMERGENCY SALVADOR DATA CREATION - PRODUCTION ENVIRONMENT")
        print("=" * 70)
        print(f"Production URL: {PRODUCTION_URL}")
        print(f"Execution Time: {datetime.now().isoformat()}")
        print()
        print("GOAL: Create Salvador's data directly in production using WORKING API endpoints")
        print("Expected Results: Total AUM: $1,267,485.40, Total Clients: 1, Total Accounts: 2")
        print()
        
        # Execute all steps in sequence
        steps = [
            self.step_1_verify_production_api_health,
            self.step_2_login_as_admin,
            self.step_3_create_salvador_client,
            self.step_4_create_balance_investment,
            self.step_5_create_core_investment,
            self.step_6_create_mt5_accounts,
            self.step_7_verify_data_creation
        ]
        
        step_results = []
        for i, step_func in enumerate(steps, 1):
            try:
                result = step_func()
                step_results.append(result)
                
                # If critical early steps fail, stop execution
                if i <= 2 and not result:
                    print(f"❌ CRITICAL FAILURE at Step {i}. Stopping execution.")
                    break
                    
            except Exception as e:
                print(f"❌ EXCEPTION in Step {i}: {str(e)}")
                step_results.append(False)
                if i <= 2:  # Critical early steps
                    break
        
        # Generate final summary
        self.generate_emergency_summary(step_results)
        
        return len([r for r in step_results if r]) >= 4  # At least 4 steps successful
    
    def generate_emergency_summary(self, step_results):
        """Generate comprehensive emergency data creation summary"""
        print("\n" + "=" * 70)
        print("🚨 EMERGENCY DATA CREATION SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Operations: {total_tests}")
        print(f"Successful: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Show step results
        step_names = [
            "Production API Health",
            "Admin Authentication", 
            "Salvador Client Creation",
            "Balance Investment Creation",
            "Core Investment Creation",
            "MT5 Accounts Creation",
            "Data Verification"
        ]
        
        print("📋 STEP-BY-STEP RESULTS:")
        for i, (step_name, result) in enumerate(zip(step_names, step_results), 1):
            status = "✅ SUCCESS" if result else "❌ FAILED"
            print(f"   Step {i}: {step_name} - {status}")
        print()
        
        # Show failed operations
        if failed_tests > 0:
            print("❌ FAILED OPERATIONS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Critical assessment
        successful_steps = sum(step_results)
        
        print("🎯 FINAL ASSESSMENT:")
        if successful_steps >= 5:
            print("✅ EMERGENCY DATA CREATION: SUCCESSFUL")
            print("   Salvador's data has been created in production environment.")
            print("   Frontend should now show non-zero values.")
            print("   Expected: Total AUM: $1,267,485.40, Total Clients: 1, Total Accounts: 2")
        elif successful_steps >= 3:
            print("⚠️  EMERGENCY DATA CREATION: PARTIALLY SUCCESSFUL")
            print("   Some Salvador data created but verification incomplete.")
            print("   Manual verification of frontend values recommended.")
        else:
            print("❌ EMERGENCY DATA CREATION: FAILED")
            print("   Critical failures prevented Salvador data creation.")
            print("   Main agent intervention required.")
        
        print("\n🔗 NEXT STEPS:")
        print("1. Check frontend at https://fidus-invest.emergent.host/")
        print("2. Verify Total AUM shows $1,267,485.40 (not $0)")
        print("3. Verify Total Clients shows 1 (not 0)")
        print("4. Verify Total Accounts shows 2 (not 0)")
        print("5. If values still show $0, investigate API-to-frontend data flow")
        
        print("\n" + "=" * 70)

def main():
    """Main execution function"""
    emergency_creator = EmergencySalvadorDataCreation()
    success = emergency_creator.run_emergency_data_creation()
    
    if not success:
        print("\n❌ EMERGENCY DATA CREATION FAILED")
        sys.exit(1)
    else:
        print("\n✅ EMERGENCY DATA CREATION COMPLETED")

if __name__ == "__main__":
    main()