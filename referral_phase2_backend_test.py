#!/usr/bin/env python3
"""
REFERRAL SYSTEM API TESTING - PHASE 2 MIGRATION VERIFICATION
Testing Date: December 18, 2025
Backend URL: https://trader-analytics-hub-1.preview.emergentagent.com/api
Auth: Admin token (username: admin, password: password123)

CONTEXT: Just completed Phase 2 database migration - removed all duplicate/deprecated fields 
and updated backend to use new field_registry module.

CRITICAL TESTS:
1. Salespeople List - GET /api/admin/referrals/salespeople
   - Should return 3 salespeople
   - Salvador Palma should show: totalSalesVolume: $118,151.41, totalCommissionsEarned: $3,272.27, totalClientsReferred: 1
   - All fields should be camelCase (NOT snake_case)

2. Salvador Detail - GET /api/admin/referrals/salespeople/sp_6909e8eaaaf69606babea151
   - Should return Salvador's complete data
   - Should include 2 investments
   - Should include 16 commissions
   - No "Salesperson not found" error

3. Referrals Overview - GET /api/admin/referrals/overview
   - Should show active salespeople, total sales, total commissions
   - All financial values should be correct

EXPECTED RESULTS:
- All endpoints return HTTP 200
- All response fields in camelCase
- Salvador data matches: $118,151.41 sales, $3,272.27 commissions
- No deprecated fields in responses (no snake_case)

DATABASE STATE:
- ✅ All deprecated fields removed (manager_name, amount, referred_by, last_sync)
- ✅ Validation script shows 0 warnings
- ✅ Salvador data verified in MongoDB
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

class ReferralSystemTester:
    def __init__(self):
        self.base_url = "https://trader-analytics-hub-1.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name: str, status: str, details: str, expected: Any = None, actual: Any = None):
        """Log test result"""
        result = {
            "test_name": test_name,
            "status": status,  # PASS, FAIL, ERROR
            "details": details,
            "expected": expected,
            "actual": actual,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {details}")
        
        if expected is not None and actual is not None:
            print(f"   Expected: {expected}")
            print(f"   Actual: {actual}")
    
    def authenticate_admin(self) -> bool:
        """Authenticate as admin user"""
        try:
            print("🔐 Authenticating as admin...")
            
            login_data = {
                "username": "admin",
                "password": "password123",
                "user_type": "admin"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                if self.admin_token:
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}'
                    })
                    self.log_test("Admin Authentication", "PASS", "Successfully authenticated as admin")
                    return True
                else:
                    self.log_test("Admin Authentication", "FAIL", "No token received in response")
                    return False
            else:
                self.log_test("Admin Authentication", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", "ERROR", f"Exception during authentication: {str(e)}")
            return False
    
    def test_salespeople_list(self) -> bool:
        """Test 1: Salespeople List - GET /api/admin/referrals/salespeople"""
        try:
            print("\n👥 Testing Salespeople List API...")
            
            response = self.session.get(f"{self.base_url}/admin/referrals/salespeople")
            
            if response.status_code != 200:
                self.log_test("Salespeople List API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            salespeople = data.get("salespeople", [])
            
            # Check total count
            if len(salespeople) == 3:
                self.log_test("Salespeople Count", "PASS", f"Found expected 3 salespeople")
            else:
                self.log_test("Salespeople Count", "FAIL", f"Expected 3 salespeople, found {len(salespeople)}")
                print(f"   Found salespeople: {[sp.get('name') for sp in salespeople]}")
                return False
            
            # Find Salvador Palma
            salvador = None
            for sp in salespeople:
                if sp.get('name') == 'Salvador Palma':
                    salvador = sp
                    break
            
            if not salvador:
                self.log_test("Salvador Palma Found", "FAIL", "Salvador Palma not found in salespeople list")
                return False
            
            self.log_test("Salvador Palma Found", "PASS", "Salvador Palma found in salespeople list")
            
            # Check Salvador's financial data
            total_sales = salvador.get('totalSalesVolume', 0)
            total_commissions = salvador.get('totalCommissionsEarned', 0)
            total_clients = salvador.get('totalClientsReferred', 0)
            
            success = True
            
            # Check totalSalesVolume
            if abs(total_sales - 118151.41) < 0.01:
                self.log_test("Salvador Total Sales Volume", "PASS", f"${total_sales:,.2f} matches expected $118,151.41")
            else:
                self.log_test("Salvador Total Sales Volume", "FAIL", f"Expected $118,151.41, got ${total_sales:,.2f}")
                success = False
            
            # Check totalCommissionsEarned
            if abs(total_commissions - 3272.27) < 0.01:
                self.log_test("Salvador Total Commissions", "PASS", f"${total_commissions:,.2f} matches expected $3,272.27")
            else:
                self.log_test("Salvador Total Commissions", "FAIL", f"Expected $3,272.27, got ${total_commissions:,.2f}")
                success = False
            
            # Check totalClientsReferred
            if total_clients == 1:
                self.log_test("Salvador Total Clients", "PASS", f"{total_clients} client matches expected 1")
            else:
                self.log_test("Salvador Total Clients", "FAIL", f"Expected 1 client, got {total_clients}")
                success = False
            
            # Check for camelCase fields (no snake_case)
            camel_case_fields = ['totalSalesVolume', 'totalCommissionsEarned', 'totalClientsReferred', 
                               'salespersonId', 'referralCode', 'referralLink', 'activeClients']
            snake_case_fields = ['total_sales_volume', 'total_commissions_earned', 'total_clients_referred',
                               'salesperson_id', 'referral_code', 'referral_link', 'active_clients']
            
            camel_found = sum(1 for field in camel_case_fields if field in salvador)
            snake_found = sum(1 for field in snake_case_fields if field in salvador)
            
            if camel_found >= 4 and snake_found == 0:
                self.log_test("Field Name Format", "PASS", f"Found {camel_found} camelCase fields, {snake_found} snake_case fields")
            else:
                self.log_test("Field Name Format", "FAIL", f"Expected camelCase fields only. Found {camel_found} camelCase, {snake_found} snake_case")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Salespeople List Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_salvador_detail(self) -> bool:
        """Test 2: Salvador Detail - GET /api/admin/referrals/salespeople/sp_6909e8eaaaf69606babea151"""
        try:
            print("\n🔍 Testing Salvador Detail API...")
            
            # Try the specific Salvador ID from the review request
            salvador_id = "sp_6909e8eaaaf69606babea151"
            response = self.session.get(f"{self.base_url}/admin/referrals/salespeople/{salvador_id}")
            
            if response.status_code == 404:
                # Try alternative ID format (MongoDB ObjectId)
                salvador_id = "6909e8eaaaf69606babea151"
                response = self.session.get(f"{self.base_url}/admin/referrals/salespeople/{salvador_id}")
            
            if response.status_code != 200:
                self.log_test("Salvador Detail API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Check that we got Salvador's data (not "Salesperson not found")
            if 'name' in data and data['name'] == 'Salvador Palma':
                self.log_test("Salvador Data Retrieved", "PASS", "Salvador Palma data retrieved successfully")
            else:
                self.log_test("Salvador Data Retrieved", "FAIL", "Salvador Palma data not found or incorrect")
                return False
            
            # Check for investments
            investments = data.get('investments', [])
            if len(investments) == 2:
                self.log_test("Salvador Investments Count", "PASS", f"Found expected 2 investments")
            else:
                self.log_test("Salvador Investments Count", "FAIL", f"Expected 2 investments, found {len(investments)}")
                print(f"   Investments found: {len(investments)}")
            
            # Check for commissions
            commissions = data.get('commissions', [])
            if len(commissions) == 16:
                self.log_test("Salvador Commissions Count", "PASS", f"Found expected 16 commissions")
            else:
                self.log_test("Salvador Commissions Count", "FAIL", f"Expected 16 commissions, found {len(commissions)}")
                print(f"   Commissions found: {len(commissions)}")
            
            # Check financial summary
            total_sales = data.get('totalSalesVolume', 0)
            total_commissions = data.get('totalCommissions', 0)
            
            success = True
            
            if abs(total_sales - 118151.41) < 0.01:
                self.log_test("Salvador Detail Sales Volume", "PASS", f"${total_sales:,.2f} matches expected")
            else:
                self.log_test("Salvador Detail Sales Volume", "FAIL", f"Expected $118,151.41, got ${total_sales:,.2f}")
                success = False
            
            if abs(total_commissions - 3272.27) < 0.01:
                self.log_test("Salvador Detail Commissions", "PASS", f"${total_commissions:,.2f} matches expected")
            else:
                self.log_test("Salvador Detail Commissions", "FAIL", f"Expected $3,272.27, got ${total_commissions:,.2f}")
                success = False
            
            return success and len(investments) == 2 and len(commissions) == 16
            
        except Exception as e:
            self.log_test("Salvador Detail Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_referrals_overview(self) -> bool:
        """Test 3: Referrals Overview - GET /api/admin/referrals/overview"""
        try:
            print("\n📊 Testing Referrals Overview API...")
            
            response = self.session.get(f"{self.base_url}/admin/referrals/overview")
            
            if response.status_code != 200:
                self.log_test("Referrals Overview API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Check for key metrics
            active_salespeople = data.get('activeSalespeople', 0)
            total_sales_volume = data.get('totalSalesVolume', 0)
            total_commissions = data.get('totalCommissions', 0)
            pending_commissions = data.get('pendingCommissions', 0)
            
            success = True
            
            # Check active salespeople count
            if active_salespeople == 3:
                self.log_test("Active Salespeople Count", "PASS", f"Found {active_salespeople} active salespeople")
            else:
                self.log_test("Active Salespeople Count", "FAIL", f"Expected 3 active salespeople, found {active_salespeople}")
                success = False
            
            # Check total sales volume
            if abs(total_sales_volume - 118151.41) < 0.01:
                self.log_test("Total Sales Volume", "PASS", f"${total_sales_volume:,.2f} matches expected")
            else:
                self.log_test("Total Sales Volume", "FAIL", f"Expected $118,151.41, got ${total_sales_volume:,.2f}")
                success = False
            
            # Check total commissions
            if abs(total_commissions - 3272.27) < 0.01:
                self.log_test("Total Commissions", "PASS", f"${total_commissions:,.2f} matches expected")
            else:
                self.log_test("Total Commissions", "FAIL", f"Expected $3,272.27, got ${total_commissions:,.2f}")
                success = False
            
            # Check for camelCase field names in overview
            camel_case_fields = ['activeSalespeople', 'totalSalesVolume', 'totalCommissions', 'pendingCommissions']
            snake_case_fields = ['active_salespeople', 'total_sales_volume', 'total_commissions', 'pending_commissions']
            
            camel_found = sum(1 for field in camel_case_fields if field in data)
            snake_found = sum(1 for field in snake_case_fields if field in data)
            
            if camel_found >= 3 and snake_found == 0:
                self.log_test("Overview Field Format", "PASS", f"Found {camel_found} camelCase fields, no snake_case")
            else:
                self.log_test("Overview Field Format", "FAIL", f"Expected camelCase only. Found {camel_found} camelCase, {snake_found} snake_case")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Referrals Overview Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def check_deprecated_fields(self) -> bool:
        """Test 4: Check for deprecated fields in responses"""
        try:
            print("\n🔍 Checking for deprecated fields...")
            
            # Get salespeople list to check for deprecated fields
            response = self.session.get(f"{self.base_url}/admin/referrals/salespeople")
            
            if response.status_code != 200:
                self.log_test("Deprecated Fields Check", "ERROR", f"Could not get salespeople data: HTTP {response.status_code}")
                return False
            
            data = response.json()
            salespeople = data.get("salespeople", [])
            
            if not salespeople:
                self.log_test("Deprecated Fields Check", "ERROR", "No salespeople data to check")
                return False
            
            # Check for deprecated fields that should NOT be present
            deprecated_fields = [
                'manager_name', 'amount', 'referred_by', 'last_sync', 
                'total_sales_volume', 'total_commissions_earned', 'salesperson_id'
            ]
            
            deprecated_found = []
            for sp in salespeople:
                for field in deprecated_fields:
                    if field in sp:
                        deprecated_found.append(field)
            
            if not deprecated_found:
                self.log_test("Deprecated Fields Check", "PASS", "No deprecated fields found in API responses")
                return True
            else:
                self.log_test("Deprecated Fields Check", "FAIL", f"Found deprecated fields: {deprecated_found}")
                return False
            
        except Exception as e:
            self.log_test("Deprecated Fields Check", "ERROR", f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all referral system tests"""
        print("🚀 Starting Referral System API Testing - Phase 2 Migration Verification")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate_admin():
            return {"success": False, "error": "Authentication failed"}
        
        # Run all tests
        test_results = {
            "salespeople_list": self.test_salespeople_list(),
            "salvador_detail": self.test_salvador_detail(),
            "referrals_overview": self.test_referrals_overview(),
            "deprecated_fields_check": self.check_deprecated_fields()
        }
        
        # Calculate summary
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result)
        success_rate = (passed_tests / total_tests) * 100
        
        print("\n" + "=" * 80)
        print("📊 REFERRAL SYSTEM API TEST SUMMARY - PHASE 2 MIGRATION")
        print("=" * 80)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name.replace('_', ' ').title()}")
        
        print(f"\n🎯 Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate == 100:
            print("🎉 REFERRAL SYSTEM VERIFICATION: EXCELLENT - Phase 2 migration successful!")
            print("   ✅ All endpoints return HTTP 200")
            print("   ✅ All response fields in camelCase (no snake_case)")
            print("   ✅ Salvador data matches: $118,151.41 sales, $3,272.27 commissions")
            print("   ✅ No deprecated fields in responses")
            print("   ✅ Salvador detail shows 2 investments and 16 commissions")
        elif success_rate >= 75:
            print("✅ REFERRAL SYSTEM VERIFICATION: GOOD - Minor issues to address")
        elif success_rate >= 50:
            print("⚠️ REFERRAL SYSTEM VERIFICATION: NEEDS ATTENTION - Several issues found")
        else:
            print("🚨 REFERRAL SYSTEM VERIFICATION: CRITICAL ISSUES - Phase 2 migration problems detected")
        
        return {
            "success": success_rate >= 75,
            "success_rate": success_rate,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "test_results": test_results,
            "detailed_results": self.test_results
        }

def main():
    """Main test execution"""
    tester = ReferralSystemTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results["success"] else 1)

if __name__ == "__main__":
    main()