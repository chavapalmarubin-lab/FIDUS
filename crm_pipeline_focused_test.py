#!/usr/bin/env python3
"""
CRM PIPELINE FOCUSED TEST - ADDRESSING SPECIFIC ISSUES
======================================================

This test focuses on the specific issues found in the Enhanced CRM Pipeline system:

1. Missing create_drive_folder method in GoogleAPIsService
2. Missing get_collection method in MongoDBManager  
3. Pipeline statistics calculation issues
4. Client-specific Google integration functionality

This test will provide detailed diagnostics for the main agent to fix these issues.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://trading-platform-76.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class CRMPipelineFocusedTest:
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
    
    def test_existing_crm_prospects_endpoint(self):
        """Test existing CRM prospects endpoint to understand current state"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            
            if response.status_code == 200:
                data = response.json()
                prospects = data if isinstance(data, list) else data.get('prospects', [])
                
                self.log_result("CRM Prospects Endpoint", True, 
                              f"Successfully retrieved {len(prospects)} prospects",
                              {"prospect_count": len(prospects), "sample_prospect": prospects[0] if prospects else None})
                
                # Test prospect creation to understand schema issues
                test_prospect = {
                    "name": "Test Prospect for Pipeline",
                    "email": "test.pipeline@example.com",
                    "phone": "+1234567890",
                    "notes": "Test prospect for pipeline statistics"
                }
                
                create_response = self.session.post(f"{BACKEND_URL}/crm/prospects", json=test_prospect)
                if create_response.status_code == 200:
                    self.log_result("CRM Prospect Creation", True, "Successfully created test prospect")
                else:
                    self.log_result("CRM Prospect Creation", False, 
                                  f"Failed to create prospect: HTTP {create_response.status_code}",
                                  {"response": create_response.text})
                
            else:
                self.log_result("CRM Prospects Endpoint", False, 
                              f"HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_result("CRM Prospects Endpoint", False, f"Exception: {str(e)}")
    
    def test_pipeline_stats_detailed(self):
        """Test pipeline statistics with detailed error analysis"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/pipeline-stats")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') is True:
                    stats = data.get('stats', {})
                    self.log_result("Pipeline Statistics - Success", True, 
                                  "Pipeline statistics calculated successfully",
                                  {"stats": stats})
                else:
                    error_msg = data.get('error', 'Unknown error')
                    self.log_result("Pipeline Statistics - Error Analysis", False, 
                                  f"Pipeline stats failed: {error_msg}",
                                  {"full_response": data})
                    
                    # Provide specific fix recommendations
                    if "get_collection" in error_msg:
                        self.log_result("Fix Recommendation - MongoDB", False, 
                                      "ISSUE: MongoDBManager missing get_collection method. FIX: Use db.crm_prospects directly or add get_collection method to MongoDBManager class")
                    
            else:
                self.log_result("Pipeline Statistics", False, 
                              f"HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_result("Pipeline Statistics", False, f"Exception: {str(e)}")
    
    def test_google_drive_folder_creation_detailed(self):
        """Test Google Drive folder creation with detailed error analysis"""
        try:
            folder_data = {
                "client_id": "client_003",
                "client_name": "Salvador Palma",
                "folder_name": "Test Folder Creation"
            }
            
            response = self.session.post(f"{BACKEND_URL}/google/drive/create-client-folder", json=folder_data)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') is True:
                    self.log_result("Google Drive Folder Creation - Success", True, 
                                  "Folder created successfully",
                                  {"folder_data": data.get('folder', {})})
                else:
                    error_msg = data.get('error', 'Unknown error')
                    self.log_result("Google Drive Folder Creation - Error Analysis", False, 
                                  f"Folder creation failed: {error_msg}",
                                  {"full_response": data})
                    
                    # Provide specific fix recommendations
                    if "create_drive_folder" in error_msg:
                        self.log_result("Fix Recommendation - Google APIs", False, 
                                      "ISSUE: GoogleAPIsService missing create_drive_folder method. FIX: Add create_drive_folder method to GoogleAPIsService class")
                    
            else:
                self.log_result("Google Drive Folder Creation", False, 
                              f"HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_result("Google Drive Folder Creation", False, f"Exception: {str(e)}")
    
    def test_client_specific_endpoints_functionality(self):
        """Test the functionality of client-specific Google integration endpoints"""
        try:
            # Test Gmail client emails
            response = self.session.get(f"{BACKEND_URL}/google/gmail/client-emails/chava@alyarglobal.com")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    emails = data.get('emails', [])
                    self.log_result("Gmail Client Emails - Functionality", True, 
                                  f"Successfully filtered {len(emails)} emails for client",
                                  {"email_count": len(emails), "client_email": data.get('client_email')})
                else:
                    self.log_result("Gmail Client Emails - Auth Status", True, 
                                  "Correctly handles missing Google OAuth",
                                  {"auth_required": data.get('auth_required')})
            
            # Test Calendar client meetings
            response = self.session.get(f"{BACKEND_URL}/google/calendar/client-meetings/chava@alyarglobal.com")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    meetings = data.get('meetings', [])
                    self.log_result("Calendar Client Meetings - Functionality", True, 
                                  f"Successfully filtered {len(meetings)} meetings for client",
                                  {"meeting_count": len(meetings), "client_email": data.get('client_email')})
                else:
                    self.log_result("Calendar Client Meetings - Auth Status", True, 
                                  "Correctly handles missing Google OAuth",
                                  {"auth_required": data.get('auth_required')})
            
            # Test Drive client documents
            response = self.session.get(f"{BACKEND_URL}/google/drive/client-documents/client_003")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    documents = data.get('documents', [])
                    self.log_result("Drive Client Documents - Functionality", True, 
                                  f"Successfully filtered {len(documents)} documents for client",
                                  {"document_count": len(documents), "client_id": data.get('client_id')})
                else:
                    self.log_result("Drive Client Documents - Auth Status", True, 
                                  "Correctly handles missing Google OAuth",
                                  {"auth_required": data.get('auth_required')})
                
        except Exception as e:
            self.log_result("Client-Specific Endpoints", False, f"Exception: {str(e)}")
    
    def run_focused_tests(self):
        """Run focused tests to diagnose specific issues"""
        print("🎯 CRM PIPELINE FOCUSED TEST - ISSUE DIAGNOSIS")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Focused Diagnostic Tests...")
        print("-" * 50)
        
        # Run focused tests
        self.test_existing_crm_prospects_endpoint()
        self.test_pipeline_stats_detailed()
        self.test_google_drive_folder_creation_detailed()
        self.test_client_specific_endpoints_functionality()
        
        # Generate diagnostic summary
        self.generate_diagnostic_summary()
        
        return True
    
    def generate_diagnostic_summary(self):
        """Generate diagnostic summary with specific fix recommendations"""
        print("\n" + "=" * 60)
        print("🎯 CRM PIPELINE DIAGNOSTIC SUMMARY")
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
        
        # Show critical issues and fixes
        print("🚨 CRITICAL ISSUES IDENTIFIED:")
        
        issues_found = []
        for result in self.test_results:
            if not result['success'] and 'Fix Recommendation' in result['test']:
                issues_found.append(result['message'])
                print(f"   • {result['message']}")
        
        if not issues_found:
            print("   • No critical implementation issues found")
        
        print()
        
        # Show working functionality
        print("✅ WORKING FUNCTIONALITY:")
        working_features = []
        for result in self.test_results:
            if result['success'] and 'Functionality' in result['test']:
                working_features.append(result['test'])
                print(f"   • {result['test']}: {result['message']}")
        
        print()
        
        # Main agent action items
        print("📋 MAIN AGENT ACTION ITEMS:")
        print("1. Add create_drive_folder method to GoogleAPIsService class")
        print("2. Fix pipeline statistics to use db.crm_prospects directly instead of mongodb_manager.get_collection")
        print("3. Verify CRM prospect creation and schema validation")
        print("4. Test complete Google OAuth integration flow")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = CRMPipelineFocusedTest()
    success = test_runner.run_focused_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()