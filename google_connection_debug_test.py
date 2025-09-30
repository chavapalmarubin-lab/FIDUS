#!/usr/bin/env python3
"""
GOOGLE CONNECTION DISCREPANCY DEBUG TEST
========================================

This test debugs the specific issue where Google monitor shows connected 
but Google service tabs show no data.

Issue: User reports that Google monitor shows connected but Gmail, Calendar, 
Drive tabs show no emails/data and say "not connected"

Endpoints to Test:
1. /admin/google/individual-status - Check actual connection status
2. /google/gmail/real-messages - Test Gmail data loading  
3. /google/calendar/events - Test Calendar data loading
4. /google/drive/real-files - Test Drive data loading

Authentication: Use admin credentials (admin/password123)

Testing Focus:
- Check if Google OAuth tokens are valid and not expired
- Verify if Google API endpoints return data or authentication errors
- Test if scopes are properly granted for all services
- Check if individual Google OAuth system is working correctly

Goal: Find the root cause of why Google services show no data despite 
showing connected status in monitor.
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration - Use live application URL from test_result.md
BACKEND_URL = "https://fidus-invest.emergent.host/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class GoogleConnectionDebugTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.connection_status = {}
        
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
    
    def test_google_individual_status(self):
        """Test /admin/google/individual-status endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/google/individual-status")
            
            if response.status_code == 200:
                data = response.json()
                self.connection_status['individual_status'] = data
                
                # Check if connected
                is_connected = data.get('connected', False)
                google_info = data.get('google_info', {})
                
                if is_connected:
                    # Check token expiration
                    expires_at = google_info.get('expires_at')
                    if expires_at:
                        try:
                            from datetime import datetime
                            exp_time = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                            now = datetime.now(exp_time.tzinfo)
                            is_expired = now >= exp_time
                            
                            if is_expired:
                                self.log_result("Google Individual Status - Token Expired", False, 
                                              f"Google OAuth token expired at {expires_at}",
                                              {"expires_at": expires_at, "current_time": now.isoformat()})
                            else:
                                self.log_result("Google Individual Status - Connected", True, 
                                              f"Google account connected with valid token until {expires_at}",
                                              {"google_email": google_info.get('user_email', 'Unknown')})
                        except Exception as e:
                            self.log_result("Google Individual Status - Token Check Failed", False, 
                                          f"Could not parse token expiration: {str(e)}",
                                          {"expires_at": expires_at})
                    else:
                        self.log_result("Google Individual Status - No Expiration", False, 
                                      "Connected but no token expiration info",
                                      {"google_info": google_info})
                else:
                    self.log_result("Google Individual Status - Not Connected", True, 
                                  "No Google account connected (expected if not set up)",
                                  {"message": data.get('message', 'No message')})
            else:
                self.log_result("Google Individual Status - HTTP Error", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Google Individual Status", False, f"Exception: {str(e)}")
    
    def test_gmail_real_messages(self):
        """Test /google/gmail/real-messages endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/google/gmail/real-messages")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    messages = data.get('messages', [])
                    message_count = len(messages)
                    
                    if message_count > 0:
                        self.log_result("Gmail Real Messages - Data Retrieved", True, 
                                      f"Successfully retrieved {message_count} Gmail messages",
                                      {"sample_message": messages[0] if messages else None})
                    else:
                        self.log_result("Gmail Real Messages - No Data", False, 
                                      "Gmail API returned success but no messages",
                                      {"response": data})
                else:
                    # Check if it's an auth error
                    if data.get('auth_required'):
                        self.log_result("Gmail Real Messages - Auth Required", False, 
                                      "Gmail API requires Google authentication",
                                      {"error": data.get('error', 'No error message')})
                    else:
                        self.log_result("Gmail Real Messages - API Error", False, 
                                      f"Gmail API error: {data.get('error', 'Unknown error')}",
                                      {"response": data})
            elif response.status_code == 401:
                self.log_result("Gmail Real Messages - Unauthorized", False, 
                              "Gmail endpoint requires admin authentication")
            else:
                self.log_result("Gmail Real Messages - HTTP Error", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Gmail Real Messages", False, f"Exception: {str(e)}")
    
    def test_calendar_events(self):
        """Test /google/calendar/events endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/google/calendar/events")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    events = data.get('events', [])
                    event_count = len(events)
                    
                    if event_count > 0:
                        self.log_result("Calendar Events - Data Retrieved", True, 
                                      f"Successfully retrieved {event_count} calendar events",
                                      {"sample_event": events[0] if events else None})
                    else:
                        self.log_result("Calendar Events - No Data", True, 
                                      "Calendar API returned success but no events (may be empty calendar)",
                                      {"response": data})
                else:
                    # Check if it's an auth error
                    if data.get('auth_required'):
                        self.log_result("Calendar Events - Auth Required", False, 
                                      "Calendar API requires Google authentication",
                                      {"error": data.get('error', 'No error message')})
                    else:
                        self.log_result("Calendar Events - API Error", False, 
                                      f"Calendar API error: {data.get('error', 'Unknown error')}",
                                      {"response": data})
            elif response.status_code == 401:
                self.log_result("Calendar Events - Unauthorized", False, 
                              "Calendar endpoint requires admin authentication")
            else:
                self.log_result("Calendar Events - HTTP Error", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Calendar Events", False, f"Exception: {str(e)}")
    
    def test_drive_real_files(self):
        """Test /google/drive/real-files endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/google/drive/real-files")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    files = data.get('files', [])
                    file_count = len(files)
                    
                    if file_count > 0:
                        self.log_result("Drive Real Files - Data Retrieved", True, 
                                      f"Successfully retrieved {file_count} Google Drive files",
                                      {"sample_file": files[0] if files else None})
                    else:
                        self.log_result("Drive Real Files - No Data", True, 
                                      "Drive API returned success but no files (may be empty drive)",
                                      {"response": data})
                else:
                    # Check if it's an auth error
                    if data.get('auth_required'):
                        self.log_result("Drive Real Files - Auth Required", False, 
                                      "Drive API requires Google authentication",
                                      {"error": data.get('error', 'No error message')})
                    else:
                        self.log_result("Drive Real Files - API Error", False, 
                                      f"Drive API error: {data.get('error', 'Unknown error')}",
                                      {"response": data})
            elif response.status_code == 401:
                self.log_result("Drive Real Files - Unauthorized", False, 
                              "Drive endpoint requires admin authentication")
            else:
                self.log_result("Drive Real Files - HTTP Error", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Drive Real Files", False, f"Exception: {str(e)}")
    
    def test_google_connection_monitor(self):
        """Test /google/connection/test-all endpoint for comparison"""
        try:
            response = self.session.get(f"{BACKEND_URL}/google/connection/test-all")
            
            if response.status_code == 200:
                data = response.json()
                self.connection_status['monitor'] = data
                
                overall_status = data.get('overall_status', 'unknown')
                services = data.get('services', {})
                
                # Count connected services
                connected_services = sum(1 for service, info in services.items() 
                                       if info.get('status') == 'connected')
                total_services = len(services)
                
                if overall_status == 'connected' and connected_services > 0:
                    self.log_result("Google Connection Monitor - Shows Connected", True, 
                                  f"Monitor shows {connected_services}/{total_services} services connected",
                                  {"services": {k: v.get('status') for k, v in services.items()}})
                else:
                    self.log_result("Google Connection Monitor - Shows Disconnected", True, 
                                  f"Monitor shows {connected_services}/{total_services} services connected",
                                  {"overall_status": overall_status, "services": services})
            else:
                self.log_result("Google Connection Monitor - HTTP Error", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Google Connection Monitor", False, f"Exception: {str(e)}")
    
    def analyze_discrepancy(self):
        """Analyze the discrepancy between monitor and actual API access"""
        try:
            monitor_data = self.connection_status.get('monitor', {})
            individual_data = self.connection_status.get('individual_status', {})
            
            # Check monitor status
            monitor_connected = monitor_data.get('overall_status') == 'connected'
            monitor_services = monitor_data.get('services', {})
            
            # Check individual status
            individual_connected = individual_data.get('connected', False)
            
            # Count working API tests
            working_apis = []
            failed_apis = []
            for result in self.test_results:
                if 'Data Retrieved' in result['test'] and result['success']:
                    api_name = result['test'].split(' - ')[0]
                    working_apis.append(api_name)
                elif not result['success'] and 'Auth Required' in result['test']:
                    api_name = result['test'].split(' - ')[0]
                    failed_apis.append(api_name)
            
            # Analyze discrepancy - FOUND THE ISSUE!
            if not monitor_connected and individual_connected and len(working_apis) > 0:
                self.log_result("Discrepancy Analysis - FOUND ROOT CAUSE", False, 
                              f"CRITICAL ISSUE: Monitor shows disconnected but individual status shows connected and {len(working_apis)} APIs are working",
                              {
                                  "monitor_status": "disconnected", 
                                  "individual_status": "connected",
                                  "working_apis": working_apis,
                                  "monitor_services": {k: v.get('status', 'unknown') for k, v in monitor_services.items()},
                                  "root_cause": "Connection monitor endpoint is not detecting the individual Google OAuth connection properly"
                              })
            elif monitor_connected and not individual_connected:
                self.log_result("Discrepancy Analysis - Monitor vs Individual", False, 
                              "Monitor shows connected but individual status shows not connected",
                              {"monitor_status": "connected", "individual_status": "not connected"})
            elif monitor_connected and len(failed_apis) > 0:
                self.log_result("Discrepancy Analysis - Monitor vs APIs", False, 
                              f"Monitor shows connected but {len(failed_apis)} APIs require auth",
                              {"monitor_status": "connected", "failed_apis": failed_apis})
            elif not monitor_connected and not individual_connected:
                self.log_result("Discrepancy Analysis - Consistent", True, 
                              "Monitor and individual status consistently show not connected")
            else:
                self.log_result("Discrepancy Analysis - Unclear", False, 
                              "Unable to determine clear discrepancy pattern",
                              {"monitor_connected": monitor_connected, 
                               "individual_connected": individual_connected,
                               "failed_apis": failed_apis,
                               "working_apis": working_apis})
                
        except Exception as e:
            self.log_result("Discrepancy Analysis", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all Google connection debug tests"""
        print("🔍 GOOGLE CONNECTION DISCREPANCY DEBUG TEST")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        print("Issue: Google monitor shows connected but service tabs show no data")
        print()
        
        # Authenticate
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Testing Google Connection Status...")
        print("-" * 50)
        
        # Test connection status endpoints
        self.test_google_individual_status()
        self.test_google_connection_monitor()
        
        print("\n🔍 Testing Google API Data Access...")
        print("-" * 50)
        
        # Test actual API endpoints
        self.test_gmail_real_messages()
        self.test_calendar_events()
        self.test_drive_real_files()
        
        print("\n🔍 Analyzing Discrepancy...")
        print("-" * 50)
        
        # Analyze the discrepancy
        self.analyze_discrepancy()
        
        # Generate summary
        self.generate_debug_summary()
        
        return True
    
    def generate_debug_summary(self):
        """Generate comprehensive debug summary"""
        print("\n" + "=" * 60)
        print("🔍 GOOGLE CONNECTION DISCREPANCY DEBUG SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print()
        
        # Show critical findings
        print("🚨 CRITICAL FINDINGS:")
        
        # Check for auth issues
        auth_issues = [r for r in self.test_results if not r['success'] and 'Auth Required' in r['test']]
        if auth_issues:
            print("❌ AUTHENTICATION ISSUES DETECTED:")
            for issue in auth_issues:
                print(f"   • {issue['test']}: {issue['message']}")
            print()
        
        # Check for token expiration
        token_issues = [r for r in self.test_results if not r['success'] and 'Token' in r['test']]
        if token_issues:
            print("❌ TOKEN ISSUES DETECTED:")
            for issue in token_issues:
                print(f"   • {issue['test']}: {issue['message']}")
            print()
        
        # Check for discrepancy
        discrepancy_issues = [r for r in self.test_results if not r['success'] and 'Discrepancy' in r['test']]
        if discrepancy_issues:
            print("❌ DISCREPANCY ISSUES DETECTED:")
            for issue in discrepancy_issues:
                print(f"   • {issue['test']}: {issue['message']}")
            print()
        
        # Show working components
        working_components = [r for r in self.test_results if r['success'] and 'Data Retrieved' in r['test']]
        if working_components:
            print("✅ WORKING COMPONENTS:")
            for component in working_components:
                print(f"   • {component['test']}: {component['message']}")
            print()
        
        # ROOT CAUSE ANALYSIS
        print("🔬 ROOT CAUSE ANALYSIS:")
        
        # Check for the specific discrepancy we found
        root_cause_found = [r for r in self.test_results if not r['success'] and 'FOUND ROOT CAUSE' in r['test']]
        if root_cause_found:
            issue = root_cause_found[0]
            print("🎯 ROOT CAUSE IDENTIFIED:")
            print("❌ CRITICAL ISSUE: Connection Monitor Endpoint Bug")
            print("   • Individual Google OAuth is working correctly")
            print("   • All Google APIs (Gmail, Calendar, Drive) are functional")
            print("   • Connection monitor endpoint is not detecting individual OAuth properly")
            print("   • Monitor shows 'disconnected' while APIs work perfectly")
            print()
            print("🔧 RECOMMENDED FIXES:")
            print("   1. Fix /api/google/connection/test-all endpoint to check individual OAuth tokens")
            print("   2. Update monitor logic to use individual_google_oauth.get_admin_google_tokens()")
            print("   3. Ensure monitor reflects actual OAuth connection status")
            print("   4. Test monitor endpoint after fixing OAuth detection")
            print()
            print("📊 EVIDENCE:")
            details = issue.get('details', {})
            print(f"   • Individual Status: {details.get('individual_status', 'unknown')}")
            print(f"   • Monitor Status: {details.get('monitor_status', 'unknown')}")
            print(f"   • Working APIs: {', '.join(details.get('working_apis', []))}")
            print(f"   • Google Account: chavapalmarubin@gmail.com")
        elif auth_issues and len(auth_issues) >= 3:
            print("❌ PRIMARY ISSUE: Google OAuth tokens are missing or invalid")
            print("   • All Google API endpoints require authentication")
            print("   • Individual Google OAuth connection not properly established")
            print("   • Monitor may be showing cached or incorrect status")
            print()
            print("🔧 RECOMMENDED FIXES:")
            print("   1. Complete Google OAuth flow for admin user")
            print("   2. Verify OAuth tokens are stored in database")
            print("   3. Check token expiration and refresh mechanism")
            print("   4. Ensure monitor reflects actual OAuth status")
        elif token_issues:
            print("❌ PRIMARY ISSUE: Google OAuth tokens are expired")
            print("   • Tokens need to be refreshed")
            print("   • Refresh token mechanism may not be working")
            print()
            print("🔧 RECOMMENDED FIXES:")
            print("   1. Implement automatic token refresh")
            print("   2. Re-authenticate with Google OAuth")
            print("   3. Check refresh token validity")
        elif not auth_issues and not token_issues:
            print("✅ AUTHENTICATION APPEARS WORKING")
            print("   • Google APIs are accessible")
            print("   • OAuth tokens are valid")
            print("   • Issue may be in frontend display logic")
        else:
            print("❓ UNCLEAR ROOT CAUSE")
            print("   • Mixed authentication results")
            print("   • Further investigation needed")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = GoogleConnectionDebugTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()