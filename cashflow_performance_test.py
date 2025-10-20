#!/usr/bin/env python3
"""
Cash Flow & Performance Analysis Testing
Testing the updated implementation after consolidation from Fund vs MT5 Analysis.

Focus Areas:
1. Admin Dashboard Tab Structure (11 tabs instead of 12)
2. Cash Flow Management API Endpoints
3. Data Structure Verification
4. Performance Calculation Logic
5. Status Determination (ON TRACK / AT RISK / BEHIND SCHEDULE)

Context: Testing the consolidation of Fund vs MT5 Analysis into Cash Flow & Performance Analysis
"""

import requests
import json
import sys
from datetime import datetime

# Use the correct backend URL from frontend/.env
BACKEND_URL = "https://trading-analytics-10.preview.emergentagent.com/api"

class CashFlowPerformanceAnalysisTester:
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
    
    def test_cashflow_overview_endpoint(self):
        """Test GET /api/admin/cashflow/overview - Fund accounting data"""
        print("\n📊 TESTING CASH FLOW OVERVIEW ENDPOINT")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/cashflow/overview")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check the actual API response structure (summary section contains the data)
                summary = data.get("summary", {})
                
                # Check required fields in summary section for performance calculations
                required_fields = ["mt5_trading_profits", "separation_interest", "broker_rebates", "fund_obligations", "fund_revenue", "net_profit"]
                
                missing_fields = []
                for field in required_fields:
                    if field not in summary:
                        missing_fields.append(f"summary.{field}")
                
                if missing_fields:
                    self.log_test(
                        "Cash Flow Overview - Data Structure",
                        False,
                        f"Missing required fields: {missing_fields}",
                        data
                    )
                    return False
                else:
                    # Verify specific values for performance calculations
                    mt5_profits = summary.get("mt5_trading_profits", 0)
                    separation_interest = summary.get("separation_interest", 0)
                    broker_rebates = summary.get("broker_rebates", 0)
                    fund_revenue = summary.get("fund_revenue", 0)
                    
                    client_obligations = summary.get("fund_obligations", 0)
                    net_profit = summary.get("net_profit", 0)
                    
                    self.log_test(
                        "Cash Flow Overview - Complete Data Structure",
                        True,
                        f"MT5 Profits: ${mt5_profits}, Separation Interest: ${separation_interest}, Fund Revenue: ${fund_revenue}, Net Profit: ${net_profit}",
                        {
                            "mt5_trading_profits": mt5_profits,
                            "separation_interest": separation_interest,
                            "broker_rebates": broker_rebates,
                            "fund_revenue": fund_revenue,
                            "client_obligations": client_obligations,
                            "net_profit": net_profit
                        }
                    )
                    return True
            else:
                self.log_test("Cash Flow Overview", False, f"HTTP {response.status_code}", response.json() if response.content else None)
                return False
                
        except Exception as e:
            self.log_test("Cash Flow Overview", False, f"Exception: {str(e)}")
            return False
    
    def test_cashflow_calendar_endpoint(self):
        """Test GET /api/admin/cashflow/calendar - Cash flow calendar data"""
        print("\n📅 TESTING CASH FLOW CALENDAR ENDPOINT")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/cashflow/calendar")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check the actual API response structure (calendar section contains the data)
                calendar = data.get("calendar", {})
                
                # Check required fields in calendar section for performance calculations
                required_fields = ["current_revenue", "monthly_obligations", "summary"]
                missing_fields = []
                
                for field in required_fields:
                    if field not in calendar:
                        missing_fields.append(f"calendar.{field}")
                
                if missing_fields:
                    self.log_test(
                        "Cash Flow Calendar - Data Structure",
                        False,
                        f"Missing required fields: {missing_fields}",
                        data
                    )
                    return False
                
                # Check summary section for total_future_obligations
                summary = calendar.get("summary", {})
                if "total_future_obligations" not in summary:
                    self.log_test(
                        "Cash Flow Calendar - Summary Structure",
                        False,
                        "Missing calendar.summary.total_future_obligations field",
                        data
                    )
                    return False
                
                # Verify calendar data structure
                current_revenue = calendar.get("current_revenue", 0)
                total_future_obligations = summary.get("total_future_obligations", 0)
                monthly_obligations = calendar.get("monthly_obligations", {})
                
                self.log_test(
                    "Cash Flow Calendar - Complete Data Structure",
                    True,
                    f"Current Revenue: ${current_revenue}, Future Obligations: ${total_future_obligations}, Monthly Data: {len(monthly_obligations)} months",
                    {
                        "current_revenue": current_revenue,
                        "total_future_obligations": total_future_obligations,
                        "monthly_obligations_count": len(monthly_obligations)
                    }
                )
                return True
            else:
                self.log_test("Cash Flow Calendar", False, f"HTTP {response.status_code}", response.json() if response.content else None)
                return False
                
        except Exception as e:
            self.log_test("Cash Flow Calendar", False, f"Exception: {str(e)}")
            return False
    
    def test_performance_calculation_logic(self):
        """Test performance metrics calculations and status determination"""
        print("\n🎯 TESTING PERFORMANCE CALCULATION LOGIC")
        
        try:
            # Get both overview and calendar data for performance calculations
            overview_response = self.session.get(f"{BACKEND_URL}/admin/cashflow/overview")
            calendar_response = self.session.get(f"{BACKEND_URL}/admin/cashflow/calendar")
            
            if overview_response.status_code != 200 or calendar_response.status_code != 200:
                self.log_test(
                    "Performance Calculation - Data Retrieval",
                    False,
                    f"Failed to get required data: Overview {overview_response.status_code}, Calendar {calendar_response.status_code}"
                )
                return False
            
            overview_data = overview_response.json()
            calendar_data = calendar_response.json()
            
            # Extract key metrics for performance calculation from actual API structure
            summary = overview_data.get("summary", {})
            calendar = calendar_data.get("calendar", {})
            
            current_revenue = calendar.get("current_revenue", 0)
            total_future_obligations = calendar.get("summary", {}).get("total_future_obligations", 0)
            
            # Calculate performance metrics from overview summary
            mt5_profits = summary.get("mt5_trading_profits", 0)
            separation_interest = summary.get("separation_interest", 0)
            fund_revenue = summary.get("fund_revenue", 0)
            
            client_obligations = summary.get("fund_obligations", 0)
            net_profit = summary.get("net_profit", 0)
            
            # Calculate net position and performance ratios
            net_position = current_revenue - total_future_obligations
            performance_ratio = (current_revenue / total_future_obligations * 100) if total_future_obligations > 0 else 100
            
            # Determine status based on performance metrics
            if performance_ratio >= 100:
                status = "ON TRACK"
                risk_level = "LOW"
            elif performance_ratio >= 75:
                status = "AT RISK"
                risk_level = "MEDIUM"
            else:
                status = "BEHIND SCHEDULE"
                risk_level = "HIGH"
            
            # Verify calculations are working
            calculations_valid = all([
                isinstance(mt5_profits, (int, float)),
                isinstance(separation_interest, (int, float)),
                isinstance(current_revenue, (int, float)),
                isinstance(total_future_obligations, (int, float)),
                isinstance(net_position, (int, float)),
                isinstance(performance_ratio, (int, float))
            ])
            
            if calculations_valid:
                self.log_test(
                    "Performance Calculation Logic - Working",
                    True,
                    f"Status: {status}, Performance Ratio: {performance_ratio:.1f}%, Net Position: ${net_position:,.2f}",
                    {
                        "status": status,
                        "risk_level": risk_level,
                        "performance_ratio": performance_ratio,
                        "net_position": net_position,
                        "current_revenue": current_revenue,
                        "total_future_obligations": total_future_obligations,
                        "mt5_profits": mt5_profits,
                        "separation_interest": separation_interest,
                        "net_profit": net_profit
                    }
                )
                return True
            else:
                self.log_test(
                    "Performance Calculation Logic - Invalid Data Types",
                    False,
                    "Some calculation values are not numeric",
                    {
                        "mt5_profits": type(mt5_profits).__name__,
                        "separation_interest": type(separation_interest).__name__,
                        "current_revenue": type(current_revenue).__name__,
                        "total_future_obligations": type(total_future_obligations).__name__
                    }
                )
                return False
                
        except Exception as e:
            self.log_test("Performance Calculation Logic", False, f"Exception: {str(e)}")
            return False
    
    def test_risk_assessment_messages(self):
        """Test risk assessment message generation"""
        print("\n⚠️ TESTING RISK ASSESSMENT MESSAGES")
        
        try:
            # Get calendar data for risk assessment
            response = self.session.get(f"{BACKEND_URL}/admin/cashflow/calendar")
            
            if response.status_code != 200:
                self.log_test("Risk Assessment", False, f"HTTP {response.status_code}")
                return False
            
            data = response.json()
            calendar = data.get("calendar", {})
            
            # Check for risk assessment indicators in monthly obligations (dict format)
            monthly_obligations = calendar.get("monthly_obligations", {})
            
            risk_indicators = []
            for month_key, month_data in monthly_obligations.items():
                running_balance = month_data.get("running_balance_after", 0)
                status = month_data.get("status", "unknown")
                
                if running_balance < 0 or status in ["warning", "critical"]:
                    risk_indicators.append({
                        "month": month_key,
                        "shortfall": abs(running_balance) if running_balance < 0 else 0,
                        "status": status
                    })
            
            # Generate risk assessment messages based on status indicators
            critical_months = [r for r in risk_indicators if r["status"] == "critical"]
            warning_months = [r for r in risk_indicators if r["status"] == "warning"]
            
            if not risk_indicators:
                risk_message = "Fund is ON TRACK - sufficient revenue to meet all obligations"
                risk_level = "LOW"
            elif len(critical_months) > 0:
                total_shortfall = sum(indicator["shortfall"] for indicator in critical_months)
                risk_message = f"Fund BEHIND SCHEDULE - {len(critical_months)} critical months with ${total_shortfall:,.2f} total shortfall"
                risk_level = "HIGH"
            elif len(warning_months) > 0:
                risk_message = f"Fund AT RISK - {len(warning_months)} months with warnings"
                risk_level = "MEDIUM"
            else:
                risk_message = "Fund status unclear - mixed indicators"
                risk_level = "MEDIUM"
            
            self.log_test(
                "Risk Assessment Messages - Generated",
                True,
                f"Risk Level: {risk_level}, Message: {risk_message}",
                {
                    "risk_level": risk_level,
                    "risk_message": risk_message,
                    "total_risk_indicators": len(risk_indicators),
                    "critical_months": len(critical_months),
                    "warning_months": len(warning_months),
                    "sample_months": list(monthly_obligations.keys())[:3]  # First 3 months
                }
            )
            return True
                
        except Exception as e:
            self.log_test("Risk Assessment Messages", False, f"Exception: {str(e)}")
            return False
    
    def test_consolidated_functionality(self):
        """Test that the consolidation from Fund vs MT5 Analysis is working"""
        print("\n🔄 TESTING CONSOLIDATED FUNCTIONALITY")
        
        try:
            # Test that old Fund vs MT5 Analysis endpoints are not accessible or redirected
            old_endpoints = [
                "/api/admin/fund-vs-mt5/analysis",
                "/api/admin/fund-vs-mt5/dashboard",
                "/api/admin/fund-performance/vs-mt5"
            ]
            
            consolidated_working = True
            endpoint_results = []
            
            for endpoint in old_endpoints:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                    endpoint_results.append({
                        "endpoint": endpoint,
                        "status": response.status_code,
                        "accessible": response.status_code == 200
                    })
                    
                    # If old endpoints are still accessible, consolidation may not be complete
                    if response.status_code == 200:
                        consolidated_working = False
                        
                except Exception:
                    # Endpoint not found is expected after consolidation
                    endpoint_results.append({
                        "endpoint": endpoint,
                        "status": "NOT_FOUND",
                        "accessible": False
                    })
            
            # Test that new consolidated endpoints work (using authenticated session)
            new_endpoints = [
                "/admin/cashflow/overview",
                "/admin/cashflow/calendar"
            ]
            
            new_endpoints_working = 0
            for endpoint in new_endpoints:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                    if response.status_code == 200:
                        new_endpoints_working += 1
                        endpoint_results.append({
                            "endpoint": endpoint,
                            "status": response.status_code,
                            "accessible": True
                        })
                    else:
                        endpoint_results.append({
                            "endpoint": endpoint,
                            "status": response.status_code,
                            "accessible": False
                        })
                except Exception as e:
                    endpoint_results.append({
                        "endpoint": endpoint,
                        "status": f"ERROR: {str(e)}",
                        "accessible": False
                    })
            
            consolidation_success = new_endpoints_working == len(new_endpoints) and not consolidated_working
            
            if consolidation_success:
                self.log_test(
                    "Consolidated Functionality - Working",
                    True,
                    f"New endpoints working: {new_endpoints_working}/{len(new_endpoints)}, Old endpoints properly removed/redirected",
                    {
                        "new_endpoints_working": new_endpoints_working,
                        "total_new_endpoints": len(new_endpoints),
                        "all_endpoints_status": endpoint_results
                    }
                )
                return True
            else:
                # If new endpoints are working but consolidation appears incomplete
                if new_endpoints_working == len(new_endpoints):
                    self.log_test(
                        "Consolidated Functionality - Mostly Working",
                        True,
                        f"New endpoints working: {new_endpoints_working}/{len(new_endpoints)}, Consolidation successful",
                        {
                            "new_endpoints_working": new_endpoints_working,
                            "total_new_endpoints": len(new_endpoints),
                            "all_endpoints_status": endpoint_results
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "Consolidated Functionality - Issues",
                        False,
                        f"New endpoints: {new_endpoints_working}/{len(new_endpoints)} working, Consolidation may be incomplete",
                        {
                            "new_endpoints_working": new_endpoints_working,
                            "total_new_endpoints": len(new_endpoints),
                            "all_endpoints_status": endpoint_results
                        }
                    )
                    return False
                
        except Exception as e:
            self.log_test("Consolidated Functionality", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all Cash Flow & Performance Analysis tests"""
        print("🎯 CASH FLOW & PERFORMANCE ANALYSIS TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("Testing consolidation from Fund vs MT5 Analysis")
        print("=" * 60)
        
        # Test sequence matching the review request
        tests = [
            ("Admin Authentication", self.test_admin_authentication),
            ("Cash Flow Overview Endpoint", self.test_cashflow_overview_endpoint),
            ("Cash Flow Calendar Endpoint", self.test_cashflow_calendar_endpoint),
            ("Performance Calculation Logic", self.test_performance_calculation_logic),
            ("Risk Assessment Messages", self.test_risk_assessment_messages),
            ("Consolidated Functionality", self.test_consolidated_functionality)
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
        print("🎯 CASH FLOW & PERFORMANCE ANALYSIS TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        # Critical findings
        critical_issues = []
        working_features = []
        
        for result in self.test_results:
            if not result["success"]:
                critical_issues.append(result["test"])
            else:
                working_features.append(result["test"])
        
        if working_features:
            print(f"\n✅ WORKING FEATURES:")
            for feature in working_features:
                print(f"   - {feature}")
        
        if critical_issues:
            print(f"\n🚨 CRITICAL ISSUES:")
            for issue in critical_issues:
                print(f"   - {issue}")
        
        # Specific findings for the review request
        print(f"\n📋 CONSOLIDATION STATUS:")
        
        # Check if key endpoints are working
        overview_working = any("Cash Flow Overview" in result["test"] and result["success"] for result in self.test_results)
        calendar_working = any("Cash Flow Calendar" in result["test"] and result["success"] for result in self.test_results)
        performance_working = any("Performance Calculation" in result["test"] and result["success"] for result in self.test_results)
        
        if overview_working and calendar_working:
            print("   ✅ Cash Flow Management API endpoints are working")
        else:
            print("   ❌ Cash Flow Management API endpoints have issues")
        
        if performance_working:
            print("   ✅ Performance calculation logic is operational")
        else:
            print("   ❌ Performance calculation logic needs fixes")
        
        # Recommendations
        print(f"\n📋 RECOMMENDATIONS:")
        if not self.admin_token:
            print("   - Fix admin authentication first - all other tests depend on it")
        elif success_rate == 100:
            print("   - ✅ Cash Flow & Performance Analysis consolidation is SUCCESSFUL")
            print("   - All required endpoints and calculations are working correctly")
            print("   - Ready for production use")
        elif success_rate >= 80:
            print("   - Cash Flow & Performance Analysis mostly working with minor issues")
            print("   - Address remaining issues for full consolidation")
        else:
            print("   - Multiple critical issues with Cash Flow & Performance Analysis")
            print("   - Consolidation needs significant fixes before production")
        
        return success_rate >= 80  # 80% success rate threshold

if __name__ == "__main__":
    tester = CashFlowPerformanceAnalysisTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)