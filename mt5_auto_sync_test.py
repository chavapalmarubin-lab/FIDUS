#!/usr/bin/env python3
"""
MT5 Auto-Sync Service Endpoints Testing
Testing the fixed MT5 Auto-Sync Service endpoints with correct /api prefix
Focus: Address the $521.88 discrepancy between FIDUS database and MEX Atlantic live
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MT5AutoSyncTestSuite:
    """MT5 Auto-Sync Service Endpoints Testing Suite"""
    
    def __init__(self):
        # Use correct backend URL from frontend/.env
        self.backend_url = "https://fidus-api.onrender.com"
        
        self.session = None
        self.admin_token = None
        self.test_results = []
        
        logger.info(f"🚀 MT5 Auto-Sync Service Test Suite initialized")
        logger.info(f"   Backend URL: {self.backend_url}")
        logger.info(f"   Focus: Test fixed MT5 sync endpoints with /api prefix")
        logger.info(f"   Critical Issue: $521.88 discrepancy for account 886528")
    
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
            
            async with self.session.post(f"{self.backend_url}/api/auth/login", json=login_data) as response:
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

    async def test_mt5_sync_dashboard(self) -> Dict[str, Any]:
        """Test MT5 Sync Dashboard - GET /api/mt5/sync-dashboard"""
        test_name = "1. MT5 Sync Dashboard (Fixed Route)"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_url = f"{self.backend_url}/api/api/mt5/sync-dashboard"
        
        try:
            validation_results.append(f"🎯 Testing URL: {endpoint_url}")
            validation_results.append("📋 Expected: Dashboard showing all MT5 accounts and sync status")
            
            async with self.session.get(endpoint_url) as response:
                status_code = response.status
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except:
                    response_data = {"raw_response": response_text}
                
                if status_code == 200:
                    validation_results.append("✅ EXPECTED: HTTP 200 (not 404) - SUCCESS")
                    
                    # Check for dashboard data
                    if isinstance(response_data, dict):
                        if 'accounts' in response_data or 'mt5_accounts' in response_data:
                            accounts = response_data.get('accounts', response_data.get('mt5_accounts', []))
                            validation_results.append(f"✅ MT5 accounts found: {len(accounts)} accounts")
                            
                            # Look for account 886528 specifically
                            account_886528 = None
                            for account in accounts:
                                if str(account.get('account_number', '')) == '886528' or str(account.get('login', '')) == '886528':
                                    account_886528 = account
                                    break
                            
                            if account_886528:
                                validation_results.append("✅ CRITICAL: Account 886528 found in dashboard")
                                balance = account_886528.get('balance', account_886528.get('equity', 'N/A'))
                                validation_results.append(f"   Current Balance: ${balance}")
                            else:
                                validation_results.append("❌ CRITICAL: Account 886528 NOT found in dashboard")
                        
                        if 'sync_status' in response_data or 'status' in response_data:
                            validation_results.append("✅ Sync status information present")
                        else:
                            validation_results.append("⚠️ Limited sync status information")
                    else:
                        validation_results.append("❌ Invalid dashboard response format")
                        
                elif status_code == 404:
                    validation_results.append("❌ CRITICAL: HTTP 404 - Endpoint not found (route not fixed)")
                else:
                    validation_results.append(f"❌ EXPECTED HTTP 200, GOT HTTP {status_code}")
                    validation_results.append(f"   Response: {response_text[:200]}")
                
                return {
                    'test_name': test_name,
                    'status': 'PASS' if status_code == 200 else 'FAIL',
                    'validation_results': validation_results,
                    'response_data': response_data,
                    'status_code': status_code
                }
                    
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"]
            }

    async def test_force_sync_account_886528(self) -> Dict[str, Any]:
        """Test Force Sync Account 886528 - POST /api/mt5/force-sync/886528"""
        test_name = "2. Force Sync Account 886528 (Fixed Route)"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_url = f"{self.backend_url}/api/api/mt5/force-sync/886528"
        
        try:
            validation_results.append(f"🎯 Testing URL: {endpoint_url}")
            validation_results.append("📋 Expected: Force sync account 886528 and show balance changes")
            validation_results.append("🎯 CRITICAL: Address $521.88 discrepancy")
            validation_results.append("   Current FIDUS DB: $3,405.53")
            validation_results.append("   Target MEX Atlantic: $3,927.41")
            validation_results.append("   Expected Change: +$521.88")
            
            async with self.session.post(endpoint_url) as response:
                status_code = response.status
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except:
                    response_data = {"raw_response": response_text}
                
                if status_code == 200:
                    validation_results.append("✅ EXPECTED: HTTP 200 (not 404) - SUCCESS")
                    
                    # Check for sync results
                    if isinstance(response_data, dict):
                        if 'sync_result' in response_data or 'result' in response_data:
                            validation_results.append("✅ Sync result information present")
                        
                        # Look for balance information
                        if 'balance' in response_data or 'new_balance' in response_data or 'updated_balance' in response_data:
                            balance = response_data.get('balance', response_data.get('new_balance', response_data.get('updated_balance')))
                            validation_results.append(f"✅ Balance information: ${balance}")
                            
                            # Check if balance is closer to target $3,927.41
                            try:
                                balance_float = float(str(balance).replace('$', '').replace(',', ''))
                                target_balance = 3927.41
                                current_fidus = 3405.53
                                
                                if abs(balance_float - target_balance) < abs(current_fidus - target_balance):
                                    validation_results.append("✅ CRITICAL: Balance moved closer to MEX Atlantic target")
                                    validation_results.append(f"   New balance ${balance_float} is closer to target ${target_balance}")
                                else:
                                    validation_results.append("⚠️ Balance not significantly updated")
                            except:
                                validation_results.append("⚠️ Could not parse balance for comparison")
                        
                        if 'account_number' in response_data or 'login' in response_data:
                            account = response_data.get('account_number', response_data.get('login'))
                            if str(account) == '886528':
                                validation_results.append("✅ Correct account 886528 synced")
                            else:
                                validation_results.append(f"❌ Wrong account synced: {account}")
                    else:
                        validation_results.append("❌ Invalid sync response format")
                        
                elif status_code == 404:
                    validation_results.append("❌ CRITICAL: HTTP 404 - Endpoint not found (route not fixed)")
                else:
                    validation_results.append(f"❌ EXPECTED HTTP 200, GOT HTTP {status_code}")
                    validation_results.append(f"   Response: {response_text[:200]}")
                
                return {
                    'test_name': test_name,
                    'status': 'PASS' if status_code == 200 else 'FAIL',
                    'validation_results': validation_results,
                    'response_data': response_data,
                    'status_code': status_code
                }
                    
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"]
            }

    async def test_mt5_health_check_886528(self) -> Dict[str, Any]:
        """Test MT5 Health Check - GET /api/mt5/account-health-check/886528"""
        test_name = "3. MT5 Health Check Account 886528 (Fixed Route)"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_url = f"{self.backend_url}/api/api/mt5/account-health-check/886528"
        
        try:
            validation_results.append(f"🎯 Testing URL: {endpoint_url}")
            validation_results.append("📋 Expected: Detailed health status for account 886528")
            
            async with self.session.get(endpoint_url) as response:
                status_code = response.status
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except:
                    response_data = {"raw_response": response_text}
                
                if status_code == 200:
                    validation_results.append("✅ EXPECTED: HTTP 200 (not 404) - SUCCESS")
                    
                    # Check for health check data
                    if isinstance(response_data, dict):
                        if 'health_status' in response_data or 'status' in response_data:
                            status = response_data.get('health_status', response_data.get('status'))
                            validation_results.append(f"✅ Health status: {status}")
                        
                        if 'account_number' in response_data or 'login' in response_data:
                            account = response_data.get('account_number', response_data.get('login'))
                            if str(account) == '886528':
                                validation_results.append("✅ Correct account 886528 health checked")
                            else:
                                validation_results.append(f"❌ Wrong account: {account}")
                        
                        if 'connection_status' in response_data:
                            conn_status = response_data.get('connection_status')
                            validation_results.append(f"✅ Connection status: {conn_status}")
                        
                        if 'balance' in response_data or 'equity' in response_data:
                            balance = response_data.get('balance', response_data.get('equity'))
                            validation_results.append(f"✅ Current balance: ${balance}")
                        
                        if 'last_sync' in response_data or 'last_update' in response_data:
                            last_sync = response_data.get('last_sync', response_data.get('last_update'))
                            validation_results.append(f"✅ Last sync: {last_sync}")
                    else:
                        validation_results.append("❌ Invalid health check response format")
                        
                elif status_code == 404:
                    validation_results.append("❌ CRITICAL: HTTP 404 - Endpoint not found (route not fixed)")
                else:
                    validation_results.append(f"❌ EXPECTED HTTP 200, GOT HTTP {status_code}")
                    validation_results.append(f"   Response: {response_text[:200]}")
                
                return {
                    'test_name': test_name,
                    'status': 'PASS' if status_code == 200 else 'FAIL',
                    'validation_results': validation_results,
                    'response_data': response_data,
                    'status_code': status_code
                }
                    
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"]
            }

    async def test_start_background_sync(self) -> Dict[str, Any]:
        """Test Start Background Sync - POST /api/mt5/start-background-sync"""
        test_name = "4. Start Background Sync Control (Fixed Route)"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_url = f"{self.backend_url}/api/api/mt5/start-background-sync"
        
        try:
            validation_results.append(f"🎯 Testing URL: {endpoint_url}")
            validation_results.append("📋 Expected: Start automated sync every 2 minutes")
            
            async with self.session.post(endpoint_url) as response:
                status_code = response.status
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except:
                    response_data = {"raw_response": response_text}
                
                if status_code == 200:
                    validation_results.append("✅ EXPECTED: HTTP 200 (not 404) - SUCCESS")
                    
                    # Check for background sync start confirmation
                    if isinstance(response_data, dict):
                        if 'status' in response_data or 'message' in response_data:
                            message = response_data.get('status', response_data.get('message'))
                            validation_results.append(f"✅ Background sync status: {message}")
                        
                        if 'sync_interval' in response_data or 'interval' in response_data:
                            interval = response_data.get('sync_interval', response_data.get('interval'))
                            validation_results.append(f"✅ Sync interval: {interval}")
                            
                            # Check if it's 2 minutes as expected
                            if '2' in str(interval) and ('minute' in str(interval).lower() or 'min' in str(interval).lower()):
                                validation_results.append("✅ EXPECTED: 2-minute sync interval confirmed")
                            else:
                                validation_results.append(f"⚠️ Unexpected sync interval: {interval}")
                        
                        if 'started' in response_data or 'active' in response_data:
                            started = response_data.get('started', response_data.get('active'))
                            if started:
                                validation_results.append("✅ Background sync successfully started")
                            else:
                                validation_results.append("❌ Background sync failed to start")
                    else:
                        validation_results.append("❌ Invalid background sync response format")
                        
                elif status_code == 404:
                    validation_results.append("❌ CRITICAL: HTTP 404 - Endpoint not found (route not fixed)")
                else:
                    validation_results.append(f"❌ EXPECTED HTTP 200, GOT HTTP {status_code}")
                    validation_results.append(f"   Response: {response_text[:200]}")
                
                return {
                    'test_name': test_name,
                    'status': 'PASS' if status_code == 200 else 'FAIL',
                    'validation_results': validation_results,
                    'response_data': response_data,
                    'status_code': status_code
                }
                    
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"]
            }

    async def test_stop_background_sync(self) -> Dict[str, Any]:
        """Test Stop Background Sync - POST /api/mt5/stop-background-sync"""
        test_name = "5. Stop Background Sync Control (Fixed Route)"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_url = f"{self.backend_url}/api/api/mt5/stop-background-sync"
        
        try:
            validation_results.append(f"🎯 Testing URL: {endpoint_url}")
            validation_results.append("📋 Expected: Stop automated sync")
            
            async with self.session.post(endpoint_url) as response:
                status_code = response.status
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except:
                    response_data = {"raw_response": response_text}
                
                if status_code == 200:
                    validation_results.append("✅ EXPECTED: HTTP 200 (not 404) - SUCCESS")
                    
                    # Check for background sync stop confirmation
                    if isinstance(response_data, dict):
                        if 'status' in response_data or 'message' in response_data:
                            message = response_data.get('status', response_data.get('message'))
                            validation_results.append(f"✅ Background sync status: {message}")
                        
                        if 'stopped' in response_data or 'active' in response_data:
                            stopped = response_data.get('stopped', not response_data.get('active', True))
                            if stopped:
                                validation_results.append("✅ Background sync successfully stopped")
                            else:
                                validation_results.append("❌ Background sync failed to stop")
                    else:
                        validation_results.append("❌ Invalid background sync response format")
                        
                elif status_code == 404:
                    validation_results.append("❌ CRITICAL: HTTP 404 - Endpoint not found (route not fixed)")
                else:
                    validation_results.append(f"❌ EXPECTED HTTP 200, GOT HTTP {status_code}")
                    validation_results.append(f"   Response: {response_text[:200]}")
                
                return {
                    'test_name': test_name,
                    'status': 'PASS' if status_code == 200 else 'FAIL',
                    'validation_results': validation_results,
                    'response_data': response_data,
                    'status_code': status_code
                }
                    
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"]
            }

    async def verify_account_886528_current_state(self) -> Dict[str, Any]:
        """Verify Account 886528 Current State"""
        test_name = "6. Verify Account 886528 Current State"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        
        try:
            validation_results.append("🎯 Verifying current state of account 886528")
            validation_results.append("📋 Expected Current Balance: $3,405.53 (FIDUS database)")
            validation_results.append("📋 Expected Target Balance: $3,927.41 (MEX Atlantic live)")
            validation_results.append("📋 Expected Change: +$521.88")
            
            # Try multiple endpoints to get account state
            endpoints_to_check = [
                f"{self.backend_url}/api/mt5/admin/accounts",
                f"{self.backend_url}/api/mt5/dashboard/overview",
                f"{self.backend_url}/api/mt5/status"
            ]
            
            account_found = False
            current_balance = None
            
            for endpoint_url in endpoints_to_check:
                try:
                    async with self.session.get(endpoint_url) as response:
                        if response.status == 200:
                            response_data = await response.json()
                            
                            # Look for account 886528 in response
                            accounts = []
                            if isinstance(response_data, dict):
                                if 'accounts' in response_data:
                                    accounts = response_data['accounts']
                                elif 'mt5_accounts' in response_data:
                                    accounts = response_data['mt5_accounts']
                            elif isinstance(response_data, list):
                                accounts = response_data
                            
                            for account in accounts:
                                if isinstance(account, dict):
                                    account_num = str(account.get('account_number', account.get('login', '')))
                                    if account_num == '886528':
                                        account_found = True
                                        current_balance = account.get('balance', account.get('equity', account.get('current_balance')))
                                        validation_results.append(f"✅ Account 886528 found via {endpoint_url}")
                                        validation_results.append(f"   Current Balance: ${current_balance}")
                                        
                                        # Check broker
                                        broker = account.get('broker_name', account.get('broker', 'Unknown'))
                                        validation_results.append(f"   Broker: {broker}")
                                        
                                        if 'MEX' in str(broker).upper() or 'ATLANTIC' in str(broker).upper():
                                            validation_results.append("✅ MEX Atlantic broker confirmed")
                                        
                                        break
                            
                            if account_found:
                                break
                                
                except Exception as e:
                    validation_results.append(f"⚠️ Could not check {endpoint_url}: {str(e)}")
            
            if account_found:
                validation_results.append("✅ Account 886528 successfully located")
                
                if current_balance:
                    try:
                        balance_float = float(str(current_balance).replace('$', '').replace(',', ''))
                        expected_current = 3405.53
                        expected_target = 3927.41
                        expected_change = 521.88
                        
                        validation_results.append(f"   Current: ${balance_float}")
                        validation_results.append(f"   Expected Current: ${expected_current}")
                        validation_results.append(f"   Target: ${expected_target}")
                        
                        # Check if balance matches expected current
                        if abs(balance_float - expected_current) < 1.0:
                            validation_results.append("✅ Balance matches FIDUS database ($3,405.53)")
                        elif abs(balance_float - expected_target) < 1.0:
                            validation_results.append("🎉 CRITICAL SUCCESS: Balance updated to MEX Atlantic target ($3,927.41)")
                            validation_results.append("✅ $521.88 discrepancy RESOLVED!")
                        else:
                            discrepancy = abs(balance_float - expected_target)
                            validation_results.append(f"⚠️ Balance discrepancy: ${discrepancy:.2f} from target")
                            
                    except Exception as e:
                        validation_results.append(f"⚠️ Could not parse balance: {str(e)}")
                else:
                    validation_results.append("❌ No balance information available")
            else:
                validation_results.append("❌ CRITICAL: Account 886528 NOT found in any endpoint")
            
            return {
                'test_name': test_name,
                'status': 'PASS' if account_found else 'FAIL',
                'validation_results': validation_results,
                'account_found': account_found,
                'current_balance': current_balance
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
        """Run all MT5 Auto-Sync Service tests"""
        logger.info("🚀 Starting MT5 Auto-Sync Service Endpoints Testing")
        
        if not await self.setup():
            return {
                'success': False,
                'error': 'Test setup failed',
                'results': []
            }
        
        # Run all MT5 sync tests
        tests = [
            self.test_mt5_sync_dashboard,
            self.test_force_sync_account_886528,
            self.test_mt5_health_check_886528,
            self.test_start_background_sync,
            self.test_stop_background_sync,
            self.verify_account_886528_current_state
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
        logger.info("📊 MT5 Auto-Sync Service Testing Summary:")
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
            'test_parameters': {
                'backend_url': self.backend_url,
                'test_type': 'MT5 Auto-Sync Service Endpoints Testing',
                'focus': 'Address $521.88 discrepancy for account 886528'
            }
        }
    
    async def cleanup(self):
        """Cleanup test resources"""
        if self.session and not self.session.closed:
            await self.session.close()
        logger.info("✅ Test cleanup completed")

async def main():
    """Main test execution"""
    test_suite = MT5AutoSyncTestSuite()
    
    try:
        results = await test_suite.run_all_tests()
        
        # Print detailed results
        print("\n" + "="*80)
        print("MT5 AUTO-SYNC SERVICE ENDPOINTS TESTING")
        print("CRITICAL: Address $521.88 discrepancy for account 886528")
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
        print(f"   Backend URL: {results['test_parameters']['backend_url']}")
        
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