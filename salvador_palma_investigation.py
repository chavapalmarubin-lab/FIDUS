#!/usr/bin/env python3
"""
CRITICAL PRODUCTION BUG INVESTIGATION: Salvador Palma Investment Data Missing
=============================================================================

This script investigates the critical production bug where Salvador Palma's investments 
with MT5 account mappings are missing from the deployed FIDUS system.

Expected Data That Should Be Present:
- Salvador Palma client profile (client_003)
- BALANCE fund investment: $1,263,485.40
- MT5 Account Login: 9928326 (DooTechnology-Live)
- Current MT5 Balance: $1,837,934.05
- MT5 Performance data and historical tracking
"""

import requests
import sys
from datetime import datetime
import json

class SalvadorPalmaInvestigator:
    def __init__(self, base_url="https://auth-troubleshoot-14.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_issues = []
        self.admin_token = None
        
        # Expected Salvador Palma data
        self.expected_salvador_data = {
            "client_id": "client_003",
            "name": "SALVADOR PALMA", 
            "email": "chava@alyarglobal.com",
            "balance_investment": 1263485.40,
            "mt5_login": "9928326",
            "mt5_server": "DooTechnology-Live",
            "mt5_balance": 1837934.05
        }

    def log_critical_issue(self, issue_type, description, expected, actual):
        """Log a critical issue found during investigation"""
        self.critical_issues.append({
            "type": issue_type,
            "description": description,
            "expected": expected,
            "actual": actual,
            "timestamp": datetime.now().isoformat()
        })
        print(f"🚨 CRITICAL ISSUE: {issue_type}")
        print(f"   Description: {description}")
        print(f"   Expected: {expected}")
        print(f"   Actual: {actual}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test with detailed logging"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 {name}")
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

            print(f"   Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ FAILED - Error: {str(e)}")
            return False, {}

    def authenticate_admin(self):
        """Authenticate as admin to access all endpoints"""
        print("\n" + "="*80)
        print("STEP 1: ADMIN AUTHENTICATION")
        print("="*80)
        
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
        
        if success and response.get('token'):
            self.admin_token = response['token']
            print(f"   ✅ Admin authenticated: {response.get('name')}")
            return True
        else:
            self.log_critical_issue(
                "AUTHENTICATION_FAILURE",
                "Cannot authenticate as admin - investigation blocked",
                "Admin login successful with token",
                "Login failed or no token received"
            )
            return False

    def investigate_salvador_client_existence(self):
        """Check if Salvador Palma client exists in the system"""
        print("\n" + "="*80)
        print("STEP 2: SALVADOR PALMA CLIENT EXISTENCE CHECK")
        print("="*80)
        
        # Get all clients
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }
        
        success, response = self.run_test(
            "Get All Clients",
            "GET", 
            "api/clients/all",
            200,
            headers=headers
        )
        
        if not success:
            self.log_critical_issue(
                "CLIENT_LIST_FAILURE",
                "Cannot retrieve client list",
                "List of all clients including Salvador Palma",
                "API call failed"
            )
            return False
            
        clients = response.get('clients', [])
        print(f"   Total clients found: {len(clients)}")
        
        # Look for Salvador Palma
        salvador_found = False
        salvador_client = None
        
        for client in clients:
            print(f"   Client: {client.get('name')} (ID: {client.get('id')}, Email: {client.get('email')})")
            if (client.get('name') == self.expected_salvador_data['name'] or 
                client.get('id') == self.expected_salvador_data['client_id'] or
                client.get('email') == self.expected_salvador_data['email']):
                salvador_found = True
                salvador_client = client
                print(f"   ✅ SALVADOR PALMA FOUND: {client}")
                break
        
        if not salvador_found:
            self.log_critical_issue(
                "SALVADOR_CLIENT_MISSING",
                "Salvador Palma client profile not found in system",
                f"Client with name '{self.expected_salvador_data['name']}' or ID '{self.expected_salvador_data['client_id']}'",
                f"No matching client found among {len(clients)} clients"
            )
            return False
            
        return salvador_client

    def investigate_salvador_investments(self, salvador_client):
        """Check Salvador's investment data"""
        print("\n" + "="*80)
        print("STEP 3: SALVADOR PALMA INVESTMENT DATA CHECK")
        print("="*80)
        
        client_id = salvador_client.get('id')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }
        
        # Check client investments
        success, response = self.run_test(
            f"Get Salvador's Investments (Client ID: {client_id})",
            "GET",
            f"api/investments/client/{client_id}",
            200,
            headers=headers
        )
        
        if not success:
            self.log_critical_issue(
                "INVESTMENT_API_FAILURE",
                f"Cannot retrieve investments for Salvador (client_id: {client_id})",
                "Investment data for Salvador Palma",
                "API call failed"
            )
            return []
            
        investments = response.get('investments', [])
        portfolio_stats = response.get('portfolio', {})
        
        print(f"   Salvador's investments found: {len(investments)}")
        print(f"   Portfolio stats: {portfolio_stats}")
        
        if len(investments) == 0:
            self.log_critical_issue(
                "SALVADOR_INVESTMENTS_MISSING",
                "Salvador Palma has no investments in the system",
                f"BALANCE fund investment of ${self.expected_salvador_data['balance_investment']:,.2f}",
                "0 investments found"
            )
            return []
        
        # Check for BALANCE fund investment
        balance_investment_found = False
        for investment in investments:
            print(f"   Investment: {investment}")
            if (investment.get('fund_code') == 'BALANCE' and 
                abs(investment.get('principal_amount', 0) - self.expected_salvador_data['balance_investment']) < 1000):
                balance_investment_found = True
                print(f"   ✅ BALANCE fund investment found: ${investment.get('principal_amount'):,.2f}")
                break
        
        if not balance_investment_found:
            self.log_critical_issue(
                "BALANCE_INVESTMENT_MISSING",
                "Salvador's BALANCE fund investment not found",
                f"BALANCE fund investment of ${self.expected_salvador_data['balance_investment']:,.2f}",
                f"Found {len(investments)} investments but no BALANCE fund with expected amount"
            )
        
        return investments

    def investigate_mt5_accounts(self):
        """Check MT5 account data and mappings"""
        print("\n" + "="*80)
        print("STEP 4: MT5 ACCOUNT MAPPING INVESTIGATION")
        print("="*80)
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }
        
        # Check MT5 admin accounts endpoint
        success, response = self.run_test(
            "Get All MT5 Accounts",
            "GET",
            "api/mt5/admin/accounts",
            200,
            headers=headers
        )
        
        if not success:
            self.log_critical_issue(
                "MT5_API_FAILURE",
                "Cannot retrieve MT5 accounts data",
                "List of MT5 accounts including Salvador's account 9928326",
                "MT5 API call failed"
            )
            return False
            
        mt5_accounts = response.get('accounts', [])
        print(f"   Total MT5 accounts found: {len(mt5_accounts)}")
        
        # Look for Salvador's MT5 account
        salvador_mt5_found = False
        for account in mt5_accounts:
            print(f"   MT5 Account: {account}")
            # Check both login field and mt5_login field
            account_login = str(account.get('login', account.get('mt5_login', '')))
            if account_login == self.expected_salvador_data['mt5_login']:
                salvador_mt5_found = True
                print(f"   ✅ SALVADOR'S MT5 ACCOUNT FOUND: {account}")
                
                # Check account details - use current_equity instead of balance
                expected_balance = self.expected_salvador_data['mt5_balance']
                actual_balance = account.get('current_equity', account.get('balance', 0))
                
                print(f"   Expected MT5 Balance: ${expected_balance:,.2f}")
                print(f"   Actual MT5 Balance: ${actual_balance:,.2f}")
                
                if abs(actual_balance - expected_balance) > 10000:  # Allow 10K variance
                    self.log_critical_issue(
                        "MT5_BALANCE_MISMATCH",
                        "Salvador's MT5 balance doesn't match expected value",
                        f"${expected_balance:,.2f}",
                        f"${actual_balance:,.2f}"
                    )
                else:
                    print(f"   ✅ MT5 Balance matches expected value (within tolerance)")
                break
        
        if not salvador_mt5_found:
            self.log_critical_issue(
                "SALVADOR_MT5_MISSING",
                "Salvador's MT5 account not found in system",
                f"MT5 account with login {self.expected_salvador_data['mt5_login']}",
                f"No matching MT5 account found among {len(mt5_accounts)} accounts"
            )
            
        return salvador_mt5_found

    def investigate_crm_dashboard_data(self):
        """Check CRM dashboard data for Salvador's information"""
        print("\n" + "="*80)
        print("STEP 5: CRM DASHBOARD DATA INVESTIGATION")
        print("="*80)
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }
        
        # Check fund performance dashboard
        success, response = self.run_test(
            "Get Fund Performance Dashboard",
            "GET",
            "api/admin/fund-performance/dashboard",
            200,
            headers=headers
        )
        
        if success:
            fund_data = response.get('funds', [])
            print(f"   Fund performance data found: {len(fund_data)} funds")
            
            for fund in fund_data:
                if fund.get('fund_code') == 'BALANCE':
                    print(f"   BALANCE fund data: {fund}")
                    
                    # Check if Salvador's investment is reflected in fund totals
                    total_aum = fund.get('total_aum', 0)
                    if total_aum < self.expected_salvador_data['balance_investment']:
                        self.log_critical_issue(
                            "FUND_AUM_MISMATCH",
                            "BALANCE fund AUM is less than Salvador's investment alone",
                            f"At least ${self.expected_salvador_data['balance_investment']:,.2f}",
                            f"${total_aum:,.2f}"
                        )
        
        # Check cash flow management
        success, response = self.run_test(
            "Get Cash Flow Management Data",
            "GET",
            "api/admin/cashflow/overview",
            200,
            headers=headers
        )
        
        if success:
            cash_flow_data = response
            print(f"   Cash flow data: {cash_flow_data}")
            
            # Check MT5 trading profits in fund accounting
            fund_accounting = cash_flow_data.get('fund_accounting', {})
            assets = fund_accounting.get('assets', {})
            mt5_profits = assets.get('mt5_trading_profits', 0)
            
            print(f"   MT5 Trading Profits: ${mt5_profits:,.2f}")
            
            if mt5_profits == 0:
                self.log_critical_issue(
                    "CASH_FLOW_MT5_ZERO",
                    "MT5 trading profits showing zero in cash flow",
                    f"Positive MT5 profits from Salvador's account",
                    f"${mt5_profits:,.2f}"
                )
            else:
                print(f"   ✅ MT5 Trading Profits found: ${mt5_profits:,.2f}")
                
            # Check BALANCE fund specific data
            fund_breakdown = cash_flow_data.get('fund_breakdown', {})
            balance_fund = fund_breakdown.get('BALANCE', {})
            balance_mt5_profits = balance_fund.get('mt5_profits', 0)
            print(f"   BALANCE Fund MT5 Profits: ${balance_mt5_profits:,.2f}")

    def test_critical_endpoints(self):
        """Test all critical endpoints mentioned in the review"""
        print("\n" + "="*80)
        print("STEP 6: CRITICAL ENDPOINT TESTING")
        print("="*80)
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }
        
        critical_endpoints = [
            ("Investment Client Endpoint", "GET", f"api/investments/client/{self.expected_salvador_data['client_id']}"),
            ("MT5 Admin Accounts", "GET", "api/mt5/admin/accounts"),
            ("Fund Performance Dashboard", "GET", "api/admin/fund-performance/dashboard"),
            ("Cash Flow Overview", "GET", "api/admin/cashflow/overview"),
            ("Client Data", "GET", f"api/client/{self.expected_salvador_data['client_id']}/data")
        ]
        
        endpoint_results = []
        for name, method, endpoint in critical_endpoints:
            success, response = self.run_test(name, method, endpoint, 200, headers=headers)
            endpoint_results.append({
                "name": name,
                "endpoint": endpoint,
                "success": success,
                "response_size": len(str(response)) if response else 0
            })
        
        return endpoint_results

    def generate_investigation_report(self):
        """Generate comprehensive investigation report"""
        print("\n" + "="*80)
        print("SALVADOR PALMA INVESTIGATION REPORT")
        print("="*80)
        
        print(f"\n📊 INVESTIGATION SUMMARY:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        print(f"   Critical Issues Found: {len(self.critical_issues)}")
        
        if self.critical_issues:
            print(f"\n🚨 CRITICAL ISSUES IDENTIFIED:")
            for i, issue in enumerate(self.critical_issues, 1):
                print(f"\n   {i}. {issue['type']}")
                print(f"      Description: {issue['description']}")
                print(f"      Expected: {issue['expected']}")
                print(f"      Actual: {issue['actual']}")
        
        print(f"\n📋 EXPECTED SALVADOR PALMA DATA:")
        for key, value in self.expected_salvador_data.items():
            print(f"   {key}: {value}")
        
        # Determine overall system status
        if len(self.critical_issues) == 0:
            print(f"\n✅ SYSTEM STATUS: HEALTHY - All Salvador Palma data present and correct")
            return True
        elif len(self.critical_issues) <= 2:
            print(f"\n⚠️  SYSTEM STATUS: DEGRADED - Minor issues found")
            return False
        else:
            print(f"\n❌ SYSTEM STATUS: CRITICAL FAILURE - Major data integrity issues")
            return False

    def run_full_investigation(self):
        """Run complete investigation of Salvador Palma data integrity"""
        print("🔍 STARTING SALVADOR PALMA INVESTMENT DATA INVESTIGATION")
        print("="*80)
        print("Investigating critical production bug where Salvador Palma's investments")
        print("with MT5 account mappings are missing from the deployed FIDUS system.")
        print("="*80)
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            return False
        
        # Step 2: Check client existence
        salvador_client = self.investigate_salvador_client_existence()
        if not salvador_client:
            return False
        
        # Step 3: Check investments
        investments = self.investigate_salvador_investments(salvador_client)
        
        # Step 4: Check MT5 accounts
        self.investigate_mt5_accounts()
        
        # Step 5: Check CRM dashboard data
        self.investigate_crm_dashboard_data()
        
        # Step 6: Test critical endpoints
        self.test_critical_endpoints()
        
        # Step 7: Generate report
        return self.generate_investigation_report()

if __name__ == "__main__":
    investigator = SalvadorPalmaInvestigator()
    
    try:
        system_healthy = investigator.run_full_investigation()
        
        if system_healthy:
            print(f"\n🎉 INVESTIGATION COMPLETE: System is healthy")
            sys.exit(0)
        else:
            print(f"\n🚨 INVESTIGATION COMPLETE: Critical issues found - immediate action required")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⚠️  Investigation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Investigation failed with error: {str(e)}")
        sys.exit(1)