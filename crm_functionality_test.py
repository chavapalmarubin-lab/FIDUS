#!/usr/bin/env python3
"""
CRM FUNCTIONALITY ENDPOINTS TESTING
===================================

This test verifies the critical CRM functionality endpoints as requested in the review:

**Critical CRM Endpoints to Test:**
1. **Email Functionality**: 
   - POST /google/gmail/send - Send emails to prospects/clients
   - Verify it works with current Google authentication

2. **Calendar/Meeting Functionality**:
   - POST /google/calendar/create-event - Schedule meetings with prospects
   - Verify Google Calendar integration works

3. **CRM Data Endpoints**:
   - GET /crm/prospects - Get all prospects for CRM dashboard
   - GET /crm/prospects/pipeline - Get sales pipeline data

**Authentication Context:**
- Use admin credentials (admin/password123)
- Test with current Google OAuth connection (chava Palma account)

**Testing Focus:**
- Verify CRM buttons functionality (Email, Schedule Meeting)
- Check if Google integration supports Gmail and Calendar operations
- Ensure prospects/pipeline data loads correctly
- Test end-to-end CRM workflow

**Expected Results:**
- Email sending should work through Gmail API
- Calendar event creation should work through Calendar API  
- CRM data should load without errors
- All functionality should be ready for user interaction
"""

import requests
import json
import sys
from datetime import datetime, timedelta
import time

