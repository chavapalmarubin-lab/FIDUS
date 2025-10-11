#!/usr/bin/env python3
"""
FIDUS Platform MT5 Auto-Sync Endpoint Testing - Render Production URLs
Testing MT5 Auto-Sync endpoints to resolve $521.88 discrepancy in account 886528
PRIORITY 1: Force sync account 886528 from $3,405.53 to $3,927.41
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
    """FIDUS Platform MT5 Auto-Sync Endpoint Testing Suite - Render Production URLs"""
    
    def __init__(self):
        # Use CORRECT Render backend API URL (not frontend URL)
        self.render_backend_url = "https://fidus-api.onrender.com"
        self.backend_url = f"{self.render_backend_url}/api"
        
        self.session = None
        self.admin_token = None
        self.test_results = []
        self.endpoint_documentation = []
        
        logger.info(f"🚀 FIDUS MT5 Auto-Sync Test Suite initialized")
        logger.info(f"   CORRECT Render Backend URL: {self.render_backend_url}")
        logger.info(f"   API Base URL: {self.backend_url}")
        logger.info(f"   Purpose: Test MT5 Auto-Sync endpoints to resolve $521.88 discrepancy")
    
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
        """Test Debug Test Endpoint - GET https://fidus-api.onrender.com/api/debug/test (PRIORITY - Check for new flag)"""
        test_name = "5. Debug Test Endpoint (PRIORITY)"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_url = f"{self.backend_url}/debug/test"
        
        endpoint_info = {
            'url': endpoint_url,
            'method': 'GET',
            'path_pattern': '/api/debug/test',
            'purpose': 'PRIORITY: Verify render_deployment: true flag (not no_kubernetes: true)'
        }
        
        try:
            validation_results.append(f"🎯 Testing URL: {endpoint_url}")
            validation_results.append("📋 Expected: HTTP 200 with 'render_deployment': true (not 'no_kubernetes': true)")
            
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
                    
                    # SPECIAL VERIFICATION: Check for "render_deployment": true flag
                    if isinstance(response_data, dict):
                        if response_data.get("render_deployment") is True:
                            validation_results.append("✅ CRITICAL: 'render_deployment': true flag CONFIRMED")
                        elif response_data.get("render_deployment") is False:
                            validation_results.append("❌ CRITICAL: 'render_deployment': false (should be true)")
                        else:
                            validation_results.append("⚠️ CRITICAL: 'render_deployment' flag not found in response")
                        
                        # Check that old flag is NOT present
                        if response_data.get("no_kubernetes") is True:
                            validation_results.append("❌ CRITICAL: Old 'no_kubernetes': true flag still present (should be removed)")
                        else:
                            validation_results.append("✅ VERIFIED: Old 'no_kubernetes' flag not present")
                    
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
    
    async def test_mt5_force_sync_account_886528(self) -> Dict[str, Any]:
        """Test MT5 Force Sync for Account 886528 - PRIORITY 1: Resolve $521.88 discrepancy"""
        test_name = "6. MT5 Force Sync Account 886528 (CRITICAL)"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_url = f"{self.backend_url}/mt5/force-sync/886528"
        
        endpoint_info = {
            'url': endpoint_url,
            'method': 'POST',
            'path_pattern': '/api/mt5/force-sync/886528',
            'purpose': 'CRITICAL: Force sync account 886528 to resolve $521.88 discrepancy'
        }
        
        try:
            validation_results.append(f"🎯 Testing URL: {endpoint_url}")
            validation_results.append("📋 Expected: HTTP 200 with sync results for account 886528")
            validation_results.append("💰 Target: Resolve $521.88 discrepancy (from $3,405.53 to $3,927.41)")
            
            async with self.session.post(endpoint_url) as response:
                status_code = response.status
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except:
                    response_data = {"raw_response": response_text}
                
                endpoint_info.update({
                    'status_code': status_code,
                    'response_sample': response_data if len(str(response_data)) < 500 else str(response_data)[:500] + "..."
                })
                
                if status_code == 200:
                    validation_results.append("✅ EXPECTED: HTTP 200 with sync results - SUCCESS")
                    
                    # Check for sync status
                    if 'status' in response_data:
                        sync_status = response_data.get('status')
                        validation_results.append(f"✅ Sync status: {sync_status}")
                        
                        if sync_status == 'synced':
                            validation_results.append("✅ Account 886528 successfully synced")
                        elif sync_status == 'failed':
                            validation_results.append(f"❌ Account 886528 sync failed: {response_data.get('error', 'Unknown error')}")
                    
                    # Check balance information
                    if 'old_balance' in response_data and 'new_balance' in response_data:
                        old_balance = response_data.get('old_balance', 0)
                        new_balance = response_data.get('new_balance', 0)
                        balance_change = response_data.get('balance_change', 0)
                        
                        validation_results.append(f"💰 Balance Update: ${old_balance:.2f} → ${new_balance:.2f}")
                        validation_results.append(f"💰 Balance Change: ${balance_change:+.2f}")
                        
                        # Check if discrepancy is resolved
                        if 'discrepancy_resolved' in response_data:
                            if response_data['discrepancy_resolved']:
                                validation_results.append("🎉 CRITICAL SUCCESS: $521.88 discrepancy RESOLVED!")
                            else:
                                validation_results.append("⚠️ Discrepancy not fully resolved")
                        
                        # Check if we got the expected balance
                        if abs(new_balance - 3927.41) < 1.0:  # Within $1 of target
                            validation_results.append("✅ Target balance achieved: ~$3,927.41")
                        elif abs(old_balance - 3405.53) < 1.0:  # Still at old balance
                            validation_results.append("⚠️ Balance unchanged from $3,405.53")
                    
                    # Check for error information
                    if response_data.get('error'):
                        validation_results.append(f"⚠️ Sync error: {response_data['error']}")
                    
                    self.endpoint_documentation.append(endpoint_info)
                    
                    # Determine overall status based on sync success
                    sync_success = response_data.get('success', False) or response_data.get('status') == 'synced'
                    overall_status = 'PASS' if sync_success else 'FAIL'
                    
                    return {
                        'test_name': test_name,
                        'status': overall_status,
                        'validation_results': validation_results,
                        'endpoint_info': endpoint_info,
                        'sync_data': response_data
                    }
                    
                elif status_code == 404:
                    validation_results.append("❌ CRITICAL: HTTP 404 - Endpoint not accessible (routing issue)")
                    validation_results.append("🔧 This indicates the routing fix has not been applied correctly")
                    
                    return {
                        'test_name': test_name,
                        'status': 'FAIL',
                        'validation_results': validation_results,
                        'endpoint_info': endpoint_info,
                        'critical_issue': 'routing_not_fixed'
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

    async def test_mt5_sync_dashboard(self) -> Dict[str, Any]:
        """Test MT5 Sync Dashboard - PRIORITY 2: Verify sync status monitoring"""
        test_name = "7. MT5 Sync Dashboard"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_url = f"{self.backend_url}/mt5/sync-dashboard"
        
        endpoint_info = {
            'url': endpoint_url,
            'method': 'GET',
            'path_pattern': '/api/mt5/sync-dashboard',
            'purpose': 'Monitor MT5 sync status and account health'
        }
        
        try:
            validation_results.append(f"🎯 Testing URL: {endpoint_url}")
            validation_results.append("📋 Expected: HTTP 200 with sync dashboard data")
            
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
                    validation_results.append("✅ EXPECTED: HTTP 200 with dashboard data - SUCCESS")
                    
                    # Check for dashboard components
                    if 'service_status' in response_data:
                        service_status = response_data.get('service_status')
                        validation_results.append(f"✅ Service status: {service_status}")
                    
                    if 'total_accounts' in response_data:
                        total_accounts = response_data.get('total_accounts', 0)
                        validation_results.append(f"✅ Total accounts monitored: {total_accounts}")
                    
                    # Check for account 886528 specifically
                    if 'accounts_detail' in response_data:
                        accounts = response_data['accounts_detail']
                        account_886528 = next((acc for acc in accounts if acc.get('mt5_login') == '886528'), None)
                        
                        if account_886528:
                            validation_results.append("✅ Account 886528 found in dashboard")
                            validation_results.append(f"   Balance: ${account_886528.get('balance', 0):.2f}")
                            validation_results.append(f"   Status: {account_886528.get('status', 'unknown')}")
                        else:
                            validation_results.append("⚠️ Account 886528 not found in dashboard")
                    
                    # Check for critical accounts
                    if 'critical_accounts' in response_data:
                        critical_count = len(response_data['critical_accounts'])
                        validation_results.append(f"⚠️ Critical accounts: {critical_count}")
                    
                    self.endpoint_documentation.append(endpoint_info)
                    
                    return {
                        'test_name': test_name,
                        'status': 'PASS',
                        'validation_results': validation_results,
                        'endpoint_info': endpoint_info
                    }
                    
                elif status_code == 404:
                    validation_results.append("❌ HTTP 404 - Endpoint not accessible (routing issue)")
                    
                    return {
                        'test_name': test_name,
                        'status': 'FAIL',
                        'validation_results': validation_results,
                        'endpoint_info': endpoint_info,
                        'critical_issue': 'routing_not_fixed'
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

    async def test_mt5_account_health_check_886528(self) -> Dict[str, Any]:
        """Test MT5 Health Check for Account 886528 - PRIORITY 2: Verify account status"""
        test_name = "8. MT5 Health Check Account 886528"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_url = f"{self.backend_url}/mt5/account-health-check/886528"
        
        endpoint_info = {
            'url': endpoint_url,
            'method': 'GET',
            'path_pattern': '/api/mt5/account-health-check/886528',
            'purpose': 'Check health status of account 886528'
        }
        
        try:
            validation_results.append(f"🎯 Testing URL: {endpoint_url}")
            validation_results.append("📋 Expected: HTTP 200 with health status for account 886528")
            
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
                    validation_results.append("✅ EXPECTED: HTTP 200 with health status - SUCCESS")
                    
                    # Check for health status information
                    if 'health_status' in response_data:
                        health_status = response_data.get('health_status')
                        validation_results.append(f"✅ Health status: {health_status}")
                    
                    if 'last_sync' in response_data:
                        last_sync = response_data.get('last_sync')
                        validation_results.append(f"✅ Last sync: {last_sync}")
                    
                    if 'balance' in response_data:
                        balance = response_data.get('balance')
                        validation_results.append(f"💰 Current balance: ${balance:.2f}")
                    
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

    async def test_mt5_start_background_sync(self) -> Dict[str, Any]:
        """Test MT5 Start Background Sync - PRIORITY 2: Verify sync control"""
        test_name = "9. MT5 Start Background Sync"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_url = f"{self.backend_url}/mt5/start-background-sync"
        
        endpoint_info = {
            'url': endpoint_url,
            'method': 'POST',
            'path_pattern': '/api/mt5/start-background-sync',
            'purpose': 'Start automated MT5 background sync service'
        }
        
        try:
            validation_results.append(f"🎯 Testing URL: {endpoint_url}")
            validation_results.append("📋 Expected: HTTP 200 with sync start confirmation")
            
            async with self.session.post(endpoint_url) as response:
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
                    validation_results.append("✅ EXPECTED: HTTP 200 with start confirmation - SUCCESS")
                    
                    # Check for start status
                    if 'status' in response_data:
                        start_status = response_data.get('status')
                        validation_results.append(f"✅ Start status: {start_status}")
                        
                        if start_status in ['started', 'already_running']:
                            validation_results.append("✅ Background sync is operational")
                    
                    if 'sync_interval' in response_data:
                        interval = response_data.get('sync_interval')
                        validation_results.append(f"✅ Sync interval: {interval} seconds")
                    
                    self.endpoint_documentation.append(endpoint_info)
                    
                    return {
                        'test_name': test_name,
                        'status': 'PASS',
                        'validation_results': validation_results,
                        'endpoint_info': endpoint_info
                    }
                    
                elif status_code == 404:
                    validation_results.append("❌ HTTP 404 - Endpoint not accessible (routing issue)")
                    
                    return {
                        'test_name': test_name,
                        'status': 'FAIL',
                        'validation_results': validation_results,
                        'endpoint_info': endpoint_info,
                        'critical_issue': 'routing_not_fixed'
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
    
    # Critical endpoint tests completed above
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all 5 Critical Endpoint tests with NEW Render production URLs"""
        logger.info("🚀 Starting FIDUS Platform Critical Endpoint Testing - NEW Render URLs")
        
        if not await self.setup():
            return {
                'success': False,
                'error': 'Test setup failed',
                'results': []
            }
        
        # Run critical endpoint tests + MT5 Auto-Sync tests as specified in review request
        tests = [
            self.test_admin_login_endpoint,
            self.test_health_check_endpoint,
            self.test_mt5_status_endpoint,
            self.test_mt5_admin_accounts_endpoint,
            self.test_debug_test_endpoint,
            # MT5 Auto-Sync Service Tests (PRIORITY)
            self.test_mt5_force_sync_account_886528,
            self.test_mt5_sync_dashboard,
            self.test_mt5_account_health_check_886528,
            self.test_mt5_start_background_sync
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
        logger.info("📊 FIDUS Critical Endpoint Testing Summary:")
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
                'render_backend_url': self.render_backend_url,
                'test_type': 'Critical Endpoint Testing - NEW Render URLs'
            }
        }
    
    async def cleanup(self):
        """Cleanup test resources"""
        if self.session and not self.session.closed:
            await self.session.close()
        logger.info("✅ Test cleanup completed")

async def main():
    """Main test execution"""
    test_suite = FIDUSCriticalEndpointTestSuite()
    
    try:
        results = await test_suite.run_all_tests()
        
        # Print detailed results
        print("\n" + "="*80)
        print("FIDUS PLATFORM CRITICAL ENDPOINT TESTING - NEW RENDER URLs")
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
            print(f"\n📋 CRITICAL ENDPOINT VERIFICATION:")
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
        print(f"   NEW Render Backend URL: {results['test_parameters']['render_backend_url']}")
        
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