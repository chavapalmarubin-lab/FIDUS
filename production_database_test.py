#!/usr/bin/env python3
"""
CRITICAL PRODUCTION DATABASE INTEGRATION TEST
Test all major API endpoints that frontend components are calling to ensure NO database errors exist.

Priority 1 - Admin Endpoints:
1. GET /api/admin/portfolio-summary - Admin dashboard main data
2. GET /api/crm/admin/dashboard - CRM dashboard data  
3. GET /api/admin/cashflow/overview - Cash flow data
4. GET /api/clients/all - Client management data
5. GET /api/crm/prospects - Prospect management data

Priority 2 - Client Endpoints:
1. GET /api/investments/client/{client_id} - Client investment data
2. GET /api/redemptions/client/{client_id} - Client redemption data
3. GET /api/mt5/client/{client_id}/performance - Client MT5 data

Priority 3 - Document/Settings:
1. GET /api/documents/admin/all - Document portal
2. GET /api/gmail/settings - Gmail settings

GOAL: ZERO DATABASE ERRORS IN PRODUCTION SYSTEM
"""

import requests
import sys
from datetime import datetime
import json

class ProductionDatabaseTester:
    def __init__(self, base_url="https://fidus-admin.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None
        self.client_token = None
        self.admin_user = None
        self.client_user = None
        self.critical_errors = []
        self.database_errors = []
        
    def log_critical_error(self, endpoint, error_type, details):
        """Log critical database errors"""
        error = {
            "endpoint": endpoint,
            "error_type": error_type,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.critical_errors.append(error)
        print(f"🚨 CRITICAL ERROR: {endpoint} - {error_type}: {details}")

    def run_authenticated_test(self, name, endpoint, expected_status, token, method="GET", data=None):
        """Run API test with JWT authentication"""
        url = f"{self.base_url}/{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        print(f"   Auth: {'Admin' if token == self.admin_token else 'Client'} JWT Token")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=15)
            else:
                response = requests.request(method, url, json=data, headers=headers, timeout=15)

            print(f"   Status Code: {response.status_code}")
            
            # Check for database-related errors
            if response.status_code >= 500:
                self.log_critical_error(endpoint, "SERVER_ERROR", f"Status {response.status_code}")
                try:
                    error_data = response.json()
                    if any(db_keyword in str(error_data).lower() for db_keyword in ['database', 'mongodb', 'connection', 'timeout']):
                        self.log_critical_error(endpoint, "DATABASE_ERROR", str(error_data))
                except:
                    pass
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    
                    # Check for data structure integrity
                    if isinstance(response_data, dict):
                        print(f"   Response keys: {list(response_data.keys())}")
                        
                        # Check for empty or null critical data
                        if endpoint.endswith('portfolio-summary'):
                            aum = response_data.get('aum') or response_data.get('total_aum')
                            if aum == 0 or aum is None:
                                self.log_critical_error(endpoint, "ZERO_AUM", f"AUM is {aum}")
                            else:
                                print(f"   ✅ AUM: ${aum:,.2f}")
                                
                        elif endpoint.endswith('clients/all'):
                            clients = response_data.get('clients', [])
                            if not clients:
                                self.log_critical_error(endpoint, "NO_CLIENTS", "Empty clients array")
                            else:
                                print(f"   ✅ Clients found: {len(clients)}")
                                
                        elif 'investments/client' in endpoint:
                            investments = response_data.get('investments', [])
                            portfolio = response_data.get('portfolio', {})
                            print(f"   ✅ Investments: {len(investments)}, Portfolio: {bool(portfolio)}")
                            
                        elif 'redemptions/client' in endpoint:
                            redemptions = response_data.get('available_redemptions', [])
                            print(f"   ✅ Available redemptions: {len(redemptions)}")
                            
                    return True, response_data
                except Exception as e:
                    print(f"   ⚠️  JSON parsing error: {e}")
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                    
                    # Check for authentication errors
                    if response.status_code == 401:
                        self.log_critical_error(endpoint, "AUTH_ERROR", "JWT token invalid or expired")
                    elif response.status_code == 403:
                        self.log_critical_error(endpoint, "PERMISSION_ERROR", "Insufficient permissions")
                        
                except:
                    print(f"   Error text: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            self.log_critical_error(endpoint, "TIMEOUT", "Request timeout - possible database connection issue")
            print(f"❌ Failed - Request timeout")
            return False, {}
        except requests.exceptions.ConnectionError:
            self.log_critical_error(endpoint, "CONNECTION_ERROR", "Connection failed - service may be down")
            print(f"❌ Failed - Connection error")
            return False, {}
        except Exception as e:
            self.log_critical_error(endpoint, "UNKNOWN_ERROR", str(e))
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def authenticate_admin(self):
        """Authenticate as admin and get JWT token"""
        print("\n🔐 Authenticating as Admin...")
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
        if success and 'token' in response:
            self.admin_token = response['token']
            self.admin_user = response
            print(f"   ✅ Admin authenticated: {response.get('name', 'Unknown')}")
            print(f"   JWT Token: {self.admin_token[:50]}...")
            return True
        else:
            self.log_critical_error("api/auth/login", "ADMIN_AUTH_FAILED", "Cannot authenticate admin user")
            return False

    def authenticate_client(self):
        """Authenticate as client and get JWT token"""
        print("\n🔐 Authenticating as Client...")
        success, response = self.run_test(
            "Client Login",
            "POST", 
            "api/auth/login",
            200,
            data={
                "username": "client1",
                "password": "password123", 
                "user_type": "client"
            }
        )
        if success and 'token' in response:
            self.client_token = response['token']
            self.client_user = response
            print(f"   ✅ Client authenticated: {response.get('name', 'Unknown')}")
            print(f"   JWT Token: {self.client_token[:50]}...")
            return True
        else:
            self.log_critical_error("api/auth/login", "CLIENT_AUTH_FAILED", "Cannot authenticate client user")
            return False

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run basic test without authentication"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            else:
                response = requests.request(method, url, json=data, headers=headers, timeout=10)

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
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    # ===============================================================================
    # PRIORITY 1 - ADMIN ENDPOINTS (CRITICAL FOR ADMIN DASHBOARD)
    # ===============================================================================

    def test_admin_portfolio_summary(self):
        """Test admin portfolio summary - CRITICAL for admin dashboard"""
        if not self.admin_token:
            print("❌ Skipping admin portfolio summary - no admin token")
            return False
            
        success, response = self.run_authenticated_test(
            "Admin Portfolio Summary",
            "api/admin/portfolio-summary",
            200,
            self.admin_token
        )
        
        if success:
            # Verify critical fields are present and not zero
            aum = response.get('aum') or response.get('total_aum', 0)
            allocation = response.get('allocation', {})
            
            if aum > 0:
                print(f"   ✅ Total AUM: ${aum:,.2f}")
            else:
                self.log_critical_error("api/admin/portfolio-summary", "ZERO_AUM", f"AUM is {aum}")
                
            if allocation:
                print(f"   ✅ Fund allocation: {len(allocation)} funds")
                for fund, percentage in allocation.items():
                    print(f"     {fund}: {percentage}%")
            else:
                self.log_critical_error("api/admin/portfolio-summary", "NO_ALLOCATION", "Empty allocation data")
        
        return success

    def test_crm_admin_dashboard(self):
        """Test CRM admin dashboard data"""
        if not self.admin_token:
            print("❌ Skipping CRM admin dashboard - no admin token")
            return False
            
        success, response = self.run_authenticated_test(
            "CRM Admin Dashboard",
            "api/crm/admin/dashboard",
            200,
            self.admin_token
        )
        
        if success:
            # Check for CRM metrics
            total_prospects = response.get('total_prospects', 0)
            active_prospects = response.get('active_prospects', 0)
            conversion_rate = response.get('conversion_rate', 0)
            
            print(f"   ✅ Total prospects: {total_prospects}")
            print(f"   ✅ Active prospects: {active_prospects}")
            print(f"   ✅ Conversion rate: {conversion_rate}%")
        
        return success

    def test_admin_cashflow_overview(self):
        """Test admin cashflow overview - FIXED endpoint"""
        if not self.admin_token:
            print("❌ Skipping admin cashflow overview - no admin token")
            return False
            
        success, response = self.run_authenticated_test(
            "Admin Cashflow Overview",
            "api/admin/cashflow/overview",
            200,
            self.admin_token
        )
        
        if success:
            # Check cashflow data
            total_inflows = response.get('total_inflows', 0)
            total_outflows = response.get('total_outflows', 0)
            net_flow = response.get('net_flow', 0)
            
            print(f"   ✅ Total inflows: ${total_inflows:,.2f}")
            print(f"   ✅ Total outflows: ${total_outflows:,.2f}")
            print(f"   ✅ Net flow: ${net_flow:,.2f}")
            
            if total_inflows == 0 and total_outflows == 0:
                self.log_critical_error("api/admin/cashflow/overview", "NO_CASHFLOW_DATA", "All cashflow values are zero")
        
        return success

    def test_clients_all(self):
        """Test get all clients - CRITICAL for client management"""
        if not self.admin_token:
            print("❌ Skipping clients all - no admin token")
            return False
            
        success, response = self.run_authenticated_test(
            "Get All Clients",
            "api/clients/all",
            200,
            self.admin_token
        )
        
        if success:
            clients = response.get('clients', [])
            if clients:
                print(f"   ✅ Clients found: {len(clients)}")
                
                # Check first client structure
                client = clients[0]
                required_fields = ['id', 'name', 'email', 'type']
                missing_fields = [field for field in required_fields if field not in client]
                
                if missing_fields:
                    self.log_critical_error("api/clients/all", "MISSING_CLIENT_FIELDS", f"Missing: {missing_fields}")
                else:
                    print(f"   ✅ Client structure valid")
                    print(f"   Sample client: {client.get('name')} ({client.get('email')})")
            else:
                self.log_critical_error("api/clients/all", "NO_CLIENTS", "Empty clients array")
        
        return success

    def test_crm_prospects(self):
        """Test CRM prospects data"""
        if not self.admin_token:
            print("❌ Skipping CRM prospects - no admin token")
            return False
            
        success, response = self.run_authenticated_test(
            "CRM Prospects",
            "api/crm/prospects",
            200,
            self.admin_token
        )
        
        if success:
            prospects = response.get('prospects', [])
            pipeline_stats = response.get('pipeline_stats', {})
            
            print(f"   ✅ Prospects: {len(prospects)}")
            if pipeline_stats:
                print(f"   ✅ Pipeline stats: {pipeline_stats}")
        
        return success

    # ===============================================================================
    # PRIORITY 2 - CLIENT ENDPOINTS (CRITICAL FOR CLIENT PORTAL)
    # ===============================================================================

    def test_client_investments(self):
        """Test client investment data"""
        if not self.client_token or not self.client_user:
            print("❌ Skipping client investments - no client token")
            return False
            
        client_id = self.client_user.get('id')
        success, response = self.run_authenticated_test(
            "Client Investment Data",
            f"api/investments/client/{client_id}",
            200,
            self.client_token
        )
        
        if success:
            investments = response.get('investments', [])
            portfolio = response.get('portfolio', {})
            
            print(f"   ✅ Investments: {len(investments)}")
            
            if portfolio:
                total_invested = portfolio.get('total_invested', 0)
                current_value = portfolio.get('current_value', 0)
                total_return = portfolio.get('total_return', 0)
                
                print(f"   ✅ Total invested: ${total_invested:,.2f}")
                print(f"   ✅ Current value: ${current_value:,.2f}")
                print(f"   ✅ Total return: ${total_return:,.2f}")
                
                if current_value == 0 and len(investments) > 0:
                    self.log_critical_error(f"api/investments/client/{client_id}", "ZERO_PORTFOLIO_VALUE", "Portfolio value is zero despite having investments")
            else:
                print(f"   ⚠️  No portfolio data")
        
        return success

    def test_client_redemptions(self):
        """Test client redemption data"""
        if not self.client_token or not self.client_user:
            print("❌ Skipping client redemptions - no client token")
            return False
            
        client_id = self.client_user.get('id')
        success, response = self.run_authenticated_test(
            "Client Redemption Data",
            f"api/redemptions/client/{client_id}",
            200,
            self.client_token
        )
        
        if success:
            available_redemptions = response.get('available_redemptions', [])
            redemption_history = response.get('redemption_history', [])
            
            print(f"   ✅ Available redemptions: {len(available_redemptions)}")
            print(f"   ✅ Redemption history: {len(redemption_history)}")
            
            # Check redemption structure
            if available_redemptions:
                redemption = available_redemptions[0]
                required_fields = ['investment_id', 'fund_code', 'current_value', 'can_redeem']
                missing_fields = [field for field in required_fields if field not in redemption]
                
                if missing_fields:
                    self.log_critical_error(f"api/redemptions/client/{client_id}", "MISSING_REDEMPTION_FIELDS", f"Missing: {missing_fields}")
                else:
                    print(f"   ✅ Redemption structure valid")
        
        return success

    def test_client_mt5_performance(self):
        """Test client MT5 performance data"""
        if not self.client_token or not self.client_user:
            print("❌ Skipping client MT5 performance - no client token")
            return False
            
        client_id = self.client_user.get('id')
        success, response = self.run_authenticated_test(
            "Client MT5 Performance",
            f"api/mt5/client/{client_id}/performance",
            200,
            self.client_token
        )
        
        if success:
            mt5_accounts = response.get('mt5_accounts', [])
            performance_summary = response.get('performance_summary', {})
            
            print(f"   ✅ MT5 accounts: {len(mt5_accounts)}")
            
            if performance_summary:
                total_equity = performance_summary.get('total_equity', 0)
                total_profit_loss = performance_summary.get('total_profit_loss', 0)
                
                print(f"   ✅ Total equity: ${total_equity:,.2f}")
                print(f"   ✅ Total P&L: ${total_profit_loss:,.2f}")
        
        return success

    # ===============================================================================
    # PRIORITY 3 - DOCUMENT/SETTINGS ENDPOINTS
    # ===============================================================================

    def test_documents_admin_all(self):
        """Test admin documents portal"""
        if not self.admin_token:
            print("❌ Skipping admin documents - no admin token")
            return False
            
        success, response = self.run_authenticated_test(
            "Admin Documents Portal",
            "api/documents/admin/all",
            200,
            self.admin_token
        )
        
        if success:
            documents = response.get('documents', [])
            print(f"   ✅ Documents: {len(documents)}")
            
            if documents:
                doc = documents[0]
                required_fields = ['id', 'name', 'category', 'status']
                missing_fields = [field for field in required_fields if field not in doc]
                
                if missing_fields:
                    self.log_critical_error("api/documents/admin/all", "MISSING_DOCUMENT_FIELDS", f"Missing: {missing_fields}")
                else:
                    print(f"   ✅ Document structure valid")
        
        return success

    def test_gmail_settings(self):
        """Test Gmail settings"""
        if not self.admin_token:
            print("❌ Skipping Gmail settings - no admin token")
            return False
            
        success, response = self.run_authenticated_test(
            "Gmail Settings",
            "api/gmail/settings",
            200,
            self.admin_token
        )
        
        if success:
            settings = response.get('settings', {})
            oauth_status = response.get('oauth_status', 'unknown')
            
            print(f"   ✅ OAuth status: {oauth_status}")
            print(f"   ✅ Settings: {bool(settings)}")
        
        return success

    # ===============================================================================
    # ADDITIONAL CRITICAL ENDPOINTS
    # ===============================================================================

    def test_admin_funds_overview(self):
        """Test admin funds overview"""
        if not self.admin_token:
            print("❌ Skipping admin funds overview - no admin token")
            return False
            
        success, response = self.run_authenticated_test(
            "Admin Funds Overview",
            "api/admin/funds-overview",
            200,
            self.admin_token
        )
        
        if success:
            funds = response.get('funds', [])
            total_aum = response.get('total_aum', 0)
            total_investors = response.get('total_investors', 0)
            
            print(f"   ✅ Funds: {len(funds)}")
            print(f"   ✅ Total AUM: ${total_aum:,.2f}")
            print(f"   ✅ Total investors: {total_investors}")
            
            if total_aum == 0:
                self.log_critical_error("api/admin/funds-overview", "ZERO_FUND_AUM", "Total fund AUM is zero")
        
        return success

    def test_investments_admin_overview(self):
        """Test admin investments overview"""
        if not self.admin_token:
            print("❌ Skipping admin investments overview - no admin token")
            return False
            
        success, response = self.run_authenticated_test(
            "Admin Investments Overview",
            "api/investments/admin/overview",
            200,
            self.admin_token
        )
        
        if success:
            total_aum = response.get('total_aum', 0)
            clients = response.get('clients', [])
            fund_summaries = response.get('fund_summaries', [])
            
            print(f"   ✅ Total AUM: ${total_aum:,.2f}")
            print(f"   ✅ Clients: {len(clients)}")
            print(f"   ✅ Fund summaries: {len(fund_summaries)}")
            
            if total_aum == 0:
                self.log_critical_error("api/investments/admin/overview", "ZERO_INVESTMENT_AUM", "Investment AUM is zero")
        
        return success

    def run_all_tests(self):
        """Run all production database integration tests"""
        print("=" * 80)
        print("🚀 STARTING CRITICAL PRODUCTION DATABASE INTEGRATION TEST")
        print("=" * 80)
        print("GOAL: ZERO DATABASE ERRORS IN PRODUCTION SYSTEM")
        print()
        
        # Step 1: Authentication
        print("📋 STEP 1: AUTHENTICATION")
        admin_auth = self.authenticate_admin()
        client_auth = self.authenticate_client()
        
        if not admin_auth:
            print("🚨 CRITICAL: Cannot authenticate admin - stopping tests")
            return False
            
        if not client_auth:
            print("🚨 CRITICAL: Cannot authenticate client - some tests will be skipped")
        
        # Step 2: Priority 1 - Admin Endpoints
        print("\n📋 STEP 2: PRIORITY 1 - ADMIN ENDPOINTS (CRITICAL)")
        self.test_admin_portfolio_summary()
        self.test_crm_admin_dashboard()
        self.test_admin_cashflow_overview()
        self.test_clients_all()
        self.test_crm_prospects()
        
        # Step 3: Priority 2 - Client Endpoints
        print("\n📋 STEP 3: PRIORITY 2 - CLIENT ENDPOINTS")
        if client_auth:
            self.test_client_investments()
            self.test_client_redemptions()
            self.test_client_mt5_performance()
        else:
            print("⚠️  Skipping client endpoint tests - authentication failed")
        
        # Step 4: Priority 3 - Document/Settings
        print("\n📋 STEP 4: PRIORITY 3 - DOCUMENT/SETTINGS ENDPOINTS")
        self.test_documents_admin_all()
        self.test_gmail_settings()
        
        # Step 5: Additional Critical Endpoints
        print("\n📋 STEP 5: ADDITIONAL CRITICAL ENDPOINTS")
        self.test_admin_funds_overview()
        self.test_investments_admin_overview()
        
        # Final Results
        self.print_final_results()
        
        return len(self.critical_errors) == 0

    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("📊 PRODUCTION DATABASE INTEGRATION TEST RESULTS")
        print("=" * 80)
        
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.critical_errors:
            print(f"\n🚨 CRITICAL ERRORS FOUND: {len(self.critical_errors)}")
            print("=" * 50)
            
            for i, error in enumerate(self.critical_errors, 1):
                print(f"{i}. {error['endpoint']}")
                print(f"   Type: {error['error_type']}")
                print(f"   Details: {error['details']}")
                print(f"   Time: {error['timestamp']}")
                print()
                
            print("🚨 PRODUCTION SYSTEM HAS DATABASE ERRORS - IMMEDIATE ACTION REQUIRED!")
        else:
            print("\n✅ ZERO DATABASE ERRORS FOUND!")
            print("✅ PRODUCTION SYSTEM IS HEALTHY!")
            
        print("=" * 80)

if __name__ == "__main__":
    tester = ProductionDatabaseTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)