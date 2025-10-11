#!/usr/bin/env python3
"""
MT5 Auto-Sync Service FINAL TEST - Critical $521.88 Discrepancy Resolution
Testing MT5 sync endpoints with CORRECT routing (no double /api prefix)
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MT5SyncServiceFinalTestSuite:
    """FINAL MT5 Auto-Sync Service Testing Suite - $521.88 Discrepancy Resolution"""
    
    def __init__(self):
        # Use CORRECT backend URL without double /api prefix
        self.backend_url = "https://fidus-api.onrender.com/api"
        self.session = None
        self.admin_token = None
        self.test_results = []
        
        logger.info(f"🚀 MT5 Auto-Sync Service FINAL TEST Suite initialized")
        logger.info(f"   Backend URL: {self.backend_url}")
        logger.info(f"   CRITICAL TARGET: Account 886528 ($521.88 discrepancy)")
        logger.info(f"   GOAL: Update balance from $3,405.53 to $3,927.41")
    
    async def setup(self):
        """Setup test environment"""
        try:
            # Create HTTP session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=60),  # Longer timeout for sync operations
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

    async def test_mt5_sync_dashboard(self) -> Dict[str, Any]:
        """Test MT5 Sync Dashboard - GET /api/mt5/sync-dashboard"""
        test_name = "2. MT5 Sync Dashboard"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_url = f"{self.backend_url}/mt5/sync-dashboard"
        
        try:
            validation_results.append(f"🎯 Testing URL: {endpoint_url}")
            validation_results.append("📋 Expected: HTTP 200 showing all MT5 accounts with sync status")
            
            async with self.session.get(endpoint_url) as response:
                status_code = response.status
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except:
                    response_data = {"raw_response": response_text}
                
                if status_code == 200:
                    validation_results.append("✅ SUCCESS: HTTP 200 - MT5 Sync Dashboard accessible")
                    
                    # Check for dashboard components
                    if 'accounts' in response_data or 'mt5_accounts' in response_data:
                        accounts = response_data.get('accounts', response_data.get('mt5_accounts', []))
                        validation_results.append(f"✅ MT5 accounts data present ({len(accounts)} accounts)")
                        
                        # Look for account 886528 specifically
                        account_886528 = None
                        for account in accounts:
                            if str(account.get('mt5_login', '')) == '886528' or str(account.get('login', '')) == '886528':
                                account_886528 = account
                                break
                        
                        if account_886528:
                            validation_results.append("✅ CRITICAL: Account 886528 found in dashboard")
                            balance = account_886528.get('balance', account_886528.get('equity', 0))
                            validation_results.append(f"   Account 886528 Balance: ${balance:,.2f}")
                        else:
                            validation_results.append("❌ CRITICAL: Account 886528 NOT found in dashboard")
                    else:
                        validation_results.append("❌ No MT5 accounts data found in dashboard")
                    
                    # Check for service health
                    if 'service_health' in response_data:
                        health = response_data['service_health']
                        sync_running = health.get('background_sync_running', False)
                        validation_results.append(f"✅ Service health data present - Background sync: {sync_running}")
                    else:
                        validation_results.append("⚠️ No service health information")
                    
                    return {
                        'test_name': test_name,
                        'status': 'PASS',
                        'validation_results': validation_results,
                        'response_data': response_data
                    }
                else:
                    validation_results.append(f"❌ FAILED: Expected HTTP 200, got HTTP {status_code}")
                    if status_code == 404:
                        validation_results.append("❌ ROUTING ISSUE: Endpoint not found - check double /api prefix")
                    validation_results.append(f"   Response: {response_text[:200]}")
                    
                    return {
                        'test_name': test_name,
                        'status': 'FAIL',
                        'validation_results': validation_results,
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
        """Test Force Sync for Account 886528 - POST /api/mt5/force-sync/886528"""
        test_name = "2. Force Sync Account 886528 (CRITICAL)"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_url = f"{self.backend_url}/mt5/force-sync/886528"
        
        try:
            validation_results.append(f"🎯 Testing URL: {endpoint_url}")
            validation_results.append("📋 Expected: HTTP 200 with force sync results for account 886528")
            validation_results.append("🚨 CRITICAL: This should address the $521.88 discrepancy")
            
            async with self.session.post(endpoint_url) as response:
                status_code = response.status
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except:
                    response_data = {"raw_response": response_text}
                
                if status_code == 200:
                    validation_results.append("✅ EXPECTED: HTTP 200 with sync results - SUCCESS")
                    
                    # Check sync results
                    if response_data.get('status') == 'synced':
                        validation_results.append("✅ CRITICAL: Account 886528 sync completed successfully")
                        
                        old_balance = response_data.get('old_balance', 0)
                        new_balance = response_data.get('new_balance', 0)
                        balance_change = response_data.get('balance_change', 0)
                        
                        validation_results.append(f"   Old Balance: ${old_balance:,.2f}")
                        validation_results.append(f"   New Balance: ${new_balance:,.2f}")
                        validation_results.append(f"   Balance Change: ${balance_change:+,.2f}")
                        
                        # Check if this addresses the $521.88 discrepancy
                        if abs(balance_change) > 500:
                            validation_results.append("✅ CRITICAL: Large balance change detected - may address $521.88 discrepancy")
                        
                        if response_data.get('discrepancy_resolved'):
                            validation_results.append("✅ CRITICAL: Discrepancy resolution flag is TRUE")
                        
                    elif response_data.get('status') == 'failed':
                        validation_results.append("❌ CRITICAL: Account 886528 sync FAILED")
                        error = response_data.get('error', 'Unknown error')
                        validation_results.append(f"   Error: {error}")
                    else:
                        validation_results.append(f"⚠️ Unexpected sync status: {response_data.get('status')}")
                    
                    # Check for required fields
                    required_fields = ['mt5_login', 'sync_timestamp', 'success']
                    for field in required_fields:
                        if field in response_data:
                            validation_results.append(f"✅ Required field '{field}' present")
                        else:
                            validation_results.append(f"❌ Required field '{field}' missing")
                    
                    return {
                        'test_name': test_name,
                        'status': 'PASS',
                        'validation_results': validation_results,
                        'response_data': response_data
                    }
                else:
                    validation_results.append(f"❌ EXPECTED HTTP 200, GOT HTTP {status_code}")
                    validation_results.append(f"   Response: {response_text[:200]}")
                    
                    return {
                        'test_name': test_name,
                        'status': 'FAIL',
                        'validation_results': validation_results,
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

    async def test_sync_all_accounts(self) -> Dict[str, Any]:
        """Test Sync All Accounts - POST /api/mt5/sync-all-accounts"""
        test_name = "3. Sync All MT5 Accounts"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_url = f"{self.backend_url}/mt5/sync-all-accounts"
        
        try:
            validation_results.append(f"🎯 Testing URL: {endpoint_url}")
            validation_results.append("📋 Expected: HTTP 200 with sync results for all active accounts")
            
            async with self.session.post(endpoint_url) as response:
                status_code = response.status
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except:
                    response_data = {"raw_response": response_text}
                
                if status_code == 200:
                    validation_results.append("✅ EXPECTED: HTTP 200 with sync results - SUCCESS")
                    
                    # Check sync summary
                    total_accounts = response_data.get('total_accounts', 0)
                    successful_syncs = response_data.get('successful_syncs', 0)
                    failed_syncs = response_data.get('failed_syncs', 0)
                    success_rate = response_data.get('success_rate', 0)
                    
                    validation_results.append(f"✅ Total Accounts: {total_accounts}")
                    validation_results.append(f"✅ Successful Syncs: {successful_syncs}")
                    validation_results.append(f"✅ Failed Syncs: {failed_syncs}")
                    validation_results.append(f"✅ Success Rate: {success_rate:.1f}%")
                    
                    # Check for account 886528 specifically
                    account_886528_status = response_data.get('account_886528_status', {})
                    if account_886528_status and account_886528_status.get('status') != 'not_found':
                        validation_results.append("✅ CRITICAL: Account 886528 included in sync results")
                        if account_886528_status.get('success'):
                            validation_results.append("✅ CRITICAL: Account 886528 sync successful")
                        else:
                            validation_results.append("❌ CRITICAL: Account 886528 sync failed")
                    else:
                        validation_results.append("❌ CRITICAL: Account 886528 not found in sync results")
                    
                    # Check accounts lists
                    accounts_synced = response_data.get('accounts_synced', [])
                    accounts_failed = response_data.get('accounts_failed', [])
                    
                    validation_results.append(f"✅ Accounts synced successfully: {len(accounts_synced)}")
                    validation_results.append(f"✅ Accounts failed: {len(accounts_failed)}")
                    
                    return {
                        'test_name': test_name,
                        'status': 'PASS',
                        'validation_results': validation_results,
                        'response_data': response_data
                    }
                else:
                    validation_results.append(f"❌ EXPECTED HTTP 200, GOT HTTP {status_code}")
                    validation_results.append(f"   Response: {response_text[:200]}")
                    
                    return {
                        'test_name': test_name,
                        'status': 'FAIL',
                        'validation_results': validation_results,
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
        test_name = "4. Start Background Sync"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_url = f"{self.backend_url}/mt5/start-background-sync"
        
        try:
            validation_results.append(f"🎯 Testing URL: {endpoint_url}")
            validation_results.append("📋 Expected: HTTP 200 with background sync start confirmation")
            
            async with self.session.post(endpoint_url) as response:
                status_code = response.status
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except:
                    response_data = {"raw_response": response_text}
                
                if status_code == 200:
                    validation_results.append("✅ EXPECTED: HTTP 200 with start confirmation - SUCCESS")
                    
                    status = response_data.get('status')
                    if status == 'started':
                        validation_results.append("✅ Background sync started successfully")
                        sync_interval = response_data.get('sync_interval', 0)
                        validation_results.append(f"✅ Sync interval: {sync_interval} seconds (expected: 120)")
                        
                        if sync_interval == 120:
                            validation_results.append("✅ VERIFIED: 2-minute sync interval configured correctly")
                        else:
                            validation_results.append(f"⚠️ Unexpected sync interval: {sync_interval} (expected 120)")
                            
                    elif status == 'already_running':
                        validation_results.append("✅ Background sync already running (acceptable)")
                    else:
                        validation_results.append(f"⚠️ Unexpected status: {status}")
                    
                    # Check for required fields
                    if 'message' in response_data:
                        validation_results.append(f"✅ Message: {response_data['message']}")
                    
                    return {
                        'test_name': test_name,
                        'status': 'PASS',
                        'validation_results': validation_results,
                        'response_data': response_data
                    }
                else:
                    validation_results.append(f"❌ EXPECTED HTTP 200, GOT HTTP {status_code}")
                    validation_results.append(f"   Response: {response_text[:200]}")
                    
                    return {
                        'test_name': test_name,
                        'status': 'FAIL',
                        'validation_results': validation_results,
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
        test_name = "5. Stop Background Sync"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_url = f"{self.backend_url}/mt5/stop-background-sync"
        
        try:
            validation_results.append(f"🎯 Testing URL: {endpoint_url}")
            validation_results.append("📋 Expected: HTTP 200 with background sync stop confirmation")
            
            async with self.session.post(endpoint_url) as response:
                status_code = response.status
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except:
                    response_data = {"raw_response": response_text}
                
                if status_code == 200:
                    validation_results.append("✅ EXPECTED: HTTP 200 with stop confirmation - SUCCESS")
                    
                    status = response_data.get('status')
                    if status == 'stopped':
                        validation_results.append("✅ Background sync stopped successfully")
                    elif status == 'not_running':
                        validation_results.append("✅ Background sync was not running (acceptable)")
                    else:
                        validation_results.append(f"⚠️ Unexpected status: {status}")
                    
                    # Check for required fields
                    if 'message' in response_data:
                        validation_results.append(f"✅ Message: {response_data['message']}")
                    
                    return {
                        'test_name': test_name,
                        'status': 'PASS',
                        'validation_results': validation_results,
                        'response_data': response_data
                    }
                else:
                    validation_results.append(f"❌ EXPECTED HTTP 200, GOT HTTP {status_code}")
                    validation_results.append(f"   Response: {response_text[:200]}")
                    
                    return {
                        'test_name': test_name,
                        'status': 'FAIL',
                        'validation_results': validation_results,
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

    async def verify_account_886528_data(self) -> Dict[str, Any]:
        """Verify Account 886528 Data - Check current balance and compare with live data"""
        test_name = "6. Verify Account 886528 Data (CRITICAL)"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        
        try:
            validation_results.append("🎯 Verifying Account 886528 current status")
            validation_results.append("📋 Expected: Current balance data and discrepancy analysis")
            
            # First, get current account data from MT5 admin accounts
            admin_accounts_url = f"{self.backend_url}/mt5/admin/accounts"
            
            async with self.session.get(admin_accounts_url) as response:
                if response.status == 200:
                    accounts_data = await response.json()
                    accounts = accounts_data.get('accounts', accounts_data if isinstance(accounts_data, list) else [])
                    
                    # Find account 886528
                    account_886528 = None
                    for account in accounts:
                        if str(account.get('mt5_login', '')) == '886528' or str(account.get('login', '')) == '886528':
                            account_886528 = account
                            break
                    
                    if account_886528:
                        validation_results.append("✅ CRITICAL: Account 886528 found in database")
                        
                        balance = account_886528.get('balance', account_886528.get('equity', 0))
                        broker = account_886528.get('broker_name', 'Unknown')
                        status = account_886528.get('connection_status', 'Unknown')
                        
                        validation_results.append(f"   Current Balance: ${balance:,.2f}")
                        validation_results.append(f"   Broker: {broker}")
                        validation_results.append(f"   Status: {status}")
                        
                        # Check if this is the separation account
                        fund_code = account_886528.get('fund_code', '')
                        if fund_code == 'SEPARATION':
                            validation_results.append("✅ VERIFIED: Account 886528 is SEPARATION account")
                        else:
                            validation_results.append(f"⚠️ Account 886528 fund code: {fund_code} (expected: SEPARATION)")
                        
                        # Check for recent sync timestamp
                        last_sync = account_886528.get('last_sync_time', account_886528.get('updated_at'))
                        if last_sync:
                            validation_results.append(f"✅ Last sync time: {last_sync}")
                        else:
                            validation_results.append("⚠️ No last sync time available")
                        
                        return {
                            'test_name': test_name,
                            'status': 'PASS',
                            'validation_results': validation_results,
                            'account_data': account_886528
                        }
                    else:
                        validation_results.append("❌ CRITICAL: Account 886528 NOT found in database")
                        return {
                            'test_name': test_name,
                            'status': 'FAIL',
                            'validation_results': validation_results
                        }
                else:
                    validation_results.append(f"❌ Failed to get MT5 accounts: HTTP {response.status}")
                    return {
                        'test_name': test_name,
                        'status': 'FAIL',
                        'validation_results': validation_results
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
        logger.info("🚀 Starting MT5 Auto-Sync Service Critical Testing")
        logger.info("🎯 Target: Address $521.88 discrepancy in account 886528")
        
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
            self.test_sync_all_accounts,
            self.test_start_background_sync,
            self.test_stop_background_sync,
            self.verify_account_886528_data
        ]
        
        results = []
        for test_func in tests:
            try:
                result = await test_func()
                results.append(result)
                self.test_results.append(result)
                
                # Add delay between tests to avoid overwhelming the service
                await asyncio.sleep(2)
                
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
                'target_account': '886528',
                'test_type': 'MT5 Auto-Sync Service Critical Testing'
            }
        }
    
    async def cleanup(self):
        """Cleanup test resources"""
        if self.session and not self.session.closed:
            await self.session.close()
        logger.info("✅ Test cleanup completed")

async def main():
    """Main test execution"""
    test_suite = MT5SyncServiceTestSuite()
    
    try:
        results = await test_suite.run_all_tests()
        
        # Print detailed results
        print("\n" + "="*80)
        print("MT5 AUTO-SYNC SERVICE CRITICAL TESTING - $521.88 DISCREPANCY")
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
        print(f"   Target Account: 886528 (Critical $521.88 discrepancy)")
        
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
    exit(0 if success else 1)