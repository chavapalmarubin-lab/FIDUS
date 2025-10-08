#!/usr/bin/env python3
"""
CLIENT UPDATE ENDPOINT TESTING
==============================

This test focuses specifically on the client update endpoint that's failing:
- PUT /api/clients/{client_id} - Update client information

Issue: Client update modal shows error "An error occurred while updating the client. Please try again."

Test Focus:
- Verify endpoint exists and is accessible
- Check if proper authentication is required
- Test with valid client ID and update data
- Verify response format and error handling
- Check for any backend validation issues

Authentication: Use admin credentials (admin/password123)
Test Data: Use existing clients like Alejandro Mariscal Romero or Lilian Limon Leite
Update Fields: name, email, phone, status, notes
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration - Use correct backend URL from frontend/.env
BACKEND_URL = "https://mt5-deploy-debug.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class ClientUpdateTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.existing_clients = []
        
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
    
    def get_existing_clients(self):
        """Get list of existing clients to test with"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.existing_clients = data
                    self.log_result("Get Existing Clients", True, f"Found {len(data)} clients", 
                                  {"client_count": len(data), "sample_clients": [c.get('name', 'Unknown') for c in data[:3]]})
                    return True
                elif isinstance(data, dict) and 'clients' in data:
                    self.existing_clients = data['clients']
                    self.log_result("Get Existing Clients", True, f"Found {len(data['clients'])} clients", 
                                  {"client_count": len(data['clients']), "sample_clients": [c.get('name', 'Unknown') for c in data['clients'][:3]]})
                    return True
                else:
                    self.log_result("Get Existing Clients", False, "Unexpected response format", {"response": data})
                    return False
            else:
                self.log_result("Get Existing Clients", False, f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Get Existing Clients", False, f"Exception: {str(e)}")
            return False
    
    def find_test_client(self, preferred_names=None):
        """Find a suitable client for testing"""
        if not self.existing_clients:
            return None
            
        preferred_names = preferred_names or ["Alejandro Mariscal Romero", "Lilian Limon Leite", "Salvador Palma"]
        
        # First try to find preferred clients
        for client in self.existing_clients:
            client_name = client.get('name', '')
            for preferred in preferred_names:
                if preferred.lower() in client_name.lower():
                    return client
        
        # If no preferred client found, use the first available client
        if self.existing_clients:
            return self.existing_clients[0]
            
        return None
    
    def test_client_update_endpoint_exists(self):
        """Test if the client update endpoint exists"""
        try:
            # Find a test client
            test_client = self.find_test_client()
            if not test_client:
                self.log_result("Client Update Endpoint Exists", False, "No test client available")
                return False
            
            client_id = test_client.get('id')
            if not client_id:
                self.log_result("Client Update Endpoint Exists", False, "Test client has no ID", {"client": test_client})
                return False
            
            # Test with minimal update data (just to check if endpoint exists)
            update_data = {
                "name": test_client.get('name', 'Test Client')  # Keep existing name
            }
            
            response = self.session.put(f"{BACKEND_URL}/clients/{client_id}", json=update_data)
            
            if response.status_code in [200, 400, 422]:  # 200=success, 400/422=validation errors (but endpoint exists)
                self.log_result("Client Update Endpoint Exists", True, 
                              f"Endpoint exists (HTTP {response.status_code})", 
                              {"client_id": client_id, "response_preview": response.text[:200]})
                return True
            elif response.status_code == 404:
                self.log_result("Client Update Endpoint Exists", False, 
                              "Endpoint not found (HTTP 404)", 
                              {"client_id": client_id, "response": response.text})
                return False
            elif response.status_code == 401:
                self.log_result("Client Update Endpoint Exists", False, 
                              "Authentication required (HTTP 401) - check admin token", 
                              {"client_id": client_id})
                return False
            else:
                self.log_result("Client Update Endpoint Exists", False, 
                              f"Unexpected HTTP {response.status_code}", 
                              {"client_id": client_id, "response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Client Update Endpoint Exists", False, f"Exception: {str(e)}")
            return False
    
    def test_client_update_authentication(self):
        """Test that client update endpoint requires authentication"""
        try:
            # Find a test client
            test_client = self.find_test_client()
            if not test_client:
                self.log_result("Client Update Authentication", False, "No test client available")
                return False
            
            client_id = test_client.get('id')
            
            # Create session without auth token
            unauth_session = requests.Session()
            
            update_data = {
                "name": "Test Update"
            }
            
            response = unauth_session.put(f"{BACKEND_URL}/clients/{client_id}", json=update_data)
            
            if response.status_code == 401:
                self.log_result("Client Update Authentication", True, 
                              "Endpoint properly requires authentication (HTTP 401)")
                return True
            else:
                self.log_result("Client Update Authentication", False, 
                              f"Endpoint not properly protected (HTTP {response.status_code})", 
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Client Update Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_client_update_with_valid_data(self):
        """Test client update with valid data"""
        try:
            # Find a test client
            test_client = self.find_test_client()
            if not test_client:
                self.log_result("Client Update Valid Data", False, "No test client available")
                return False
            
            client_id = test_client.get('id')
            original_name = test_client.get('name', 'Unknown')
            
            # Prepare update data with all fields mentioned in the issue
            update_data = {
                "name": f"{original_name} (Updated)",
                "email": test_client.get('email', 'test@example.com'),
                "phone": test_client.get('phone', '+1-555-0123'),
                "status": "active",
                "notes": f"Updated via test at {datetime.now().isoformat()}"
            }
            
            response = self.session.put(f"{BACKEND_URL}/clients/{client_id}", json=update_data)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.log_result("Client Update Valid Data", True, 
                                  "Successfully updated client with valid data", 
                                  {"client_id": client_id, "response": data})
                    
                    # Try to revert the name change
                    revert_data = {"name": original_name}
                    revert_response = self.session.put(f"{BACKEND_URL}/clients/{client_id}", json=revert_data)
                    if revert_response.status_code == 200:
                        print(f"   ✅ Reverted client name back to original: {original_name}")
                    
                    return True
                except json.JSONDecodeError:
                    self.log_result("Client Update Valid Data", False, 
                                  "Success response but invalid JSON", 
                                  {"client_id": client_id, "response_text": response.text})
                    return False
            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    self.log_result("Client Update Valid Data", False, 
                                  "Validation error with valid data", 
                                  {"client_id": client_id, "error": error_data})
                    return False
                except json.JSONDecodeError:
                    self.log_result("Client Update Valid Data", False, 
                                  f"HTTP 400 with non-JSON response", 
                                  {"client_id": client_id, "response_text": response.text})
                    return False
            elif response.status_code == 404:
                self.log_result("Client Update Valid Data", False, 
                              "Client not found", 
                              {"client_id": client_id})
                return False
            elif response.status_code == 500:
                self.log_result("Client Update Valid Data", False, 
                              "Internal server error", 
                              {"client_id": client_id, "response": response.text})
                return False
            else:
                self.log_result("Client Update Valid Data", False, 
                              f"Unexpected HTTP {response.status_code}", 
                              {"client_id": client_id, "response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Client Update Valid Data", False, f"Exception: {str(e)}")
            return False
    
    def test_client_update_with_invalid_data(self):
        """Test client update with invalid data to check validation"""
        try:
            # Find a test client
            test_client = self.find_test_client()
            if not test_client:
                self.log_result("Client Update Invalid Data", False, "No test client available")
                return False
            
            client_id = test_client.get('id')
            
            # Test with invalid email format
            invalid_data = {
                "name": "Test Client",
                "email": "invalid-email-format",  # Invalid email
                "phone": "invalid-phone",
                "status": "invalid-status"
            }
            
            response = self.session.put(f"{BACKEND_URL}/clients/{client_id}", json=invalid_data)
            
            if response.status_code == 400 or response.status_code == 422:
                try:
                    error_data = response.json()
                    self.log_result("Client Update Invalid Data", True, 
                                  "Properly validates invalid data", 
                                  {"client_id": client_id, "validation_errors": error_data})
                    return True
                except json.JSONDecodeError:
                    self.log_result("Client Update Invalid Data", True, 
                                  f"Properly rejects invalid data (HTTP {response.status_code})", 
                                  {"client_id": client_id, "response_text": response.text})
                    return True
            elif response.status_code == 200:
                self.log_result("Client Update Invalid Data", False, 
                              "Accepts invalid data without validation", 
                              {"client_id": client_id, "response": response.text})
                return False
            else:
                self.log_result("Client Update Invalid Data", False, 
                              f"Unexpected response to invalid data (HTTP {response.status_code})", 
                              {"client_id": client_id, "response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Client Update Invalid Data", False, f"Exception: {str(e)}")
            return False
    
    def test_client_update_with_nonexistent_id(self):
        """Test client update with non-existent client ID"""
        try:
            fake_client_id = "nonexistent_client_12345"
            
            update_data = {
                "name": "Test Client",
                "email": "test@example.com"
            }
            
            response = self.session.put(f"{BACKEND_URL}/clients/{fake_client_id}", json=update_data)
            
            if response.status_code == 404:
                self.log_result("Client Update Nonexistent ID", True, 
                              "Properly returns 404 for non-existent client", 
                              {"fake_id": fake_client_id})
                return True
            else:
                self.log_result("Client Update Nonexistent ID", False, 
                              f"Unexpected response for non-existent client (HTTP {response.status_code})", 
                              {"fake_id": fake_client_id, "response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Client Update Nonexistent ID", False, f"Exception: {str(e)}")
            return False
    
    def test_client_update_partial_data(self):
        """Test client update with partial data (only some fields)"""
        try:
            # Find a test client
            test_client = self.find_test_client()
            if not test_client:
                self.log_result("Client Update Partial Data", False, "No test client available")
                return False
            
            client_id = test_client.get('id')
            original_name = test_client.get('name', 'Unknown')
            
            # Update only the notes field
            partial_data = {
                "notes": f"Partial update test at {datetime.now().isoformat()}"
            }
            
            response = self.session.put(f"{BACKEND_URL}/clients/{client_id}", json=partial_data)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.log_result("Client Update Partial Data", True, 
                                  "Successfully updated client with partial data", 
                                  {"client_id": client_id, "updated_fields": list(partial_data.keys())})
                    return True
                except json.JSONDecodeError:
                    self.log_result("Client Update Partial Data", False, 
                                  "Success response but invalid JSON", 
                                  {"client_id": client_id, "response_text": response.text})
                    return False
            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    # Check if it's requiring all fields
                    if "required" in str(error_data).lower():
                        self.log_result("Client Update Partial Data", False, 
                                      "Endpoint requires all fields (doesn't support partial updates)", 
                                      {"client_id": client_id, "error": error_data})
                    else:
                        self.log_result("Client Update Partial Data", False, 
                                      "Validation error with partial data", 
                                      {"client_id": client_id, "error": error_data})
                    return False
                except json.JSONDecodeError:
                    self.log_result("Client Update Partial Data", False, 
                                  "HTTP 400 with non-JSON response", 
                                  {"client_id": client_id, "response_text": response.text})
                    return False
            else:
                self.log_result("Client Update Partial Data", False, 
                              f"Unexpected HTTP {response.status_code}", 
                              {"client_id": client_id, "response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Client Update Partial Data", False, f"Exception: {str(e)}")
            return False
    
    def test_specific_clients_mentioned_in_issue(self):
        """Test update specifically with clients mentioned in the issue"""
        try:
            target_clients = ["Alejandro Mariscal Romero", "Lilian Limon Leite"]
            found_clients = []
            
            for client in self.existing_clients:
                client_name = client.get('name', '')
                for target in target_clients:
                    if target.lower() in client_name.lower():
                        found_clients.append((target, client))
                        break
            
            if not found_clients:
                self.log_result("Specific Clients Update", False, 
                              "Neither Alejandro Mariscal Romero nor Lilian Limon Leite found in client list", 
                              {"available_clients": [c.get('name') for c in self.existing_clients[:5]]})
                return False
            
            success_count = 0
            total_tests = len(found_clients)
            
            for target_name, client in found_clients:
                client_id = client.get('id')
                client_name = client.get('name')
                
                # Test update with the specific client
                update_data = {
                    "name": client_name,  # Keep same name
                    "email": client.get('email', 'test@example.com'),
                    "phone": client.get('phone', '+1-555-0123'),
                    "status": "active",
                    "notes": f"Test update for {target_name} at {datetime.now().isoformat()}"
                }
                
                response = self.session.put(f"{BACKEND_URL}/clients/{client_id}", json=update_data)
                
                if response.status_code == 200:
                    success_count += 1
                    print(f"   ✅ Successfully updated {target_name} (ID: {client_id})")
                else:
                    print(f"   ❌ Failed to update {target_name} (ID: {client_id}): HTTP {response.status_code}")
                    print(f"      Response: {response.text[:200]}")
            
            if success_count == total_tests:
                self.log_result("Specific Clients Update", True, 
                              f"Successfully updated all {total_tests} target clients", 
                              {"updated_clients": [name for name, _ in found_clients]})
                return True
            elif success_count > 0:
                self.log_result("Specific Clients Update", False, 
                              f"Partially successful: {success_count}/{total_tests} clients updated", 
                              {"successful": success_count, "total": total_tests})
                return False
            else:
                self.log_result("Specific Clients Update", False, 
                              f"Failed to update any of the {total_tests} target clients")
                return False
                
        except Exception as e:
            self.log_result("Specific Clients Update", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all client update tests"""
        print("🎯 CLIENT UPDATE ENDPOINT TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate as admin
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        # Get existing clients
        if not self.get_existing_clients():
            print("❌ CRITICAL: Could not retrieve existing clients. Cannot proceed with tests.")
            return False
        
        print(f"\n🔍 Running Client Update Tests with {len(self.existing_clients)} available clients...")
        print("-" * 50)
        
        # Run all tests
        self.test_client_update_endpoint_exists()
        self.test_client_update_authentication()
        self.test_client_update_with_valid_data()
        self.test_client_update_with_invalid_data()
        self.test_client_update_with_nonexistent_id()
        self.test_client_update_partial_data()
        self.test_specific_clients_mentioned_in_issue()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 CLIENT UPDATE ENDPOINT TEST SUMMARY")
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
        
        # Show failed tests first (most important)
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
                    if result.get('details'):
                        for key, value in result['details'].items():
                            if key in ['error', 'validation_errors', 'response']:
                                print(f"     - {key}: {str(value)[:100]}...")
            print()
        
        # Show passed tests
        if passed_tests > 0:
            print("✅ PASSED TESTS:")
            for result in self.test_results:
                if result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Critical assessment for client update functionality
        critical_tests = [
            "Client Update Endpoint Exists",
            "Client Update Valid Data",
            "Specific Clients Update"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(critical in result['test'] for critical in critical_tests))
        
        print("🚨 CRITICAL ASSESSMENT:")
        if critical_passed >= 2:  # At least 2 out of 3 critical tests
            print("✅ CLIENT UPDATE FUNCTIONALITY: WORKING")
            print("   Client update endpoint is accessible and functional.")
            print("   The reported issue may be frontend-related or data-specific.")
        else:
            print("❌ CLIENT UPDATE FUNCTIONALITY: BROKEN")
            print("   Critical client update issues confirmed.")
            print("   This matches the user's reported problem.")
            print("   Main agent action required to fix backend implementation.")
        
        # Specific recommendations based on test results
        print("\n🔧 RECOMMENDATIONS:")
        
        endpoint_exists = any(r['success'] and 'Endpoint Exists' in r['test'] for r in self.test_results)
        valid_data_works = any(r['success'] and 'Valid Data' in r['test'] for r in self.test_results)
        auth_works = any(r['success'] and 'Authentication' in r['test'] for r in self.test_results)
        
        if not endpoint_exists:
            print("   1. ❌ CRITICAL: Client update endpoint (PUT /api/clients/{id}) is missing or not accessible")
            print("      - Check if the endpoint is properly defined in server.py")
            print("      - Verify the route is registered with the API router")
        
        if not auth_works:
            print("   2. ❌ CRITICAL: Authentication issues with client update endpoint")
            print("      - Check JWT token validation in the endpoint")
            print("      - Verify admin permissions are properly checked")
        
        if not valid_data_works:
            print("   3. ❌ CRITICAL: Client update fails even with valid data")
            print("      - Check database connection and MongoDB operations")
            print("      - Verify client update logic in the backend")
            print("      - Check for validation schema issues")
        
        if endpoint_exists and auth_works and not valid_data_works:
            print("   4. 🔍 LIKELY ISSUE: Backend validation or database operation problems")
            print("      - Check MongoDB client update queries")
            print("      - Verify field validation logic")
            print("      - Check for any missing required fields")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = ClientUpdateTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()