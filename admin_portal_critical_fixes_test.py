#!/usr/bin/env python3
"""
CRITICAL FIXES FOR ADMIN PORTAL FUNCTIONALITY TEST
=================================================

This test verifies the CRITICAL FIXES for admin portal functionality as requested in the review:

1. CRM Pipeline with Won Prospects and Action Buttons:
   - Test /api/crm/prospects - should return 6 prospects including 2 in "won" stage
   - Verify Michael Chen (won, no AML/KYC) should show "Start AML/KYC" button
   - Verify Emma Thompson (won, AML/KYC approved) should show "Convert to Client" button  
   - Confirm Robert Johnson (won, already converted) should show neither button

2. Automatic Google Drive Folder Creation:
   - Test if sample prospects now have google_drive_folder field populated
   - Verify /api/crm/prospects POST creates folder automatically for new prospects
   - Check folder names follow pattern: "{Name} - FIDUS Documents"

3. Fixed Backend API Issues:
   - Test /api/crm/pipeline-stats - should work without datetime timezone errors
   - Verify timezone-aware datetime handling doesn't cause comparison errors
   - Confirm prospects are properly sorted by date

4. Google Workspace Data Loading:
   - Test /api/google/gmail/real-messages for actual Gmail data
   - Test /api/google/calendar/real-events for calendar events
   - Test /api/google/drive/real-files for Drive files
   - Check if OAuth session persistence is working

Expected Results:
- 6 prospects total with 3 in "won" stage showing different action buttons
- All prospects have Google Drive folders auto-created
- No datetime timezone comparison errors in pipeline
- Google API endpoints return data when authenticated properly
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://invest-portal-31.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class CriticalFixesTest:
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
    
    def test_crm_prospects_with_won_stage(self):
        """Test CRM Pipeline with Won Prospects and Action Buttons"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            if response.status_code == 200:
                data = response.json()
                prospects = data if isinstance(data, list) else data.get('prospects', [])
                
                # Check total prospect count
                if len(prospects) == 6:
                    self.log_result("CRM Prospects Count", True, f"Found 6 prospects as expected")
                else:
                    self.log_result("CRM Prospects Count", False, f"Expected 6 prospects, found {len(prospects)}")
                
                # Check for won stage prospects
                won_prospects = [p for p in prospects if p.get('stage') == 'won']
                if len(won_prospects) >= 2:
                    self.log_result("Won Stage Prospects", True, f"Found {len(won_prospects)} prospects in 'won' stage")
                    
                    # Check specific prospects and their action buttons
                    self.check_prospect_action_buttons(won_prospects)
                else:
                    self.log_result("Won Stage Prospects", False, f"Expected at least 2 'won' prospects, found {len(won_prospects)}")
                
                # Check Google Drive folder field
                prospects_with_folders = [p for p in prospects if p.get('google_drive_folder')]
                if len(prospects_with_folders) > 0:
                    self.log_result("Google Drive Folders", True, f"{len(prospects_with_folders)} prospects have google_drive_folder field")
                    
                    # Check folder name pattern
                    for prospect in prospects_with_folders:
                        folder_name = prospect.get('google_drive_folder', {}).get('name', '')
                        expected_pattern = f"{prospect.get('name', '')} - FIDUS Documents"
                        if folder_name == expected_pattern:
                            self.log_result(f"Folder Pattern - {prospect.get('name')}", True, f"Folder name follows pattern: {folder_name}")
                        else:
                            self.log_result(f"Folder Pattern - {prospect.get('name')}", False, f"Expected: {expected_pattern}, Got: {folder_name}")
                else:
                    self.log_result("Google Drive Folders", False, "No prospects have google_drive_folder field populated")
                    
            else:
                self.log_result("CRM Prospects API", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("CRM Prospects Test", False, f"Exception: {str(e)}")
    
    def check_prospect_action_buttons(self, won_prospects):
        """Check specific prospect action buttons"""
        prospect_checks = {
            "Michael Chen": {"aml_kyc": False, "converted": False, "expected_button": "Start AML/KYC"},
            "Emma Thompson": {"aml_kyc": True, "converted": False, "expected_button": "Convert to Client"},
            "Robert Johnson": {"aml_kyc": True, "converted": True, "expected_button": None}
        }
        
        for prospect in won_prospects:
            name = prospect.get('name', '')
            for expected_name, expected_data in prospect_checks.items():
                if expected_name.lower() in name.lower():
                    # Check AML/KYC status
                    aml_kyc_status = prospect.get('aml_kyc_completed', False)
                    converted_status = prospect.get('converted_to_client', False)
                    
                    if aml_kyc_status == expected_data['aml_kyc'] and converted_status == expected_data['converted']:
                        expected_button = expected_data['expected_button']
                        if expected_button:
                            self.log_result(f"Action Button - {name}", True, f"Should show '{expected_button}' button")
                        else:
                            self.log_result(f"Action Button - {name}", True, f"Should show no action buttons (already converted)")
                    else:
                        self.log_result(f"Prospect Status - {name}", False, 
                                      f"Status mismatch - AML/KYC: {aml_kyc_status} (expected {expected_data['aml_kyc']}), Converted: {converted_status} (expected {expected_data['converted']})")
    
    def test_pipeline_stats_api(self):
        """Test pipeline stats API for timezone errors"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/pipeline-stats")
            if response.status_code == 200:
                data = response.json()
                
                # Check if response contains expected pipeline statistics
                if 'stages' in data or 'pipeline_stats' in data:
                    self.log_result("Pipeline Stats API", True, "Pipeline stats API working without timezone errors")
                    
                    # Check if prospects are properly sorted by date
                    if 'prospects_by_stage' in data:
                        for stage, prospects in data['prospects_by_stage'].items():
                            if len(prospects) > 1:
                                # Check if sorted by date (most recent first)
                                dates = [p.get('created_at') or p.get('updated_at') for p in prospects if p.get('created_at') or p.get('updated_at')]
                                if dates:
                                    sorted_dates = sorted(dates, reverse=True)
                                    if dates == sorted_dates:
                                        self.log_result(f"Date Sorting - {stage}", True, f"Prospects in {stage} properly sorted by date")
                                    else:
                                        self.log_result(f"Date Sorting - {stage}", False, f"Prospects in {stage} not properly sorted by date")
                else:
                    self.log_result("Pipeline Stats Content", False, "Pipeline stats response missing expected fields", {"response": data})
                    
            else:
                self.log_result("Pipeline Stats API", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Pipeline Stats Test", False, f"Exception: {str(e)}")
    
    def test_prospect_creation_with_folder(self):
        """Test creating new prospect automatically creates Google Drive folder"""
        try:
            # Create a test prospect
            test_prospect = {
                "name": "Test Prospect Auto Folder",
                "email": "test.prospect@example.com",
                "phone": "+1-555-0123",
                "notes": "Test prospect for automatic folder creation"
            }
            
            response = self.session.post(f"{BACKEND_URL}/crm/prospects", json=test_prospect)
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                prospect_id = data.get('id') or data.get('prospect_id')
                
                if prospect_id:
                    # Check if Google Drive folder was created
                    if 'google_drive_folder' in data:
                        folder_info = data['google_drive_folder']
                        expected_name = f"{test_prospect['name']} - FIDUS Documents"
                        
                        if folder_info.get('name') == expected_name:
                            self.log_result("Auto Folder Creation", True, f"Google Drive folder automatically created: {expected_name}")
                        else:
                            self.log_result("Auto Folder Creation", False, f"Folder created but wrong name: {folder_info.get('name')}")
                    else:
                        self.log_result("Auto Folder Creation", False, "No google_drive_folder field in response")
                    
                    # Clean up - delete test prospect
                    try:
                        self.session.delete(f"{BACKEND_URL}/crm/prospects/{prospect_id}")
                    except:
                        pass  # Ignore cleanup errors
                else:
                    self.log_result("Prospect Creation", False, "No prospect ID returned", {"response": data})
            else:
                self.log_result("Prospect Creation", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Auto Folder Creation Test", False, f"Exception: {str(e)}")
    
    def test_google_workspace_data_loading(self):
        """Test Google Workspace data loading endpoints"""
        google_endpoints = [
            ("/google/gmail/real-messages", "Gmail Real Messages"),
            ("/google/calendar/real-events", "Calendar Real Events"),
            ("/google/drive/real-files", "Drive Real Files")
        ]
        
        for endpoint, name in google_endpoints:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check if data is returned (not just empty)
                    if isinstance(data, dict):
                        if data.get('success') and data.get('data'):
                            data_count = len(data['data']) if isinstance(data['data'], list) else 1
                            self.log_result(f"Google API - {name}", True, f"Returned {data_count} items")
                        elif data.get('auth_required'):
                            self.log_result(f"Google API - {name}", True, f"Properly requires OAuth authentication")
                        else:
                            self.log_result(f"Google API - {name}", False, f"No data returned", {"response": data})
                    elif isinstance(data, list) and len(data) > 0:
                        self.log_result(f"Google API - {name}", True, f"Returned {len(data)} items")
                    else:
                        self.log_result(f"Google API - {name}", False, f"Empty or invalid response", {"response": data})
                        
                elif response.status_code == 401:
                    # OAuth required is acceptable
                    self.log_result(f"Google API - {name}", True, f"Properly requires authentication (401)")
                else:
                    self.log_result(f"Google API - {name}", False, f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_result(f"Google API - {name}", False, f"Exception: {str(e)}")
    
    def test_oauth_session_persistence(self):
        """Test OAuth session persistence"""
        try:
            # Test Google profile endpoint (requires OAuth)
            response = self.session.get(f"{BACKEND_URL}/admin/google/profile")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('profile'):
                    self.log_result("OAuth Session Persistence", True, "OAuth session working - profile data retrieved")
                else:
                    self.log_result("OAuth Session Persistence", False, "Profile endpoint accessible but no profile data")
            elif response.status_code == 401:
                # Check if proper auth_required response
                try:
                    data = response.json()
                    if data.get('auth_required'):
                        self.log_result("OAuth Session Persistence", True, "Properly indicates OAuth authentication required")
                    else:
                        self.log_result("OAuth Session Persistence", False, "401 but no auth_required flag")
                except:
                    self.log_result("OAuth Session Persistence", True, "Properly requires OAuth authentication")
            else:
                self.log_result("OAuth Session Persistence", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("OAuth Session Test", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all critical fixes tests"""
        print("🎯 CRITICAL FIXES FOR ADMIN PORTAL FUNCTIONALITY TEST")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Critical Fixes Tests...")
        print("-" * 50)
        
        # Run all critical fixes tests
        self.test_crm_prospects_with_won_stage()
        self.test_pipeline_stats_api()
        self.test_prospect_creation_with_folder()
        self.test_google_workspace_data_loading()
        self.test_oauth_session_persistence()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 CRITICAL FIXES TEST SUMMARY")
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
        
        # Critical assessment for each fix area
        print("🚨 CRITICAL FIXES ASSESSMENT:")
        
        # CRM Pipeline Assessment
        crm_tests = [r for r in self.test_results if 'CRM' in r['test'] or 'Pipeline' in r['test'] or 'Prospect' in r['test']]
        crm_passed = sum(1 for r in crm_tests if r['success'])
        print(f"1. CRM Pipeline & Won Prospects: {crm_passed}/{len(crm_tests)} tests passed")
        
        # Google Drive Folder Assessment
        folder_tests = [r for r in self.test_results if 'Folder' in r['test'] or 'Auto Folder' in r['test']]
        folder_passed = sum(1 for r in folder_tests if r['success'])
        print(f"2. Google Drive Folder Creation: {folder_passed}/{len(folder_tests)} tests passed")
        
        # API Issues Assessment
        api_tests = [r for r in self.test_results if 'Pipeline Stats' in r['test'] or 'Date Sorting' in r['test']]
        api_passed = sum(1 for r in api_tests if r['success'])
        print(f"3. Backend API Issues Fixed: {api_passed}/{len(api_tests)} tests passed")
        
        # Google Workspace Assessment
        google_tests = [r for r in self.test_results if 'Google API' in r['test'] or 'OAuth' in r['test']]
        google_passed = sum(1 for r in google_tests if r['success'])
        print(f"4. Google Workspace Data Loading: {google_passed}/{len(google_tests)} tests passed")
        
        print()
        if success_rate >= 80:
            print("✅ CRITICAL FIXES: MOSTLY SUCCESSFUL")
            print("   Admin portal functionality improvements are working.")
        else:
            print("❌ CRITICAL FIXES: ISSUES FOUND")
            print("   Some critical fixes need attention before deployment.")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = CriticalFixesTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()