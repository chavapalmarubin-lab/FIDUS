#!/usr/bin/env python3
"""
MT5 Health Check Endpoint Testing for Account 886528
Testing the newly implemented MT5 health check endpoint and debug endpoints
Focus: Analyze the $521.88 discrepancy for account 886528
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

class MT5HealthCheckTestSuite:
    """MT5 Health Check and Debug Endpoint Testing Suite for Account 886528"""
    
    def __init__(self):
        # Use backend URL from environment configuration
        self.backend_url = "https://fidus-api.onrender.com/api"
        
        self.session = None
        self.admin_token = None
        self.test_results = []
        self.target_account = "886528"
        self.discrepancy_analysis = {}
        
        logger.info(f"🚀 MT5 Health Check Test Suite initialized")
        logger.info(f"   Backend URL: {self.backend_url}")
        logger.info(f"   Target Account: {self.target_account}")
        logger.info(f"   Purpose: Test MT5 health check and analyze $521.88 discrepancy")
    
    async def setup(self):
        """Setup test environment"""
        try:
            # Create HTTP session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=60),
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
        """Test NEW MT5 Health Check Endpoint for Account 886528"""
        test_name = f"1. MT5 Account Health Check - Account {self.target_account}"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_url = f"{self.backend_url}/mt5/account-health-check/{self.target_account}"
        
        try:
            validation_results.append(f"🎯 Testing URL: {endpoint_url}")
            validation_results.append(f"📋 Expected: Detailed health check with database vs live MT5 data comparison")
            
            async with self.session.get(endpoint_url) as response:
                status_code = response.status
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except:
                    response_data = {"raw_response": response_text}
                
                if status_code == 200:
                    validation_results.append("✅ EXPECTED: HTTP 200 with health check data - SUCCESS")
                    
                    # Analyze health check response
                    if isinstance(response_data, dict):
                        # Check for required fields
                        required_fields = ['mt5_login', 'status', 'database', 'mt5_live', 'discrepancy']
                        missing_fields = [field for field in required_fields if field not in response_data]
                        
                        if not missing_fields:
                            validation_results.append("✅ All required health check fields present")
                        else:
                            validation_results.append(f"⚠️ Missing fields: {missing_fields}")
                        
                        # Extract key data for discrepancy analysis
                        if 'database' in response_data and 'mt5_live' in response_data:
                            db_data = response_data['database']
                            live_data = response_data['mt5_live']
                            discrepancy = response_data.get('discrepancy', {})
                            
                            validation_results.append(f"📊 Database Balance: ${db_data.get('balance', 0):,.2f}")
                            validation_results.append(f"📊 Live MT5 Balance: ${live_data.get('balance', 0):,.2f}")
                            validation_results.append(f"📊 Balance Difference: {discrepancy.get('balance_diff_usd', '$0.00')}")
                            
                            # Store discrepancy data for analysis
                            self.discrepancy_analysis['health_check'] = {
                                'database_balance': db_data.get('balance', 0),
                                'live_balance': live_data.get('balance', 0),
                                'balance_diff': discrepancy.get('balance_diff', 0),
                                'balance_diff_usd': discrepancy.get('balance_diff_usd', '$0.00'),
                                'status': response_data.get('status'),
                                'severity': response_data.get('severity'),
                                'recommendation': response_data.get('recommendation')
                            }
                            
                            # Check if this matches the reported $521.88 discrepancy
                            balance_diff = abs(discrepancy.get('balance_diff', 0))
                            if 520 <= balance_diff <= 525:
                                validation_results.append(f"🎯 CRITICAL: Found expected ~$521.88 discrepancy: ${balance_diff:.2f}")
                            elif balance_diff > 0:
                                validation_results.append(f"⚠️ Different discrepancy found: ${balance_diff:.2f}")
                            else:
                                validation_results.append("✅ No significant discrepancy detected")
                        
                        # Check sync status
                        sync_status = response_data.get('status', 'unknown')
                        validation_results.append(f"🔄 Sync Status: {sync_status}")
                        
                        if sync_status == 'out_of_sync':
                            validation_results.append("⚠️ Account is out of sync - discrepancy confirmed")
                        elif sync_status == 'synced':
                            validation_results.append("✅ Account is in sync")
                        elif sync_status == 'no_live_data':
                            validation_results.append("❌ No live MT5 data available")
                    
                    return {
                        'test_name': test_name,
                        'status': 'PASS',
                        'validation_results': validation_results,
                        'response_data': response_data,
                        'endpoint_url': endpoint_url
                    }
                else:
                    validation_results.append(f"❌ EXPECTED HTTP 200, GOT HTTP {status_code}")
                    validation_results.append(f"   Response: {response_text[:200]}")
                    
                    return {
                        'test_name': test_name,
                        'status': 'FAIL',
                        'validation_results': validation_results,
                        'response_text': response_text,
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
        """Test MT5 Connection Test Debug Endpoint"""
        test_name = "2. MT5 Connection Test Debug Endpoint"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_url = f"{self.backend_url}/debug/mt5/connection-test"
        
        try:
            validation_results.append(f"🎯 Testing URL: {endpoint_url}")
            
            async with self.session.get(endpoint_url) as response:
                status_code = response.status
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except:
                    response_data = {"raw_response": response_text}
                
                validation_results.append(f"📊 Status Code: HTTP {status_code}")
                
                if status_code == 200:
                    validation_results.append("✅ MT5 Connection Test endpoint accessible")
                    
                    # Check for connection status
                    if isinstance(response_data, dict):
                        if 'status' in response_data or 'connection' in response_data:
                            validation_results.append("✅ Connection status information present")
                        
                        # Store connection data
                        self.discrepancy_analysis['connection_test'] = response_data
                else:
                    validation_results.append(f"❌ Connection test failed: HTTP {status_code}")
                
                return {
                    'test_name': test_name,
                    'status': 'PASS' if status_code == 200 else 'FAIL',
                    'validation_results': validation_results,
                    'response_data': response_data,
                    'endpoint_url': endpoint_url
                }
                
        except Exception as e:
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"],
                'endpoint_url': endpoint_url
            }

    async def test_mt5_sync_status(self) -> Dict[str, Any]:
        """Test MT5 Sync Status Debug Endpoint"""
        test_name = "3. MT5 Sync Status Debug Endpoint"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_url = f"{self.backend_url}/debug/mt5/sync-status"
        
        try:
            validation_results.append(f"🎯 Testing URL: {endpoint_url}")
            
            async with self.session.get(endpoint_url) as response:
                status_code = response.status
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except:
                    response_data = {"raw_response": response_text}
                
                validation_results.append(f"📊 Status Code: HTTP {status_code}")
                
                if status_code == 200:
                    validation_results.append("✅ MT5 Sync Status endpoint accessible")
                    
                    # Store sync status data
                    self.discrepancy_analysis['sync_status'] = response_data
                else:
                    validation_results.append(f"❌ Sync status failed: HTTP {status_code}")
                
                return {
                    'test_name': test_name,
                    'status': 'PASS' if status_code == 200 else 'FAIL',
                    'validation_results': validation_results,
                    'response_data': response_data,
                    'endpoint_url': endpoint_url
                }
                
        except Exception as e:
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"],
                'endpoint_url': endpoint_url
            }

    async def test_mt5_data_comparison(self) -> Dict[str, Any]:
        """Test MT5 Data Comparison Debug Endpoint for Account 886528"""
        test_name = f"4. MT5 Data Comparison - Account {self.target_account}"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_url = f"{self.backend_url}/debug/mt5/data-comparison/{self.target_account}"
        
        try:
            validation_results.append(f"🎯 Testing URL: {endpoint_url}")
            
            async with self.session.get(endpoint_url) as response:
                status_code = response.status
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except:
                    response_data = {"raw_response": response_text}
                
                validation_results.append(f"📊 Status Code: HTTP {status_code}")
                
                if status_code == 200:
                    validation_results.append("✅ MT5 Data Comparison endpoint accessible")
                    
                    # Analyze comparison data for discrepancies
                    if isinstance(response_data, dict):
                        if 'database' in response_data and 'live' in response_data:
                            db_data = response_data['database']
                            live_data = response_data['live']
                            
                            validation_results.append(f"📊 DB Balance: ${db_data.get('balance', 0):,.2f}")
                            validation_results.append(f"📊 Live Balance: ${live_data.get('balance', 0):,.2f}")
                            
                            # Calculate difference
                            db_balance = float(db_data.get('balance', 0))
                            live_balance = float(live_data.get('balance', 0))
                            difference = abs(live_balance - db_balance)
                            
                            validation_results.append(f"📊 Difference: ${difference:,.2f}")
                            
                            # Check for the expected $521.88 discrepancy
                            if 520 <= difference <= 525:
                                validation_results.append(f"🎯 CRITICAL: Found expected ~$521.88 discrepancy!")
                    
                    # Store comparison data
                    self.discrepancy_analysis['data_comparison'] = response_data
                else:
                    validation_results.append(f"❌ Data comparison failed: HTTP {status_code}")
                
                return {
                    'test_name': test_name,
                    'status': 'PASS' if status_code == 200 else 'FAIL',
                    'validation_results': validation_results,
                    'response_data': response_data,
                    'endpoint_url': endpoint_url
                }
                
        except Exception as e:
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"],
                'endpoint_url': endpoint_url
            }

    async def test_mt5_raw_account_data(self) -> Dict[str, Any]:
        """Test MT5 Raw Account Data Debug Endpoint for Account 886528"""
        test_name = f"5. MT5 Raw Account Data - Account {self.target_account}"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_url = f"{self.backend_url}/debug/mt5/raw-account-data/{self.target_account}"
        
        try:
            validation_results.append(f"🎯 Testing URL: {endpoint_url}")
            
            async with self.session.get(endpoint_url) as response:
                status_code = response.status
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except:
                    response_data = {"raw_response": response_text}
                
                validation_results.append(f"📊 Status Code: HTTP {status_code}")
                
                if status_code == 200:
                    validation_results.append("✅ MT5 Raw Account Data endpoint accessible")
                    
                    # Store raw account data
                    self.discrepancy_analysis['raw_account_data'] = response_data
                    
                    # Analyze raw data for account details
                    if isinstance(response_data, dict):
                        if 'balance' in response_data:
                            validation_results.append(f"📊 Raw Balance: ${response_data.get('balance', 0):,.2f}")
                        if 'equity' in response_data:
                            validation_results.append(f"📊 Raw Equity: ${response_data.get('equity', 0):,.2f}")
                        if 'profit' in response_data:
                            validation_results.append(f"📊 Raw Profit: ${response_data.get('profit', 0):,.2f}")
                else:
                    validation_results.append(f"❌ Raw account data failed: HTTP {status_code}")
                
                return {
                    'test_name': test_name,
                    'status': 'PASS' if status_code == 200 else 'FAIL',
                    'validation_results': validation_results,
                    'response_data': response_data,
                    'endpoint_url': endpoint_url
                }
                
        except Exception as e:
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"],
                'endpoint_url': endpoint_url
            }

    def analyze_discrepancy(self) -> Dict[str, Any]:
        """Analyze the $521.88 discrepancy based on collected data"""
        logger.info("🔍 Analyzing MT5 data discrepancy for account 886528")
        
        analysis = {
            'target_discrepancy': 521.88,
            'found_discrepancies': [],
            'root_cause_analysis': [],
            'recommendations': []
        }
        
        # Check health check data
        if 'health_check' in self.discrepancy_analysis:
            health_data = self.discrepancy_analysis['health_check']
            balance_diff = abs(health_data.get('balance_diff', 0))
            
            analysis['found_discrepancies'].append({
                'source': 'health_check',
                'amount': balance_diff,
                'matches_target': 520 <= balance_diff <= 525,
                'status': health_data.get('status'),
                'severity': health_data.get('severity')
            })
        
        # Check data comparison
        if 'data_comparison' in self.discrepancy_analysis:
            comp_data = self.discrepancy_analysis['data_comparison']
            if isinstance(comp_data, dict) and 'database' in comp_data and 'live' in comp_data:
                db_balance = float(comp_data['database'].get('balance', 0))
                live_balance = float(comp_data['live'].get('balance', 0))
                difference = abs(live_balance - db_balance)
                
                analysis['found_discrepancies'].append({
                    'source': 'data_comparison',
                    'amount': difference,
                    'matches_target': 520 <= difference <= 525,
                    'db_balance': db_balance,
                    'live_balance': live_balance
                })
        
        # Root cause analysis
        if any(d['matches_target'] for d in analysis['found_discrepancies']):
            analysis['root_cause_analysis'].extend([
                "✅ CONFIRMED: $521.88 discrepancy found in account 886528",
                "🔍 LIKELY CAUSES:",
                "   - Sync timing issue between database and live MT5 data",
                "   - Pending transactions not reflected in database",
                "   - MT5 bridge connection intermittency",
                "   - Data mapping inconsistency in sync process"
            ])
            
            analysis['recommendations'].extend([
                "🔧 IMMEDIATE ACTIONS:",
                "   1. Force refresh MT5 data sync for account 886528",
                "   2. Check MT5 bridge connection stability",
                "   3. Verify transaction history for missing entries",
                "   4. Review sync process logs for errors"
            ])
        else:
            analysis['root_cause_analysis'].append("⚠️ Expected $521.88 discrepancy not found in current data")
            analysis['recommendations'].append("🔍 Investigate if discrepancy was already resolved or if account number is incorrect")
        
        return analysis

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all MT5 health check and debug endpoint tests"""
        logger.info("🚀 Starting MT5 Health Check Testing for Account 886528")
        
        if not await self.setup():
            return {
                'success': False,
                'error': 'Test setup failed',
                'results': []
            }
        
        # Run all MT5 tests
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
        
        # Perform discrepancy analysis
        discrepancy_analysis = self.analyze_discrepancy()
        
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
        
        return {
            'success': summary['overall_status'] == 'PASS',
            'summary': summary,
            'results': results,
            'discrepancy_analysis': discrepancy_analysis,
            'target_account': self.target_account,
            'test_parameters': {
                'backend_url': self.backend_url,
                'test_type': 'MT5 Health Check and Debug Testing'
            }
        }
    
    async def cleanup(self):
        """Cleanup test resources"""
        if self.session and not self.session.closed:
            await self.session.close()
        logger.info("✅ Test cleanup completed")

