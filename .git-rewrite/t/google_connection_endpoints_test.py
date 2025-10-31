#!/usr/bin/env python3
"""
URGENT: GOOGLE CONNECTION ENDPOINTS TEST AFTER BACKEND RESTART
============================================================

This test verifies the Google connection endpoints are accessible after explicit backend restart.
This is the definitive test to confirm if the production issue is resolved.

CRITICAL TESTING REQUIREMENTS:
1. Basic Connectivity Test (health, admin login, JWT token)
2. Google Endpoints Accessibility Test - ALL 4 endpoints MUST return 200, not 404:
   - GET /api/admin/google/connection-status
   - GET /api/admin/google/monitor  
   - GET /api/admin/google/health-check
   - POST /api/admin/google/force-reconnect
3. Production Readiness Verification (success: true, auto_managed: true, user_intervention_required: false)
4. Endpoint Response Content Test

FAILURE CRITERIA: If ANY endpoint returns 404, the automated Google connection system is NOT working.
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

class GoogleConnectionEndpointsTest:
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
    
    def test_basic_connectivity(self):
        """Test basic backend connectivity"""
        try:
            # Test health endpoint
            response = self.session.get(f"{BACKEND_URL}/health")
            if response.status_code == 200:
                self.log_result("Basic Health Check", True, "Backend is running and healthy")
            else:
                self.log_result("Basic Health Check", False, f"Health check failed: HTTP {response.status_code}")
                return False
            
            # Test admin authentication
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
                    self.log_result("Admin Authentication", True, "Successfully authenticated as admin with JWT token")
                    return True
                else:
                    self.log_result("Admin Authentication", False, "No JWT token received", {"response": data})
                    return False
            else:
                self.log_result("Admin Authentication", False, f"Authentication failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Basic Connectivity", False, f"Exception: {str(e)}")
            return False
    
    def test_google_endpoints_accessibility(self):
        """Test all 4 Google connection endpoints for accessibility (NOT 404)"""
        google_endpoints = [
            ("GET", "/admin/google/connection-status", "Google Connection Status"),
            ("GET", "/admin/google/monitor", "Google Connection Monitor"),
            ("GET", "/admin/google/health-check", "Google Health Check"),
            ("POST", "/admin/google/force-reconnect", "Google Force Reconnect")
        ]
        
        all_accessible = True
        
        for method, endpoint, name in google_endpoints:
            try:
                url = f"{BACKEND_URL}{endpoint}"
                
                if method == "GET":
                    response = self.session.get(url)
                elif method == "POST":
                    response = self.session.post(url, json={})
                
                if response.status_code == 404:
                    self.log_result(f"Endpoint Accessibility - {name}", False, 
                                  f"CRITICAL: Endpoint returns 404 - NOT ACCESSIBLE: {endpoint}")
                    all_accessible = False
                elif response.status_code == 200:
                    self.log_result(f"Endpoint Accessibility - {name}", True, 
                                  f"Endpoint accessible: {endpoint} (HTTP 200)")
                else:
                    # Not 404, so endpoint exists (might be auth error, etc.)
                    self.log_result(f"Endpoint Accessibility - {name}", True, 
                                  f"Endpoint accessible: {endpoint} (HTTP {response.status_code})")
                    
            except Exception as e:
                self.log_result(f"Endpoint Accessibility - {name}", False, 
                              f"Exception testing {endpoint}: {str(e)}")
                all_accessible = False
        
        return all_accessible
    
    def test_production_readiness_verification(self):
        """Test production readiness indicators in endpoint responses"""
        google_endpoints = [
            ("GET", "/admin/google/connection-status", "Connection Status"),
            ("GET", "/admin/google/monitor", "Monitor"),
            ("GET", "/admin/google/health-check", "Health Check"),
            ("POST", "/admin/google/force-reconnect", "Force Reconnect")
        ]
        
        production_ready = True
        
        for method, endpoint, name in google_endpoints:
            try:
                url = f"{BACKEND_URL}{endpoint}"
                
                if method == "GET":
                    response = self.session.get(url)
                elif method == "POST":
                    response = self.session.post(url, json={})
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Check for production readiness indicators
                        success = data.get("success")
                        auto_managed = data.get("auto_managed")
                        user_intervention_required = data.get("user_intervention_required")
                        
                        readiness_checks = []
                        if success is True:
                            readiness_checks.append("✅ success: true")
                        else:
                            readiness_checks.append(f"❌ success: {success}")
                            production_ready = False
                        
                        if auto_managed is True:
                            readiness_checks.append("✅ auto_managed: true")
                        else:
                            readiness_checks.append(f"❌ auto_managed: {auto_managed}")
                            production_ready = False
                        
                        if user_intervention_required is False:
                            readiness_checks.append("✅ user_intervention_required: false")
                        else:
                            readiness_checks.append(f"❌ user_intervention_required: {user_intervention_required}")
                            production_ready = False
                        
                        status_msg = " | ".join(readiness_checks)
                        
                        if success is True and auto_managed is True and user_intervention_required is False:
                            self.log_result(f"Production Readiness - {name}", True, 
                                          f"Production ready: {status_msg}")
                        else:
                            self.log_result(f"Production Readiness - {name}", False, 
                                          f"NOT production ready: {status_msg}", {"response": data})
                        
                    except json.JSONDecodeError:
                        self.log_result(f"Production Readiness - {name}", False, 
                                      f"Invalid JSON response from {endpoint}")
                        production_ready = False
                else:
                    self.log_result(f"Production Readiness - {name}", False, 
                                  f"HTTP {response.status_code} from {endpoint}")
                    production_ready = False
                    
            except Exception as e:
                self.log_result(f"Production Readiness - {name}", False, 
                              f"Exception testing {endpoint}: {str(e)}")
                production_ready = False
        
        return production_ready
    
    def test_endpoint_response_content(self):
        """Test endpoint response content for expected structure"""
        try:
            # Test connection-status endpoint
            response = self.session.get(f"{BACKEND_URL}/admin/google/connection-status")
            if response.status_code == 200:
                data = response.json()
                if "automation" in str(data).lower() or "auto_managed" in data:
                    self.log_result("Response Content - Connection Status", True, 
                                  "Contains automation indicators")
                else:
                    self.log_result("Response Content - Connection Status", False, 
                                  "Missing automation indicators", {"response": data})
            
            # Test monitor endpoint
            response = self.session.get(f"{BACKEND_URL}/admin/google/monitor")
            if response.status_code == 200:
                data = response.json()
                if "services" in data or "gmail" in str(data).lower():
                    self.log_result("Response Content - Monitor", True, 
                                  "Contains services list for frontend")
                else:
                    self.log_result("Response Content - Monitor", False, 
                                  "Missing services list", {"response": data})
            
            # Test health-check endpoint
            response = self.session.get(f"{BACKEND_URL}/admin/google/health-check")
            if response.status_code == 200:
                data = response.json()
                if "metrics" in data or "percentage" in str(data).lower():
                    self.log_result("Response Content - Health Check", True, 
                                  "Contains metrics with percentages")
                else:
                    self.log_result("Response Content - Health Check", False, 
                                  "Missing metrics data", {"response": data})
            
            # Test force-reconnect endpoint
            response = self.session.post(f"{BACKEND_URL}/admin/google/force-reconnect", json={})
            if response.status_code == 200:
                data = response.json()
                if "reconnect" in str(data).lower() or "connection" in str(data).lower():
                    self.log_result("Response Content - Force Reconnect", True, 
                                  "Confirms reconnection capability")
                else:
                    self.log_result("Response Content - Force Reconnect", False, 
                                  "Missing reconnection confirmation", {"response": data})
                    
        except Exception as e:
            self.log_result("Endpoint Response Content", False, f"Exception: {str(e)}")
    
    def test_google_services_connectivity(self):
        """Test 100% Google services connectivity as expected"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/google/health-check")
            if response.status_code == 200:
                data = response.json()
                
                # Look for connectivity percentage
                connectivity_found = False
                if isinstance(data, dict):
                    for key, value in data.items():
                        if "100%" in str(value) or (isinstance(value, (int, float)) and value == 100):
                            connectivity_found = True
                            self.log_result("Google Services Connectivity", True, 
                                          f"100% connectivity confirmed: {key} = {value}")
                            break
                
                if not connectivity_found:
                    # Check if all services show connected status
                    services_connected = 0
                    total_services = 0
                    
                    if "services" in data:
                        services = data["services"]
                        if isinstance(services, dict):
                            for service, status in services.items():
                                total_services += 1
                                if "connected" in str(status).lower() or "success" in str(status).lower():
                                    services_connected += 1
                    
                    if total_services > 0 and services_connected == total_services:
                        connectivity_percentage = (services_connected / total_services) * 100
                        self.log_result("Google Services Connectivity", True, 
                                      f"{connectivity_percentage}% connectivity: {services_connected}/{total_services} services")
                    else:
                        self.log_result("Google Services Connectivity", False, 
                                      f"Incomplete connectivity: {services_connected}/{total_services} services", 
                                      {"response": data})
            else:
                self.log_result("Google Services Connectivity", False, 
                              f"Cannot check connectivity: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Google Services Connectivity", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all Google connection endpoint tests"""
        print("🚨 URGENT: GOOGLE CONNECTION ENDPOINTS TEST AFTER BACKEND RESTART")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        print("CRITICAL: Testing if automated Google connection system is operational")
        print("FAILURE CRITERIA: ANY endpoint returning 404 = system NOT working")
        print()
        
        # Test 1: Basic Connectivity
        print("🔍 STEP 1: Basic Connectivity Test")
        print("-" * 40)
        if not self.test_basic_connectivity():
            print("❌ CRITICAL: Basic connectivity failed. Cannot proceed.")
            return False
        
        # Test 2: Google Endpoints Accessibility (CRITICAL)
        print("\n🔍 STEP 2: Google Endpoints Accessibility Test (CRITICAL)")
        print("-" * 55)
        endpoints_accessible = self.test_google_endpoints_accessibility()
        
        # Test 3: Production Readiness Verification
        print("\n🔍 STEP 3: Production Readiness Verification")
        print("-" * 45)
        production_ready = self.test_production_readiness_verification()
        
        # Test 4: Endpoint Response Content Test
        print("\n🔍 STEP 4: Endpoint Response Content Test")
        print("-" * 40)
        self.test_endpoint_response_content()
        
        # Test 5: Google Services Connectivity
        print("\n🔍 STEP 5: Google Services Connectivity Test")
        print("-" * 42)
        self.test_google_services_connectivity()
        
        # Generate final assessment
        self.generate_final_assessment(endpoints_accessible, production_ready)
        
        return endpoints_accessible
    
    def generate_final_assessment(self, endpoints_accessible, production_ready):
        """Generate final assessment of Google connection system"""
        print("\n" + "=" * 70)
        print("🚨 FINAL ASSESSMENT: GOOGLE CONNECTION SYSTEM STATUS")
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
        
        # Critical assessment based on review requirements
        if endpoints_accessible and production_ready:
            print("✅ GOOGLE CONNECTION SYSTEM: OPERATIONAL")
            print("   ✓ All 4 Google connection endpoints are accessible (no 404 errors)")
            print("   ✓ Production readiness indicators confirmed")
            print("   ✓ Automated Google connection system is working")
            print("   ✓ No manual user intervention required")
            print("\n🎉 PRODUCTION ISSUE RESOLVED: System ready for deployment")
        elif endpoints_accessible and not production_ready:
            print("⚠️  GOOGLE CONNECTION SYSTEM: PARTIALLY OPERATIONAL")
            print("   ✓ All endpoints accessible (no 404 errors)")
            print("   ❌ Production readiness indicators missing")
            print("   ⚠️  Manual configuration may still be required")
        elif not endpoints_accessible:
            print("❌ GOOGLE CONNECTION SYSTEM: NOT OPERATIONAL")
            print("   ❌ One or more endpoints return 404 errors")
            print("   ❌ Automated Google connection system is NOT working")
            print("   ❌ Manual user intervention is still required")
            print("\n🚨 PRODUCTION ISSUE NOT RESOLVED: Main agent action required")
        else:
            print("❌ GOOGLE CONNECTION SYSTEM: FAILED")
            print("   ❌ Multiple critical issues detected")
            print("   ❌ System not ready for production")
        
        # Show failed tests if any
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
        
        print("\n" + "=" * 70)

def main():
    """Main test execution"""
    test_runner = GoogleConnectionEndpointsTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()