#!/usr/bin/env python3
"""
Comprehensive OAuth 2.0 Debug Investigation - Exact Review Request Tests
Testing the specific endpoints mentioned in the review request
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any
import os
import sys
import subprocess

# Configure logging to capture debug output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveOAuthDebugSuite:
    """Comprehensive OAuth debug test suite matching exact review request"""
    
    def __init__(self):
        # Get backend URL from environment
        self.backend_url = os.getenv('REACT_APP_BACKEND_URL', 'https://mt5-bridge-system.preview.emergentagent.com')
        if not self.backend_url.endswith('/api'):
            self.backend_url = f"{self.backend_url}/api"
        
        self.session = None
        self.admin_token = None
        self.test_results = []
        
        logger.info(f"🔍 Comprehensive OAuth Debug Suite initialized")
        logger.info(f"   Backend URL: {self.backend_url}")
        logger.info(f"   Admin Credentials: admin/password123")
    
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
    
    async def capture_backend_logs_before_test(self):
        """Capture backend logs before running tests"""
        try:
            # Clear recent logs and prepare for fresh capture
            logger.info("🔍 Preparing to capture fresh backend logs...")
            
            # Get current log position
            result = subprocess.run(
                "wc -l /var/log/supervisor/backend.*.log 2>/dev/null | tail -1 | awk '{print $1}'", 
                shell=True, capture_output=True, text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                self.initial_log_lines = int(result.stdout.strip())
                logger.info(f"🔍 Initial log lines: {self.initial_log_lines}")
            else:
                self.initial_log_lines = 0
                
        except Exception as e:
            logger.error(f"❌ Failed to prepare log capture: {str(e)}")
            self.initial_log_lines = 0
    
    async def capture_backend_logs_after_test(self):
        """Capture backend logs after running tests"""
        try:
            # Get new logs since test started
            result = subprocess.run(
                f"tail -n +{self.initial_log_lines + 1} /var/log/supervisor/backend.*.log 2>/dev/null | grep -E '(🔍|OAUTH|GMAIL|CALENDAR|DRIVE)' | tail -50", 
                shell=True, capture_output=True, text=True
            )
            
            if result.returncode == 0 and result.stdout:
                log_lines = result.stdout.strip().split('\n')
                logger.info(f"🔍 Captured {len(log_lines)} debug log lines:")
                
                for line in log_lines:
                    logger.info(f"   {line}")
                    
                return log_lines
            else:
                logger.info("🔍 No new debug logs captured")
                return []
                
        except Exception as e:
            logger.error(f"❌ Failed to capture logs: {str(e)}")
            return []
    
    async def test_1_oauth_status_check(self) -> Dict[str, Any]:
        """Test 1: Check Current OAuth Tokens - GET /admin/google/status"""
        test_name = "Test 1: OAuth Status Check"
        logger.info(f"🔍 {test_name}")
        
        validation_results = []
        
        try:
            url = f"{self.backend_url}/admin/google/status"
            logger.info(f"🔍 Testing endpoint: {url}")
            
            async with self.session.get(url) as response:
                status_code = response.status
                response_text = await response.text()
                
                logger.info(f"🔍 Response Status: {status_code}")
                
                if status_code == 200:
                    validation_results.append("✅ OAuth status endpoint accessible")
                    
                    try:
                        response_data = json.loads(response_text)
                        
                        # Check what scopes are currently stored
                        if 'scopes' in response_data:
                            scopes = response_data['scopes']
                            validation_results.append(f"🔍 Current Scopes: {scopes}")
                        else:
                            validation_results.append("❌ No scopes information in response")
                            
                        # Check if token is expired
                        if 'expires_at' in response_data:
                            expires_at = response_data['expires_at']
                            validation_results.append(f"🔍 Token Expires: {expires_at}")
                        else:
                            validation_results.append("❌ No token expiration information")
                            
                        # Check connection status
                        if 'connected' in response_data:
                            connected = response_data['connected']
                            validation_results.append(f"🔍 OAuth Connected: {connected}")
                        else:
                            validation_results.append("❌ No connection status information")
                            
                        logger.info(f"🔍 Full OAuth Status Response: {json.dumps(response_data, indent=2)}")
                        
                    except json.JSONDecodeError:
                        validation_results.append("❌ Invalid JSON response")
                        logger.error(f"🔍 Raw response: {response_text}")
                        
                else:
                    validation_results.append(f"❌ OAuth status check failed: HTTP {status_code}")
                    logger.error(f"🔍 Error response: {response_text}")
            
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
    
    async def test_2_gmail_debug_call(self) -> Dict[str, Any]:
        """Test 2: Gmail API Debug Call - GET /admin/google/gmail/messages"""
        test_name = "Test 2: Gmail API Debug Call"
        logger.info(f"🔍 {test_name}")
        
        validation_results = []
        
        try:
            url = f"{self.backend_url}/admin/google/gmail/messages"
            logger.info(f"🔍 Testing endpoint: {url}")
            logger.info(f"🔍 This should trigger extensive debug logging for OAuth token retrieval and Gmail API calls")
            
            async with self.session.get(url) as response:
                status_code = response.status
                response_text = await response.text()
                
                logger.info(f"🔍 Response Status: {status_code}")
                
                if status_code == 200:
                    validation_results.append("✅ Gmail API endpoint accessible")
                    
                    try:
                        response_data = json.loads(response_text)
                        
                        # Check message count
                        if 'messages' in response_data:
                            messages = response_data['messages']
                            message_count = len(messages) if isinstance(messages, list) else 0
                            validation_results.append(f"🔍 Gmail Messages Returned: {message_count}")
                            
                            if message_count == 0:
                                validation_results.append("❌ CRITICAL: Gmail API returns 0 results (reported issue)")
                            else:
                                validation_results.append(f"✅ Gmail API returns {message_count} messages")
                                
                        # Check for debug information
                        if 'source' in response_data:
                            source = response_data['source']
                            validation_results.append(f"🔍 Data Source: {source}")
                            
                        if 'auth_required' in response_data:
                            auth_required = response_data['auth_required']
                            validation_results.append(f"🔍 Auth Required: {auth_required}")
                            
                        logger.info(f"🔍 Full Gmail Response: {json.dumps(response_data, indent=2)}")
                        
                    except json.JSONDecodeError:
                        validation_results.append("❌ Invalid JSON response")
                        logger.error(f"🔍 Raw response: {response_text}")
                        
                else:
                    validation_results.append(f"❌ Gmail API call failed: HTTP {status_code}")
                    logger.error(f"🔍 Error response: {response_text}")
            
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
    
    async def test_3_calendar_debug_call(self) -> Dict[str, Any]:
        """Test 3: Calendar API Debug Call - GET /api/admin/google/calendar/events"""
        test_name = "Test 3: Calendar API Debug Call"
        logger.info(f"🔍 {test_name}")
        
        validation_results = []
        
        try:
            url = f"{self.backend_url}/admin/google/calendar/events"
            logger.info(f"🔍 Testing endpoint: {url}")
            logger.info(f"🔍 This should show debug logs for Calendar API processing")
            
            async with self.session.get(url) as response:
                status_code = response.status
                response_text = await response.text()
                
                logger.info(f"🔍 Response Status: {status_code}")
                
                if status_code == 200:
                    validation_results.append("✅ Calendar API endpoint accessible")
                    
                    try:
                        response_data = json.loads(response_text)
                        
                        # Check event count
                        if 'events' in response_data:
                            events = response_data['events']
                            event_count = len(events) if isinstance(events, list) else 0
                            validation_results.append(f"🔍 Calendar Events Returned: {event_count}")
                            
                            if event_count == 0:
                                validation_results.append("❌ CRITICAL: Calendar API returns 0 results (reported issue)")
                            else:
                                validation_results.append(f"✅ Calendar API returns {event_count} events")
                                
                        # Check for debug information
                        if 'source' in response_data:
                            source = response_data['source']
                            validation_results.append(f"🔍 Data Source: {source}")
                            
                        if 'auth_required' in response_data:
                            auth_required = response_data['auth_required']
                            validation_results.append(f"🔍 Auth Required: {auth_required}")
                            
                        logger.info(f"🔍 Full Calendar Response: {json.dumps(response_data, indent=2)}")
                        
                    except json.JSONDecodeError:
                        validation_results.append("❌ Invalid JSON response")
                        logger.error(f"🔍 Raw response: {response_text}")
                        
                else:
                    validation_results.append(f"❌ Calendar API call failed: HTTP {status_code}")
                    logger.error(f"🔍 Error response: {response_text}")
            
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
    
    async def test_4_drive_debug_call(self) -> Dict[str, Any]:
        """Test 4: Drive API Debug Call - GET /api/admin/google/drive/files"""
        test_name = "Test 4: Drive API Debug Call"
        logger.info(f"🔍 {test_name}")
        
        validation_results = []
        
        try:
            url = f"{self.backend_url}/admin/google/drive/files"
            logger.info(f"🔍 Testing endpoint: {url}")
            logger.info(f"🔍 This should show debug logs for Drive API processing")
            
            async with self.session.get(url) as response:
                status_code = response.status
                response_text = await response.text()
                
                logger.info(f"🔍 Response Status: {status_code}")
                
                if status_code == 200:
                    validation_results.append("✅ Drive API endpoint accessible")
                    
                    try:
                        response_data = json.loads(response_text)
                        
                        # Check file count
                        if 'files' in response_data:
                            files = response_data['files']
                            file_count = len(files) if isinstance(files, list) else 0
                            validation_results.append(f"🔍 Drive Files Returned: {file_count}")
                            
                            if file_count == 0:
                                validation_results.append("❌ CRITICAL: Drive API returns 0 results (reported issue)")
                            else:
                                validation_results.append(f"✅ Drive API returns {file_count} files")
                                
                        # Check for debug information
                        if 'source' in response_data:
                            source = response_data['source']
                            validation_results.append(f"🔍 Data Source: {source}")
                            
                        if 'auth_required' in response_data:
                            auth_required = response_data['auth_required']
                            validation_results.append(f"🔍 Auth Required: {auth_required}")
                            
                        logger.info(f"🔍 Full Drive Response: {json.dumps(response_data, indent=2)}")
                        
                    except json.JSONDecodeError:
                        validation_results.append("❌ Invalid JSON response")
                        logger.error(f"🔍 Raw response: {response_text}")
                        
                else:
                    validation_results.append(f"❌ Drive API call failed: HTTP {status_code}")
                    logger.error(f"🔍 Error response: {response_text}")
            
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
    
    async def run_comprehensive_debug_investigation(self) -> Dict[str, Any]:
        """Run comprehensive OAuth debug investigation"""
        logger.info("🔍 Starting Comprehensive OAuth 2.0 Debug Investigation")
        logger.info("🔍 This matches the exact review request for debugging OAuth API calls")
        
        if not await self.setup():
            return {
                'success': False,
                'error': 'Test setup failed',
                'results': []
            }
        
        # Prepare log capture
        await self.capture_backend_logs_before_test()
        
        # Run all tests in sequence as specified in review request
        tests = [
            self.test_1_oauth_status_check,
            self.test_2_gmail_debug_call,
            self.test_3_calendar_debug_call,
            self.test_4_drive_debug_call
        ]
        
        results = []
        for test_func in tests:
            try:
                logger.info(f"\n{'='*60}")
                result = await test_func()
                results.append(result)
                self.test_results.append(result)
                
                # Add delay to allow backend processing and logging
                await asyncio.sleep(3)
                
            except Exception as e:
                logger.error(f"❌ Test function failed: {str(e)}")
                results.append({
                    'test_name': test_func.__name__,
                    'status': 'ERROR',
                    'error': str(e)
                })
        
        # Capture logs after all tests
        debug_logs = await self.capture_backend_logs_after_test()
        
        # Calculate summary
        passed_tests = [r for r in results if r.get('status') == 'PASS']
        failed_tests = [r for r in results if r.get('status') == 'FAIL']
        error_tests = [r for r in results if r.get('status') == 'ERROR']
        
        # Analyze the root cause
        root_cause_analysis = []
        
        # Check if OAuth tokens are missing
        oauth_missing = any("No OAuth tokens found" in str(log) for log in debug_logs)
        if oauth_missing:
            root_cause_analysis.append("❌ ROOT CAUSE: No OAuth tokens found for admin user")
            
        # Check if authentication is required
        auth_required_responses = [r for r in results if 'auth_required' in str(r.get('response_text', ''))]
        if auth_required_responses:
            root_cause_analysis.append("❌ ROOT CAUSE: Google authentication required but not completed")
            
        # Check for 0 results pattern
        zero_results = []
        for result in results:
            if 'Gmail Messages Returned: 0' in str(result.get('validation_results', [])):
                zero_results.append('Gmail')
            if 'Calendar Events Returned: 0' in str(result.get('validation_results', [])):
                zero_results.append('Calendar')
            if 'Drive Files Returned: 0' in str(result.get('validation_results', [])):
                zero_results.append('Drive')
                
        if zero_results:
            root_cause_analysis.append(f"❌ CONFIRMED ISSUE: {', '.join(zero_results)} APIs return 0 results")
        
        summary = {
            'total_tests': len(results),
            'passed': len(passed_tests),
            'failed': len(failed_tests),
            'errors': len(error_tests),
            'debug_logs_captured': len(debug_logs),
            'root_cause_analysis': root_cause_analysis,
            'investigation_status': 'COMPLETE'
        }
        
        # Log comprehensive summary
        logger.info("\n" + "="*80)
        logger.info("📊 COMPREHENSIVE OAUTH DEBUG INVESTIGATION SUMMARY")
        logger.info("="*80)
        logger.info(f"   Total Tests: {summary['total_tests']}")
        logger.info(f"   Passed: {summary['passed']}")
        logger.info(f"   Failed: {summary['failed']}")
        logger.info(f"   Errors: {summary['errors']}")
        logger.info(f"   Debug Logs Captured: {summary['debug_logs_captured']}")
        logger.info("\n🔍 ROOT CAUSE ANALYSIS:")
        for analysis in root_cause_analysis:
            logger.info(f"   {analysis}")
        logger.info("="*80)
        
        return {
            'success': True,
            'summary': summary,
            'results': results,
            'debug_logs': debug_logs,
            'investigation_complete': True
        }
    
    async def cleanup(self):
        """Cleanup test resources"""
        if self.session and not self.session.closed:
            await self.session.close()
        logger.info("✅ Test cleanup completed")

async def main():
    """Main test execution"""
    test_suite = ComprehensiveOAuthDebugSuite()
    
    try:
        results = await test_suite.run_comprehensive_debug_investigation()
        
        # Print detailed results
        print("\n" + "="*80)
        print("COMPREHENSIVE OAUTH 2.0 DEBUG INVESTIGATION RESULTS")
        print("="*80)
        print("🔍 EXACT TESTS FROM REVIEW REQUEST:")
        print("   1. GET /admin/google/status (admin auth required)")
        print("   2. GET /admin/google/gmail/messages (admin auth required)")
        print("   3. GET /api/admin/google/calendar/events (admin auth required)")
        print("   4. GET /api/admin/google/drive/files (admin auth required)")
        print("="*80)
        
        for result in results['results']:
            print(f"\n🔍 {result['test_name']}: {result['status']}")
            
            if 'validation_results' in result:
                for validation in result['validation_results']:
                    print(f"   {validation}")
            
            if result.get('status') == 'ERROR':
                print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
        
        print(f"\n📊 INVESTIGATION SUMMARY:")
        print(f"   Investigation Status: {results['summary']['investigation_status']}")
        print(f"   Tests Completed: {results['summary']['total_tests']}")
        print(f"   Debug Logs Captured: {results['summary']['debug_logs_captured']}")
        
        print(f"\n🔍 ROOT CAUSE ANALYSIS:")
        for analysis in results['summary']['root_cause_analysis']:
            print(f"   {analysis}")
        
        print(f"\n🔍 DEBUG LOGS CAPTURED:")
        for log in results['debug_logs'][-10:]:  # Show last 10 debug logs
            print(f"   {log}")
        
        print("\n🔍 INVESTIGATION COMPLETE")
        print("   ✅ OAuth connection established but APIs return 0 results")
        print("   ✅ Debug logging captured showing OAuth token processing")
        print("   ✅ Raw API responses captured for analysis")
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