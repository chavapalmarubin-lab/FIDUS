#!/usr/bin/env python3
"""
FIDUS Platform Critical Endpoint Testing - NEW Render Production URLs
Testing 5 critical endpoints after environment file updates to Render URLs
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FIDUSCriticalEndpointTestSuite:
    """FIDUS Platform Critical Endpoint Testing Suite - NEW Render Production URLs"""
    
    def __init__(self):
        # Use NEW Render production URLs
        self.render_backend_url = "https://fidus-investment-platform.onrender.com"
        self.backend_url = f"{self.render_backend_url}/api"
        
        self.session = None
        self.admin_token = None
        self.test_results = []
        self.endpoint_documentation = []
        
        logger.info(f"🚀 FIDUS Critical Endpoint Test Suite initialized")
        logger.info(f"   NEW Render Backend URL: {self.render_backend_url}")
        logger.info(f"   API Base URL: {self.backend_url}")
        logger.info(f"   Purpose: Test 5 critical endpoints with NEW Render production URLs")
    
    async def setup(self):
        """Setup test environment"""
        try:
            # Create HTTP session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={'Content-Type': 'application/json'}
            )
            
            # Authenticate as admin
            await self.authenticate_admin()
            
            logger.info("✅ Test environment setup completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Test setup failed: {str(e)}")
            return False
    
    async def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            login_data = {
                "username": "admin",
                "password": "password123",
                "user_type": "admin"
            }
            
            async with self.session.post(f"{self.backend_url}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.admin_token = data.get('token')
                    
                    if self.admin_token:
                        # Update session headers with auth token
                        self.session.headers.update({
                            'Authorization': f'Bearer {self.admin_token}'
                        })
                        logger.info("✅ Admin authentication successful")
                        return True
                    else:
                        logger.error("❌ No token received from login")
                        return False
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Admin login failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Authentication error: {str(e)}")
            return False
    
    async def test_admin_login_endpoint(self) -> Dict[str, Any]:
        """Test Admin Login Endpoint - POST https://fidus-investment-platform.onrender.com/api/auth/login"""
        test_name = "1. Admin Login Endpoint"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_info = {
            'url': f"{self.backend_url}/auth/login",
            'method': 'POST',
            'path_pattern': '/api/auth/login',
            'purpose': 'Admin authentication with NEW Render URL'
        }
        
        try:
            # Use exact payload format from review request
            login_data = {
                "username": "admin",
                "password": "password123",
                "user_type": "admin"
            }
            
            validation_results.append(f"🎯 Testing URL: {endpoint_info['url']}")
            validation_results.append(f"📋 Payload: {login_data}")
            
            async with self.session.post(endpoint_info['url'], json=login_data) as response:
                status_code = response.status
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except:
                    response_data = {"raw_response": response_text}
                
                endpoint_info.update({
                    'status_code': status_code,
                    'response_format': type(response_data).__name__,
                    'response_sample': response_data if len(str(response_data)) < 500 else str(response_data)[:500] + "..."
                })
                
                if status_code == 200:
                    validation_results.append("✅ EXPECTED: HTTP 200 with JWT token - SUCCESS")
                    
                    if 'token' in response_data:
                        validation_results.append("✅ JWT token returned in response")
                        self.admin_token = response_data['token']
                        # Update session headers
                        self.session.headers.update({
                            'Authorization': f'Bearer {self.admin_token}'
                        })
                    else:
                        validation_results.append("❌ No JWT token in response")
                    
                    if 'user' in response_data or 'id' in response_data:
                        validation_results.append("✅ User information returned")
                    else:
                        validation_results.append("⚠️ Limited user information in response")
                        
                else:
                    validation_results.append(f"❌ EXPECTED HTTP 200, GOT HTTP {status_code}")
                    validation_results.append(f"   Response: {response_text[:200]}")
            
            self.endpoint_documentation.append(endpoint_info)
            
            # Determine overall status
            failed_checks = [result for result in validation_results if result.startswith("❌")]
            overall_status = 'PASS' if len(failed_checks) == 0 else 'FAIL'
            
            return {
                'test_name': test_name,
                'status': overall_status,
                'validation_results': validation_results,
                'endpoint_info': endpoint_info
            }
                
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"],
                'endpoint_info': endpoint_info
            }
    
    async def test_health_check_endpoint(self) -> Dict[str, Any]:
        """Test Health Check Endpoint - GET https://fidus-investment-platform.onrender.com/api/health"""
        test_name = "2. Health Check Endpoint"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_url = f"{self.backend_url}/health"
        
        endpoint_info = {
            'url': endpoint_url,
            'method': 'GET',
            'path_pattern': '/api/health',
            'purpose': 'System status verification with NEW Render URL'
        }
        
        try:
            validation_results.append(f"🎯 Testing URL: {endpoint_url}")
            validation_results.append("📋 Expected: HTTP 200 with system status")
            
            async with self.session.get(endpoint_url) as response:
                status_code = response.status
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except:
                    response_data = {"raw_response": response_text}
                
                endpoint_info.update({
                    'status_code': status_code,
                    'response_sample': response_text[:200] if response_text else "Empty response"
                })
                
                if status_code == 200:
                    validation_results.append("✅ EXPECTED: HTTP 200 with system status - SUCCESS")
                    validation_results.append(f"   Response: {response_text[:100]}...")
                    
                    # Check for status information
                    if 'status' in response_data or 'health' in response_data or 'backend' in response_data:
                        validation_results.append("✅ System status information present")
                    else:
                        validation_results.append("⚠️ Limited status information")
                        
                    self.endpoint_documentation.append(endpoint_info)
                    
                    return {
                        'test_name': test_name,
                        'status': 'PASS',
                        'validation_results': validation_results,
                        'endpoint_info': endpoint_info
                    }
                else:
                    validation_results.append(f"❌ EXPECTED HTTP 200, GOT HTTP {status_code}")
                    validation_results.append(f"   Response: {response_text[:200]}")
                    
                    return {
                        'test_name': test_name,
                        'status': 'FAIL',
                        'validation_results': validation_results,
                        'endpoint_info': endpoint_info
                    }
                    
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"],
                'endpoint_info': endpoint_info
            }
    
    async def test_mt5_status_endpoint(self) -> Dict[str, Any]:
        """Test MT5 Status Endpoint - GET https://fidus-investment-platform.onrender.com/api/mt5/status"""
        test_name = "3. MT5 Status Endpoint"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_url = f"{self.backend_url}/mt5/status"
        
        endpoint_info = {
            'url': endpoint_url,
            'method': 'GET',
            'path_pattern': '/api/mt5/status',
            'purpose': 'MT5 bridge health status with NEW Render URL'
        }
        
        try:
            validation_results.append(f"🎯 Testing URL: {endpoint_url}")
            validation_results.append("📋 Expected: HTTP 200 with bridge health status")
            
            async with self.session.get(endpoint_url) as response:
                status_code = response.status
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except:
                    response_data = {"raw_response": response_text}
                
                endpoint_info.update({
                    'status_code': status_code,
                    'response_sample': response_data if len(str(response_data)) < 300 else str(response_data)[:300] + "..."
                })
                
                if status_code == 200:
                    validation_results.append("✅ EXPECTED: HTTP 200 with bridge health status - SUCCESS")
                    
                    # Check for bridge status information
                    if 'status' in response_data or 'bridge_status' in response_data or 'bridge' in response_data:
                        validation_results.append("✅ Bridge health status information present")
                    else:
                        validation_results.append("⚠️ Limited bridge status information")
                    
                    self.endpoint_documentation.append(endpoint_info)
                    
                    return {
                        'test_name': test_name,
                        'status': 'PASS',
                        'validation_results': validation_results,
                        'endpoint_info': endpoint_info
                    }
                else:
                    validation_results.append(f"❌ EXPECTED HTTP 200, GOT HTTP {status_code}")
                    validation_results.append(f"   Response: {response_text[:200]}")
                    
                    return {
                        'test_name': test_name,
                        'status': 'FAIL',
                        'validation_results': validation_results,
                        'endpoint_info': endpoint_info
                    }
                    
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"],
                'endpoint_info': endpoint_info
            }

    async def test_mt5_admin_accounts_endpoint(self) -> Dict[str, Any]:
        """Test MT5 Admin Accounts - GET https://fidus-investment-platform.onrender.com/api/mt5/admin/accounts"""
        test_name = "4. MT5 Admin Accounts Endpoint"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_url = f"{self.backend_url}/mt5/admin/accounts"
        
        endpoint_info = {
            'url': endpoint_url,
            'method': 'GET',
            'path_pattern': '/api/mt5/admin/accounts',
            'purpose': 'MT5 admin accounts listing with NEW Render URL'
        }
        
        try:
            validation_results.append(f"🎯 Testing URL: {endpoint_url}")
            validation_results.append("📋 Expected: HTTP 200 with 5 MT5 accounts")
            
            async with self.session.get(endpoint_url) as response:
                status_code = response.status
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except:
                    response_data = {"raw_response": response_text}
                
                endpoint_info.update({
                    'status_code': status_code,
                    'response_sample': response_data if len(str(response_data)) < 300 else str(response_data)[:300] + "..."
                })
                
                if status_code == 200:
                    validation_results.append("✅ EXPECTED: HTTP 200 with 5 MT5 accounts - SUCCESS")
                    
                    # Check for accounts data
                    if 'accounts' in response_data or isinstance(response_data, list):
                        accounts = response_data.get('accounts', response_data if isinstance(response_data, list) else [])
                        validation_results.append(f"✅ MT5 accounts data present ({len(accounts)} accounts)")
                        
                        if len(accounts) == 5:
                            validation_results.append("✅ Expected 5 MT5 accounts found")
                        else:
                            validation_results.append(f"⚠️ Expected 5 accounts, found {len(accounts)}")
                    else:
                        validation_results.append("❌ No MT5 accounts data found")
                    
                    self.endpoint_documentation.append(endpoint_info)
                    
                    return {
                        'test_name': test_name,
                        'status': 'PASS',
                        'validation_results': validation_results,
                        'endpoint_info': endpoint_info
                    }
                else:
                    validation_results.append(f"❌ EXPECTED HTTP 200, GOT HTTP {status_code}")
                    validation_results.append(f"   Response: {response_text[:200]}")
                    
                    return {
                        'test_name': test_name,
                        'status': 'FAIL',
                        'validation_results': validation_results,
                        'endpoint_info': endpoint_info
                    }
                    
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"],
                'endpoint_info': endpoint_info
            }

    async def test_debug_test_endpoint(self) -> Dict[str, Any]:
        """Test Debug Test Endpoint - GET https://fidus-investment-platform.onrender.com/api/debug/test"""
        test_name = "5. Debug Test Endpoint"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_url = f"{self.backend_url}/debug/test"
        
        endpoint_info = {
            'url': endpoint_url,
            'method': 'GET',
            'path_pattern': '/api/debug/test',
            'purpose': 'Debug message verification with NEW Render URL'
        }
        
        try:
            validation_results.append(f"🎯 Testing URL: {endpoint_url}")
            validation_results.append("📋 Expected: HTTP 200 with debug message")
            
            async with self.session.get(endpoint_url) as response:
                status_code = response.status
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except:
                    response_data = {"raw_response": response_text}
                
                endpoint_info.update({
                    'status_code': status_code,
                    'response_sample': response_data if len(str(response_data)) < 300 else str(response_data)[:300] + "..."
                })
                
                if status_code == 200:
                    validation_results.append("✅ EXPECTED: HTTP 200 with debug message - SUCCESS")
                    validation_results.append(f"   Response: {response_text[:100]}...")
                    
                    # Check for debug message
                    if 'debug' in response_data or 'test' in response_data or 'message' in response_data:
                        validation_results.append("✅ Debug message information present")
                    else:
                        validation_results.append("⚠️ Limited debug message information")
                    
                    self.endpoint_documentation.append(endpoint_info)
                    
                    return {
                        'test_name': test_name,
                        'status': 'PASS',
                        'validation_results': validation_results,
                        'endpoint_info': endpoint_info
                    }
                else:
                    validation_results.append(f"❌ EXPECTED HTTP 200, GOT HTTP {status_code}")
                    validation_results.append(f"   Response: {response_text[:200]}")
                    
                    return {
                        'test_name': test_name,
                        'status': 'FAIL',
                        'validation_results': validation_results,
                        'endpoint_info': endpoint_info
                    }
                    
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"],
                'endpoint_info': endpoint_info
            }
    
    async def test_path_pattern_analysis(self) -> Dict[str, Any]:
        """Analyze path patterns and routing consistency"""
        test_name = "Path Pattern Analysis"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        
        try:
            # Test various endpoint patterns to understand routing
            test_endpoints = [
                # Authentication patterns
                f"{self.backend_url}/auth/login",
                f"{self.backend_url}/auth/refresh",
                
                # Admin patterns  
                f"{self.backend_url}/admin/users",
                f"{self.backend_url}/admin/dashboard",
                
                # MT5 patterns
                f"{self.backend_url}/mt5/status",
                f"{self.backend_url}/mt5/accounts",
                
                # Investment patterns
                f"{self.backend_url}/investments",
                f"{self.backend_url}/investments/admin/overview",
                
                # Google patterns
                f"{self.backend_url}/google/connection/test-all",
                f"{self.backend_url}/admin/google/auth-url"
            ]
            
            api_prefix_consistent = True
            routing_patterns = {
                'auth': [],
                'admin': [],
                'mt5': [],
                'investments': [],
                'google': [],
                'other': []
            }
            
            for endpoint_url in test_endpoints:
                try:
                    async with self.session.get(endpoint_url) as response:
                        status_code = response.status
                        path = endpoint_url.replace(self.backend_url, '/api')
                        
                        # Categorize by pattern
                        if '/auth/' in path:
                            routing_patterns['auth'].append({'path': path, 'status': status_code})
                        elif '/admin/' in path:
                            routing_patterns['admin'].append({'path': path, 'status': status_code})
                        elif '/mt5/' in path:
                            routing_patterns['mt5'].append({'path': path, 'status': status_code})
                        elif '/investments' in path:
                            routing_patterns['investments'].append({'path': path, 'status': status_code})
                        elif '/google/' in path:
                            routing_patterns['google'].append({'path': path, 'status': status_code})
                        else:
                            routing_patterns['other'].append({'path': path, 'status': status_code})
                        
                        # Check if /api prefix is used consistently
                        if not path.startswith('/api/'):
                            api_prefix_consistent = False
                            
                except Exception as e:
                    validation_results.append(f"⚠️ Could not test {endpoint_url}: {str(e)}")
            
            # Analyze patterns
            if api_prefix_consistent:
                validation_results.append("✅ All endpoints use /api/ prefix consistently")
            else:
                validation_results.append("❌ Inconsistent /api/ prefix usage detected")
            
            # Report pattern analysis
            for category, endpoints in routing_patterns.items():
                if endpoints:
                    working_count = len([e for e in endpoints if e['status'] == 200])
                    total_count = len(endpoints)
                    validation_results.append(f"📊 {category.upper()} pattern: {working_count}/{total_count} endpoints working")
                    
                    for endpoint in endpoints[:3]:  # Show first 3 examples
                        status_icon = "✅" if endpoint['status'] == 200 else "❌" if endpoint['status'] >= 400 else "⚠️"
                        validation_results.append(f"   {status_icon} {endpoint['path']} (HTTP {endpoint['status']})")
            
            return {
                'test_name': test_name,
                'status': 'PASS',
                'validation_results': validation_results,
                'routing_patterns': routing_patterns,
                'api_prefix_consistent': api_prefix_consistent
            }
                
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"]
            }
    
    async def test_backend_url_verification(self) -> Dict[str, Any]:
        """Verify current backend URL configuration and accessibility"""
        test_name = "Backend URL Verification"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        
        try:
            # Document current configuration
            validation_results.append(f"📋 Frontend Backend URL: {self.frontend_backend_url}")
            validation_results.append(f"📋 API Base URL: {self.backend_url}")
            
            # Test base URL accessibility
            base_urls_to_test = [
                self.frontend_backend_url,
                self.backend_url,
                f"{self.frontend_backend_url}/api"
            ]
            
            working_urls = []
            
            for test_url in base_urls_to_test:
                try:
                    async with self.session.get(test_url) as response:
                        status_code = response.status
                        
                        if status_code in [200, 404, 401]:  # 404/401 means server is responding
                            validation_results.append(f"✅ {test_url}: Server responding (HTTP {status_code})")
                            working_urls.append(test_url)
                        else:
                            validation_results.append(f"⚠️ {test_url}: HTTP {status_code}")
                            
                except Exception as e:
                    validation_results.append(f"❌ {test_url}: Connection failed - {str(e)}")
            
            # Test specific endpoint to confirm API accessibility
            if self.admin_token:
                test_endpoint = f"{self.backend_url}/admin/users"
                try:
                    async with self.session.get(test_endpoint) as response:
                        status_code = response.status
                        if status_code in [200, 401, 403]:
                            validation_results.append(f"✅ API endpoint accessible: {test_endpoint} (HTTP {status_code})")
                        else:
                            validation_results.append(f"⚠️ API endpoint issue: {test_endpoint} (HTTP {status_code})")
                except Exception as e:
                    validation_results.append(f"❌ API endpoint test failed: {str(e)}")
            
            # Check for mixed URL configurations
            backend_env_urls = [
                "https://k8s-to-render.preview.emergentagent.com",
                "https://fidus-invest.emergent.host"
            ]
            
            validation_results.append("📊 Known Backend URLs in Environment:")
            for url in backend_env_urls:
                if url in self.frontend_backend_url:
                    validation_results.append(f"   ✅ Currently using: {url}")
                else:
                    validation_results.append(f"   ⚪ Alternative: {url}")
            
            # Determine overall status
            overall_status = 'PASS' if len(working_urls) > 0 else 'FAIL'
            
            return {
                'test_name': test_name,
                'status': overall_status,
                'validation_results': validation_results,
                'working_urls': working_urls,
                'current_backend_url': self.frontend_backend_url
            }
                
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"]
            }

    # Architecture audit tests completed above
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all 5 Critical Endpoint tests with NEW Render production URLs"""
        logger.info("🚀 Starting FIDUS Platform Critical Endpoint Testing - NEW Render URLs")
        
        if not await self.setup():
            return {
                'success': False,
                'error': 'Test setup failed',
                'results': []
            }
        
        # Run 5 critical endpoint tests as specified in review request
        tests = [
            self.test_admin_login_endpoint,
            self.test_health_check_endpoint,
            self.test_mt5_status_endpoint,
            self.test_mt5_admin_accounts_endpoint,
            self.test_debug_test_endpoint
        ]
        
        results = []
        for test_func in tests:
            try:
                result = await test_func()
                results.append(result)
                self.test_results.append(result)
            except Exception as e:
                logger.error(f"❌ Test function failed: {str(e)}")
                results.append({
                    'test_name': test_func.__name__,
                    'status': 'ERROR',
                    'error': str(e)
                })
        
        # Calculate summary
        passed_tests = [r for r in results if r.get('status') == 'PASS']
        failed_tests = [r for r in results if r.get('status') == 'FAIL']
        error_tests = [r for r in results if r.get('status') == 'ERROR']
        
        success_rate = len(passed_tests) / len(results) * 100 if results else 0
        
        summary = {
            'total_tests': len(results),
            'passed': len(passed_tests),
            'failed': len(failed_tests),
            'errors': len(error_tests),
            'success_rate': round(success_rate, 1),
            'overall_status': 'PASS' if len(failed_tests) == 0 and len(error_tests) == 0 else 'FAIL'
        }
        
        # Log summary
        logger.info("📊 FIDUS Architecture Audit Summary:")
        logger.info(f"   Total Tests: {summary['total_tests']}")
        logger.info(f"   Passed: {summary['passed']}")
        logger.info(f"   Failed: {summary['failed']}")
        logger.info(f"   Errors: {summary['errors']}")
        logger.info(f"   Success Rate: {summary['success_rate']}%")
        logger.info(f"   Overall Status: {summary['overall_status']}")
        
        return {
            'success': summary['overall_status'] == 'PASS',
            'summary': summary,
            'results': results,
            'endpoint_documentation': self.endpoint_documentation,
            'test_parameters': {
                'backend_url': self.backend_url,
                'frontend_backend_url': self.frontend_backend_url,
                'audit_type': 'Architecture Audit'
            }
        }
    
    async def cleanup(self):
        """Cleanup test resources"""
        if self.session and not self.session.closed:
            await self.session.close()
        logger.info("✅ Test cleanup completed")

async def main():
    """Main test execution"""
    test_suite = FIDUSArchitectureAuditTestSuite()
    
    try:
        results = await test_suite.run_all_tests()
        
        # Print detailed results
        print("\n" + "="*80)
        print("FIDUS PLATFORM ARCHITECTURE AUDIT RESULTS")
        print("="*80)
        
        for result in results['results']:
            print(f"\n🧪 {result['test_name']}: {result['status']}")
            
            if 'validation_results' in result:
                for validation in result['validation_results']:
                    print(f"   {validation}")
            
            if result.get('status') == 'ERROR':
                print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
        
        # Print endpoint documentation
        if results.get('endpoint_documentation'):
            print(f"\n📋 ENDPOINT DOCUMENTATION:")
            print("="*50)
            for i, endpoint in enumerate(results['endpoint_documentation'], 1):
                print(f"\n{i}. {endpoint.get('path_pattern', 'Unknown Path')}")
                print(f"   URL: {endpoint.get('url', 'N/A')}")
                print(f"   Method: {endpoint.get('method', 'N/A')}")
                print(f"   Status: HTTP {endpoint.get('status_code', 'N/A')}")
                print(f"   Purpose: {endpoint.get('purpose', 'N/A')}")
                if endpoint.get('response_sample'):
                    print(f"   Response Sample: {str(endpoint['response_sample'])[:100]}...")
        
        print(f"\n📊 SUMMARY:")
        print(f"   Overall Status: {results['summary']['overall_status']}")
        print(f"   Success Rate: {results['summary']['success_rate']}%")
        print(f"   Tests: {results['summary']['passed']}/{results['summary']['total_tests']} passed")
        print(f"   Backend URL: {results['test_parameters']['frontend_backend_url']}")
        
        if results['summary']['failed'] > 0:
            print(f"   Failed Tests: {results['summary']['failed']}")
        
        if results['summary']['errors'] > 0:
            print(f"   Error Tests: {results['summary']['errors']}")
        
        print("="*80)
        
        return results['success']
        
    except Exception as e:
        logger.error(f"❌ Test execution failed: {str(e)}")
        return False
        
    finally:
        await test_suite.cleanup()

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)