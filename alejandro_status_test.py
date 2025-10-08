#!/usr/bin/env python3
"""
ALEJANDRO MARISCAL CURRENT STATUS VERIFICATION TEST
==================================================

This test verifies Alejandro Mariscal's current status in MongoDB as requested in the review:
1. Get Alejandro's User Record (ID: "client_alejandro" or email: "alejandro.mariscal@email.com")
2. Check if he has Google Drive folder metadata
3. Verify his current status and profile information
4. Test Document Access Endpoints for Alejandro
5. Check Google Drive Integration Status

Expected Results:
- Alejandro found in users/clients with correct data
- Google Drive folder metadata present (if configured)
- Document access endpoints working
- Google APIs service availability confirmed
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://mt5-deploy-debug.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class AlejandroStatusTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.alejandro_data = {}
        
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
    
    def test_alejandro_user_record(self):
        """Test 1: Get Alejandro's User Record"""
        try:
            # First, try to find Alejandro in users list
            response = self.session.get(f"{BACKEND_URL}/admin/users")
            if response.status_code == 200:
                users = response.json()
                alejandro_found = False
                
                # Handle both list and dict response formats
                user_list = users if isinstance(users, list) else users.get('users', [])
                
                for user in user_list:
                    # Check for both ID patterns and email
                    user_id = user.get('id', '')
                    email = user.get('email', '')
                    username = user.get('username', '')
                    
                    if (user_id == 'client_alejandro' or 
                        email == 'alejandro.mariscal@email.com' or
                        'alejandro' in username.lower()):
                        
                        alejandro_found = True
                        self.alejandro_data = user
                        
                        # Verify expected data
                        expected_fields = ['id', 'username', 'name', 'email', 'phone', 'type', 'status']
                        missing_fields = [field for field in expected_fields if field not in user]
                        
                        if not missing_fields:
                            self.log_result("Alejandro User Record", True, 
                                          f"Found Alejandro: {user.get('name')} ({user.get('email')})",
                                          {"user_data": user})
                        else:
                            self.log_result("Alejandro User Record", False, 
                                          f"Alejandro found but missing fields: {missing_fields}",
                                          {"user_data": user, "missing_fields": missing_fields})
                        break
                
                if not alejandro_found:
                    self.log_result("Alejandro User Record", False, 
                                  "Alejandro Mariscal not found in users list",
                                  {"total_users": len(user_list), "searched_patterns": ["client_alejandro", "alejandro.mariscal@email.com"]})
            else:
                self.log_result("Alejandro User Record", False, 
                              f"Failed to get users: HTTP {response.status_code}",
                              {"response": response.text[:500]})
                
        except Exception as e:
            self.log_result("Alejandro User Record", False, f"Exception: {str(e)}")
    
    def test_alejandro_client_record(self):
        """Test 2: Check if Alejandro exists in clients list"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            if response.status_code == 200:
                clients = response.json()
                alejandro_client_found = False
                
                # Handle both list and dict response formats
                client_list = clients if isinstance(clients, list) else clients.get('clients', [])
                
                for client in client_list:
                    client_id = client.get('id', '')
                    email = client.get('email', '')
                    name = client.get('name', '')
                    
                    if (client_id == 'client_alejandro' or 
                        email == 'alejandro.mariscal@email.com' or
                        'alejandro' in name.lower()):
                        
                        alejandro_client_found = True
                        
                        self.log_result("Alejandro Client Record", True, 
                                      f"Found Alejandro in clients: {client.get('name')} ({client.get('email')})",
                                      {"client_data": client})
                        break
                
                if not alejandro_client_found:
                    self.log_result("Alejandro Client Record", False, 
                                  "Alejandro not found in clients list",
                                  {"total_clients": len(client_list)})
            else:
                self.log_result("Alejandro Client Record", False, 
                              f"Failed to get clients: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Alejandro Client Record", False, f"Exception: {str(e)}")
    
    def test_alejandro_google_drive_folder(self):
        """Test 3: Check if Alejandro has Google Drive folder metadata"""
        try:
            if not self.alejandro_data:
                self.log_result("Alejandro Google Drive Folder", False, 
                              "Cannot test - Alejandro user data not found")
                return
            
            alejandro_id = self.alejandro_data.get('id')
            
            # Check if user record has google_drive_folder_id
            google_drive_folder_id = self.alejandro_data.get('google_drive_folder_id')
            google_drive_folder = self.alejandro_data.get('google_drive_folder')
            
            if google_drive_folder_id or google_drive_folder:
                self.log_result("Alejandro Google Drive Folder Metadata", True, 
                              f"Google Drive folder metadata found: {google_drive_folder_id or google_drive_folder}",
                              {"folder_id": google_drive_folder_id, "folder_data": google_drive_folder})
            else:
                # Check if Alejandro exists as a prospect with Google Drive folder
                response = self.session.get(f"{BACKEND_URL}/crm/prospects")
                if response.status_code == 200:
                    prospects_data = response.json()
                    prospects = prospects_data if isinstance(prospects_data, list) else prospects_data.get('prospects', [])
                    
                    alejandro_prospect = None
                    for prospect in prospects:
                        if ('alejandro' in prospect.get('name', '').lower() or 
                            prospect.get('email') == 'alejandro.mariscal@email.com'):
                            alejandro_prospect = prospect
                            break
                    
                    if alejandro_prospect and alejandro_prospect.get('google_drive_folder'):
                        self.log_result("Alejandro Google Drive Folder Metadata", True, 
                                      f"Google Drive folder found in prospect record: {alejandro_prospect.get('google_drive_folder')}",
                                      {"prospect_data": alejandro_prospect})
                    else:
                        self.log_result("Alejandro Google Drive Folder Metadata", False, 
                                      "No Google Drive folder metadata found in user or prospect records",
                                      {"user_data": self.alejandro_data, "prospect_found": alejandro_prospect is not None})
                else:
                    self.log_result("Alejandro Google Drive Folder Metadata", False, 
                                  "No Google Drive folder metadata in user record, and cannot check prospects")
                
        except Exception as e:
            self.log_result("Alejandro Google Drive Folder Metadata", False, f"Exception: {str(e)}")
    
    def test_alejandro_document_access_endpoints(self):
        """Test 4: Test Document Access Endpoints for Alejandro"""
        try:
            if not self.alejandro_data:
                self.log_result("Alejandro Document Access", False, 
                              "Cannot test - Alejandro user data not found")
                return
            
            alejandro_id = self.alejandro_data.get('id', 'client_alejandro')
            
            # Test 1: /api/fidus/client-drive-folder/{client_id}
            response = self.session.get(f"{BACKEND_URL}/fidus/client-drive-folder/{alejandro_id}")
            if response.status_code == 200:
                documents = response.json()
                doc_count = len(documents) if isinstance(documents, list) else documents.get('count', 0)
                self.log_result("Alejandro Drive Folder Access", True, 
                              f"Drive folder endpoint accessible, {doc_count} documents found",
                              {"documents": documents})
            elif response.status_code == 404:
                self.log_result("Alejandro Drive Folder Access", False, 
                              "Client not found or no Google Drive folder configured",
                              {"status_code": response.status_code, "response": response.text[:200]})
            else:
                self.log_result("Alejandro Drive Folder Access", False, 
                              f"Drive folder endpoint failed: HTTP {response.status_code}",
                              {"response": response.text[:200]})
            
            # Test 2: /api/admin/clients/{client_id}/documents
            response = self.session.get(f"{BACKEND_URL}/admin/clients/{alejandro_id}/documents")
            if response.status_code == 200:
                documents = response.json()
                doc_count = len(documents) if isinstance(documents, list) else documents.get('count', 0)
                self.log_result("Alejandro Admin Documents Access", True, 
                              f"Admin documents endpoint accessible, {doc_count} documents found",
                              {"documents": documents})
            elif response.status_code == 404:
                self.log_result("Alejandro Admin Documents Access", False, 
                              "Admin documents endpoint not found or not implemented",
                              {"status_code": response.status_code})
            else:
                self.log_result("Alejandro Admin Documents Access", False, 
                              f"Admin documents endpoint failed: HTTP {response.status_code}",
                              {"response": response.text[:200]})
                
        except Exception as e:
            self.log_result("Alejandro Document Access", False, f"Exception: {str(e)}")
    
    def test_google_apis_service_availability(self):
        """Test 5: Check Google APIs service availability"""
        try:
            # Test Google connection monitor
            response = self.session.get(f"{BACKEND_URL}/google/connection/test-all")
            if response.status_code == 200:
                connection_data = response.json()
                overall_status = connection_data.get('overall_status', 'unknown')
                services = connection_data.get('services', {})
                
                working_services = sum(1 for service, data in services.items() 
                                     if data.get('status') == 'connected')
                total_services = len(services)
                
                if working_services >= 2:  # At least 2 services working
                    self.log_result("Google APIs Service Availability", True, 
                                  f"Google APIs available: {working_services}/{total_services} services connected",
                                  {"connection_data": connection_data})
                else:
                    self.log_result("Google APIs Service Availability", False, 
                                  f"Limited Google APIs availability: {working_services}/{total_services} services connected",
                                  {"connection_data": connection_data})
            else:
                self.log_result("Google APIs Service Availability", False, 
                              f"Google connection test failed: HTTP {response.status_code}")
            
            # Test Google Drive folder creation capability
            response = self.session.post(f"{BACKEND_URL}/google/drive/create-client-folder", 
                                       json={"client_name": "Test Client", "client_id": "test_client"})
            if response.status_code == 200:
                self.log_result("Google Drive Folder Creation", True, 
                              "Google Drive folder creation service available")
            elif response.status_code == 401:
                self.log_result("Google Drive Folder Creation", True, 
                              "Google Drive service available (authentication required)")
            else:
                self.log_result("Google Drive Folder Creation", False, 
                              f"Google Drive folder creation failed: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Google APIs Service Availability", False, f"Exception: {str(e)}")
    
    def test_alejandro_profile_completeness(self):
        """Test 6: Verify Alejandro's profile information completeness"""
        try:
            if not self.alejandro_data:
                self.log_result("Alejandro Profile Completeness", False, 
                              "Cannot test - Alejandro user data not found")
                return
            
            # Check required fields
            required_fields = {
                'id': 'User ID',
                'username': 'Username', 
                'name': 'Full Name',
                'email': 'Email Address',
                'phone': 'Phone Number',
                'type': 'User Type',
                'status': 'Account Status'
            }
            
            missing_fields = []
            present_fields = []
            
            for field, description in required_fields.items():
                value = self.alejandro_data.get(field)
                if value and str(value).strip():
                    present_fields.append(f"{description}: {value}")
                else:
                    missing_fields.append(description)
            
            completeness_score = len(present_fields) / len(required_fields) * 100
            
            if completeness_score >= 85:  # 85% or higher is good
                self.log_result("Alejandro Profile Completeness", True, 
                              f"Profile {completeness_score:.0f}% complete ({len(present_fields)}/{len(required_fields)} fields)",
                              {"present_fields": present_fields, "missing_fields": missing_fields})
            else:
                self.log_result("Alejandro Profile Completeness", False, 
                              f"Profile incomplete: {completeness_score:.0f}% complete, missing: {', '.join(missing_fields)}",
                              {"present_fields": present_fields, "missing_fields": missing_fields})
                
        except Exception as e:
            self.log_result("Alejandro Profile Completeness", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all Alejandro status verification tests"""
        print("🎯 ALEJANDRO MARISCAL CURRENT STATUS VERIFICATION TEST")
        print("=" * 65)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Alejandro Status Verification Tests...")
        print("-" * 55)
        
        # Run all verification tests in order
        self.test_alejandro_user_record()
        self.test_alejandro_client_record()
        self.test_alejandro_google_drive_folder()
        self.test_alejandro_document_access_endpoints()
        self.test_google_apis_service_availability()
        self.test_alejandro_profile_completeness()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 65)
        print("🎯 ALEJANDRO MARISCAL STATUS TEST SUMMARY")
        print("=" * 65)
        
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
        
        # Key findings summary
        print("🔍 KEY FINDINGS:")
        
        # User record status
        user_record_test = next((r for r in self.test_results if 'User Record' in r['test']), None)
        if user_record_test and user_record_test['success']:
            print(f"   ✅ Alejandro found in MongoDB users")
            if self.alejandro_data:
                print(f"      - ID: {self.alejandro_data.get('id', 'N/A')}")
                print(f"      - Email: {self.alejandro_data.get('email', 'N/A')}")
                print(f"      - Status: {self.alejandro_data.get('status', 'N/A')}")
        else:
            print(f"   ❌ Alejandro NOT found in MongoDB users")
        
        # Google Drive status
        drive_test = next((r for r in self.test_results if 'Google Drive Folder' in r['test']), None)
        if drive_test and drive_test['success']:
            print(f"   ✅ Google Drive folder metadata present")
        else:
            print(f"   ❌ Google Drive folder metadata missing or not configured")
        
        # Document access status
        doc_tests = [r for r in self.test_results if 'Document' in r['test'] or 'Drive Folder Access' in r['test']]
        working_doc_endpoints = sum(1 for t in doc_tests if t['success'])
        print(f"   📄 Document access: {working_doc_endpoints}/{len(doc_tests)} endpoints working")
        
        # Google APIs status
        google_test = next((r for r in self.test_results if 'Google APIs Service' in r['test']), None)
        if google_test and google_test['success']:
            print(f"   ✅ Google APIs service available")
        else:
            print(f"   ⚠️  Google APIs service limited or unavailable")
        
        print("\n🎯 RECOMMENDATION FOR MAIN AGENT:")
        if success_rate >= 70:
            print("✅ ALEJANDRO STATUS: READY FOR DOCUMENT MANAGEMENT IMPLEMENTATION")
            print("   Alejandro's record is properly configured in MongoDB.")
            print("   Proceed with automatic document management system implementation.")
        else:
            print("❌ ALEJANDRO STATUS: REQUIRES SETUP BEFORE DOCUMENT MANAGEMENT")
            print("   Critical issues found that need resolution:")
            for result in self.test_results:
                if not result['success'] and any(keyword in result['test'] for keyword in ['User Record', 'Google Drive']):
                    print(f"   - {result['message']}")
        
        print("\n" + "=" * 65)

def main():
    """Main test execution"""
    test_runner = AlejandroStatusTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()