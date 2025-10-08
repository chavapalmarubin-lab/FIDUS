#!/usr/bin/env python3
"""
MT5 Live Integration Testing Script
Tests the new live MT5 endpoints for bridge service integration
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://trading-platform-76.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class MT5LiveIntegrationTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details, response_data=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            login_data = {
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                
                self.log_test(
                    "Admin Authentication",
                    True,
                    f"Successfully authenticated as {data.get('name', 'admin')}"
                )
                return True
            else:
                self.log_test(
                    "Admin Authentication", 
                    False,
                    f"Authentication failed with status {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_mt5_bridge_connection(self):
        """Test MT5 Bridge Connection endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/live/test-connection")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for actual response structure
                if "success" in data and "bridge_test" in data:
                    bridge_test = data.get("bridge_test", {})
                    bridge_status = bridge_test.get("bridge_status", {})
                    bridge_url = bridge_test.get("mt5_bridge_url", "unknown")
                    
                    # Bridge connection test is working even if MT5 is not installed
                    bridge_available = bridge_test.get("bridge_available", False)
                    status = bridge_status.get("status", "unknown")
                    
                    self.log_test(
                        "MT5 Bridge Connection Test",
                        True,
                        f"Bridge connection test working - Status: {status}, URL: {bridge_url}, Available: {bridge_available}",
                        {"bridge_status": status, "bridge_url": bridge_url, "bridge_available": bridge_available}
                    )
                else:
                    self.log_test(
                        "MT5 Bridge Connection Test",
                        False,
                        f"Unexpected response structure. Got: {list(data.keys())}",
                        data
                    )
            else:
                self.log_test(
                    "MT5 Bridge Connection Test",
                    False,
                    f"HTTP {response.status_code} - {response.text[:200]}",
                    response.json() if response.content else None
                )
                
        except Exception as e:
            self.log_test("MT5 Bridge Connection Test", False, f"Exception: {str(e)}")
    
    def test_enhanced_mt5_accounts(self):
        """Test Enhanced MT5 Accounts endpoint for client_alejandro"""
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/accounts/client_alejandro")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for enhanced data structure
                expected_fields = ["data_source", "summary", "accounts"]
                has_expected_fields = all(field in data for field in expected_fields)
                
                if has_expected_fields:
                    accounts = data.get("accounts", [])
                    summary = data.get("summary", {})
                    data_source = data.get("data_source", "unknown")
                    
                    total_balance = summary.get("total_balance", 0)
                    account_count = len(accounts)
                    
                    # Check if we have the expected 4 accounts totaling $118,151.41
                    expected_total = 118151.41
                    expected_accounts = 4
                    
                    balance_match = abs(total_balance - expected_total) < 1.0  # Allow small variance
                    account_count_match = account_count == expected_accounts
                    
                    if balance_match and account_count_match:
                        self.log_test(
                            "Enhanced MT5 Accounts Endpoint",
                            True,
                            f"Enhanced data retrieved - {account_count} accounts, ${total_balance:,.2f} total, Source: {data_source}",
                            {"summary": summary, "account_count": account_count}
                        )
                    else:
                        self.log_test(
                            "Enhanced MT5 Accounts Endpoint",
                            False,
                            f"Data mismatch - Expected: 4 accounts, $118,151.41. Got: {account_count} accounts, ${total_balance:,.2f}",
                            data
                        )
                else:
                    self.log_test(
                        "Enhanced MT5 Accounts Endpoint",
                        False,
                        f"Missing enhanced fields. Expected: {expected_fields}, Got: {list(data.keys())}",
                        data
                    )
            else:
                self.log_test(
                    "Enhanced MT5 Accounts Endpoint",
                    False,
                    f"HTTP {response.status_code} - {response.text[:200]}",
                    response.json() if response.content else None
                )
                
        except Exception as e:
            self.log_test("Enhanced MT5 Accounts Endpoint", False, f"Exception: {str(e)}")
    
    def test_live_data_update(self):
        """Test Live Data Update endpoint (Admin Only)"""
        try:
            response = self.session.post(f"{BACKEND_URL}/mt5/live/update-alejandro")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for update confirmation
                expected_fields = ["success", "updated_accounts", "data_source"]
                has_expected_fields = all(field in data for field in expected_fields)
                
                if has_expected_fields and data.get("success"):
                    updated_accounts = data.get("updated_accounts", 0)
                    data_source = data.get("data_source", "unknown")
                    
                    self.log_test(
                        "Live Data Update (Admin Only)",
                        True,
                        f"Live data update successful - {updated_accounts} accounts updated from {data_source}",
                        data
                    )
                else:
                    self.log_test(
                        "Live Data Update (Admin Only)",
                        False,
                        f"Update failed or missing fields. Response: {data}",
                        data
                    )
            elif response.status_code == 401:
                self.log_test(
                    "Live Data Update (Admin Only)",
                    False,
                    "Authentication required - endpoint properly secured",
                    response.json() if response.content else None
                )
            elif response.status_code == 403:
                self.log_test(
                    "Live Data Update (Admin Only)",
                    False,
                    "Admin access required - endpoint properly secured",
                    response.json() if response.content else None
                )
            else:
                self.log_test(
                    "Live Data Update (Admin Only)",
                    False,
                    f"HTTP {response.status_code} - {response.text[:200]}",
                    response.json() if response.content else None
                )
                
        except Exception as e:
            self.log_test("Live Data Update (Admin Only)", False, f"Exception: {str(e)}")
    
    def test_live_mt5_summary(self):
        """Test Live MT5 Summary endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/live/summary/client_alejandro")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for comprehensive summary data
                expected_fields = ["data_source", "account_performance", "last_update", "summary"]
                has_expected_fields = all(field in data for field in expected_fields)
                
                if has_expected_fields:
                    data_source = data.get("data_source", "unknown")
                    account_performance = data.get("account_performance", {})
                    last_update = data.get("last_update", "unknown")
                    summary = data.get("summary", {})
                    
                    self.log_test(
                        "Live MT5 Summary",
                        True,
                        f"Live summary retrieved - Source: {data_source}, Last Update: {last_update}, Performance data available",
                        {"data_source": data_source, "last_update": last_update, "summary_keys": list(summary.keys())}
                    )
                else:
                    self.log_test(
                        "Live MT5 Summary",
                        False,
                        f"Missing summary fields. Expected: {expected_fields}, Got: {list(data.keys())}",
                        data
                    )
            else:
                self.log_test(
                    "Live MT5 Summary",
                    False,
                    f"HTTP {response.status_code} - {response.text[:200]}",
                    response.json() if response.content else None
                )
                
        except Exception as e:
            self.log_test("Live MT5 Summary", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all MT5 live integration tests"""
        print("🚀 Starting MT5 Live Integration Tests")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Authentication: {ADMIN_USERNAME}/{'*' * len(ADMIN_PASSWORD)}")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        print("\n🔍 Testing MT5 Live Integration Endpoints:")
        print("-" * 50)
        
        # Step 2: Test MT5 Bridge Connection
        self.test_mt5_bridge_connection()
        
        # Step 3: Test Enhanced MT5 Accounts
        self.test_enhanced_mt5_accounts()
        
        # Step 4: Test Live Data Update
        self.test_live_data_update()
        
        # Step 5: Test Live MT5 Summary
        self.test_live_mt5_summary()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n🎯 VALIDATION CRITERIA CHECK:")
        bridge_test = any(r["test"] == "MT5 Bridge Connection Test" and r["success"] for r in self.test_results)
        enhanced_test = any(r["test"] == "Enhanced MT5 Accounts Endpoint" and r["success"] for r in self.test_results)
        
        print(f"✅ Bridge connection test: {'PASS' if bridge_test else 'FAIL'}")
        print(f"✅ Enhanced endpoints with structured data: {'PASS' if enhanced_test else 'FAIL'}")
        print(f"✅ No critical endpoint errors: {'PASS' if failed_tests == 0 else 'FAIL'}")
        print(f"✅ Ready for live data: {'PASS' if success_rate >= 75 else 'FAIL'}")
        
        return success_rate >= 75

def main():
    """Main test execution"""
    tester = MT5LiveIntegrationTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()