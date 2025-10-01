#!/usr/bin/env python3
"""
SCHEMA TEST USER DELETION INVESTIGATION
======================================

This test investigates the specific issue where user tried to delete "Schema Test User" 
and couldn't do it after clicking "OK".

Investigation Areas:
1. Find Schema Test User via GET /api/admin/clients
2. Get the client ID for "Schema Test User" 
3. Test deletion of Schema Test User via DELETE /api/admin/clients/{schema_test_user_id}
4. Check for any special constraints preventing deletion
5. Test client refresh after deletion
6. Check frontend API call investigation
7. Check database dependencies

Expected Results:
- Schema Test User should be found in clients list
- DELETE operation should work or provide clear error message
- Any dependencies should be identified
- Frontend refresh should work properly
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://crm-workspace-1.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class SchemaTestUserDeletionTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.schema_test_user = None
        
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
            print(f"   Details: {details}")
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                if self.admin_token:
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    self.log_result("Admin Authentication", True, "Successfully authenticated as admin")
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
    
    def find_schema_test_user(self):
        """Find Schema Test User in clients list"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            if response.status_code == 200:
                clients_data = response.json()
                
                # Handle different response formats
                if isinstance(clients_data, list):
                    clients = clients_data
                elif isinstance(clients_data, dict) and 'clients' in clients_data:
                    clients = clients_data['clients']
                elif isinstance(clients_data, dict) and 'users' in clients_data:
                    clients = clients_data['users']
                else:
                    clients = []
                
                # Search for Schema Test User
                schema_test_users = []
                for client in clients:
                    client_name = client.get('name', '').lower()
                    client_username = client.get('username', '').lower()
                    
                    if ('schema' in client_name and 'test' in client_name) or \
                       ('schema' in client_username and 'test' in client_username) or \
                       client_name == 'schema test user' or \
                       client_username == 'test_schema':
                        schema_test_users.append(client)
                
                if schema_test_users:
                    self.schema_test_user = schema_test_users[0]  # Take the first match
                    self.log_result("Find Schema Test User", True, 
                                  f"Found Schema Test User: {self.schema_test_user.get('name')} (ID: {self.schema_test_user.get('id')})",
                                  {"user_data": self.schema_test_user, "total_matches": len(schema_test_users)})
                    return True
                else:
                    # List all clients for debugging
                    client_names = [f"{c.get('name', 'N/A')} (ID: {c.get('id', 'N/A')})" for c in clients[:10]]
                    self.log_result("Find Schema Test User", False, 
                                  "Schema Test User not found in clients list",
                                  {"total_clients": len(clients), "sample_clients": client_names})
                    return False
            else:
                self.log_result("Find Schema Test User", False, 
                              f"Failed to get clients: HTTP {response.status_code}",
                              {"response": response.text[:500]})
                return False
                
        except Exception as e:
            self.log_result("Find Schema Test User", False, f"Exception: {str(e)}")
            return False
    
    def check_user_dependencies(self):
        """Check if Schema Test User has any dependencies that might prevent deletion"""
        if not self.schema_test_user:
            self.log_result("Check User Dependencies", False, "No Schema Test User found to check dependencies")
            return
        
        user_id = self.schema_test_user.get('id')
        dependencies_found = []
        
        try:
            # Check for investments
            response = self.session.get(f"{BACKEND_URL}/investments/client/{user_id}")
            if response.status_code == 200:
                investments = response.json()
                if investments and len(investments) > 0:
                    dependencies_found.append(f"Investments: {len(investments)} found")
                    self.log_result("Check Dependencies - Investments", False, 
                                  f"Found {len(investments)} investments for Schema Test User",
                                  {"investments": investments})
                else:
                    self.log_result("Check Dependencies - Investments", True, "No investments found")
            else:
                self.log_result("Check Dependencies - Investments", True, 
                              f"No investments endpoint or user has no investments (HTTP {response.status_code})")
            
            # Check for MT5 accounts
            response = self.session.get(f"{BACKEND_URL}/mt5/admin/accounts")
            if response.status_code == 200:
                mt5_accounts = response.json()
                user_mt5_accounts = []
                if isinstance(mt5_accounts, list):
                    user_mt5_accounts = [acc for acc in mt5_accounts if acc.get('client_id') == user_id]
                
                if user_mt5_accounts:
                    dependencies_found.append(f"MT5 Accounts: {len(user_mt5_accounts)} found")
                    self.log_result("Check Dependencies - MT5 Accounts", False, 
                                  f"Found {len(user_mt5_accounts)} MT5 accounts for Schema Test User",
                                  {"mt5_accounts": user_mt5_accounts})
                else:
                    self.log_result("Check Dependencies - MT5 Accounts", True, "No MT5 accounts found")
            else:
                self.log_result("Check Dependencies - MT5 Accounts", True, 
                              f"No MT5 accounts endpoint or user has no accounts (HTTP {response.status_code})")
            
            # Check for transactions
            response = self.session.get(f"{BACKEND_URL}/client/{user_id}/data")
            if response.status_code == 200:
                client_data = response.json()
                transactions = client_data.get('transactions', [])
                if transactions and len(transactions) > 0:
                    dependencies_found.append(f"Transactions: {len(transactions)} found")
                    self.log_result("Check Dependencies - Transactions", False, 
                                  f"Found {len(transactions)} transactions for Schema Test User",
                                  {"transaction_count": len(transactions)})
                else:
                    self.log_result("Check Dependencies - Transactions", True, "No transactions found")
            else:
                self.log_result("Check Dependencies - Transactions", True, 
                              f"No client data endpoint or user has no transactions (HTTP {response.status_code})")
            
            # Check for CRM prospects (if user was converted from prospect)
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            if response.status_code == 200:
                prospects_data = response.json()
                prospects = prospects_data.get('prospects', []) if isinstance(prospects_data, dict) else prospects_data
                
                related_prospects = []
                if isinstance(prospects, list):
                    for prospect in prospects:
                        if (prospect.get('client_id') == user_id or 
                            prospect.get('converted_to_client') == True and 
                            'schema' in prospect.get('name', '').lower()):
                            related_prospects.append(prospect)
                
                if related_prospects:
                    dependencies_found.append(f"CRM Prospects: {len(related_prospects)} found")
                    self.log_result("Check Dependencies - CRM Prospects", False, 
                                  f"Found {len(related_prospects)} related CRM prospects",
                                  {"prospects": related_prospects})
                else:
                    self.log_result("Check Dependencies - CRM Prospects", True, "No related CRM prospects found")
            else:
                self.log_result("Check Dependencies - CRM Prospects", True, 
                              f"No CRM prospects endpoint (HTTP {response.status_code})")
            
            # Summary of dependencies
            if dependencies_found:
                self.log_result("User Dependencies Summary", False, 
                              f"Schema Test User has dependencies that may prevent deletion: {', '.join(dependencies_found)}",
                              {"dependencies": dependencies_found})
            else:
                self.log_result("User Dependencies Summary", True, 
                              "No dependencies found - user should be safe to delete")
                
        except Exception as e:
            self.log_result("Check User Dependencies", False, f"Exception: {str(e)}")
    
    def test_user_deletion(self):
        """Test deletion of Schema Test User"""
        if not self.schema_test_user:
            self.log_result("Test User Deletion", False, "No Schema Test User found to delete")
            return
        
        user_id = self.schema_test_user.get('id')
        user_name = self.schema_test_user.get('name', 'Unknown')
        
        try:
            # First, check if DELETE endpoint exists and what it expects
            response = self.session.delete(f"{BACKEND_URL}/admin/clients/{user_id}")
            
            if response.status_code == 200:
                self.log_result("Test User Deletion", True, 
                              f"Successfully deleted Schema Test User: {user_name}",
                              {"response": response.json() if response.content else "No response body"})
                
                # Verify deletion by trying to find the user again
                time.sleep(1)  # Brief pause to allow database update
                self.verify_user_deletion(user_id, user_name)
                
            elif response.status_code == 404:
                self.log_result("Test User Deletion", False, 
                              "DELETE endpoint not found - endpoint may not be implemented",
                              {"status_code": response.status_code, "response": response.text})
                
            elif response.status_code == 405:
                self.log_result("Test User Deletion", False, 
                              "Method not allowed - DELETE may not be supported on this endpoint",
                              {"status_code": response.status_code, "response": response.text})
                
            elif response.status_code == 400:
                self.log_result("Test User Deletion", False, 
                              "Bad request - user may have dependencies preventing deletion",
                              {"status_code": response.status_code, "response": response.text})
                
            elif response.status_code == 403:
                self.log_result("Test User Deletion", False, 
                              "Forbidden - insufficient permissions or user protected from deletion",
                              {"status_code": response.status_code, "response": response.text})
                
            elif response.status_code == 409:
                self.log_result("Test User Deletion", False, 
                              "Conflict - user has dependencies that prevent deletion",
                              {"status_code": response.status_code, "response": response.text})
                
            else:
                self.log_result("Test User Deletion", False, 
                              f"Unexpected response: HTTP {response.status_code}",
                              {"status_code": response.status_code, "response": response.text})
                
        except Exception as e:
            self.log_result("Test User Deletion", False, f"Exception during deletion: {str(e)}")
    
    def verify_user_deletion(self, user_id, user_name):
        """Verify that the user was actually deleted"""
        try:
            # Try to find the user again
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            if response.status_code == 200:
                clients_data = response.json()
                
                # Handle different response formats
                if isinstance(clients_data, list):
                    clients = clients_data
                elif isinstance(clients_data, dict) and 'clients' in clients_data:
                    clients = clients_data['clients']
                else:
                    clients = []
                
                # Look for the deleted user
                user_still_exists = False
                for client in clients:
                    if client.get('id') == user_id:
                        user_still_exists = True
                        break
                
                if user_still_exists:
                    self.log_result("Verify User Deletion", False, 
                                  f"User {user_name} still exists after deletion attempt",
                                  {"user_id": user_id})
                else:
                    self.log_result("Verify User Deletion", True, 
                                  f"User {user_name} successfully removed from clients list")
            else:
                self.log_result("Verify User Deletion", False, 
                              f"Could not verify deletion - failed to get clients list: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Verify User Deletion", False, f"Exception during verification: {str(e)}")
    
    def test_frontend_api_calls(self):
        """Test the API calls that frontend should be making for deletion"""
        try:
            # Test the endpoints that frontend might be calling
            frontend_endpoints = [
                ("/admin/clients", "GET", "Get clients list"),
                ("/admin/users", "GET", "Get users list (alternative endpoint)"),
            ]
            
            for endpoint, method, description in frontend_endpoints:
                try:
                    if method == "GET":
                        response = self.session.get(f"{BACKEND_URL}{endpoint}")
                    else:
                        continue  # Skip non-GET methods for now
                    
                    if response.status_code == 200:
                        self.log_result(f"Frontend API - {description}", True, 
                                      f"{method} {endpoint} working correctly")
                    else:
                        self.log_result(f"Frontend API - {description}", False, 
                                      f"{method} {endpoint} failed: HTTP {response.status_code}")
                        
                except Exception as e:
                    self.log_result(f"Frontend API - {description}", False, 
                                  f"Exception on {method} {endpoint}: {str(e)}")
            
            # Test authentication requirements
            temp_session = requests.Session()  # Session without auth token
            response = temp_session.get(f"{BACKEND_URL}/admin/clients")
            
            if response.status_code == 401:
                self.log_result("Frontend API - Authentication", True, 
                              "Endpoints properly require authentication")
            else:
                self.log_result("Frontend API - Authentication", False, 
                              f"Endpoints may not require authentication: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Test Frontend API Calls", False, f"Exception: {str(e)}")
    
    def test_client_refresh_functionality(self):
        """Test client list refresh functionality"""
        try:
            # Get initial client count
            response1 = self.session.get(f"{BACKEND_URL}/admin/clients")
            if response1.status_code == 200:
                clients_data1 = response1.json()
                initial_count = len(clients_data1) if isinstance(clients_data1, list) else len(clients_data1.get('clients', []))
                
                # Wait a moment and get count again
                time.sleep(1)
                response2 = self.session.get(f"{BACKEND_URL}/admin/clients")
                
                if response2.status_code == 200:
                    clients_data2 = response2.json()
                    second_count = len(clients_data2) if isinstance(clients_data2, list) else len(clients_data2.get('clients', []))
                    
                    self.log_result("Client Refresh Functionality", True, 
                                  f"Client list refresh working - consistent count: {initial_count} -> {second_count}")
                else:
                    self.log_result("Client Refresh Functionality", False, 
                                  f"Second refresh failed: HTTP {response2.status_code}")
            else:
                self.log_result("Client Refresh Functionality", False, 
                              f"Initial client list fetch failed: HTTP {response1.status_code}")
                
        except Exception as e:
            self.log_result("Client Refresh Functionality", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all Schema Test User deletion investigation tests"""
        print("🔍 SCHEMA TEST USER DELETION INVESTIGATION")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Schema Test User Deletion Investigation...")
        print("-" * 50)
        
        # Run all investigation tests
        self.find_schema_test_user()
        self.check_user_dependencies()
        self.test_user_deletion()
        self.test_frontend_api_calls()
        self.test_client_refresh_functionality()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🔍 SCHEMA TEST USER DELETION INVESTIGATION SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Show failed tests (these are the issues)
        if failed_tests > 0:
            print("❌ ISSUES FOUND:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Show passed tests
        if passed_tests > 0:
            print("✅ WORKING CORRECTLY:")
            for result in self.test_results:
                if result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Investigation conclusions
        print("🚨 INVESTIGATION CONCLUSIONS:")
        
        if self.schema_test_user:
            print(f"✅ Schema Test User Found: {self.schema_test_user.get('name')} (ID: {self.schema_test_user.get('id')})")
            
            # Check if deletion was successful
            deletion_successful = any(result['success'] and 'deletion' in result['test'].lower() 
                                    for result in self.test_results)
            
            if deletion_successful:
                print("✅ DELETION SUCCESSFUL: Schema Test User was successfully deleted")
            else:
                print("❌ DELETION FAILED: Schema Test User could not be deleted")
                
                # Identify likely causes
                dependency_issues = any('dependencies' in result['test'].lower() and not result['success'] 
                                      for result in self.test_results)
                endpoint_issues = any('endpoint' in result['message'].lower() or 'method not allowed' in result['message'].lower()
                                    for result in self.test_results if not result['success'])
                
                if dependency_issues:
                    print("   → LIKELY CAUSE: User has dependencies (investments, MT5 accounts, etc.)")
                elif endpoint_issues:
                    print("   → LIKELY CAUSE: DELETE endpoint not implemented or not working")
                else:
                    print("   → LIKELY CAUSE: Unknown - check detailed logs above")
        else:
            print("❌ Schema Test User Not Found: User may have been already deleted or named differently")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = SchemaTestUserDeletionTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()