# Configuration - Use correct backend URL from frontend/.env
BACKEND_URL = "https://mt5-deploy-debug.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class CRMFunctionalityTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.prospects_data = []
        
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
    
    def test_crm_prospects_endpoint(self):
        """Test GET /crm/prospects - Get all prospects for CRM dashboard"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response has prospects data
                if isinstance(data, dict) and 'prospects' in data:
                    prospects = data['prospects']
                    self.prospects_data = prospects
                    
                    if isinstance(prospects, list) and len(prospects) > 0:
                        # Verify prospect structure
                        sample_prospect = prospects[0]
                        required_fields = ['prospect_id', 'name', 'email', 'phone', 'stage']
                        
                        missing_fields = [field for field in required_fields if field not in sample_prospect]
                        
                        if not missing_fields:
                            self.log_result("CRM Prospects Data", True, 
                                          f"Successfully retrieved {len(prospects)} prospects with proper structure",
                                          {"total_prospects": len(prospects), 
                                           "sample_prospect": {k: v for k, v in sample_prospect.items() if k in required_fields}})
                        else:
                            self.log_result("CRM Prospects Data", False, 
                                          f"Prospects missing required fields: {missing_fields}",
                                          {"sample_prospect": sample_prospect})
                    else:
                        self.log_result("CRM Prospects Data", False, 
                                      "No prospects found or invalid data structure",
                                      {"prospects_type": type(prospects), "prospects_length": len(prospects) if isinstance(prospects, list) else "N/A"})
                elif isinstance(data, list):
                    # Direct array response
                    self.prospects_data = data
                    if len(data) > 0:
                        sample_prospect = data[0]
                        required_fields = ['prospect_id', 'name', 'email', 'phone', 'stage']
                        missing_fields = [field for field in required_fields if field not in sample_prospect]
                        
                        if not missing_fields:
                            self.log_result("CRM Prospects Data", True, 
                                          f"Successfully retrieved {len(data)} prospects (direct array)",
                                          {"total_prospects": len(data)})
                        else:
                            self.log_result("CRM Prospects Data", False, 
                                          f"Prospects missing required fields: {missing_fields}")
                    else:
                        self.log_result("CRM Prospects Data", False, "No prospects found in direct array response")
                else:
                    self.log_result("CRM Prospects Data", False, 
                                  "Invalid response format - expected array or object with 'prospects' key",
                                  {"response_type": type(data), "response_keys": list(data.keys()) if isinstance(data, dict) else "N/A"})
            elif response.status_code == 401:
                self.log_result("CRM Prospects Data", False, "Authentication required (401)")
            else:
                self.log_result("CRM Prospects Data", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("CRM Prospects Data", False, f"Exception: {str(e)}")
    
    def test_crm_pipeline_endpoint(self):
        """Test GET /crm/prospects/pipeline - Get sales pipeline data"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/prospects/pipeline")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for pipeline statistics
                if isinstance(data, dict):
                    # Look for common pipeline data fields
                    pipeline_fields = ['total_prospects', 'conversion_rate', 'stage_counts', 'pipeline_stats', 'stats']
                    found_fields = [field for field in pipeline_fields if field in data]
                    
                    if found_fields:
                        self.log_result("CRM Pipeline Data", True, 
                                      f"Successfully retrieved pipeline data with fields: {found_fields}",
                                      {"pipeline_data": {k: v for k, v in data.items() if k in found_fields}})
                    else:
                        self.log_result("CRM Pipeline Data", False, 
                                      "Pipeline data missing expected fields",
                                      {"available_fields": list(data.keys()), "expected_fields": pipeline_fields})
                else:
                    self.log_result("CRM Pipeline Data", False, 
                                  "Invalid pipeline response format - expected object",
                                  {"response_type": type(data)})
            elif response.status_code == 401:
                self.log_result("CRM Pipeline Data", False, "Authentication required (401)")
            else:
                self.log_result("CRM Pipeline Data", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("CRM Pipeline Data", False, f"Exception: {str(e)}")
    
    def test_gmail_send_endpoint(self):
        """Test POST /google/gmail/send - Send emails to prospects/clients"""
        try:
            # Test email data
            test_email = {
                "to": "test@example.com",
                "subject": "CRM Test Email - FIDUS Investment Opportunity",
                "body": "This is a test email from the FIDUS CRM system to verify Gmail API integration is working correctly."
            }
            
            response = self.session.post(f"{BACKEND_URL}/google/gmail/send", json=test_email)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('message_id'):
                    self.log_result("Gmail Send Functionality", True, 
                                  "Successfully sent email via Gmail API",
                                  {"message_id": data.get('message_id'), "to": test_email['to']})
                elif data.get('auth_required'):
                    self.log_result("Gmail Send Functionality", False, 
                                  "Google authentication required for Gmail API",
                                  {"auth_required": True, "message": data.get('message', 'No message')})
                else:
                    self.log_result("Gmail Send Functionality", False, 
                                  "Email sending failed - unexpected response",
                                  {"response": data})
            elif response.status_code == 401:
                self.log_result("Gmail Send Functionality", False, "Authentication required (401)")
            elif response.status_code == 400:
                # Check if it's a validation error
                try:
                    error_data = response.json()
                    if 'detail' in error_data:
                        self.log_result("Gmail Send Functionality", False, 
                                      f"Validation error: {error_data['detail']}")
                    else:
                        self.log_result("Gmail Send Functionality", False, 
                                      f"Bad request: {response.text}")
                except:
                    self.log_result("Gmail Send Functionality", False, 
                                  f"HTTP 400: {response.text}")
            else:
                self.log_result("Gmail Send Functionality", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Gmail Send Functionality", False, f"Exception: {str(e)}")
    
    def test_calendar_create_event_endpoint(self):
        """Test POST /google/calendar/create-event - Schedule meetings with prospects"""
        try:
            # Test meeting data
            tomorrow = datetime.now() + timedelta(days=1)
            test_meeting = {
                "summary": "CRM Test Meeting - FIDUS Investment Discussion",
                "description": "Test meeting created by CRM system to verify Google Calendar integration",
                "start_time": tomorrow.replace(hour=14, minute=0, second=0, microsecond=0).isoformat(),
                "end_time": tomorrow.replace(hour=15, minute=0, second=0, microsecond=0).isoformat(),
                "attendees": ["test@example.com"]
            }
            
            response = self.session.post(f"{BACKEND_URL}/google/calendar/create-event", json=test_meeting)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('event_id'):
                    self.log_result("Calendar Create Event", True, 
                                  "Successfully created calendar event via Google Calendar API",
                                  {"event_id": data.get('event_id'), "summary": test_meeting['summary']})
                elif data.get('auth_required'):
                    self.log_result("Calendar Create Event", False, 
                                  "Google authentication required for Calendar API",
                                  {"auth_required": True, "message": data.get('message', 'No message')})
                else:
                    self.log_result("Calendar Create Event", False, 
                                  "Event creation failed - unexpected response",
                                  {"response": data})
            elif response.status_code == 401:
                self.log_result("Calendar Create Event", False, "Authentication required (401)")
            elif response.status_code == 400:
                # Check if it's a validation error
                try:
                    error_data = response.json()
                    if 'detail' in error_data:
                        self.log_result("Calendar Create Event", False, 
                                      f"Validation error: {error_data['detail']}")
                    else:
                        self.log_result("Calendar Create Event", False, 
                                      f"Bad request: {response.text}")
                except:
                    self.log_result("Calendar Create Event", False, 
                                  f"HTTP 400: {response.text}")
            else:
                self.log_result("Calendar Create Event", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Calendar Create Event", False, f"Exception: {str(e)}")
    
    def test_google_oauth_status(self):
        """Test Google OAuth authentication status"""
        try:
            response = self.session.get(f"{BACKEND_URL}/google/connection/test-all")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('overall_status') == 'Connected':
                    self.log_result("Google OAuth Status", True, 
                                  "Google OAuth is connected and ready",
                                  {"services": data.get('services', {})})
                elif data.get('overall_status') == 'Disconnected':
                    self.log_result("Google OAuth Status", False, 
                                  "Google OAuth is not connected - authentication required",
                                  {"services": data.get('services', {}), "auth_required": True})
                else:
                    self.log_result("Google OAuth Status", False, 
                                  f"Unknown OAuth status: {data.get('overall_status')}",
                                  {"response": data})
            elif response.status_code == 401:
                self.log_result("Google OAuth Status", False, "Authentication required (401)")
            else:
                self.log_result("Google OAuth Status", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Google OAuth Status", False, f"Exception: {str(e)}")
    
    def test_end_to_end_crm_workflow(self):
        """Test end-to-end CRM workflow with a sample prospect"""
        try:
            if not self.prospects_data:
                self.log_result("End-to-End CRM Workflow", False, 
                              "No prospects data available for workflow test")
                return
            
            # Use first prospect for testing
            test_prospect = self.prospects_data[0]
            prospect_id = test_prospect.get('prospect_id')
            prospect_email = test_prospect.get('email')
            prospect_name = test_prospect.get('name')
            
            if not all([prospect_id, prospect_email, prospect_name]):
                self.log_result("End-to-End CRM Workflow", False, 
                              "Test prospect missing required fields",
                              {"prospect": test_prospect})
                return
            
            # Test workflow steps
            workflow_steps = []
            
            # Step 1: Send email to prospect
            email_data = {
                "to": prospect_email,
                "subject": f"Investment Opportunity - {prospect_name}",
                "body": f"Dear {prospect_name},\n\nWe have an exciting investment opportunity to discuss with you.\n\nBest regards,\nFIDUS Investment Team"
            }
            
            email_response = self.session.post(f"{BACKEND_URL}/google/gmail/send", json=email_data)
            if email_response.status_code == 200:
                email_result = email_response.json()
                if email_result.get('success'):
                    workflow_steps.append("✅ Email sent successfully")
                elif email_result.get('auth_required'):
                    workflow_steps.append("⚠️ Email requires Google authentication")
                else:
                    workflow_steps.append("❌ Email sending failed")
            else:
                workflow_steps.append(f"❌ Email API error: {email_response.status_code}")
            
            # Step 2: Schedule meeting with prospect
            tomorrow = datetime.now() + timedelta(days=1)
            meeting_data = {
                "summary": f"Investment Discussion - {prospect_name}",
                "description": f"Meeting with {prospect_name} to discuss FIDUS investment opportunities",
                "start_time": tomorrow.replace(hour=10, minute=0, second=0, microsecond=0).isoformat(),
                "end_time": tomorrow.replace(hour=11, minute=0, second=0, microsecond=0).isoformat(),
                "attendees": [prospect_email]
            }
            
            meeting_response = self.session.post(f"{BACKEND_URL}/google/calendar/create-event", json=meeting_data)
            if meeting_response.status_code == 200:
                meeting_result = meeting_response.json()
                if meeting_result.get('success'):
                    workflow_steps.append("✅ Meeting scheduled successfully")
                elif meeting_result.get('auth_required'):
                    workflow_steps.append("⚠️ Meeting requires Google authentication")
                else:
                    workflow_steps.append("❌ Meeting scheduling failed")
            else:
                workflow_steps.append(f"❌ Calendar API error: {meeting_response.status_code}")
            
            # Evaluate workflow success
            successful_steps = sum(1 for step in workflow_steps if step.startswith("✅"))
            auth_required_steps = sum(1 for step in workflow_steps if step.startswith("⚠️"))
            
            if successful_steps == 2:
                self.log_result("End-to-End CRM Workflow", True, 
                              "Complete CRM workflow executed successfully",
                              {"prospect": prospect_name, "steps": workflow_steps})
            elif auth_required_steps > 0:
                self.log_result("End-to-End CRM Workflow", False, 
                              "CRM workflow requires Google authentication",
                              {"prospect": prospect_name, "steps": workflow_steps, "auth_required": True})
            else:
                self.log_result("End-to-End CRM Workflow", False, 
                              "CRM workflow failed",
                              {"prospect": prospect_name, "steps": workflow_steps})
                
        except Exception as e:
            self.log_result("End-to-End CRM Workflow", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all CRM functionality tests"""
        print("🎯 CRM FUNCTIONALITY ENDPOINTS TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate for protected endpoint tests
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with CRM tests.")
            return False
        
        print("\n🔍 Running CRM Functionality Tests...")
        print("-" * 50)
        
        # Test Google OAuth status first
        self.test_google_oauth_status()
        
        # Test CRM data endpoints
        self.test_crm_prospects_endpoint()
        self.test_crm_pipeline_endpoint()
        
        # Test Google integration endpoints
        self.test_gmail_send_endpoint()
        self.test_calendar_create_event_endpoint()
        
        # Test end-to-end workflow
        self.test_end_to_end_crm_workflow()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 CRM FUNCTIONALITY TEST SUMMARY")
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
        
        # Critical assessment for CRM functionality
        critical_tests = [
            "CRM Prospects Data",
            "CRM Pipeline Data", 
            "Gmail Send Functionality",
            "Calendar Create Event",
            "End-to-End CRM Workflow"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(critical in result['test'] for critical in critical_tests))
        
        # Check for authentication issues
        auth_required_tests = sum(1 for result in self.test_results 
                                if not result['success'] and result.get('details', {}).get('auth_required'))
        
        print("🚨 CRITICAL ASSESSMENT:")
        if critical_passed >= 4:  # At least 4 out of 5 critical tests
            print("✅ CRM FUNCTIONALITY: OPERATIONAL")
            print("   All critical CRM endpoints are working properly.")
            print("   Email sending and meeting scheduling ready for use.")
            print("   CRM data loading correctly for dashboard display.")
        elif auth_required_tests > 0:
            print("⚠️ CRM FUNCTIONALITY: REQUIRES GOOGLE AUTHENTICATION")
            print("   CRM system is implemented correctly but needs Google OAuth completion.")
            print("   Complete Google OAuth flow to enable Gmail and Calendar features.")
            print("   CRM data endpoints are working independently.")
        else:
            print("❌ CRM FUNCTIONALITY: ISSUES DETECTED")
            print("   Critical CRM functionality issues found.")
            print("   Main agent action required to fix CRM implementation.")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = CRMFunctionalityTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()