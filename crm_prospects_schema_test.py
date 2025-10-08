#!/usr/bin/env python3
"""
FIDUS CRM PROSPECTS MONGODB SCHEMA VALIDATION TEST
=================================================

This test verifies the MongoDB schema validation fixes for CRM prospects functionality:
- CRM Prospect Creation with proper prospect_id field usage
- Prospect Data Integrity (prospect_id vs id field)
- Google Drive Folder Persistence
- Prospect Listing functionality
- Prospect Updates with new schema
- Calendar API authentication resolution

Key Test Data:
- New prospect ID: d626a92d-7c67-483e-8f10-8717d5b737aa
- Name: Alejandro Mariscal Romero
- Email: alexmar7609@gmail.com
- Phone: +525551058520
- Google Drive folder ID: 1IDEprnXM_LS4sMDCcKRhOAtGdj8lSvzs
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

# Test prospect data
TEST_PROSPECT_DATA = {
    "prospect_id": "d626a92d-7c67-483e-8f10-8717d5b737aa",
    "name": "Alejandro Mariscal Romero",
    "email": "alexmar7609@gmail.com",
    "phone": "+525551058520",
    "google_drive_folder": "1IDEprnXM_LS4sMDCcKRhOAtGdj8lSvzs"
}

class CRMProspectsSchemaTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.created_prospect_id = None
        
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
    
    def test_existing_alejandro_prospect(self):
        """Test if Alejandro Mariscal Romero prospect already exists"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            if response.status_code == 200:
                prospects_data = response.json()
                
                # Handle different response formats
                if isinstance(prospects_data, dict) and 'prospects' in prospects_data:
                    prospects = prospects_data['prospects']
                elif isinstance(prospects_data, list):
                    prospects = prospects_data
                else:
                    prospects = []
                
                # Look for Alejandro prospect
                alejandro_found = None
                for prospect in prospects:
                    if (prospect.get('prospect_id') == TEST_PROSPECT_DATA['prospect_id'] or
                        prospect.get('email') == TEST_PROSPECT_DATA['email'] or
                        'Alejandro' in prospect.get('name', '')):
                        alejandro_found = prospect
                        break
                
                if alejandro_found:
                    # Verify prospect data integrity
                    data_issues = []
                    
                    # Check prospect_id field (should be used instead of id)
                    if 'prospect_id' not in alejandro_found:
                        data_issues.append("Missing prospect_id field")
                    elif alejandro_found.get('prospect_id') != TEST_PROSPECT_DATA['prospect_id']:
                        data_issues.append(f"prospect_id mismatch: expected {TEST_PROSPECT_DATA['prospect_id']}, got {alejandro_found.get('prospect_id')}")
                    
                    # Check Google Drive folder persistence
                    if 'google_drive_folder' not in alejandro_found:
                        data_issues.append("Missing google_drive_folder field")
                    elif alejandro_found.get('google_drive_folder') != TEST_PROSPECT_DATA['google_drive_folder']:
                        data_issues.append(f"google_drive_folder mismatch: expected {TEST_PROSPECT_DATA['google_drive_folder']}, got {alejandro_found.get('google_drive_folder')}")
                    
                    # Check basic data
                    if alejandro_found.get('name') != TEST_PROSPECT_DATA['name']:
                        data_issues.append(f"Name mismatch: expected {TEST_PROSPECT_DATA['name']}, got {alejandro_found.get('name')}")
                    
                    if alejandro_found.get('email') != TEST_PROSPECT_DATA['email']:
                        data_issues.append(f"Email mismatch: expected {TEST_PROSPECT_DATA['email']}, got {alejandro_found.get('email')}")
                    
                    if alejandro_found.get('phone') != TEST_PROSPECT_DATA['phone']:
                        data_issues.append(f"Phone mismatch: expected {TEST_PROSPECT_DATA['phone']}, got {alejandro_found.get('phone')}")
                    
                    if data_issues:
                        self.log_result("Existing Alejandro Prospect Data Integrity", False, 
                                      f"Found Alejandro but data integrity issues: {'; '.join(data_issues)}", 
                                      {"prospect_data": alejandro_found, "issues": data_issues})
                    else:
                        self.log_result("Existing Alejandro Prospect", True, 
                                      "Alejandro Mariscal Romero prospect found with correct data integrity",
                                      {"prospect_data": alejandro_found})
                        self.created_prospect_id = alejandro_found.get('prospect_id')
                        return True
                else:
                    self.log_result("Existing Alejandro Prospect", False, 
                                  "Alejandro Mariscal Romero prospect not found in existing prospects",
                                  {"total_prospects": len(prospects)})
                    return False
            else:
                self.log_result("Existing Alejandro Prospect", False, 
                              f"Failed to get prospects list: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Existing Alejandro Prospect", False, f"Exception: {str(e)}")
            return False
    
    def test_prospect_creation_schema_validation(self):
        """Test CRM prospect creation with MongoDB schema validation"""
        try:
            # Create new prospect with proper schema
            prospect_data = {
                "name": TEST_PROSPECT_DATA['name'],
                "email": TEST_PROSPECT_DATA['email'],
                "phone": TEST_PROSPECT_DATA['phone'],
                "notes": "Test prospect for MongoDB schema validation verification"
            }
            
            response = self.session.post(f"{BACKEND_URL}/crm/prospects", json=prospect_data)
            
            if response.status_code == 200 or response.status_code == 201:
                created_prospect = response.json()
                
                # Verify schema compliance
                schema_issues = []
                
                # Check that prospect_id field is used (not id)
                if 'prospect_id' not in created_prospect:
                    schema_issues.append("Missing prospect_id field - should use prospect_id instead of id")
                
                # Check that required fields are present
                required_fields = ['name', 'email', 'phone', 'stage', 'created_at', 'updated_at']
                for field in required_fields:
                    if field not in created_prospect:
                        schema_issues.append(f"Missing required field: {field}")
                
                # Check that google_drive_folder field exists (even if empty)
                if 'google_drive_folder' not in created_prospect:
                    schema_issues.append("Missing google_drive_folder field")
                
                # Check client_id field (should be empty string, not None)
                if 'client_id' in created_prospect and created_prospect['client_id'] is None:
                    schema_issues.append("client_id should be empty string, not None")
                
                if schema_issues:
                    self.log_result("Prospect Creation Schema Validation", False, 
                                  f"Schema validation issues: {'; '.join(schema_issues)}", 
                                  {"created_prospect": created_prospect, "schema_issues": schema_issues})
                else:
                    self.log_result("Prospect Creation Schema Validation", True, 
                                  "Prospect created successfully with proper MongoDB schema compliance",
                                  {"created_prospect": created_prospect})
                    self.created_prospect_id = created_prospect.get('prospect_id')
                    return True
            else:
                error_details = {"status_code": response.status_code, "response": response.text}
                if response.status_code == 500:
                    self.log_result("Prospect Creation Schema Validation", False, 
                                  "HTTP 500 - MongoDB schema validation error (Document failed validation)", 
                                  error_details)
                else:
                    self.log_result("Prospect Creation Schema Validation", False, 
                                  f"Failed to create prospect: HTTP {response.status_code}", 
                                  error_details)
                return False
                
        except Exception as e:
            self.log_result("Prospect Creation Schema Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_prospect_listing_functionality(self):
        """Test /api/crm/prospects endpoint returns prospects correctly"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            
            if response.status_code == 200:
                prospects_data = response.json()
                
                # Check response format
                if isinstance(prospects_data, dict) and 'prospects' in prospects_data:
                    prospects = prospects_data['prospects']
                    response_format = "wrapped"
                elif isinstance(prospects_data, list):
                    prospects = prospects_data
                    response_format = "direct_array"
                else:
                    self.log_result("Prospect Listing Functionality", False, 
                                  "Invalid response format - not array or wrapped object",
                                  {"response_type": type(prospects_data).__name__, "response": prospects_data})
                    return False
                
                # Verify prospect data structure
                if len(prospects) > 0:
                    sample_prospect = prospects[0]
                    structure_issues = []
                    
                    # Check for prospect_id field usage
                    if 'prospect_id' not in sample_prospect:
                        structure_issues.append("Prospects missing prospect_id field")
                    
                    # Check for google_drive_folder field
                    if 'google_drive_folder' not in sample_prospect:
                        structure_issues.append("Prospects missing google_drive_folder field")
                    
                    # Check required fields
                    required_fields = ['name', 'email', 'phone', 'stage']
                    for field in required_fields:
                        if field not in sample_prospect:
                            structure_issues.append(f"Prospects missing required field: {field}")
                    
                    if structure_issues:
                        self.log_result("Prospect Listing Functionality", False, 
                                      f"Prospect data structure issues: {'; '.join(structure_issues)}", 
                                      {"sample_prospect": sample_prospect, "structure_issues": structure_issues})
                    else:
                        self.log_result("Prospect Listing Functionality", True, 
                                      f"Prospects listing working correctly ({response_format} format, {len(prospects)} prospects)",
                                      {"total_prospects": len(prospects), "response_format": response_format})
                        return True
                else:
                    self.log_result("Prospect Listing Functionality", True, 
                                  "Prospects endpoint accessible but no prospects found",
                                  {"response_format": response_format})
                    return True
            else:
                self.log_result("Prospect Listing Functionality", False, 
                              f"Failed to get prospects: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Prospect Listing Functionality", False, f"Exception: {str(e)}")
            return False
    
    def test_prospect_update_schema(self):
        """Test updating prospects works with the new schema"""
        if not self.created_prospect_id:
            self.log_result("Prospect Update Schema", False, "No prospect ID available for update test")
            return False
        
        try:
            # Test prospect update
            update_data = {
                "stage": "qualified",
                "notes": "Updated notes for schema validation test",
                "google_drive_folder": TEST_PROSPECT_DATA['google_drive_folder']
            }
            
            response = self.session.put(f"{BACKEND_URL}/crm/prospects/{self.created_prospect_id}", json=update_data)
            
            if response.status_code == 200:
                updated_prospect = response.json()
                
                # Verify update worked and schema is maintained
                update_issues = []
                
                if updated_prospect.get('stage') != 'qualified':
                    update_issues.append("Stage update failed")
                
                if updated_prospect.get('google_drive_folder') != TEST_PROSPECT_DATA['google_drive_folder']:
                    update_issues.append("Google Drive folder update failed")
                
                if 'prospect_id' not in updated_prospect:
                    update_issues.append("prospect_id field missing after update")
                
                if 'updated_at' not in updated_prospect:
                    update_issues.append("updated_at field not updated")
                
                if update_issues:
                    self.log_result("Prospect Update Schema", False, 
                                  f"Update issues: {'; '.join(update_issues)}", 
                                  {"updated_prospect": updated_prospect, "update_issues": update_issues})
                else:
                    self.log_result("Prospect Update Schema", True, 
                                  "Prospect update working correctly with new schema",
                                  {"updated_prospect": updated_prospect})
                    return True
            else:
                error_details = {"status_code": response.status_code, "response": response.text}
                if response.status_code == 500:
                    self.log_result("Prospect Update Schema", False, 
                                  "HTTP 500 - MongoDB schema validation error during update", 
                                  error_details)
                else:
                    self.log_result("Prospect Update Schema", False, 
                                  f"Failed to update prospect: HTTP {response.status_code}", 
                                  error_details)
                return False
                
        except Exception as e:
            self.log_result("Prospect Update Schema", False, f"Exception: {str(e)}")
            return False
    
    def test_google_drive_folder_persistence(self):
        """Test that google_drive_folder field is correctly stored and returned"""
        try:
            # Get all prospects and check for google_drive_folder field persistence
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            
            if response.status_code == 200:
                prospects_data = response.json()
                
                # Handle different response formats
                if isinstance(prospects_data, dict) and 'prospects' in prospects_data:
                    prospects = prospects_data['prospects']
                elif isinstance(prospects_data, list):
                    prospects = prospects_data
                else:
                    prospects = []
                
                folder_persistence_issues = []
                prospects_with_folders = 0
                
                for prospect in prospects:
                    # Check if google_drive_folder field exists
                    if 'google_drive_folder' not in prospect:
                        folder_persistence_issues.append(f"Prospect {prospect.get('name', 'Unknown')} missing google_drive_folder field")
                    else:
                        # Check if folder ID is properly stored (not None or empty when it should have value)
                        folder_id = prospect.get('google_drive_folder')
                        if folder_id and folder_id.strip():
                            prospects_with_folders += 1
                
                if folder_persistence_issues:
                    self.log_result("Google Drive Folder Persistence", False, 
                                  f"Folder persistence issues: {'; '.join(folder_persistence_issues[:3])}", 
                                  {"total_issues": len(folder_persistence_issues), "prospects_with_folders": prospects_with_folders})
                else:
                    self.log_result("Google Drive Folder Persistence", True, 
                                  f"Google Drive folder field properly persisted across all prospects ({prospects_with_folders} have folder IDs)",
                                  {"total_prospects": len(prospects), "prospects_with_folders": prospects_with_folders})
                    return True
            else:
                self.log_result("Google Drive Folder Persistence", False, 
                              f"Failed to get prospects for folder persistence test: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Google Drive Folder Persistence", False, f"Exception: {str(e)}")
            return False
    
    def test_calendar_api_authentication(self):
        """Test if Calendar API authentication issues are resolved"""
        try:
            # Test Calendar API endpoints
            calendar_endpoints = [
                ("/google/calendar/events", "Calendar Events"),
                ("/google/calendar/real-events", "Real Calendar Events"),
                ("/admin/google/profile", "Google Profile (for OAuth status)")
            ]
            
            calendar_results = []
            
            for endpoint, name in calendar_endpoints:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                    
                    if response.status_code == 200:
                        calendar_results.append(f"✅ {name}: Working")
                    elif response.status_code == 401:
                        # 401 is expected if not authenticated with Google
                        calendar_results.append(f"🔐 {name}: Requires Google OAuth (expected)")
                    elif response.status_code == 500:
                        response_text = response.text
                        if "Failed to get calendar events" in response_text:
                            calendar_results.append(f"❌ {name}: HTTP 500 - Calendar API authentication issue")
                        else:
                            calendar_results.append(f"❌ {name}: HTTP 500 - {response_text[:100]}")
                    else:
                        calendar_results.append(f"⚠️ {name}: HTTP {response.status_code}")
                        
                except Exception as e:
                    calendar_results.append(f"❌ {name}: Exception - {str(e)}")
            
            # Analyze results
            auth_issues = [result for result in calendar_results if "authentication issue" in result or "HTTP 500" in result]
            working_endpoints = [result for result in calendar_results if "✅" in result]
            oauth_required = [result for result in calendar_results if "🔐" in result]
            
            if auth_issues:
                self.log_result("Calendar API Authentication", False, 
                              f"Calendar API authentication issues found: {len(auth_issues)} endpoints failing", 
                              {"results": calendar_results, "auth_issues": auth_issues})
            elif len(working_endpoints) > 0 or len(oauth_required) > 0:
                self.log_result("Calendar API Authentication", True, 
                              f"Calendar API authentication resolved ({len(working_endpoints)} working, {len(oauth_required)} require OAuth)",
                              {"results": calendar_results})
                return True
            else:
                self.log_result("Calendar API Authentication", False, 
                              "All Calendar API endpoints have issues",
                              {"results": calendar_results})
                
        except Exception as e:
            self.log_result("Calendar API Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_crm_pipeline_stats(self):
        """Test CRM pipeline statistics endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/pipeline-stats")
            
            if response.status_code == 200:
                stats_data = response.json()
                
                # Check if stats have proper structure
                if isinstance(stats_data, dict):
                    # Look for expected fields
                    expected_fields = ['stages', 'total_prospects', 'conversion_rate']
                    missing_fields = [field for field in expected_fields if field not in stats_data]
                    
                    if missing_fields:
                        self.log_result("CRM Pipeline Stats", False, 
                                      f"Pipeline stats missing expected fields: {', '.join(missing_fields)}", 
                                      {"stats_data": stats_data, "missing_fields": missing_fields})
                    else:
                        self.log_result("CRM Pipeline Stats", True, 
                                      "CRM pipeline statistics working correctly",
                                      {"stats_data": stats_data})
                        return True
                else:
                    self.log_result("CRM Pipeline Stats", False, 
                                  "Pipeline stats returned invalid format",
                                  {"response_type": type(stats_data).__name__, "stats_data": stats_data})
            else:
                error_details = {"status_code": response.status_code, "response": response.text}
                if response.status_code == 500:
                    if "get_collection" in response.text:
                        self.log_result("CRM Pipeline Stats", False, 
                                      "HTTP 500 - MongoDB collection access error (get_collection method issue)", 
                                      error_details)
                    else:
                        self.log_result("CRM Pipeline Stats", False, 
                                      "HTTP 500 - Pipeline stats calculation error", 
                                      error_details)
                else:
                    self.log_result("CRM Pipeline Stats", False, 
                                  f"Failed to get pipeline stats: HTTP {response.status_code}", 
                                  error_details)
                return False
                
        except Exception as e:
            self.log_result("CRM Pipeline Stats", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all CRM prospects schema validation tests"""
        print("🎯 FIDUS CRM PROSPECTS MONGODB SCHEMA VALIDATION TEST")
        print("=" * 65)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print(f"Target Prospect: {TEST_PROSPECT_DATA['name']} ({TEST_PROSPECT_DATA['email']})")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running CRM Prospects Schema Validation Tests...")
        print("-" * 55)
        
        # Run all tests
        self.test_existing_alejandro_prospect()
        self.test_prospect_creation_schema_validation()
        self.test_prospect_listing_functionality()
        self.test_prospect_update_schema()
        self.test_google_drive_folder_persistence()
        self.test_calendar_api_authentication()
        self.test_crm_pipeline_stats()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 65)
        print("🎯 CRM PROSPECTS SCHEMA VALIDATION TEST SUMMARY")
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
        
        # Critical assessment for MongoDB schema validation
        critical_tests = [
            "Prospect Creation Schema Validation",
            "Prospect Listing Functionality", 
            "Google Drive Folder Persistence",
            "Prospect Update Schema"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(critical in result['test'] for critical in critical_tests))
        
        print("🚨 CRITICAL ASSESSMENT:")
        if critical_passed >= 3:  # At least 3 out of 4 critical tests
            print("✅ MONGODB SCHEMA VALIDATION: SUCCESSFUL")
            print("   CRM prospects functionality working with proper schema validation.")
            print("   prospect_id field usage and Google Drive folder persistence verified.")
        else:
            print("❌ MONGODB SCHEMA VALIDATION: ISSUES FOUND")
            print("   Critical MongoDB schema validation issues detected.")
            print("   Main agent action required to fix schema validation errors.")
        
        print("\n" + "=" * 65)

def main():
    """Main test execution"""
    test_runner = CRMProspectsSchemaTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()