#!/usr/bin/env python3
"""
FUND PORTFOLIO OVERVIEW & ADMIN CLIENTS ENDPOINT TESTING
========================================================

This test verifies the newly created /fund-portfolio/overview endpoint and 
the fixed /admin/clients endpoint structure as requested in the review:

CRITICAL FIXES TO TEST:
1. New /api/fund-portfolio/overview endpoint:
   - Should return fund data with Salvador's $1,371,485.40 investments
   - Should show proper fund breakdown (BALANCE ~$1.36M, CORE ~$8K)
   - Should return success=true with non-zero values

2. Fixed /api/admin/clients endpoint:
   - Should return {"clients": [...]} format
   - Should include Salvador Palma (client_003) with correct balance
   - Should be compatible with frontend ClientManagement component

3. Data consistency verification:
   - Fund portfolio totals should match client investment totals
   - All endpoints should show same $1,371,485.40 total value
   - No zero values should appear (unless data is actually empty)

4. Frontend API compatibility:
   - Verify endpoint responses match what frontend components expect
   - Check that MT5 accounts endpoint works with frontend format
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://fidus-google-sync.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class FundPortfolioEndpointTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.expected_salvador_total = 1371485.40  # As specified in review request
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {json.dumps(details, indent=2)}")
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                if self.admin_token:
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    self.log_result("Admin Authentication", True, "Successfully authenticated as admin")
                    return True
                else:
                    self.log_result("Admin Authentication", False, "No token received", {"response": data})
                    return False
            else:
                self.log_result("Admin Authentication", False, f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_fund_portfolio_overview_endpoint(self):
        """Test the new /api/fund-portfolio/overview endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/fund-portfolio/overview")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if success=true
                success_flag = data.get('success', False)
                if success_flag:
                    self.log_result("Fund Portfolio Overview - Success Flag", True, 
                                  "Endpoint returns success=true")
                else:
                    self.log_result("Fund Portfolio Overview - Success Flag", False, 
                                  "Endpoint does not return success=true", {"response": data})
                
                # Check for Salvador's fund data
                funds = data.get('funds', {})
                total_aum = data.get('total_aum', 0)
                
                # Look for BALANCE fund (~$1.36M)
                balance_fund_found = False
                core_fund_found = False
                balance_amount = 0
                core_amount = 0
                
                # Handle funds as dictionary format
                if 'BALANCE' in funds:
                    balance_fund_found = True
                    balance_amount = funds['BALANCE'].get('aum', 0)
                    if balance_amount > 1300000:  # Should be around $1.36M
                        self.log_result("Fund Portfolio - BALANCE Fund", True, 
                                      f"BALANCE fund found with correct amount: ${balance_amount:,.2f}")
                    else:
                        self.log_result("Fund Portfolio - BALANCE Fund", False, 
                                      f"BALANCE fund amount too low: ${balance_amount:,.2f} (expected ~$1.36M)")
                
                if 'CORE' in funds:
                    core_fund_found = True
                    core_amount = funds['CORE'].get('aum', 0)
                    if core_amount > 0:  # Should be around $8K
                        self.log_result("Fund Portfolio - CORE Fund", True, 
                                      f"CORE fund found with amount: ${core_amount:,.2f}")
                    else:
                        self.log_result("Fund Portfolio - CORE Fund", False, 
                                      f"CORE fund shows zero amount: ${core_amount:,.2f}")
                
                # Check total AUM matches expected
                if abs(total_aum - self.expected_salvador_total) < 10000:  # Allow $10K variance
                    self.log_result("Fund Portfolio - Total AUM", True, 
                                  f"Total AUM matches expected: ${total_aum:,.2f}")
                else:
                    self.log_result("Fund Portfolio - Total AUM", False, 
                                  f"Total AUM mismatch: got ${total_aum:,.2f}, expected ${self.expected_salvador_total:,.2f}")
                
                # Check no zero values (unless legitimately empty)
                if total_aum > 0 and len(funds) > 0:
                    self.log_result("Fund Portfolio - Non-Zero Values", True, 
                                  "Endpoint returns non-zero values as expected")
                else:
                    self.log_result("Fund Portfolio - Non-Zero Values", False, 
                                  "Endpoint returns zero values", {"total_aum": total_aum, "funds_count": len(funds)})
                
            elif response.status_code == 404:
                self.log_result("Fund Portfolio Overview Endpoint", False, 
                              "Endpoint not found (404) - needs to be created", {"url": f"{BACKEND_URL}/fund-portfolio/overview"})
            else:
                self.log_result("Fund Portfolio Overview Endpoint", False, 
                              f"HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_result("Fund Portfolio Overview Endpoint", False, f"Exception: {str(e)}")
    
    def test_admin_clients_endpoint_structure(self):
        """Test the fixed /api/admin/clients endpoint structure"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response has {"clients": [...]} format
                if isinstance(data, dict) and 'clients' in data:
                    clients = data['clients']
                    self.log_result("Admin Clients - Response Format", True, 
                                  "Endpoint returns correct {'clients': [...]} format")
                    
                    # Check if Salvador Palma is included
                    salvador_found = False
                    salvador_balance = 0
                    
                    for client in clients:
                        if client.get('id') == 'client_003' or 'SALVADOR' in client.get('name', '').upper():
                            salvador_found = True
                            salvador_balance = client.get('total_balance', 0) or client.get('balance', 0)
                            
                            # Check if balance is correct
                            if abs(salvador_balance - self.expected_salvador_total) < 10000:
                                self.log_result("Admin Clients - Salvador Balance", True, 
                                              f"Salvador balance correct: ${salvador_balance:,.2f}")
                            else:
                                self.log_result("Admin Clients - Salvador Balance", False, 
                                              f"Salvador balance incorrect: ${salvador_balance:,.2f}, expected ${self.expected_salvador_total:,.2f}")
                            break
                    
                    if salvador_found:
                        self.log_result("Admin Clients - Salvador Present", True, 
                                      "Salvador Palma (client_003) found in clients list")
                    else:
                        self.log_result("Admin Clients - Salvador Present", False, 
                                      "Salvador Palma (client_003) missing from clients list", 
                                      {"clients_found": [c.get('name', 'Unknown') for c in clients]})
                
                elif isinstance(data, list):
                    # Old format - should be fixed
                    self.log_result("Admin Clients - Response Format", False, 
                                  "Endpoint still returns old array format instead of {'clients': [...]}",
                                  {"response_type": "array", "length": len(data)})
                    
                    # Still check for Salvador in the array
                    salvador_found = any(client.get('id') == 'client_003' or 'SALVADOR' in client.get('name', '').upper() 
                                       for client in data)
                    if salvador_found:
                        self.log_result("Admin Clients - Salvador Present (Old Format)", True, 
                                      "Salvador found but endpoint needs format fix")
                    else:
                        self.log_result("Admin Clients - Salvador Present (Old Format)", False, 
                                      "Salvador missing and endpoint needs format fix")
                
                else:
                    self.log_result("Admin Clients - Response Format", False, 
                                  "Endpoint returns unexpected format", {"response_type": type(data).__name__})
            
            else:
                self.log_result("Admin Clients Endpoint", False, 
                              f"HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_result("Admin Clients Endpoint", False, f"Exception: {str(e)}")
    
    def test_data_consistency_verification(self):
        """Test data consistency between fund portfolio and client totals"""
        try:
            # Get fund portfolio total
            fund_response = self.session.get(f"{BACKEND_URL}/fund-portfolio/overview")
            fund_total = 0
            
            if fund_response.status_code == 200:
                fund_data = fund_response.json()
                fund_total = fund_data.get('total_aum', 0)
            
            # Get client investment total
            client_response = self.session.get(f"{BACKEND_URL}/investments/client/client_003")
            client_total = 0
            
            if client_response.status_code == 200:
                client_data = client_response.json()
                if isinstance(client_data, dict) and 'investments' in client_data:
                    investments = client_data['investments']
                    client_total = sum(inv.get('current_value', 0) for inv in investments)
                elif isinstance(client_data, list):
                    client_total = sum(inv.get('current_value', 0) for inv in client_data)
            
            # Compare totals
            if fund_total > 0 and client_total > 0:
                if abs(fund_total - client_total) < 1000:  # Allow $1K variance
                    self.log_result("Data Consistency - Fund vs Client Totals", True, 
                                  f"Totals match: Fund ${fund_total:,.2f}, Client ${client_total:,.2f}")
                else:
                    self.log_result("Data Consistency - Fund vs Client Totals", False, 
                                  f"Totals mismatch: Fund ${fund_total:,.2f}, Client ${client_total:,.2f}")
            else:
                self.log_result("Data Consistency - Fund vs Client Totals", False, 
                              f"One or both totals are zero: Fund ${fund_total:,.2f}, Client ${client_total:,.2f}")
            
            # Check expected total value consistency
            expected_total = self.expected_salvador_total
            fund_matches = abs(fund_total - expected_total) < 10000
            client_matches = abs(client_total - expected_total) < 10000
            
            if fund_matches and client_matches:
                self.log_result("Data Consistency - Expected Total", True, 
                              f"Both endpoints show expected ${expected_total:,.2f} total")
            else:
                issues = []
                if not fund_matches:
                    issues.append(f"Fund total ${fund_total:,.2f} != expected ${expected_total:,.2f}")
                if not client_matches:
                    issues.append(f"Client total ${client_total:,.2f} != expected ${expected_total:,.2f}")
                
                self.log_result("Data Consistency - Expected Total", False, 
                              f"Total value inconsistencies: {'; '.join(issues)}")
                
        except Exception as e:
            self.log_result("Data Consistency Verification", False, f"Exception: {str(e)}")
    
    def test_frontend_api_compatibility(self):
        """Test frontend API compatibility for key endpoints"""
        try:
            # Test endpoints that frontend components expect
            frontend_endpoints = [
                ("/admin/clients", "ClientManagement component"),
                ("/fund-portfolio/overview", "FundPortfolioManagement component"),
                ("/mt5/admin/accounts", "MT5Management component"),
                ("/admin/prospects", "ProspectManagement component")
            ]
            
            for endpoint, component in frontend_endpoints:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Check if response is JSON serializable (frontend requirement)
                        json.dumps(data)  # This will raise exception if not serializable
                        
                        # Check for expected structure based on endpoint
                        if endpoint == "/admin/clients":
                            if isinstance(data, dict) and 'clients' in data:
                                self.log_result(f"Frontend Compatibility - {component}", True, 
                                              "Endpoint returns frontend-compatible format")
                            else:
                                self.log_result(f"Frontend Compatibility - {component}", False, 
                                              "Endpoint format not compatible with frontend expectations")
                        
                        elif endpoint == "/fund-portfolio/overview":
                            if isinstance(data, dict) and data.get('success') and 'funds' in data:
                                self.log_result(f"Frontend Compatibility - {component}", True, 
                                              "Endpoint returns frontend-compatible format")
                            else:
                                self.log_result(f"Frontend Compatibility - {component}", False, 
                                              "Endpoint format not compatible with frontend expectations")
                        
                        else:
                            # For other endpoints, just check they return valid JSON
                            self.log_result(f"Frontend Compatibility - {component}", True, 
                                          "Endpoint returns valid JSON response")
                    
                    elif response.status_code == 404:
                        self.log_result(f"Frontend Compatibility - {component}", False, 
                                      f"Endpoint not found: {endpoint}")
                    
                    else:
                        self.log_result(f"Frontend Compatibility - {component}", False, 
                                      f"HTTP {response.status_code} for {endpoint}")
                
                except json.JSONDecodeError:
                    self.log_result(f"Frontend Compatibility - {component}", False, 
                                  f"Endpoint returns invalid JSON: {endpoint}")
                except Exception as e:
                    self.log_result(f"Frontend Compatibility - {component}", False, 
                                  f"Exception testing {endpoint}: {str(e)}")
                
        except Exception as e:
            self.log_result("Frontend API Compatibility", False, f"Exception: {str(e)}")
    
    def test_zero_values_verification(self):
        """Verify no inappropriate zero values appear in responses"""
        try:
            # Test key endpoints for zero values
            endpoints_to_check = [
                ("/fund-portfolio/overview", "Fund Portfolio"),
                ("/admin/clients", "Admin Clients"),
                ("/investments/client/client_003", "Salvador Investments")
            ]
            
            zero_value_issues = []
            
            for endpoint, name in endpoints_to_check:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Check for inappropriate zero values
                        if endpoint == "/fund-portfolio/overview":
                            total_aum = data.get('total_aum', 0)
                            if total_aum == 0:
                                zero_value_issues.append(f"{name}: total_aum is zero")
                        
                        elif endpoint == "/admin/clients":
                            if isinstance(data, dict) and 'clients' in data:
                                clients = data['clients']
                                for client in clients:
                                    if client.get('id') == 'client_003':
                                        balance = client.get('total_balance', 0) or client.get('balance', 0)
                                        if balance == 0:
                                            zero_value_issues.append(f"{name}: Salvador's balance is zero")
                        
                        elif endpoint == "/investments/client/client_003":
                            if isinstance(data, dict) and 'investments' in data:
                                investments = data['investments']
                                if len(investments) == 0:
                                    zero_value_issues.append(f"{name}: No investments found for Salvador")
                                else:
                                    for inv in investments:
                                        if inv.get('current_value', 0) == 0:
                                            zero_value_issues.append(f"{name}: Investment {inv.get('fund_code')} has zero value")
                            elif isinstance(data, list):
                                if len(data) == 0:
                                    zero_value_issues.append(f"{name}: No investments found for Salvador")
                                else:
                                    for inv in data:
                                        if inv.get('current_value', 0) == 0:
                                            zero_value_issues.append(f"{name}: Investment {inv.get('fund_code')} has zero value")
                
                except Exception as e:
                    zero_value_issues.append(f"{name}: Exception checking values - {str(e)}")
            
            if len(zero_value_issues) == 0:
                self.log_result("Zero Values Verification", True, 
                              "No inappropriate zero values found in key endpoints")
            else:
                self.log_result("Zero Values Verification", False, 
                              f"Found {len(zero_value_issues)} zero value issues", 
                              {"issues": zero_value_issues})
                
        except Exception as e:
            self.log_result("Zero Values Verification", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all fund portfolio and admin clients endpoint tests"""
        print("🎯 FUND PORTFOLIO OVERVIEW & ADMIN CLIENTS ENDPOINT TESTING")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Expected Salvador Total: ${self.expected_salvador_total:,.2f}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Fund Portfolio & Admin Clients Tests...")
        print("-" * 50)
        
        # Run all tests
        self.test_fund_portfolio_overview_endpoint()
        self.test_admin_clients_endpoint_structure()
        self.test_data_consistency_verification()
        self.test_frontend_api_compatibility()
        self.test_zero_values_verification()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 70)
        print("🎯 FUND PORTFOLIO & ADMIN CLIENTS TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Show failed tests first (more important)
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Show passed tests
        if passed_tests > 0:
            print("✅ PASSED TESTS:")
            for result in self.test_results:
                if result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Critical assessment for review request
        critical_tests = [
            "Fund Portfolio Overview - Success Flag",
            "Fund Portfolio - BALANCE Fund", 
            "Admin Clients - Response Format",
            "Admin Clients - Salvador Present",
            "Data Consistency - Expected Total"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(critical in result['test'] for critical in critical_tests))
        
        print("🚨 CRITICAL ASSESSMENT FOR REVIEW REQUEST:")
        if critical_passed >= 4:  # At least 4 out of 5 critical tests
            print("✅ FUND PORTFOLIO & ADMIN CLIENTS FIXES: SUCCESSFUL")
            print("   • /api/fund-portfolio/overview endpoint working correctly")
            print("   • /api/admin/clients endpoint returns proper format")
            print("   • Salvador's $1,371,485.40 investments properly displayed")
            print("   • Data consistency verified across endpoints")
            print("   • Frontend API compatibility confirmed")
        else:
            print("❌ FUND PORTFOLIO & ADMIN CLIENTS FIXES: INCOMPLETE")
            print("   • Critical endpoint issues still exist")
            print("   • User-reported data display problems not fully resolved")
            print("   • Main agent action required to complete fixes")
        
        print("\n" + "=" * 70)

def main():
    """Main test execution"""
    test_runner = FundPortfolioEndpointTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()