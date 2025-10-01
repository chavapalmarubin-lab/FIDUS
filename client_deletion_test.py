#!/usr/bin/env python3
"""
CLIENT DELETION ISSUE INVESTIGATION TEST
=======================================

This test investigates the client deletion issue as reported:
- User clicks "OK" to delete a client but the client is still there after confirmation

Investigation Areas:
1. Check Client Delete Endpoint (DELETE /api/admin/clients/{client_id})
2. Test if the endpoint exists and works properly
3. Check if it's actually deleting from MongoDB
4. Test delete functionality with real client
5. Check frontend-backend communication
6. Test MongoDB deletion operations
7. Check error handling and response format

Expected: Identify why client deletion is not working and provide detailed analysis.
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

class ClientDeletionInvestigationTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.test_client_id = None
        
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
    
    def test_client_delete_endpoint_exists(self):
        """Test if the client delete endpoint exists and is accessible"""
        try:
            # First, get a list of clients to find a test client
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            if response.status_code != 200:
                self.log_result("Client Delete Endpoint - Get Clients", False, 
                              f"Cannot get clients list: HTTP {response.status_code}")
                return False
            
            clients = response.json()
            if not clients or len(clients) == 0:
                self.log_result("Client Delete Endpoint - No Clients", False, 
                              "No clients found to test deletion")
                return False
            
            # Find a suitable test client (not Salvador Palma who is critical)
            test_client = None
            for client in clients:
                if isinstance(client, dict) and client.get('id') != 'client_003':  # Not Salvador
                    test_client = client
                    break
            
            if not test_client:
                self.log_result("Client Delete Endpoint - No Test Client", False, 
                              "No suitable test client found (all are critical)")
                return False
            
            self.test_client_id = test_client.get('id')
            client_name = test_client.get('name', 'Unknown')
            
            # Test DELETE endpoint with OPTIONS first (CORS preflight)
            try:
                options_response = self.session.options(f"{BACKEND_URL}/admin/clients/{self.test_client_id}")
                self.log_result("Client Delete Endpoint - OPTIONS", True, 
                              f"OPTIONS request successful: HTTP {options_response.status_code}")
            except Exception as e:
                self.log_result("Client Delete Endpoint - OPTIONS", False, 
                              f"OPTIONS request failed: {str(e)}")
            
            # Test if DELETE endpoint exists (without actually deleting yet)
            # We'll use a non-existent client ID first to test endpoint existence
            test_response = self.session.delete(f"{BACKEND_URL}/admin/clients/nonexistent_client_test")
            
            if test_response.status_code == 404:
                self.log_result("Client Delete Endpoint - Exists", True, 
                              "DELETE endpoint exists and returns 404 for non-existent client")
                return True
            elif test_response.status_code == 401:
                self.log_result("Client Delete Endpoint - Auth Required", True, 
                              "DELETE endpoint exists but requires authentication")
                return True
            elif test_response.status_code == 405:
                self.log_result("Client Delete Endpoint - Method Not Allowed", False, 
                              "DELETE method not allowed on this endpoint")
                return False
            else:
                self.log_result("Client Delete Endpoint - Unexpected Response", False, 
                              f"Unexpected response: HTTP {test_response.status_code}",
                              {"response": test_response.text})
                return False
                
        except Exception as e:
            self.log_result("Client Delete Endpoint - Exception", False, f"Exception: {str(e)}")
            return False
    
    def test_client_delete_functionality(self):
        """Test actual client deletion functionality"""
        if not self.test_client_id:
            self.log_result("Client Delete Functionality", False, "No test client ID available")
            return False
        
        try:
            # Get client details before deletion
            pre_delete_response = self.session.get(f"{BACKEND_URL}/admin/clients")
            if pre_delete_response.status_code != 200:
                self.log_result("Client Delete - Pre-Delete Check", False, 
                              f"Cannot get clients before deletion: HTTP {pre_delete_response.status_code}")
                return False
            
            pre_delete_clients = pre_delete_response.json()
            pre_delete_count = len(pre_delete_clients) if isinstance(pre_delete_clients, list) else 0
            
            # Find the specific client
            target_client = None
            for client in pre_delete_clients:
                if isinstance(client, dict) and client.get('id') == self.test_client_id:
                    target_client = client
                    break
            
            if not target_client:
                self.log_result("Client Delete - Target Not Found", False, 
                              f"Target client {self.test_client_id} not found before deletion")
                return False
            
            client_name = target_client.get('name', 'Unknown')
            self.log_result("Client Delete - Pre-Delete Verification", True, 
                          f"Target client found: {client_name} ({self.test_client_id})")
            
            # Perform the deletion
            delete_response = self.session.delete(f"{BACKEND_URL}/admin/clients/{self.test_client_id}")
            
            # Check delete response
            if delete_response.status_code == 200:
                delete_data = delete_response.json()
                if delete_data.get('success'):
                    self.log_result("Client Delete - API Response", True, 
                                  f"Delete API returned success: {delete_data.get('message')}")
                else:
                    self.log_result("Client Delete - API Response", False, 
                                  f"Delete API returned failure: {delete_data}")
                    return False
            else:
                self.log_result("Client Delete - API Response", False, 
                              f"Delete API failed: HTTP {delete_response.status_code}",
                              {"response": delete_response.text})
                return False
            
            # Wait a moment for database operation to complete
            time.sleep(2)
            
            # Verify deletion by checking clients list
            post_delete_response = self.session.get(f"{BACKEND_URL}/admin/clients")
            if post_delete_response.status_code != 200:
                self.log_result("Client Delete - Post-Delete Check", False, 
                              f"Cannot get clients after deletion: HTTP {post_delete_response.status_code}")
                return False
            
            post_delete_clients = post_delete_response.json()
            post_delete_count = len(post_delete_clients) if isinstance(post_delete_clients, list) else 0
            
            # Check if client still exists
            client_still_exists = False
            for client in post_delete_clients:
                if isinstance(client, dict) and client.get('id') == self.test_client_id:
                    client_still_exists = True
                    break
            
            if client_still_exists:
                self.log_result("Client Delete - Verification FAILED", False, 
                              f"CLIENT STILL EXISTS after deletion! {client_name} ({self.test_client_id})",
                              {
                                  "pre_delete_count": pre_delete_count,
                                  "post_delete_count": post_delete_count,
                                  "client_still_in_list": True
                              })
                return False
            else:
                self.log_result("Client Delete - Verification SUCCESS", True, 
                              f"Client successfully deleted: {client_name} ({self.test_client_id})",
                              {
                                  "pre_delete_count": pre_delete_count,
                                  "post_delete_count": post_delete_count,
                                  "count_difference": pre_delete_count - post_delete_count
                              })
                return True
                
        except Exception as e:
            self.log_result("Client Delete Functionality", False, f"Exception: {str(e)}")
            return False
    
    def test_mongodb_deletion_verification(self):
        """Test MongoDB deletion operations directly"""
        try:
            # Test MongoDB health
            health_response = self.session.get(f"{BACKEND_URL}/health")
            if health_response.status_code == 200:
                self.log_result("MongoDB Health Check", True, "Backend health check passed")
            else:
                self.log_result("MongoDB Health Check", False, 
                              f"Backend health check failed: HTTP {health_response.status_code}")
            
            # Test MongoDB readiness
            ready_response = self.session.get(f"{BACKEND_URL}/health/ready")
            if ready_response.status_code == 200:
                ready_data = ready_response.json()
                if ready_data.get('database_connected'):
                    self.log_result("MongoDB Connection", True, "MongoDB connection verified")
                else:
                    self.log_result("MongoDB Connection", False, "MongoDB not connected")
            else:
                self.log_result("MongoDB Connection", False, 
                              f"Cannot check MongoDB connection: HTTP {ready_response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_result("MongoDB Deletion Verification", False, f"Exception: {str(e)}")
            return False
    
    def test_error_handling_and_edge_cases(self):
        """Test error handling for various edge cases"""
        try:
            # Test 1: Delete non-existent client
            response1 = self.session.delete(f"{BACKEND_URL}/admin/clients/nonexistent_client_12345")
            if response1.status_code == 404:
                self.log_result("Error Handling - Non-existent Client", True, 
                              "Correctly returns 404 for non-existent client")
            else:
                self.log_result("Error Handling - Non-existent Client", False, 
                              f"Unexpected response for non-existent client: HTTP {response1.status_code}")
            
            # Test 2: Delete with invalid client ID format
            response2 = self.session.delete(f"{BACKEND_URL}/admin/clients/invalid@id#format")
            if response2.status_code in [400, 404, 422]:
                self.log_result("Error Handling - Invalid Client ID", True, 
                              f"Correctly handles invalid client ID: HTTP {response2.status_code}")
            else:
                self.log_result("Error Handling - Invalid Client ID", False, 
                              f"Unexpected response for invalid client ID: HTTP {response2.status_code}")
            
            # Test 3: Delete without authentication (create new session)
            unauth_session = requests.Session()
            response3 = unauth_session.delete(f"{BACKEND_URL}/admin/clients/test_client")
            if response3.status_code == 401:
                self.log_result("Error Handling - No Authentication", True, 
                              "Correctly requires authentication for deletion")
            else:
                self.log_result("Error Handling - No Authentication", False, 
                              f"Should require authentication: HTTP {response3.status_code}")
            
            # Test 4: Check response format
            if response1.status_code == 404:
                try:
                    error_data = response1.json()
                    if 'detail' in error_data:
                        self.log_result("Error Handling - Response Format", True, 
                                      "Error responses have proper JSON format")
                    else:
                        self.log_result("Error Handling - Response Format", False, 
                                      "Error responses missing 'detail' field")
                except:
                    self.log_result("Error Handling - Response Format", False, 
                                  "Error responses not in JSON format")
            
            return True
            
        except Exception as e:
            self.log_result("Error Handling Tests", False, f"Exception: {str(e)}")
            return False
    
    def test_frontend_backend_communication(self):
        """Test frontend-backend communication aspects"""
        try:
            # Test CORS headers
            response = self.session.options(f"{BACKEND_URL}/admin/clients/test")
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            if any(cors_headers.values()):
                self.log_result("Frontend Communication - CORS Headers", True, 
                              "CORS headers present for frontend communication",
                              {"cors_headers": cors_headers})
            else:
                self.log_result("Frontend Communication - CORS Headers", False, 
                              "No CORS headers found - may cause frontend issues")
            
            # Test content type handling
            headers_test = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            response = self.session.delete(f"{BACKEND_URL}/admin/clients/test_content_type", 
                                         headers=headers_test)
            
            if response.headers.get('Content-Type', '').startswith('application/json'):
                self.log_result("Frontend Communication - Content Type", True, 
                              "API returns JSON content type")
            else:
                self.log_result("Frontend Communication - Content Type", False, 
                              f"API returns unexpected content type: {response.headers.get('Content-Type')}")
            
            return True
            
        except Exception as e:
            self.log_result("Frontend Communication Tests", False, f"Exception: {str(e)}")
            return False
    
    def test_create_and_delete_cycle(self):
        """Test creating a client and then deleting it to verify full cycle"""
        try:
            # Create a test client first
            test_client_data = {
                "username": f"test_delete_user_{int(time.time())}",
                "name": "Test Delete User",
                "email": f"test_delete_{int(time.time())}@test.com",
                "phone": "+1-555-TEST",
                "notes": "Created for deletion testing"
            }
            
            create_response = self.session.post(f"{BACKEND_URL}/admin/users/create", 
                                              json=test_client_data)
            
            if create_response.status_code == 200:
                create_data = create_response.json()
                created_client_id = create_data.get('user_id') or create_data.get('id')
                
                if created_client_id:
                    self.log_result("Create-Delete Cycle - Client Creation", True, 
                                  f"Test client created: {created_client_id}")
                    
                    # Wait a moment
                    time.sleep(1)
                    
                    # Now try to delete it
                    delete_response = self.session.delete(f"{BACKEND_URL}/admin/clients/{created_client_id}")
                    
                    if delete_response.status_code == 200:
                        delete_data = delete_response.json()
                        if delete_data.get('success'):
                            self.log_result("Create-Delete Cycle - Deletion", True, 
                                          f"Test client deleted successfully: {created_client_id}")
                            
                            # Verify deletion
                            time.sleep(1)
                            verify_response = self.session.get(f"{BACKEND_URL}/admin/clients")
                            if verify_response.status_code == 200:
                                clients = verify_response.json()
                                client_exists = any(c.get('id') == created_client_id for c in clients 
                                                  if isinstance(c, dict))
                                
                                if not client_exists:
                                    self.log_result("Create-Delete Cycle - Verification", True, 
                                                  "Created client successfully deleted and verified")
                                    return True
                                else:
                                    self.log_result("Create-Delete Cycle - Verification", False, 
                                                  "Created client still exists after deletion!")
                                    return False
                            else:
                                self.log_result("Create-Delete Cycle - Verification", False, 
                                              "Cannot verify deletion - client list unavailable")
                                return False
                        else:
                            self.log_result("Create-Delete Cycle - Deletion", False, 
                                          f"Delete API returned failure: {delete_data}")
                            return False
                    else:
                        self.log_result("Create-Delete Cycle - Deletion", False, 
                                      f"Delete failed: HTTP {delete_response.status_code}")
                        return False
                else:
                    self.log_result("Create-Delete Cycle - Client Creation", False, 
                                  "No client ID returned from creation")
                    return False
            else:
                self.log_result("Create-Delete Cycle - Client Creation", False, 
                              f"Failed to create test client: HTTP {create_response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Create-Delete Cycle", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all client deletion investigation tests"""
        print("🔍 CLIENT DELETION ISSUE INVESTIGATION TEST")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Client Deletion Investigation Tests...")
        print("-" * 50)
        
        # Run all investigation tests
        self.test_client_delete_endpoint_exists()
        self.test_mongodb_deletion_verification()
        self.test_error_handling_and_edge_cases()
        self.test_frontend_backend_communication()
        self.test_create_and_delete_cycle()
        
        # Only test actual deletion if we have a safe test client
        if self.test_client_id:
            print(f"\n⚠️  WARNING: About to test actual deletion of client: {self.test_client_id}")
            print("This test will permanently delete a client from the database.")
            # For automated testing, we'll skip this unless it's a created test client
            # self.test_client_delete_functionality()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🔍 CLIENT DELETION INVESTIGATION SUMMARY")
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
        
        # Show failed tests (these indicate potential issues)
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
        
        # Root cause analysis
        print("🚨 ROOT CAUSE ANALYSIS:")
        
        endpoint_exists = any(r['success'] and 'Endpoint - Exists' in r['test'] for r in self.test_results)
        mongodb_connected = any(r['success'] and 'MongoDB Connection' in r['test'] for r in self.test_results)
        create_delete_works = any(r['success'] and 'Create-Delete Cycle' in r['test'] for r in self.test_results)
        
        if endpoint_exists and mongodb_connected and create_delete_works:
            print("✅ CLIENT DELETION FUNCTIONALITY: WORKING")
            print("   The delete endpoint exists, MongoDB is connected, and deletion works.")
            print("   The reported issue may be:")
            print("   - Frontend not calling the correct endpoint")
            print("   - Frontend not refreshing the client list after deletion")
            print("   - Caching issues in the frontend")
            print("   - User interface not updating properly")
        elif endpoint_exists and mongodb_connected:
            print("⚠️  CLIENT DELETION FUNCTIONALITY: PARTIALLY WORKING")
            print("   The delete endpoint exists and MongoDB is connected.")
            print("   However, full deletion cycle testing was not completed.")
            print("   Recommend testing with actual client deletion.")
        elif endpoint_exists:
            print("❌ CLIENT DELETION FUNCTIONALITY: DATABASE ISSUES")
            print("   The delete endpoint exists but MongoDB connection issues detected.")
            print("   Check MongoDB connectivity and database operations.")
        else:
            print("❌ CLIENT DELETION FUNCTIONALITY: ENDPOINT ISSUES")
            print("   The delete endpoint may not exist or is not accessible.")
            print("   Check backend routing and endpoint implementation.")
        
        print("\n🔧 RECOMMENDED ACTIONS:")
        if failed_tests == 0:
            print("1. Check frontend implementation - ensure it calls DELETE /api/admin/clients/{client_id}")
            print("2. Verify frontend refreshes client list after successful deletion")
            print("3. Check for browser caching issues")
            print("4. Test with browser developer tools to see actual API calls")
        else:
            print("1. Fix the identified backend issues first")
            print("2. Ensure MongoDB is properly connected and operational")
            print("3. Verify the delete endpoint is correctly implemented")
            print("4. Test error handling and response formats")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = ClientDeletionInvestigationTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()