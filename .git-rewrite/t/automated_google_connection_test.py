#!/usr/bin/env python3
"""
AUTOMATED GOOGLE CONNECTION MANAGEMENT SYSTEM TEST
=================================================

This test verifies the newly implemented automated Google connection management system
that eliminates the need for manual user connections as requested in the review.

Key Features to Test:
1. Automated Connection Manager (auto_google_connection.py)
2. Production Monitoring Endpoints
3. Automated Connection Health
4. Production Readiness Verification
5. Frontend Integration

Expected Results:
- Google services automatically connected and managed
- No manual user intervention required
- Real-time monitoring working
- Auto-reconnection functional
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

class AutomatedGoogleConnectionTest:
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
    
    def test_automated_connection_manager_initialization(self):
        """Test if auto_google_connection.py is properly initializing on server startup"""
        try:
            # Test backend health to ensure server is running
            response = self.session.get(f"{BACKEND_URL}/health")
            if response.status_code == 200:
                health_data = response.json()
                self.log_result("Backend Server Health", True, 
                              f"Backend server is running and healthy")
                
                # Check if automated Google connection system is mentioned in health
                if "google" in str(health_data).lower() or "connection" in str(health_data).lower():
                    self.log_result("Auto Connection System Detection", True, 
                                  "Google connection system detected in health check")
                else:
                    self.log_result("Auto Connection System Detection", False, 
                                  "No Google connection system detected in health check", 
                                  {"health_data": health_data})
            else:
                self.log_result("Backend Server Health", False, 
                              f"Backend server health check failed: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Automated Connection Manager Initialization", False, f"Exception: {str(e)}")
    
    def test_service_account_credentials_loading(self):
        """Test if service account credentials are loading correctly"""
        try:
            # Test connection status endpoint to verify credentials
            response = self.session.get(f"{BACKEND_URL}/admin/google/connection-status")
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and data.get("production_ready"):
                    self.log_result("Service Account Credentials", True, 
                                  "Service account credentials loaded successfully",
                                  {"connection_status": data.get("connection_status", {})})
                else:
                    self.log_result("Service Account Credentials", False, 
                                  "Service account credentials not properly loaded", 
                                  {"response": data})
            else:
                self.log_result("Service Account Credentials", False, 
                              f"Failed to check credentials: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Service Account Credentials Loading", False, f"Exception: {str(e)}")
    
    def test_google_services_auto_connection(self):
        """Test if Google services are auto-connecting (Gmail, Calendar, Drive, Meet)"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/google/connection-status")
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    connection_status = data.get("connection_status", {})
                    services = connection_status.get("services", {})
                    
                    expected_services = ["gmail", "calendar", "drive", "meet"]
                    connected_services = []
                    failed_services = []
                    
                    for service in expected_services:
                        if service in services:
                            if services[service].get("connected"):
                                connected_services.append(service)
                            else:
                                failed_services.append(service)
                        else:
                            failed_services.append(f"{service} (not found)")
                    
                    if len(connected_services) == len(expected_services):
                        self.log_result("Google Services Auto-Connection", True, 
                                      f"All {len(connected_services)} Google services auto-connected successfully",
                                      {"connected_services": connected_services})
                    elif len(connected_services) > 0:
                        self.log_result("Google Services Auto-Connection", False, 
                                      f"Partial connection: {len(connected_services)}/{len(expected_services)} services connected",
                                      {"connected": connected_services, "failed": failed_services})
                    else:
                        self.log_result("Google Services Auto-Connection", False, 
                                      "No Google services auto-connected",
                                      {"failed_services": failed_services})
                else:
                    self.log_result("Google Services Auto-Connection", False, 
                                  "Connection status check failed", {"response": data})
            else:
                self.log_result("Google Services Auto-Connection", False, 
                              f"Failed to get connection status: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Google Services Auto-Connection", False, f"Exception: {str(e)}")
    
    def test_production_monitoring_endpoints(self):
        """Test production monitoring endpoints"""
        endpoints_to_test = [
            ("/admin/google/connection-status", "Real-time Connection Status"),
            ("/admin/google/monitor", "Frontend Dashboard Monitor"),
            ("/admin/google/health-check", "Health Check with Metrics")
        ]
        
        for endpoint, name in endpoints_to_test:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("success"):
                        # Check for key production readiness indicators
                        auto_managed = data.get("auto_managed") or data.get("monitoring_active")
                        user_intervention = data.get("user_intervention_required", True)
                        
                        if auto_managed and not user_intervention:
                            self.log_result(f"Production Endpoint - {name}", True, 
                                          f"Endpoint working with production readiness confirmed",
                                          {"auto_managed": auto_managed, "user_intervention_required": user_intervention})
                        else:
                            self.log_result(f"Production Endpoint - {name}", False, 
                                          f"Endpoint working but not production ready",
                                          {"auto_managed": auto_managed, "user_intervention_required": user_intervention})
                    else:
                        self.log_result(f"Production Endpoint - {name}", False, 
                                      f"Endpoint returned success=false", {"response": data})
                else:
                    self.log_result(f"Production Endpoint - {name}", False, 
                                  f"HTTP {response.status_code}: {endpoint}")
                    
            except Exception as e:
                self.log_result(f"Production Endpoint - {name}", False, 
                              f"Exception on {endpoint}: {str(e)}")
    
    def test_force_reconnect_admin_tool(self):
        """Test POST /api/admin/google/force-reconnect admin tool"""
        try:
            response = self.session.post(f"{BACKEND_URL}/admin/google/force-reconnect")
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and data.get("reconnection_forced"):
                    self.log_result("Force Reconnect Admin Tool", True, 
                                  "Force reconnection tool working correctly",
                                  {"connection_status": data.get("connection_status", {})})
                else:
                    self.log_result("Force Reconnect Admin Tool", False, 
                                  "Force reconnection failed", {"response": data})
            else:
                self.log_result("Force Reconnect Admin Tool", False, 
                              f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Force Reconnect Admin Tool", False, f"Exception: {str(e)}")
    
    def test_automated_connection_health_monitoring(self):
        """Test if system detects and reports connection status automatically"""
        try:
            # Test health check endpoint for comprehensive metrics
            response = self.session.get(f"{BACKEND_URL}/admin/google/health-check")
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    health_percentage = data.get("health_percentage", 0)
                    overall_status = data.get("overall_status", "UNKNOWN")
                    auto_managed = data.get("auto_managed", False)
                    production_ready = data.get("production_ready", False)
                    
                    if health_percentage >= 75 and auto_managed and production_ready:
                        self.log_result("Automated Health Monitoring", True, 
                                      f"Health monitoring working: {health_percentage}% health, {overall_status} status",
                                      {"health_metrics": {
                                          "health_percentage": health_percentage,
                                          "overall_status": overall_status,
                                          "auto_managed": auto_managed,
                                          "production_ready": production_ready
                                      }})
                    else:
                        self.log_result("Automated Health Monitoring", False, 
                                      f"Health monitoring issues: {health_percentage}% health, auto_managed={auto_managed}",
                                      {"health_metrics": data})
                else:
                    self.log_result("Automated Health Monitoring", False, 
                                  "Health check failed", {"response": data})
            else:
                self.log_result("Automated Health Monitoring", False, 
                              f"Health check endpoint failed: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Automated Health Monitoring", False, f"Exception: {str(e)}")
    
    def test_continuous_monitoring_system(self):
        """Test if continuous monitoring is working (every 5 minutes)"""
        try:
            # Get connection status and check for monitoring indicators
            response = self.session.get(f"{BACKEND_URL}/admin/google/connection-status")
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    connection_status = data.get("connection_status", {})
                    last_monitoring_check = connection_status.get("last_monitoring_check")
                    auto_managed = connection_status.get("auto_managed", False)
                    
                    if last_monitoring_check and auto_managed:
                        self.log_result("Continuous Monitoring System", True, 
                                      f"Continuous monitoring active with last check: {last_monitoring_check}",
                                      {"last_check": last_monitoring_check, "auto_managed": auto_managed})
                    else:
                        self.log_result("Continuous Monitoring System", False, 
                                      "Continuous monitoring not detected",
                                      {"last_check": last_monitoring_check, "auto_managed": auto_managed})
                else:
                    self.log_result("Continuous Monitoring System", False, 
                                  "Failed to check monitoring status", {"response": data})
            else:
                self.log_result("Continuous Monitoring System", False, 
                              f"Failed to get monitoring status: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Continuous Monitoring System", False, f"Exception: {str(e)}")
    
    def test_production_readiness_verification(self):
        """Test production readiness verification"""
        try:
            # Test all endpoints for production readiness indicators
            endpoints = [
                "/admin/google/connection-status",
                "/admin/google/monitor", 
                "/admin/google/health-check"
            ]
            
            production_ready_count = 0
            user_intervention_required_count = 0
            auto_managed_count = 0
            
            for endpoint in endpoints:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("production_ready") or data.get("monitoring_active"):
                        production_ready_count += 1
                    
                    if not data.get("user_intervention_required", True):
                        user_intervention_required_count += 1
                    
                    if data.get("auto_managed"):
                        auto_managed_count += 1
            
            total_endpoints = len(endpoints)
            
            if (production_ready_count >= 2 and 
                user_intervention_required_count >= 2 and 
                auto_managed_count >= 2):
                self.log_result("Production Readiness Verification", True, 
                              f"Production readiness confirmed across {total_endpoints} endpoints",
                              {
                                  "production_ready": production_ready_count,
                                  "no_user_intervention": user_intervention_required_count,
                                  "auto_managed": auto_managed_count
                              })
            else:
                self.log_result("Production Readiness Verification", False, 
                              f"Production readiness not fully confirmed",
                              {
                                  "production_ready": f"{production_ready_count}/{total_endpoints}",
                                  "no_user_intervention": f"{user_intervention_required_count}/{total_endpoints}",
                                  "auto_managed": f"{auto_managed_count}/{total_endpoints}"
                              })
                
        except Exception as e:
            self.log_result("Production Readiness Verification", False, f"Exception: {str(e)}")
    
    def test_frontend_integration_compatibility(self):
        """Test that frontend can retrieve status without manual connection"""
        try:
            # Test monitor endpoint specifically designed for frontend
            response = self.session.get(f"{BACKEND_URL}/admin/google/monitor")
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    # Check for frontend-friendly format
                    services = data.get("services", [])
                    user_connection_required = data.get("user_connection_required", True)
                    monitoring_active = data.get("monitoring_active", False)
                    
                    if (len(services) >= 4 and 
                        not user_connection_required and 
                        monitoring_active):
                        self.log_result("Frontend Integration", True, 
                                      f"Frontend integration ready: {len(services)} services, no user connection required",
                                      {
                                          "services_count": len(services),
                                          "user_connection_required": user_connection_required,
                                          "monitoring_active": monitoring_active
                                      })
                    else:
                        self.log_result("Frontend Integration", False, 
                                      f"Frontend integration issues detected",
                                      {
                                          "services_count": len(services),
                                          "user_connection_required": user_connection_required,
                                          "monitoring_active": monitoring_active
                                      })
                else:
                    self.log_result("Frontend Integration", False, 
                                  "Frontend monitor endpoint failed", {"response": data})
            else:
                self.log_result("Frontend Integration", False, 
                              f"Frontend monitor endpoint error: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Frontend Integration", False, f"Exception: {str(e)}")
    
    def test_no_manual_connection_required(self):
        """Test that manual 'Connect Google Workspace' is no longer needed"""
        try:
            # Check all endpoints to ensure no manual connection prompts
            response = self.session.get(f"{BACKEND_URL}/admin/google/monitor")
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    subtitle = data.get("subtitle", "")
                    user_connection_required = data.get("user_connection_required", True)
                    
                    if ("No user action required" in subtitle and 
                        not user_connection_required):
                        self.log_result("No Manual Connection Required", True, 
                                      "System confirms no manual connection required",
                                      {"subtitle": subtitle, "user_connection_required": user_connection_required})
                    else:
                        self.log_result("No Manual Connection Required", False, 
                                      "System still requires manual connection",
                                      {"subtitle": subtitle, "user_connection_required": user_connection_required})
                else:
                    self.log_result("No Manual Connection Required", False, 
                                  "Failed to check manual connection requirement", {"response": data})
            else:
                self.log_result("No Manual Connection Required", False, 
                              f"Failed to check connection requirement: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("No Manual Connection Required", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all automated Google connection management tests"""
        print("🤖 AUTOMATED GOOGLE CONNECTION MANAGEMENT SYSTEM TEST")
        print("=" * 65)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Automated Google Connection Tests...")
        print("-" * 55)
        
        # Run all tests
        self.test_automated_connection_manager_initialization()
        self.test_service_account_credentials_loading()
        self.test_google_services_auto_connection()
        self.test_production_monitoring_endpoints()
        self.test_force_reconnect_admin_tool()
        self.test_automated_connection_health_monitoring()
        self.test_continuous_monitoring_system()
        self.test_production_readiness_verification()
        self.test_frontend_integration_compatibility()
        self.test_no_manual_connection_required()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 65)
        print("🤖 AUTOMATED GOOGLE CONNECTION TEST SUMMARY")
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
        
        # Critical assessment for automated system
        critical_tests = [
            "Google Services Auto-Connection",
            "Production Readiness Verification", 
            "No Manual Connection Required",
            "Automated Health Monitoring",
            "Frontend Integration"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(critical in result['test'] for critical in critical_tests))
        
        print("🚨 CRITICAL ASSESSMENT:")
        if critical_passed >= 4:  # At least 4 out of 5 critical tests
            print("✅ AUTOMATED GOOGLE CONNECTION SYSTEM: OPERATIONAL")
            print("   Google services are automatically managed without user intervention.")
            print("   System ready for production deployment with automated management.")
        else:
            print("❌ AUTOMATED GOOGLE CONNECTION SYSTEM: NOT READY")
            print("   Critical automated connection issues found.")
            print("   Manual intervention may still be required.")
        
        print("\n" + "=" * 65)

def main():
    """Main test execution"""
    test_runner = AutomatedGoogleConnectionTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()