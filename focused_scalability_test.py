#!/usr/bin/env python3
"""
FOCUSED SCALABILITY TEST - Key Issues Validation
Testing the specific improvements mentioned in the review request
"""

import requests
import time
import concurrent.futures
import json
from datetime import datetime

class FocusedScalabilityTester:
    def __init__(self, base_url="https://fund-performance.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        
    def authenticate_admin(self):
        """Authenticate admin user"""
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
            admin_data = response.json()
            self.admin_token = admin_data.get('token')
            print(f"✅ Admin authenticated: {admin_data.get('name')}")
            return True
        else:
            print(f"❌ Admin authentication failed: {response.status_code}")
            return False

    def test_rate_limiting_fixed(self):
        """Test that rate limiting is now working (previously 0/150 requests limited)"""
        print("\n🚦 TESTING RATE LIMITING FIX")
        print("="*60)
        print("Previous Result: FAILED - 0/150 requests limited")
        print("Expected: >95% of excess requests properly blocked")
        
        # Test with non-health endpoint (rate limiting skips health endpoints)
        endpoint = f"{self.base_url}/api/crm/funds"
        
        print(f"\n🔍 Sending 150 requests to {endpoint}")
        print("   (100 allowed + 50 excess = should block 50)")
        
        blocked_count = 0
        success_count = 0
        
        start_time = time.time()
        
        for i in range(150):
            try:
                response = requests.get(endpoint, timeout=5)
                if response.status_code == 429:
                    blocked_count += 1
                elif response.status_code == 200:
                    success_count += 1
                time.sleep(0.01)  # Small delay
            except Exception as e:
                print(f"   Request {i+1} failed: {e}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        excess_requests = 50  # 150 - 100 limit
        blocking_rate = (blocked_count / excess_requests * 100) if excess_requests > 0 else 0
        
        print(f"\n📊 RATE LIMITING RESULTS:")
        print(f"   Duration: {duration:.2f} seconds")
        print(f"   Total requests: 150")
        print(f"   Successful requests: {success_count}")
        print(f"   Blocked requests (429): {blocked_count}")
        print(f"   Excess requests: {excess_requests}")
        print(f"   Blocking rate: {blocking_rate:.1f}%")
        
        if blocking_rate >= 95:
            print(f"   ✅ RATE LIMITING FIXED: {blocking_rate:.1f}% blocking rate")
            return True
        else:
            print(f"   ❌ RATE LIMITING STILL FAILING: {blocking_rate:.1f}% blocking rate")
            return False

    def test_mt5_integration_stability(self):
        """Test MT5 integration stability (previously 90% vs required 95%)"""
        print("\n📈 TESTING MT5 INTEGRATION STABILITY")
        print("="*60)
        print("Previous Result: 90% success rate (below 95% requirement)")
        print("Expected: >95% connection success rate")
        
        if not self.admin_token:
            print("❌ No admin token for MT5 testing")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test MT5 endpoints multiple times
        mt5_endpoints = [
            "/api/mt5/admin/accounts",
            "/api/mt5/admin/performance/overview",
            "/api/mt5/brokers",
            "/api/mt5/brokers/multibank/servers",
            "/api/mt5/brokers/dootechnology/servers"
        ]
        
        total_attempts = 0
        successful_attempts = 0
        
        print(f"\n🔍 Testing {len(mt5_endpoints)} MT5 endpoints (20 attempts each)")
        
        for endpoint in mt5_endpoints:
            print(f"   Testing {endpoint}...")
            endpoint_success = 0
            
            for i in range(20):
                try:
                    response = requests.get(f"{self.base_url}{endpoint}", 
                                          headers=headers, timeout=10)
                    total_attempts += 1
                    
                    if response.status_code == 200:
                        successful_attempts += 1
                        endpoint_success += 1
                    
                    time.sleep(0.05)  # Small delay
                    
                except Exception as e:
                    total_attempts += 1
            
            endpoint_rate = (endpoint_success / 20) * 100
            print(f"      Success rate: {endpoint_rate:.1f}%")
        
        overall_success_rate = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
        
        print(f"\n📊 MT5 INTEGRATION RESULTS:")
        print(f"   Total attempts: {total_attempts}")
        print(f"   Successful: {successful_attempts}")
        print(f"   Overall success rate: {overall_success_rate:.1f}%")
        
        if overall_success_rate >= 95:
            print(f"   ✅ MT5 INTEGRATION FIXED: {overall_success_rate:.1f}% success rate")
            return True
        else:
            print(f"   ❌ MT5 INTEGRATION NEEDS WORK: {overall_success_rate:.1f}% success rate")
            return False

    def test_health_monitoring_endpoints(self):
        """Test enhanced health check endpoints with rate limiter stats"""
        print("\n🏥 TESTING SYSTEM HEALTH MONITORING")
        print("="*60)
        print("Testing: Enhanced health check endpoints with comprehensive metrics")
        print("Expected: All health endpoints responsive with rate limiter stats")
        
        health_endpoints = [
            ("/api/health", "Basic health check"),
            ("/api/health/ready", "Readiness check with dependencies"),
            ("/api/health/metrics", "Detailed metrics with rate limiter stats")
        ]
        
        results = {}
        
        for endpoint, description in health_endpoints:
            print(f"\n🔍 Testing {description}: {endpoint}")
            
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                
                if response.status_code in [200, 503]:  # 503 acceptable for degraded
                    data = response.json()
                    status = data.get('status', 'unknown')
                    
                    print(f"   ✅ Endpoint responsive: {response.status_code}")
                    print(f"   Status: {status}")
                    
                    # Check for specific features
                    if endpoint == "/api/health/metrics":
                        rate_limiter_stats = data.get('rate_limiter', {})
                        system_metrics = data.get('system', {})
                        database_info = data.get('database', {})
                        
                        print(f"   Rate limiter stats: {'✅' if rate_limiter_stats else '❌'}")
                        print(f"   System metrics: {'✅' if system_metrics else '❌'}")
                        print(f"   Database info: {'✅' if database_info else '❌'}")
                        
                        if rate_limiter_stats:
                            print(f"      Rate limiter metrics: {list(rate_limiter_stats.keys())}")
                        
                        results[endpoint] = {
                            "responsive": True,
                            "has_rate_limiter_stats": bool(rate_limiter_stats),
                            "has_system_metrics": bool(system_metrics),
                            "has_database_info": bool(database_info)
                        }
                    else:
                        results[endpoint] = {"responsive": True}
                else:
                    print(f"   ❌ Endpoint failed: {response.status_code}")
                    results[endpoint] = {"responsive": False}
                    
            except Exception as e:
                print(f"   ❌ Endpoint error: {e}")
                results[endpoint] = {"responsive": False}
        
        # Evaluate results
        responsive_count = sum(1 for r in results.values() if r.get('responsive', False))
        total_endpoints = len(health_endpoints)
        
        metrics_endpoint = results.get('/api/health/metrics', {})
        has_comprehensive_metrics = (
            metrics_endpoint.get('has_rate_limiter_stats', False) and
            metrics_endpoint.get('has_system_metrics', False) and
            metrics_endpoint.get('has_database_info', False)
        )
        
        print(f"\n📊 HEALTH MONITORING RESULTS:")
        print(f"   Responsive endpoints: {responsive_count}/{total_endpoints}")
        print(f"   Comprehensive metrics: {'✅' if has_comprehensive_metrics else '❌'}")
        
        success = responsive_count == total_endpoints and has_comprehensive_metrics
        
        if success:
            print(f"   ✅ HEALTH MONITORING WORKING: All endpoints responsive with metrics")
            return True
        else:
            print(f"   ❌ HEALTH MONITORING ISSUES: Missing functionality")
            return False

    def test_database_performance_maintained(self):
        """Test that database performance remains excellent (no regression)"""
        print("\n🗄️ TESTING DATABASE PERFORMANCE (NO REGRESSION)")
        print("="*60)
        print("Previous Result: PASSED - excellent performance")
        print("Expected: Maintain performance, no regression")
        
        if not self.admin_token:
            print("❌ No admin token for database testing")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test database-intensive endpoints
        db_endpoints = [
            ("/api/clients/all", "Client data retrieval"),
            ("/api/investments/admin/overview", "Investment overview aggregation"),
            ("/api/crm/prospects/pipeline", "Prospect pipeline aggregation")
        ]
        
        print(f"\n🔍 Testing database performance with {len(db_endpoints)} endpoints")
        
        response_times = []
        successful_queries = 0
        total_queries = 0
        
        for endpoint, description in db_endpoints:
            print(f"   Testing {description}: {endpoint}")
            
            # Test each endpoint 5 times
            for i in range(5):
                try:
                    start_time = time.time()
                    response = requests.get(f"{self.base_url}{endpoint}", 
                                          headers=headers, timeout=15)
                    end_time = time.time()
                    
                    query_time = end_time - start_time
                    total_queries += 1
                    
                    if response.status_code == 200:
                        successful_queries += 1
                        response_times.append(query_time)
                        
                        if i == 0:  # Log first successful response
                            print(f"      ✅ Query successful: {query_time:.3f}s")
                    else:
                        print(f"      ❌ Query failed: {response.status_code}")
                    
                    time.sleep(0.1)  # Brief pause
                    
                except Exception as e:
                    total_queries += 1
                    print(f"      ❌ Query error: {e}")
        
        # Calculate performance metrics
        success_rate = (successful_queries / total_queries * 100) if total_queries > 0 else 0
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            
            print(f"\n📊 DATABASE PERFORMANCE RESULTS:")
            print(f"   Total queries: {total_queries}")
            print(f"   Successful queries: {successful_queries}")
            print(f"   Success rate: {success_rate:.1f}%")
            print(f"   Average response time: {avg_response_time:.3f}s")
            print(f"   Maximum response time: {max_response_time:.3f}s")
            
            # Performance thresholds (maintain excellent performance)
            performance_maintained = (
                success_rate >= 90 and 
                avg_response_time < 2.0 and 
                max_response_time < 5.0
            )
            
            if performance_maintained:
                print(f"   ✅ DATABASE PERFORMANCE MAINTAINED: Excellent performance")
                return True
            else:
                print(f"   ❌ DATABASE PERFORMANCE REGRESSION: Performance degraded")
                return False
        else:
            print(f"\n📊 DATABASE PERFORMANCE RESULTS:")
            print(f"   ❌ No successful queries - database performance severely degraded")
            return False

    def run_focused_tests(self):
        """Run focused tests on the key scalability improvements"""
        print("🎯 FOCUSED SCALABILITY VALIDATION TEST")
        print("="*80)
        print("Testing specific improvements for 100 MT5 account scalability")
        print(f"Target: {self.base_url}")
        print("="*80)
        
        # Authenticate
        if not self.authenticate_admin():
            print("❌ Authentication failed - cannot proceed")
            return False
        
        # Run focused tests
        results = {}
        
        print("\n📋 EXECUTING FOCUSED TESTS...")
        
        # 1. Rate Limiting Fix (Critical)
        results['rate_limiting'] = self.test_rate_limiting_fixed()
        
        # 2. MT5 Integration Stability (Critical)
        results['mt5_integration'] = self.test_mt5_integration_stability()
        
        # 3. Health Monitoring (Important)
        results['health_monitoring'] = self.test_health_monitoring_endpoints()
        
        # 4. Database Performance (Regression Check)
        results['database_performance'] = self.test_database_performance_maintained()
        
        # Generate focused report
        self.generate_focused_report(results)
        
        return True

    def generate_focused_report(self, results):
        """Generate focused validation report"""
        print("\n" + "="*80)
        print("🎯 FOCUSED VALIDATION REPORT")
        print("="*80)
        
        # Count successes
        successful_tests = sum(1 for success in results.values() if success)
        total_tests = len(results)
        
        print(f"\n📊 SUMMARY:")
        print(f"   Tests Passed: {successful_tests}/{total_tests}")
        
        # Detailed results
        print(f"\n📈 DETAILED RESULTS:")
        
        test_descriptions = {
            'rate_limiting': '🚦 Rate Limiting (100 req/min limit)',
            'mt5_integration': '📈 MT5 Integration Stability (>95% success)',
            'health_monitoring': '🏥 Health Monitoring (comprehensive metrics)',
            'database_performance': '🗄️ Database Performance (no regression)'
        }
        
        for test_key, success in results.items():
            description = test_descriptions.get(test_key, test_key)
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"   {description}: {status}")
        
        # Critical fixes evaluation
        critical_fixes = ['rate_limiting', 'mt5_integration']
        critical_passed = sum(1 for key in critical_fixes if results.get(key, False))
        
        print(f"\n🎯 CRITICAL FIXES STATUS:")
        print(f"   Critical fixes passed: {critical_passed}/{len(critical_fixes)}")
        
        # Final recommendation
        print(f"\n🏁 PRODUCTION READINESS:")
        
        if critical_passed == len(critical_fixes):
            if successful_tests == total_tests:
                print(f"   ✅ FULLY READY: All improvements validated")
                print(f"   ✅ System ready for 100 MT5 account scale")
            else:
                print(f"   ⚠️ MOSTLY READY: Critical fixes working, minor issues remain")
                print(f"   ✅ Core scalability improvements validated")
        else:
            print(f"   ❌ NOT READY: Critical scalability issues remain")
            print(f"   ❌ {len(critical_fixes) - critical_passed} critical fixes still failing")
        
        # Before/After comparison
        print(f"\n📊 BEFORE/AFTER COMPARISON:")
        print(f"   Rate Limiting: BEFORE: 0/150 blocked → AFTER: {'WORKING' if results.get('rate_limiting') else 'STILL FAILING'}")
        print(f"   MT5 Integration: BEFORE: 90% success → AFTER: {'≥95% SUCCESS' if results.get('mt5_integration') else '<95% SUCCESS'}")
        print(f"   Health Monitoring: BEFORE: N/A → AFTER: {'IMPLEMENTED' if results.get('health_monitoring') else 'ISSUES'}")
        print(f"   Database Performance: BEFORE: EXCELLENT → AFTER: {'MAINTAINED' if results.get('database_performance') else 'DEGRADED'}")
        
        print("="*80)

if __name__ == "__main__":
    tester = FocusedScalabilityTester()
    tester.run_focused_tests()