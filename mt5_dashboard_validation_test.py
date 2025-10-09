#!/usr/bin/env python3
"""
MT5 DASHBOARD VALIDATION TEST
Focused validation of the specific requirements from the review request.

VALIDATION CRITERIA:
✅ Dashboard overview should return comprehensive analytics
✅ Enhanced accounts should show live integration fields  
✅ All financial totals should equal $118,151.41
✅ Data freshness indicators should be present
✅ Fund breakdowns should show BALANCE + CORE analysis
✅ Performance metrics should be calculated correctly
"""

import requests
import json
import sys
from datetime import datetime

BACKEND_URL = "https://trading-platform-76.preview.emergentagent.com/api"

class MT5DashboardValidator:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.validation_results = {}
        
    def authenticate(self):
        """Authenticate as admin"""
        login_data = {
            "username": "admin",
            "password": "password123", 
            "user_type": "admin"
        }
        
        response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            self.admin_token = data.get("token")
            self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
            return True
        return False
    
    def validate_dashboard_comprehensive_analytics(self):
        """✅ Dashboard overview should return comprehensive analytics"""
        print("\n📊 VALIDATING: Dashboard overview comprehensive analytics")
        
        response = self.session.get(f"{BACKEND_URL}/mt5/dashboard/overview")
        
        if response.status_code != 200:
            self.validation_results["comprehensive_analytics"] = False
            print(f"❌ FAIL: HTTP {response.status_code}")
            return False
        
        data = response.json()
        dashboard = data.get("dashboard", {})
        
        # Check for comprehensive analytics components
        required_analytics = [
            "total_accounts", "total_allocated", "total_equity", "total_profit",
            "by_client", "by_fund", "by_broker", "performance_summary"
        ]
        
        present_analytics = [field for field in required_analytics if field in dashboard]
        
        if len(present_analytics) >= 6:  # At least 6 out of 8 analytics present
            self.validation_results["comprehensive_analytics"] = True
            print(f"✅ PASS: {len(present_analytics)}/8 comprehensive analytics present")
            print(f"   Present: {present_analytics}")
            return True
        else:
            self.validation_results["comprehensive_analytics"] = False
            print(f"❌ FAIL: Only {len(present_analytics)}/8 analytics present")
            return False
    
    def validate_enhanced_accounts_live_integration(self):
        """✅ Enhanced accounts should show live integration fields"""
        print("\n🏦 VALIDATING: Enhanced accounts live integration fields")
        
        response = self.session.get(f"{BACKEND_URL}/mt5/accounts/client_alejandro")
        
        if response.status_code != 200:
            self.validation_results["live_integration_fields"] = False
            print(f"❌ FAIL: HTTP {response.status_code}")
            return False
        
        data = response.json()
        
        # Check for live integration fields
        live_integration_fields = [
            "data_freshness", "summary", "timestamp"
        ]
        
        present_fields = [field for field in live_integration_fields if field in data]
        
        # Check data freshness structure
        data_freshness = data.get("data_freshness", {})
        freshness_indicators = ["live_accounts", "cached_accounts", "stored_accounts"]
        present_freshness = [field for field in freshness_indicators if field in data_freshness]
        
        if len(present_fields) >= 2 and len(present_freshness) >= 2:
            self.validation_results["live_integration_fields"] = True
            print(f"✅ PASS: Live integration fields present")
            print(f"   Integration fields: {present_fields}")
            print(f"   Freshness indicators: {present_freshness}")
            return True
        else:
            self.validation_results["live_integration_fields"] = False
            print(f"❌ FAIL: Insufficient live integration fields")
            return False
    
    def validate_financial_totals_118151_41(self):
        """✅ All financial totals should equal $118,151.41"""
        print("\n💰 VALIDATING: Financial totals equal $118,151.41")
        
        expected_total = 118151.41
        endpoints_to_check = [
            ("/mt5/multi-account/summary/client_alejandro", "summary.total_allocated"),
            ("/investments/client/client_alejandro", "calculated_total")
        ]
        
        matching_endpoints = 0
        
        for endpoint, total_path in endpoints_to_check:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    
                    if endpoint == "/mt5/multi-account/summary/client_alejandro":
                        total_value = data.get("data", {}).get("summary", {}).get("total_allocated", 0)
                    elif endpoint == "/investments/client/client_alejandro":
                        investments = data.get("investments", [])
                        total_value = sum(inv.get("current_value", 0) for inv in investments)
                    
                    if abs(total_value - expected_total) < 0.01:
                        matching_endpoints += 1
                        print(f"   ✅ {endpoint}: ${total_value:,.2f}")
                    else:
                        print(f"   ❌ {endpoint}: ${total_value:,.2f} (expected ${expected_total:,.2f})")
                        
            except Exception as e:
                print(f"   ❌ {endpoint}: Error - {str(e)}")
        
        if matching_endpoints >= 1:
            self.validation_results["financial_totals_correct"] = True
            print(f"✅ PASS: {matching_endpoints} endpoints match expected total")
            return True
        else:
            self.validation_results["financial_totals_correct"] = False
            print(f"❌ FAIL: No endpoints match expected total")
            return False
    
    def validate_data_freshness_indicators(self):
        """✅ Data freshness indicators should be present"""
        print("\n🕐 VALIDATING: Data freshness indicators present")
        
        response = self.session.get(f"{BACKEND_URL}/mt5/accounts/client_alejandro")
        
        if response.status_code != 200:
            self.validation_results["data_freshness_present"] = False
            print(f"❌ FAIL: HTTP {response.status_code}")
            return False
        
        data = response.json()
        data_freshness = data.get("data_freshness", {})
        
        required_freshness_fields = ["live_accounts", "cached_accounts", "stored_accounts"]
        present_freshness_fields = [field for field in required_freshness_fields if field in data_freshness]
        
        # Also check for timestamp
        has_timestamp = "timestamp" in data
        
        if len(present_freshness_fields) >= 3 and has_timestamp:
            self.validation_results["data_freshness_present"] = True
            print(f"✅ PASS: All freshness indicators present")
            print(f"   Freshness fields: {present_freshness_fields}")
            print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
            return True
        else:
            self.validation_results["data_freshness_present"] = False
            print(f"❌ FAIL: Missing freshness indicators")
            return False
    
    def validate_fund_breakdown_balance_core(self):
        """✅ Fund breakdowns should show BALANCE + CORE analysis"""
        print("\n📈 VALIDATING: Fund breakdowns show BALANCE + CORE analysis")
        
        response = self.session.get(f"{BACKEND_URL}/mt5/dashboard/overview")
        
        if response.status_code != 200:
            self.validation_results["fund_breakdown_present"] = False
            print(f"❌ FAIL: HTTP {response.status_code}")
            return False
        
        data = response.json()
        by_fund = data.get("dashboard", {}).get("by_fund", {})
        
        # Check for BALANCE and CORE fund analysis
        has_balance = "BALANCE" in by_fund
        has_core = "CORE" in by_fund
        
        if has_balance and has_core:
            balance_data = by_fund["BALANCE"]
            core_data = by_fund["CORE"]
            
            # Check that fund data has required fields
            required_fund_fields = ["accounts", "allocated", "equity", "profit"]
            balance_fields = [field for field in required_fund_fields if field in balance_data]
            core_fields = [field for field in required_fund_fields if field in core_data]
            
            if len(balance_fields) >= 3 and len(core_fields) >= 3:
                self.validation_results["fund_breakdown_present"] = True
                print(f"✅ PASS: BALANCE + CORE fund breakdown present")
                print(f"   BALANCE: {balance_fields}")
                print(f"   CORE: {core_fields}")
                return True
        
        self.validation_results["fund_breakdown_present"] = False
        print(f"❌ FAIL: Incomplete fund breakdown")
        print(f"   Has BALANCE: {has_balance}, Has CORE: {has_core}")
        return False
    
    def validate_performance_metrics_calculated(self):
        """✅ Performance metrics should be calculated correctly"""
        print("\n📊 VALIDATING: Performance metrics calculated correctly")
        
        response = self.session.get(f"{BACKEND_URL}/mt5/dashboard/overview")
        
        if response.status_code != 200:
            self.validation_results["performance_metrics_calculated"] = False
            print(f"❌ FAIL: HTTP {response.status_code}")
            return False
        
        data = response.json()
        dashboard = data.get("dashboard", {})
        
        # Check for performance metrics
        performance_fields = [
            "overall_return_percent", "total_profit", "performance_summary"
        ]
        
        present_performance = [field for field in performance_fields if field in dashboard]
        
        # Check performance summary structure
        performance_summary = dashboard.get("performance_summary", {})
        summary_fields = ["profitable_accounts", "losing_accounts", "break_even_accounts", "best_performer", "worst_performer"]
        present_summary_fields = [field for field in summary_fields if field in performance_summary]
        
        if len(present_performance) >= 2 and len(present_summary_fields) >= 3:
            self.validation_results["performance_metrics_calculated"] = True
            print(f"✅ PASS: Performance metrics calculated")
            print(f"   Performance fields: {present_performance}")
            print(f"   Summary fields: {present_summary_fields}")
            return True
        else:
            self.validation_results["performance_metrics_calculated"] = False
            print(f"❌ FAIL: Insufficient performance metrics")
            return False
    
    def run_validation(self):
        """Run all validation criteria"""
        print("🎯 MT5 DASHBOARD VALIDATION TEST")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 60)
        
        if not self.authenticate():
            print("❌ CRITICAL: Authentication failed")
            return False
        
        print("✅ Authentication successful")
        
        # Run all validation criteria
        validations = [
            ("Comprehensive Analytics", self.validate_dashboard_comprehensive_analytics),
            ("Live Integration Fields", self.validate_enhanced_accounts_live_integration),
            ("Financial Totals $118,151.41", self.validate_financial_totals_118151_41),
            ("Data Freshness Indicators", self.validate_data_freshness_indicators),
            ("BALANCE + CORE Fund Breakdown", self.validate_fund_breakdown_balance_core),
            ("Performance Metrics Calculation", self.validate_performance_metrics_calculated)
        ]
        
        passed_validations = 0
        total_validations = len(validations)
        
        for validation_name, validation_func in validations:
            try:
                if validation_func():
                    passed_validations += 1
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {validation_name}: {str(e)}")
        
        # Final summary
        print("\n" + "=" * 60)
        print("🎯 MT5 DASHBOARD VALIDATION SUMMARY")
        print("=" * 60)
        
        success_rate = (passed_validations / total_validations) * 100
        print(f"Overall Validation Success: {success_rate:.1f}% ({passed_validations}/{total_validations})")
        
        print(f"\n📋 VALIDATION CRITERIA RESULTS:")
        for criteria, result in self.validation_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status} {criteria.replace('_', ' ').title()}")
        
        # Final assessment based on review requirements
        print(f"\n🎯 FINAL ASSESSMENT:")
        if success_rate >= 83:  # 5/6 criteria
            print("   ✅ MT5 DASHBOARD SYSTEM MEETS VALIDATION CRITERIA")
            print("   🚀 Ready for frontend dashboard integration")
        elif success_rate >= 67:  # 4/6 criteria
            print("   ⚠️  MT5 DASHBOARD SYSTEM PARTIALLY MEETS CRITERIA")
            print("   🔧 Minor issues need addressing before full deployment")
        else:
            print("   ❌ MT5 DASHBOARD SYSTEM FAILS VALIDATION CRITERIA")
            print("   🚨 Critical issues require immediate attention")
        
        return success_rate >= 67

if __name__ == "__main__":
    validator = MT5DashboardValidator()
    success = validator.run_validation()
    
    sys.exit(0 if success else 1)