async def main():
    """Main test execution"""
    test_suite = MT5HealthCheckTestSuite()
    
    try:
        results = await test_suite.run_all_tests()
        
        # Print detailed results
        print("\n" + "="*80)
        print("MT5 HEALTH CHECK TESTING - ACCOUNT 886528 DISCREPANCY ANALYSIS")
        print("="*80)
        
        for result in results['results']:
            print(f"\n🧪 {result['test_name']}: {result['status']}")
            
            if 'validation_results' in result:
                for validation in result['validation_results']:
                    print(f"   {validation}")
            
            if result.get('status') == 'ERROR':
                print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
        
        # Print discrepancy analysis
        print(f"\n🔍 DISCREPANCY ANALYSIS:")
        print("="*50)
        analysis = results['discrepancy_analysis']
        
        print(f"Target Discrepancy: ${analysis['target_discrepancy']}")
        print(f"Found Discrepancies: {len(analysis['found_discrepancies'])}")
        
        for discrepancy in analysis['found_discrepancies']:
            print(f"\n📊 Source: {discrepancy['source']}")
            print(f"   Amount: ${discrepancy['amount']:,.2f}")
            print(f"   Matches Target: {'✅ YES' if discrepancy['matches_target'] else '❌ NO'}")
        
        print(f"\n🔍 ROOT CAUSE ANALYSIS:")
        for cause in analysis['root_cause_analysis']:
            print(f"   {cause}")
        
        print(f"\n🔧 RECOMMENDATIONS:")
        for rec in analysis['recommendations']:
            print(f"   {rec}")
        
        print(f"\n📊 SUMMARY:")
        print(f"   Overall Status: {results['summary']['overall_status']}")
        print(f"   Success Rate: {results['summary']['success_rate']}%")
        print(f"   Tests: {results['summary']['passed']}/{results['summary']['total_tests']} passed")
        print(f"   Backend URL: {results['test_parameters']['backend_url']}")
        
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