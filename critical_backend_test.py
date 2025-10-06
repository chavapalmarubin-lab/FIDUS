#!/usr/bin/env python3
"""
FIDUS Critical Backend Testing Script
Focus on user-priority flows as requested in review:
1. Client Registration → Admin Leads Flow
2. Investment Creation Data Consistency 
3. Financial Calculations Flow
4. Core Authentication & User Management
5. Database Integration
"""

import requests
import sys
from datetime import datetime
import json

class FidusCriticalTester:
    def __init__(self, base_url="https://tradehub-mt5.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.client_user = None
        self.admin_user = None
        self.created_investment_id = None
        self.test_client_id = None
        
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
                    print(f"   Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Non-dict response'}")
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

    # ===============================================================================
    # 1. CORE AUTHENTICATION & USER MANAGEMENT TESTING
    # ===============================================================================
    
    def test_client_login(self):
        """Test client login functionality"""
        success, response = self.run_test(
            "Client Login (client1/password123)",
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
            self.test_client_id = response.get('id')
            print(f"   ✅ Client logged in: {response.get('name', 'Unknown')} (ID: {self.test_client_id})")
        return success

    def test_admin_login(self):
        """Test admin login functionality"""
        success, response = self.run_test(
            "Admin Login (admin/password123)",
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
            print(f"   ✅ Admin logged in: {response.get('name', 'Unknown')}")
        return success

    # ===============================================================================
    # 2. CLIENT REGISTRATION → ADMIN LEADS FLOW TESTING
    # ===============================================================================
    
    def test_client_registration_flow(self):
        """Test if new client registrations appear in admin CRM leads"""
        print("\n🎯 TESTING CLIENT REGISTRATION → ADMIN LEADS FLOW")
        
        # Step 1: Check current prospects count
        success, initial_response = self.run_test(
            "Get Initial CRM Prospects Count",
            "GET",
            "api/crm/prospects",
            200
        )
        
        if not success:
            return False
            
        initial_count = len(initial_response.get('prospects', []))
        print(f"   Initial prospects count: {initial_count}")
        
        # Step 2: Create a new prospect (simulating client registration)
        test_prospect = {
            "name": "Test Registration Client",
            "email": "test.registration@fidus.com",
            "phone": "+1-555-TEST",
            "notes": "Created via registration flow test"
        }
        
        success, create_response = self.run_test(
            "Create New Prospect (Simulating Registration)",
            "POST",
            "api/crm/prospects",
            200,
            data=test_prospect
        )
        
        if not success:
            return False
            
        prospect_id = create_response.get('prospect_id')
        print(f"   ✅ New prospect created: {prospect_id}")
        
        # Step 3: Verify prospect appears in admin leads
        success, final_response = self.run_test(
            "Verify Prospect Appears in Admin Leads",
            "GET",
            "api/crm/prospects",
            200
        )
        
        if not success:
            return False
            
        final_count = len(final_response.get('prospects', []))
        print(f"   Final prospects count: {final_count}")
        
        # Check if the new prospect is in the list
        prospects = final_response.get('prospects', [])
        found_prospect = None
        for prospect in prospects:
            if prospect.get('email') == test_prospect['email']:
                found_prospect = prospect
                break
                
        if found_prospect:
            print(f"   ✅ REGISTRATION → LEADS FLOW WORKING: New prospect found in admin leads")
            print(f"   Prospect details: {found_prospect.get('name')} - {found_prospect.get('stage')}")
            return True
        else:
            print(f"   ❌ REGISTRATION → LEADS FLOW BROKEN: New prospect not found in admin leads")
            return False

    # ===============================================================================
    # 3. INVESTMENT CREATION DATA CONSISTENCY TESTING
    # ===============================================================================
    
    def test_investment_creation_data_consistency(self):
        """Test admin-client data consistency issue where admin shows 0 clients despite having investments"""
        print("\n🎯 TESTING INVESTMENT CREATION DATA CONSISTENCY")
        
        if not self.test_client_id:
            print("❌ No test client available for investment creation")
            return False
            
        # Step 1: Check admin investment overview BEFORE creating investment
        success, admin_before = self.run_test(
            "Admin Investment Overview (BEFORE)",
            "GET",
            "api/investments/admin/overview",
            200
        )
        
        if success:
            total_aum_before = admin_before.get('total_aum', 0)
            clients_array_before = admin_before.get('clients', [])
            total_clients_before = admin_before.get('total_clients', 0)
            print(f"   BEFORE - Total AUM: ${total_aum_before:,.2f}")
            print(f"   BEFORE - Clients array length: {len(clients_array_before)}")
            print(f"   BEFORE - Total clients count: {total_clients_before}")
        
        # Step 2: Create a new investment
        investment_data = {
            "client_id": self.test_client_id,
            "fund_code": "CORE",
            "amount": 25000.0,
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
            return False
            
        self.created_investment_id = investment_response.get('investment_id')
        print(f"   ✅ Investment created: {self.created_investment_id}")
        
        # Step 3: Check client investment view
        success, client_response = self.run_test(
            "Client Investment Portfolio View",
            "GET",
            f"api/investments/client/{self.test_client_id}",
            200
        )
        
        if success:
            client_investments = client_response.get('investments', [])
            client_portfolio_stats = client_response.get('portfolio_statistics', {})
            print(f"   CLIENT VIEW - Investments count: {len(client_investments)}")
            print(f"   CLIENT VIEW - Total invested: ${client_portfolio_stats.get('total_invested', 0):,.2f}")
            print(f"   CLIENT VIEW - Current value: ${client_portfolio_stats.get('current_value', 0):,.2f}")
        
        # Step 4: Check admin investment overview AFTER creating investment
        success, admin_after = self.run_test(
            "Admin Investment Overview (AFTER)",
            "GET",
            "api/investments/admin/overview",
            200
        )
        
        if not success:
            return False
            
        total_aum_after = admin_after.get('total_aum', 0)
        clients_array_after = admin_after.get('clients', [])
        total_clients_after = admin_after.get('total_clients', 0)
        
        print(f"   AFTER - Total AUM: ${total_aum_after:,.2f}")
        print(f"   AFTER - Clients array length: {len(clients_array_after)}")
        print(f"   AFTER - Total clients count: {total_clients_after}")
        
        # Step 5: Analyze data consistency
        aum_increased = total_aum_after > total_aum_before
        clients_array_populated = len(clients_array_after) > 0
        
        print(f"\n   📊 DATA CONSISTENCY ANALYSIS:")
        print(f"   AUM increased: {aum_increased} (${total_aum_before:,.2f} → ${total_aum_after:,.2f})")
        print(f"   Clients array populated: {clients_array_populated} ({len(clients_array_before)} → {len(clients_array_after)})")
        
        if aum_increased and clients_array_populated:
            print(f"   ✅ DATA CONSISTENCY WORKING: Admin dashboard shows correct client data")
            return True
        elif aum_increased and not clients_array_populated:
            print(f"   ❌ DATA CONSISTENCY ISSUE CONFIRMED: AUM updated but clients array empty")
            print(f"   🚨 CRITICAL BUG: Admin dashboard shows total AUM but 0 clients")
            return False
        else:
            print(f"   ❌ INVESTMENT CREATION ISSUE: AUM not updated properly")
            return False

    # ===============================================================================
    # 4. FINANCIAL CALCULATIONS FLOW TESTING
    # ===============================================================================
    
    def test_financial_calculations_flow(self):
        """Test complete financial calculation chain from investment creation to portfolio updates"""
        print("\n🎯 TESTING FINANCIAL CALCULATIONS FLOW")
        
        if not self.created_investment_id:
            print("❌ No investment available for financial calculations testing")
            return False
            
        # Step 1: Test fund configuration and interest rates
        success, fund_config = self.run_test(
            "Fund Configuration & Interest Rates",
            "GET",
            "api/investments/funds/config",
            200
        )
        
        if success:
            funds = fund_config.get('funds', [])
            print(f"   Available funds: {len(funds)}")
            
            for fund in funds:
                fund_code = fund.get('fund_code')
                interest_rate = fund.get('interest_rate')
                minimum_investment = fund.get('minimum_investment')
                
                print(f"   {fund_code}: {interest_rate}% monthly, min ${minimum_investment:,.2f}")
                
                # Check for None interest rates (critical issue)
                if interest_rate is None:
                    print(f"   ❌ CRITICAL: {fund_code} has None interest rate!")
                    return False
                    
        # Step 2: Test investment projections
        success, projections = self.run_test(
            "Investment Projections & Timeline",
            "GET",
            f"api/investments/{self.created_investment_id}/projections",
            200
        )
        
        if success:
            projected_payments = projections.get('projected_payments', [])
            total_projected_interest = projections.get('total_projected_interest', 0)
            final_value = projections.get('final_value', 0)
            
            print(f"   Projected payments: {len(projected_payments)} months")
            print(f"   Total projected interest: ${total_projected_interest:,.2f}")
            print(f"   Final projected value: ${final_value:,.2f}")
            
            # Verify calculations make sense
            if len(projected_payments) > 0 and total_projected_interest > 0:
                print(f"   ✅ Financial projections calculated correctly")
            else:
                print(f"   ❌ Financial projections calculation issue")
                return False
                
        # Step 3: Test cash flow calculations
        success, cash_flows = self.run_test(
            "Client Cash Flow History",
            "GET",
            f"api/crm/client/{self.test_client_id}/capital-flows",
            200
        )
        
        if success:
            flows = cash_flows.get('capital_flows', [])
            summary = cash_flows.get('summary', {})
            
            print(f"   Capital flows: {len(flows)}")
            print(f"   Total subscriptions: ${summary.get('total_subscriptions', 0):,.2f}")
            print(f"   Total redemptions: ${summary.get('total_redemptions', 0):,.2f}")
            print(f"   Net flow: ${summary.get('net_flow', 0):,.2f}")
            
        return True

    # ===============================================================================
    # 5. DATABASE INTEGRATION TESTING
    # ===============================================================================
    
    def test_database_integration(self):
        """Verify the application is using real MongoDB data instead of mock data"""
        print("\n🎯 TESTING DATABASE INTEGRATION")
        
        # Step 1: Test client data persistence
        if not self.test_client_id:
            print("❌ No test client available for database testing")
            return False
            
        success, client_data = self.run_test(
            "Client Data Persistence",
            "GET",
            f"api/client/{self.test_client_id}/data",
            200
        )
        
        if success:
            balance = client_data.get('balance', {})
            transactions = client_data.get('transactions', [])
            monthly_statement = client_data.get('monthly_statement', {})
            
            print(f"   Client balance data: {balance}")
            print(f"   Transactions count: {len(transactions)}")
            print(f"   Monthly statement: {monthly_statement}")
            
            # Check if data looks real vs mock
            total_balance = balance.get('total_balance', 0)
            if total_balance > 0:
                print(f"   ✅ Real balance data found: ${total_balance:,.2f}")
            else:
                print(f"   ⚠️  Zero balance - may be using mock data or clean start")
                
        # Step 2: Test investment data persistence
        if self.created_investment_id:
            success, investment_data = self.run_test(
                "Investment Data Persistence",
                "GET",
                f"api/investments/client/{self.test_client_id}",
                200
            )
            
            if success:
                investments = investment_data.get('investments', [])
                if len(investments) > 0:
                    print(f"   ✅ Investment data persisted: {len(investments)} investments found")
                    
                    # Check investment details
                    for inv in investments:
                        print(f"   Investment: {inv.get('fund_code')} - ${inv.get('principal_amount', 0):,.2f}")
                else:
                    print(f"   ❌ No investment data found - database persistence issue")
                    return False
                    
        # Step 3: Test admin data aggregation
        success, admin_data = self.run_test(
            "Admin Data Aggregation",
            "GET",
            "api/admin/clients",
            200
        )
        
        if success:
            clients = admin_data.get('clients', [])
            print(f"   Admin client list: {len(clients)} clients")
            
            if len(clients) > 0:
                print(f"   ✅ Database integration working - client data aggregated")
                return True
            else:
                print(f"   ❌ No clients found - database integration issue")
                return False
                
        return False

    # ===============================================================================
    # MAIN TEST EXECUTION
    # ===============================================================================
    
    def run_critical_tests(self):
        """Run all critical tests focusing on user-priority flows"""
        print("=" * 80)
        print("🚀 FIDUS CRITICAL BACKEND TESTING - USER PRIORITY FLOWS")
        print("=" * 80)
        
        # Test 1: Core Authentication
        print("\n1️⃣ CORE AUTHENTICATION & USER MANAGEMENT")
        auth_client = self.test_client_login()
        auth_admin = self.test_admin_login()
        
        if not (auth_client and auth_admin):
            print("❌ CRITICAL: Authentication system not working - cannot proceed with other tests")
            return False
            
        # Test 2: Client Registration → Admin Leads Flow
        print("\n2️⃣ CLIENT REGISTRATION → ADMIN LEADS FLOW")
        registration_flow = self.test_client_registration_flow()
        
        # Test 3: Investment Creation Data Consistency
        print("\n3️⃣ INVESTMENT CREATION DATA CONSISTENCY")
        data_consistency = self.test_investment_creation_data_consistency()
        
        # Test 4: Financial Calculations Flow
        print("\n4️⃣ FINANCIAL CALCULATIONS FLOW")
        financial_calculations = self.test_financial_calculations_flow()
        
        # Test 5: Database Integration
        print("\n5️⃣ DATABASE INTEGRATION")
        database_integration = self.test_database_integration()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 CRITICAL TESTING SUMMARY")
        print("=" * 80)
        
        results = {
            "Authentication & User Management": auth_client and auth_admin,
            "Client Registration → Admin Leads Flow": registration_flow,
            "Investment Creation Data Consistency": data_consistency,
            "Financial Calculations Flow": financial_calculations,
            "Database Integration": database_integration
        }
        
        for test_name, result in results.items():
            status = "✅ WORKING" if result else "❌ FAILING"
            print(f"{status}: {test_name}")
            
        total_passed = sum(1 for result in results.values() if result)
        total_tests = len(results)
        
        print(f"\nOverall Results: {total_passed}/{total_tests} critical flows working")
        print(f"Success Rate: {(total_passed/total_tests)*100:.1f}%")
        
        if total_passed == total_tests:
            print("🎉 ALL CRITICAL FLOWS WORKING - SYSTEM READY")
        else:
            print("🚨 CRITICAL ISSUES FOUND - REQUIRES IMMEDIATE ATTENTION")
            
        return total_passed == total_tests

def main():
    """Main execution function"""
    tester = FidusCriticalTester()
    
    try:
        success = tester.run_critical_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Testing failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()