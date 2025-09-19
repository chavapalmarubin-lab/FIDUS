#!/usr/bin/env python3
"""
COMPREHENSIVE PRODUCTION SYSTEM CHECK - END OF DAY VALIDATION
FIDUS Investment Management System

This test validates the production system for Monday deployment focusing on:
1. Core Investment System with MT5 integration
2. Authentication & Security (JWT)
3. Wallet System (FIDUS official wallets)
4. Data Integrity (Salvador Palma only)
5. Critical Financial Calculations
"""

import requests
import sys
import json
from datetime import datetime
import time

class ProductionSystemTester:
    def __init__(self, base_url="https://wealth-portal-17.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None
        self.client_token = None
        self.salvador_client_id = "client_003"  # Salvador Palma's client ID
        self.critical_issues = []
        self.minor_issues = []
        
    def log_critical_issue(self, issue):
        """Log critical issues that block production"""
        self.critical_issues.append(issue)
        print(f"🚨 CRITICAL: {issue}")
        
    def log_minor_issue(self, issue):
        """Log minor issues that don't block production"""
        self.minor_issues.append(issue)
        print(f"⚠️  MINOR: {issue}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, auth_required=False):
        """Run a single API test with authentication support"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}
            
        # Add authentication if required
        if auth_required and self.admin_token:
            headers['Authorization'] = f'Bearer {self.admin_token}'

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
                print(f"✅ PASSED - Status: {response.status_code}")
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

    def test_admin_authentication(self):
        """Test admin login and JWT authentication"""
        print("\n" + "="*80)
        print("🔐 TESTING AUTHENTICATION & SECURITY")
        print("="*80)
        
        success, response = self.run_test(
            "Admin Login with JWT",
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
            self.admin_token = response.get('token')
            if self.admin_token:
                print(f"   ✅ JWT Token received: {self.admin_token[:50]}...")
                return True
            else:
                self.log_critical_issue("Admin login successful but no JWT token received")
                return False
        else:
            self.log_critical_issue("Admin authentication failed")
            return False

    def test_client_authentication(self):
        """Test client login (Salvador Palma)"""
        success, response = self.run_test(
            "Client Login (Salvador Palma)",
            "POST",
            "api/auth/login",
            200,
            data={
                "username": "client3", 
                "password": "password123",
                "user_type": "client"
            }
        )
        
        if success:
            self.client_token = response.get('token')
            client_name = response.get('name', 'Unknown')
            if "SALVADOR PALMA" in client_name.upper():
                print(f"   ✅ Salvador Palma authenticated successfully")
                return True
            else:
                self.log_critical_issue(f"Expected Salvador Palma, got {client_name}")
                return False
        else:
            self.log_critical_issue("Salvador Palma authentication failed")
            return False

    def test_fund_performance_dashboard(self):
        """Test Fund Performance vs MT5 Reality dashboard - should show only Salvador Palma"""
        print("\n" + "="*80)
        print("📊 TESTING FUND PERFORMANCE VS MT5 REALITY DASHBOARD")
        print("="*80)
        
        success, response = self.run_test(
            "Fund Performance Dashboard",
            "GET",
            "api/admin/fund-performance/dashboard",
            200,
            auth_required=True
        )
        
        if success:
            # Check dashboard structure
            dashboard = response.get('dashboard', {})
            fund_commitments = dashboard.get('fund_commitments', {})
            performance_gaps = dashboard.get('performance_gaps', [])
            
            print(f"   Fund commitments: {len(fund_commitments)}")
            print(f"   Performance gaps: {len(performance_gaps)}")
            
            # Check for Salvador Palma's BALANCE fund investment
            salvador_found = False
            if 'BALANCE' in fund_commitments:
                balance_fund = fund_commitments['BALANCE']
                client_investment = balance_fund.get('client_investment', {})
                client_id = client_investment.get('client_id', '')
                principal_amount = client_investment.get('principal_amount', 0)
                
                if client_id == self.salvador_client_id:
                    salvador_found = True
                    print(f"   ✅ Salvador Palma found in BALANCE fund: ${principal_amount:,.2f}")
                    
                    # Verify expected amount ($1,263,485.40)
                    expected_amount = 1263485.40
                    if abs(principal_amount - expected_amount) < 1000:  # Allow small variance
                        print(f"   ✅ Investment amount matches expected: ${expected_amount:,.2f}")
                    else:
                        self.log_critical_issue(f"Salvador's investment amount incorrect: ${principal_amount:,.2f} vs expected ${expected_amount:,.2f}")
            
            if not salvador_found:
                self.log_critical_issue("Salvador Palma not found in Fund Performance dashboard")
                return False
            
            # Check performance gaps for Salvador
            salvador_gap_found = False
            for gap in performance_gaps:
                if gap.get('client_id') == self.salvador_client_id:
                    salvador_gap_found = True
                    actual_performance = gap.get('actual_mt5_performance', 0)
                    expected_performance = gap.get('expected_performance', 0)
                    gap_amount = gap.get('gap_amount', 0)
                    print(f"   MT5 Performance: ${actual_performance:,.2f}")
                    print(f"   Expected Performance: ${expected_performance:,.2f}")
                    print(f"   Performance Gap: ${gap_amount:,.2f}")
            
            if salvador_gap_found:
                print(f"   ✅ Salvador's performance data found and calculated")
            else:
                self.log_minor_issue("Salvador's performance gap data not found")
            
            return True
        else:
            self.log_critical_issue("Fund Performance dashboard not accessible")
            return False

    def test_cash_flow_management(self):
        """Test Cash Flow Management calculations"""
        print("\n" + "="*80)
        print("💰 TESTING CASH FLOW MANAGEMENT CALCULATIONS")
        print("="*80)
        
        success, response = self.run_test(
            "Cash Flow Overview",
            "GET",
            "api/admin/cashflow/overview",
            200,
            auth_required=True
        )
        
        if success:
            # Check fund accounting structure
            fund_accounting = response.get('fund_accounting', {})
            assets = fund_accounting.get('assets', {})
            liabilities = fund_accounting.get('liabilities', {})
            
            # Check MT5 trading profits ($860,448.65 expected)
            mt5_profits = assets.get('mt5_trading_profits', 0)
            expected_mt5_profits = 860448.65
            
            print(f"   MT5 Trading Profits: ${mt5_profits:,.2f}")
            
            if abs(mt5_profits - expected_mt5_profits) < 1000:  # Allow small variance
                print(f"   ✅ MT5 profits match expected: ${expected_mt5_profits:,.2f}")
            else:
                self.log_critical_issue(f"MT5 profits incorrect: ${mt5_profits:,.2f} vs expected ${expected_mt5_profits:,.2f}")
            
            # Check client obligations ($1,421,421.07 expected)
            client_obligations = liabilities.get('client_obligations', 0)
            expected_obligations = 1421421.07
            
            print(f"   Client Obligations: ${client_obligations:,.2f}")
            
            if abs(client_obligations - expected_obligations) < 1000:  # Allow small variance
                print(f"   ✅ Client obligations match expected: ${expected_obligations:,.2f}")
            else:
                self.log_critical_issue(f"Client obligations incorrect: ${client_obligations:,.2f} vs expected ${expected_obligations:,.2f}")
            
            # Check net fund profitability
            net_profitability = fund_accounting.get('net_fund_profitability', 0)
            print(f"   Net Fund Profitability: ${net_profitability:,.2f}")
            
            # Check fund breakdown for BALANCE fund
            fund_breakdown = response.get('fund_breakdown', {})
            balance_fund = fund_breakdown.get('BALANCE', {})
            if balance_fund:
                balance_mt5_profits = balance_fund.get('mt5_profits', 0)
                balance_obligations = balance_fund.get('client_obligations', 0)
                print(f"   BALANCE Fund MT5 Profits: ${balance_mt5_profits:,.2f}")
                print(f"   BALANCE Fund Client Obligations: ${balance_obligations:,.2f}")
            
            return True
        else:
            self.log_critical_issue("Cash Flow Management not accessible")
            return False

    def test_investment_creation_system(self):
        """Test investment creation with MT5 account mapping"""
        print("\n" + "="*80)
        print("🏦 TESTING INVESTMENT CREATION WITH MT5 MAPPING")
        print("="*80)
        
        # Test investment creation endpoint
        success, response = self.run_test(
            "Investment Creation Endpoint",
            "POST",
            "api/investments/create",
            200,
            data={
                "client_id": "test_client_001",
                "fund_code": "CORE",
                "amount": 15000,
                "deposit_date": "2024-12-19",
                "create_mt5_account": True,
                "mt5_login": "9928326",
                "mt5_password": "TestPassword123",
                "mt5_server": "Multibank-Live",
                "broker_name": "Multibank",
                "mt5_initial_balance": 15000,
                "banking_fees": 50,
                "fee_notes": "Wire transfer fee"
            },
            auth_required=True
        )
        
        if success:
            investment_id = response.get('investment_id')
            mt5_mapping_success = response.get('mt5_mapping_success', False)
            
            if investment_id:
                print(f"   ✅ Investment created: {investment_id}")
            
            if mt5_mapping_success:
                print(f"   ✅ MT5 account mapping successful")
            else:
                self.log_minor_issue("MT5 account mapping failed but investment created")
            
            return True
        else:
            self.log_critical_issue("Investment creation system not working")
            return False

    def test_wallet_system(self):
        """Test FIDUS official wallet system"""
        print("\n" + "="*80)
        print("💳 TESTING WALLET SYSTEM")
        print("="*80)
        
        # Test FIDUS official wallets endpoint
        success, response = self.run_test(
            "FIDUS Official Wallets",
            "GET",
            "api/wallets/fidus",
            200
        )
        
        if success:
            wallets = response.get('wallets', [])
            print(f"   Total FIDUS wallets: {len(wallets)}")
            
            # Check for expected wallet addresses
            expected_addresses = {
                'USDT_ERC20': '0xDe2DC29591dBc6e540b63050D73E2E9430733A90',
                'USDT_TRC20': 'TGoTqWUhLMFQyAm3BeFUEwMuUPDMY4g3iG',
                'BTC': '1JT2h9aQ6KnP2vjRiPT13Dvc3ASp9mQ6fj',
                'ETH': '0xDe2DC29591dBc6e540b63050D73E2E9430733A90'
            }
            
            found_addresses = {}
            for wallet in wallets:
                currency = wallet.get('currency', '')
                network = wallet.get('network', '')
                address = wallet.get('address', '')
                
                key = f"{currency}_{network}" if network != currency else currency
                found_addresses[key] = address
                print(f"   {currency} ({network}): {address}")
            
            # Verify expected addresses
            all_found = True
            for expected_key, expected_addr in expected_addresses.items():
                if expected_key in found_addresses:
                    if found_addresses[expected_key] == expected_addr:
                        print(f"   ✅ {expected_key} address correct")
                    else:
                        self.log_critical_issue(f"{expected_key} address mismatch")
                        all_found = False
                else:
                    self.log_critical_issue(f"{expected_key} wallet not found")
                    all_found = False
            
            return all_found
        else:
            self.log_critical_issue("FIDUS wallet system not accessible")
            return False

    def test_client_wallet_management(self):
        """Test client wallet management endpoints"""
        success, response = self.run_test(
            "Client Wallet Management",
            "GET",
            f"api/client/{self.salvador_client_id}/wallets",
            200
        )
        
        if success:
            wallets = response.get('wallets', [])
            print(f"   Salvador's wallets: {len(wallets)}")
            return True
        else:
            self.log_minor_issue("Client wallet management not accessible")
            return False

    def test_redemption_system(self):
        """Test redemption management system"""
        print("\n" + "="*80)
        print("🔄 TESTING REDEMPTION MANAGEMENT SYSTEM")
        print("="*80)
        
        # Test redemption data for Salvador
        success, response = self.run_test(
            "Salvador's Redemption Data",
            "GET",
            f"api/redemptions/client/{self.salvador_client_id}",
            200
        )
        
        if success:
            investments = response.get('investments', [])
            print(f"   Salvador's investments available for redemption: {len(investments)}")
            
            total_value = 0
            for investment in investments:
                current_value = investment.get('current_value', 0)
                fund_code = investment.get('fund_code', '')
                total_value += current_value
                print(f"   {fund_code} Fund: ${current_value:,.2f}")
            
            print(f"   Total redemption value: ${total_value:,.2f}")
            return True
        else:
            self.log_critical_issue("Redemption system not accessible")
            return False

    def test_data_integrity(self):
        """Test overall data integrity - no fake test data"""
        print("\n" + "="*80)
        print("🔍 TESTING DATA INTEGRITY")
        print("="*80)
        
        # Check all clients to ensure no test contamination
        success, response = self.run_test(
            "All Clients Data Integrity Check",
            "GET",
            "api/clients/all",
            200,
            auth_required=True
        )
        
        if success:
            clients = response.get('clients', [])
            print(f"   Total clients in system: {len(clients)}")
            
            legitimate_clients = []
            test_clients = []
            
            for client in clients:
                client_name = client.get('name', '').lower()
                client_email = client.get('email', '').lower()
                
                # Check for test data patterns
                if any(test_pattern in client_name for test_pattern in ['test', 'client_001', 'fake', 'dummy']):
                    test_clients.append(client['name'])
                elif any(test_pattern in client_email for test_pattern in ['test@', 'fake@', 'dummy@']):
                    test_clients.append(client['name'])
                else:
                    legitimate_clients.append(client['name'])
                    print(f"   Legitimate client: {client['name']}")
            
            if test_clients:
                self.log_critical_issue(f"Test data contamination found: {test_clients}")
                return False
            else:
                print(f"   ✅ No test data contamination detected")
                return True
        else:
            self.log_critical_issue("Cannot access client data for integrity check")
            return False

    def test_critical_endpoints(self):
        """Test all critical endpoints mentioned in review"""
        print("\n" + "="*80)
        print("🎯 TESTING CRITICAL ENDPOINTS")
        print("="*80)
        
        critical_endpoints = [
            ("Fund Performance Dashboard", "GET", "api/admin/fund-performance/dashboard", 200, True),
            ("Cash Flow Overview", "GET", "api/admin/cashflow/overview", 200, True),
            ("Investment Creation", "GET", "api/investments/funds/config", 200, False),
            ("FIDUS Wallets", "GET", "api/wallets/fidus", 200, False),
            ("Health Check", "GET", "api/health", 200, False),
        ]
        
        all_passed = True
        for name, method, endpoint, expected_status, auth_required in critical_endpoints:
            success, _ = self.run_test(name, method, endpoint, expected_status, auth_required=auth_required)
            if not success:
                self.log_critical_issue(f"Critical endpoint failed: {endpoint}")
                all_passed = False
        
        return all_passed

    def run_production_validation(self):
        """Run complete production validation suite"""
        print("🚀 FIDUS INVESTMENT MANAGEMENT SYSTEM")
        print("📋 COMPREHENSIVE PRODUCTION SYSTEM CHECK")
        print("🗓️  END OF DAY VALIDATION - MONDAY DEPLOYMENT READINESS")
        print("="*80)
        
        start_time = time.time()
        
        # Core test sequence
        tests = [
            ("Authentication & Security", self.test_admin_authentication),
            ("Client Authentication", self.test_client_authentication),
            ("Fund Performance Dashboard", self.test_fund_performance_dashboard),
            ("Cash Flow Management", self.test_cash_flow_management),
            ("Investment Creation System", self.test_investment_creation_system),
            ("Wallet System", self.test_wallet_system),
            ("Client Wallet Management", self.test_client_wallet_management),
            ("Redemption System", self.test_redemption_system),
            ("Data Integrity", self.test_data_integrity),
            ("Critical Endpoints", self.test_critical_endpoints),
        ]
        
        passed_tests = 0
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log_critical_issue(f"Test {test_name} crashed: {str(e)}")
        
        # Final report
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "="*80)
        print("📊 PRODUCTION VALIDATION RESULTS")
        print("="*80)
        
        print(f"⏱️  Test Duration: {duration:.2f} seconds")
        print(f"🧪 Total Tests Run: {self.tests_run}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        print(f"\n🎯 Core System Tests: {passed_tests}/{len(tests)} passed")
        
        if self.critical_issues:
            print(f"\n🚨 CRITICAL ISSUES ({len(self.critical_issues)}):")
            for issue in self.critical_issues:
                print(f"   • {issue}")
        
        if self.minor_issues:
            print(f"\n⚠️  MINOR ISSUES ({len(self.minor_issues)}):")
            for issue in self.minor_issues:
                print(f"   • {issue}")
        
        # Production readiness assessment
        print("\n" + "="*80)
        print("🎯 PRODUCTION READINESS ASSESSMENT")
        print("="*80)
        
        if not self.critical_issues and passed_tests >= 8:
            print("✅ SYSTEM IS PRODUCTION READY")
            print("✅ All critical functionality working")
            print("✅ Data integrity confirmed")
            print("✅ Financial calculations accurate")
            print("✅ Authentication systems operational")
            print("✅ APPROVED FOR MONDAY DEPLOYMENT")
            return True
        else:
            print("❌ SYSTEM NOT READY FOR PRODUCTION")
            print("❌ Critical issues must be resolved before deployment")
            return False

if __name__ == "__main__":
    print("Starting FIDUS Production System Validation...")
    
    tester = ProductionSystemTester()
    production_ready = tester.run_production_validation()
    
    # Exit with appropriate code
    sys.exit(0 if production_ready else 1)