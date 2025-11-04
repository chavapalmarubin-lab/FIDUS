#!/usr/bin/env python3
"""
Quick Actions API Endpoints Testing (Phase 6)
Testing newly implemented Quick Actions API endpoints for admin tools.

Test Coverage:
1. Deployment Actions (restart-backend, restart-frontend, restart-all)
2. Data Management Actions (sync-mt5, refresh-performance, backup-database)  
3. System Tools Actions (test-integrations, generate-report)
4. Action History (recent, logs)

All endpoints require admin authentication.
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend configuration
BACKEND_URL = "https://referral-tracker-8.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials for testing
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "password123",
    "user_type": "admin"
}

class QuickActionsAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, status_code, response_data, error_msg=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "status_code": status_code,
            "response": response_data,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name} - Status: {status_code}")
        if error_msg:
            print(f"   Error: {error_msg}")
        if response_data and isinstance(response_data, dict):
            if 'message' in response_data:
                print(f"   Message: {response_data['message']}")
            if 'success' in response_data:
                print(f"   Success: {response_data['success']}")
        print()

    def authenticate_admin(self):
        """Authenticate as admin and get JWT token"""
        print("🔐 Authenticating as admin...")
        
        try:
            response = self.session.post(
                f"{API_BASE}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data:
                    self.admin_token = data['token']
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}'
                    })
                    print(f"✅ Admin authentication successful")
                    print(f"   User: {data.get('name', 'Unknown')}")
                    print(f"   Email: {data.get('email', 'Unknown')}")
                    return True
                else:
                    print(f"❌ No token in response: {data}")
                    return False
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False

    def test_deployment_actions(self):
        """Test deployment action endpoints"""
        print("🚀 Testing Deployment Actions...")
        
        deployment_endpoints = [
            ("restart-backend", "Restart Backend Service"),
            ("restart-frontend", "Restart Frontend Service"), 
            ("restart-all", "Restart All Services")
        ]
        
        for endpoint, description in deployment_endpoints:
            try:
                response = self.session.post(
                    f"{API_BASE}/actions/{endpoint}",
                    timeout=30  # Longer timeout for restart operations
                )
                
                success = response.status_code == 200
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"raw": response.text}
                
                self.log_result(
                    f"POST /api/actions/{endpoint}",
                    success,
                    response.status_code,
                    data,
                    None if success else f"Failed to {description.lower()}"
                )
                
            except Exception as e:
                self.log_result(
                    f"POST /api/actions/{endpoint}",
                    False,
                    0,
                    {},
                    f"Request error: {str(e)}"
                )

    def test_data_management_actions(self):
        """Test data management action endpoints"""
        print("📊 Testing Data Management Actions...")
        
        data_endpoints = [
            ("sync-mt5", "Sync MT5 Data"),
            ("refresh-performance", "Refresh Fund Performance"),
            ("backup-database", "Backup Database")
        ]
        
        for endpoint, description in data_endpoints:
            try:
                response = self.session.post(
                    f"{API_BASE}/actions/{endpoint}",
                    timeout=60  # Longer timeout for data operations
                )
                
                success = response.status_code == 200
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"raw": response.text}
                
                self.log_result(
                    f"POST /api/actions/{endpoint}",
                    success,
                    response.status_code,
                    data,
                    None if success else f"Failed to {description.lower()}"
                )
                
            except Exception as e:
                self.log_result(
                    f"POST /api/actions/{endpoint}",
                    False,
                    0,
                    {},
                    f"Request error: {str(e)}"
                )

    def test_system_tools_actions(self):
        """Test system tools action endpoints"""
        print("🔧 Testing System Tools Actions...")
        
        tools_endpoints = [
            ("test-integrations", "Test All Integrations"),
            ("generate-report", "Generate System Report")
        ]
        
        for endpoint, description in tools_endpoints:
            try:
                response = self.session.post(
                    f"{API_BASE}/actions/{endpoint}",
                    timeout=45  # Longer timeout for system operations
                )
                
                success = response.status_code == 200
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"raw": response.text}
                
                self.log_result(
                    f"POST /api/actions/{endpoint}",
                    success,
                    response.status_code,
                    data,
                    None if success else f"Failed to {description.lower()}"
                )
                
            except Exception as e:
                self.log_result(
                    f"POST /api/actions/{endpoint}",
                    False,
                    0,
                    {},
                    f"Request error: {str(e)}"
                )

    def test_action_history(self):
        """Test action history endpoints"""
        print("📋 Testing Action History...")
        
        # Test recent actions endpoint
        try:
            response = self.session.get(
                f"{API_BASE}/actions/recent",
                params={"limit": 10},
                timeout=15
            )
            
            success = response.status_code == 200
            data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"raw": response.text}
            
            # Verify response structure for recent actions
            if success and isinstance(data, dict):
                if 'actions' in data:
                    print(f"   Found {len(data['actions'])} recent actions")
                    if data['actions']:
                        sample_action = data['actions'][0]
                        print(f"   Sample action: {sample_action.get('action_type', 'Unknown')} by {sample_action.get('performed_by', 'Unknown')}")
            
            self.log_result(
                "GET /api/actions/recent",
                success,
                response.status_code,
                data,
                None if success else "Failed to get recent actions"
            )
            
        except Exception as e:
            self.log_result(
                "GET /api/actions/recent",
                False,
                0,
                {},
                f"Request error: {str(e)}"
            )
        
        # Test action logs endpoint
        try:
            response = self.session.get(
                f"{API_BASE}/actions/logs",
                params={"limit": 20},
                timeout=15
            )
            
            success = response.status_code == 200
            data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"raw": response.text}
            
            # Verify response structure for logs
            if success and isinstance(data, dict):
                if 'logs' in data:
                    print(f"   Found {len(data['logs'])} log entries")
                elif 'success' in data:
                    print(f"   Logs operation success: {data['success']}")
            
            self.log_result(
                "GET /api/actions/logs",
                success,
                response.status_code,
                data,
                None if success else "Failed to get action logs"
            )
            
        except Exception as e:
            self.log_result(
                "GET /api/actions/logs",
                False,
                0,
                {},
                f"Request error: {str(e)}"
            )

    def verify_logging_functionality(self):
        """Verify that actions are being logged to MongoDB"""
        print("🗄️ Verifying Action Logging...")
        
        # Get recent actions to verify logging is working
        try:
            response = self.session.get(
                f"{API_BASE}/actions/recent",
                params={"limit": 5},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'actions' in data:
                    actions = data['actions']
                    if actions:
                        print(f"✅ Action logging verified - {len(actions)} actions found")
                        
                        # Check for required fields in logged actions
                        sample_action = actions[0]
                        required_fields = ['action_type', 'performed_by', 'timestamp', 'success']
                        missing_fields = [field for field in required_fields if field not in sample_action]
                        
                        if not missing_fields:
                            print("✅ All required fields present in logged actions")
                        else:
                            print(f"⚠️ Missing fields in logged actions: {missing_fields}")
                        
                        # Check for timestamps
                        if 'timestamp' in sample_action:
                            print(f"   Latest action timestamp: {sample_action['timestamp']}")
                        
                        return True
                    else:
                        print("⚠️ No actions found in recent actions - logging may not be working")
                        return False
                else:
                    print("⚠️ Unexpected response format for recent actions")
                    return False
            else:
                print(f"❌ Failed to verify logging: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error verifying logging: {str(e)}")
            return False

    def run_comprehensive_test(self):
        """Run all Quick Actions API tests"""
        print("=" * 80)
        print("🎯 QUICK ACTIONS API ENDPOINTS TESTING (PHASE 6)")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing Time: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        print()
        
        # Step 2: Test deployment actions
        self.test_deployment_actions()
        
        # Step 3: Test data management actions  
        self.test_data_management_actions()
        
        # Step 4: Test system tools actions
        self.test_system_tools_actions()
        
        # Step 5: Test action history
        self.test_action_history()
        
        # Step 6: Verify logging functionality
        self.verify_logging_functionality()
        
        # Generate summary
        self.generate_test_summary()
        
        return True

    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print()
        print("=" * 80)
        print("📊 QUICK ACTIONS API TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Group results by category
        categories = {
            "Deployment Actions": [],
            "Data Management Actions": [],
            "System Tools Actions": [],
            "Action History": []
        }
        
        for result in self.test_results:
            test_name = result['test']
            if 'restart' in test_name:
                categories["Deployment Actions"].append(result)
            elif any(x in test_name for x in ['sync-mt5', 'refresh-performance', 'backup-database']):
                categories["Data Management Actions"].append(result)
            elif any(x in test_name for x in ['test-integrations', 'generate-report']):
                categories["System Tools Actions"].append(result)
            elif any(x in test_name for x in ['recent', 'logs']):
                categories["Action History"].append(result)
        
        # Print category summaries
        for category, results in categories.items():
            if results:
                passed = len([r for r in results if r['success']])
                total = len(results)
                print(f"{category}: {passed}/{total} passed")
                
                for result in results:
                    status = "✅" if result['success'] else "❌"
                    print(f"  {status} {result['test']} (HTTP {result['status_code']})")
        
        print()
        
        # Print failed tests details
        failed_results = [r for r in self.test_results if not r['success']]
        if failed_results:
            print("❌ FAILED TESTS DETAILS:")
            for result in failed_results:
                print(f"  • {result['test']}")
                print(f"    Status: {result['status_code']}")
                if result['error']:
                    print(f"    Error: {result['error']}")
                print()
        
        # Print success summary
        if success_rate >= 90:
            print("🎉 EXCELLENT: Quick Actions API is working excellently!")
        elif success_rate >= 70:
            print("✅ GOOD: Quick Actions API is mostly functional with minor issues")
        elif success_rate >= 50:
            print("⚠️ PARTIAL: Quick Actions API has significant issues that need attention")
        else:
            print("❌ CRITICAL: Quick Actions API has major failures requiring immediate fixes")
        
        print()
        print("=" * 80)

def main():
    """Main test execution"""
    tester = QuickActionsAPITester()
    
    try:
        success = tester.run_comprehensive_test()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)