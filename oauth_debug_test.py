#!/usr/bin/env python3
"""
OAuth 2.0 API Debug Investigation Test Suite
Testing OAuth connection status and API calls to capture debug output
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any
import os
import sys

# Configure logging to capture debug output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OAuthDebugTestSuite:
    """Comprehensive test suite for OAuth 2.0 debug investigation"""
    
    def __init__(self):
        # Get backend URL from environment
        self.backend_url = os.getenv('REACT_APP_BACKEND_URL', 'https://transfer-classifier.preview.emergentagent.com')
        if not self.backend_url.endswith('/api'):
            self.backend_url = f"{self.backend_url}/api"
        
        self.session = None
        self.admin_token = None
        self.test_results = []
        
        logger.info(f"🔍 OAuth Debug Test Suite initialized")
        logger.info(f"   Backend URL: {self.backend_url}")
        logger.info(f"   Admin Credentials: admin/password123")
    
    async def setup(self):
        """Setup test environment"""
        try:
            # Create HTTP session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=60),  # Longer timeout for debug calls
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
    
    async def test_oauth_token_status(self) -> Dict[str, Any]:
        """Test 1: Check Current OAuth Tokens - GET /admin/google/status"""
        test_name = "OAuth Token Status Check"
        logger.info(f"🔍 Testing {test_name}")
        
        validation_results = []
        
        try:
            url = f"{self.backend_url}/admin/google/status"
            
            async with self.session.get(url) as response:
                status_code = response.status
                response_text = await response.text()
                
                logger.info(f"🔍 [OAUTH DEBUG] Status endpoint response: {status_code}")
                logger.info(f"🔍 [OAUTH DEBUG] Response body: {response_text}")
                
                if status_code == 200:
                    validation_results.append("✅ OAuth status endpoint accessible (HTTP 200)")
                    
                    try:
                        response_data = json.loads(response_text)
                        
                        # Check for OAuth connection status
                        if 'connected' in response_data:
                            connected = response_data['connected']
                            validation_results.append(f"🔍 OAuth Connected: {connected}")
                            
                        # Check for stored scopes
                        if 'scopes' in response_data:
                            scopes = response_data['scopes']
                            validation_results.append(f"🔍 OAuth Scopes: {scopes}")
                            
                        # Check for token expiration
                        if 'expires_at' in response_data:
                            expires_at = response_data['expires_at']
                            validation_results.append(f"🔍 Token Expires: {expires_at}")
                            
                        # Check for Google account info
                        if 'google_email' in response_data:
                            google_email = response_data['google_email']
                            validation_results.append(f"🔍 Google Account: {google_email}")
                            
                        # Log full response for debugging
                        logger.info(f"🔍 [OAUTH DEBUG] Full status response: {json.dumps(response_data, indent=2)}")
                        
                    except json.JSONDecodeError:
                        validation_results.append("❌ Invalid JSON response from status endpoint")
                        logger.error(f"🔍 [OAUTH DEBUG] Invalid JSON: {response_text}")
                        
                elif status_code == 401:
                    validation_results.append("❌ OAuth status endpoint requires authentication")
                elif status_code == 404:
                    validation_results.append("❌ OAuth status endpoint not found")
                else:
                    validation_results.append(f"❌ OAuth status endpoint failed: HTTP {status_code}")
                    logger.error(f"🔍 [OAUTH DEBUG] Status endpoint error: {response_text}")
            
            return {
                'test_name': test_name,
                'status': 'PASS' if status_code == 200 else 'FAIL',
                'status_code': status_code,
                'validation_results': validation_results,
                'response_text': response_text
            }
                
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"]
            }
    
    async def test_gmail_api_debug(self) -> Dict[str, Any]:
        """Test 2: Gmail API Debug Call - GET /admin/google/gmail/messages"""
        test_name = "Gmail API Debug Call"
        logger.info(f"🔍 Testing {test_name}")
        
        validation_results = []
        
        try:
            url = f"{self.backend_url}/admin/google/gmail/messages"
            
            logger.info(f"🔍 [GMAIL DEBUG] Making Gmail API call to: {url}")
            
            async with self.session.get(url) as response:
                status_code = response.status
                response_text = await response.text()
                
                logger.info(f"🔍 [GMAIL DEBUG] Gmail API response: {status_code}")
                logger.info(f"🔍 [GMAIL DEBUG] Response body: {response_text}")
                
                if status_code == 200:
                    validation_results.append("✅ Gmail API endpoint accessible (HTTP 200)")
                    
                    try:
                        response_data = json.loads(response_text)
                        
                        # Check for messages
                        if 'messages' in response_data:
                            messages = response_data['messages']
                            message_count = len(messages) if isinstance(messages, list) else 0
                            validation_results.append(f"🔍 Gmail Messages Count: {message_count}")
                            
                            if message_count == 0:
                                validation_results.append("❌ Gmail API returns 0 messages (reported issue)")
                            else:
                                validation_results.append(f"✅ Gmail API returns {message_count} messages")
                                
                        # Check for auth_required flag
                        if 'auth_required' in response_data:
                            auth_required = response_data['auth_required']
                            validation_results.append(f"🔍 Auth Required: {auth_required}")
                            
                        # Check for source information
                        if 'source' in response_data:
                            source = response_data['source']
                            validation_results.append(f"🔍 Data Source: {source}")
                            
                        # Log full response for debugging
                        logger.info(f"🔍 [GMAIL DEBUG] Full Gmail response: {json.dumps(response_data, indent=2)}")
                        
                    except json.JSONDecodeError:
                        validation_results.append("❌ Invalid JSON response from Gmail API")
                        logger.error(f"🔍 [GMAIL DEBUG] Invalid JSON: {response_text}")
                        
                elif status_code == 401:
                    validation_results.append("❌ Gmail API requires authentication")
                elif status_code == 404:
                    validation_results.append("❌ Gmail API endpoint not found")
                else:
                    validation_results.append(f"❌ Gmail API failed: HTTP {status_code}")
                    logger.error(f"🔍 [GMAIL DEBUG] Gmail API error: {response_text}")
            
            return {
                'test_name': test_name,
                'status': 'PASS' if status_code == 200 else 'FAIL',
                'status_code': status_code,
                'validation_results': validation_results,
                'response_text': response_text
            }
                
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"]
            }
    
    async def test_calendar_api_debug(self) -> Dict[str, Any]:
        """Test 3: Calendar API Debug Call - GET /api/admin/google/calendar/events"""
        test_name = "Calendar API Debug Call"
        logger.info(f"🔍 Testing {test_name}")
        
        validation_results = []
        
        try:
            url = f"{self.backend_url}/admin/google/calendar/events"
            
            logger.info(f"🔍 [CALENDAR DEBUG] Making Calendar API call to: {url}")
            
            async with self.session.get(url) as response:
                status_code = response.status
                response_text = await response.text()
                
                logger.info(f"🔍 [CALENDAR DEBUG] Calendar API response: {status_code}")
                logger.info(f"🔍 [CALENDAR DEBUG] Response body: {response_text}")
                
                if status_code == 200:
                    validation_results.append("✅ Calendar API endpoint accessible (HTTP 200)")
                    
                    try:
                        response_data = json.loads(response_text)
                        
                        # Check for events
                        if 'events' in response_data:
                            events = response_data['events']
                            event_count = len(events) if isinstance(events, list) else 0
                            validation_results.append(f"🔍 Calendar Events Count: {event_count}")
                            
                            if event_count == 0:
                                validation_results.append("❌ Calendar API returns 0 events (reported issue)")
                            else:
                                validation_results.append(f"✅ Calendar API returns {event_count} events")
                                
                        # Check for auth_required flag
                        if 'auth_required' in response_data:
                            auth_required = response_data['auth_required']
                            validation_results.append(f"🔍 Auth Required: {auth_required}")
                            
                        # Check for source information
                        if 'source' in response_data:
                            source = response_data['source']
                            validation_results.append(f"🔍 Data Source: {source}")
                            
                        # Log full response for debugging
                        logger.info(f"🔍 [CALENDAR DEBUG] Full Calendar response: {json.dumps(response_data, indent=2)}")
                        
                    except json.JSONDecodeError:
                        validation_results.append("❌ Invalid JSON response from Calendar API")
                        logger.error(f"🔍 [CALENDAR DEBUG] Invalid JSON: {response_text}")
                        
                elif status_code == 401:
                    validation_results.append("❌ Calendar API requires authentication")
                elif status_code == 404:
                    validation_results.append("❌ Calendar API endpoint not found")
                else:
                    validation_results.append(f"❌ Calendar API failed: HTTP {status_code}")
                    logger.error(f"🔍 [CALENDAR DEBUG] Calendar API error: {response_text}")
            
            return {
                'test_name': test_name,
                'status': 'PASS' if status_code == 200 else 'FAIL',
                'status_code': status_code,
                'validation_results': validation_results,
                'response_text': response_text
            }
                
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"]
            }
    
    async def test_drive_api_debug(self) -> Dict[str, Any]:
        """Test 4: Drive API Debug Call - GET /api/admin/google/drive/files"""
        test_name = "Drive API Debug Call"
        logger.info(f"🔍 Testing {test_name}")
        
        validation_results = []
        
        try:
            url = f"{self.backend_url}/admin/google/drive/files"
            
            logger.info(f"🔍 [DRIVE DEBUG] Making Drive API call to: {url}")
            
            async with self.session.get(url) as response:
                status_code = response.status
                response_text = await response.text()
                
                logger.info(f"🔍 [DRIVE DEBUG] Drive API response: {status_code}")
                logger.info(f"🔍 [DRIVE DEBUG] Response body: {response_text}")
                
                if status_code == 200:
                    validation_results.append("✅ Drive API endpoint accessible (HTTP 200)")
                    
                    try:
                        response_data = json.loads(response_text)
                        
                        # Check for files
                        if 'files' in response_data:
                            files = response_data['files']
                            file_count = len(files) if isinstance(files, list) else 0
                            validation_results.append(f"🔍 Drive Files Count: {file_count}")
                            
                            if file_count == 0:
                                validation_results.append("❌ Drive API returns 0 files (reported issue)")
                            else:
                                validation_results.append(f"✅ Drive API returns {file_count} files")
                                
                        # Check for auth_required flag
                        if 'auth_required' in response_data:
                            auth_required = response_data['auth_required']
                            validation_results.append(f"🔍 Auth Required: {auth_required}")
                            
                        # Check for source information
                        if 'source' in response_data:
                            source = response_data['source']
                            validation_results.append(f"🔍 Data Source: {source}")
                            
                        # Log full response for debugging
                        logger.info(f"🔍 [DRIVE DEBUG] Full Drive response: {json.dumps(response_data, indent=2)}")
                        
                    except json.JSONDecodeError:
                        validation_results.append("❌ Invalid JSON response from Drive API")
                        logger.error(f"🔍 [DRIVE DEBUG] Invalid JSON: {response_text}")
                        
                elif status_code == 401:
                    validation_results.append("❌ Drive API requires authentication")
                elif status_code == 404:
                    validation_results.append("❌ Drive API endpoint not found")
                else:
                    validation_results.append(f"❌ Drive API failed: HTTP {status_code}")
                    logger.error(f"🔍 [DRIVE DEBUG] Drive API error: {response_text}")
            
            return {
                'test_name': test_name,
                'status': 'PASS' if status_code == 200 else 'FAIL',
                'status_code': status_code,
                'validation_results': validation_results,
                'response_text': response_text
            }
                
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"]
            }
    
    async def test_backend_logs_capture(self) -> Dict[str, Any]:
        """Capture backend logs to look for debug output"""
        test_name = "Backend Logs Capture"
        logger.info(f"🔍 Testing {test_name}")
        
        validation_results = []
        
        try:
            # Check if we can access backend logs
            import subprocess
            
            # Try to capture recent backend logs
            log_commands = [
                "tail -n 100 /var/log/supervisor/backend.*.log",
                "journalctl -u backend --no-pager -n 100",
                "docker logs backend 2>&1 | tail -n 100"
            ]
            
            logs_captured = False
            
            for cmd in log_commands:
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                    if result.returncode == 0 and result.stdout:
                        logs_captured = True
                        log_output = result.stdout
                        
                        # Look for OAuth debug logs
                        oauth_debug_lines = [line for line in log_output.split('\n') if '🔍 [OAUTH DEBUG]' in line]
                        gmail_debug_lines = [line for line in log_output.split('\n') if '🔍 [GMAIL DEBUG]' in line]
                        calendar_debug_lines = [line for line in log_output.split('\n') if '🔍 [CALENDAR DEBUG]' in line]
                        drive_debug_lines = [line for line in log_output.split('\n') if '🔍 [DRIVE DEBUG]' in line]
                        
                        validation_results.append(f"✅ Backend logs captured using: {cmd}")
                        validation_results.append(f"🔍 OAuth debug lines found: {len(oauth_debug_lines)}")
                        validation_results.append(f"🔍 Gmail debug lines found: {len(gmail_debug_lines)}")
                        validation_results.append(f"🔍 Calendar debug lines found: {len(calendar_debug_lines)}")
                        validation_results.append(f"🔍 Drive debug lines found: {len(drive_debug_lines)}")
                        
                        # Log the debug lines
                        for line in oauth_debug_lines[-5:]:  # Last 5 OAuth debug lines
                            logger.info(f"🔍 [OAUTH DEBUG] {line}")
                            
                        for line in gmail_debug_lines[-5:]:  # Last 5 Gmail debug lines
                            logger.info(f"🔍 [GMAIL DEBUG] {line}")
                            
                        break
                        
                except subprocess.TimeoutExpired:
                    validation_results.append(f"⚠️ Log command timeout: {cmd}")
                except Exception as e:
                    validation_results.append(f"⚠️ Log command failed: {cmd} - {str(e)}")
            
            if not logs_captured:
                validation_results.append("❌ Could not capture backend logs")
            
            return {
                'test_name': test_name,
                'status': 'PASS' if logs_captured else 'FAIL',
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
    
    async def run_oauth_debug_investigation(self) -> Dict[str, Any]:
        """Run all OAuth debug tests"""
        logger.info("🔍 Starting OAuth 2.0 Debug Investigation")
        
        if not await self.setup():
            return {
                'success': False,
                'error': 'Test setup failed',
                'results': []
            }
        
        # Run all OAuth debug tests in sequence
        tests = [
            self.test_oauth_token_status,
            self.test_gmail_api_debug,
            self.test_calendar_api_debug,
            self.test_drive_api_debug,
            self.test_backend_logs_capture
        ]
        
        results = []
        for test_func in tests:
            try:
                result = await test_func()
                results.append(result)
                self.test_results.append(result)
                
                # Add delay between tests to allow log capture
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
            'overall_status': 'INVESTIGATION_COMPLETE'
        }
        
        # Log summary
        logger.info("📊 OAuth Debug Investigation Summary:")
        logger.info(f"   Total Tests: {summary['total_tests']}")
        logger.info(f"   Passed: {summary['passed']}")
        logger.info(f"   Failed: {summary['failed']}")
        logger.info(f"   Errors: {summary['errors']}")
        logger.info(f"   Success Rate: {summary['success_rate']}%")
        
        return {
            'success': True,
            'summary': summary,
            'results': results,
            'investigation_complete': True
        }
    
    async def cleanup(self):
        """Cleanup test resources"""
        if self.session and not self.session.closed:
            await self.session.close()
        logger.info("✅ Test cleanup completed")

async def main():
    """Main test execution"""
    test_suite = OAuthDebugTestSuite()
    
    try:
        results = await test_suite.run_oauth_debug_investigation()
        
        # Print detailed results
        print("\n" + "="*80)
        print("OAUTH 2.0 DEBUG INVESTIGATION RESULTS")
        print("="*80)
        
        for result in results['results']:
            print(f"\n🔍 {result['test_name']}: {result['status']}")
            
            if 'validation_results' in result:
                for validation in result['validation_results']:
                    print(f"   {validation}")
            
            if result.get('status') == 'ERROR':
                print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
        
        print(f"\n📊 INVESTIGATION SUMMARY:")
        print(f"   Overall Status: {results['summary']['overall_status']}")
        print(f"   Success Rate: {results['summary']['success_rate']}%")
        print(f"   Tests: {results['summary']['passed']}/{results['summary']['total_tests']} passed")
        
        if results['summary']['failed'] > 0:
            print(f"   Failed Tests: {results['summary']['failed']}")
        
        if results['summary']['errors'] > 0:
            print(f"   Error Tests: {results['summary']['errors']}")
        
        print("\n🔍 DEBUG INVESTIGATION COMPLETE")
        print("   Check logs above for OAuth token processing details")
        print("   Look for 🔍 [OAUTH DEBUG], 🔍 [GMAIL DEBUG], 🔍 [CALENDAR DEBUG], 🔍 [DRIVE DEBUG] markers")
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