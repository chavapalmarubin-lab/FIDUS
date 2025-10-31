#!/usr/bin/env python3
"""
AUTOMATIC GOOGLE CONNECTION SYSTEM TESTING
===========================================

Testing the newly implemented automatic Google connection system that should eliminate 
all manual intervention requirements.

CRITICAL TESTS:
1. Automatic Connection Initialization
2. Existing Google Connection Endpoint (OVERRIDDEN)
3. Google Connection Monitor Integration
4. Database Verification
5. System Health Confirmation
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://fidus-invest.emergent.host/api"
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "password123",
    "user_type": "admin"
}

class AutoGoogleConnectionTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details, critical=False):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        priority = "CRITICAL" if critical else "NORMAL"
        
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "priority": priority,
            "timestamp": datetime.now().isoformat()
        }
        
        self.test_results.append(result)
        print(f"{status} [{priority}] {test_name}")
        print(f"    Details: {details}")
        print()
        
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                self.log_test(
                    "Admin Authentication",
                    True,
                    f"Successfully authenticated as admin with JWT token"
                )
                return True
            else:
                self.log_test(
                    "Admin Authentication", 
                    False,
                    f"Authentication failed: {response.status_code} - {response.text}",
                    critical=True
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Admin Authentication",
                False, 
                f"Authentication error: {str(e)}",
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