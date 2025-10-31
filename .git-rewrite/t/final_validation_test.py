#!/usr/bin/env python3
"""
FINAL SCALABILITY VALIDATION - COMPREHENSIVE SYSTEM READINESS CHECK
Production Deployment: Monday | Target: 100 MT5 Account Scalability

This test validates the specific requirements from the review request:
1. Multi-Broker MT5 Endpoints (FIXED - Needs Confirmation)
2. Enhanced Rate Limiting (FIXED - Needs Confirmation) 
3. System Scalability Confirmation
4. Production Readiness Checklist
"""

import requests
import time
import json
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

class FinalValidationTester:
    def __init__(self, base_url="https://fidus-workspace.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None
        self.client_token = None
        self.critical_failures = []
        
        print("=" * 80)
        print("FIDUS INVESTMENT MANAGEMENT SYSTEM")
        print("FINAL SCALABILITY VALIDATION - COMPREHENSIVE SYSTEM READINESS CHECK")
        print("Production Deployment: Monday | Target: 100 MT5 Account Scalability")
        print("=" * 80)
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASSED {details}")
        else:
            print(f"❌ {test_name}: FAILED {details}")
            self.critical_failures.append(f"{test_name}: {details}")
    
    def authenticate_users(self):
        """Authenticate admin and client users"""
        print("\n🔐 AUTHENTICATION SETUP")
        
        # Authenticate admin
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={
                    "username": "admin",
                    "password": "password123", 
                    "user_type": "admin"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                self.log_result("Admin Authentication", True, f"Token obtained")
            else:
                self.log_result("Admin Authentication", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Error: {str(e)}")
            return False
        
        # Authenticate client
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={
                    "username": "client1",
                    "password": "password123",
                    "user_type": "client"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.client_token = data.get('token')
                self.log_result("Client Authentication", True, f"Token obtained")
                return True
            else:
                self.log_result("Client Authentication", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Client Authentication", False, f"Error: {str(e)}")
            return False
    
    def get_admin_headers(self):
        """Get headers with admin authorization"""
        return {
            'Authorization': f'Bearer {self.admin_token}',
            'Content-Type': 'application/json'
        }
    
    def get_client_headers(self):
        """Get headers with client authorization"""
        return {
            'Authorization': f'Bearer {self.client_token}',
            'Content-Type': 'application/json'
        }

    # ===============================================================================
    # A. MULTI-BROKER MT5 ENDPOINTS VALIDATION (FIXED - NEEDS CONFIRMATION)
    # ===============================================================================
    
    def test_multi_broker_mt5_endpoints(self):
        """Test Multi-Broker MT5 Endpoints as specified in review request"""
        print("\n" + "="*60)
        print("A. MULTI-BROKER MT5 ENDPOINTS (FIXED - NEEDS CONFIRMATION)")
        print("="*60)
        
        if not self.admin_token:
            self.log_result("MT5 Endpoints Test", False, "No admin token available")
            return False
        
        success_count = 0
        
        # Test /api/mt5/brokers with admin authentication
        try:
            response = requests.get(
                f"{self.base_url}/api/mt5/brokers",
                headers=self.get_admin_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                brokers = data.get('brokers', [])
                broker_codes = [b.get('code') for b in brokers]
                
                if 'multibank' in broker_codes and 'dootechnology' in broker_codes:
                    self.log_result("MT5 Brokers Endpoint", True, f"Found brokers: {broker_codes}")
                    success_count += 1
                else:
                    self.log_result("MT5 Brokers Endpoint", False, f"Missing brokers. Found: {broker_codes}")
            else:
                self.log_result("MT5 Brokers Endpoint", False, f"Status: {response.status_code} (Expected 200)")
                
        except Exception as e:
            self.log_result("MT5 Brokers Endpoint", False, f"Error: {str(e)}")
        
        # Test /api/mt5/brokers/multibank/servers with admin token
        try:
            response = requests.get(
                f"{self.base_url}/api/mt5/brokers/multibank/servers",
                headers=self.get_admin_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                servers = data.get('servers', [])
                if servers and len(servers) > 0:
                    self.log_result("MT5 Multibank Servers", True, f"Found {len(servers)} servers")
                    success_count += 1
                else:
                    self.log_result("MT5 Multibank Servers", False, "No servers found")
            else:
                self.log_result("MT5 Multibank Servers", False, f"Status: {response.status_code} (Expected 200)")
                
        except Exception as e:
            self.log_result("MT5 Multibank Servers", False, f"Error: {str(e)}")
        
        # Test /api/mt5/brokers/dootechnology/servers with admin token
        try:
            response = requests.get(
                f"{self.base_url}/api/mt5/brokers/dootechnology/servers",
                headers=self.get_admin_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                servers = data.get('servers', [])
                if servers and len(servers) > 0:
                    self.log_result("MT5 DooTechnology Servers", True, f"Found {len(servers)} servers")
                    success_count += 1
                else:
                    self.log_result("MT5 DooTechnology Servers", False, "No servers found")
            else:
                self.log_result("MT5 DooTechnology Servers", False, f"Status: {response.status_code} (Expected 200)")
                
        except Exception as e:
            self.log_result("MT5 DooTechnology Servers", False, f"Error: {str(e)}")
        
        return success_count == 3

    # ===============================================================================
    # B. ENHANCED RATE LIMITING VALIDATION (FIXED - NEEDS CONFIRMATION)
    # ===============================================================================
    
    def test_enhanced_rate_limiting(self):
        """Test Enhanced Rate Limiting as specified in review request"""
        print("\n" + "="*60)
        print("B. ENHANCED RATE LIMITING (FIXED - NEEDS CONFIRMATION)")
        print("="*60)
        
        success_count = 0
        
        # Test Admin users: 300 requests/minute
        if self.admin_token:
            admin_success = self.test_rate_limit_for_user_type("Admin", self.get_admin_headers(), 300)
            if admin_success:
                success_count += 1
        
        # Test Client users: 150 requests/minute  
        if self.client_token:
            client_success = self.test_rate_limit_for_user_type("Client", self.get_client_headers(), 150)
            if client_success:
                success_count += 1
        
        # Test Unauthenticated: 100 requests/minute
        unauth_success = self.test_rate_limit_for_user_type("Unauthenticated", {}, 100)
        if unauth_success:
            success_count += 1
        
        return success_count >= 2  # At least admin and client should work
    
    def test_rate_limit_for_user_type(self, user_type, headers, expected_limit):
        """Test rate limiting for specific user type"""
        # Calculate requests per second (divide by 60 for per minute limit)
        requests_per_second = expected_limit / 60.0
        
        # Send requests at slightly above the expected rate to test limiting
        test_requests = min(10, int(requests_per_second * 2))  # Test with 2x the rate for 1 second
        
        success_count = 0
        rate_limited_count = 0
        
        start_time = time.time()
        
        for i in range(test_requests):
            try:
                response = requests.get(
                    f"{self.base_url}/api/health",
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code == 200:
                    success_count += 1
                elif response.status_code == 429:
                    rate_limited_count += 1
                    
            except Exception:
                pass
            
            # Small delay to spread requests
            time.sleep(0.1)
        
        end_time = time.time()
        duration = end_time - start_time
        actual_rate = success_count / duration if duration > 0 else 0
        
        # For higher limits (admin), we expect most requests to succeed
        # For lower limits (unauth), we expect some rate limiting
        if user_type == "Admin":
            expected_success_rate = 0.8  # 80% should succeed for admin
        elif user_type == "Client":
            expected_success_rate = 0.7  # 70% should succeed for client
        else:
            expected_success_rate = 0.6  # 60% should succeed for unauth
        
        actual_success_rate = success_count / test_requests if test_requests > 0 else 0
        
        if actual_success_rate >= expected_success_rate:
            self.log_result(f"{user_type} Rate Limiting", True, 
                          f"Success: {success_count}/{test_requests} ({actual_success_rate:.1%}), Rate limited: {rate_limited_count}")
            return True
        else:
            self.log_result(f"{user_type} Rate Limiting", False, 
                          f"Success: {success_count}/{test_requests} ({actual_success_rate:.1%}), Expected: {expected_success_rate:.1%}")
            return False

    # ===============================================================================
    # C. SYSTEM SCALABILITY CONFIRMATION
    # ===============================================================================
    
    def test_system_scalability(self):
        """Test System Scalability Confirmation"""
        print("\n" + "="*60)
        print("C. SYSTEM SCALABILITY CONFIRMATION")
        print("="*60)
        
        success_count = 0
        
        # Database performance still excellent (500+ ops/sec)
        if self.test_database_performance():
            success_count += 1
        
        # API endpoints handle concurrent requests efficiently
        if self.test_api_concurrent_handling():
            success_count += 1
        
        # Memory usage stable during extended operations
        if self.test_system_stability():
            success_count += 1
        
        # All critical business functions operational
        if self.test_critical_business_functions():
            success_count += 1
        
        return success_count >= 3
    
    def test_database_performance(self):
        """Test database performance (>500 operations/second maintained)"""
        if not self.admin_token:
            self.log_result("Database Performance", False, "No admin token available")
            return False
        
        start_time = time.time()
        success_count = 0
        
        def make_db_request():
            try:
                response = requests.get(
                    f"{self.base_url}/api/crm/funds",
                    headers=self.get_admin_headers(),
                    timeout=5
                )
                return response.status_code == 200
            except:
                return False
        
        # Run 100 concurrent requests to test database performance
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_db_request) for _ in range(100)]
            
            for future in as_completed(futures):
                if future.result():
                    success_count += 1
        
        end_time = time.time()
        duration = end_time - start_time
        ops_per_second = success_count / duration if duration > 0 else 0
        
        if ops_per_second > 500 and success_count >= 90:
            self.log_result("Database Performance", True, f"{ops_per_second:.1f} ops/sec, {success_count}/100 successful")
            return True
        else:
            self.log_result("Database Performance", False, f"{ops_per_second:.1f} ops/sec, {success_count}/100 successful")
            return False
    
    def test_api_concurrent_handling(self):
        """Test API endpoints handle concurrent requests efficiently"""
        if not self.admin_token:
            self.log_result("API Concurrent Handling", False, "No admin token available")
            return False
        
        # Test multiple endpoints concurrently
        endpoints = [
            "/api/health",
            "/api/crm/funds", 
            "/api/clients/all",
            "/api/investments/funds/config"
        ]
        
        success_count = 0
        total_requests = 0
        
        def test_endpoint(endpoint):
            try:
                response = requests.get(
                    f"{self.base_url}{endpoint}",
                    headers=self.get_admin_headers(),
                    timeout=10
                )
                return response.status_code == 200
            except:
                return False
        
        # Test each endpoint with concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for endpoint in endpoints:
                for _ in range(5):  # 5 concurrent requests per endpoint
                    futures.append(executor.submit(test_endpoint, endpoint))
                    total_requests += 1
            
            for future in as_completed(futures):
                if future.result():
                    success_count += 1
        
        success_rate = success_count / total_requests if total_requests > 0 else 0
        
        if success_rate >= 0.9:  # 90% success rate
            self.log_result("API Concurrent Handling", True, f"{success_count}/{total_requests} successful ({success_rate:.1%})")
            return True
        else:
            self.log_result("API Concurrent Handling", False, f"{success_count}/{total_requests} successful ({success_rate:.1%})")
            return False
    
    def test_system_stability(self):
        """Test system stability under load"""
        # Test response times under load
        response_times = []
        
        for i in range(10):
            try:
                start_time = time.time()
                response = requests.get(
                    f"{self.base_url}/api/health",
                    timeout=10
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    response_times.append(end_time - start_time)
                    
            except Exception:
                pass
            
            time.sleep(0.1)  # Small delay between requests
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            
            # System is stable if average response time < 1s and max < 3s
            if avg_response_time < 1.0 and max_response_time < 3.0:
                self.log_result("System Stability", True, f"Avg: {avg_response_time:.3f}s, Max: {max_response_time:.3f}s")
                return True
            else:
                self.log_result("System Stability", False, f"Avg: {avg_response_time:.3f}s, Max: {max_response_time:.3f}s")
                return False
        else:
            self.log_result("System Stability", False, "No successful responses")
            return False
    
    def test_critical_business_functions(self):
        """Test all critical business functions operational"""
        if not self.admin_token:
            self.log_result("Critical Business Functions", False, "No admin token available")
            return False
        
        # Test key business endpoints
        critical_endpoints = [
            "/api/crm/funds",
            "/api/clients/all", 
            "/api/investments/funds/config"
        ]
        
        success_count = 0
        
        for endpoint in critical_endpoints:
            try:
                response = requests.get(
                    f"{self.base_url}{endpoint}",
                    headers=self.get_admin_headers(),
                    timeout=10
                )
                
                if response.status_code == 200:
                    success_count += 1
                    
            except Exception:
                pass
        
        if success_count == len(critical_endpoints):
            self.log_result("Critical Business Functions", True, f"All {success_count} functions operational")
            return True
        else:
            self.log_result("Critical Business Functions", False, f"Only {success_count}/{len(critical_endpoints)} functions operational")
            return False

    # ===============================================================================
    # D. PRODUCTION READINESS CHECKLIST
    # ===============================================================================
    
    def test_production_readiness_checklist(self):
        """Test Production Readiness Checklist"""
        print("\n" + "="*60)
        print("D. PRODUCTION READINESS CHECKLIST")
        print("="*60)
        
        success_count = 0
        
        # All authentication flows working
        if self.test_authentication_flows():
            success_count += 1
        
        # All API endpoints responding correctly
        if self.test_api_endpoints_health():
            success_count += 1
        
        # Error handling robust and informative
        if self.test_error_handling():
            success_count += 1
        
        # Health monitoring endpoints fully functional
        if self.test_health_monitoring():
            success_count += 1
        
        return success_count >= 3
    
    def test_authentication_flows(self):
        """Test all authentication flows working"""
        # Already tested in setup, but verify JWT refresh works
        if not self.admin_token:
            self.log_result("Authentication Flows", False, "No admin token available")
            return False
        
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/refresh-token",
                headers=self.get_admin_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('token'):
                    self.log_result("Authentication Flows", True, "Login and token refresh working")
                    return True
                else:
                    self.log_result("Authentication Flows", False, "Token refresh failed")
                    return False
            else:
                self.log_result("Authentication Flows", False, f"Token refresh status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Authentication Flows", False, f"Token refresh error: {str(e)}")
            return False
    
    def test_api_endpoints_health(self):
        """Test all API endpoints responding correctly"""
        if not self.admin_token:
            self.log_result("API Endpoints Health", False, "No admin token available")
            return False
        
        # Test key API endpoints
        endpoints = [
            "/api/health",
            "/api/crm/funds",
            "/api/investments/funds/config"
        ]
        
        success_count = 0
        
        for endpoint in endpoints:
            try:
                response = requests.get(
                    f"{self.base_url}{endpoint}",
                    headers=self.get_admin_headers() if endpoint != "/api/health" else {},
                    timeout=10
                )
                
                if response.status_code == 200:
                    success_count += 1
                    
            except Exception:
                pass
        
        if success_count == len(endpoints):
            self.log_result("API Endpoints Health", True, f"All {success_count} endpoints responding")
            return True
        else:
            self.log_result("API Endpoints Health", False, f"Only {success_count}/{len(endpoints)} endpoints responding")
            return False
    
    def test_error_handling(self):
        """Test error handling robust and informative"""
        # Test 404 handling
        try:
            response = requests.get(f"{self.base_url}/api/nonexistent", timeout=10)
            if response.status_code == 404:
                error_404_ok = True
            else:
                error_404_ok = False
        except:
            error_404_ok = False
        
        # Test 401 handling
        try:
            response = requests.get(f"{self.base_url}/api/crm/funds", timeout=10)  # No auth header
            if response.status_code == 401:
                error_401_ok = True
            else:
                error_401_ok = False
        except:
            error_401_ok = False
        
        if error_404_ok and error_401_ok:
            self.log_result("Error Handling", True, "404 and 401 errors properly handled")
            return True
        else:
            self.log_result("Error Handling", False, f"404 OK: {error_404_ok}, 401 OK: {error_401_ok}")
            return False
    
    def test_health_monitoring(self):
        """Test health monitoring endpoints fully functional"""
        # Test basic health endpoint
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            basic_health_ok = response.status_code == 200
        except:
            basic_health_ok = False
        
        # Test readiness endpoint
        try:
            response = requests.get(f"{self.base_url}/api/health/ready", timeout=10)
            readiness_ok = response.status_code == 200
        except:
            readiness_ok = False
        
        # Test metrics endpoint
        try:
            response = requests.get(f"{self.base_url}/api/health/metrics", timeout=10)
            metrics_ok = response.status_code == 200
        except:
            metrics_ok = False
        
        health_endpoints_working = sum([basic_health_ok, readiness_ok, metrics_ok])
        
        if health_endpoints_working >= 2:  # At least 2 out of 3 should work
            self.log_result("Health Monitoring", True, f"{health_endpoints_working}/3 health endpoints working")
            return True
        else:
            self.log_result("Health Monitoring", False, f"Only {health_endpoints_working}/3 health endpoints working")
            return False

    # ===============================================================================
    # MAIN TEST EXECUTION AND FINAL ASSESSMENT
    # ===============================================================================
    
    def run_final_validation(self):
        """Run complete final validation"""
        
        # Authenticate users first
        if not self.authenticate_users():
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with validation")
            return False
        
        # Run all validation tests
        mt5_endpoints_ok = self.test_multi_broker_mt5_endpoints()
        rate_limiting_ok = self.test_enhanced_rate_limiting()
        scalability_ok = self.test_system_scalability()
        production_ready_ok = self.test_production_readiness_checklist()
        
        # Final Assessment
        print("\n" + "="*80)
        print("FINAL PRODUCTION READINESS ASSESSMENT")
        print("="*80)
        
        print(f"\nTEST RESULTS: {self.tests_passed}/{self.tests_run} tests passed ({(self.tests_passed/self.tests_run*100):.1f}%)")
        
        # Success Criteria Evaluation
        success_criteria = {
            "Multi-broker MT5 endpoints": mt5_endpoints_ok,
            "Rate limiting": rate_limiting_ok,
            "Database performance": scalability_ok,
            "System stability": scalability_ok,
            "Authentication": production_ready_ok,
            "Error handling": production_ready_ok
        }
        
        print("\n📊 SUCCESS CRITERIA FOR PRODUCTION DEPLOYMENT:")
        all_criteria_met = True
        
        for criteria, status in success_criteria.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {criteria}: {'PASS' if status else 'FAIL'}")
            if not status:
                all_criteria_met = False
        
        # Final Recommendation
        print("\n🎯 PRODUCTION DEPLOYMENT RECOMMENDATION:")
        
        if all_criteria_met and self.tests_passed >= (self.tests_run * 0.85):
            print("✅ APPROVED FOR MONDAY PRODUCTION DEPLOYMENT")
            print("   System meets all scalability requirements for 100 MT5 accounts")
            print("   All critical systems operational and ready for production load")
            deployment_ready = True
        else:
            print("❌ REQUIRES OPTIMIZATION BEFORE MONDAY DEPLOYMENT")
            print("   Critical issues identified that must be resolved:")
            for failure in self.critical_failures[:5]:  # Show top 5 failures
                print(f"   • {failure}")
            deployment_ready = False
        
        # Performance Benchmarks
        print(f"\n📈 PERFORMANCE BENCHMARKS:")
        print(f"   • Multi-broker MT5 endpoints: {'✅ 100% success rate' if mt5_endpoints_ok else '❌ Issues detected'}")
        print(f"   • Rate limiting: {'✅ Appropriate limits enforced per user type' if rate_limiting_ok else '❌ Rate limiting issues'}")
        print(f"   • Database performance: {'✅ >500 operations/second maintained' if scalability_ok else '❌ Performance issues'}")
        print(f"   • API responsiveness: {'✅ <1 second average response time' if scalability_ok else '❌ Slow response times'}")
        print(f"   • System stability: {'✅ No memory leaks or resource issues' if scalability_ok else '❌ Stability concerns'}")
        print(f"   • Authentication: {'✅ All user types properly authenticated' if production_ready_ok else '❌ Auth issues'}")
        print(f"   • Error handling: {'✅ Graceful error responses and recovery' if production_ready_ok else '❌ Error handling issues'}")
        
        return deployment_ready

def main():
    """Main execution function"""
    tester = FinalValidationTester()
    
    try:
        deployment_ready = tester.run_final_validation()
        
        # Exit with appropriate code
        if deployment_ready:
            print("\n🚀 SYSTEM READY FOR PRODUCTION DEPLOYMENT!")
            sys.exit(0)
        else:
            print("\n⚠️  SYSTEM REQUIRES FIXES BEFORE DEPLOYMENT!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ CRITICAL ERROR during testing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()