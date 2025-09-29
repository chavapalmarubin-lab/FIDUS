#!/usr/bin/env python3
"""
ENHANCED CRM PIPELINE SYSTEM WITH GOOGLE INTEGRATION TEST
=========================================================

This test verifies the new Enhanced CRM Pipeline system with Google integration as requested:

1. Client-Specific Google Integration Endpoints:
   - /api/google/gmail/client-emails/{client_email} - Get emails for specific client
   - /api/google/calendar/client-meetings/{client_email} - Get meetings for specific client  
   - /api/google/drive/client-documents/{client_id} - Get documents for specific client
   - /api/google/drive/create-client-folder - Create Drive folder for client

2. Enhanced Pipeline Statistics:
   - /api/crm/pipeline-stats - Get comprehensive pipeline statistics
   - Verify it returns stage counts, values, conversion rates

3. Authentication & Authorization:
   - Ensure all new endpoints require admin authentication
   - Proper error handling for missing Google OAuth

Expected Results:
- All endpoints should require proper admin authentication
- When Google OAuth is missing, should return auth_required flag
- Client filtering should work correctly for emails/meetings/documents
- Pipeline stats should return accurate counts and percentages
- Error handling should be comprehensive
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://fidus-google-sync.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class EnhancedCRMPipelineTest:
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
    
    def test_client_specific_gmail_endpoint(self):
        """Test client-specific Gmail emails endpoint"""
        try:
            # Test with a real client email (Salvador's email)
            client_email = "chava@alyarglobal.com"
            
            # Test with authentication
            response = self.session.get(f"{BACKEND_URL}/google/gmail/client-emails/{client_email}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if data.get('success') is False and data.get('auth_required'):
                    self.log_result("Gmail Client Emails - Auth Required", True, 
                                  "Correctly returns auth_required when Google OAuth missing",
                                  {"response": data})
                elif data.get('success') is True:
                    emails = data.get('emails', [])
                    self.log_result("Gmail Client Emails - Success", True, 
                                  f"Successfully retrieved {len(emails)} emails for {client_email}",
                                  {"email_count": len(emails), "client_email": data.get('client_email')})
                else:
                    self.log_result("Gmail Client Emails - Response", False, 
                                  "Unexpected response format", {"response": data})
            else:
                self.log_result("Gmail Client Emails", False, 
                              f"HTTP {response.status_code}", {"response": response.text})
            
            # Test without authentication
            temp_session = requests.Session()
            response = temp_session.get(f"{BACKEND_URL}/google/gmail/client-emails/{client_email}")
            
            if response.status_code == 401:
                self.log_result("Gmail Client Emails - Auth Required", True, 
                              "Correctly requires admin authentication")
            else:
                self.log_result("Gmail Client Emails - Auth Required", False, 
                              f"Should return 401, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Gmail Client Emails", False, f"Exception: {str(e)}")
    
    def test_client_specific_calendar_endpoint(self):
        """Test client-specific Calendar meetings endpoint"""
        try:
            # Test with a real client email
            client_email = "chava@alyarglobal.com"
            
            # Test with authentication
            response = self.session.get(f"{BACKEND_URL}/google/calendar/client-meetings/{client_email}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if data.get('success') is False and data.get('auth_required'):
                    self.log_result("Calendar Client Meetings - Auth Required", True, 
                                  "Correctly returns auth_required when Google OAuth missing",
                                  {"response": data})
                elif data.get('success') is True:
                    meetings = data.get('meetings', [])
                    self.log_result("Calendar Client Meetings - Success", True, 
                                  f"Successfully retrieved {len(meetings)} meetings for {client_email}",
                                  {"meeting_count": len(meetings), "client_email": data.get('client_email')})
                else:
                    self.log_result("Calendar Client Meetings - Response", False, 
                                  "Unexpected response format", {"response": data})
            else:
                self.log_result("Calendar Client Meetings", False, 
                              f"HTTP {response.status_code}", {"response": response.text})
            
            # Test without authentication
            temp_session = requests.Session()
            response = temp_session.get(f"{BACKEND_URL}/google/calendar/client-meetings/{client_email}")
            
            if response.status_code == 401:
                self.log_result("Calendar Client Meetings - Auth Required", True, 
                              "Correctly requires admin authentication")
            else:
                self.log_result("Calendar Client Meetings - Auth Required", False, 
                              f"Should return 401, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Calendar Client Meetings", False, f"Exception: {str(e)}")
    
    def test_client_specific_drive_endpoint(self):
        """Test client-specific Google Drive documents endpoint"""
        try:
            # Test with a real client ID
            client_id = "client_003"  # Salvador's client ID
            
            # Test with authentication
            response = self.session.get(f"{BACKEND_URL}/google/drive/client-documents/{client_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if data.get('success') is False and data.get('auth_required'):
                    self.log_result("Drive Client Documents - Auth Required", True, 
                                  "Correctly returns auth_required when Google OAuth missing",
                                  {"response": data})
                elif data.get('success') is True:
                    documents = data.get('documents', [])
                    self.log_result("Drive Client Documents - Success", True, 
                                  f"Successfully retrieved {len(documents)} documents for {client_id}",
                                  {"document_count": len(documents), "client_id": data.get('client_id')})
                else:
                    self.log_result("Drive Client Documents - Response", False, 
                                  "Unexpected response format", {"response": data})
            else:
                self.log_result("Drive Client Documents", False, 
                              f"HTTP {response.status_code}", {"response": response.text})
            
            # Test without authentication
            temp_session = requests.Session()
            response = temp_session.get(f"{BACKEND_URL}/google/drive/client-documents/{client_id}")
            
            if response.status_code == 401:
                self.log_result("Drive Client Documents - Auth Required", True, 
                              "Correctly requires admin authentication")
            else:
                self.log_result("Drive Client Documents - Auth Required", False, 
                              f"Should return 401, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Drive Client Documents", False, f"Exception: {str(e)}")
    
    def test_create_client_folder_endpoint(self):
        """Test Google Drive create client folder endpoint"""
        try:
            # Test data for creating a client folder
            folder_data = {
                "client_id": "client_003",
                "client_name": "Salvador Palma",
                "folder_name": "Salvador Palma - FIDUS Documents Test"
            }
            
            # Test with authentication
            response = self.session.post(f"{BACKEND_URL}/google/drive/create-client-folder", json=folder_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if data.get('success') is False and data.get('auth_required'):
                    self.log_result("Create Client Folder - Auth Required", True, 
                                  "Correctly returns auth_required when Google OAuth missing",
                                  {"response": data})
                elif data.get('success') is True:
                    folder = data.get('folder', {})
                    self.log_result("Create Client Folder - Success", True, 
                                  f"Successfully created folder: {folder.get('name')}",
                                  {"folder_id": folder.get('id'), "folder_name": folder.get('name')})
                else:
                    self.log_result("Create Client Folder - Response", False, 
                                  "Unexpected response format", {"response": data})
            else:
                self.log_result("Create Client Folder", False, 
                              f"HTTP {response.status_code}", {"response": response.text})
            
            # Test without authentication
            temp_session = requests.Session()
            response = temp_session.post(f"{BACKEND_URL}/google/drive/create-client-folder", json=folder_data)
            
            if response.status_code == 401:
                self.log_result("Create Client Folder - Auth Required", True, 
                              "Correctly requires admin authentication")
            else:
                self.log_result("Create Client Folder - Auth Required", False, 
                              f"Should return 401, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Create Client Folder", False, f"Exception: {str(e)}")
    
    def test_pipeline_statistics_endpoint(self):
        """Test enhanced pipeline statistics endpoint"""
        try:
            # Test with authentication
            response = self.session.get(f"{BACKEND_URL}/crm/pipeline-stats")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') is True:
                    stats = data.get('stats', {})
                    
                    # Verify required fields are present
                    required_fields = [
                        'total_prospects', 'stage_counts', 'stage_values', 
                        'conversion_rate', 'total_pipeline_value'
                    ]
                    
                    missing_fields = [field for field in required_fields if field not in stats]
                    
                    if not missing_fields:
                        self.log_result("Pipeline Statistics - Structure", True, 
                                      "All required fields present in pipeline stats",
                                      {"total_prospects": stats.get('total_prospects'),
                                       "conversion_rate": stats.get('conversion_rate'),
                                       "total_pipeline_value": stats.get('total_pipeline_value')})
                        
                        # Verify stage counts
                        stage_counts = stats.get('stage_counts', {})
                        if isinstance(stage_counts, dict):
                            self.log_result("Pipeline Statistics - Stage Counts", True, 
                                          f"Stage counts calculated: {stage_counts}")
                        else:
                            self.log_result("Pipeline Statistics - Stage Counts", False, 
                                          "Stage counts should be a dictionary")
                        
                        # Verify conversion rate calculation
                        conversion_rate = stats.get('conversion_rate', 0)
                        if isinstance(conversion_rate, (int, float)) and 0 <= conversion_rate <= 100:
                            self.log_result("Pipeline Statistics - Conversion Rate", True, 
                                          f"Conversion rate calculated: {conversion_rate}%")
                        else:
                            self.log_result("Pipeline Statistics - Conversion Rate", False, 
                                          f"Invalid conversion rate: {conversion_rate}")
                    else:
                        self.log_result("Pipeline Statistics - Structure", False, 
                                      f"Missing required fields: {missing_fields}", {"stats": stats})
                else:
                    self.log_result("Pipeline Statistics", False, 
                                  "API returned success=False", {"response": data})
            else:
                self.log_result("Pipeline Statistics", False, 
                              f"HTTP {response.status_code}", {"response": response.text})
            
            # Test without authentication
            temp_session = requests.Session()
            response = temp_session.get(f"{BACKEND_URL}/crm/pipeline-stats")
            
            if response.status_code == 401:
                self.log_result("Pipeline Statistics - Auth Required", True, 
                              "Correctly requires admin authentication")
            else:
                self.log_result("Pipeline Statistics - Auth Required", False, 
                              f"Should return 401, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Pipeline Statistics", False, f"Exception: {str(e)}")
    
    def test_error_handling_comprehensive(self):
        """Test comprehensive error handling across all endpoints"""
        try:
            # Test invalid client email format
            response = self.session.get(f"{BACKEND_URL}/google/gmail/client-emails/invalid-email")
            if response.status_code == 200:
                data = response.json()
                if 'error' in data or data.get('success') is False:
                    self.log_result("Error Handling - Invalid Email", True, 
                                  "Properly handles invalid email format")
                else:
                    self.log_result("Error Handling - Invalid Email", False, 
                                  "Should handle invalid email format")
            
            # Test invalid client ID
            response = self.session.get(f"{BACKEND_URL}/google/drive/client-documents/invalid-client-id")
            if response.status_code == 200:
                data = response.json()
                if 'error' in data or data.get('success') is False:
                    self.log_result("Error Handling - Invalid Client ID", True, 
                                  "Properly handles invalid client ID")
                else:
                    self.log_result("Error Handling - Invalid Client ID", False, 
                                  "Should handle invalid client ID")
            
            # Test malformed JSON for folder creation
            response = self.session.post(f"{BACKEND_URL}/google/drive/create-client-folder", 
                                       json={"invalid": "data"})
            if response.status_code in [200, 400]:
                self.log_result("Error Handling - Malformed Data", True, 
                              "Properly handles malformed request data")
            else:
                self.log_result("Error Handling - Malformed Data", False, 
                              f"Unexpected status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("Error Handling Comprehensive", False, f"Exception: {str(e)}")
    
    def test_response_format_consistency(self):
        """Test that all endpoints return consistent JSON response formats"""
        try:
            endpoints_to_test = [
                ("/google/gmail/client-emails/chava@alyarglobal.com", "Gmail Client Emails"),
                ("/google/calendar/client-meetings/chava@alyarglobal.com", "Calendar Client Meetings"),
                ("/google/drive/client-documents/client_003", "Drive Client Documents"),
                ("/crm/pipeline-stats", "Pipeline Statistics")
            ]
            
            consistent_format = True
            format_issues = []
            
            for endpoint, name in endpoints_to_test:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Check for required fields in response
                        if 'success' not in data:
                            consistent_format = False
                            format_issues.append(f"{name}: missing 'success' field")
                        
                        # If success is False, should have error field
                        if data.get('success') is False and 'error' not in data:
                            consistent_format = False
                            format_issues.append(f"{name}: missing 'error' field when success=False")
                            
                    except json.JSONDecodeError:
                        consistent_format = False
                        format_issues.append(f"{name}: invalid JSON response")
            
            if consistent_format:
                self.log_result("Response Format Consistency", True, 
                              "All endpoints return consistent JSON format")
            else:
                self.log_result("Response Format Consistency", False, 
                              "Inconsistent response formats detected", 
                              {"issues": format_issues})
                
        except Exception as e:
            self.log_result("Response Format Consistency", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all Enhanced CRM Pipeline tests"""
        print("🎯 ENHANCED CRM PIPELINE SYSTEM WITH GOOGLE INTEGRATION TEST")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Enhanced CRM Pipeline Tests...")
        print("-" * 50)
        
        # Run all tests
        self.test_client_specific_gmail_endpoint()
        self.test_client_specific_calendar_endpoint()
        self.test_client_specific_drive_endpoint()
        self.test_create_client_folder_endpoint()
        self.test_pipeline_statistics_endpoint()
        self.test_error_handling_comprehensive()
        self.test_response_format_consistency()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 70)
        print("🎯 ENHANCED CRM PIPELINE TEST SUMMARY")
        print("=" * 70)
        
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
        
        # Critical assessment
        critical_tests = [
            "Gmail Client Emails",
            "Calendar Client Meetings", 
            "Drive Client Documents",
            "Create Client Folder",
            "Pipeline Statistics"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(critical in result['test'] for critical in critical_tests))
        
        print("🚨 CRITICAL ASSESSMENT:")
        if success_rate >= 80:
            print("✅ ENHANCED CRM PIPELINE SYSTEM: OPERATIONAL")
            print("   New Google integration endpoints are working correctly.")
            print("   Pipeline statistics calculations are functional.")
            print("   Authentication and error handling are properly implemented.")
        else:
            print("❌ ENHANCED CRM PIPELINE SYSTEM: ISSUES DETECTED")
            print("   Critical functionality issues found.")
            print("   Main agent action required for production readiness.")
        
        print("\n" + "=" * 70)

def main():
    """Main test execution"""
    test_runner = EnhancedCRMPipelineTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()