#!/usr/bin/env python3
"""
MT5 Diagnostic Endpoints Production Testing
Testing all MT5 diagnostic endpoints on production URL for final verification
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

class MT5DiagnosticProductionTestSuite:
    """MT5 Diagnostic Endpoints Production Testing Suite"""
    
    def __init__(self):
        # Production URL from review request
        self.production_url = "https://fidus-api.onrender.com"
        self.backend_url = f"{self.production_url}/api"
        
        self.session = None
        self.admin_token = None
        self.test_results = []
        self.account_886528_data = {}
        
        logger.info(f"🚀 MT5 Diagnostic Production Test Suite initialized")
        logger.info(f"   Production URL: {self.production_url}")
        logger.info(f"   API Base URL: {self.backend_url}")
        logger.info(f"   Target Account: 886528")
    
    async def setup(self):
        """Setup test environment"""
        try:
            # Create HTTP session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=60),  # Longer timeout for production
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

    async def test_mt5_account_health_check(self) -> Dict[str, Any]:
        """Test MT5 Account Health Check Endpoint - GET /api/mt5/account-health-check/886528"""
        test_name = "1. MT5 Account Health Check (886528)"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_url = f"{self.backend_url}/mt5/account-health-check/886528"
        
        try:
            validation_results.append(f"🎯 Testing URL: {endpoint_url}")
            validation_results.append("📋 Expected: Account health status for separation account 886528")
            
            async with self.session.get(endpoint_url) as response:
                status_code = response.status
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except:
                    response_data = {"raw_response": response_text}
                
                if status_code == 200:
                    validation_results.append("✅ HTTP 200 - Account health check successful")
                    
                    # Store account data for comparison
                    self.account_886528_data['health_check'] = response_data
                    
                    # Validate response structure
                    if isinstance(response_data, dict):
                        if 'account_number' in response_data:
                            validation_results.append(f"✅ Account Number: {response_data.get('account_number')}")
                        
                        if 'balance' in response_data or 'equity' in response_data:
                            balance = response_data.get('balance', response_data.get('equity', 'N/A'))
                            validation_results.append(f"✅ Account Balance/Equity: {balance}")
                        
                        if 'status' in response_data or 'connection_status' in response_data:
                            status = response_data.get('status', response_data.get('connection_status', 'N/A'))
                            validation_results.append(f"✅ Connection Status: {status}")
                        
                        if 'broker' in response_data or 'broker_name' in response_data:
                            broker = response_data.get('broker', response_data.get('broker_name', 'N/A'))
                            validation_results.append(f"✅ Broker: {broker}")
                        
                        # Check for separation account specific data
                        if 'fund_type' in response_data:
                            fund_type = response_data.get('fund_type')
                            if fund_type == 'SEPARATION':
                                validation_results.append("✅ Confirmed: SEPARATION fund type")
                            else:
                                validation_results.append(f"⚠️ Fund type: {fund_type} (expected SEPARATION)")
                    
                    return {
                        'test_name': test_name,
                        'status': 'PASS',
                        'validation_results': validation_results,
                        'response_data': response_data,
                        'endpoint_url': endpoint_url
                    }
                    
                elif status_code == 404:
                    validation_results.append("❌ HTTP 404 - Account 886528 not found")
                    return {
                        'test_name': test_name,
                        'status': 'FAIL',
                        'validation_results': validation_results,
                        'error': 'Account not found',
                        'endpoint_url': endpoint_url
                    }
                    
                elif status_code == 500:
                    validation_results.append("❌ HTTP 500 - Server error during health check")
                    validation_results.append(f"   Response: {response_text[:200]}")
                    return {
                        'test_name': test_name,
                        'status': 'FAIL',
                        'validation_results': validation_results,
                        'error': 'Server error',
                        'endpoint_url': endpoint_url
                    }
                    
                else:
                    validation_results.append(f"❌ Unexpected status code: {status_code}")
                    validation_results.append(f"   Response: {response_text[:200]}")
                    return {
                        'test_name': test_name,
                        'status': 'FAIL',
                        'validation_results': validation_results,
                        'error': f'HTTP {status_code}',
                        'endpoint_url': endpoint_url
                    }
                    
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"],
                'endpoint_url': endpoint_url
            }

    async def test_mt5_connection_test(self) -> Dict[str, Any]:
        """Test MT5 Debug Connection Test - GET /api/debug/mt5/connection-test"""
        test_name = "2. MT5 Debug Connection Test"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_url = f"{self.backend_url}/debug/mt5/connection-test"
        
        try:
            validation_results.append(f"🎯 Testing URL: {endpoint_url}")
            validation_results.append("📋 Expected: MT5 bridge connection status")
            
            async with self.session.get(endpoint_url) as response:
                status_code = response.status
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except:
                    response_data = {"raw_response": response_text}
                
                if status_code == 200:
                    validation_results.append("✅ HTTP 200 - Connection test successful")
                    
                    # Validate connection test response
                    if isinstance(response_data, dict):
                        if 'bridge_status' in response_data or 'connection_status' in response_data:
                            status = response_data.get('bridge_status', response_data.get('connection_status'))
                            validation_results.append(f"✅ Bridge Status: {status}")
                        
                        if 'bridge_url' in response_data:
                            bridge_url = response_data.get('bridge_url')
                            validation_results.append(f"✅ Bridge URL: {bridge_url}")
                        
                        if 'response_time' in response_data:
                            response_time = response_data.get('response_time')
                            validation_results.append(f"✅ Response Time: {response_time}")
                        
                        if 'error' in response_data:
                            error = response_data.get('error')
                            validation_results.append(f"⚠️ Error reported: {error}")
                    
                    return {
                        'test_name': test_name,
                        'status': 'PASS',
                        'validation_results': validation_results,
                        'response_data': response_data,
                        'endpoint_url': endpoint_url
                    }
                    
                else:
                    validation_results.append(f"❌ HTTP {status_code} - Connection test failed")
                    validation_results.append(f"   Response: {response_text[:200]}")
                    return {
                        'test_name': test_name,
                        'status': 'FAIL',
                        'validation_results': validation_results,
                        'error': f'HTTP {status_code}',
                        'endpoint_url': endpoint_url
                    }
                    
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"],
                'endpoint_url': endpoint_url
            }

    async def test_mt5_sync_status(self) -> Dict[str, Any]:
        """Test MT5 Debug Sync Status - GET /api/debug/mt5/sync-status"""
        test_name = "3. MT5 Debug Sync Status"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_url = f"{self.backend_url}/debug/mt5/sync-status"
        
        try:
            validation_results.append(f"🎯 Testing URL: {endpoint_url}")
            validation_results.append("📋 Expected: MT5 data synchronization status")
            
            async with self.session.get(endpoint_url) as response:
                status_code = response.status
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except:
                    response_data = {"raw_response": response_text}
                
                if status_code == 200:
                    validation_results.append("✅ HTTP 200 - Sync status retrieved")
                    
                    # Validate sync status response
                    if isinstance(response_data, dict):
                        if 'sync_status' in response_data:
                            sync_status = response_data.get('sync_status')
                            validation_results.append(f"✅ Sync Status: {sync_status}")
                        
                        if 'last_sync' in response_data:
                            last_sync = response_data.get('last_sync')
                            validation_results.append(f"✅ Last Sync: {last_sync}")
                        
                        if 'accounts_synced' in response_data:
                            accounts_synced = response_data.get('accounts_synced')
                            validation_results.append(f"✅ Accounts Synced: {accounts_synced}")
                        
                        if 'sync_errors' in response_data:
                            sync_errors = response_data.get('sync_errors')
                            if sync_errors:
                                validation_results.append(f"⚠️ Sync Errors: {sync_errors}")
                            else:
                                validation_results.append("✅ No sync errors reported")
                    
                    return {
                        'test_name': test_name,
                        'status': 'PASS',
                        'validation_results': validation_results,
                        'response_data': response_data,
                        'endpoint_url': endpoint_url
                    }
                    
                else:
                    validation_results.append(f"❌ HTTP {status_code} - Sync status failed")
                    validation_results.append(f"   Response: {response_text[:200]}")
                    return {
                        'test_name': test_name,
                        'status': 'FAIL',
                        'validation_results': validation_results,
                        'error': f'HTTP {status_code}',
                        'endpoint_url': endpoint_url
                    }
                    
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"],
                'endpoint_url': endpoint_url
            }

    async def test_mt5_data_comparison(self) -> Dict[str, Any]:
        """Test MT5 Debug Data Comparison - GET /api/debug/mt5/data-comparison/886528"""
        test_name = "4. MT5 Debug Data Comparison (886528)"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_url = f"{self.backend_url}/debug/mt5/data-comparison/886528"
        
        try:
            validation_results.append(f"🎯 Testing URL: {endpoint_url}")
            validation_results.append("📋 Expected: Data comparison between database and MT5 for account 886528")
            
            async with self.session.get(endpoint_url) as response:
                status_code = response.status
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except:
                    response_data = {"raw_response": response_text}
                
                if status_code == 200:
                    validation_results.append("✅ HTTP 200 - Data comparison successful")
                    
                    # Store comparison data
                    self.account_886528_data['data_comparison'] = response_data
                    
                    # Validate comparison response
                    if isinstance(response_data, dict):
                        if 'database_data' in response_data:
                            db_data = response_data.get('database_data')
                            validation_results.append("✅ Database data present")
                            if isinstance(db_data, dict) and 'balance' in db_data:
                                db_balance = db_data.get('balance')
                                validation_results.append(f"✅ Database Balance: {db_balance}")
                        
                        if 'mt5_data' in response_data:
                            mt5_data = response_data.get('mt5_data')
                            validation_results.append("✅ MT5 data present")
                            if isinstance(mt5_data, dict) and 'balance' in mt5_data:
                                mt5_balance = mt5_data.get('balance')
                                validation_results.append(f"✅ MT5 Balance: {mt5_balance}")
                        
                        if 'discrepancy' in response_data:
                            discrepancy = response_data.get('discrepancy')
                            validation_results.append(f"✅ Discrepancy: {discrepancy}")
                            
                            # Check for the reported $521.88 difference
                            if isinstance(discrepancy, (int, float)):
                                if abs(discrepancy - 521.88) < 1.0:
                                    validation_results.append("🎯 CONFIRMED: ~$521.88 discrepancy found")
                                else:
                                    validation_results.append(f"⚠️ Different discrepancy amount: ${discrepancy}")
                        
                        if 'sync_issues' in response_data:
                            sync_issues = response_data.get('sync_issues')
                            if sync_issues:
                                validation_results.append(f"⚠️ Sync Issues: {sync_issues}")
                            else:
                                validation_results.append("✅ No sync issues reported")
                    
                    return {
                        'test_name': test_name,
                        'status': 'PASS',
                        'validation_results': validation_results,
                        'response_data': response_data,
                        'endpoint_url': endpoint_url
                    }
                    
                else:
                    validation_results.append(f"❌ HTTP {status_code} - Data comparison failed")
                    validation_results.append(f"   Response: {response_text[:200]}")
                    return {
                        'test_name': test_name,
                        'status': 'FAIL',
                        'validation_results': validation_results,
                        'error': f'HTTP {status_code}',
                        'endpoint_url': endpoint_url
                    }
                    
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"],
                'endpoint_url': endpoint_url
            }

    async def test_mt5_raw_account_data(self) -> Dict[str, Any]:
        """Test MT5 Debug Raw Account Data - GET /api/debug/mt5/raw-account-data/886528"""
        test_name = "5. MT5 Debug Raw Account Data (886528)"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_url = f"{self.backend_url}/debug/mt5/raw-account-data/886528"
        
        try:
            validation_results.append(f"🎯 Testing URL: {endpoint_url}")
            validation_results.append("📋 Expected: Raw MT5 account data for account 886528")
            
            async with self.session.get(endpoint_url) as response:
                status_code = response.status
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except:
                    response_data = {"raw_response": response_text}
                
                if status_code == 200:
                    validation_results.append("✅ HTTP 200 - Raw account data retrieved")
                    
                    # Store raw data
                    self.account_886528_data['raw_data'] = response_data
                    
                    # Validate raw data response
                    if isinstance(response_data, dict):
                        if 'account_info' in response_data:
                            account_info = response_data.get('account_info')
                            validation_results.append("✅ Account info present")
                            
                            if isinstance(account_info, dict):
                                if 'login' in account_info:
                                    login = account_info.get('login')
                                    validation_results.append(f"✅ Account Login: {login}")
                                
                                if 'balance' in account_info:
                                    balance = account_info.get('balance')
                                    validation_results.append(f"✅ Raw Balance: {balance}")
                                
                                if 'equity' in account_info:
                                    equity = account_info.get('equity')
                                    validation_results.append(f"✅ Raw Equity: {equity}")
                                
                                if 'margin' in account_info:
                                    margin = account_info.get('margin')
                                    validation_results.append(f"✅ Raw Margin: {margin}")
                        
                        if 'positions' in response_data:
                            positions = response_data.get('positions')
                            if isinstance(positions, list):
                                validation_results.append(f"✅ Positions: {len(positions)} found")
                            else:
                                validation_results.append("✅ Positions data present")
                        
                        if 'orders' in response_data:
                            orders = response_data.get('orders')
                            if isinstance(orders, list):
                                validation_results.append(f"✅ Orders: {len(orders)} found")
                            else:
                                validation_results.append("✅ Orders data present")
                        
                        if 'history' in response_data:
                            history = response_data.get('history')
                            validation_results.append("✅ History data present")
                    
                    return {
                        'test_name': test_name,
                        'status': 'PASS',
                        'validation_results': validation_results,
                        'response_data': response_data,
                        'endpoint_url': endpoint_url
                    }
                    
                else:
                    validation_results.append(f"❌ HTTP {status_code} - Raw data retrieval failed")
                    validation_results.append(f"   Response: {response_text[:200]}")
                    return {
                        'test_name': test_name,
                        'status': 'FAIL',
                        'validation_results': validation_results,
                        'error': f'HTTP {status_code}',
                        'endpoint_url': endpoint_url
                    }
                    
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"],
                'endpoint_url': endpoint_url
            }

    async def analyze_account_886528_status(self) -> Dict[str, Any]:
        """Analyze current status of account 886528 based on all collected data"""
        analysis_name = "6. Account 886528 Status Analysis"
        logger.info(f"🧪 Performing {analysis_name}")
        
        analysis_results = []
        
        try:
            analysis_results.append("📊 ACCOUNT 886528 COMPREHENSIVE ANALYSIS:")
            analysis_results.append("="*50)
            
            # Analyze health check data
            if 'health_check' in self.account_886528_data:
                health_data = self.account_886528_data['health_check']
                analysis_results.append("✅ Health Check Data Available:")
                
                if isinstance(health_data, dict):
                    for key, value in health_data.items():
                        analysis_results.append(f"   {key}: {value}")
            else:
                analysis_results.append("❌ Health Check Data: Not Available")
            
            # Analyze comparison data
            if 'data_comparison' in self.account_886528_data:
                comparison_data = self.account_886528_data['data_comparison']
                analysis_results.append("\n✅ Data Comparison Available:")
                
                if isinstance(comparison_data, dict):
                    db_balance = None
                    mt5_balance = None
                    
                    if 'database_data' in comparison_data:
                        db_data = comparison_data['database_data']
                        if isinstance(db_data, dict) and 'balance' in db_data:
                            db_balance = db_data['balance']
                            analysis_results.append(f"   Database Balance: {db_balance}")
                    
                    if 'mt5_data' in comparison_data:
                        mt5_data = comparison_data['mt5_data']
                        if isinstance(mt5_data, dict) and 'balance' in mt5_data:
                            mt5_balance = mt5_data['balance']
                            analysis_results.append(f"   MT5 Balance: {mt5_balance}")
                    
                    if db_balance is not None and mt5_balance is not None:
                        calculated_diff = abs(float(db_balance) - float(mt5_balance))
                        analysis_results.append(f"   Calculated Difference: ${calculated_diff:.2f}")
                        
                        if abs(calculated_diff - 521.88) < 1.0:
                            analysis_results.append("   🎯 CONFIRMED: ~$521.88 discrepancy matches report")
                        else:
                            analysis_results.append(f"   ⚠️ Different from reported $521.88 discrepancy")
            else:
                analysis_results.append("❌ Data Comparison: Not Available")
            
            # Analyze raw data
            if 'raw_data' in self.account_886528_data:
                raw_data = self.account_886528_data['raw_data']
                analysis_results.append("\n✅ Raw Data Available:")
                
                if isinstance(raw_data, dict) and 'account_info' in raw_data:
                    account_info = raw_data['account_info']
                    if isinstance(account_info, dict):
                        for key in ['login', 'balance', 'equity', 'margin']:
                            if key in account_info:
                                analysis_results.append(f"   Raw {key.title()}: {account_info[key]}")
            else:
                analysis_results.append("❌ Raw Data: Not Available")
            
            # Overall status assessment
            analysis_results.append("\n📋 OVERALL ASSESSMENT:")
            
            data_sources = len(self.account_886528_data)
            if data_sources >= 3:
                analysis_results.append("✅ Comprehensive data collection successful")
            elif data_sources >= 2:
                analysis_results.append("⚠️ Partial data collection - some endpoints failed")
            else:
                analysis_results.append("❌ Limited data collection - most endpoints failed")
            
            return {
                'analysis_name': analysis_name,
                'status': 'COMPLETE',
                'analysis_results': analysis_results,
                'data_sources_count': data_sources,
                'collected_data': self.account_886528_data
            }
            
        except Exception as e:
            logger.error(f"❌ {analysis_name} failed: {str(e)}")
            return {
                'analysis_name': analysis_name,
                'status': 'ERROR',
                'error': str(e),
                'analysis_results': [f"❌ Analysis Exception: {str(e)}"]
            }

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all MT5 diagnostic endpoint tests"""
        logger.info("🚀 Starting MT5 Diagnostic Production Testing")
        
        if not await self.setup():
            return {
                'success': False,
                'error': 'Test setup failed',
                'results': []
            }
        
        # Run all diagnostic tests
        tests = [
            self.test_mt5_account_health_check,
            self.test_mt5_connection_test,
            self.test_mt5_sync_status,
            self.test_mt5_data_comparison,
            self.test_mt5_raw_account_data
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
        
        # Perform account analysis
        try:
            analysis_result = await self.analyze_account_886528_status()
            results.append(analysis_result)
        except Exception as e:
            logger.error(f"❌ Account analysis failed: {str(e)}")
        
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
        logger.info("📊 MT5 Diagnostic Testing Summary:")
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
            'account_886528_data': self.account_886528_data,
            'test_parameters': {
                'production_url': self.production_url,
                'backend_url': self.backend_url,
                'target_account': '886528',
                'test_type': 'MT5 Diagnostic Production Testing'
            }
        }
    
    async def cleanup(self):
        """Cleanup test resources"""
        if self.session and not self.session.closed:
            await self.session.close()
        logger.info("✅ Test cleanup completed")

async def main():
    """Main test execution"""
    test_suite = MT5DiagnosticProductionTestSuite()
    
    try:
        results = await test_suite.run_all_tests()
        
        # Print detailed results
        print("\n" + "="*80)
        print("MT5 DIAGNOSTIC ENDPOINTS PRODUCTION TESTING")
        print("="*80)
        print(f"Production URL: {results['test_parameters']['production_url']}")
        print(f"Target Account: {results['test_parameters']['target_account']}")
        
        for result in results['results']:
            if 'test_name' in result:
                print(f"\n🧪 {result['test_name']}: {result['status']}")
            elif 'analysis_name' in result:
                print(f"\n📊 {result['analysis_name']}: {result['status']}")
            
            if 'validation_results' in result:
                for validation in result['validation_results']:
                    print(f"   {validation}")
            
            if 'analysis_results' in result:
                for analysis in result['analysis_results']:
                    print(f"   {analysis}")
            
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
        
        # Print deployment validation
        print(f"\n🚀 DEPLOYMENT VALIDATION:")
        if results['summary']['passed'] >= 3:
            print("   ✅ MT5 diagnostic endpoints are deployed correctly")
        else:
            print("   ❌ MT5 diagnostic endpoints have deployment issues")
        
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