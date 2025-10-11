#!/usr/bin/env python3
"""
FIDUS Platform Architecture Audit - Backend Endpoint Testing
Testing current working endpoints to document path patterns and responses
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

class FIDUSArchitectureAuditTestSuite:
    """FIDUS Platform Architecture Audit - Backend Endpoint Testing Suite"""
    
    def __init__(self):
        # Get backend URL from frontend environment
        self.frontend_backend_url = os.getenv('REACT_APP_BACKEND_URL', 'https://k8s-to-render.preview.emergentagent.com')
        self.backend_url = self.frontend_backend_url
        if not self.backend_url.endswith('/api'):
            self.backend_url = f"{self.backend_url}/api"
        
        self.session = None
        self.admin_token = None
        self.test_results = []
        self.endpoint_documentation = []
        
        logger.info(f"🏗️ FIDUS Platform Architecture Audit Test Suite initialized")
        logger.info(f"   Frontend Backend URL: {self.frontend_backend_url}")
        logger.info(f"   API Base URL: {self.backend_url}")
        logger.info(f"   Purpose: Document working endpoint patterns and responses")
    
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
        """Test Admin Login Endpoint - /api/auth/login"""
        test_name = "Admin Login Endpoint"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_info = {
            'url': f"{self.backend_url}/auth/login",
            'method': 'POST',
            'path_pattern': '/api/auth/login',
            'purpose': 'Admin authentication'
        }
        
        try:
            login_data = {
                "email": "admin",
                "password": "password123"
            }
            
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
                    validation_results.append("✅ Admin login endpoint returns HTTP 200")
                    
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
                    validation_results.append(f"❌ Admin login failed: HTTP {status_code}")
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
        """Test Health Check or Simple GET Endpoint"""
        test_name = "Health Check Endpoint"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        health_endpoints = [
            f"{self.backend_url}/health",
            f"{self.backend_url}/status", 
            f"{self.backend_url}/ping",
            f"{self.backend_url}/"
        ]
        
        working_endpoint = None
        
        try:
            for endpoint_url in health_endpoints:
                try:
                    async with self.session.get(endpoint_url) as response:
                        status_code = response.status
                        response_text = await response.text()
                        
                        endpoint_info = {
                            'url': endpoint_url,
                            'method': 'GET',
                            'path_pattern': endpoint_url.replace(self.backend_url, '/api'),
                            'purpose': 'Health check / Status verification',
                            'status_code': status_code,
                            'response_sample': response_text[:200] if response_text else "Empty response"
                        }
                        
                        if status_code == 200:
                            validation_results.append(f"✅ Health endpoint found: {endpoint_url}")
                            validation_results.append(f"   Status: HTTP {status_code}")
                            validation_results.append(f"   Response: {response_text[:100]}...")
                            working_endpoint = endpoint_info
                            self.endpoint_documentation.append(endpoint_info)
                            break
                        else:
                            validation_results.append(f"⚠️ {endpoint_url}: HTTP {status_code}")
                            
                except Exception as e:
                    validation_results.append(f"❌ {endpoint_url}: {str(e)}")
            
            if not working_endpoint:
                validation_results.append("❌ No working health check endpoint found")
                return {
                    'test_name': test_name,
                    'status': 'FAIL',
                    'validation_results': validation_results
                }
            
            return {
                'test_name': test_name,
                'status': 'PASS',
                'validation_results': validation_results,
                'endpoint_info': working_endpoint
            }
                
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"]
            }
    
    async def test_mt5_endpoints(self) -> Dict[str, Any]:
        """Test MT5 Endpoints - /api/mt5/status and /api/mt5/admin/accounts"""
        test_name = "MT5 Endpoints"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        mt5_endpoints = [
            {
                'url': f"{self.backend_url}/mt5/status",
                'path_pattern': '/api/mt5/status',
                'purpose': 'MT5 service status check'
            },
            {
                'url': f"{self.backend_url}/mt5/admin/accounts",
                'path_pattern': '/api/mt5/admin/accounts', 
                'purpose': 'MT5 admin accounts listing'
            },
            {
                'url': f"{self.backend_url}/mt5/dashboard/overview",
                'path_pattern': '/api/mt5/dashboard/overview',
                'purpose': 'MT5 dashboard overview'
            }
        ]
        
        try:
            for endpoint in mt5_endpoints:
                try:
                    async with self.session.get(endpoint['url']) as response:
                        status_code = response.status
                        response_text = await response.text()
                        
                        try:
                            response_data = json.loads(response_text)
                        except:
                            response_data = {"raw_response": response_text}
                        
                        endpoint_info = {
                            **endpoint,
                            'method': 'GET',
                            'status_code': status_code,
                            'response_format': type(response_data).__name__,
                            'response_sample': response_data if len(str(response_data)) < 300 else str(response_data)[:300] + "..."
                        }
                        
                        if status_code == 200:
                            validation_results.append(f"✅ {endpoint['path_pattern']}: HTTP 200")
                            
                            # Specific validation for MT5 status
                            if 'status' in endpoint['path_pattern']:
                                if 'status' in response_data or 'bridge_status' in response_data:
                                    validation_results.append("   ✅ Status information present")
                                else:
                                    validation_results.append("   ⚠️ Limited status information")
                            
                            # Specific validation for MT5 accounts
                            elif 'accounts' in endpoint['path_pattern']:
                                if 'accounts' in response_data or isinstance(response_data, list):
                                    accounts = response_data.get('accounts', response_data if isinstance(response_data, list) else [])
                                    validation_results.append(f"   ✅ Accounts data present ({len(accounts)} accounts)")
                                else:
                                    validation_results.append("   ⚠️ No accounts data found")
                            
                            self.endpoint_documentation.append(endpoint_info)
                            
                        elif status_code == 401:
                            validation_results.append(f"🔒 {endpoint['path_pattern']}: HTTP 401 (Authentication required)")
                            endpoint_info['requires_auth'] = True
                            self.endpoint_documentation.append(endpoint_info)
                            
                        elif status_code == 404:
                            validation_results.append(f"❌ {endpoint['path_pattern']}: HTTP 404 (Not found)")
                            
                        elif status_code == 500:
                            validation_results.append(f"⚠️ {endpoint['path_pattern']}: HTTP 500 (Server error)")
                            validation_results.append(f"   Response: {response_text[:100]}")
                            
                        else:
                            validation_results.append(f"⚠️ {endpoint['path_pattern']}: HTTP {status_code}")
                            validation_results.append(f"   Response: {response_text[:100]}")
                            
                except Exception as e:
                    validation_results.append(f"❌ {endpoint['path_pattern']}: Exception - {str(e)}")
            
            # Determine overall status
            working_endpoints = [result for result in validation_results if "✅" in result and "HTTP 200" in result]
            overall_status = 'PASS' if len(working_endpoints) > 0 else 'FAIL'
            
            return {
                'test_name': test_name,
                'status': overall_status,
                'validation_results': validation_results,
                'working_endpoints': len(working_endpoints),
                'total_endpoints': len(mt5_endpoints)
            }
                
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"]
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

    async def test_database_collections(self) -> Dict[str, Any]:
        """Test that database collections store data for all 4 accounts"""
        test_name = "Database Collections Multi-Account"
        logger.info(f"🧪 Testing {test_name}")
        
        try:
            validation_results = []
            
            # First, trigger a sync to ensure collections have data
            sync_url = f"{self.backend_url}/admin/trading/analytics/sync"
            async with self.session.post(sync_url) as sync_response:
                if sync_response.status == 200:
                    validation_results.append("✅ Sync endpoint accessible for collection population")
                else:
                    validation_results.append("❌ Sync endpoint not accessible")
            
            # Test mt5_trades collection - should have trades for all accounts
            trades_url = f"{self.backend_url}/admin/trading/analytics/trades?account=0&limit=100"
            async with self.session.get(trades_url) as trades_response:
                if trades_response.status == 200:
                    trades_data = await trades_response.json()
                    trades = trades_data.get('trades', [])
                    
                    if trades:
                        validation_results.append(f"✅ MT5 trades collection accessible ({len(trades)} trades)")
                        
                        # Check if trades from all accounts are present
                        account_numbers = set(trade.get('account') for trade in trades)
                        expected_accounts = set(self.all_accounts)
                        
                        if account_numbers.intersection(expected_accounts):
                            validation_results.append(f"✅ Trades from multiple accounts in collection: {sorted(account_numbers)}")
                        else:
                            validation_results.append(f"❌ No trades from expected accounts: {sorted(account_numbers)}")
                    else:
                        validation_results.append("⚠️ MT5 trades collection empty")
                else:
                    validation_results.append("❌ MT5 trades collection not accessible")
            
            # Test daily_performance collection - should have entries for all accounts
            daily_url = f"{self.backend_url}/admin/trading/analytics/daily?account=0&days=7"
            async with self.session.get(daily_url) as daily_response:
                if daily_response.status == 200:
                    daily_data = await daily_response.json()
                    daily_performance = daily_data.get('daily_performance', [])
                    
                    if daily_performance:
                        validation_results.append(f"✅ Daily performance collection accessible ({len(daily_performance)} entries)")
                        
                        # Check aggregation functionality
                        sample_entry = daily_performance[0]
                        if 'total_trades' in sample_entry and 'total_pnl' in sample_entry:
                            validation_results.append("✅ Daily performance aggregation working")
                        else:
                            validation_results.append("❌ Daily performance aggregation incomplete")
                    else:
                        validation_results.append("⚠️ Daily performance collection empty")
                else:
                    validation_results.append("❌ Daily performance collection not accessible")
            
            # Test individual account daily performance
            accounts_with_daily_data = []
            for account_num in self.all_accounts:
                daily_account_url = f"{self.backend_url}/admin/trading/analytics/daily?account={account_num}&days=3"
                async with self.session.get(daily_account_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        daily_data = data.get('daily_performance', [])
                        if daily_data:
                            accounts_with_daily_data.append(account_num)
            
            if accounts_with_daily_data:
                validation_results.append(f"✅ Daily performance data exists for accounts: {accounts_with_daily_data}")
            else:
                validation_results.append("⚠️ No daily performance data for individual accounts")
            
            # Test analytics overview aggregation pipeline
            overview_url = f"{self.backend_url}/admin/trading/analytics/overview?account=0"
            async with self.session.get(overview_url) as overview_response:
                if overview_response.status == 200:
                    overview_data = await overview_response.json()
                    analytics = overview_data.get('analytics', {})
                    
                    if analytics and 'overview' in analytics:
                        validation_results.append("✅ Analytics aggregation pipeline working")
                        
                        overview = analytics['overview']
                        if overview.get('total_trades', 0) > 0:
                            validation_results.append(f"✅ Aggregated analytics show activity: {overview.get('total_trades')} trades")
                        else:
                            validation_results.append("⚠️ Aggregated analytics show no activity")
                    else:
                        validation_results.append("❌ Analytics aggregation not working")
                else:
                    validation_results.append("❌ Analytics overview endpoint failed")
            
            # Determine overall status
            failed_checks = [result for result in validation_results if result.startswith("❌")]
            overall_status = 'PASS' if len(failed_checks) == 0 else 'FAIL'
            
            logger.info(f"   Database Collections Status: {overall_status}")
            logger.info(f"   Failed Checks: {len(failed_checks)}")
            
            return {
                'test_name': test_name,
                'status': overall_status,
                'validation_results': validation_results,
                'details': {
                    'collections_tested': ['mt5_trades', 'daily_performance'],
                    'accounts_with_data': accounts_with_daily_data,
                    'failed_checks': len(failed_checks),
                    'total_checks': len(validation_results)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"]
            }
    
    async def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling for invalid requests"""
        test_name = "Error Handling"
        logger.info(f"🧪 Testing {test_name}")
        
        try:
            validation_results = []
            
            # Test invalid account parameter
            invalid_account_url = f"{self.backend_url}/admin/trading/analytics/daily?account=999999"
            async with self.session.get(invalid_account_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success') and len(data.get('daily_performance', [])) == 0:
                        validation_results.append("✅ Invalid account handled gracefully (empty result)")
                    else:
                        validation_results.append("⚠️ Invalid account returned data (unexpected)")
                else:
                    validation_results.append("❌ Invalid account caused server error")
            
            # Test invalid days parameter
            invalid_days_url = f"{self.backend_url}/admin/trading/analytics/daily?days=-1"
            async with self.session.get(invalid_days_url) as response:
                if response.status in [200, 400]:
                    validation_results.append("✅ Invalid days parameter handled")
                else:
                    validation_results.append("❌ Invalid days parameter caused server error")
            
            # Test invalid limit parameter
            invalid_limit_url = f"{self.backend_url}/admin/trading/analytics/trades?limit=abc"
            async with self.session.get(invalid_limit_url) as response:
                if response.status in [200, 400]:
                    validation_results.append("✅ Invalid limit parameter handled")
                else:
                    validation_results.append("❌ Invalid limit parameter caused server error")
            
            # Test unauthenticated request (remove auth header temporarily)
            original_headers = self.session.headers.copy()
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            unauth_url = f"{self.backend_url}/admin/trading/analytics/overview"
            async with self.session.get(unauth_url) as response:
                if response.status == 401:
                    validation_results.append("✅ Unauthenticated request properly rejected")
                else:
                    validation_results.append(f"❌ Unauthenticated request not rejected (status: {response.status})")
            
            # Restore auth headers
            self.session.headers.update(original_headers)
            
            # Determine overall status
            failed_checks = [result for result in validation_results if result.startswith("❌")]
            overall_status = 'PASS' if len(failed_checks) == 0 else 'FAIL'
            
            logger.info(f"   Error Handling Status: {overall_status}")
            logger.info(f"   Failed Checks: {len(failed_checks)}")
            
            return {
                'test_name': test_name,
                'status': overall_status,
                'validation_results': validation_results,
                'details': {
                    'error_scenarios_tested': 4,
                    'failed_checks': len(failed_checks)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"]
            }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all FIDUS Architecture Audit tests"""
        logger.info("🏗️ Starting FIDUS Platform Architecture Audit")
        
        if not await self.setup():
            return {
                'success': False,
                'error': 'Test setup failed',
                'results': []
            }
        
        # Run architecture audit tests
        tests = [
            self.test_backend_url_verification,
            self.test_admin_login_endpoint,
            self.test_health_check_endpoint,
            self.test_mt5_endpoints,
            self.test_path_pattern_analysis
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
    test_suite = TradingAnalyticsPhase1BTestSuite()
    
    try:
        results = await test_suite.run_all_tests()
        
        # Print detailed results
        print("\n" + "="*80)
        print("TRADING ANALYTICS PHASE 1B MULTI-ACCOUNT TEST RESULTS")
        print("="*80)
        
        for result in results['results']:
            print(f"\n🧪 {result['test_name']}: {result['status']}")
            
            if 'validation_results' in result:
                for validation in result['validation_results']:
                    print(f"   {validation}")
            
            if result.get('status') == 'ERROR':
                print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
        
        print(f"\n📊 SUMMARY:")
        print(f"   Overall Status: {results['summary']['overall_status']}")
        print(f"   Success Rate: {results['summary']['success_rate']}%")
        print(f"   Tests: {results['summary']['passed']}/{results['summary']['total_tests']} passed")
        
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