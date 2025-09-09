#!/usr/bin/env python3
"""
FIDUS Critical Data Flow Verification Test
Focus on specific backend endpoints that were showing zeros in frontend:

PRIORITY ENDPOINTS TO TEST:
1. GET /api/admin/portfolio-summary - Was showing $0 Total AUM in Fund Portfolio tab
2. GET /api/admin/funds-overview - Was showing Fund AUM $0, 0 Investors in CRM Dashboard  
3. GET /api/admin/cashflow/overview - Was showing all $0 values in Cash Flow tab
4. GET /api/investments/client/{client_id} - User reported client investment tab getting errors

TEST CLIENT DATA:
- Use client_001 (Gerardo Briones) who has investments in system
- Verify data consistency across all endpoints
- Confirm no more hardcoded zeros or empty client_investments dictionary usage
"""

import requests
import sys
from datetime import datetime
import json

class FidusDataFlowTester:
    def __init__(self, base_url="https://mt5-portal.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.client_user = None
        self.admin_user = None
        self.test_client_id = "client_001"  # Gerardo Briones
        self.critical_issues = []
        self.data_consistency_issues = []
        
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

    def test_authentication(self):
        """Test authentication for both client and admin"""
        print("\n🔐 AUTHENTICATION SETUP")
        
        # Test client login (Gerardo Briones)
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
            print(f"   ✅ Client logged in: {response.get('name', 'Unknown')} (ID: {response.get('id')})")
        else:
            self.critical_issues.append("Client authentication failed")
            return False

        # Test admin login
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
        else:
            self.critical_issues.append("Admin authentication failed")
            return False
            
        return True

    def test_client_investment_tab(self):
        """Test GET /api/investments/client/{client_id} - User reported client investment tab getting errors"""
        print("\n🎯 PRIORITY TEST 1: CLIENT INVESTMENT TAB")
        
        success, response = self.run_test(
            "Client Investment Portfolio (Gerardo Briones)",
            "GET",
            f"api/investments/client/{self.test_client_id}",
            200
        )
        
        if not success:
            self.critical_issues.append("Client investment tab endpoint failing")
            return False
            
        # Analyze response data
        investments = response.get('investments', [])
        portfolio_statistics = response.get('portfolio_statistics', {})
        
        print(f"   📊 ANALYSIS:")
        print(f"   Investments found: {len(investments)}")
        print(f"   Portfolio statistics: {portfolio_statistics}")
        
        if len(investments) == 0:
            self.data_consistency_issues.append("Client has no investments - expected Gerardo to have investments")
            print(f"   ⚠️  No investments found for Gerardo Briones")
            return False
            
        # Check investment details
        total_invested = 0
        total_current_value = 0
        
        for inv in investments:
            fund_code = inv.get('fund_code', 'Unknown')
            principal = inv.get('principal_amount', 0)
            current_value = inv.get('current_value', 0)
            
            print(f"   Investment: {fund_code} - Principal: ${principal:,.2f}, Current: ${current_value:,.2f}")
            total_invested += principal
            total_current_value += current_value
            
        print(f"   ✅ CLIENT INVESTMENT TAB WORKING: {len(investments)} investments, Total: ${total_current_value:,.2f}")
        return True

    def test_admin_portfolio_summary(self):
        """Test GET /api/admin/portfolio-summary - Was showing $0 Total AUM in Fund Portfolio tab"""
        print("\n🎯 PRIORITY TEST 2: ADMIN PORTFOLIO SUMMARY")
        
        success, response = self.run_test(
            "Admin Portfolio Summary",
            "GET",
            "api/admin/portfolio-summary",
            200
        )
        
        if not success:
            self.critical_issues.append("Admin portfolio summary endpoint failing")
            return False
            
        # Analyze AUM data
        aum = response.get('total_aum', 0)  # Fixed: correct field name
        allocation = response.get('allocation', {})
        ytd_return = response.get('ytd_return', 0)
        weekly_performance = response.get('weekly_performance', [])
        
        print(f"   📊 ANALYSIS:")
        print(f"   Total AUM: ${aum:,.2f}")
        print(f"   Allocation: {allocation}")
        print(f"   YTD Return: {ytd_return}%")
        print(f"   Weekly performance data points: {len(weekly_performance)}")
        
        if aum == 0:
            self.data_consistency_issues.append("Portfolio summary shows $0 AUM - should show real investment data")
            print(f"   ❌ CRITICAL ISSUE: Portfolio summary shows $0 Total AUM")
            return False
        else:
            print(f"   ✅ PORTFOLIO SUMMARY WORKING: Shows ${aum:,.2f} Total AUM")
            return True

    def test_admin_funds_overview(self):
        """Test GET /api/admin/funds-overview - Was showing Fund AUM $0, 0 Investors in CRM Dashboard"""
        print("\n🎯 PRIORITY TEST 3: ADMIN FUNDS OVERVIEW")
        
        success, response = self.run_test(
            "Admin Funds Overview",
            "GET",
            "api/admin/funds-overview",
            200
        )
        
        if not success:
            self.critical_issues.append("Admin funds overview endpoint failing")
            return False
            
        # Analyze funds data
        funds = response.get('funds', [])
        total_aum = response.get('total_aum', 0)
        total_investors = response.get('total_investors', 0)
        
        print(f"   📊 ANALYSIS:")
        print(f"   Total AUM: ${total_aum:,.2f}")
        print(f"   Total Investors: {total_investors}")
        print(f"   Funds count: {len(funds)}")
        
        # Check individual fund data
        zero_aum_funds = []
        zero_investor_funds = []
        
        for fund in funds:
            # Handle both dict and string fund objects
            if isinstance(fund, dict):
                fund_code = fund.get('fund_code', 'Unknown')
                fund_aum = fund.get('aum', 0)
                fund_investors = fund.get('total_investors', 0)
            else:
                # If fund is a string or other type, skip detailed analysis
                print(f"   Fund data type: {type(fund)} - {fund}")
                continue
            
            print(f"   Fund {fund_code}: AUM ${fund_aum:,.2f}, Investors: {fund_investors}")
            
            if fund_aum == 0:
                zero_aum_funds.append(fund_code)
            if fund_investors == 0:
                zero_investor_funds.append(fund_code)
                
        # Check for critical issues
        if total_aum == 0:
            self.data_consistency_issues.append("Funds overview shows $0 total AUM")
            print(f"   ❌ CRITICAL ISSUE: Funds overview shows $0 Total AUM")
            return False
            
        if total_investors == 0:
            self.data_consistency_issues.append("Funds overview shows 0 total investors")
            print(f"   ❌ CRITICAL ISSUE: Funds overview shows 0 Investors")
            return False
            
        if len(zero_aum_funds) > 0:
            print(f"   ⚠️  Funds with $0 AUM: {zero_aum_funds}")
            
        if len(zero_investor_funds) > 0:
            print(f"   ⚠️  Funds with 0 investors: {zero_investor_funds}")
            
        print(f"   ✅ FUNDS OVERVIEW WORKING: ${total_aum:,.2f} AUM, {total_investors} Investors")
        return True

    def test_admin_cashflow_overview(self):
        """Test GET /api/admin/cashflow/overview - Was showing all $0 values in Cash Flow tab"""
        print("\n🎯 PRIORITY TEST 4: ADMIN CASHFLOW OVERVIEW")
        
        success, response = self.run_test(
            "Admin Cashflow Overview",
            "GET",
            "api/admin/cashflow/overview",
            200
        )
        
        if not success:
            self.critical_issues.append("Admin cashflow overview endpoint failing")
            return False
            
        # Analyze cashflow data
        total_inflows = response.get('total_inflow', 0)  # Fixed: correct field name
        total_outflows = response.get('total_outflow', 0)  # Fixed: correct field name
        net_flow = response.get('net_cash_flow', 0)  # Fixed: correct field name
        monthly_flows = response.get('cash_flows', [])  # Fixed: correct field name
        
        print(f"   📊 ANALYSIS:")
        print(f"   Total Inflows: ${total_inflows:,.2f}")
        print(f"   Total Outflows: ${total_outflows:,.2f}")
        print(f"   Net Flow: ${net_flow:,.2f}")
        print(f"   Monthly flow data points: {len(monthly_flows)}")
        
        # Check for all zero values
        all_zero = (total_inflows == 0 and total_outflows == 0 and net_flow == 0)
        
        if all_zero:
            self.data_consistency_issues.append("Cashflow overview shows all $0 values")
            print(f"   ❌ CRITICAL ISSUE: Cashflow overview shows all $0 values")
            return False
        else:
            print(f"   ✅ CASHFLOW OVERVIEW WORKING: Shows real flow data")
            return True

    def test_data_consistency_across_endpoints(self):
        """Test data consistency across all endpoints"""
        print("\n🔄 DATA CONSISTENCY VERIFICATION")
        
        # Get data from all endpoints
        endpoints_data = {}
        
        # Client investment data
        success, client_data = self.run_test(
            "Client Investment Data for Consistency Check",
            "GET",
            f"api/investments/client/{self.test_client_id}",
            200
        )
        if success:
            endpoints_data['client_investments'] = client_data
            
        # Admin portfolio summary
        success, portfolio_data = self.run_test(
            "Portfolio Summary for Consistency Check",
            "GET",
            "api/admin/portfolio-summary",
            200
        )
        if success:
            endpoints_data['portfolio_summary'] = portfolio_data
            
        # Admin funds overview
        success, funds_data = self.run_test(
            "Funds Overview for Consistency Check",
            "GET",
            "api/admin/funds-overview",
            200
        )
        if success:
            endpoints_data['funds_overview'] = funds_data
            
        # Admin investment overview (additional check)
        success, admin_inv_data = self.run_test(
            "Admin Investment Overview for Consistency Check",
            "GET",
            "api/investments/admin/overview",
            200
        )
        if success:
            endpoints_data['admin_investments'] = admin_inv_data
            
        # Analyze consistency
        print(f"\n   📊 CROSS-ENDPOINT CONSISTENCY ANALYSIS:")
        
        # Extract AUM values from different endpoints
        client_total = 0
        if 'client_investments' in endpoints_data:
            client_investments = endpoints_data['client_investments'].get('investments', [])
            client_total = sum(inv.get('current_value', 0) for inv in client_investments)
            print(f"   Client total investment value: ${client_total:,.2f}")
            
        portfolio_aum = endpoints_data.get('portfolio_summary', {}).get('total_aum', 0)  # Fixed: correct field name
        print(f"   Portfolio summary AUM: ${portfolio_aum:,.2f}")
        
        funds_aum = endpoints_data.get('funds_overview', {}).get('total_aum', 0)
        print(f"   Funds overview AUM: ${funds_aum:,.2f}")
        
        admin_aum = endpoints_data.get('admin_investments', {}).get('total_aum', 0)
        print(f"   Admin investments AUM: ${admin_aum:,.2f}")
        
        # Check for consistency issues
        aum_values = [portfolio_aum, funds_aum, admin_aum]
        aum_values = [v for v in aum_values if v > 0]  # Filter out zeros
        
        if len(set(aum_values)) > 1:
            self.data_consistency_issues.append(f"Inconsistent AUM values across endpoints: {aum_values}")
            print(f"   ⚠️  INCONSISTENT AUM VALUES: {aum_values}")
            
        # Check client data appears in admin views
        admin_clients = endpoints_data.get('admin_investments', {}).get('clients', [])
        gerardo_found = any(client.get('client_id') == self.test_client_id for client in admin_clients)
        
        if not gerardo_found and client_total > 0:
            self.data_consistency_issues.append("Client has investments but doesn't appear in admin client list")
            print(f"   ❌ CONSISTENCY ISSUE: Gerardo has investments but not in admin client list")
            return False
        elif gerardo_found:
            print(f"   ✅ CONSISTENCY CHECK: Gerardo appears in admin client list")
            
        return True

    def run_critical_data_flow_tests(self):
        """Run all critical data flow tests"""
        print("=" * 80)
        print("🚀 FIDUS CRITICAL DATA FLOW VERIFICATION")
        print("Focus: Backend endpoints showing zeros in frontend")
        print("=" * 80)
        
        # Setup authentication
        if not self.test_authentication():
            print("❌ CRITICAL: Authentication failed - cannot proceed")
            return False
            
        # Run priority endpoint tests
        test_results = {}
        
        print("\n🎯 PRIORITY ENDPOINT TESTING")
        test_results['client_investment_tab'] = self.test_client_investment_tab()
        test_results['admin_portfolio_summary'] = self.test_admin_portfolio_summary()
        test_results['admin_funds_overview'] = self.test_admin_funds_overview()
        test_results['admin_cashflow_overview'] = self.test_admin_cashflow_overview()
        
        # Data consistency check
        print("\n🔄 DATA CONSISTENCY VERIFICATION")
        test_results['data_consistency'] = self.test_data_consistency_across_endpoints()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 CRITICAL DATA FLOW TEST RESULTS")
        print("=" * 80)
        
        for test_name, result in test_results.items():
            status = "✅ WORKING" if result else "❌ FAILING"
            print(f"{status}: {test_name.replace('_', ' ').title()}")
            
        # Critical issues summary
        if self.critical_issues:
            print(f"\n🚨 CRITICAL ISSUES FOUND:")
            for issue in self.critical_issues:
                print(f"   • {issue}")
                
        # Data consistency issues
        if self.data_consistency_issues:
            print(f"\n⚠️  DATA CONSISTENCY ISSUES:")
            for issue in self.data_consistency_issues:
                print(f"   • {issue}")
                
        total_passed = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        
        print(f"\nOverall Results: {total_passed}/{total_tests} endpoints working correctly")
        print(f"Success Rate: {(total_passed/total_tests)*100:.1f}%")
        
        if total_passed == total_tests and not self.critical_issues and not self.data_consistency_issues:
            print("🎉 ALL CRITICAL DATA FLOW ENDPOINTS WORKING - NO ZEROS DETECTED")
            return True
        else:
            print("🚨 CRITICAL DATA FLOW ISSUES DETECTED - FRONTEND ZEROS CONFIRMED")
            return False

def main():
    """Main execution function"""
    tester = FidusDataFlowTester()
    
    try:
        success = tester.run_critical_data_flow_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Testing failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()