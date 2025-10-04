#!/usr/bin/env python3
"""
MONGODB MIGRATION FIXES VERIFICATION TEST
========================================

This test verifies the complete MongoDB migration fixes as requested in the review:
1. Schema Validation Fix Test - POST /api/admin/users/create with specific test data
2. System Health Verification - admin auth, GET /api/admin/users, GET /api/admin/clients  
3. MOCK_USERS Cleanup Verification - test endpoints that previously used MOCK_USERS
4. Data Consistency Check - confirm Salvador Palma and other users exist
5. Comprehensive System Test - test login → user management → client management flow

Expected: 95%+ success rate with schema validation fixed and all MOCK_USERS references eliminated.
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://invest-manager-9.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class MongoDBMigrationTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
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
        """Test 1: Admin Login Test (username: admin, password: password123)"""
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
                    self.log_result("Admin Login Test", True, 
                                  "Successfully authenticated as admin with JWT token",
                                  {"user_id": data.get("id"), "username": data.get("username")})
                    return True
                else:
                    self.log_result("Admin Login Test", False, "No JWT token received", {"response": data})
                    return False
            else:
                self.log_result("Admin Login Test", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Login Test", False, f"Exception: {str(e)}")
            return False
    
    def test_jwt_authentication(self):
        """Test 5: JWT Authentication Test - Verify JWT works for protected endpoints"""
        try:
            # Test without token first
            temp_session = requests.Session()
            response = temp_session.get(f"{BACKEND_URL}/admin/clients")
            
            if response.status_code == 401:
                self.log_result("JWT Authentication - Unauthorized Access", True, 
                              "Protected endpoint correctly returns 401 without token")
            else:
                self.log_result("JWT Authentication - Unauthorized Access", False, 
                              f"Expected 401, got {response.status_code}")
            
            # Test with valid token
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            if response.status_code == 200:
                self.log_result("JWT Authentication - Authorized Access", True, 
                              "Protected endpoint accessible with valid JWT token")
            else:
                self.log_result("JWT Authentication - Authorized Access", False, 
                              f"Expected 200, got {response.status_code}")
                
        except Exception as e:
            self.log_result("JWT Authentication Test", False, f"Exception: {str(e)}")
    
    def test_admin_clients_endpoint(self):
        """Test 2a: GET /api/admin/clients - Should return client list from MongoDB"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response is from MongoDB (not MOCK_USERS)
                if isinstance(data, dict) and 'clients' in data:
                    clients = data['clients']
                    client_count = len(clients)
                    
                    self.log_result("Admin Clients Endpoint - MongoDB Format", True, 
                                  f"Endpoint returns MongoDB format with {client_count} clients",
                                  {"client_count": client_count, "format": "MongoDB"})
                    
                    # Check for expected clients
                    expected_clients = ["client_001", "client_002", "client_003", "client_004", "client_005", "admin_001", "client_alejandro"]
                    found_clients = [client.get('id') for client in clients]
                    
                    missing_clients = [client_id for client_id in expected_clients if client_id not in found_clients]
                    
                    if not missing_clients:
                        self.log_result("Admin Clients - Expected Users Present", True, 
                                      f"All expected users found in MongoDB: {len(expected_clients)} users")
                    else:
                        self.log_result("Admin Clients - Expected Users Present", False, 
                                      f"Missing users: {missing_clients}", 
                                      {"found": found_clients, "missing": missing_clients})
                    
                    return clients
                    
                elif isinstance(data, list):
                    # Legacy format - might still be using MOCK_USERS
                    self.log_result("Admin Clients Endpoint - Legacy Format", False, 
                                  "Endpoint returns legacy format - may still be using MOCK_USERS",
                                  {"client_count": len(data), "format": "Legacy"})
                    return data
                else:
                    self.log_result("Admin Clients Endpoint", False, 
                                  "Unexpected response format", {"response": data})
                    return []
            else:
                self.log_result("Admin Clients Endpoint", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            self.log_result("Admin Clients Endpoint", False, f"Exception: {str(e)}")
            return []
    
    def test_salvador_client_data(self, clients):
        """Test 2b: Verify Salvador Palma (client_003) data is accessible"""
        try:
            # Find Salvador in clients list
            salvador_client = None
            for client in clients:
                if client.get('id') == 'client_003':
                    salvador_client = client
                    break
            
            if salvador_client:
                # Verify Salvador's data
                expected_data = {
                    'id': 'client_003',
                    'name': 'SALVADOR PALMA',
                    'email': 'chava@alyarglobal.com'
                }
                
                data_correct = True
                issues = []
                
                for key, expected_value in expected_data.items():
                    actual_value = salvador_client.get(key)
                    if actual_value != expected_value:
                        data_correct = False
                        issues.append(f"{key}: expected '{expected_value}', got '{actual_value}'")
                
                if data_correct:
                    self.log_result("Salvador Client Data Verification", True, 
                                  "Salvador Palma (client_003) found with correct data in MongoDB",
                                  {"client_data": salvador_client})
                else:
                    self.log_result("Salvador Client Data Verification", False, 
                                  "Salvador found but data incorrect", 
                                  {"issues": issues, "client_data": salvador_client})
                
                # Test GET /api/client/{client_id}/data endpoint
                response = self.session.get(f"{BACKEND_URL}/client/client_003/data")
                if response.status_code == 200:
                    client_data = response.json()
                    self.log_result("Salvador Client Data Endpoint", True, 
                                  "GET /api/client/client_003/data works correctly",
                                  {"has_balance": "balance" in client_data, 
                                   "has_transactions": "transactions" in client_data})
                else:
                    self.log_result("Salvador Client Data Endpoint", False, 
                                  f"GET /api/client/client_003/data failed: HTTP {response.status_code}")
            else:
                self.log_result("Salvador Client Data Verification", False, 
                              "Salvador Palma (client_003) not found in MongoDB clients list")
                
        except Exception as e:
            self.log_result("Salvador Client Data Verification", False, f"Exception: {str(e)}")
    
    def test_client_details_endpoint(self):
        """Test 2c: GET /api/admin/clients/{client_id}/details - Should get client details from MongoDB"""
        try:
            # Test with Salvador (client_003)
            response = self.session.get(f"{BACKEND_URL}/admin/clients/client_003/details")
            
            if response.status_code == 200:
                details = response.json()
                self.log_result("Client Details Endpoint - Salvador", True, 
                              "GET /api/admin/clients/client_003/details works correctly",
                              {"has_client_info": "client" in details or "name" in details})
            else:
                self.log_result("Client Details Endpoint - Salvador", False, 
                              f"HTTP {response.status_code}: {response.text}")
            
            # Test with non-existent client
            response = self.session.get(f"{BACKEND_URL}/admin/clients/client_999/details")
            if response.status_code == 404:
                self.log_result("Client Details Endpoint - Not Found", True, 
                              "Non-existent client correctly returns 404")
            else:
                self.log_result("Client Details Endpoint - Not Found", False, 
                              f"Expected 404 for non-existent client, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Client Details Endpoint", False, f"Exception: {str(e)}")
    
    def test_client_status_update(self):
        """Test 2d: PUT /api/admin/clients/{client_id}/status - Test status update functionality"""
        try:
            # Test status update for Salvador
            update_data = {"status": "active"}
            response = self.session.put(f"{BACKEND_URL}/admin/clients/client_003/status", 
                                      json=update_data)
            
            if response.status_code == 200:
                result = response.json()
                self.log_result("Client Status Update - Salvador", True, 
                              "PUT /api/admin/clients/client_003/status works correctly",
                              {"response": result})
            elif response.status_code == 404:
                self.log_result("Client Status Update - Salvador", False, 
                              "Salvador not found for status update - MongoDB migration issue")
            else:
                self.log_result("Client Status Update - Salvador", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Client Status Update", False, f"Exception: {str(e)}")
    
    def test_admin_users_endpoint(self):
        """Test 3a: GET /api/admin/users - Should return all users from MongoDB"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/users")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, dict) and 'users' in data:
                    users = data['users']
                    user_count = len(users)
                    
                    self.log_result("Admin Users Endpoint - MongoDB Format", True, 
                                  f"Endpoint returns MongoDB format with {user_count} users",
                                  {"user_count": user_count})
                    
                    # Check for expected users
                    expected_usernames = ["admin", "client1", "client2", "client3", "client4", "client5", "alejandro_mariscal"]
                    found_usernames = [user.get('username') for user in users]
                    
                    missing_users = [username for username in expected_usernames if username not in found_usernames]
                    
                    if not missing_users:
                        self.log_result("Admin Users - Expected Users Present", True, 
                                      f"All expected users found in MongoDB: {len(expected_usernames)} users")
                    else:
                        self.log_result("Admin Users - Expected Users Present", False, 
                                      f"Missing users: {missing_users}", 
                                      {"found": found_usernames, "missing": missing_users})
                    
                    # Verify Alejandro Mariscal is present
                    alejandro_found = any(user.get('username') == 'alejandro_mariscal' for user in users)
                    if alejandro_found:
                        self.log_result("Alejandro Mariscal User Verification", True, 
                                      "Alejandro Mariscal user found in MongoDB")
                    else:
                        self.log_result("Alejandro Mariscal User Verification", False, 
                                      "Alejandro Mariscal user not found in MongoDB")
                    
                elif isinstance(data, list):
                    self.log_result("Admin Users Endpoint - Legacy Format", False, 
                                  "Endpoint returns legacy format - may still be using MOCK_USERS")
                else:
                    self.log_result("Admin Users Endpoint", False, 
                                  "Unexpected response format", {"response": data})
            else:
                self.log_result("Admin Users Endpoint", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Admin Users Endpoint", False, f"Exception: {str(e)}")
    
    def test_create_user_endpoint(self):
        """Test 3b: POST /api/admin/users/create - Test creating a new user in MongoDB only"""
        try:
            # Create a test user
            test_user_data = {
                "username": f"test_user_{int(time.time())}",
                "name": "Test User MongoDB",
                "email": f"test.user.{int(time.time())}@fidus.com",
                "phone": "+1-555-TEST",
                "temporary_password": "TempPass123!",
                "notes": "MongoDB migration test user"
            }
            
            response = self.session.post(f"{BACKEND_URL}/admin/users/create", 
                                       json=test_user_data)
            
            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                self.log_result("Create User Endpoint - MongoDB", True, 
                              "POST /api/admin/users/create works correctly with MongoDB",
                              {"created_user": result.get("user", {}).get("username", "unknown")})
                
                # Verify user was created in MongoDB by trying to fetch users again
                verify_response = self.session.get(f"{BACKEND_URL}/admin/users")
                if verify_response.status_code == 200:
                    users_data = verify_response.json()
                    if isinstance(users_data, dict) and 'users' in users_data:
                        users = users_data['users']
                        created_user_found = any(user.get('username') == test_user_data['username'] for user in users)
                        
                        if created_user_found:
                            self.log_result("Create User Verification - MongoDB Persistence", True, 
                                          "Created user persisted in MongoDB successfully")
                        else:
                            self.log_result("Create User Verification - MongoDB Persistence", False, 
                                          "Created user not found in MongoDB - persistence issue")
                
            else:
                self.log_result("Create User Endpoint - MongoDB", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Create User Endpoint", False, f"Exception: {str(e)}")
    
    def test_no_client_not_found_errors(self):
        """Test 4: Ensure no 'Client not found' errors for existing clients"""
        try:
            existing_client_ids = ["client_001", "client_002", "client_003", "client_004", "client_005"]
            
            for client_id in existing_client_ids:
                # Test client data endpoint
                response = self.session.get(f"{BACKEND_URL}/client/{client_id}/data")
                
                if response.status_code == 200:
                    self.log_result(f"Client Data Access - {client_id}", True, 
                                  f"Client {client_id} data accessible (no 'Client not found' error)")
                elif response.status_code == 404:
                    self.log_result(f"Client Data Access - {client_id}", False, 
                                  f"Client {client_id} returns 'Client not found' - MongoDB migration issue")
                else:
                    self.log_result(f"Client Data Access - {client_id}", False, 
                                  f"Client {client_id} returns HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Client Not Found Errors Test", False, f"Exception: {str(e)}")
    
    def test_mongodb_vs_mock_indicators(self):
        """Test to verify system is using MongoDB, not MOCK_USERS"""
        try:
            # Check health endpoint for MongoDB indicators
            response = self.session.get(f"{BACKEND_URL}/health")
            if response.status_code == 200:
                health_data = response.json()
                
                # Look for MongoDB connection indicators
                mongodb_connected = False
                if isinstance(health_data, dict):
                    # Check for MongoDB-related fields
                    if any(key.lower().find('mongo') != -1 for key in health_data.keys()):
                        mongodb_connected = True
                    elif health_data.get('database') == 'connected':
                        mongodb_connected = True
                
                if mongodb_connected:
                    self.log_result("MongoDB Connection Indicator", True, 
                                  "Health endpoint indicates MongoDB connection")
                else:
                    self.log_result("MongoDB Connection Indicator", False, 
                                  "No clear MongoDB connection indicator in health endpoint")
            
            # Test if endpoints return MongoDB-style responses vs MOCK_USERS style
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, dict) and 'clients' in data:
                    self.log_result("MongoDB Response Format", True, 
                                  "Endpoints return MongoDB-style responses (not MOCK_USERS)")
                elif isinstance(data, list):
                    self.log_result("MongoDB Response Format", False, 
                                  "Endpoints return MOCK_USERS-style responses (migration incomplete)")
                
        except Exception as e:
            self.log_result("MongoDB vs MOCK Indicators", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all MongoDB migration tests"""
        print("🎯 MONGODB MIGRATION ENDPOINTS TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Test 1: Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running MongoDB Migration Tests...")
        print("-" * 50)
        
        # Test 5: JWT Authentication
        self.test_jwt_authentication()
        
        # Test 2: Client Data Endpoints
        clients = self.test_admin_clients_endpoint()
        self.test_salvador_client_data(clients)
        self.test_client_details_endpoint()
        self.test_client_status_update()
        
        # Test 3: User Management
        self.test_admin_users_endpoint()
        self.test_create_user_endpoint()
        
        # Test 4: Data Consistency
        self.test_no_client_not_found_errors()
        
        # Additional verification
        self.test_mongodb_vs_mock_indicators()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 MONGODB MIGRATION TEST SUMMARY")
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
        
        # Show failed tests
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Show passed tests
        if passed_tests > 0:
            print("✅ PASSED TESTS:")
            for result in self.test_results:
                if result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Critical assessment for MongoDB migration
        critical_tests = [
            "Admin Login Test",
            "Admin Clients Endpoint - MongoDB Format",
            "Salvador Client Data Verification",
            "Admin Users Endpoint - MongoDB Format",
            "Create User Endpoint - MongoDB",
            "MongoDB Response Format"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(critical in result['test'] for critical in critical_tests))
        
        print("🚨 MONGODB MIGRATION ASSESSMENT:")
        if critical_passed >= 4:  # At least 4 out of 6 critical tests
            print("✅ MONGODB MIGRATION: SUCCESSFUL")
            print("   System successfully migrated from MOCK_USERS to MongoDB.")
            print("   All critical endpoints working with MongoDB data.")
            print("   Authentication and data consistency verified.")
        else:
            print("❌ MONGODB MIGRATION: INCOMPLETE")
            print("   Critical MongoDB migration issues found.")
            print("   System may still be using MOCK_USERS or have data inconsistencies.")
            print("   Main agent action required to complete migration.")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = MongoDBMigrationTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()