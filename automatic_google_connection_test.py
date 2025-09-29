#!/usr/bin/env python3
"""
AUTOMATIC GOOGLE CONNECTION SYSTEM TESTING
==========================================

This test verifies the new automatic Google connection system as requested in the review:

1. **New Automatic Google Connection Endpoints**:
   - Test `/api/admin/google/connection-status` - should return automatic connection status
   - Test `/api/admin/google/monitor` - should return monitoring dashboard data
   - Test `/api/admin/google/health-check` - should return health metrics
   - Test `/api/admin/google/force-reconnect` - should trigger reconnection

2. **New Automatic Google API Endpoints**:
   - Test `/api/google/gmail/auto-messages` - should retrieve Gmail messages via service account
   - Test `/api/google/calendar/auto-events` - should retrieve Calendar events via service account  
   - Test `/api/google/drive/auto-files` - should retrieve Drive files via service account

3. **Connection Status Verification**:
   - Verify that the system reports "auto_managed": true
   - Verify that the system reports "user_intervention_required": false
   - Check if the automatic Google manager is initialized and working

4. **Compare with Previous System**:
   - Test the old manual endpoints to compare (like `/api/google/gmail/real-messages`)
   - Verify that the new automatic endpoints return data without requiring OAuth

Authentication: Use admin/password123 for all tests.
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration - Use the correct backend URL from frontend/.env
BACKEND_URL = "https://fidus-workspace-2.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class AutomaticGoogleConnectionTest:
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
    
    def test_automatic_connection_status(self):
        """Test /api/admin/google/connection-status endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/google/connection-status")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for automatic connection indicators
                auto_managed = data.get("auto_managed", False)
                user_intervention_required = data.get("user_intervention_required", True)
                
                if auto_managed and not user_intervention_required:
                    self.log_result("Automatic Connection Status", True, 
                                  "System reports automatic management enabled",
                                  {"auto_managed": auto_managed, "user_intervention_required": user_intervention_required})
                else:
                    self.log_result("Automatic Connection Status", False, 
                                  f"System not fully automatic: auto_managed={auto_managed}, user_intervention_required={user_intervention_required}",
                                  {"response_data": data})
            else:
                self.log_result("Automatic Connection Status", False, 
                              f"HTTP {response.status_code}: Connection status endpoint not accessible",
                              {"response": response.text})
                
        except Exception as e:
            self.log_result("Automatic Connection Status", False, f"Exception: {str(e)}")
    
    def test_automatic_monitor_endpoint(self):
        """Test /api/admin/google/monitor endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/google/monitor")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for monitoring dashboard data
                expected_fields = ["connection_status", "services", "monitoring_data"]
                has_monitoring_data = any(field in data for field in expected_fields)
                
                if has_monitoring_data:
                    self.log_result("Automatic Monitor Dashboard", True, 
                                  "Monitor endpoint returns dashboard data",
                                  {"data_keys": list(data.keys())})
                else:
                    self.log_result("Automatic Monitor Dashboard", False, 
                                  "Monitor endpoint missing expected monitoring data",
                                  {"response_data": data})
            else:
                self.log_result("Automatic Monitor Dashboard", False, 
                              f"HTTP {response.status_code}: Monitor endpoint not accessible",
                              {"response": response.text})
                
        except Exception as e:
            self.log_result("Automatic Monitor Dashboard", False, f"Exception: {str(e)}")
    
    def test_automatic_health_check(self):
        """Test /api/admin/google/health-check endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/google/health-check")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for health metrics
                expected_fields = ["health_status", "metrics", "services_health"]
                has_health_data = any(field in data for field in expected_fields)
                
                if has_health_data:
                    self.log_result("Automatic Health Check", True, 
                                  "Health check endpoint returns metrics",
                                  {"data_keys": list(data.keys())})
                else:
                    self.log_result("Automatic Health Check", False, 
                                  "Health check endpoint missing expected metrics",
                                  {"response_data": data})
            else:
                self.log_result("Automatic Health Check", False, 
                              f"HTTP {response.status_code}: Health check endpoint not accessible",
                              {"response": response.text})
                
        except Exception as e:
            self.log_result("Automatic Health Check", False, f"Exception: {str(e)}")
    
    def test_automatic_force_reconnect(self):
        """Test /api/admin/google/force-reconnect endpoint"""
        try:
            response = self.session.post(f"{BACKEND_URL}/admin/google/force-reconnect")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for reconnection response
                success = data.get("success", False)
                message = data.get("message", "")
                
                if success or "reconnect" in message.lower():
                    self.log_result("Automatic Force Reconnect", True, 
                                  "Force reconnect endpoint triggered successfully",
                                  {"response": data})
                else:
                    self.log_result("Automatic Force Reconnect", False, 
                                  "Force reconnect endpoint did not indicate success",
                                  {"response_data": data})
            else:
                self.log_result("Automatic Force Reconnect", False, 
                              f"HTTP {response.status_code}: Force reconnect endpoint not accessible",
                              {"response": response.text})
                
        except Exception as e:
            self.log_result("Automatic Force Reconnect", False, f"Exception: {str(e)}")
    
    def test_automatic_gmail_messages(self):
        """Test /api/google/gmail/auto-messages endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/google/gmail/auto-messages")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if messages are returned via service account
                if isinstance(data, list) and len(data) > 0:
                    self.log_result("Automatic Gmail Messages", True, 
                                  f"Retrieved {len(data)} Gmail messages via service account",
                                  {"message_count": len(data), "first_message": data[0] if data else None})
                elif isinstance(data, dict) and data.get("messages"):
                    messages = data["messages"]
                    self.log_result("Automatic Gmail Messages", True, 
                                  f"Retrieved {len(messages)} Gmail messages via service account",
                                  {"message_count": len(messages)})
                else:
                    self.log_result("Automatic Gmail Messages", False, 
                                  "No Gmail messages returned from automatic endpoint",
                                  {"response_data": data})
            else:
                self.log_result("Automatic Gmail Messages", False, 
                              f"HTTP {response.status_code}: Auto Gmail messages endpoint failed",
                              {"response": response.text})
                
        except Exception as e:
            self.log_result("Automatic Gmail Messages", False, f"Exception: {str(e)}")
    
    def test_automatic_calendar_events(self):
        """Test /api/google/calendar/auto-events endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/google/calendar/auto-events")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if events are returned via service account
                if isinstance(data, list):
                    self.log_result("Automatic Calendar Events", True, 
                                  f"Retrieved {len(data)} Calendar events via service account",
                                  {"event_count": len(data)})
                elif isinstance(data, dict) and data.get("events"):
                    events = data["events"]
                    self.log_result("Automatic Calendar Events", True, 
                                  f"Retrieved {len(events)} Calendar events via service account",
                                  {"event_count": len(events)})
                else:
                    self.log_result("Automatic Calendar Events", False, 
                                  "No Calendar events returned from automatic endpoint",
                                  {"response_data": data})
            else:
                self.log_result("Automatic Calendar Events", False, 
                              f"HTTP {response.status_code}: Auto Calendar events endpoint failed",
                              {"response": response.text})
                
        except Exception as e:
            self.log_result("Automatic Calendar Events", False, f"Exception: {str(e)}")
    
    def test_automatic_drive_files(self):
        """Test /api/google/drive/auto-files endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/google/drive/auto-files")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if files are returned via service account
                if isinstance(data, list):
                    self.log_result("Automatic Drive Files", True, 
                                  f"Retrieved {len(data)} Drive files via service account",
                                  {"file_count": len(data)})
                elif isinstance(data, dict) and data.get("files"):
                    files = data["files"]
                    self.log_result("Automatic Drive Files", True, 
                                  f"Retrieved {len(files)} Drive files via service account",
                                  {"file_count": len(files)})
                else:
                    self.log_result("Automatic Drive Files", False, 
                                  "No Drive files returned from automatic endpoint",
                                  {"response_data": data})
            else:
                self.log_result("Automatic Drive Files", False, 
                              f"HTTP {response.status_code}: Auto Drive files endpoint failed",
                              {"response": response.text})
                
        except Exception as e:
            self.log_result("Automatic Drive Files", False, f"Exception: {str(e)}")
    
    def test_compare_with_manual_endpoints(self):
        """Compare automatic endpoints with manual OAuth endpoints"""
        try:
            # Test manual Gmail endpoint for comparison
            response = self.session.get(f"{BACKEND_URL}/google/gmail/real-messages")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.log_result("Manual Gmail Comparison", True, 
                                  f"Manual Gmail endpoint returns {len(data)} messages (requires OAuth)",
                                  {"manual_message_count": len(data)})
                else:
                    self.log_result("Manual Gmail Comparison", False, 
                                  "Manual Gmail endpoint returns no messages",
                                  {"response_data": data})
            else:
                # This might be expected if OAuth is not completed
                if response.status_code == 401 or "auth" in response.text.lower():
                    self.log_result("Manual Gmail Comparison", True, 
                                  "Manual Gmail endpoint requires authentication as expected",
                                  {"status_code": response.status_code})
                else:
                    self.log_result("Manual Gmail Comparison", False, 
                                  f"Manual Gmail endpoint unexpected error: HTTP {response.status_code}",
                                  {"response": response.text})
                
        except Exception as e:
            self.log_result("Manual Gmail Comparison", False, f"Exception: {str(e)}")
    
    def test_system_initialization(self):
        """Test if automatic Google manager is initialized"""
        try:
            # Check system health to see if automatic connection is mentioned
            response = self.session.get(f"{BACKEND_URL}/health")
            
            if response.status_code == 200:
                data = response.json()
                
                # Look for automatic connection indicators in health response
                health_text = json.dumps(data).lower()
                if "automatic" in health_text or "auto" in health_text:
                    self.log_result("System Initialization", True, 
                                  "System health indicates automatic connection features",
                                  {"health_data": data})
                else:
                    # Try the connection status endpoint as backup
                    status_response = self.session.get(f"{BACKEND_URL}/admin/google/connection-status")
                    if status_response.status_code == 200:
                        self.log_result("System Initialization", True, 
                                      "Automatic connection endpoints are accessible",
                                      {"connection_status_accessible": True})
                    else:
                        self.log_result("System Initialization", False, 
                                      "No evidence of automatic connection system initialization",
                                      {"health_data": data})
            else:
                self.log_result("System Initialization", False, 
                              f"Cannot check system health: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("System Initialization", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all automatic Google connection tests"""
        print("🤖 AUTOMATIC GOOGLE CONNECTION SYSTEM TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Testing Automatic Google Connection System...")
        print("-" * 50)
        
        # Test 1: New Automatic Google Connection Endpoints
        print("\n1️⃣ Testing Automatic Google Connection Endpoints:")
        self.test_automatic_connection_status()
        self.test_automatic_monitor_endpoint()
        self.test_automatic_health_check()
        self.test_automatic_force_reconnect()
        
        # Test 2: New Automatic Google API Endpoints
        print("\n2️⃣ Testing Automatic Google API Endpoints:")
        self.test_automatic_gmail_messages()
        self.test_automatic_calendar_events()
        self.test_automatic_drive_files()
        
        # Test 3: Connection Status Verification
        print("\n3️⃣ Testing Connection Status Verification:")
        self.test_system_initialization()
        
        # Test 4: Compare with Previous System
        print("\n4️⃣ Comparing with Manual OAuth System:")
        self.test_compare_with_manual_endpoints()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🤖 AUTOMATIC GOOGLE CONNECTION TEST SUMMARY")
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
        
        # Categorize results
        connection_tests = [r for r in self.test_results if "Connection" in r['test'] or "Monitor" in r['test'] or "Health" in r['test'] or "Reconnect" in r['test']]
        api_tests = [r for r in self.test_results if "Gmail" in r['test'] or "Calendar" in r['test'] or "Drive" in r['test']]
        system_tests = [r for r in self.test_results if "System" in r['test'] or "Comparison" in r['test']]
        
        print("📊 RESULTS BY CATEGORY:")
        print(f"Connection Management: {sum(1 for r in connection_tests if r['success'])}/{len(connection_tests)} passed")
        print(f"Automatic API Endpoints: {sum(1 for r in api_tests if r['success'])}/{len(api_tests)} passed")
        print(f"System Integration: {sum(1 for r in system_tests if r['success'])}/{len(system_tests)} passed")
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
            "Automatic Connection Status",
            "Automatic Gmail Messages", 
            "Automatic Calendar Events",
            "Automatic Drive Files"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(critical in result['test'] for critical in critical_tests))
        
        print("🚨 CRITICAL ASSESSMENT:")
        if critical_passed >= 3:  # At least 3 out of 4 critical tests
            print("✅ AUTOMATIC GOOGLE CONNECTION SYSTEM: OPERATIONAL")
            print("   The new automatic Google connection system is working.")
            print("   Service account integration successfully replaces manual OAuth.")
        else:
            print("❌ AUTOMATIC GOOGLE CONNECTION SYSTEM: NOT OPERATIONAL")
            print("   Critical automatic connection features are not working.")
            print("   System still requires manual OAuth intervention.")
        
def main():
    """Main test execution"""
    test_runner = AutomaticGoogleConnectionTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()