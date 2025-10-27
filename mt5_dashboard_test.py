#!/usr/bin/env python3
"""
MT5 DASHBOARD SYSTEM TESTING
Testing the newly implemented MT5 dashboard API endpoints and live data integration.

Focus Areas:
1. MT5 Dashboard Overview (NEW ENDPOINT)
2. Enhanced MT5 Accounts Endpoint  
3. Multi-Account Integration Endpoints
4. Data validation for $118,151.41 total allocation
5. Live data integration and freshness indicators

Authentication: admin/password123
Backend: https://oauth-flow-debug.preview.emergentagent.com/api
"""

import requests
import json
import sys
from datetime import datetime

# Use the correct backend URL from frontend/.env
BACKEND_URL = "https://oauth-flow-debug.preview.emergentagent.com/api"

class MT5DashboardTester:
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
    
    def test_mt5_dashboard_overview(self):
        """Test NEW MT5 Dashboard Overview endpoint"""
        print("\n📊 TESTING MT5 DASHBOARD OVERVIEW (NEW ENDPOINT)")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/dashboard/overview")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for expected comprehensive dashboard structure
                required_fields = ["total_accounts", "total_allocated", "by_fund", "performance_metrics"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test(
                        "MT5 Dashboard Overview - Structure",
                        False,
                        f"Missing required fields: {missing_fields}",
                        data
                    )
                    return False
                
                # Validate expected totals
                total_accounts = data.get("total_accounts", 0)
                total_allocated = data.get("total_allocated", 0)
                
                # Check for expected values from review request
                accounts_correct = total_accounts == 4
                allocation_correct = abs(total_allocated - 118151.41) < 0.01  # Allow for floating point precision
                
                if accounts_correct and allocation_correct:
                    self.log_test(
                        "MT5 Dashboard Overview - Data Validation",
                        True,
                        f"Correct totals: {total_accounts} accounts, ${total_allocated:,.2f} allocated",
                        {
                            "total_accounts": total_accounts,
                            "total_allocated": total_allocated,
                            "by_fund": data.get("by_fund", {}),
                            "performance_metrics": data.get("performance_metrics", {})
                        }
                    )
                else:
                    self.log_test(
                        "MT5 Dashboard Overview - Data Validation",
                        False,
                        f"Incorrect totals: Expected 4 accounts/${118151.41:,.2f}, Got {total_accounts} accounts/${total_allocated:,.2f}",
                        data
                    )
                
                # Check fund breakdown (BALANCE + CORE analysis)
                by_fund = data.get("by_fund", {})
                if "BALANCE" in by_fund and "CORE" in by_fund:
                    balance_amount = by_fund["BALANCE"].get("amount", 0)
                    core_amount = by_fund["CORE"].get("amount", 0)
                    fund_total = balance_amount + core_amount
                    
                    if abs(fund_total - 118151.41) < 0.01:
                        self.log_test(
                            "MT5 Dashboard Overview - Fund Breakdown",
                            True,
                            f"BALANCE: ${balance_amount:,.2f}, CORE: ${core_amount:,.2f}, Total: ${fund_total:,.2f}",
                            by_fund
                        )
                    else:
                        self.log_test(
                            "MT5 Dashboard Overview - Fund Breakdown",
                            False,
                            f"Fund totals don't match: ${fund_total:,.2f} vs expected ${118151.41:,.2f}",
                            by_fund
                        )
                else:
                    self.log_test(
                        "MT5 Dashboard Overview - Fund Breakdown",
                        False,
                        "Missing BALANCE or CORE fund data in breakdown",
                        by_fund
                    )
                
                return response.status_code == 200
            else:
                self.log_test("MT5 Dashboard Overview", False, f"HTTP {response.status_code}", response.json() if response.content else None)
                return False
                
        except Exception as e:
            self.log_test("MT5 Dashboard Overview", False, f"Exception: {str(e)}")
            return False
    
    def test_enhanced_mt5_accounts(self):
        """Test Enhanced MT5 Accounts endpoint for client_alejandro"""
        print("\n🏦 TESTING ENHANCED MT5 ACCOUNTS ENDPOINT")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/accounts/client_alejandro")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for enhanced response structure with live data integration
                enhanced_fields = ["accounts", "fund_summaries", "data_freshness", "live_integration"]
                present_fields = [field for field in enhanced_fields if field in data]
                
                if len(present_fields) >= 2:  # At least accounts and one enhancement
                    self.log_test(
                        "Enhanced MT5 Accounts - Structure",
                        True,
                        f"Enhanced fields present: {present_fields}",
                        {"enhanced_fields": present_fields}
                    )
                else:
                    self.log_test(
                        "Enhanced MT5 Accounts - Structure",
                        False,
                        f"Missing enhanced fields. Present: {present_fields}, Expected: {enhanced_fields}",
                        data
                    )
                
                # Check accounts data
                accounts = data.get("accounts", [])
                if accounts:
                    # Look for margin data, positions count, trading history
                    enhanced_account_data = []
                    for account in accounts:
                        enhancements = []
                        if "margin_data" in account or "margin" in account:
                            enhancements.append("margin_data")
                        if "positions_count" in account or "positions" in account:
                            enhancements.append("positions")
                        if "recent_trading_history" in account or "trading_history" in account:
                            enhancements.append("trading_history")
                        
                        if enhancements:
                            enhanced_account_data.append({
                                "account": account.get("mt5_account_number", "unknown"),
                                "enhancements": enhancements
                            })
                    
                    if enhanced_account_data:
                        self.log_test(
                            "Enhanced MT5 Accounts - Live Data Integration",
                            True,
                            f"Found enhanced data in {len(enhanced_account_data)} accounts",
                            enhanced_account_data
                        )
                    else:
                        self.log_test(
                            "Enhanced MT5 Accounts - Live Data Integration",
                            False,
                            "No enhanced live data fields found in accounts",
                            {"sample_account": accounts[0] if accounts else None}
                        )
                else:
                    self.log_test(
                        "Enhanced MT5 Accounts - No Accounts",
                        False,
                        "No accounts found for client_alejandro",
                        data
                    )
                
                # Check data freshness indicators
                data_freshness = data.get("data_freshness")
                if data_freshness:
                    self.log_test(
                        "Enhanced MT5 Accounts - Data Freshness",
                        True,
                        f"Data freshness indicators present: {list(data_freshness.keys()) if isinstance(data_freshness, dict) else 'present'}",
                        data_freshness
                    )
                else:
                    self.log_test(
                        "Enhanced MT5 Accounts - Data Freshness",
                        False,
                        "No data freshness indicators found",
                        None
                    )
                
                return response.status_code == 200
            else:
                self.log_test("Enhanced MT5 Accounts", False, f"HTTP {response.status_code}", response.json() if response.content else None)
                return False
                
        except Exception as e:
            self.log_test("Enhanced MT5 Accounts", False, f"Exception: {str(e)}")
            return False
    
    def test_multi_account_test_init(self):
        """Test Multi-Account Integration Test Init endpoint"""
        print("\n🔧 TESTING MULTI-ACCOUNT TEST INIT")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/multi-account/test-init")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for MT5 initialization test results
                if "initialization_status" in data or "mt5_status" in data or "test_result" in data:
                    self.log_test(
                        "Multi-Account Test Init",
                        True,
                        f"MT5 initialization test completed successfully",
                        data
                    )
                else:
                    self.log_test(
                        "Multi-Account Test Init",
                        False,
                        "Response doesn't contain expected initialization status",
                        data
                    )
                
                return response.status_code == 200
            else:
                self.log_test("Multi-Account Test Init", False, f"HTTP {response.status_code}", response.json() if response.content else None)
                return False
                
        except Exception as e:
            self.log_test("Multi-Account Test Init", False, f"Exception: {str(e)}")
            return False
    
    def test_multi_account_summary(self):
        """Test Multi-Account Summary endpoint for client_alejandro"""
        print("\n📋 TESTING MULTI-ACCOUNT SUMMARY")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/multi-account/summary/client_alejandro")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for cached data structure
                if "cached_data" in data or "summary" in data or "accounts" in data:
                    # Look for expected summary fields
                    summary_fields = []
                    if "total_balance" in data or "total_equity" in data:
                        summary_fields.append("balance_data")
                    if "account_count" in data or len(data.get("accounts", [])) > 0:
                        summary_fields.append("account_data")
                    if "last_updated" in data or "cache_timestamp" in data:
                        summary_fields.append("cache_info")
                    
                    if summary_fields:
                        self.log_test(
                            "Multi-Account Summary",
                            True,
                            f"Cached summary data returned with fields: {summary_fields}",
                            {"summary_fields": summary_fields, "data_keys": list(data.keys())}
                        )
                    else:
                        self.log_test(
                            "Multi-Account Summary",
                            False,
                            "Response structure doesn't contain expected summary fields",
                            data
                        )
                else:
                    self.log_test(
                        "Multi-Account Summary",
                        False,
                        "Response doesn't contain expected cached data structure",
                        data
                    )
                
                return response.status_code == 200
            else:
                self.log_test("Multi-Account Summary", False, f"HTTP {response.status_code}", response.json() if response.content else None)
                return False
                
        except Exception as e:
            self.log_test("Multi-Account Summary", False, f"Exception: {str(e)}")
            return False
    
    def test_financial_totals_validation(self):
        """Validate that all financial totals equal $118,151.41"""
        print("\n💰 TESTING FINANCIAL TOTALS VALIDATION")
        
        try:
            # Test multiple endpoints to ensure consistency
            endpoints_to_check = [
                ("/mt5/dashboard/overview", "total_allocated"),
                ("/investments/admin/overview", "total_aum"),
                ("/investments/client/client_alejandro", "total_value")
            ]
            
            total_validations = []
            expected_total = 118151.41
            
            for endpoint, total_field in endpoints_to_check:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Extract total value based on endpoint structure
                        if endpoint == "/investments/client/client_alejandro":
                            # Calculate total from investments
                            investments = data.get("investments", [])
                            total_value = sum(inv.get("current_value", 0) for inv in investments)
                        else:
                            # Direct field access
                            total_value = data.get(total_field, 0)
                            if isinstance(total_value, str):
                                # Remove currency symbols and convert
                                total_value = float(total_value.replace("$", "").replace(",", ""))
                        
                        validation_result = {
                            "endpoint": endpoint,
                            "total_field": total_field,
                            "value": total_value,
                            "matches_expected": abs(total_value - expected_total) < 0.01
                        }
                        total_validations.append(validation_result)
                        
                except Exception as e:
                    total_validations.append({
                        "endpoint": endpoint,
                        "total_field": total_field,
                        "error": str(e),
                        "matches_expected": False
                    })
            
            # Analyze validation results
            matching_totals = [v for v in total_validations if v.get("matches_expected", False)]
            
            if len(matching_totals) >= 2:  # At least 2 endpoints match
                self.log_test(
                    "Financial Totals Validation",
                    True,
                    f"{len(matching_totals)}/{len(total_validations)} endpoints match expected total ${expected_total:,.2f}",
                    total_validations
                )
            else:
                self.log_test(
                    "Financial Totals Validation",
                    False,
                    f"Only {len(matching_totals)}/{len(total_validations)} endpoints match expected total ${expected_total:,.2f}",
                    total_validations
                )
            
            return len(matching_totals) >= 1  # At least one endpoint should match
            
        except Exception as e:
            self.log_test("Financial Totals Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_performance_metrics(self):
        """Test performance metrics calculation in dashboard"""
        print("\n📈 TESTING PERFORMANCE METRICS")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/dashboard/overview")
            
            if response.status_code == 200:
                data = response.json()
                
                performance_metrics = data.get("performance_metrics", {})
                
                if performance_metrics:
                    # Check for expected performance fields
                    expected_metrics = ["total_return", "monthly_return", "ytd_return", "risk_metrics"]
                    present_metrics = [metric for metric in expected_metrics if metric in performance_metrics]
                    
                    if present_metrics:
                        self.log_test(
                            "Performance Metrics",
                            True,
                            f"Performance metrics calculated: {present_metrics}",
                            performance_metrics
                        )
                    else:
                        self.log_test(
                            "Performance Metrics",
                            False,
                            f"No expected performance metrics found. Available: {list(performance_metrics.keys())}",
                            performance_metrics
                        )
                else:
                    self.log_test(
                        "Performance Metrics",
                        False,
                        "No performance metrics found in dashboard overview",
                        data
                    )
                
                return response.status_code == 200
            else:
                self.log_test("Performance Metrics", False, f"HTTP {response.status_code}", response.json() if response.content else None)
                return False
                
        except Exception as e:
            self.log_test("Performance Metrics", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all MT5 dashboard system tests"""
        print("🚀 MT5 DASHBOARD SYSTEM TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print(f"Expected Total Allocation: $118,151.41")
        print(f"Expected Total Accounts: 4")
        print("=" * 60)
        
        # Test sequence for MT5 dashboard validation
        tests = [
            ("Admin Authentication", self.test_admin_authentication),
            ("MT5 Dashboard Overview", self.test_mt5_dashboard_overview),
            ("Enhanced MT5 Accounts", self.test_enhanced_mt5_accounts),
            ("Multi-Account Test Init", self.test_multi_account_test_init),
            ("Multi-Account Summary", self.test_multi_account_summary),
            ("Financial Totals Validation", self.test_financial_totals_validation),
            ("Performance Metrics", self.test_performance_metrics)
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
        print("🎯 MT5 DASHBOARD SYSTEM TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        # Validation criteria analysis
        validation_results = {
            "dashboard_overview": any("MT5 Dashboard Overview" in r["test"] and r["success"] for r in self.test_results),
            "enhanced_accounts": any("Enhanced MT5 Accounts" in r["test"] and r["success"] for r in self.test_results),
            "financial_totals": any("Financial Totals" in r["test"] and r["success"] for r in self.test_results),
            "data_freshness": any("Data Freshness" in r["test"] and r["success"] for r in self.test_results),
            "fund_breakdown": any("Fund Breakdown" in r["test"] and r["success"] for r in self.test_results),
            "performance_metrics": any("Performance Metrics" in r["test"] and r["success"] for r in self.test_results)
        }
        
        print(f"\n✅ VALIDATION CRITERIA RESULTS:")
        for criteria, passed in validation_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status} {criteria.replace('_', ' ').title()}")
        
        # Critical findings
        critical_issues = []
        for result in self.test_results:
            if not result["success"] and any(keyword in result["test"].lower() for keyword in ["dashboard", "overview", "financial", "totals"]):
                critical_issues.append(result["test"])
        
        if critical_issues:
            print(f"\n🚨 CRITICAL ISSUES:")
            for issue in critical_issues:
                print(f"   - {issue}")
        
        # Final assessment
        print(f"\n📋 MT5 DASHBOARD SYSTEM ASSESSMENT:")
        if success_rate >= 85:
            print("   ✅ MT5 dashboard system is OPERATIONAL and ready for frontend integration")
        elif success_rate >= 70:
            print("   ⚠️  MT5 dashboard system is PARTIALLY FUNCTIONAL with minor issues")
        else:
            print("   ❌ MT5 dashboard system has CRITICAL ISSUES requiring immediate attention")
        
        return success_rate >= 70  # 70% success rate threshold for MT5 dashboard

if __name__ == "__main__":
    tester = MT5DashboardTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)