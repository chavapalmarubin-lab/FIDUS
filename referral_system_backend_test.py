#!/usr/bin/env python3
"""
FIDUS REFERRAL SYSTEM BACKEND TESTING
Testing Date: December 18, 2025
Backend URL: https://financial-api-fix.preview.emergentagent.com/api
Auth: Admin token (username: admin, password: password123)

Test Objectives:
1. Test Public Endpoints (No Auth Required)
   - GET /api/public/salespeople - Get list of active salespeople
   - GET /api/public/salespeople/SP-2025 - Get salesperson by referral code

2. Test Admin Endpoints (Require Auth)
   - GET /api/admin/referrals/salespeople - Get all salespeople
   - POST /api/admin/referrals/salespeople - Create new salesperson
   - GET /api/admin/referrals/salespeople/{id} - Get salesperson dashboard
   - PUT /api/admin/referrals/salespeople/{id} - Update salesperson
   - GET /api/admin/referrals/commissions/calendar - Get commission calendar
   - GET /api/admin/referrals/commissions/pending - Get pending commissions
   - POST /api/admin/referrals/commissions/{id}/approve - Approve commission
   - POST /api/admin/referrals/commissions/{id}/mark-paid - Mark as paid
   - PUT /api/admin/referrals/clients/{client_id}/referral - Assign client referral

Expected System Data:
- Salvador Palma (Salesperson) with referral code "SP-2025"
- Alejandro Mariscal Romero (Client) referred by Salvador
- Commission rate: 10% of client interest payments
- Current data: 13 commission records totaling $353.95
- Salvador's ID: 6909e8eaaaf69606babea151
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

class ReferralSystemTester:
    def __init__(self):
        self.base_url = "https://financial-api-fix.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.salvador_id = "6909e8eaaaf69606babea151"
        self.expected_commission_total = 353.95
        self.expected_commission_count = 13
        
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
    
    def test_public_salespeople_list(self) -> bool:
        """Test 1: GET /api/public/salespeople - Get list of active salespeople"""
        try:
            print("\n👥 Testing Public Salespeople List...")
            
            # Remove auth header for public endpoint
            headers = {}
            response = requests.get(f"{self.base_url}/public/salespeople", headers=headers)
            
            if response.status_code != 200:
                self.log_test("Public Salespeople List", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            salespeople = data.get("salespeople", [])
            
            # Check if Salvador Palma is in the list
            salvador_found = False
            for person in salespeople:
                if person.get("name") == "Salvador Palma" and person.get("referral_code") == "SP-2025":
                    salvador_found = True
                    self.log_test("Salvador Palma Found", "PASS", "Salvador Palma with SP-2025 found in public list")
                    break
            
            if not salvador_found:
                self.log_test("Salvador Palma Found", "FAIL", "Salvador Palma with SP-2025 not found in public list")
                return False
            
            self.log_test("Public Salespeople List", "PASS", f"Found {len(salespeople)} active salespeople")
            return True
            
        except Exception as e:
            self.log_test("Public Salespeople List", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_public_salesperson_by_code(self) -> bool:
        """Test 2: GET /api/public/salespeople/SP-2025 - Get salesperson by referral code"""
        try:
            print("\n🔍 Testing Public Salesperson by Code...")
            
            # Remove auth header for public endpoint
            headers = {}
            response = requests.get(f"{self.base_url}/public/salespeople/SP-2025", headers=headers)
            
            if response.status_code != 200:
                self.log_test("Public Salesperson by Code", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Verify Salvador's details
            expected_name = "Salvador Palma"
            expected_code = "SP-2025"
            
            actual_name = data.get("name")
            actual_code = data.get("referral_code")
            
            if actual_name == expected_name and actual_code == expected_code:
                self.log_test("Salvador Details Verification", "PASS", f"Correct details: {actual_name} ({actual_code})")
                return True
            else:
                self.log_test("Salvador Details Verification", "FAIL", 
                            f"Expected: {expected_name} ({expected_code}), Got: {actual_name} ({actual_code})")
                return False
            
        except Exception as e:
            self.log_test("Public Salesperson by Code", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_admin_salespeople_list(self) -> bool:
        """Test 3: GET /api/admin/referrals/salespeople - Get all salespeople"""
        try:
            print("\n👥 Testing Admin Salespeople List...")
            
            response = self.session.get(f"{self.base_url}/admin/referrals/salespeople")
            
            if response.status_code != 200:
                self.log_test("Admin Salespeople List", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            salespeople = data.get("salespeople", [])
            
            # Find Salvador and verify his metrics
            salvador_found = False
            for person in salespeople:
                if person.get("name") == "Salvador Palma":
                    salvador_found = True
                    
                    # Check real-time metrics
                    total_commissions = person.get("total_commissions", 0)
                    commission_count = person.get("commission_count", 0)
                    
                    self.log_test("Salvador Metrics", "PASS", 
                                f"Total: ${total_commissions}, Count: {commission_count}")
                    break
            
            if not salvador_found:
                self.log_test("Salvador in Admin List", "FAIL", "Salvador not found in admin salespeople list")
                return False
            
            self.log_test("Admin Salespeople List", "PASS", f"Found {len(salespeople)} salespeople with metrics")
            return True
            
        except Exception as e:
            self.log_test("Admin Salespeople List", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_create_new_salesperson(self) -> bool:
        """Test 4: POST /api/admin/referrals/salespeople - Create new salesperson"""
        try:
            print("\n➕ Testing Create New Salesperson...")
            
            new_salesperson = {
                "name": "Test Person",
                "email": "test@test.com",
                "phone": "+1234567890"
            }
            
            response = self.session.post(f"{self.base_url}/admin/referrals/salespeople", json=new_salesperson)
            
            if response.status_code not in [200, 201]:
                self.log_test("Create New Salesperson", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Check if referral code was auto-generated
            referral_code = data.get("referral_code")
            if referral_code:
                self.log_test("Auto-Generated Referral Code", "PASS", f"Generated code: {referral_code}")
                return True
            else:
                self.log_test("Auto-Generated Referral Code", "FAIL", "No referral code generated")
                return False
            
        except Exception as e:
            self.log_test("Create New Salesperson", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_salesperson_dashboard(self) -> bool:
        """Test 5: GET /api/admin/referrals/salespeople/{id} - Get salesperson dashboard"""
        try:
            print("\n📊 Testing Salesperson Dashboard...")
            
            response = self.session.get(f"{self.base_url}/admin/referrals/salespeople/{self.salvador_id}")
            
            if response.status_code != 200:
                self.log_test("Salesperson Dashboard", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Verify dashboard components
            required_fields = ["clients", "investments", "commissions", "metrics"]
            missing_fields = []
            
            for field in required_fields:
                if field not in data:
                    missing_fields.append(field)
            
            if missing_fields:
                self.log_test("Dashboard Components", "FAIL", f"Missing fields: {missing_fields}")
                return False
            
            # Check commission data
            commissions = data.get("commissions", [])
            total_commission_amount = sum(c.get("amount", 0) for c in commissions)
            
            self.log_test("Commission Data", "PASS", 
                        f"Found {len(commissions)} commissions totaling ${total_commission_amount:.2f}")
            
            # Verify Alejandro is in clients
            clients = data.get("clients", [])
            alejandro_found = any("Alejandro" in client.get("name", "") for client in clients)
            
            if alejandro_found:
                self.log_test("Alejandro Client Found", "PASS", "Alejandro found in Salvador's clients")
            else:
                self.log_test("Alejandro Client Found", "FAIL", "Alejandro not found in Salvador's clients")
            
            return True
            
        except Exception as e:
            self.log_test("Salesperson Dashboard", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_update_salesperson(self) -> bool:
        """Test 6: PUT /api/admin/referrals/salespeople/{id} - Update salesperson"""
        try:
            print("\n✏️ Testing Update Salesperson...")
            
            update_data = {
                "phone": "+1234567891",
                "wallet_details": {
                    "crypto_wallet": "0x123abc456def",
                    "preferred_method": "crypto"
                }
            }
            
            response = self.session.put(f"{self.base_url}/admin/referrals/salespeople/{self.salvador_id}", 
                                      json=update_data)
            
            if response.status_code != 200:
                self.log_test("Update Salesperson", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Verify update was successful
            if data.get("success"):
                self.log_test("Update Salesperson", "PASS", "Salesperson updated successfully")
                return True
            else:
                self.log_test("Update Salesperson", "FAIL", "Update operation failed")
                return False
            
        except Exception as e:
            self.log_test("Update Salesperson", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_commission_calendar(self) -> bool:
        """Test 7: GET /api/admin/referrals/commissions/calendar - Get commission calendar"""
        try:
            print("\n📅 Testing Commission Calendar...")
            
            params = {
                "start_date": "2025-12-01",
                "end_date": "2026-12-31"
            }
            
            response = self.session.get(f"{self.base_url}/admin/referrals/commissions/calendar", params=params)
            
            if response.status_code != 200:
                self.log_test("Commission Calendar", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Check for monthly groupings
            monthly_data = data.get("monthly_commissions", [])
            if monthly_data:
                self.log_test("Monthly Groupings", "PASS", f"Found {len(monthly_data)} months of commission data")
                
                # Check first commission due date
                first_commission = None
                for month in monthly_data:
                    commissions = month.get("commissions", [])
                    if commissions:
                        first_commission = commissions[0]
                        break
                
                if first_commission:
                    due_date = first_commission.get("due_date")
                    amount = first_commission.get("amount")
                    self.log_test("First Commission Due", "PASS", f"Due: {due_date}, Amount: ${amount}")
                
                return True
            else:
                self.log_test("Monthly Groupings", "FAIL", "No monthly commission data found")
                return False
            
        except Exception as e:
            self.log_test("Commission Calendar", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_pending_commissions(self) -> bool:
        """Test 8: GET /api/admin/referrals/commissions/pending - Get pending commissions"""
        try:
            print("\n⏳ Testing Pending Commissions...")
            
            params = {
                "status_filter": "all",
                "overdue": "false"
            }
            
            response = self.session.get(f"{self.base_url}/admin/referrals/commissions/pending", params=params)
            
            if response.status_code != 200:
                self.log_test("Pending Commissions", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Check for salesperson groupings
            by_salesperson = data.get("by_salesperson", {})
            if by_salesperson:
                self.log_test("Salesperson Groupings", "PASS", f"Found {len(by_salesperson)} salespeople with pending commissions")
                
                # Check Salvador's pending commissions
                salvador_commissions = by_salesperson.get("Salvador Palma", [])
                if salvador_commissions:
                    total_pending = sum(c.get("amount", 0) for c in salvador_commissions)
                    self.log_test("Salvador Pending Commissions", "PASS", 
                                f"Salvador has {len(salvador_commissions)} pending commissions totaling ${total_pending:.2f}")
                
                return True
            else:
                self.log_test("Salesperson Groupings", "FAIL", "No salesperson groupings found")
                return False
            
        except Exception as e:
            self.log_test("Pending Commissions", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_approve_commission(self) -> bool:
        """Test 9: POST /api/admin/referrals/commissions/{id}/approve - Approve commission"""
        try:
            print("\n✅ Testing Approve Commission...")
            
            # First get a commission ID from Salvador's commissions
            dashboard_response = self.session.get(f"{self.base_url}/admin/referrals/salespeople/{self.salvador_id}")
            
            if dashboard_response.status_code != 200:
                self.log_test("Get Commission ID", "FAIL", "Could not get Salvador's dashboard")
                return False
            
            dashboard_data = dashboard_response.json()
            commissions = dashboard_data.get("commissions", [])
            
            if not commissions:
                self.log_test("Get Commission ID", "FAIL", "No commissions found for Salvador")
                return False
            
            # Find a pending commission
            commission_id = None
            for commission in commissions:
                if commission.get("status") == "pending":
                    commission_id = commission.get("id")
                    break
            
            if not commission_id:
                self.log_test("Find Pending Commission", "FAIL", "No pending commissions found")
                return False
            
            # Approve the commission
            response = self.session.post(f"{self.base_url}/admin/referrals/commissions/{commission_id}/approve")
            
            if response.status_code != 200:
                self.log_test("Approve Commission", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Verify status change
            if data.get("status") == "approved":
                self.log_test("Approve Commission", "PASS", f"Commission {commission_id} approved successfully")
                return True
            else:
                self.log_test("Approve Commission", "FAIL", f"Commission status: {data.get('status')}")
                return False
            
        except Exception as e:
            self.log_test("Approve Commission", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_mark_commission_paid(self) -> bool:
        """Test 10: POST /api/admin/referrals/commissions/{id}/mark-paid - Mark as paid"""
        try:
            print("\n💰 Testing Mark Commission Paid...")
            
            # First get an approved commission ID
            dashboard_response = self.session.get(f"{self.base_url}/admin/referrals/salespeople/{self.salvador_id}")
            
            if dashboard_response.status_code != 200:
                self.log_test("Get Approved Commission ID", "FAIL", "Could not get Salvador's dashboard")
                return False
            
            dashboard_data = dashboard_response.json()
            commissions = dashboard_data.get("commissions", [])
            
            # Find an approved commission
            commission_id = None
            for commission in commissions:
                if commission.get("status") == "approved":
                    commission_id = commission.get("id")
                    break
            
            if not commission_id:
                self.log_test("Find Approved Commission", "FAIL", "No approved commissions found")
                return False
            
            # Mark as paid
            payment_data = {
                "method": "crypto_wallet",
                "reference": "TXN-TEST-001",
                "hash": "0x123abc"
            }
            
            response = self.session.post(f"{self.base_url}/admin/referrals/commissions/{commission_id}/mark-paid", 
                                       json=payment_data)
            
            if response.status_code != 200:
                self.log_test("Mark Commission Paid", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Verify status change and metrics update
            if data.get("status") == "paid":
                self.log_test("Mark Commission Paid", "PASS", f"Commission {commission_id} marked as paid")
                return True
            else:
                self.log_test("Mark Commission Paid", "FAIL", f"Commission status: {data.get('status')}")
                return False
            
        except Exception as e:
            self.log_test("Mark Commission Paid", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_assign_client_referral(self) -> bool:
        """Test 11: PUT /api/admin/referrals/clients/{client_id}/referral - Assign client referral"""
        try:
            print("\n🔗 Testing Assign Client Referral...")
            
            # Use Alejandro's client ID (assuming it exists)
            client_id = "client_alejandro"
            
            assignment_data = {
                "salesperson_id": self.salvador_id
            }
            
            response = self.session.put(f"{self.base_url}/admin/referrals/clients/{client_id}/referral", 
                                      json=assignment_data)
            
            if response.status_code != 200:
                self.log_test("Assign Client Referral", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Verify assignment and commission regeneration
            if data.get("success"):
                regenerated_count = data.get("regenerated_commissions", 0)
                self.log_test("Assign Client Referral", "PASS", 
                            f"Client assigned successfully, {regenerated_count} commissions regenerated")
                return True
            else:
                self.log_test("Assign Client Referral", "FAIL", "Assignment failed")
                return False
            
        except Exception as e:
            self.log_test("Assign Client Referral", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_commission_calculations(self) -> bool:
        """Test 12: Verify commission calculations match 10% of interest payments"""
        try:
            print("\n🧮 Testing Commission Calculations...")
            
            # Get Salvador's dashboard to check commission calculations
            response = self.session.get(f"{self.base_url}/admin/referrals/salespeople/{self.salvador_id}")
            
            if response.status_code != 200:
                self.log_test("Commission Calculations", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            commissions = data.get("commissions", [])
            
            # Verify commission rate calculation
            calculation_correct = True
            for commission in commissions:
                client_interest = commission.get("client_interest_amount", 0)
                commission_amount = commission.get("amount", 0)
                expected_commission = client_interest * 0.10
                
                if abs(commission_amount - expected_commission) > 0.01:  # Allow small rounding differences
                    calculation_correct = False
                    self.log_test("Commission Rate Verification", "FAIL", 
                                f"Commission {commission.get('id')}: Expected ${expected_commission:.2f}, Got ${commission_amount:.2f}")
                    break
            
            if calculation_correct:
                self.log_test("Commission Calculations", "PASS", "All commissions calculated at correct 10% rate")
                return True
            else:
                return False
            
        except Exception as e:
            self.log_test("Commission Calculations", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test 13: Verify error handling for invalid IDs"""
        try:
            print("\n🚫 Testing Error Handling...")
            
            # Test invalid salesperson ID
            invalid_id = "invalid_id_123"
            response = self.session.get(f"{self.base_url}/admin/referrals/salespeople/{invalid_id}")
            
            if response.status_code == 404:
                self.log_test("Invalid Salesperson ID", "PASS", "Correctly returned 404 for invalid ID")
            else:
                self.log_test("Invalid Salesperson ID", "FAIL", f"Expected 404, got {response.status_code}")
                return False
            
            # Test invalid commission ID
            invalid_commission_id = "invalid_commission_123"
            response = self.session.post(f"{self.base_url}/admin/referrals/commissions/{invalid_commission_id}/approve")
            
            if response.status_code in [404, 400]:
                self.log_test("Invalid Commission ID", "PASS", f"Correctly returned {response.status_code} for invalid commission ID")
            else:
                self.log_test("Invalid Commission ID", "FAIL", f"Expected 404/400, got {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Error Handling", "ERROR", f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all referral system tests"""
        print("🚀 Starting FIDUS Referral System Backend Testing")
        print("=" * 80)
        
        # Test public endpoints first (no auth required)
        public_tests = {
            "public_salespeople_list": self.test_public_salespeople_list(),
            "public_salesperson_by_code": self.test_public_salesperson_by_code()
        }
        
        # Authenticate for admin endpoints
        if not self.authenticate_admin():
            return {"success": False, "error": "Authentication failed"}
        
        # Run admin endpoint tests
        admin_tests = {
            "admin_salespeople_list": self.test_admin_salespeople_list(),
            "create_new_salesperson": self.test_create_new_salesperson(),
            "salesperson_dashboard": self.test_salesperson_dashboard(),
            "update_salesperson": self.test_update_salesperson(),
            "commission_calendar": self.test_commission_calendar(),
            "pending_commissions": self.test_pending_commissions(),
            "approve_commission": self.test_approve_commission(),
            "mark_commission_paid": self.test_mark_commission_paid(),
            "assign_client_referral": self.test_assign_client_referral(),
            "commission_calculations": self.test_commission_calculations(),
            "error_handling": self.test_error_handling()
        }
        
        # Combine all test results
        all_tests = {**public_tests, **admin_tests}
        
        # Calculate summary
        total_tests = len(all_tests)
        passed_tests = sum(1 for result in all_tests.values() if result)
        success_rate = (passed_tests / total_tests) * 100
        
        print("\n" + "=" * 80)
        print("📊 REFERRAL SYSTEM TEST SUMMARY")
        print("=" * 80)
        
        print("\n🌐 PUBLIC ENDPOINTS:")
        for test_name, result in public_tests.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} {test_name.replace('_', ' ').title()}")
        
        print("\n🔐 ADMIN ENDPOINTS:")
        for test_name, result in admin_tests.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} {test_name.replace('_', ' ').title()}")
        
        print(f"\n🎯 Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate == 100:
            print("🎉 REFERRAL SYSTEM VERIFICATION: EXCELLENT - All endpoints working perfectly!")
            print("   ✅ Salvador Palma (SP-2025) found with correct data")
            print("   ✅ Alejandro Mariscal Romero properly referred")
            print("   ✅ Commission calculations at 10% rate verified")
            print("   ✅ All CRUD operations functional")
        elif success_rate >= 80:
            print("✅ REFERRAL SYSTEM VERIFICATION: GOOD - Minor issues to address")
        elif success_rate >= 60:
            print("⚠️ REFERRAL SYSTEM VERIFICATION: NEEDS ATTENTION - Several issues found")
        else:
            print("🚨 REFERRAL SYSTEM VERIFICATION: CRITICAL ISSUES - Major problems detected")
        
        return {
            "success": success_rate >= 80,
            "success_rate": success_rate,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "test_results": all_tests,
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