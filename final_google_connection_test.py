#!/usr/bin/env python3
"""
FINAL PRODUCTION TEST: Automatic Google Connection System Verification
====================================================================

This test performs comprehensive end-to-end verification of the automatic Google 
connection system that eliminates all manual intervention as requested in the review.

CRITICAL VERIFICATION POINTS:
1. Automatic System Status - GET /api/google/connection/test-all must return HTTP 200
2. Admin Authentication Integration - POST /api/auth/login must work normally  
3. System Health Verification - Backend must be running without errors
4. Production Readiness Check - Automatic connection system must be active on startup
5. Frontend Integration Readiness - Proper response formatting for frontend

SUCCESS CRITERIA FOR PRODUCTION:
✅ All Google services automatically show "Connected" without user action
✅ System reports 100% health and success rates consistently
✅ No manual "Connect Google Workspace" intervention required
✅ Automatic reconnection and monitoring system active
✅ Frontend receives proper connection status data

FAILURE CRITERIA (REQUIRING IMMEDIATE FIX):
❌ Any Google service shows "Disconnected" or "no_auth" status
❌ System requires manual user intervention for Google connection
❌ HTTP 404 errors or endpoint accessibility issues
❌ Overall health below 100% or success rate below 100%
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration - Use production URL from frontend/.env
BACKEND_URL = "https://fidus-invest.emergent.host/api"
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
            print(f"   Details: {json.dumps(details, indent=2)}")
    
    def authenticate_admin(self):
        """Authenticate as admin user - CRITICAL for Google endpoints"""
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
                    self.log_result("Admin Authentication Integration", True, 
                                  "Admin authentication working normally with JWT token generation")
                    return True
                else:
                    self.log_result("Admin Authentication Integration", False, 
                                  "No JWT token received in response", {"response": data})
                    return False
            else:
                self.log_result("Admin Authentication Integration", False, 
                              f"HTTP {response.status_code} - Admin login failed", 
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication Integration", False, 
                          f"Exception during admin authentication: {str(e)}")
            return False
    
    def test_automatic_google_connection_status(self):
        """Test GET /api/google/connection/test-all - CRITICAL SUCCESS CRITERIA"""
        try:
            response = self.session.get(f"{BACKEND_URL}/google/connection/test-all")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify automatic connection data structure
                required_fields = ["overall_status", "services", "overall_health", "success_rate"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result("Automatic System Status - Response Format", False,
                                  f"Missing required fields: {missing_fields}", {"response": data})
                    return False
                
                # Check overall health and success rate
                overall_health = data.get("overall_health", 0)
                success_rate = data.get("success_rate", 0)
                
                if overall_health == 100.0 and success_rate == 100.0:
                    self.log_result("Automatic System Status - Health Metrics", True,
                                  f"Perfect health metrics: {overall_health}% health, {success_rate}% success")
                else:
                    self.log_result("Automatic System Status - Health Metrics", False,
                                  f"Health metrics below 100%: {overall_health}% health, {success_rate}% success",
                                  {"expected": "100.0% for both", "actual": data})
                    return False
                
                # Check all 4 Google services status
                services = data.get("services", {})
                required_services = ["gmail", "calendar", "drive", "meet"]
                
                all_connected = True
                service_status = {}
                
                for service in required_services:
                    if service in services:
                        service_data = services[service]
                        status = service_data.get("status", "unknown")
                        service_status[service] = status
                        
                        if status != "Connected":
                            all_connected = False
                            self.log_result(f"Automatic System Status - {service.title()} Service", False,
                                          f"{service.title()} shows '{status}' instead of 'Connected'",
                                          {"service_data": service_data})
                        else:
                            self.log_result(f"Automatic System Status - {service.title()} Service", True,
                                          f"{service.title()} automatically connected")
                    else:
                        all_connected = False
                        self.log_result(f"Automatic System Status - {service.title()} Service", False,
                                      f"{service.title()} service missing from response")
                
                # Check for automatic management flags
                auto_managed = data.get("auto_managed", False)
                user_intervention_required = data.get("user_intervention_required", True)
                
                if auto_managed and not user_intervention_required:
                    self.log_result("Automatic System Status - Auto Management", True,
                                  "System shows auto_managed=true and user_intervention_required=false")
                else:
                    self.log_result("Automatic System Status - Auto Management", False,
                                  f"Auto management flags incorrect: auto_managed={auto_managed}, user_intervention_required={user_intervention_required}",
                                  {"expected": "auto_managed=true, user_intervention_required=false"})
                    return False
                
                if all_connected:
                    self.log_result("Automatic System Status - All Services", True,
                                  "All 4 Google services (Gmail, Calendar, Drive, Meet) show 'Connected' status")
                    return True
                else:
                    self.log_result("Automatic System Status - All Services", False,
                                  "Not all Google services show 'Connected' status",
                                  {"service_status": service_status})
                    return False
                    
            elif response.status_code == 404:
                self.log_result("Automatic System Status - Endpoint Access", False,
                              "HTTP 404 - Google connection endpoint not accessible (route conflict or missing)",
                              {"url": f"{BACKEND_URL}/google/connection/test-all"})
                return False
            else:
                self.log_result("Automatic System Status - Endpoint Access", False,
                              f"HTTP {response.status_code} - Endpoint accessibility issue",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Automatic System Status - Connection Test", False,
                          f"Exception during automatic connection test: {str(e)}")
            return False
    
    def test_system_health_verification(self):
        """Test system health and backend running without errors"""
        try:
            # Test basic health endpoint
            response = self.session.get(f"{BACKEND_URL}/health")
            if response.status_code == 200:
                self.log_result("System Health Verification - Basic Health", True,
                              "Backend health endpoint responding correctly")
            else:
                self.log_result("System Health Verification - Basic Health", False,
                              f"Health endpoint failed: HTTP {response.status_code}")
                return False
            
            # Test readiness probe
            response = self.session.get(f"{BACKEND_URL}/health/ready")
            if response.status_code == 200:
                self.log_result("System Health Verification - Readiness", True,
                              "Backend readiness probe successful")
            else:
                self.log_result("System Health Verification - Readiness", False,
                              f"Readiness probe failed: HTTP {response.status_code}")
            
            # Test that other core functionality remains intact
            core_endpoints = [
                ("/admin/users", "User Management"),
                ("/admin/clients", "Client Management"),
                ("/health/metrics", "Health Metrics")
            ]
            
            all_core_working = True
            for endpoint, name in core_endpoints:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                    if response.status_code == 200:
                        self.log_result(f"System Health Verification - {name}", True,
                                      f"{name} endpoint operational")
                    else:
                        self.log_result(f"System Health Verification - {name}", False,
                                      f"{name} endpoint failed: HTTP {response.status_code}")
                        all_core_working = False
                except Exception as e:
                    self.log_result(f"System Health Verification - {name}", False,
                                  f"{name} endpoint exception: {str(e)}")
                    all_core_working = False
            
            return all_core_working
            
        except Exception as e:
            self.log_result("System Health Verification", False,
                          f"Exception during system health check: {str(e)}")
            return False
    
    def test_production_readiness_check(self):
        """Test automatic connection system active on startup"""
        try:
            # Check if automatic connection system initialized
            response = self.session.get(f"{BACKEND_URL}/google/connection/test-all")
            
            if response.status_code == 200:
                data = response.json()
                
                # Look for signs of automatic system initialization
                startup_indicators = [
                    data.get("auto_managed", False),
                    not data.get("user_intervention_required", True),
                    data.get("overall_health", 0) == 100.0,
                    data.get("success_rate", 0) == 100.0
                ]
                
                if all(startup_indicators):
                    self.log_result("Production Readiness Check - Startup Initialization", True,
                                  "Automatic connection system active on startup with perfect metrics")
                    
                    # Check for automatic reconnection capability
                    connection_quality = data.get("connection_quality", {})
                    if connection_quality:
                        self.log_result("Production Readiness Check - Monitoring System", True,
                                      "Automatic monitoring and reconnection system operational")
                    else:
                        self.log_result("Production Readiness Check - Monitoring System", False,
                                      "Connection monitoring system not detected")
                        return False
                    
                    return True
                else:
                    self.log_result("Production Readiness Check - Startup Initialization", False,
                                  "Automatic connection system not properly initialized on startup",
                                  {"startup_indicators": startup_indicators, "data": data})
                    return False
            else:
                self.log_result("Production Readiness Check - System Access", False,
                              f"Cannot access automatic connection system: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Production Readiness Check", False,
                          f"Exception during production readiness check: {str(e)}")
            return False
    
    def test_frontend_integration_readiness(self):
        """Test Google Connection Monitor endpoint responses for frontend compatibility"""
        try:
            # Test main connection endpoint for frontend
            response = self.session.get(f"{BACKEND_URL}/google/connection/test-all")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response format compatibility with frontend
                frontend_required_fields = [
                    "overall_status",
                    "services",
                    "overall_health", 
                    "success_rate",
                    "auto_managed",
                    "user_intervention_required"
                ]
                
                missing_frontend_fields = [field for field in frontend_required_fields if field not in data]
                
                if not missing_frontend_fields:
                    self.log_result("Frontend Integration Readiness - Response Format", True,
                                  "Response format compatible with frontend requirements")
                    
                    # Check that no "no_auth" errors present
                    services = data.get("services", {})
                    no_auth_errors = []
                    
                    for service_name, service_data in services.items():
                        if service_data.get("status") == "no_auth":
                            no_auth_errors.append(service_name)
                    
                    if not no_auth_errors:
                        self.log_result("Frontend Integration Readiness - No Auth Errors", True,
                                      "No 'no_auth' errors found - frontend will not show manual connection prompts")
                        return True
                    else:
                        self.log_result("Frontend Integration Readiness - No Auth Errors", False,
                                      f"'no_auth' errors found for services: {no_auth_errors}",
                                      {"services_with_no_auth": no_auth_errors})
                        return False
                else:
                    self.log_result("Frontend Integration Readiness - Response Format", False,
                                  f"Missing frontend required fields: {missing_frontend_fields}",
                                  {"response": data})
                    return False
            else:
                self.log_result("Frontend Integration Readiness - Endpoint Access", False,
                              f"Frontend cannot access connection status: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Frontend Integration Readiness", False,
                          f"Exception during frontend integration test: {str(e)}")
            return False
    
    def test_individual_google_services(self):
        """Test individual Google service endpoints for completeness"""
        services = ["gmail", "calendar", "drive", "meet"]
        
        for service in services:
            try:
                response = self.session.get(f"{BACKEND_URL}/google/connection/test/{service}")
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status", "unknown")
                    
                    if status == "Connected":
                        self.log_result(f"Individual Service Test - {service.title()}", True,
                                      f"{service.title()} service individually reports 'Connected'")
                    else:
                        self.log_result(f"Individual Service Test - {service.title()}", False,
                                      f"{service.title()} service reports '{status}' instead of 'Connected'",
                                      {"service_response": data})
                else:
                    self.log_result(f"Individual Service Test - {service.title()}", False,
                                  f"{service.title()} service test failed: HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Individual Service Test - {service.title()}", False,
                              f"{service.title()} service test exception: {str(e)}")
    
    def run_comprehensive_test(self):
        """Run comprehensive automatic Google connection system verification"""
        print("🚀 FINAL PRODUCTION TEST: Automatic Google Connection System Verification")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        print("OBJECTIVE: Verify Complete Automatic Google Connection System")
        print("SUCCESS CRITERIA: 100% automatic connection without user intervention")
        print()
        
        # Step 1: Admin Authentication Integration
        if not self.authenticate_admin():
            print("🚨 CRITICAL FAILURE: Admin authentication failed. Cannot proceed.")
            return False
        
        print("\n🔍 Running Automatic Google Connection Verification Tests...")
        print("-" * 60)
        
        # Step 2: Test Automatic System Status (MOST CRITICAL)
        automatic_status_success = self.test_automatic_google_connection_status()
        
        # Step 3: System Health Verification
        system_health_success = self.test_system_health_verification()
        
        # Step 4: Production Readiness Check
        production_ready_success = self.test_production_readiness_check()
        
        # Step 5: Frontend Integration Readiness
        frontend_ready_success = self.test_frontend_integration_readiness()
        
        # Step 6: Individual Service Tests
        self.test_individual_google_services()
        
        # Generate comprehensive summary
        self.generate_production_test_summary(
            automatic_status_success,
            system_health_success, 
            production_ready_success,
            frontend_ready_success
        )
        
        return automatic_status_success and system_health_success
    
    def generate_production_test_summary(self, automatic_status, system_health, production_ready, frontend_ready):
        """Generate comprehensive production test summary"""
        print("\n" + "=" * 80)
        print("🎯 AUTOMATIC GOOGLE CONNECTION SYSTEM - PRODUCTION TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Critical Success Criteria Assessment
        print("🚨 CRITICAL SUCCESS CRITERIA ASSESSMENT:")
        print("-" * 50)
        
        criteria_results = [
            ("Automatic System Status", automatic_status, "All Google services show 'Connected' automatically"),
            ("System Health Verification", system_health, "Backend running without errors"),
            ("Production Readiness", production_ready, "Automatic connection active on startup"),
            ("Frontend Integration", frontend_ready, "Proper response formatting for frontend")
        ]
        
        all_critical_passed = True
        for criteria, passed, description in criteria_results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status}: {criteria} - {description}")
            if not passed:
                all_critical_passed = False
        
        print()
        
        # Show detailed failures if any
        if failed_tests > 0:
            print("❌ DETAILED FAILURE ANALYSIS:")
            print("-" * 40)
            for result in self.test_results:
                if not result['success']:
                    print(f"• {result['test']}: {result['message']}")
            print()
        
        # Final Production Assessment
        print("🏆 FINAL PRODUCTION ASSESSMENT:")
        print("-" * 40)
        
        if all_critical_passed and success_rate >= 90.0:
            print("✅ PRODUCTION READY: Automatic Google Connection System OPERATIONAL")
            print("   ✓ All Google services automatically connected without user intervention")
            print("   ✓ System reports 100% health and success rates")
            print("   ✓ No manual 'Connect Google Workspace' intervention required")
            print("   ✓ Automatic reconnection and monitoring system active")
            print("   ✓ Frontend integration ready for deployment")
            print()
            print("🚀 RECOMMENDATION: APPROVE FOR PRODUCTION DEPLOYMENT")
        else:
            print("❌ PRODUCTION NOT READY: Critical Issues Found")
            print("   ⚠️  Automatic Google connection system has failures")
            print("   ⚠️  Manual user intervention may still be required")
            print("   ⚠️  System does not meet 100% automatic connection criteria")
            print()
            print("🔧 RECOMMENDATION: IMMEDIATE MAIN AGENT INTERVENTION REQUIRED")
            
            # Specific recommendations based on failures
            if not automatic_status:
                print("   → Fix automatic Google connection status endpoint")
                print("   → Resolve route conflicts preventing access to automatic endpoint")
                print("   → Ensure all 4 services show 'Connected' status automatically")
            
            if not system_health:
                print("   → Fix backend health and core functionality issues")
                print("   → Resolve any endpoint registration problems")
            
            if not production_ready:
                print("   → Fix automatic connection system startup initialization")
                print("   → Implement proper automatic reconnection monitoring")
            
            if not frontend_ready:
                print("   → Fix response format compatibility with frontend")
                print("   → Eliminate 'no_auth' errors that trigger manual connection prompts")
        
        print("\n" + "=" * 80)

def main():
    """Main test execution"""
    test_runner = AutomaticGoogleConnectionTest()
    success = test_runner.run_comprehensive_test()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()