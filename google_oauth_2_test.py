#!/usr/bin/env python3
"""
Google OAuth 2.0 Implementation Testing
Testing the new Google OAuth 2.0 implementation that replaces the service account approach
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any
import os
import sys
from urllib.parse import urlparse, parse_qs

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GoogleOAuth2TestSuite:
    """Comprehensive test suite for Google OAuth 2.0 implementation"""
    
    def __init__(self):
        # Get backend URL from environment
        self.backend_url = os.getenv('REACT_APP_BACKEND_URL', 'https://fidus-invest.emergent.host')
        if not self.backend_url.endswith('/api'):
            self.backend_url = f"{self.backend_url}/api"
        
        self.session = None
        self.admin_token = None
        self.test_results = []
        
        # Expected OAuth configuration
        self.expected_client_id = "909926639154-r3v0ka94cbu4uo0sn8g4jvtiulf4i9qs.apps.googleusercontent.com"
        self.expected_redirect_uri = "https://fidus-invest.emergent.host/api/auth/google/callback"
        self.expected_scopes = ["gmail.readonly", "gmail.send", "calendar", "drive", "spreadsheets"]
        
        logger.info(f"🚀 Google OAuth 2.0 Test Suite initialized")
        logger.info(f"   Backend URL: {self.backend_url}")
        logger.info(f"   Expected Client ID: {self.expected_client_id}")
        logger.info(f"   Expected Redirect URI: {self.expected_redirect_uri}")
    
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
    
    async def test_oauth_url_generation(self) -> Dict[str, Any]:
        """Phase 1: Test GET /auth/google/url (requires admin JWT auth)"""
        test_name = "OAuth URL Generation"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        
        try:
            # Test OAuth URL generation endpoint
            url = f"{self.backend_url}/auth/google/url"
            async with self.session.get(url) as response:
                status_code = response.status
                
                if status_code == 200:
                    validation_results.append("✅ OAuth URL generation endpoint returns HTTP 200")
                    
                    try:
                        response_data = await response.json()
                        oauth_url = response_data.get('oauth_url') or response_data.get('url')
                        
                        if oauth_url:
                            validation_results.append("✅ OAuth URL present in response")
                            
                            # Parse OAuth URL to validate parameters
                            parsed_url = urlparse(oauth_url)
                            query_params = parse_qs(parsed_url.query)
                            
                            # Check if it's a Google OAuth URL
                            if 'accounts.google.com' in oauth_url:
                                validation_results.append("✅ OAuth URL points to Google OAuth service")
                            else:
                                validation_results.append(f"❌ OAuth URL does not point to Google: {parsed_url.netloc}")
                            
                            # Validate client_id
                            client_id = query_params.get('client_id', [None])[0]
                            if client_id == self.expected_client_id:
                                validation_results.append("✅ Correct client_id in OAuth URL")
                            else:
                                validation_results.append(f"❌ Wrong client_id: {client_id} (expected {self.expected_client_id})")
                            
                            # Validate redirect_uri
                            redirect_uri = query_params.get('redirect_uri', [None])[0]
                            if redirect_uri == self.expected_redirect_uri:
                                validation_results.append("✅ Correct redirect_uri in OAuth URL")
                            else:
                                validation_results.append(f"❌ Wrong redirect_uri: {redirect_uri} (expected {self.expected_redirect_uri})")
                            
                            # Validate scopes
                            scope = query_params.get('scope', [None])[0]
                            if scope:
                                scopes_in_url = scope.split(' ')
                                missing_scopes = [s for s in self.expected_scopes if s not in scopes_in_url]
                                if not missing_scopes:
                                    validation_results.append(f"✅ All required scopes present: {scopes_in_url}")
                                else:
                                    validation_results.append(f"❌ Missing scopes: {missing_scopes}")
                            else:
                                validation_results.append("❌ No scope parameter in OAuth URL")
                            
                            # Validate access_type=offline
                            access_type = query_params.get('access_type', [None])[0]
                            if access_type == 'offline':
                                validation_results.append("✅ access_type=offline for refresh tokens")
                            else:
                                validation_results.append(f"❌ Wrong access_type: {access_type} (expected offline)")
                            
                            # Validate prompt=consent
                            prompt = query_params.get('prompt', [None])[0]
                            if prompt == 'consent':
                                validation_results.append("✅ prompt=consent for refresh tokens")
                            else:
                                validation_results.append(f"❌ Wrong prompt: {prompt} (expected consent)")
                            
                            # Log the full OAuth URL for debugging
                            logger.info(f"   Generated OAuth URL: {oauth_url}")
                            
                        else:
                            validation_results.append("❌ No OAuth URL in response")
                            
                    except json.JSONDecodeError:
                        response_text = await response.text()
                        validation_results.append(f"❌ Invalid JSON response: {response_text[:200]}")
                        
                elif status_code == 401:
                    validation_results.append("❌ OAuth URL generation requires authentication (401)")
                else:
                    error_text = await response.text()
                    validation_results.append(f"❌ OAuth URL generation failed: HTTP {status_code} - {error_text[:200]}")
            
            # Test without authentication
            original_headers = self.session.headers.copy()
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            async with self.session.get(url) as response:
                if response.status == 401:
                    validation_results.append("✅ OAuth URL generation properly requires admin JWT auth")
                else:
                    validation_results.append(f"❌ OAuth URL generation should require auth (got {response.status})")
            
            # Restore auth headers
            self.session.headers.update(original_headers)
            
            # Determine overall status
            failed_checks = [result for result in validation_results if result.startswith("❌")]
            overall_status = 'PASS' if len(failed_checks) == 0 else 'FAIL'
            
            return {
                'test_name': test_name,
                'status': overall_status,
                'validation_results': validation_results,
                'details': {
                    'endpoint': url,
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
    
    async def test_connection_status(self) -> Dict[str, Any]:
        """Phase 2: Test GET /admin/google/status (requires admin JWT auth)"""
        test_name = "Connection Status"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        
        try:
            # Test connection status endpoint
            url = f"{self.backend_url}/admin/google/status"
            async with self.session.get(url) as response:
                status_code = response.status
                
                if status_code == 200:
                    validation_results.append("✅ Connection status endpoint returns HTTP 200")
                    
                    try:
                        response_data = await response.json()
                        
                        # Check response structure
                        if 'status' in response_data:
                            status_obj = response_data['status']
                            validation_results.append("✅ Status object present in response")
                            
                            # Check required fields
                            if 'connected' in status_obj:
                                connected = status_obj['connected']
                                validation_results.append(f"✅ Connected field present: {connected}")
                            else:
                                validation_results.append("❌ Missing 'connected' field in status")
                            
                            if 'is_expired' in status_obj:
                                is_expired = status_obj['is_expired']
                                validation_results.append(f"✅ is_expired field present: {is_expired}")
                            else:
                                validation_results.append("❌ Missing 'is_expired' field in status")
                            
                            if 'scopes' in status_obj:
                                scopes = status_obj['scopes']
                                if isinstance(scopes, list):
                                    validation_results.append(f"✅ Scopes array present: {scopes}")
                                else:
                                    validation_results.append(f"❌ Scopes should be array, got: {type(scopes)}")
                            else:
                                validation_results.append("❌ Missing 'scopes' field in status")
                            
                            # Since no OAuth tokens exist yet, should show not connected
                            if status_obj.get('connected') == False:
                                validation_results.append("✅ Correctly shows not connected (no OAuth tokens)")
                            else:
                                validation_results.append("⚠️ Shows connected (unexpected without OAuth)")
                            
                        else:
                            validation_results.append("❌ No 'status' object in response")
                        
                        logger.info(f"   Connection Status Response: {response_data}")
                        
                    except json.JSONDecodeError:
                        response_text = await response.text()
                        validation_results.append(f"❌ Invalid JSON response: {response_text[:200]}")
                        
                elif status_code == 401:
                    validation_results.append("❌ Connection status requires authentication (401)")
                else:
                    error_text = await response.text()
                    validation_results.append(f"❌ Connection status failed: HTTP {status_code} - {error_text[:200]}")
            
            # Test without authentication
            original_headers = self.session.headers.copy()
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            async with self.session.get(url) as response:
                if response.status == 401:
                    validation_results.append("✅ Connection status properly requires admin JWT auth")
                else:
                    validation_results.append(f"❌ Connection status should require auth (got {response.status})")
            
            # Restore auth headers
            self.session.headers.update(original_headers)
            
            # Determine overall status
            failed_checks = [result for result in validation_results if result.startswith("❌")]
            overall_status = 'PASS' if len(failed_checks) == 0 else 'FAIL'
            
            return {
                'test_name': test_name,
                'status': overall_status,
                'validation_results': validation_results,
                'details': {
                    'endpoint': url,
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
    
    async def test_google_api_endpoints_auth_required(self) -> Dict[str, Any]:
        """Phase 3: Test Google API endpoints should fail with auth required"""
        test_name = "Google API Endpoints Auth Required"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        
        # List of Google API endpoints to test
        endpoints_to_test = [
            ("/google/gmail/real-messages", "Gmail Messages"),
            ("/google/calendar/events", "Calendar Events"),
            ("/google/drive/files", "Drive Files")
        ]
        
        try:
            for endpoint_path, endpoint_name in endpoints_to_test:
                url = f"{self.backend_url}{endpoint_path}"
                
                async with self.session.get(url) as response:
                    status_code = response.status
                    
                    if status_code == 401:
                        validation_results.append(f"✅ {endpoint_name} returns 401 (auth required)")
                    elif status_code == 200:
                        # Check if response indicates auth required
                        try:
                            response_data = await response.json()
                            if response_data.get('auth_required') == True:
                                validation_results.append(f"✅ {endpoint_name} returns auth_required=true")
                            else:
                                validation_results.append(f"❌ {endpoint_name} should require OAuth auth")
                        except:
                            validation_results.append(f"❌ {endpoint_name} should require OAuth auth")
                    else:
                        error_text = await response.text()
                        validation_results.append(f"⚠️ {endpoint_name} returns {status_code}: {error_text[:100]}")
                
                logger.info(f"   {endpoint_name}: HTTP {status_code}")
            
            # Test without admin JWT auth
            original_headers = self.session.headers.copy()
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            for endpoint_path, endpoint_name in endpoints_to_test:
                url = f"{self.backend_url}{endpoint_path}"
                
                async with self.session.get(url) as response:
                    if response.status == 401:
                        validation_results.append(f"✅ {endpoint_name} requires admin JWT auth")
                    else:
                        validation_results.append(f"❌ {endpoint_name} should require admin JWT auth")
            
            # Restore auth headers
            self.session.headers.update(original_headers)
            
            # Determine overall status
            failed_checks = [result for result in validation_results if result.startswith("❌")]
            overall_status = 'PASS' if len(failed_checks) == 0 else 'FAIL'
            
            return {
                'test_name': test_name,
                'status': overall_status,
                'validation_results': validation_results,
                'details': {
                    'endpoints_tested': len(endpoints_to_test),
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
    
    async def test_legacy_compatibility(self) -> Dict[str, Any]:
        """Phase 4: Test legacy compatibility endpoints"""
        test_name = "Legacy Compatibility"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        
        try:
            # Test legacy Gmail endpoint
            url = f"{self.backend_url}/google/gmail/real-messages"
            async with self.session.get(url) as response:
                status_code = response.status
                
                if status_code == 200:
                    validation_results.append("✅ Legacy Gmail endpoint accessible")
                    
                    try:
                        response_data = await response.json()
                        
                        # Should use OAuth now and return auth_required
                        if response_data.get('auth_required') == True:
                            validation_results.append("✅ Legacy endpoint now uses OAuth (auth_required=true)")
                        elif 'messages' in response_data and len(response_data['messages']) == 0:
                            validation_results.append("✅ Legacy endpoint returns empty messages (OAuth required)")
                        else:
                            validation_results.append("⚠️ Legacy endpoint behavior unclear")
                        
                        logger.info(f"   Legacy Gmail Response: {response_data}")
                        
                    except json.JSONDecodeError:
                        response_text = await response.text()
                        validation_results.append(f"❌ Invalid JSON response: {response_text[:200]}")
                        
                elif status_code == 401:
                    validation_results.append("✅ Legacy Gmail endpoint requires authentication")
                else:
                    error_text = await response.text()
                    validation_results.append(f"❌ Legacy Gmail endpoint failed: HTTP {status_code} - {error_text[:200]}")
            
            # Test without authentication
            original_headers = self.session.headers.copy()
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            async with self.session.get(url) as response:
                if response.status == 401:
                    validation_results.append("✅ Legacy endpoint properly requires admin JWT auth")
                else:
                    validation_results.append(f"❌ Legacy endpoint should require auth (got {response.status})")
            
            # Restore auth headers
            self.session.headers.update(original_headers)
            
            # Determine overall status
            failed_checks = [result for result in validation_results if result.startswith("❌")]
            overall_status = 'PASS' if len(failed_checks) == 0 else 'FAIL'
            
            return {
                'test_name': test_name,
                'status': overall_status,
                'validation_results': validation_results,
                'details': {
                    'endpoint': url,
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
    
    async def test_no_500_errors(self) -> Dict[str, Any]:
        """Test that no 500 errors occur from service account failures"""
        test_name = "No 500 Errors from Service Account"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        
        # List of endpoints that previously might have had service account issues
        endpoints_to_test = [
            ("/auth/google/authorize", "OAuth URL Generation"),
            ("/admin/google/status", "Connection Status"),
            ("/admin/google/gmail/messages", "Gmail Messages"),
            ("/admin/google/calendar/events", "Calendar Events"),
            ("/admin/google/drive/files", "Drive Files"),
            ("/google/gmail/real-messages", "Legacy Gmail")
        ]
        
        try:
            for endpoint_path, endpoint_name in endpoints_to_test:
                url = f"{self.backend_url}{endpoint_path}"
                
                async with self.session.get(url) as response:
                    status_code = response.status
                    
                    if status_code == 500:
                        error_text = await response.text()
                        validation_results.append(f"❌ {endpoint_name} returns 500 error: {error_text[:100]}")
                    else:
                        validation_results.append(f"✅ {endpoint_name} no 500 error (HTTP {status_code})")
                
                logger.info(f"   {endpoint_name}: HTTP {status_code}")
            
            # Determine overall status
            failed_checks = [result for result in validation_results if result.startswith("❌")]
            overall_status = 'PASS' if len(failed_checks) == 0 else 'FAIL'
            
            return {
                'test_name': test_name,
                'status': overall_status,
                'validation_results': validation_results,
                'details': {
                    'endpoints_tested': len(endpoints_to_test),
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
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all Google OAuth 2.0 tests"""
        logger.info("🚀 Starting Google OAuth 2.0 Test Suite")
        
        if not await self.setup():
            return {
                'success': False,
                'error': 'Test setup failed',
                'results': []
            }
        
        # Run all OAuth 2.0 tests
        tests = [
            self.test_oauth_url_generation,
            self.test_connection_status,
            self.test_google_api_endpoints_auth_required,
            self.test_legacy_compatibility,
            self.test_no_500_errors
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
        logger.info("📊 Google OAuth 2.0 Test Summary:")
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
                'expected_client_id': self.expected_client_id,
                'expected_redirect_uri': self.expected_redirect_uri,
                'expected_scopes': self.expected_scopes
            }
        }
    
    async def cleanup(self):
        """Cleanup test resources"""
        if self.session and not self.session.closed:
            await self.session.close()
        logger.info("✅ Test cleanup completed")

async def main():
    """Main test execution"""
    test_suite = GoogleOAuth2TestSuite()
    
    try:
        results = await test_suite.run_all_tests()
        
        # Print detailed results
        print("\n" + "="*80)
        print("GOOGLE OAUTH 2.0 IMPLEMENTATION TEST RESULTS")
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