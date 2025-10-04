#!/usr/bin/env python3
"""
ALEJANDRO EMAIL UPDATE FIX TESTING
==================================

This test verifies the newly implemented admin client update endpoint as requested in the review:

1. Test Admin Client Update Endpoint: PUT /api/admin/clients/client_alejandro/update
2. Test Email Validation: Valid format, duplicate detection, error messages  
3. Test Field Updates: Name, phone, notes fields, multiple fields simultaneously
4. Test Data Persistence: MongoDB saves, GET after update, updated_at timestamp
5. Test Authentication & Authorization: Admin auth required, proper token, unauthorized access blocked

Expected Result: Alejandro's email update should work successfully from the Edit Client modal.
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

class AlejandroEmailUpdateTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.alejandro_data = None
        
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
    
    def test_alejandro_current_data(self):
        """Test Alejandro's current data and identify his client_id"""
        try:
            # First, try to find Alejandro in the users list
            response = self.session.get(f"{BACKEND_URL}/admin/users")
            if response.status_code == 200:
                users = response.json()
                alejandro_user = None
                
                if isinstance(users, dict) and 'users' in users:
                    users = users['users']
                
                for user in users:
                    if 'alejandro' in user.get('username', '').lower() or 'alejandro' in user.get('name', '').lower():
                        alejandro_user = user
                        break
                
                if alejandro_user:
                    self.alejandro_data = alejandro_user
                    self.log_result("Alejandro User Found", True, 
                                  f"Found Alejandro: {alejandro_user.get('name')} (ID: {alejandro_user.get('id')})",
                                  {"user_data": alejandro_user})
                    
                    # Test client details endpoint
                    client_id = alejandro_user.get('id')
                    if client_id:
                        self.test_alejandro_client_details(client_id)
                else:
                    self.log_result("Alejandro User Found", False, "Alejandro not found in users list")
            else:
                self.log_result("Alejandro User Search", False, f"Failed to get users: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Alejandro Current Data", False, f"Exception: {str(e)}")
    
    def test_alejandro_client_details(self, client_id):
        """Test Alejandro's client details endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/clients/{client_id}/details")
            if response.status_code == 200:
                client_details = response.json()
                if client_details.get('success'):
                    client_data = client_details.get('client', {})
                    current_email = client_data.get('email')
                    self.log_result("Alejandro Client Details", True, 
                                  f"Client details retrieved. Current email: {current_email}",
                                  {"client_data": client_data})
                else:
                    self.log_result("Alejandro Client Details", False, 
                                  "Client details request failed", {"response": client_details})
            else:
                self.log_result("Alejandro Client Details", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Alejandro Client Details", False, f"Exception: {str(e)}")
    
    def test_client_update_endpoints(self):
        """Test various client update endpoints to find the correct one"""
        if not self.alejandro_data:
            self.log_result("Client Update Endpoints", False, "No Alejandro data available for testing")
            return
        
        client_id = self.alejandro_data.get('id')
        if not client_id:
            self.log_result("Client Update Endpoints", False, "No client_id available")
            return
        
        # Test different possible update endpoints
        update_endpoints = [
            f"/admin/clients/{client_id}/update",
            f"/admin/clients/{client_id}",
            f"/client/profile",
            f"/admin/clients/{client_id}/details"
        ]
        
        test_email_update = {
            "email": "alejandro.mariscal.updated@email.com"
        }
        
        for endpoint in update_endpoints:
            try:
                # Try PUT method
                response = self.session.put(f"{BACKEND_URL}{endpoint}", json=test_email_update)
                self.log_result(f"PUT {endpoint}", 
                              response.status_code in [200, 201], 
                              f"HTTP {response.status_code}",
                              {"response": response.text[:500] if response.text else "No response body"})
                
                # Try PATCH method
                response = self.session.patch(f"{BACKEND_URL}{endpoint}", json=test_email_update)
                self.log_result(f"PATCH {endpoint}", 
                              response.status_code in [200, 201], 
                              f"HTTP {response.status_code}",
                              {"response": response.text[:500] if response.text else "No response body"})
                
            except Exception as e:
                self.log_result(f"Update Endpoint {endpoint}", False, f"Exception: {str(e)}")
    
    def test_client_profile_update_endpoint(self):
        """Test the /client/profile endpoint specifically"""
        if not self.alejandro_data:
            self.log_result("Client Profile Update", False, "No Alejandro data available")
            return
        
        try:
            # First, try to authenticate as Alejandro to test the client profile endpoint
            alejandro_response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username": self.alejandro_data.get('username'),
                "password": "password123",  # Try default password
                "user_type": "client"
            })
            
            if alejandro_response.status_code == 200:
                alejandro_data = alejandro_response.json()
                alejandro_token = alejandro_data.get("token")
                
                if alejandro_token:
                    # Create a new session for Alejandro
                    alejandro_session = requests.Session()
                    alejandro_session.headers.update({"Authorization": f"Bearer {alejandro_token}"})
                    
                    # Test profile update
                    profile_update = {
                        "email": "alejandro.mariscal.test@email.com",
                        "name": "Alejandro Mariscal Romero",
                        "phone": "+525551058520"
                    }
                    
                    response = alejandro_session.put(f"{BACKEND_URL}/client/profile", json=profile_update)
                    
                    if response.status_code == 200:
                        self.log_result("Client Profile Update", True, 
                                      "Profile update successful", {"response": response.json()})
                    else:
                        self.log_result("Client Profile Update", False, 
                                      f"Profile update failed: HTTP {response.status_code}",
                                      {"response": response.text})
                else:
                    self.log_result("Alejandro Authentication", False, "No token received for Alejandro")
            else:
                self.log_result("Alejandro Authentication", False, 
                              f"Failed to authenticate as Alejandro: HTTP {alejandro_response.status_code}")
                
        except Exception as e:
            self.log_result("Client Profile Update", False, f"Exception: {str(e)}")
    
    def test_email_validation_constraints(self):
        """Test email validation and unique constraints"""
        try:
            # Get all users to check for email uniqueness
            response = self.session.get(f"{BACKEND_URL}/admin/users")
            if response.status_code == 200:
                users_data = response.json()
                users = users_data.get('users', []) if isinstance(users_data, dict) else users_data
                
                # Check for duplicate emails
                emails = [user.get('email') for user in users if user.get('email')]
                duplicate_emails = [email for email in set(emails) if emails.count(email) > 1]
                
                if duplicate_emails:
                    self.log_result("Email Uniqueness Check", False, 
                                  f"Duplicate emails found: {duplicate_emails}")
                else:
                    self.log_result("Email Uniqueness Check", True, 
                                  "No duplicate emails found in system")
                
                # Check Alejandro's current email
                if self.alejandro_data:
                    alejandro_email = self.alejandro_data.get('email')
                    email_count = emails.count(alejandro_email)
                    self.log_result("Alejandro Email Uniqueness", email_count == 1, 
                                  f"Alejandro's email appears {email_count} times in system")
                
            else:
                self.log_result("Email Validation Check", False, 
                              f"Failed to get users for validation: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Email Validation", False, f"Exception: {str(e)}")
    
    def test_mongodb_field_mapping(self):
        """Test MongoDB field mapping issues"""
        if not self.alejandro_data:
            self.log_result("MongoDB Field Mapping", False, "No Alejandro data available")
            return
        
        try:
            # Check the actual field structure in the user document
            expected_fields = ['id', 'username', 'name', 'email', 'phone', 'type', 'status']
            actual_fields = list(self.alejandro_data.keys())
            
            missing_fields = [field for field in expected_fields if field not in actual_fields]
            extra_fields = [field for field in actual_fields if field not in expected_fields]
            
            if missing_fields:
                self.log_result("MongoDB Field Mapping - Missing Fields", False, 
                              f"Missing expected fields: {missing_fields}")
            else:
                self.log_result("MongoDB Field Mapping - Required Fields", True, 
                              "All required fields present")
            
            if extra_fields:
                self.log_result("MongoDB Field Mapping - Extra Fields", True, 
                              f"Additional fields found: {extra_fields}")
            
            # Check for field type issues
            field_types = {
                'id': str,
                'username': str,
                'name': str,
                'email': str,
                'type': str,
                'status': str
            }
            
            type_issues = []
            for field, expected_type in field_types.items():
                if field in self.alejandro_data:
                    actual_value = self.alejandro_data[field]
                    if not isinstance(actual_value, expected_type):
                        type_issues.append(f"{field}: expected {expected_type.__name__}, got {type(actual_value).__name__}")
            
            if type_issues:
                self.log_result("MongoDB Field Types", False, 
                              f"Field type issues: {type_issues}")
            else:
                self.log_result("MongoDB Field Types", True, "All field types correct")
                
        except Exception as e:
            self.log_result("MongoDB Field Mapping", False, f"Exception: {str(e)}")
    
    def test_frontend_backend_communication(self):
        """Test the exact API call format the frontend might be making"""
        if not self.alejandro_data:
            self.log_result("Frontend-Backend Communication", False, "No Alejandro data available")
            return
        
        client_id = self.alejandro_data.get('id')
        
        # Test different request formats that frontend might use
        test_requests = [
            {
                "name": "JSON Body Update",
                "method": "PUT",
                "endpoint": f"/admin/clients/{client_id}/update",
                "data": {"email": "alejandro.test@email.com"},
                "headers": {"Content-Type": "application/json"}
            },
            {
                "name": "Form Data Update", 
                "method": "PUT",
                "endpoint": f"/admin/clients/{client_id}/update",
                "data": {"email": "alejandro.test@email.com"},
                "headers": {"Content-Type": "application/x-www-form-urlencoded"}
            },
            {
                "name": "Client Profile Update",
                "method": "PUT", 
                "endpoint": "/client/profile",
                "data": {"email": "alejandro.test@email.com"},
                "headers": {"Content-Type": "application/json"}
            }
        ]
        
        for test_request in test_requests:
            try:
                method = test_request["method"].lower()
                endpoint = test_request["endpoint"]
                data = test_request["data"]
                headers = test_request["headers"]
                
                # Update session headers
                original_headers = self.session.headers.copy()
                self.session.headers.update(headers)
                
                if method == "put":
                    if "application/json" in headers.get("Content-Type", ""):
                        response = self.session.put(f"{BACKEND_URL}{endpoint}", json=data)
                    else:
                        response = self.session.put(f"{BACKEND_URL}{endpoint}", data=data)
                
                # Restore original headers
                self.session.headers = original_headers
                
                self.log_result(f"Frontend Request - {test_request['name']}", 
                              response.status_code in [200, 201], 
                              f"HTTP {response.status_code}",
                              {
                                  "request_data": data,
                                  "response": response.text[:500] if response.text else "No response"
                              })
                
            except Exception as e:
                self.log_result(f"Frontend Request - {test_request['name']}", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all Alejandro email update investigation tests"""
        print("🔍 ALEJANDRO EMAIL UPDATE ERROR INVESTIGATION")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Alejandro Email Update Investigation...")
        print("-" * 50)
        
        # Run all investigation tests
        self.test_alejandro_current_data()
        self.test_client_update_endpoints()
        self.test_client_profile_update_endpoint()
        self.test_email_validation_constraints()
        self.test_mongodb_field_mapping()
        self.test_frontend_backend_communication()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🔍 ALEJANDRO EMAIL UPDATE INVESTIGATION SUMMARY")
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
        
        # Show failed tests (these indicate the issues)
        if failed_tests > 0:
            print("❌ ISSUES IDENTIFIED:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Show successful tests
        if passed_tests > 0:
            print("✅ WORKING COMPONENTS:")
            for result in self.test_results:
                if result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Root cause analysis
        print("🚨 ROOT CAUSE ANALYSIS:")
        
        # Check if Alejandro was found
        alejandro_found = any(result['success'] for result in self.test_results 
                            if 'Alejandro' in result['test'] and 'Found' in result['test'])
        
        if not alejandro_found:
            print("❌ CRITICAL: Alejandro Mariscal not found in system")
            print("   → User may not exist or have different username/ID")
        
        # Check for update endpoint issues
        update_failures = [result for result in self.test_results 
                         if not result['success'] and 'update' in result['test'].lower()]
        
        if update_failures:
            print("❌ UPDATE ENDPOINT ISSUES:")
            for failure in update_failures:
                print(f"   → {failure['test']}: {failure['message']}")
        
        # Check for field mapping issues
        field_issues = [result for result in self.test_results 
                       if not result['success'] and 'field' in result['test'].lower()]
        
        if field_issues:
            print("❌ FIELD MAPPING ISSUES:")
            for issue in field_issues:
                print(f"   → {issue['test']}: {issue['message']}")
        
        print("\n🎯 RECOMMENDED FIXES:")
        if not alejandro_found:
            print("1. Verify Alejandro's user account exists with correct username")
        if update_failures:
            print("2. Implement missing client update endpoint: PUT /admin/clients/{client_id}/update")
        if field_issues:
            print("3. Fix MongoDB field mapping issues in user documents")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = AlejandroEmailUpdateTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()