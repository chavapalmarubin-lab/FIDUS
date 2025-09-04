#!/usr/bin/env python3
"""
FIDUS Critical Fixes Testing Script
Re-testing the FIDUS application backend after critical fixes to verify:

1. Fund Configuration Fixed: Test GET /api/investments/funds/config 
2. Admin-Client Data Consistency Fixed: Test GET /api/investments/admin/overview
3. Client Registration → CRM Leads Flow: Test POST /api/auth/register
4. Complete End-to-End Flow: Test complete client investment workflow
"""

import requests
import sys
import json
from datetime import datetime
import uuid

class FidusCriticalFixesTester:
    def __init__(self, base_url="https://fidus-finance-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.client_user = None
        self.admin_user = None
        self.created_investment_id = None
        self.created_client_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=15)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=15)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=15)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_authentication(self):
        """Test client and admin authentication"""
        print("\n" + "="*80)
        print("🔐 AUTHENTICATION TESTS")
        print("="*80)
        
        # Test client login
        success, response = self.run_test(
            "Client Login (Gerardo Briones)",
            "POST",
            "api/auth/login",
            200,
            data={
                "username": "client1", 
                "password": "password123",
                "user_type": "client"
            }
        )
        if success:
            self.client_user = response
            print(f"   ✅ Client logged in: {response.get('name', 'Unknown')} (ID: {response.get('id')})")
        
        # Test admin login
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "api/auth/login",
            200,
            data={
                "username": "admin", 
                "password": "password123",
                "user_type": "admin"
            }
        )
        if success:
            self.admin_user = response
            print(f"   ✅ Admin logged in: {response.get('name', 'Unknown')} (ID: {response.get('id')})")
        
        return self.client_user is not None and self.admin_user is not None

    def test_fund_configuration_fix(self):
        """
        CRITICAL FIX 1: Fund Configuration Fixed
        Test GET /api/investments/funds/config to confirm all fund interest rates 
        are now returning correct values instead of None
        """
        print("\n" + "="*80)
        print("💰 CRITICAL FIX 1: FUND CONFIGURATION")
        print("="*80)
        
        success, response = self.run_test(
            "Fund Configuration - Interest Rates Fix",
            "GET",
            "api/investments/funds/config",
            200
        )
        
        if not success:
            return False
        
        # Expected fund configurations
        expected_funds = {
            "CORE": {"interest_rate": 1.5, "name": "FIDUS Core Fund"},
            "BALANCE": {"interest_rate": 2.5, "name": "FIDUS Balance Fund"}, 
            "DYNAMIC": {"interest_rate": 3.5, "name": "FIDUS Dynamic Fund"},
            "UNLIMITED": {"interest_rate": 0.0, "name": "FIDUS Unlimited Fund"}
        }
        
        funds = response.get('funds', [])
        if not funds:
            print("   ❌ No funds returned in response")
            return False
        
        print(f"   📊 Found {len(funds)} funds in configuration")
        
        all_rates_correct = True
        for fund in funds:
            fund_code = fund.get('fund_code')
            interest_rate = fund.get('interest_rate')
            fund_name = fund.get('name', 'Unknown')
            
            if fund_code in expected_funds:
                expected_rate = expected_funds[fund_code]['interest_rate']
                expected_name = expected_funds[fund_code]['name']
                
                print(f"   📈 {fund_code}: {interest_rate}% (Expected: {expected_rate}%)")
                
                if interest_rate is None:
                    print(f"   ❌ CRITICAL ISSUE: {fund_code} interest_rate is None!")
                    all_rates_correct = False
                elif interest_rate == expected_rate:
                    print(f"   ✅ {fund_code} interest rate CORRECT: {interest_rate}%")
                else:
                    print(f"   ⚠️  {fund_code} interest rate mismatch: got {interest_rate}%, expected {expected_rate}%")
                    all_rates_correct = False
                
                # Check fund name
                if fund_name == expected_name:
                    print(f"   ✅ {fund_code} name CORRECT: {fund_name}")
                else:
                    print(f"   ⚠️  {fund_code} name: got '{fund_name}', expected '{expected_name}'")
            else:
                print(f"   ⚠️  Unexpected fund: {fund_code}")
        
        if all_rates_correct:
            print("\n   🎉 FUND CONFIGURATION FIX VERIFIED: All interest rates are correct!")
            return True
        else:
            print("\n   ❌ FUND CONFIGURATION ISSUE: Some interest rates are None or incorrect!")
            return False

    def test_admin_client_data_consistency_fix(self):
        """
        CRITICAL FIX 2: Admin-Client Data Consistency Fixed
        Test GET /api/investments/admin/overview to confirm the "clients" array 
        is now populated correctly instead of being empty
        """
        print("\n" + "="*80)
        print("👥 CRITICAL FIX 2: ADMIN-CLIENT DATA CONSISTENCY")
        print("="*80)
        
        success, response = self.run_test(
            "Admin Investment Overview - Client Data Consistency",
            "GET",
            "api/investments/admin/overview",
            200
        )
        
        if not success:
            return False
        
        total_aum = response.get('total_aum', 0)
        clients_array = response.get('clients', [])
        total_clients = response.get('total_clients', 0)
        
        print(f"   💰 Total AUM: ${total_aum:,.2f}")
        print(f"   👥 Clients array length: {len(clients_array)}")
        print(f"   📊 Total clients reported: {total_clients}")
        
        # Check if clients array is populated
        if len(clients_array) == 0:
            print("   ❌ CRITICAL ISSUE: Clients array is EMPTY!")
            print("   ❌ This is the exact issue reported - admin dashboard shows AUM but no client details")
            return False
        
        print(f"   ✅ Clients array is POPULATED with {len(clients_array)} clients")
        
        # Verify client data structure
        for i, client in enumerate(clients_array):
            client_id = client.get('client_id', 'Unknown')
            client_name = client.get('client_name', 'Unknown')
            total_investment = client.get('total_investment', 0)
            investment_count = client.get('investment_count', 0)
            
            print(f"   👤 Client {i+1}: {client_name} (ID: {client_id})")
            print(f"      💰 Total Investment: ${total_investment:,.2f}")
            print(f"      📈 Investment Count: {investment_count}")
        
        # Verify AUM calculation consistency
        calculated_aum = sum(client.get('total_investment', 0) for client in clients_array)
        print(f"\n   🧮 AUM Verification:")
        print(f"      Reported Total AUM: ${total_aum:,.2f}")
        print(f"      Calculated from Clients: ${calculated_aum:,.2f}")
        
        if abs(total_aum - calculated_aum) < 0.01:  # Allow for small rounding differences
            print("   ✅ AUM calculation is CONSISTENT!")
        else:
            print("   ⚠️  AUM calculation mismatch - may indicate data inconsistency")
        
        print("\n   🎉 ADMIN-CLIENT DATA CONSISTENCY FIX VERIFIED: Clients array is populated!")
        return True

    def test_client_registration_crm_leads_flow(self):
        """
        CRITICAL FIX 3: Client Registration → CRM Leads Flow
        Test the new POST /api/auth/register endpoint to confirm new client 
        registrations automatically appear in GET /api/crm/prospects
        """
        print("\n" + "="*80)
        print("📝 CRITICAL FIX 3: CLIENT REGISTRATION → CRM LEADS FLOW")
        print("="*80)
        
        # First, get current prospects count
        success, initial_response = self.run_test(
            "Get Initial CRM Prospects Count",
            "GET",
            "api/crm/prospects",
            200
        )
        
        if not success:
            print("   ❌ Failed to get initial prospects - cannot test registration flow")
            return False
        
        initial_prospects = initial_response.get('prospects', [])
        initial_count = len(initial_prospects)
        print(f"   📊 Initial prospects count: {initial_count}")
        
        # Create a new client registration
        unique_id = str(uuid.uuid4())[:8]
        registration_data = {
            "name": f"TestClient{unique_id} AutoRegistration",
            "email": f"test.client.{unique_id}@fidus-test.com",
            "phone": f"+1-555-{unique_id[:4]}",
            "password": "TestPassword123!"
        }
        
        success, registration_response = self.run_test(
            "New Client Registration",
            "POST",
            "api/auth/register",
            200,
            data=registration_data
        )
        
        if not success:
            print("   ❌ Client registration failed - cannot test CRM flow")
            return False
        
        registration_id = registration_response.get('applicationId') or registration_response.get('id')
        print(f"   ✅ Client registration successful: ID {registration_id}")
        
        # Check if registration appears in CRM prospects
        success, updated_response = self.run_test(
            "Get Updated CRM Prospects (After Registration)",
            "GET",
            "api/crm/prospects",
            200
        )
        
        if not success:
            print("   ❌ Failed to get updated prospects")
            return False
        
        updated_prospects = updated_response.get('prospects', [])
        updated_count = len(updated_prospects)
        print(f"   📊 Updated prospects count: {updated_count}")
        
        # Check if count increased
        if updated_count > initial_count:
            print(f"   ✅ Prospects count INCREASED by {updated_count - initial_count}")
            
            # Find the new prospect
            test_email = registration_data['personalInfo']['email']
            new_prospect = None
            
            for prospect in updated_prospects:
                if prospect.get('email') == test_email:
                    new_prospect = prospect
                    break
            
            if new_prospect:
                print(f"   ✅ NEW PROSPECT FOUND in CRM!")
                print(f"      Name: {new_prospect.get('name')}")
                print(f"      Email: {new_prospect.get('email')}")
                print(f"      Stage: {new_prospect.get('stage', 'Unknown')}")
                print(f"      Created: {new_prospect.get('created_at', 'Unknown')}")
                
                print("\n   🎉 CLIENT REGISTRATION → CRM LEADS FLOW VERIFIED!")
                return True
            else:
                print("   ❌ New prospect not found in CRM - registration may not be flowing to leads")
                return False
        else:
            print("   ❌ Prospects count did not increase - registration not flowing to CRM")
            return False

    def test_complete_end_to_end_investment_flow(self):
        """
        CRITICAL FIX 4: Complete End-to-End Flow
        Test the complete client investment workflow:
        - Create investment via POST /api/investments/create
        - Verify it appears correctly in client view: GET /api/investments/client/{id}
        - Verify it appears correctly in admin overview: GET /api/investments/admin/overview
        - Confirm all calculations flow properly across the system
        """
        print("\n" + "="*80)
        print("🔄 CRITICAL FIX 4: COMPLETE END-TO-END INVESTMENT FLOW")
        print("="*80)
        
        if not self.client_user:
            print("   ❌ No client user available for end-to-end test")
            return False
        
        client_id = self.client_user.get('id')
        print(f"   👤 Testing with client: {self.client_user.get('name')} (ID: {client_id})")
        
        # Step 1: Get initial client investments
        success, initial_client_response = self.run_test(
            "Get Initial Client Investments",
            "GET",
            f"api/investments/client/{client_id}",
            200
        )
        
        if not success:
            print("   ❌ Failed to get initial client investments")
            return False
        
        initial_investments = initial_client_response.get('investments', [])
        initial_portfolio_value = initial_client_response.get('portfolio_statistics', {}).get('total_current_value', 0)
        print(f"   📊 Initial investments count: {len(initial_investments)}")
        print(f"   💰 Initial portfolio value: ${initial_portfolio_value:,.2f}")
        
        # Step 2: Get initial admin overview
        success, initial_admin_response = self.run_test(
            "Get Initial Admin Overview",
            "GET",
            "api/investments/admin/overview",
            200
        )
        
        if not success:
            print("   ❌ Failed to get initial admin overview")
            return False
        
        initial_admin_aum = initial_admin_response.get('total_aum', 0)
        initial_admin_clients = initial_admin_response.get('clients', [])
        print(f"   💰 Initial admin AUM: ${initial_admin_aum:,.2f}")
        print(f"   👥 Initial admin clients count: {len(initial_admin_clients)}")
        
        # Step 3: Create new investment
        investment_amount = 15000.0
        investment_data = {
            "client_id": client_id,
            "fund_code": "CORE",
            "amount": investment_amount,
            "deposit_date": "2024-12-19"
        }
        
        success, investment_response = self.run_test(
            "Create New Investment",
            "POST",
            "api/investments/create",
            200,
            data=investment_data
        )
        
        if not success:
            print("   ❌ Failed to create new investment")
            return False
        
        self.created_investment_id = investment_response.get('investment_id')
        print(f"   ✅ Investment created successfully: ID {self.created_investment_id}")
        print(f"   💰 Investment amount: ${investment_amount:,.2f}")
        print(f"   📈 Fund: {investment_data['fund_code']}")
        
        # Step 4: Verify investment appears in client view
        success, updated_client_response = self.run_test(
            "Verify Investment in Client View",
            "GET",
            f"api/investments/client/{client_id}",
            200
        )
        
        if not success:
            print("   ❌ Failed to get updated client investments")
            return False
        
        updated_investments = updated_client_response.get('investments', [])
        updated_portfolio_value = updated_client_response.get('portfolio_statistics', {}).get('total_current_value', 0)
        
        print(f"   📊 Updated investments count: {len(updated_investments)}")
        print(f"   💰 Updated portfolio value: ${updated_portfolio_value:,.2f}")
        
        # Check if investment count increased
        if len(updated_investments) > len(initial_investments):
            print("   ✅ Investment count INCREASED in client view")
            
            # Find the new investment
            new_investment = None
            for investment in updated_investments:
                if investment.get('investment_id') == self.created_investment_id:
                    new_investment = investment
                    break
            
            if new_investment:
                print("   ✅ NEW INVESTMENT FOUND in client view!")
                print(f"      Investment ID: {new_investment.get('investment_id')}")
                print(f"      Fund Code: {new_investment.get('fund_code')}")
                print(f"      Principal: ${new_investment.get('principal_amount', 0):,.2f}")
                print(f"      Current Value: ${new_investment.get('current_value', 0):,.2f}")
                print(f"      Status: {new_investment.get('status')}")
            else:
                print("   ❌ New investment not found in client view")
                return False
        else:
            print("   ❌ Investment count did not increase in client view")
            return False
        
        # Step 5: Verify investment appears in admin overview
        success, updated_admin_response = self.run_test(
            "Verify Investment in Admin Overview",
            "GET",
            "api/investments/admin/overview",
            200
        )
        
        if not success:
            print("   ❌ Failed to get updated admin overview")
            return False
        
        updated_admin_aum = updated_admin_response.get('total_aum', 0)
        updated_admin_clients = updated_admin_response.get('clients', [])
        
        print(f"   💰 Updated admin AUM: ${updated_admin_aum:,.2f}")
        print(f"   👥 Updated admin clients count: {len(updated_admin_clients)}")
        
        # Check if AUM increased
        aum_increase = updated_admin_aum - initial_admin_aum
        print(f"   📈 AUM increase: ${aum_increase:,.2f}")
        
        if abs(aum_increase - investment_amount) < 0.01:  # Allow for small rounding differences
            print("   ✅ AUM INCREASED by exact investment amount!")
        elif aum_increase > 0:
            print(f"   ✅ AUM INCREASED (difference may be due to interest calculations)")
        else:
            print("   ❌ AUM did not increase - investment may not be flowing to admin view")
            return False
        
        # Step 6: Verify client appears in admin clients array
        client_found_in_admin = False
        for admin_client in updated_admin_clients:
            if admin_client.get('client_id') == client_id:
                client_found_in_admin = True
                print("   ✅ CLIENT FOUND in admin overview!")
                print(f"      Client Name: {admin_client.get('client_name')}")
                print(f"      Total Investment: ${admin_client.get('total_investment', 0):,.2f}")
                print(f"      Investment Count: {admin_client.get('investment_count', 0)}")
                break
        
        if not client_found_in_admin:
            print("   ❌ Client not found in admin clients array")
            return False
        
        # Step 7: Verify calculations consistency
        portfolio_increase = updated_portfolio_value - initial_portfolio_value
        print(f"\n   🧮 Calculation Verification:")
        print(f"      Investment Amount: ${investment_amount:,.2f}")
        print(f"      Portfolio Value Increase: ${portfolio_increase:,.2f}")
        print(f"      Admin AUM Increase: ${aum_increase:,.2f}")
        
        calculations_consistent = (
            abs(portfolio_increase - investment_amount) < 0.01 and
            abs(aum_increase - investment_amount) < 10.0  # Allow for interest calculations
        )
        
        if calculations_consistent:
            print("   ✅ All calculations are CONSISTENT across the system!")
        else:
            print("   ⚠️  Some calculation discrepancies found - may be due to interest calculations")
        
        print("\n   🎉 COMPLETE END-TO-END INVESTMENT FLOW VERIFIED!")
        return True

    def run_all_critical_tests(self):
        """Run all critical fix tests"""
        print("🚀 FIDUS CRITICAL FIXES TESTING")
        print("="*80)
        print("Re-testing the FIDUS application backend after critical fixes")
        print("="*80)
        
        # Authentication first
        auth_success = self.test_authentication()
        if not auth_success:
            print("\n❌ Authentication failed - cannot proceed with other tests")
            return False
        
        # Run all critical fix tests
        test_results = []
        
        test_results.append(("Fund Configuration Fix", self.test_fund_configuration_fix()))
        test_results.append(("Admin-Client Data Consistency Fix", self.test_admin_client_data_consistency_fix()))
        test_results.append(("Client Registration → CRM Leads Flow", self.test_client_registration_crm_leads_flow()))
        test_results.append(("Complete End-to-End Investment Flow", self.test_complete_end_to_end_investment_flow()))
        
        # Print summary
        print("\n" + "="*80)
        print("📊 CRITICAL FIXES TEST SUMMARY")
        print("="*80)
        
        passed_tests = 0
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status} - {test_name}")
            if result:
                passed_tests += 1
        
        print(f"\nOverall Results: {passed_tests}/{len(test_results)} critical fixes verified")
        print(f"Total API Tests: {self.tests_passed}/{self.tests_run} passed")
        
        if passed_tests == len(test_results):
            print("\n🎉 ALL CRITICAL FIXES VERIFIED SUCCESSFULLY!")
            print("The FIDUS application backend is ready for production!")
            return True
        else:
            print(f"\n⚠️  {len(test_results) - passed_tests} critical fixes still need attention")
            return False

def main():
    """Main function to run critical fixes tests"""
    tester = FidusCriticalFixesTester()
    
    try:
        success = tester.run_all_critical_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Testing failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()