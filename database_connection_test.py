#!/usr/bin/env python3
"""
URGENT DATABASE CONNECTION VERIFICATION TEST
===========================================

This test investigates the critical database connection issue as requested in the urgent review:
- Check which database the backend is actually connected to
- Verify Salvador Palma's data location in current backend instance
- Check database consistency between frontend and backend
- Verify environment configuration

CRITICAL ISSUE IDENTIFIED:
- Frontend .env: REACT_APP_BACKEND_URL=https://crm-workspace-1.preview.emergentagent.com
- Backend .env: MONGO_URL="mongodb://localhost:27017" with DB_NAME="fidus_investment_db"

INVESTIGATION REQUIRED:
1. Check current backend database connection
2. Verify Salvador Palma's data location
3. Check database consistency
4. Environment verification
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration - Use the EXACT URLs from the review request
FRONTEND_BACKEND_URL = "https://crm-workspace-1.preview.emergentagent.com/api"  # From frontend .env
LOCAL_BACKEND_URL = "http://localhost:8001/api"  # Local backend if running
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class DatabaseConnectionVerificationTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.current_backend_url = None
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {json.dumps(details, indent=2)}")
    
    def test_backend_connectivity(self):
        """Test which backend URL is actually accessible"""
        backends_to_test = [
            (FRONTEND_BACKEND_URL, "Frontend Backend (from .env)"),
            (LOCAL_BACKEND_URL, "Local Backend"),
        ]
        
        accessible_backends = []
        
        for backend_url, description in backends_to_test:
            try:
                response = requests.get(f"{backend_url}/health", timeout=10)
                if response.status_code == 200:
                    health_data = response.json()
                    accessible_backends.append((backend_url, description, health_data))
                    self.log_result(f"Backend Connectivity - {description}", True, 
                                  f"Backend accessible at {backend_url}",
                                  {"health_data": health_data})
                else:
                    self.log_result(f"Backend Connectivity - {description}", False, 
                                  f"HTTP {response.status_code} at {backend_url}")
            except Exception as e:
                self.log_result(f"Backend Connectivity - {description}", False, 
                              f"Connection failed to {backend_url}: {str(e)}")
        
        if accessible_backends:
            # Use the first accessible backend (prioritize frontend backend)
            self.current_backend_url = accessible_backends[0][0]
            self.log_result("Primary Backend Selection", True, 
                          f"Using backend: {self.current_backend_url}")
            return True
        else:
            self.log_result("Backend Connectivity", False, 
                          "No accessible backends found")
            return False
    
    def authenticate_admin(self):
        """Authenticate as admin user with current backend"""
        if not self.current_backend_url:
            return False
            
        try:
            response = self.session.post(f"{self.current_backend_url}/auth/login", json={
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                if self.admin_token:
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    self.log_result("Admin Authentication", True, 
                                  f"Successfully authenticated with {self.current_backend_url}")
                    return True
                else:
                    self.log_result("Admin Authentication", False, "No token received", {"response": data})
                    return False
            else:
                self.log_result("Admin Authentication", False, f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_database_connection_info(self):
        """Test database connection information from backend"""
        try:
            # Try to get database info from health endpoints
            response = self.session.get(f"{self.current_backend_url}/health/ready")
            if response.status_code == 200:
                health_data = response.json()
                database_status = health_data.get('database', 'unknown')
                self.log_result("Database Connection Status", True, 
                              f"Database status: {database_status}",
                              {"health_data": health_data})
            else:
                self.log_result("Database Connection Status", False, 
                              f"Health check failed: HTTP {response.status_code}")
            
            # Try to get detailed metrics
            response = self.session.get(f"{self.current_backend_url}/health/metrics")
            if response.status_code == 200:
                metrics = response.json()
                db_info = metrics.get('database', {})
                self.log_result("Database Metrics", True, 
                              "Database metrics retrieved",
                              {"database_info": db_info})
            else:
                self.log_result("Database Metrics", False, 
                              f"Metrics unavailable: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Database Connection Info", False, f"Exception: {str(e)}")
    
    def test_salvador_data_location(self):
        """Test Salvador Palma's data location in current backend"""
        try:
            # Test 1: Check if Salvador exists in clients
            response = self.session.get(f"{self.current_backend_url}/admin/clients")
            salvador_in_clients = False
            total_clients = 0
            
            if response.status_code == 200:
                clients_response = response.json()
                
                # Handle both list format and object format with 'clients' key
                if isinstance(clients_response, list):
                    clients = clients_response
                elif isinstance(clients_response, dict) and 'clients' in clients_response:
                    clients = clients_response['clients']
                else:
                    clients = []
                
                if isinstance(clients, list):
                    total_clients = len(clients)
                    for client in clients:
                        if client.get('id') == 'client_003' or 'SALVADOR' in client.get('name', '').upper():
                            salvador_in_clients = True
                            self.log_result("Salvador in Clients List", True, 
                                          f"Salvador Palma found in clients (Total clients: {total_clients})",
                                          {"salvador_data": client})
                            break
                    
                    if not salvador_in_clients:
                        self.log_result("Salvador in Clients List", False, 
                                      f"Salvador Palma NOT found in {total_clients} clients",
                                      {"all_clients": clients})
                else:
                    self.log_result("Salvador in Clients List", False, 
                                  "Clients endpoint returned invalid format",
                                  {"response": clients_response})
            else:
                self.log_result("Salvador in Clients List", False, 
                              f"Failed to get clients: HTTP {response.status_code}")
            
            # Test 2: Check Salvador's investments
            response = self.session.get(f"{self.current_backend_url}/investments/client/client_003")
            salvador_investments = []
            
            if response.status_code == 200:
                investments_response = response.json()
                
                # Handle both list format and object format with 'investments' key
                if isinstance(investments_response, list):
                    investments = investments_response
                elif isinstance(investments_response, dict) and 'investments' in investments_response:
                    investments = investments_response['investments']
                else:
                    investments = []
                
                if isinstance(investments, list):
                    salvador_investments = investments
                    if len(investments) > 0:
                        total_value = sum(inv.get('current_value', 0) for inv in investments)
                        self.log_result("Salvador Investments", True, 
                                      f"Found {len(investments)} investments, Total value: ${total_value:,.2f}",
                                      {"investments": investments})
                    else:
                        self.log_result("Salvador Investments", False, 
                                      "Salvador has 0 investments in current database")
                else:
                    self.log_result("Salvador Investments", False, 
                                  "Investments endpoint returned invalid format",
                                  {"response": investments_response})
            else:
                self.log_result("Salvador Investments", False, 
                              f"Failed to get Salvador's investments: HTTP {response.status_code}")
            
            # Test 3: Check Salvador's MT5 accounts
            response = self.session.get(f"{self.current_backend_url}/mt5/admin/accounts")
            salvador_mt5_accounts = []
            
            if response.status_code == 200:
                mt5_response = response.json()
                
                # Handle both list format and object format
                if isinstance(mt5_response, list):
                    all_mt5_accounts = mt5_response
                elif isinstance(mt5_response, dict) and 'accounts' in mt5_response:
                    all_mt5_accounts = mt5_response['accounts']
                else:
                    all_mt5_accounts = []
                
                # Filter for Salvador's accounts
                if isinstance(all_mt5_accounts, list):
                    for account in all_mt5_accounts:
                        if account.get('client_id') == 'client_003':
                            salvador_mt5_accounts.append(account)
                    
                    if len(salvador_mt5_accounts) > 0:
                        self.log_result("Salvador MT5 Accounts", True, 
                                      f"Found {len(salvador_mt5_accounts)} MT5 accounts for Salvador",
                                      {"mt5_accounts": salvador_mt5_accounts})
                    else:
                        self.log_result("Salvador MT5 Accounts", False, 
                                      "Salvador has 0 MT5 accounts in current database",
                                      {"total_mt5_accounts": len(all_mt5_accounts)})
                else:
                    self.log_result("Salvador MT5 Accounts", False, 
                                  "MT5 accounts endpoint returned invalid format",
                                  {"response": mt5_response})
            else:
                self.log_result("Salvador MT5 Accounts", False, 
                              f"Failed to get MT5 accounts: HTTP {response.status_code}")
            
            # Summary of Salvador's data location
            salvador_data_exists = salvador_in_clients or len(salvador_investments) > 0 or len(salvador_mt5_accounts) > 0
            
            if salvador_data_exists:
                self.log_result("Salvador Data Location Summary", True, 
                              f"Salvador's data EXISTS in current backend database",
                              {
                                  "backend_url": self.current_backend_url,
                                  "client_profile": salvador_in_clients,
                                  "investments_count": len(salvador_investments),
                                  "mt5_accounts_count": len(salvador_mt5_accounts)
                              })
            else:
                self.log_result("Salvador Data Location Summary", False, 
                              f"Salvador's data MISSING from current backend database",
                              {
                                  "backend_url": self.current_backend_url,
                                  "total_clients": total_clients,
                                  "client_profile": salvador_in_clients,
                                  "investments_count": len(salvador_investments),
                                  "mt5_accounts_count": len(salvador_mt5_accounts)
                              })
                
        except Exception as e:
            self.log_result("Salvador Data Location", False, f"Exception: {str(e)}")
    
    def test_environment_configuration(self):
        """Test environment configuration consistency"""
        try:
            # Check what backend URL the frontend should be using
            frontend_backend = FRONTEND_BACKEND_URL
            current_backend = self.current_backend_url
            
            if frontend_backend == current_backend:
                self.log_result("Environment Configuration", True, 
                              "Frontend and current backend URLs match",
                              {
                                  "frontend_backend_url": frontend_backend,
                                  "current_backend_url": current_backend
                              })
            else:
                self.log_result("Environment Configuration", False, 
                              "Frontend and current backend URLs DO NOT match",
                              {
                                  "frontend_backend_url": frontend_backend,
                                  "current_backend_url": current_backend,
                                  "issue": "Frontend may be connecting to different backend than tested"
                              })
            
            # Test if we can access the frontend's expected backend
            try:
                response = requests.get(f"{frontend_backend}/health", timeout=10)
                if response.status_code == 200:
                    health_data = response.json()
                    self.log_result("Frontend Backend Accessibility", True, 
                                  f"Frontend's expected backend is accessible",
                                  {"health_data": health_data})
                else:
                    self.log_result("Frontend Backend Accessibility", False, 
                                  f"Frontend's expected backend returned HTTP {response.status_code}")
            except Exception as e:
                self.log_result("Frontend Backend Accessibility", False, 
                              f"Frontend's expected backend not accessible: {str(e)}")
                
        except Exception as e:
            self.log_result("Environment Configuration", False, f"Exception: {str(e)}")
    
    def test_database_consistency(self):
        """Test database consistency across different endpoints"""
        try:
            # Get data from multiple endpoints and check consistency
            endpoints_data = {}
            
            # Test fund performance dashboard
            response = self.session.get(f"{self.current_backend_url}/admin/fund-performance/dashboard")
            if response.status_code == 200:
                endpoints_data['fund_performance'] = response.json()
                self.log_result("Fund Performance Dashboard", True, "Data retrieved successfully")
            else:
                self.log_result("Fund Performance Dashboard", False, f"HTTP {response.status_code}")
            
            # Test cash flow overview
            response = self.session.get(f"{self.current_backend_url}/admin/cashflow/overview")
            if response.status_code == 200:
                endpoints_data['cash_flow'] = response.json()
                self.log_result("Cash Flow Overview", True, "Data retrieved successfully")
            else:
                self.log_result("Cash Flow Overview", False, f"HTTP {response.status_code}")
            
            # Check if data is consistent (non-zero values indicate data exists)
            has_fund_data = False
            has_cash_flow_data = False
            
            if 'fund_performance' in endpoints_data:
                fund_data = endpoints_data['fund_performance']
                # Look for non-zero values in fund performance
                if isinstance(fund_data, dict):
                    for key, value in fund_data.items():
                        if isinstance(value, (int, float)) and value != 0:
                            has_fund_data = True
                            break
            
            if 'cash_flow' in endpoints_data:
                cash_data = endpoints_data['cash_flow']
                # Look for non-zero values in cash flow
                if isinstance(cash_data, dict):
                    for key, value in cash_data.items():
                        if isinstance(value, (int, float)) and value != 0:
                            has_cash_flow_data = True
                            break
            
            if has_fund_data or has_cash_flow_data:
                self.log_result("Database Consistency", True, 
                              "Database contains financial data (non-zero values found)",
                              {
                                  "fund_performance_has_data": has_fund_data,
                                  "cash_flow_has_data": has_cash_flow_data
                              })
            else:
                self.log_result("Database Consistency", False, 
                              "Database appears empty (all zero values)",
                              {
                                  "fund_performance_data": endpoints_data.get('fund_performance'),
                                  "cash_flow_data": endpoints_data.get('cash_flow')
                              })
                
        except Exception as e:
            self.log_result("Database Consistency", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all database connection verification tests"""
        print("🚨 URGENT DATABASE CONNECTION VERIFICATION TEST")
        print("=" * 60)
        print("CRITICAL ISSUE INVESTIGATION:")
        print(f"Frontend Backend URL: {FRONTEND_BACKEND_URL}")
        print(f"Local Backend URL: {LOCAL_BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Test backend connectivity first
        if not self.test_backend_connectivity():
            print("❌ CRITICAL: No accessible backends found. Cannot proceed with tests.")
            return False
        
        # Authenticate with the accessible backend
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print(f"\n🔍 Running Database Connection Verification Tests on: {self.current_backend_url}")
        print("-" * 70)
        
        # Run all verification tests
        self.test_database_connection_info()
        self.test_salvador_data_location()
        self.test_environment_configuration()
        self.test_database_consistency()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 70)
        print("🚨 DATABASE CONNECTION VERIFICATION SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Backend Tested: {self.current_backend_url}")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Show critical findings
        print("🔍 CRITICAL FINDINGS:")
        
        # Check Salvador data existence
        salvador_tests = [r for r in self.test_results if 'Salvador' in r['test']]
        salvador_data_found = any(r['success'] for r in salvador_tests)
        
        if salvador_data_found:
            print("✅ Salvador Palma's data EXISTS in current backend database")
        else:
            print("❌ Salvador Palma's data MISSING from current backend database")
        
        # Check environment consistency
        env_tests = [r for r in self.test_results if 'Environment' in r['test']]
        env_consistent = any(r['success'] for r in env_tests)
        
        if env_consistent:
            print("✅ Frontend and backend environment configuration is consistent")
        else:
            print("❌ Frontend and backend environment configuration MISMATCH detected")
        
        # Check database connectivity
        db_tests = [r for r in self.test_results if 'Database' in r['test']]
        db_connected = any(r['success'] for r in db_tests)
        
        if db_connected:
            print("✅ Backend is connected to a database with data")
        else:
            print("❌ Backend database connection issues or empty database")
        
        print()
        
        # Show failed tests details
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Root cause analysis
        print("🎯 ROOT CAUSE ANALYSIS:")
        
        if not salvador_data_found and not env_consistent:
            print("❌ CRITICAL: Salvador's data missing AND environment mismatch")
            print("   → Frontend may be connecting to different backend/database than expected")
            print("   → This explains ALL user-reported issues (missing Salvador, zero values)")
        elif not salvador_data_found:
            print("❌ CRITICAL: Salvador's data missing from current database")
            print("   → Data may exist in different database instance")
            print("   → Database restoration or migration required")
        elif not env_consistent:
            print("⚠️  WARNING: Environment configuration mismatch")
            print("   → Frontend may not be using the correct backend URL")
            print("   → Verify frontend .env configuration")
        else:
            print("✅ No critical issues detected in database connection")
        
        print("\n" + "=" * 70)

def main():
    """Main test execution"""
    test_runner = DatabaseConnectionVerificationTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()