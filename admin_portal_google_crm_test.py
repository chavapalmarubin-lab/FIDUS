#!/usr/bin/env python3
"""
ADMIN PORTAL GOOGLE WORKSPACE AND CRM FUNCTIONALITY TEST
========================================================

This test addresses the critical admin portal issues identified in the review request:

1. **Google Workspace Data Loading**:
   - Test /api/google/gmail/real-messages - should return actual Gmail data when connected
   - Test /api/google/calendar/real-events - should return calendar events
   - Test /api/google/drive/real-files - should return Drive files
   - Verify why connection shows "connected" but no data loads

2. **CRM Pipeline Issues**:
   - Test /api/crm/prospects - should return prospects for pipeline display
   - Test /api/crm/pipeline-stats - verify stats vs actual pipeline data
   - Check why pipeline shows empty despite having 8 prospects in stats

3. **Add Prospect Functionality**:
   - Test /api/crm/prospects POST endpoint for adding new prospects
   - Verify the add prospect form submission works

4. **Connection Monitor Inconsistency**:
   - Test /api/google/connection/test-all - check if success rate calculation is accurate
   - Verify service count vs connected count mismatch

Expected Behavior:
- If Google is connected, Gmail/Calendar/Drive should show real data
- CRM prospects should display in pipeline view
- Add prospect functionality should work
- Connection monitor stats should be consistent
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

class AdminPortalGoogleCRMTest:
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
    
    def test_google_gmail_real_messages(self):
        """Test /api/google/gmail/real-messages endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/google/gmail/real-messages")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if we get actual Gmail data
                if isinstance(data, list) and len(data) > 0:
                    # Check for real Gmail message structure
                    first_message = data[0]
                    required_fields = ['id', 'subject', 'sender', 'date']
                    has_required_fields = all(field in first_message for field in required_fields)
                    
                    if has_required_fields:
                        self.log_result("Google Gmail Real Messages", True, 
                                      f"Retrieved {len(data)} Gmail messages with proper structure",
                                      {"message_count": len(data), "sample_message": first_message})
                    else:
                        missing_fields = [field for field in required_fields if field not in first_message]
                        self.log_result("Google Gmail Real Messages", False, 
                                      f"Gmail messages missing required fields: {missing_fields}",
                                      {"first_message": first_message})
                elif isinstance(data, dict) and data.get('auth_required'):
                    self.log_result("Google Gmail Real Messages", False, 
                                  "Gmail API requires authentication - connection not properly established",
                                  {"response": data})
                else:
                    self.log_result("Google Gmail Real Messages", False, 
                                  "No Gmail messages returned or invalid response format",
                                  {"response": data})
            else:
                self.log_result("Google Gmail Real Messages", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Google Gmail Real Messages", False, f"Exception: {str(e)}")
    
    def test_google_calendar_real_events(self):
        """Test /api/google/calendar/real-events endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/google/calendar/real-events")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if we get actual Calendar data
                if isinstance(data, list):
                    if len(data) > 0:
                        # Check for real Calendar event structure
                        first_event = data[0]
                        required_fields = ['id', 'summary', 'start', 'end']
                        has_required_fields = all(field in first_event for field in required_fields)
                        
                        if has_required_fields:
                            self.log_result("Google Calendar Real Events", True, 
                                          f"Retrieved {len(data)} Calendar events with proper structure",
                                          {"event_count": len(data), "sample_event": first_event})
                        else:
                            missing_fields = [field for field in required_fields if field not in first_event]
                            self.log_result("Google Calendar Real Events", False, 
                                          f"Calendar events missing required fields: {missing_fields}",
                                          {"first_event": first_event})
                    else:
                        self.log_result("Google Calendar Real Events", True, 
                                      "No Calendar events found (empty calendar is valid)",
                                      {"event_count": 0})
                elif isinstance(data, dict) and data.get('auth_required'):
                    self.log_result("Google Calendar Real Events", False, 
                                  "Calendar API requires authentication - connection not properly established",
                                  {"response": data})
                else:
                    self.log_result("Google Calendar Real Events", False, 
                                  "Invalid Calendar response format",
                                  {"response": data})
            else:
                self.log_result("Google Calendar Real Events", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Google Calendar Real Events", False, f"Exception: {str(e)}")
    
    def test_google_drive_real_files(self):
        """Test /api/google/drive/real-files endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/google/drive/real-files")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if we get actual Drive data
                if isinstance(data, list) and len(data) > 0:
                    # Check for real Drive file structure
                    first_file = data[0]
                    required_fields = ['id', 'name', 'mimeType']
                    has_required_fields = all(field in first_file for field in required_fields)
                    
                    if has_required_fields:
                        self.log_result("Google Drive Real Files", True, 
                                      f"Retrieved {len(data)} Drive files with proper structure",
                                      {"file_count": len(data), "sample_file": first_file})
                    else:
                        missing_fields = [field for field in required_fields if field not in first_file]
                        self.log_result("Google Drive Real Files", False, 
                                      f"Drive files missing required fields: {missing_fields}",
                                      {"first_file": first_file})
                elif isinstance(data, dict) and data.get('auth_required'):
                    self.log_result("Google Drive Real Files", False, 
                                  "Drive API requires authentication - connection not properly established",
                                  {"response": data})
                else:
                    self.log_result("Google Drive Real Files", False, 
                                  "No Drive files returned or invalid response format",
                                  {"response": data})
            else:
                self.log_result("Google Drive Real Files", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Google Drive Real Files", False, f"Exception: {str(e)}")
    
    def test_crm_prospects_get(self):
        """Test /api/crm/prospects GET endpoint for pipeline display"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    prospect_count = len(data)
                    if prospect_count > 0:
                        # Check prospect structure
                        first_prospect = data[0]
                        required_fields = ['id', 'name', 'email', 'stage']
                        has_required_fields = all(field in first_prospect for field in required_fields)
                        
                        if has_required_fields:
                            # Count prospects by stage
                            stage_counts = {}
                            for prospect in data:
                                stage = prospect.get('stage', 'unknown')
                                stage_counts[stage] = stage_counts.get(stage, 0) + 1
                            
                            self.log_result("CRM Prospects GET", True, 
                                          f"Retrieved {prospect_count} prospects with proper structure",
                                          {"prospect_count": prospect_count, "stage_distribution": stage_counts, "sample_prospect": first_prospect})
                        else:
                            missing_fields = [field for field in required_fields if field not in first_prospect]
                            self.log_result("CRM Prospects GET", False, 
                                          f"Prospects missing required fields: {missing_fields}",
                                          {"first_prospect": first_prospect})
                    else:
                        self.log_result("CRM Prospects GET", False, 
                                      "No prospects found - pipeline should show 8 prospects according to stats",
                                      {"prospect_count": 0})
                else:
                    self.log_result("CRM Prospects GET", False, 
                                  "Invalid prospects response format",
                                  {"response": data})
            else:
                self.log_result("CRM Prospects GET", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("CRM Prospects GET", False, f"Exception: {str(e)}")
    
    def test_crm_pipeline_stats(self):
        """Test /api/crm/pipeline-stats endpoint and verify consistency"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/pipeline-stats")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, dict):
                    # Check for expected stats structure
                    expected_fields = ['total_prospects', 'pipeline_stages', 'conversion_rate']
                    has_expected_fields = any(field in data for field in expected_fields)
                    
                    if has_expected_fields:
                        total_prospects = data.get('total_prospects', 0)
                        
                        # Compare with actual prospects count from previous test
                        prospects_test = next((r for r in self.test_results if r['test'] == 'CRM Prospects GET'), None)
                        if prospects_test and prospects_test['success']:
                            actual_count = prospects_test['details'].get('prospect_count', 0)
                            
                            if total_prospects == actual_count:
                                self.log_result("CRM Pipeline Stats Consistency", True, 
                                              f"Pipeline stats consistent: {total_prospects} prospects match actual count",
                                              {"stats": data, "actual_count": actual_count})
                            else:
                                self.log_result("CRM Pipeline Stats Consistency", False, 
                                              f"Pipeline stats inconsistent: stats show {total_prospects}, actual count is {actual_count}",
                                              {"stats": data, "actual_count": actual_count})
                        else:
                            self.log_result("CRM Pipeline Stats", True, 
                                          f"Pipeline stats retrieved: {total_prospects} total prospects",
                                          {"stats": data})
                    else:
                        self.log_result("CRM Pipeline Stats", False, 
                                      "Pipeline stats missing expected fields",
                                      {"response": data})
                else:
                    self.log_result("CRM Pipeline Stats", False, 
                                  "Invalid pipeline stats response format",
                                  {"response": data})
            else:
                self.log_result("CRM Pipeline Stats", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("CRM Pipeline Stats", False, f"Exception: {str(e)}")
    
    def test_crm_prospects_post(self):
        """Test /api/crm/prospects POST endpoint for adding new prospects"""
        try:
            # Test prospect data
            test_prospect = {
                "name": "Test Prospect Admin Portal",
                "email": "test.prospect@adminportal.com",
                "phone": "+1-555-0123",
                "notes": "Test prospect created during admin portal testing"
            }
            
            response = self.session.post(f"{BACKEND_URL}/crm/prospects", json=test_prospect)
            
            if response.status_code == 201 or response.status_code == 200:
                data = response.json()
                
                if isinstance(data, dict) and 'id' in data:
                    # Verify the created prospect has correct data
                    created_prospect = data
                    data_correct = True
                    issues = []
                    
                    for key, expected_value in test_prospect.items():
                        actual_value = created_prospect.get(key)
                        if actual_value != expected_value:
                            data_correct = False
                            issues.append(f"{key}: expected '{expected_value}', got '{actual_value}'")
                    
                    if data_correct:
                        self.log_result("CRM Prospects POST", True, 
                                      f"Successfully created prospect: {created_prospect.get('name')}",
                                      {"created_prospect": created_prospect})
                    else:
                        self.log_result("CRM Prospects POST", False, 
                                      "Prospect created but data incorrect",
                                      {"issues": issues, "created_prospect": created_prospect})
                else:
                    self.log_result("CRM Prospects POST", False, 
                                  "Invalid prospect creation response",
                                  {"response": data})
            else:
                self.log_result("CRM Prospects POST", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("CRM Prospects POST", False, f"Exception: {str(e)}")
    
    def test_google_connection_test_all(self):
        """Test /api/google/connection/test-all endpoint for connection monitoring"""
        try:
            response = self.session.get(f"{BACKEND_URL}/google/connection/test-all")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, dict):
                    # Check for expected connection monitor structure
                    expected_fields = ['overall_status', 'services', 'connection_quality']
                    has_expected_fields = all(field in data for field in expected_fields)
                    
                    if has_expected_fields:
                        overall_status = data.get('overall_status')
                        services = data.get('services', {})
                        connection_quality = data.get('connection_quality', {})
                        
                        # Check service count vs connected count
                        total_services = len(services)
                        connected_services = sum(1 for service_data in services.values() 
                                               if isinstance(service_data, dict) and service_data.get('status') == 'connected')
                        
                        success_rate = connection_quality.get('success_rate', 0)
                        
                        # Verify consistency
                        if total_services > 0:
                            expected_success_rate = (connected_services / total_services) * 100
                            rate_difference = abs(success_rate - expected_success_rate)
                            
                            if rate_difference < 5:  # Allow 5% tolerance
                                self.log_result("Google Connection Monitor Consistency", True, 
                                              f"Connection stats consistent: {connected_services}/{total_services} services connected, {success_rate}% success rate",
                                              {"services": services, "connection_quality": connection_quality})
                            else:
                                self.log_result("Google Connection Monitor Consistency", False, 
                                              f"Connection stats inconsistent: {connected_services}/{total_services} connected but {success_rate}% success rate",
                                              {"expected_rate": expected_success_rate, "actual_rate": success_rate, "services": services})
                        else:
                            self.log_result("Google Connection Monitor", True, 
                                          "Connection monitor responding with valid structure",
                                          {"data": data})
                    else:
                        missing_fields = [field for field in expected_fields if field not in data]
                        self.log_result("Google Connection Monitor", False, 
                                      f"Connection monitor missing expected fields: {missing_fields}",
                                      {"response": data})
                else:
                    self.log_result("Google Connection Monitor", False, 
                                  "Invalid connection monitor response format",
                                  {"response": data})
            else:
                self.log_result("Google Connection Monitor", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Google Connection Monitor", False, f"Exception: {str(e)}")
    
    def test_google_connection_individual_services(self):
        """Test individual Google service connection endpoints"""
        services = ['gmail', 'calendar', 'drive', 'meet']
        
        for service in services:
            try:
                response = self.session.get(f"{BACKEND_URL}/google/connection/test/{service}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if isinstance(data, dict):
                        status = data.get('status')
                        response_time = data.get('response_time')
                        
                        if status and response_time is not None:
                            self.log_result(f"Google {service.title()} Connection", True, 
                                          f"{service.title()} service connection test: {status} ({response_time}ms)",
                                          {"service_data": data})
                        else:
                            self.log_result(f"Google {service.title()} Connection", False, 
                                          f"{service.title()} service response missing status or response_time",
                                          {"response": data})
                    else:
                        self.log_result(f"Google {service.title()} Connection", False, 
                                      f"Invalid {service} service response format",
                                      {"response": data})
                else:
                    self.log_result(f"Google {service.title()} Connection", False, 
                                  f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_result(f"Google {service.title()} Connection", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all admin portal Google Workspace and CRM tests"""
        print("🎯 ADMIN PORTAL GOOGLE WORKSPACE AND CRM FUNCTIONALITY TEST")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Testing Google Workspace Data Loading...")
        print("-" * 50)
        self.test_google_gmail_real_messages()
        self.test_google_calendar_real_events()
        self.test_google_drive_real_files()
        
        print("\n🔍 Testing CRM Pipeline Functionality...")
        print("-" * 50)
        self.test_crm_prospects_get()
        self.test_crm_pipeline_stats()
        self.test_crm_prospects_post()
        
        print("\n🔍 Testing Google Connection Monitor...")
        print("-" * 50)
        self.test_google_connection_test_all()
        self.test_google_connection_individual_services()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 70)
        print("🎯 ADMIN PORTAL GOOGLE WORKSPACE AND CRM TEST SUMMARY")
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
        
        # Categorize results
        google_workspace_tests = [r for r in self.test_results if 'Google' in r['test'] and 'Connection' not in r['test']]
        crm_tests = [r for r in self.test_results if 'CRM' in r['test']]
        connection_tests = [r for r in self.test_results if 'Connection' in r['test']]
        
        # Google Workspace Data Loading Results
        print("📧 GOOGLE WORKSPACE DATA LOADING RESULTS:")
        google_passed = sum(1 for r in google_workspace_tests if r['success'])
        google_total = len(google_workspace_tests)
        print(f"   Passed: {google_passed}/{google_total}")
        
        for result in google_workspace_tests:
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {result['test']}: {result['message']}")
        print()
        
        # CRM Pipeline Results
        print("📊 CRM PIPELINE FUNCTIONALITY RESULTS:")
        crm_passed = sum(1 for r in crm_tests if r['success'])
        crm_total = len(crm_tests)
        print(f"   Passed: {crm_passed}/{crm_total}")
        
        for result in crm_tests:
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {result['test']}: {result['message']}")
        print()
        
        # Connection Monitor Results
        print("🔗 GOOGLE CONNECTION MONITOR RESULTS:")
        connection_passed = sum(1 for r in connection_tests if r['success'])
        connection_total = len(connection_tests)
        print(f"   Passed: {connection_passed}/{connection_total}")
        
        for result in connection_tests:
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {result['test']}: {result['message']}")
        print()
        
        # Critical Issues Analysis
        print("🚨 CRITICAL ISSUES ANALYSIS:")
        critical_failures = []
        
        # Check for specific issues mentioned in review request
        gmail_test = next((r for r in self.test_results if 'Gmail Real Messages' in r['test']), None)
        if gmail_test and not gmail_test['success']:
            critical_failures.append("Gmail data not loading despite connection")
        
        prospects_test = next((r for r in self.test_results if 'CRM Prospects GET' in r['test']), None)
        if prospects_test and not prospects_test['success']:
            critical_failures.append("CRM prospects not displaying in pipeline")
        
        stats_test = next((r for r in self.test_results if 'Pipeline Stats Consistency' in r['test']), None)
        if stats_test and not stats_test['success']:
            critical_failures.append("Pipeline stats inconsistent with actual data")
        
        add_prospect_test = next((r for r in self.test_results if 'CRM Prospects POST' in r['test']), None)
        if add_prospect_test and not add_prospect_test['success']:
            critical_failures.append("Add prospect functionality not working")
        
        connection_consistency_test = next((r for r in self.test_results if 'Connection Monitor Consistency' in r['test']), None)
        if connection_consistency_test and not connection_consistency_test['success']:
            critical_failures.append("Connection monitor stats inconsistent")
        
        if critical_failures:
            print("❌ CRITICAL FAILURES IDENTIFIED:")
            for failure in critical_failures:
                print(f"   • {failure}")
            print("\n   These issues match the user's reported problems and require immediate attention.")
        else:
            print("✅ NO CRITICAL FAILURES - All reported issues appear to be resolved")
        
        print("\n" + "=" * 70)

def main():
    """Main test execution"""
    test_runner = AdminPortalGoogleCRMTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()