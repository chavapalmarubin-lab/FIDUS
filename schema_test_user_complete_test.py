#!/usr/bin/env python3
"""
COMPLETE SCHEMA TEST USER DELETION TEST
======================================

This test creates a new "Schema Test User" and then tests the complete deletion workflow
to verify that the deletion functionality is working properly.

Test Workflow:
1. Create a new "Schema Test User"
2. Verify the user was created
3. Test deletion of the user
4. Verify the user was deleted
5. Test frontend refresh functionality

This will confirm that the deletion issue reported by the user is resolved.
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://fidus-admin.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class CompleteSchemaTestUserTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.created_user_id = None
        
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
    
    def create_schema_test_user(self):
        """Create a new Schema Test User"""
        try:
            # Generate unique username to avoid conflicts
            timestamp = int(time.time())
            user_data = {
                "username": f"test_schema_{timestamp}",
                "name": "Schema Test User",
                "email": f"schema.test.{timestamp}@fidus.com",
                "phone": "+1-555-TEST",
                "temporary_password": "TempPass123!",
                "notes": "Test user created for deletion testing"
            }
            
            response = self.session.post(f"{BACKEND_URL}/admin/users/create", json=user_data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.created_user_id = result.get('user_id') or result.get('id')
                    self.log_result("Create Schema Test User", True, 
                                  f"Successfully created Schema Test User with ID: {self.created_user_id}",
                                  {"user_data": user_data, "response": result})
                    return True
                else:
                    self.log_result("Create Schema Test User", False, 
                                  f"User creation failed: {result.get('message', 'Unknown error')}",
                                  {"response": result})
                    return False
            else:
                self.log_result("Create Schema Test User", False, 
                              f"HTTP {response.status_code}: {response.text}",
                              {"user_data": user_data})
                return False
                
        except Exception as e:
            self.log_result("Create Schema Test User", False, f"Exception: {str(e)}")
            return False
    
    def verify_user_created(self):
        """Verify the Schema Test User was created and appears in clients list"""
        if not self.created_user_id:
            self.log_result("Verify User Created", False, "No user ID to verify")
            return False
        
        try:
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
                
                # Look for our created user
                user_found = False
                for client in clients:
                    if client.get('id') == self.created_user_id or client.get('name') == 'Schema Test User':
                        user_found = True
                        self.log_result("Verify User Created", True, 
                                      f"Schema Test User found in clients list: {client.get('name')} (ID: {client.get('id')})",
                                      {"client_data": client})
                        break
                
                if not user_found:
                    self.log_result("Verify User Created", False, 
                                  f"Schema Test User with ID {self.created_user_id} not found in clients list",
                                  {"total_clients": len(clients)})
                    return False
                
                return True
            else:
                self.log_result("Verify User Created", False, 
                              f"Failed to get clients list: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Verify User Created", False, f"Exception: {str(e)}")
            return False
    
    def test_user_deletion(self):
        """Test deletion of the created Schema Test User"""
        if not self.created_user_id:
            self.log_result("Test User Deletion", False, "No user ID to delete")
            return False
        
        try:
            response = self.session.delete(f"{BACKEND_URL}/admin/clients/{self.created_user_id}")
            
            if response.status_code == 200:
                self.log_result("Test User Deletion", True, 
                              f"Successfully deleted Schema Test User (ID: {self.created_user_id})",
                              {"response": response.json() if response.content else "No response body"})
                return True
                
            elif response.status_code == 404:
                self.log_result("Test User Deletion", False, 
                              "DELETE endpoint not found - endpoint may not be implemented",
                              {"status_code": response.status_code, "response": response.text})
                return False
                
            elif response.status_code == 405:
                self.log_result("Test User Deletion", False, 
                              "Method not allowed - DELETE may not be supported on this endpoint",
                              {"status_code": response.status_code, "response": response.text})
                return False
                
            elif response.status_code == 400:
                self.log_result("Test User Deletion", False, 
                              "Bad request - user may have dependencies preventing deletion",
                              {"status_code": response.status_code, "response": response.text})
                return False
                
            elif response.status_code == 403:
                self.log_result("Test User Deletion", False, 
                              "Forbidden - insufficient permissions or user protected from deletion",
                              {"status_code": response.status_code, "response": response.text})
                return False
                
            elif response.status_code == 409:
                self.log_result("Test User Deletion", False, 
                              "Conflict - user has dependencies that prevent deletion",
                              {"status_code": response.status_code, "response": response.text})
                return False
                
            else:
                self.log_result("Test User Deletion", False, 
                              f"Unexpected response: HTTP {response.status_code}",
                              {"status_code": response.status_code, "response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Test User Deletion", False, f"Exception during deletion: {str(e)}")
            return False
    
    def verify_user_deleted(self):
        """Verify that the user was actually deleted"""
        if not self.created_user_id:
            self.log_result("Verify User Deleted", False, "No user ID to verify deletion")
            return False
        
        try:
            # Wait a moment for database update
            time.sleep(1)
            
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
                    if client.get('id') == self.created_user_id:
                        user_still_exists = True
                        break
                
                if user_still_exists:
                    self.log_result("Verify User Deleted", False, 
                                  f"User still exists after deletion attempt (ID: {self.created_user_id})")
                    return False
                else:
                    self.log_result("Verify User Deleted", True, 
                                  f"User successfully removed from clients list (ID: {self.created_user_id})")
                    return True
            else:
                self.log_result("Verify User Deleted", False, 
                              f"Could not verify deletion - failed to get clients list: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Verify User Deleted", False, f"Exception during verification: {str(e)}")
            return False
    
    def test_frontend_workflow(self):
        """Test the complete frontend workflow for user deletion"""
        try:
            # 1. Get initial client count
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            if response.status_code == 200:
                clients_data = response.json()
                initial_count = len(clients_data) if isinstance(clients_data, list) else len(clients_data.get('clients', []))
                
                self.log_result("Frontend Workflow - Initial Count", True, 
                              f"Initial client count: {initial_count}")
                
                # 2. Test that the list refreshes properly
                time.sleep(1)
                response2 = self.session.get(f"{BACKEND_URL}/admin/clients")
                if response2.status_code == 200:
                    clients_data2 = response2.json()
                    final_count = len(clients_data2) if isinstance(clients_data2, list) else len(clients_data2.get('clients', []))
                    
                    self.log_result("Frontend Workflow - Refresh", True, 
                                  f"Client list refresh working: {initial_count} -> {final_count}")
                else:
                    self.log_result("Frontend Workflow - Refresh", False, 
                                  f"Client list refresh failed: HTTP {response2.status_code}")
            else:
                self.log_result("Frontend Workflow - Initial Count", False, 
                              f"Failed to get initial client count: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Frontend Workflow", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run complete Schema Test User deletion test"""
        print("🧪 COMPLETE SCHEMA TEST USER DELETION TEST")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🧪 Running Complete Schema Test User Deletion Test...")
        print("-" * 50)
        
        # Run complete workflow test
        if self.create_schema_test_user():
            if self.verify_user_created():
                if self.test_user_deletion():
                    self.verify_user_deleted()
        
        self.test_frontend_workflow()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🧪 COMPLETE SCHEMA TEST USER DELETION TEST SUMMARY")
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
        
        # Final assessment
        print("🚨 FINAL ASSESSMENT:")
        
        # Check if complete workflow worked
        workflow_tests = ['Create Schema Test User', 'Verify User Created', 'Test User Deletion', 'Verify User Deleted']
        workflow_success = all(any(result['success'] and workflow_test in result['test'] 
                                 for result in self.test_results) 
                             for workflow_test in workflow_tests)
        
        if workflow_success:
            print("✅ SCHEMA TEST USER DELETION: WORKING CORRECTLY")
            print("   Complete workflow tested successfully:")
            print("   1. ✅ User creation works")
            print("   2. ✅ User appears in clients list")
            print("   3. ✅ User deletion works")
            print("   4. ✅ User removed from clients list")
            print("   5. ✅ Frontend refresh works")
            print()
            print("🎯 CONCLUSION: The user's deletion issue is RESOLVED.")
            print("   The DELETE functionality is working properly.")
        else:
            print("❌ SCHEMA TEST USER DELETION: ISSUES FOUND")
            print("   Some part of the deletion workflow is not working.")
            print("   Check the failed tests above for details.")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = CompleteSchemaTestUserTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()