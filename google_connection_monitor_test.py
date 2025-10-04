#!/usr/bin/env python3
"""
Google Connection Monitor Endpoints Testing
Tests the new Google Connection Monitor endpoints added to FIDUS backend
"""

import requests
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')
load_dotenv('/app/frontend/.env')

# Get backend URL from frontend environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://invest-manager-9.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class GoogleConnectionMonitorTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            login_data = {
                "username": "admin",
                "password": "password123",
                "user_type": "admin"
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                self.session.headers.update({'Authorization': f'Bearer {self.admin_token}'})
                self.log_test("Admin Authentication", True, f"Successfully authenticated as admin with JWT token")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def test_admin_auth_required(self):
        """Test that endpoints require admin authentication"""
        try:
            # Test without authentication
            temp_session = requests.Session()
            
            endpoints = [
                "/google/connection/test-all",
                "/google/connection/test/gmail", 
                "/google/connection/history"
            ]
            
            auth_failures = 0
            for endpoint in endpoints:
                response = temp_session.get(f"{API_BASE}{endpoint}")
                if response.status_code == 401:
                    auth_failures += 1
                    
            if auth_failures == len(endpoints):
                self.log_test("Admin Authentication Required", True, f"All {len(endpoints)} endpoints properly require admin authentication (401 Unauthorized)")
                return True
            else:
                self.log_test("Admin Authentication Required", False, f"Only {auth_failures}/{len(endpoints)} endpoints require authentication")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication Required", False, f"Auth test error: {str(e)}")
            return False
    
    def test_connection_test_all(self):
        """Test /api/google/connection/test-all endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/google/connection/test-all")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ['success', 'overall_status', 'services', 'connection_quality']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Test All Connections - Structure", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Verify services structure
                expected_services = ['gmail', 'calendar', 'drive', 'meet']
                services = data.get('services', {})
                missing_services = [svc for svc in expected_services if svc not in services]
                
                if missing_services:
                    self.log_test("Test All Connections - Services", False, f"Missing services: {missing_services}")
                    return False
                
                # Verify connection quality metrics
                quality = data.get('connection_quality', {})
                quality_fields = ['total_tests', 'successful_tests', 'success_rate', 'last_test_time']
                missing_quality = [field for field in quality_fields if field not in quality]
                
                if missing_quality:
                    self.log_test("Test All Connections - Quality Metrics", False, f"Missing quality fields: {missing_quality}")
                    return False
                
                # Check if response includes timing metrics
                has_timing = any('response_time_ms' in service for service in services.values() if isinstance(service, dict))
                
                self.log_test("Test All Connections", True, 
                    f"Endpoint working correctly. Status: {data.get('overall_status')}, "
                    f"Success rate: {quality.get('success_rate', 0)}%, "
                    f"Services tested: {len(services)}, "
                    f"Timing metrics: {'Yes' if has_timing else 'No'}")
                return True
                
            else:
                self.log_test("Test All Connections", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Test All Connections", False, f"Request error: {str(e)}")
            return False
    
    def test_individual_service_endpoints(self):
        """Test individual service endpoints"""
        services = ['gmail', 'calendar', 'drive', 'meet']
        successful_tests = 0
        
        for service in services:
            try:
                response = self.session.get(f"{API_BASE}/google/connection/test/{service}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify response structure
                    required_fields = ['success', 'service', 'status', 'message']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_test(f"Individual Service Test - {service.title()}", False, f"Missing fields: {missing_fields}")
                        continue
                    
                    # Verify service name matches
                    if data.get('service') != service:
                        self.log_test(f"Individual Service Test - {service.title()}", False, f"Service mismatch: expected {service}, got {data.get('service')}")
                        continue
                    
                    # Check for response time metrics
                    has_response_time = 'response_time_ms' in data
                    
                    # Check for troubleshooting information
                    has_troubleshooting = 'troubleshooting_steps' in data
                    
                    self.log_test(f"Individual Service Test - {service.title()}", True, 
                        f"Status: {data.get('status')}, "
                        f"Response time: {'Yes' if has_response_time else 'No'}, "
                        f"Troubleshooting: {'Yes' if has_troubleshooting else 'No'}")
                    successful_tests += 1
                    
                else:
                    self.log_test(f"Individual Service Test - {service.title()}", False, f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_test(f"Individual Service Test - {service.title()}", False, f"Request error: {str(e)}")
        
        return successful_tests == len(services)
    
    def test_invalid_service_name(self):
        """Test invalid service name handling"""
        try:
            response = self.session.get(f"{API_BASE}/google/connection/test/invalid_service")
            
            if response.status_code == 200:
                data = response.json()
                # Check if the response indicates an error for invalid service
                if (data.get('success') == False and 
                    'Invalid service' in data.get('message', '') and
                    data.get('status') == 'test_failed'):
                    self.log_test("Invalid Service Name Handling", True, "Properly handles invalid service names with structured error response")
                    return True
                else:
                    self.log_test("Invalid Service Name Handling", False, f"Wrong error response: {data}")
                    return False
            else:
                self.log_test("Invalid Service Name Handling", False, f"Expected 200 with error details, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Invalid Service Name Handling", False, f"Request error: {str(e)}")
            return False
    
    def test_connection_history(self):
        """Test /api/google/connection/history endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/google/connection/history")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ['success', 'history', 'summary']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Connection History - Structure", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Verify history data structure
                history = data.get('history', [])
                if not isinstance(history, list):
                    self.log_test("Connection History - History Format", False, "History should be a list")
                    return False
                
                if len(history) > 0:
                    # Check first history entry structure
                    first_entry = history[0]
                    history_fields = ['timestamp', 'success_rate', 'average_response_time_ms', 'services_tested']
                    missing_history_fields = [field for field in history_fields if field not in first_entry]
                    
                    if missing_history_fields:
                        self.log_test("Connection History - Entry Structure", False, f"Missing history fields: {missing_history_fields}")
                        return False
                
                # Verify summary structure
                summary = data.get('summary', {})
                summary_fields = ['total_tests', 'average_success_rate', 'average_response_time', 'uptime_percentage']
                missing_summary_fields = [field for field in summary_fields if field not in summary]
                
                if missing_summary_fields:
                    self.log_test("Connection History - Summary Structure", False, f"Missing summary fields: {missing_summary_fields}")
                    return False
                
                self.log_test("Connection History", True, 
                    f"History entries: {len(history)}, "
                    f"Avg success rate: {summary.get('average_success_rate', 0):.1f}%, "
                    f"Uptime: {summary.get('uptime_percentage', 0)}%")
                return True
                
            else:
                self.log_test("Connection History", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Connection History", False, f"Request error: {str(e)}")
            return False
    
    def test_response_format_validation(self):
        """Test that all endpoints return proper JSON with expected fields"""
        try:
            endpoints_to_test = [
                ("/google/connection/test-all", ["success", "overall_status", "services", "connection_quality"]),
                ("/google/connection/test/gmail", ["success", "service", "status", "message"]),
                ("/google/connection/history", ["success", "history", "summary"])
            ]
            
            format_tests_passed = 0
            
            for endpoint, required_fields in endpoints_to_test:
                response = self.session.get(f"{API_BASE}{endpoint}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        missing_fields = [field for field in required_fields if field not in data]
                        
                        if not missing_fields:
                            format_tests_passed += 1
                        else:
                            self.log_test(f"Response Format - {endpoint}", False, f"Missing fields: {missing_fields}")
                    except json.JSONDecodeError:
                        self.log_test(f"Response Format - {endpoint}", False, "Invalid JSON response")
                else:
                    self.log_test(f"Response Format - {endpoint}", False, f"HTTP {response.status_code}")
            
            if format_tests_passed == len(endpoints_to_test):
                self.log_test("Response Format Validation", True, f"All {len(endpoints_to_test)} endpoints return proper JSON format")
                return True
            else:
                self.log_test("Response Format Validation", False, f"Only {format_tests_passed}/{len(endpoints_to_test)} endpoints have proper format")
                return False
                
        except Exception as e:
            self.log_test("Response Format Validation", False, f"Format test error: {str(e)}")
            return False
    
    def test_error_scenarios(self):
        """Test various error scenarios"""
        try:
            error_tests_passed = 0
            total_error_tests = 2
            
            # Test 1: Invalid service name (structured error response)
            response = self.session.get(f"{API_BASE}/google/connection/test/nonexistent")
            if response.status_code == 200:
                data = response.json()
                if (data.get('success') == False and 
                    'Invalid service' in data.get('message', '') and
                    data.get('status') == 'test_failed'):
                    error_tests_passed += 1
            
            # Test 2: Test endpoints handle missing authentication gracefully
            temp_session = requests.Session()
            response = temp_session.get(f"{API_BASE}/google/connection/test-all")
            if response.status_code == 401:
                error_tests_passed += 1
            
            if error_tests_passed == total_error_tests:
                self.log_test("Error Scenario Handling", True, f"All {total_error_tests} error scenarios handled correctly")
                return True
            else:
                self.log_test("Error Scenario Handling", False, f"Only {error_tests_passed}/{total_error_tests} error scenarios handled correctly")
                return False
                
        except Exception as e:
            self.log_test("Error Scenario Handling", False, f"Error scenario test failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all Google Connection Monitor tests"""
        print("🔍 Starting Google Connection Monitor Endpoints Testing...")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        # Step 1: Test authentication requirements (before login)
        self.test_admin_auth_required()
        
        # Step 2: Authenticate as admin
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Step 3: Run all endpoint tests
        tests = [
            self.test_connection_test_all,
            self.test_individual_service_endpoints,
            self.test_invalid_service_name,
            self.test_connection_history,
            self.test_response_format_validation,
            self.test_error_scenarios
        ]
        
        passed_tests = 0
        for test in tests:
            if test():
                passed_tests += 1
        
        # Summary
        print("=" * 80)
        print(f"📊 GOOGLE CONNECTION MONITOR TESTING SUMMARY")
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Passed: {sum(1 for r in self.test_results if r['success'])}")
        print(f"Failed: {sum(1 for r in self.test_results if not r['success'])}")
        print(f"Success Rate: {(sum(1 for r in self.test_results if r['success']) / len(self.test_results) * 100):.1f}%")
        
        # Show failed tests
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        return len(failed_tests) == 0

def main():
    """Main test execution"""
    tester = GoogleConnectionMonitorTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL GOOGLE CONNECTION MONITOR TESTS PASSED!")
        exit(0)
    else:
        print("\n⚠️  SOME TESTS FAILED - CHECK RESULTS ABOVE")
        exit(1)

if __name__ == "__main__":
    main()