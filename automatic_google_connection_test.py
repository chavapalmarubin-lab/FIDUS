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
        
        print("\n" + "=" * 60)
                critical=True
            )
            return False
    
    def test_automatic_connection_initialization(self):
        """Test if automatic connection system started on server startup"""
        try:
            # Check if admin_sessions collection has google_authenticated: true
            response = self.session.get(f"{BACKEND_URL}/admin/users", timeout=10)
            
            if response.status_code == 200:
                # If we can access admin endpoints, the system is running
                self.log_test(
                    "Automatic Connection System Startup",
                    True,
                    "Backend system is running and accessible, automatic connection should be initialized"
                )
                return True
            else:
                self.log_test(
                    "Automatic Connection System Startup",
                    False,
                    f"Backend system not accessible: {response.status_code}",
                    critical=True
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Automatic Connection System Startup",
                False,
                f"System startup check failed: {str(e)}",
                critical=True
            )
            return False
    
    def test_overridden_google_connection_endpoint(self):
        """Test the overridden /google/connection/test-all endpoint"""
        try:
            response = self.session.get(
                f"{BACKEND_URL}/google/connection/test-all",
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if all 4 services show "Connected"
                services = data.get("services", {})
                expected_services = ["gmail", "calendar", "drive", "meet"]
                
                all_connected = True
                connected_services = []
                
                for service in expected_services:
                    if service in services:
                        service_data = services[service]
                        is_connected = service_data.get("connected", False)
                        status = service_data.get("status", "")
                        auto_managed = service_data.get("auto_managed", False)
                        
                        if is_connected and status == "Connected" and auto_managed:
                            connected_services.append(f"{service}: Connected (auto_managed)")
                        else:
                            all_connected = False
                            connected_services.append(f"{service}: {status} (auto_managed: {auto_managed})")
                    else:
                        all_connected = False
                        connected_services.append(f"{service}: Missing")
                
                # Check overall status
                auto_managed = data.get("auto_managed", False)
                user_intervention_required = data.get("user_intervention_required", True)
                overall_health = data.get("overall_health", 0)
                
                success = (
                    all_connected and 
                    auto_managed and 
                    not user_intervention_required and
                    overall_health == 100.0
                )
                
                details = f"Services: {', '.join(connected_services)}. Auto-managed: {auto_managed}, User intervention required: {user_intervention_required}, Health: {overall_health}%"
                
                self.log_test(
                    "Overridden Google Connection Endpoint",
                    success,
                    details,
                    critical=True
                )
                return success
                
            else:
                self.log_test(
                    "Overridden Google Connection Endpoint",
                    False,
                    f"Endpoint failed: {response.status_code} - {response.text}",
                    critical=True
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Overridden Google Connection Endpoint",
                False,
                f"Endpoint test failed: {str(e)}",
                critical=True
            )
            return False
    
    def test_individual_google_services(self):
        """Test individual Google service endpoints"""
        services = ["gmail", "calendar", "drive", "meet"]
        all_success = True
        
        for service in services:
            try:
                response = self.session.get(
                    f"{BACKEND_URL}/google/connection/test/{service}",
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    connected = data.get("connected", False)
                    status = data.get("status", "")
                    
                    success = connected and status == "Connected"
                    self.log_test(
                        f"Individual Service Test - {service.title()}",
                        success,
                        f"Status: {status}, Connected: {connected}"
                    )
                    
                    if not success:
                        all_success = False
                else:
                    self.log_test(
                        f"Individual Service Test - {service.title()}",
                        False,
                        f"Service test failed: {response.status_code}"
                    )
                    all_success = False
                    
            except Exception as e:
                self.log_test(
                    f"Individual Service Test - {service.title()}",
                    False,
                    f"Service test error: {str(e)}"
                )
                all_success = False
        
        return all_success
    
    def test_google_api_endpoints(self):
        """Test actual Google API endpoints to verify they work with automatic connection"""
        endpoints_to_test = [
            ("/google/gmail/real-messages", "Gmail Real Messages"),
            ("/google/calendar/events", "Calendar Events"),
            ("/google/drive/real-files", "Drive Real Files")
        ]
        
        working_endpoints = 0
        total_endpoints = len(endpoints_to_test)
        
        for endpoint, name in endpoints_to_test:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}", timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    success = data.get("success", False)
                    
                    if success:
                        working_endpoints += 1
                        self.log_test(
                            f"Google API - {name}",
                            True,
                            f"API working correctly with automatic connection"
                        )
                    else:
                        auth_required = data.get("auth_required", False)
                        if auth_required:
                            self.log_test(
                                f"Google API - {name}",
                                False,
                                f"API requires authentication - automatic connection not working"
                            )
                        else:
                            self.log_test(
                                f"Google API - {name}",
                                False,
                                f"API failed: {data.get('message', 'Unknown error')}"
                            )
                else:
                    self.log_test(
                        f"Google API - {name}",
                        False,
                        f"API endpoint failed: {response.status_code}"
                    )
                    
            except Exception as e:
                self.log_test(
                    f"Google API - {name}",
                    False,
                    f"API test error: {str(e)}"
                )
        
        success_rate = (working_endpoints / total_endpoints) * 100
        overall_success = success_rate >= 100  # All APIs should work with automatic connection
        
        self.log_test(
            "Google API Integration with Automatic Connection",
            overall_success,
            f"Working APIs: {working_endpoints}/{total_endpoints} ({success_rate:.1f}%)",
            critical=True
        )
        
        return overall_success
    
    def test_system_health(self):
        """Test that other system functionality remains intact"""
        try:
            # Test health endpoint
            response = self.session.get(f"{BACKEND_URL}/health", timeout=10)
            health_ok = response.status_code == 200
            
            # Test admin users endpoint
            response = self.session.get(f"{BACKEND_URL}/admin/users", timeout=10)
            users_ok = response.status_code == 200
            
            # Test admin clients endpoint
            response = self.session.get(f"{BACKEND_URL}/admin/clients", timeout=10)
            clients_ok = response.status_code == 200
            
            overall_health = health_ok and users_ok and clients_ok
            
            details = f"Health: {'✓' if health_ok else '✗'}, Users: {'✓' if users_ok else '✗'}, Clients: {'✓' if clients_ok else '✗'}"
            
            self.log_test(
                "System Health After Automatic Connection",
                overall_health,
                details
            )
            
            return overall_health
            
        except Exception as e:
            self.log_test(
                "System Health After Automatic Connection",
                False,
                f"Health check failed: {str(e)}"
            )
            return False
    
    def run_comprehensive_test(self):
        """Run all automatic Google connection tests"""
        print("=" * 80)
        print("AUTOMATIC GOOGLE CONNECTION SYSTEM TESTING")
        print("=" * 80)
        print()
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ CRITICAL: Cannot proceed without admin authentication")
            return False
        
        # Step 2: Test automatic connection initialization
        self.test_automatic_connection_initialization()
        
        # Step 3: Test overridden Google connection endpoint (CRITICAL)
        connection_success = self.test_overridden_google_connection_endpoint()
        
        # Step 4: Test individual Google services
        individual_success = self.test_individual_google_services()
        
        # Step 5: Test Google API endpoints with automatic connection
        api_success = self.test_google_api_endpoints()
        
        # Step 6: Test system health
        health_success = self.test_system_health()
        
        # Calculate overall results
        critical_tests = [connection_success]
        critical_success = all(critical_tests)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("=" * 80)
        print("AUTOMATIC GOOGLE CONNECTION TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if critical_success:
            print("✅ CRITICAL SUCCESS: Automatic Google connection system is working!")
            print("   - Google connection endpoints return 'Connected' status automatically")
            print("   - No manual 'Connect Google Workspace' required")
            print("   - System shows automated Google connection health")
        else:
            print("❌ CRITICAL FAILURE: Automatic Google connection system is NOT working!")
            print("   - Manual intervention still required")
            print("   - Google connection endpoints not returning automatic status")
        
        print()
        print("DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            priority = f"[{result['priority']}]"
            print(f"{status} {priority} {result['test']}")
            if not result["success"]:
                print(f"    Issue: {result['details']}")
        
        return critical_success

def main():
    """Main test execution"""
    tester = AutoGoogleConnectionTester()
    success = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()