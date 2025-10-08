#!/usr/bin/env python3
"""
URGENT DEBUG: Frontend Data Visibility Testing
Testing specific endpoints that frontend should be calling but user reports no data visible.

Focus Areas:
1. Admin Authentication 
2. Investment Admin Overview (dashboard totals)
3. Ready Clients (investment dropdown)
4. Client Investments (Alejandro's data)
5. MT5 Accounts (Alejandro's accounts)
6. Google Connection Status

Context: User reports no investments, MT5 accounts, or Google email functionality visible in frontend.
Need to verify these specific endpoints are returning correct data for frontend consumption.
"""

import requests
import json
import sys
from datetime import datetime

# Use the correct backend URL from frontend/.env
BACKEND_URL = "https://trading-platform-76.preview.emergentagent.com/api"

class FrontendDataVisibilityTester:
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
    
    def test_admin_authentication(self):
        """Test admin login with credentials admin/password123"""
        print("\n🔐 TESTING ADMIN AUTHENTICATION")
        
        try:
            login_data = {
                "username": "admin",
                "password": "password123", 
                "user_type": "admin"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("token"):
                    self.admin_token = data["token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    
                    self.log_test(
                        "Admin Authentication",
                        True,
                        f"Successfully authenticated as {data.get('name', 'admin')} with JWT token",
                        {"user_id": data.get("id"), "username": data.get("username"), "type": data.get("type")}
                    )
                    return True
                else:
                    self.log_test("Admin Authentication", False, "No token in response", data)
                    return False
            else:
                self.log_test("Admin Authentication", False, f"HTTP {response.status_code}", response.json() if response.content else None)
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_investment_admin_overview(self):
        """Test investment admin overview for dashboard totals"""
        print("\n📊 TESTING INVESTMENT ADMIN OVERVIEW")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/investments/admin/overview")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if data structure is correct for frontend
                required_fields = ["total_aum", "total_investments", "total_clients"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test(
                        "Investment Admin Overview",
                        False,
                        f"Missing required fields: {missing_fields}",
                        data
                    )
                else:
                    self.log_test(
                        "Investment Admin Overview", 
                        True,
                        f"AUM: {data.get('total_aum', 'N/A')}, Investments: {data.get('total_investments', 'N/A')}, Clients: {data.get('total_clients', 'N/A')}",
                        data
                    )
                    
                return response.status_code == 200
            else:
                self.log_test("Investment Admin Overview", False, f"HTTP {response.status_code}", response.json() if response.content else None)
                return False
                
        except Exception as e:
            self.log_test("Investment Admin Overview", False, f"Exception: {str(e)}")
            return False
    
    def test_ready_clients(self):
        """Test ready clients endpoint for investment dropdown"""
        print("\n👥 TESTING READY CLIENTS (Investment Dropdown)")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/clients/ready-for-investment")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if Alejandro is in the list
                ready_clients = data.get("ready_clients", [])
                alejandro_found = any(
                    client.get("client_id") == "client_alejandro" or 
                    "Alejandro" in client.get("name", "") 
                    for client in ready_clients
                )
                
                if alejandro_found:
                    alejandro_client = next(
                        client for client in ready_clients 
                        if client.get("client_id") == "client_alejandro" or "Alejandro" in client.get("name", "")
                    )
                    self.log_test(
                        "Ready Clients - Alejandro Found",
                        True,
                        f"Alejandro found: {alejandro_client.get('name')} ({alejandro_client.get('client_id')})",
                        alejandro_client
                    )
                else:
                    self.log_test(
                        "Ready Clients - Alejandro Missing",
                        False,
                        f"Alejandro not found in {len(ready_clients)} ready clients",
                        data
                    )
                
                return response.status_code == 200
            else:
                self.log_test("Ready Clients", False, f"HTTP {response.status_code}", response.json() if response.content else None)
                return False
                
        except Exception as e:
            self.log_test("Ready Clients", False, f"Exception: {str(e)}")
            return False
    
    def test_client_investments(self):
        """Test client investments for Alejandro"""
        print("\n💰 TESTING CLIENT INVESTMENTS (Alejandro)")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/investments/client/client_alejandro")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for expected investments (BALANCE + CORE)
                investments = data.get("investments", [])
                
                balance_investment = next((inv for inv in investments if inv.get("fund_code") == "BALANCE"), None)
                core_investment = next((inv for inv in investments if inv.get("fund_code") == "CORE"), None)
                
                if balance_investment and core_investment:
                    total_value = sum(inv.get("current_value", 0) for inv in investments)
                    self.log_test(
                        "Client Investments - Complete",
                        True,
                        f"Found {len(investments)} investments, Total: ${total_value:,.2f}",
                        {"investment_count": len(investments), "funds": [inv.get("fund_code") for inv in investments]}
                    )
                elif investments:
                    self.log_test(
                        "Client Investments - Partial",
                        False,
                        f"Found {len(investments)} investments but missing expected BALANCE/CORE funds",
                        data
                    )
                else:
                    self.log_test(
                        "Client Investments - Empty",
                        False,
                        "No investments found for client_alejandro",
                        data
                    )
                
                return response.status_code == 200
            else:
                self.log_test("Client Investments", False, f"HTTP {response.status_code}", response.json() if response.content else None)
                return False
                
        except Exception as e:
            self.log_test("Client Investments", False, f"Exception: {str(e)}")
            return False
    
    def test_mt5_accounts(self):
        """Test MT5 accounts for Alejandro"""
        print("\n🏦 TESTING MT5 ACCOUNTS (Alejandro)")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/accounts/client_alejandro")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for expected 4 MEXAtlantic accounts
                accounts = data.get("accounts", [])
                
                if accounts:
                    mexatlantic_accounts = [acc for acc in accounts if "MEXAtlantic" in acc.get("broker_name", "")]
                    
                    if len(mexatlantic_accounts) >= 4:
                        self.log_test(
                            "MT5 Accounts - Complete",
                            True,
                            f"Found {len(mexatlantic_accounts)} MEXAtlantic accounts out of {len(accounts)} total",
                            {"total_accounts": len(accounts), "mexatlantic_count": len(mexatlantic_accounts)}
                        )
                    else:
                        self.log_test(
                            "MT5 Accounts - Incomplete",
                            False,
                            f"Expected 4 MEXAtlantic accounts, found {len(mexatlantic_accounts)}",
                            data
                        )
                else:
                    self.log_test(
                        "MT5 Accounts - Empty",
                        False,
                        "No MT5 accounts found for client_alejandro",
                        data
                    )
                
                return response.status_code == 200
            else:
                self.log_test("MT5 Accounts", False, f"HTTP {response.status_code}", response.json() if response.content else None)
                return False
                
        except Exception as e:
            self.log_test("MT5 Accounts", False, f"Exception: {str(e)}")
            return False
    
    def test_google_connection(self):
        """Test Google connection status"""
        print("\n🔗 TESTING GOOGLE CONNECTION STATUS")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/google/connection/test-all")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check overall status and individual services
                overall_status = data.get("overall_status", "unknown")
                services = data.get("services", {})
                
                connected_services = sum(1 for service, status in services.items() if status.get("status") == "connected")
                total_services = len(services)
                
                success_rate = (connected_services / total_services * 100) if total_services > 0 else 0
                
                if success_rate == 0:
                    self.log_test(
                        "Google Connection - No Services",
                        False,
                        f"0% success rate - no services connected ({connected_services}/{total_services})",
                        data
                    )
                elif success_rate < 50:
                    self.log_test(
                        "Google Connection - Poor",
                        False,
                        f"{success_rate:.1f}% success rate - most services failing ({connected_services}/{total_services})",
                        data
                    )
                else:
                    self.log_test(
                        "Google Connection - Good",
                        True,
                        f"{success_rate:.1f}% success rate - {connected_services}/{total_services} services connected",
                        {"overall_status": overall_status, "connected_services": connected_services}
                    )
                
                return response.status_code == 200
            else:
                self.log_test("Google Connection", False, f"HTTP {response.status_code}", response.json() if response.content else None)
                return False
                
        except Exception as e:
            self.log_test("Google Connection", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all frontend data visibility tests"""
        print("🚨 URGENT DEBUG: Frontend Data Visibility Testing")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Test sequence matching the review request
        tests = [
            ("Admin Authentication", self.test_admin_authentication),
            ("Investment Admin Overview", self.test_investment_admin_overview),
            ("Ready Clients", self.test_ready_clients),
            ("Client Investments", self.test_client_investments),
            ("MT5 Accounts", self.test_mt5_accounts),
            ("Google Connection", self.test_google_connection)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_name}: {str(e)}")
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 FRONTEND DATA VISIBILITY TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        # Critical findings
        critical_issues = []
        for result in self.test_results:
            if not result["success"] and any(keyword in result["test"].lower() for keyword in ["authentication", "investment", "ready", "mt5"]):
                critical_issues.append(result["test"])
        
        if critical_issues:
            print(f"\n🚨 CRITICAL ISSUES PREVENTING FRONTEND DATA DISPLAY:")
            for issue in critical_issues:
                print(f"   - {issue}")
        
        # Recommendations
        print(f"\n📋 RECOMMENDATIONS:")
        if not self.admin_token:
            print("   - Fix admin authentication first - all other tests depend on it")
        elif success_rate < 50:
            print("   - Multiple critical endpoints failing - backend infrastructure issue")
        elif success_rate < 100:
            print("   - Some endpoints working but missing data - check database setup")
        else:
            print("   - All endpoints working - issue may be in frontend integration")
        
        return success_rate >= 80  # 80% success rate threshold

if __name__ == "__main__":
    tester = FrontendDataVisibilityTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)