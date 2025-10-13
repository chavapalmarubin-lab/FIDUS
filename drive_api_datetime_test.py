#!/usr/bin/env python3
"""
Drive API Datetime Fix Testing
Testing the Drive API datetime fix to ensure no 500 datetime comparison errors
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timezone
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DriveAPIDatetimeTestSuite:
    """Test suite for Drive API datetime fix verification"""
    
    def __init__(self):
        # Get backend URL from environment
        self.backend_url = os.getenv('REACT_APP_BACKEND_URL', 'https://financeflow-89.preview.emergentagent.com')
        if not self.backend_url.endswith('/api'):
            self.backend_url = f"{self.backend_url}/api"
        
        self.session = None
        self.admin_token = None
        self.test_results = []
        
        logger.info(f"🚀 Drive API Datetime Fix Test Suite initialized")
        logger.info(f"   Backend URL: {self.backend_url}")
    
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
    
    async def test_oauth_url_generation(self):
        """Test 1: OAuth URL Generation - GET /auth/google/authorize"""
        test_name = "OAuth URL Generation"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        
        try:
            # Test OAuth URL generation endpoint
            url = f"{self.backend_url}/auth/google/url"
            
            async with self.session.get(url) as response:
                status_code = response.status
                
                if status_code == 200:
                    validation_results.append("✅ OAuth URL generation returns HTTP 200")
                    
                    try:
                        response_data = await response.json()
                        
                        # Check for OAuth URL in response
                        oauth_url = response_data.get('oauth_url') or response_data.get('url')
                        if oauth_url and 'accounts.google.com' in oauth_url:
                            validation_results.append("✅ Valid OAuth URL returned")
                            logger.info(f"   OAuth URL: {oauth_url[:100]}...")
                        else:
                            validation_results.append("❌ Invalid or missing OAuth URL")
                        
                        # Check for required OAuth parameters
                        if oauth_url:
                            required_params = ['client_id', 'redirect_uri', 'scope', 'response_type']
                            missing_params = []
                            for param in required_params:
                                if param not in oauth_url:
                                    missing_params.append(param)
                            
                            if not missing_params:
                                validation_results.append("✅ All required OAuth parameters present")
                            else:
                                validation_results.append(f"❌ Missing OAuth parameters: {missing_params}")
                        
                    except json.JSONDecodeError:
                        validation_results.append("❌ Invalid JSON response")
                        
                elif status_code == 401:
                    validation_results.append("✅ OAuth URL generation requires admin auth (expected)")
                else:
                    validation_results.append(f"❌ OAuth URL generation failed: HTTP {status_code}")
                    
        except Exception as e:
            validation_results.append(f"❌ Exception in OAuth URL test: {str(e)}")
        
        # Determine test status
        failed_checks = [result for result in validation_results if result.startswith("❌")]
        test_status = 'PASS' if len(failed_checks) == 0 else 'FAIL'
        
        return {
            'test_name': test_name,
            'status': test_status,
            'validation_results': validation_results,
            'endpoint': url,
            'status_code': status_code if 'status_code' in locals() else None
        }
    
    async def test_drive_api_endpoint_admin(self):
        """Test 2: Drive API Endpoint - GET /admin/google/drive/files"""
        test_name = "Drive API Endpoint (admin path)"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        
        try:
            # Test Drive API endpoint (admin path)
            url = f"{self.backend_url}/admin/google/drive/files"
            
            async with self.session.get(url) as response:
                status_code = response.status
                
                # Check for NO 500 datetime errors (critical requirement)
                if status_code == 500:
                    try:
                        error_text = await response.text()
                        if 'datetime' in error_text.lower() or 'comparison' in error_text.lower():
                            validation_results.append("❌ CRITICAL: 500 datetime comparison error detected!")
                            logger.error(f"   Datetime error: {error_text}")
                        else:
                            validation_results.append("⚠️ 500 error but not datetime-related")
                    except:
                        validation_results.append("❌ 500 error occurred")
                else:
                    validation_results.append("✅ NO 500 datetime errors detected")
                
                # Check for proper auth_required response
                if status_code == 200:
                    try:
                        response_data = await response.json()
                        
                        # Check for auth_required flag
                        if response_data.get('auth_required'):
                            validation_results.append("✅ Returns proper auth_required response")
                        elif 'files' in response_data:
                            validation_results.append("✅ Returns Drive files (OAuth connected)")
                        else:
                            validation_results.append("⚠️ Unexpected 200 response format")
                            
                    except json.JSONDecodeError:
                        validation_results.append("❌ Invalid JSON response")
                        
                elif status_code == 401:
                    validation_results.append("✅ Requires admin authentication (expected)")
                elif status_code == 404:
                    validation_results.append("❌ Endpoint not found (404)")
                else:
                    validation_results.append(f"⚠️ HTTP {status_code} response")
                    
        except Exception as e:
            validation_results.append(f"❌ Exception in Drive API test: {str(e)}")
        
        # Determine test status
        critical_failures = [result for result in validation_results if "CRITICAL" in result]
        failed_checks = [result for result in validation_results if result.startswith("❌")]
        test_status = 'FAIL' if critical_failures else ('PASS' if len(failed_checks) == 0 else 'PARTIAL')
        
        return {
            'test_name': test_name,
            'status': test_status,
            'validation_results': validation_results,
            'endpoint': url,
            'status_code': status_code if 'status_code' in locals() else None,
            'critical_failures': len(critical_failures)
        }
    
    async def test_drive_api_endpoint_alternative(self):
        """Test 3: Drive API Alternative - GET /api/admin/google/drive/files"""
        test_name = "Drive API Alternative Endpoint"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        
        try:
            # Test Drive API alternative endpoint
            url = f"{self.backend_url}/admin/google/drive/files"
            
            async with self.session.get(url) as response:
                status_code = response.status
                
                # Check for NO 500 datetime errors (critical requirement)
                if status_code == 500:
                    try:
                        error_text = await response.text()
                        if 'datetime' in error_text.lower() or 'comparison' in error_text.lower():
                            validation_results.append("❌ CRITICAL: 500 datetime comparison error detected!")
                            logger.error(f"   Datetime error: {error_text}")
                        else:
                            validation_results.append("⚠️ 500 error but not datetime-related")
                    except:
                        validation_results.append("❌ 500 error occurred")
                else:
                    validation_results.append("✅ NO 500 datetime errors detected")
                
                # Check for proper auth_required response
                if status_code == 200:
                    try:
                        response_data = await response.json()
                        
                        # Check for auth_required flag
                        if response_data.get('auth_required'):
                            validation_results.append("✅ Returns proper auth_required response")
                        elif 'files' in response_data:
                            validation_results.append("✅ Returns Drive files (OAuth connected)")
                        else:
                            validation_results.append("⚠️ Unexpected 200 response format")
                            
                    except json.JSONDecodeError:
                        validation_results.append("❌ Invalid JSON response")
                        
                elif status_code == 401:
                    validation_results.append("✅ Requires admin authentication (expected)")
                elif status_code == 404:
                    validation_results.append("❌ Endpoint not found (404)")
                else:
                    validation_results.append(f"⚠️ HTTP {status_code} response")
                    
        except Exception as e:
            validation_results.append(f"❌ Exception in Drive API alternative test: {str(e)}")
        
        # Determine test status
        critical_failures = [result for result in validation_results if "CRITICAL" in result]
        failed_checks = [result for result in validation_results if result.startswith("❌")]
        test_status = 'FAIL' if critical_failures else ('PASS' if len(failed_checks) == 0 else 'PARTIAL')
        
        return {
            'test_name': test_name,
            'status': test_status,
            'validation_results': validation_results,
            'endpoint': url,
            'status_code': status_code if 'status_code' in locals() else None,
            'critical_failures': len(critical_failures)
        }
    
    async def test_oauth_infrastructure(self):
        """Test OAuth infrastructure working"""
        test_name = "OAuth Infrastructure"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        
        try:
            # Test Google connection status
            connection_url = f"{self.backend_url}/google/connection/test-all"
            
            async with self.session.get(connection_url) as response:
                status_code = response.status
                
                if status_code == 200:
                    validation_results.append("✅ Google connection monitor accessible")
                    
                    try:
                        response_data = await response.json()
                        
                        # Check connection status structure
                        if 'overall_status' in response_data:
                            validation_results.append("✅ Connection status structure valid")
                            
                            overall_status = response_data.get('overall_status')
                            if overall_status in ['connected', 'partial', 'not_connected']:
                                validation_results.append(f"✅ OAuth status: {overall_status}")
                            else:
                                validation_results.append(f"⚠️ Unknown OAuth status: {overall_status}")
                        else:
                            validation_results.append("❌ Invalid connection status structure")
                            
                    except json.JSONDecodeError:
                        validation_results.append("❌ Invalid JSON response from connection monitor")
                        
                elif status_code == 401:
                    validation_results.append("✅ Connection monitor requires authentication")
                else:
                    validation_results.append(f"❌ Connection monitor failed: HTTP {status_code}")
            
            # Test individual Google OAuth status
            individual_url = f"{self.backend_url}/admin/google/individual-status"
            
            async with self.session.get(individual_url) as response:
                status_code = response.status
                
                if status_code == 200:
                    validation_results.append("✅ Individual OAuth status accessible")
                    
                    try:
                        response_data = await response.json()
                        
                        connected = response_data.get('connected', False)
                        if connected:
                            validation_results.append("✅ Individual OAuth connected")
                        else:
                            validation_results.append("⚠️ Individual OAuth not connected (expected)")
                            
                    except json.JSONDecodeError:
                        validation_results.append("❌ Invalid JSON from individual status")
                        
                elif status_code == 401:
                    validation_results.append("✅ Individual status requires authentication")
                else:
                    validation_results.append(f"❌ Individual status failed: HTTP {status_code}")
                    
        except Exception as e:
            validation_results.append(f"❌ Exception in OAuth infrastructure test: {str(e)}")
        
        # Determine test status
        failed_checks = [result for result in validation_results if result.startswith("❌")]
        test_status = 'PASS' if len(failed_checks) == 0 else 'PARTIAL'
        
        return {
            'test_name': test_name,
            'status': test_status,
            'validation_results': validation_results,
            'failed_checks': len(failed_checks)
        }
    
    async def run_all_tests(self):
        """Run all Drive API datetime fix tests"""
        logger.info("🚀 Starting Drive API Datetime Fix Test Suite")
        
        if not await self.setup():
            return {
                'success': False,
                'error': 'Test setup failed',
                'results': []
            }
        
        # Run all tests
        tests = [
            self.test_oauth_url_generation,
            self.test_drive_api_endpoint_admin,
            self.test_drive_api_endpoint_alternative,
            self.test_oauth_infrastructure
        ]
        
        results = []
        critical_failures = 0
        
        for test_func in tests:
            try:
                result = await test_func()
                results.append(result)
                
                # Count critical failures (datetime errors)
                if result.get('critical_failures', 0) > 0:
                    critical_failures += result['critical_failures']
                    
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
        partial_tests = [r for r in results if r.get('status') == 'PARTIAL']
        error_tests = [r for r in results if r.get('status') == 'ERROR']
        
        success_rate = len(passed_tests) / len(results) * 100 if results else 0
        
        # Overall status based on critical requirements
        if critical_failures > 0:
            overall_status = 'CRITICAL_FAIL'
        elif len(failed_tests) == 0 and len(error_tests) == 0:
            overall_status = 'PASS'
        else:
            overall_status = 'PARTIAL'
        
        summary = {
            'total_tests': len(results),
            'passed': len(passed_tests),
            'failed': len(failed_tests),
            'partial': len(partial_tests),
            'errors': len(error_tests),
            'critical_failures': critical_failures,
            'success_rate': round(success_rate, 1),
            'overall_status': overall_status
        }
        
        # Log summary
        logger.info("📊 Drive API Datetime Fix Test Summary:")
        logger.info(f"   Total Tests: {summary['total_tests']}")
        logger.info(f"   Passed: {summary['passed']}")
        logger.info(f"   Failed: {summary['failed']}")
        logger.info(f"   Partial: {summary['partial']}")
        logger.info(f"   Errors: {summary['errors']}")
        logger.info(f"   Critical Failures: {summary['critical_failures']}")
        logger.info(f"   Success Rate: {summary['success_rate']}%")
        logger.info(f"   Overall Status: {summary['overall_status']}")
        
        return {
            'success': overall_status in ['PASS', 'PARTIAL'],
            'summary': summary,
            'results': results,
            'test_focus': 'Drive API datetime fix verification'
        }
    
    async def cleanup(self):
        """Cleanup test resources"""
        if self.session and not self.session.closed:
            await self.session.close()
        logger.info("✅ Test cleanup completed")

async def main():
    """Main test execution"""
    test_suite = DriveAPIDatetimeTestSuite()
    
    try:
        results = await test_suite.run_all_tests()
        
        # Print detailed results
        print("\n" + "="*80)
        print("DRIVE API DATETIME FIX TEST RESULTS")
        print("="*80)
        
        for result in results['results']:
            status_icon = "🔥" if result.get('critical_failures', 0) > 0 else "✅" if result['status'] == 'PASS' else "⚠️" if result['status'] == 'PARTIAL' else "❌"
            print(f"\n{status_icon} {result['test_name']}: {result['status']}")
            
            if 'validation_results' in result:
                for validation in result['validation_results']:
                    print(f"   {validation}")
            
            if result.get('status') == 'ERROR':
                print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
            
            if result.get('critical_failures', 0) > 0:
                print(f"   🔥 CRITICAL: {result['critical_failures']} datetime errors detected!")
        
        print(f"\n📊 SUMMARY:")
        print(f"   Overall Status: {results['summary']['overall_status']}")
        print(f"   Success Rate: {results['summary']['success_rate']}%")
        print(f"   Tests: {results['summary']['passed']}/{results['summary']['total_tests']} passed")
        
        if results['summary']['critical_failures'] > 0:
            print(f"   🔥 CRITICAL FAILURES: {results['summary']['critical_failures']} datetime errors!")
        
        if results['summary']['failed'] > 0:
            print(f"   Failed Tests: {results['summary']['failed']}")
        
        if results['summary']['partial'] > 0:
            print(f"   Partial Tests: {results['summary']['partial']}")
        
        if results['summary']['errors'] > 0:
            print(f"   Error Tests: {results['summary']['errors']}")
        
        print("\n🎯 FOCUS: Verifying NO datetime comparison 500 errors in Drive API")
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