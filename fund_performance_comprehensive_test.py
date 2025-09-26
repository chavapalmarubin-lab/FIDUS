#!/usr/bin/env python3
"""
Comprehensive Fund Performance Management System Testing
Testing all fund performance endpoints and documenting findings
"""

import requests
import sys
from datetime import datetime
import json

class ComprehensiveFundPerformanceTester:
    def __init__(self, base_url="https://invest-portal-31.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None
        self.findings = []
        
    def log_finding(self, category, status, message):
        """Log a test finding"""
        self.findings.append({
            "category": category,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
    def get_admin_token(self):
        """Get admin authentication token"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={
                    "username": "admin",
                    "password": "password123", 
                    "user_type": "admin"
                },
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                self.log_finding("AUTHENTICATION", "SUCCESS", f"Admin login successful: {data.get('name')}")
                return True
            else:
                self.log_finding("AUTHENTICATION", "FAILED", f"Admin login failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_finding("AUTHENTICATION", "ERROR", f"Admin login error: {str(e)}")
            return False
    
    def get_auth_headers(self):
        """Get headers with authentication"""
        headers = {'Content-Type': 'application/json'}
        if self.admin_token:
            headers['Authorization'] = f'Bearer {self.admin_token}'
        return headers
    
    def test_endpoint(self, name, endpoint, expected_keys=None):
        """Test a single endpoint and return response"""
        self.tests_run += 1
        try:
            response = requests.get(
                f"{self.base_url}/{endpoint}",
                headers=self.get_auth_headers(),
                timeout=15
            )
            
            if response.status_code == 200:
                self.tests_passed += 1
                data = response.json()
                
                # Check for expected keys
                if expected_keys:
                    missing_keys = [key for key in expected_keys if key not in data]
                    if missing_keys:
                        self.log_finding(name, "PARTIAL", f"Missing keys: {missing_keys}")
                    else:
                        self.log_finding(name, "SUCCESS", "All expected keys present")
                else:
                    self.log_finding(name, "SUCCESS", "Endpoint accessible")
                
                return True, data
            else:
                self.log_finding(name, "FAILED", f"HTTP {response.status_code}: {response.text}")
                return False, {}
                
        except Exception as e:
            self.log_finding(name, "ERROR", f"Exception: {str(e)}")
            return False, {}
    
    def test_fund_performance_dashboard(self):
        """Test fund performance dashboard endpoint"""
        print("\n📊 Testing Fund Performance Dashboard...")
        
        success, data = self.test_endpoint(
            "DASHBOARD",
            "api/admin/fund-performance/dashboard",
            ["success", "dashboard", "generated_at"]
        )
        
        if success:
            dashboard = data.get('dashboard', {})
            
            # Check dashboard components
            components = ['fund_commitments', 'client_positions', 'performance_gaps', 'risk_summary', 'action_items']
            for component in components:
                if component in dashboard:
                    value = dashboard[component]
                    if isinstance(value, list):
                        self.log_finding("DASHBOARD", "INFO", f"{component}: {len(value)} items")
                    elif isinstance(value, dict):
                        self.log_finding("DASHBOARD", "INFO", f"{component}: {len(value)} keys")
                    else:
                        self.log_finding("DASHBOARD", "INFO", f"{component}: {value}")
                else:
                    self.log_finding("DASHBOARD", "WARNING", f"Missing component: {component}")
            
            # Check fund commitments
            fund_commitments = dashboard.get('fund_commitments', {})
            expected_funds = ['CORE', 'BALANCE', 'DYNAMIC', 'UNLIMITED']
            for fund in expected_funds:
                if fund in fund_commitments:
                    fund_data = fund_commitments[fund]
                    monthly_return = fund_data.get('monthly_return')
                    self.log_finding("DASHBOARD", "SUCCESS", f"{fund} fund: {monthly_return}% monthly return")
                else:
                    self.log_finding("DASHBOARD", "ERROR", f"Missing fund: {fund}")
        
        return success
    
    def test_fund_performance_gaps(self):
        """Test fund performance gaps endpoint"""
        print("\n📈 Testing Fund Performance Gaps...")
        
        success, data = self.test_endpoint(
            "PERFORMANCE_GAPS",
            "api/admin/fund-performance/gaps",
            ["success", "performance_gaps", "total_gaps", "generated_at"]
        )
        
        if success:
            gaps = data.get('performance_gaps', [])
            total_gaps = data.get('total_gaps', 0)
            
            self.log_finding("PERFORMANCE_GAPS", "INFO", f"Total gaps reported: {total_gaps}")
            self.log_finding("PERFORMANCE_GAPS", "INFO", f"Gaps array length: {len(gaps)}")
            
            if total_gaps == 0:
                self.log_finding("PERFORMANCE_GAPS", "WARNING", "No performance gaps found - fund_performance_manager may not be available")
            else:
                # Look for Salvador Palma's gap
                salvador_gap = None
                for gap in gaps:
                    if gap.get('client_id') == 'client_003' and gap.get('fund_code') == 'BALANCE':
                        salvador_gap = gap
                        break
                
                if salvador_gap:
                    gap_percentage = salvador_gap.get('gap_percentage', 0)
                    self.log_finding("PERFORMANCE_GAPS", "SUCCESS", f"Salvador BALANCE gap: {gap_percentage}%")
                else:
                    self.log_finding("PERFORMANCE_GAPS", "WARNING", "Salvador Palma BALANCE gap not found")
        
        return success
    
    def test_fund_commitments(self):
        """Test fund commitments endpoint"""
        print("\n📋 Testing Fund Commitments...")
        
        success, data = self.test_endpoint(
            "FUND_COMMITMENTS",
            "api/admin/fund-commitments",
            ["success", "fund_commitments", "generated_at"]
        )
        
        if success:
            commitments = data.get('fund_commitments', {})
            expected_funds = ['CORE', 'BALANCE', 'DYNAMIC', 'UNLIMITED']
            
            for fund in expected_funds:
                if fund in commitments:
                    fund_data = commitments[fund]
                    monthly_return = fund_data.get('monthly_return')
                    risk_level = fund_data.get('risk_level')
                    guaranteed = fund_data.get('guaranteed')
                    
                    self.log_finding("FUND_COMMITMENTS", "SUCCESS", 
                                   f"{fund}: {monthly_return}% monthly, {risk_level} risk, guaranteed: {guaranteed}")
                    
                    # Verify BALANCE fund specifically
                    if fund == 'BALANCE' and monthly_return == 2.5:
                        self.log_finding("FUND_COMMITMENTS", "SUCCESS", "BALANCE fund 2.5% monthly return verified")
                else:
                    self.log_finding("FUND_COMMITMENTS", "ERROR", f"Missing fund: {fund}")
        
        return success
    
    def test_client_fund_performance(self):
        """Test client fund performance endpoint"""
        print("\n👤 Testing Client Fund Performance...")
        
        client_id = "client_003"  # Salvador Palma
        success, data = self.test_endpoint(
            "CLIENT_PERFORMANCE",
            f"api/admin/fund-performance/client/{client_id}",
            ["success", "client_comparison", "generated_at"]
        )
        
        if success:
            comparison = data.get('client_comparison', {})
            
            # Check comparison structure
            if 'client_id' in comparison:
                self.log_finding("CLIENT_PERFORMANCE", "SUCCESS", f"Client ID: {comparison['client_id']}")
            
            funds = comparison.get('funds', [])
            total_expected = comparison.get('total_expected', 0)
            total_actual = comparison.get('total_actual', 0)
            overall_gap = comparison.get('overall_gap', 0)
            
            self.log_finding("CLIENT_PERFORMANCE", "INFO", f"Funds analyzed: {len(funds)}")
            self.log_finding("CLIENT_PERFORMANCE", "INFO", f"Total expected: {total_expected}")
            self.log_finding("CLIENT_PERFORMANCE", "INFO", f"Total actual: {total_actual}")
            self.log_finding("CLIENT_PERFORMANCE", "INFO", f"Overall gap: {overall_gap}")
            
            if len(funds) == 0:
                self.log_finding("CLIENT_PERFORMANCE", "WARNING", "No funds data - fund_performance_manager may not be available")
        
        return success
    
    def test_salvador_palma_investment_data(self):
        """Test Salvador Palma's investment data"""
        print("\n🎯 Testing Salvador Palma Investment Data...")
        
        success, data = self.test_endpoint(
            "SALVADOR_INVESTMENT",
            "api/investments/client/client_003",
            ["success", "investments"]
        )
        
        if success:
            investments = data.get('investments', [])
            balance_investment = None
            
            for inv in investments:
                if inv.get('fund_code') == 'BALANCE':
                    balance_investment = inv
                    break
            
            if balance_investment:
                principal = balance_investment.get('principal_amount', 0)
                current_value = balance_investment.get('current_value', 0)
                deposit_date = balance_investment.get('deposit_date', '')
                interest_start = balance_investment.get('interest_start_date', '')
                
                self.log_finding("SALVADOR_INVESTMENT", "SUCCESS", f"Principal: ${principal:,.2f}")
                self.log_finding("SALVADOR_INVESTMENT", "SUCCESS", f"Current value: ${current_value:,.2f}")
                self.log_finding("SALVADOR_INVESTMENT", "SUCCESS", f"Deposit date: {deposit_date}")
                self.log_finding("SALVADOR_INVESTMENT", "SUCCESS", f"Interest start: {interest_start}")
                
                # Verify expected values
                if abs(principal - 100000) < 1000:
                    self.log_finding("SALVADOR_INVESTMENT", "SUCCESS", "Principal matches expected $100K")
                else:
                    self.log_finding("SALVADOR_INVESTMENT", "WARNING", f"Principal ${principal:,.2f} differs from expected $100K")
                
                if abs(current_value - 117500) < 5000:
                    self.log_finding("SALVADOR_INVESTMENT", "SUCCESS", "Current value matches expected $117.5K")
                else:
                    self.log_finding("SALVADOR_INVESTMENT", "WARNING", f"Current value ${current_value:,.2f} differs from expected $117.5K")
                
                if '2024-12-19' in deposit_date:
                    self.log_finding("SALVADOR_INVESTMENT", "SUCCESS", "Deposit date matches expected 2024-12-19")
                else:
                    self.log_finding("SALVADOR_INVESTMENT", "WARNING", f"Deposit date {deposit_date} differs from expected 2024-12-19")
                
                if '2025-02-19' in interest_start:
                    self.log_finding("SALVADOR_INVESTMENT", "SUCCESS", "Interest start matches expected 2025-02-19")
                else:
                    self.log_finding("SALVADOR_INVESTMENT", "WARNING", f"Interest start {interest_start} differs from expected 2025-02-19")
            else:
                self.log_finding("SALVADOR_INVESTMENT", "ERROR", "Salvador's BALANCE investment not found")
        
        return success
    
    def test_salvador_palma_mt5_data(self):
        """Test Salvador Palma's MT5 account data"""
        print("\n🔗 Testing Salvador Palma MT5 Data...")
        
        success, data = self.test_endpoint(
            "SALVADOR_MT5",
            "api/mt5/client/client_003/accounts",
            ["success", "accounts"]
        )
        
        if success:
            accounts = data.get('accounts', [])
            balance_account = None
            
            for account in accounts:
                if account.get('fund_code') == 'BALANCE':
                    balance_account = account
                    break
            
            if balance_account:
                mt5_login = balance_account.get('mt5_login')
                mt5_server = balance_account.get('mt5_server', '')
                total_allocated = balance_account.get('total_allocated', 0)
                current_equity = balance_account.get('current_equity', 0)
                profit_loss = balance_account.get('profit_loss', 0)
                
                self.log_finding("SALVADOR_MT5", "SUCCESS", f"MT5 Login: {mt5_login}")
                self.log_finding("SALVADOR_MT5", "SUCCESS", f"MT5 Server: {mt5_server}")
                self.log_finding("SALVADOR_MT5", "SUCCESS", f"Total allocated: ${total_allocated:,.2f}")
                self.log_finding("SALVADOR_MT5", "SUCCESS", f"Current equity: ${current_equity:,.2f}")
                self.log_finding("SALVADOR_MT5", "SUCCESS", f"Profit/Loss: ${profit_loss:,.2f}")
                
                # Verify expected MT5 login
                if mt5_login == 9928326:
                    self.log_finding("SALVADOR_MT5", "SUCCESS", "MT5 login matches expected 9928326")
                else:
                    self.log_finding("SALVADOR_MT5", "WARNING", f"MT5 login {mt5_login} differs from expected 9928326")
                
                # Verify DooTechnology server
                if 'DooTechnology-Live' in mt5_server:
                    self.log_finding("SALVADOR_MT5", "SUCCESS", "Server matches expected DooTechnology-Live")
                else:
                    self.log_finding("SALVADOR_MT5", "WARNING", f"Server {mt5_server} differs from expected DooTechnology-Live")
                
                # Calculate performance gap manually
                if total_allocated > 0:
                    performance_percentage = (profit_loss / total_allocated) * 100
                    self.log_finding("SALVADOR_MT5", "INFO", f"MT5 Performance: {performance_percentage:.2f}%")
                    
                    # Compare with FIDUS BALANCE commitment (2.5% monthly)
                    # Assuming investment period calculation
                    fidus_expected = 2.5  # Monthly rate
                    gap = performance_percentage - fidus_expected
                    self.log_finding("SALVADOR_MT5", "INFO", f"Performance gap vs FIDUS: {gap:.2f}%")
            else:
                self.log_finding("SALVADOR_MT5", "ERROR", "Salvador's BALANCE MT5 account not found")
        
        return success
    
    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🚀 COMPREHENSIVE FUND PERFORMANCE MANAGEMENT TESTING")
        print("=" * 80)
        
        # Get authentication
        if not self.get_admin_token():
            print("❌ CRITICAL: Authentication failed")
            return False
        
        # Run all tests
        tests = [
            self.test_fund_performance_dashboard,
            self.test_fund_performance_gaps,
            self.test_fund_commitments,
            self.test_client_fund_performance,
            self.test_salvador_palma_investment_data,
            self.test_salvador_palma_mt5_data
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_finding("TEST_ERROR", "ERROR", f"{test.__name__}: {str(e)}")
        
        # Generate comprehensive report
        self.generate_report()
        
        return self.tests_passed == self.tests_run
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE FUND PERFORMANCE TEST REPORT")
        print("=" * 80)
        
        # Summary statistics
        print(f"Total tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_run - self.tests_passed}")
        print(f"Success rate: {(self.tests_passed / self.tests_run * 100):.1f}%")
        
        # Categorize findings
        categories = {}
        for finding in self.findings:
            category = finding['category']
            if category not in categories:
                categories[category] = {'SUCCESS': [], 'WARNING': [], 'ERROR': [], 'INFO': [], 'FAILED': [], 'PARTIAL': []}
            categories[category][finding['status']].append(finding['message'])
        
        # Print detailed findings
        for category, statuses in categories.items():
            print(f"\n📋 {category}")
            print("-" * 40)
            
            for status, messages in statuses.items():
                if messages:
                    status_icon = {
                        'SUCCESS': '✅',
                        'WARNING': '⚠️',
                        'ERROR': '❌',
                        'INFO': 'ℹ️',
                        'FAILED': '❌',
                        'PARTIAL': '⚠️'
                    }.get(status, '•')
                    
                    print(f"{status_icon} {status}:")
                    for message in messages:
                        print(f"   • {message}")
        
        # Critical issues summary
        print(f"\n🎯 CRITICAL FINDINGS")
        print("-" * 40)
        
        critical_issues = []
        for finding in self.findings:
            if finding['status'] in ['ERROR', 'FAILED']:
                critical_issues.append(f"{finding['category']}: {finding['message']}")
        
        if critical_issues:
            for issue in critical_issues:
                print(f"❌ {issue}")
        else:
            print("✅ No critical issues found")
        
        # Key verification results
        print(f"\n🔍 KEY VERIFICATION RESULTS")
        print("-" * 40)
        
        key_verifications = [
            ("Salvador Palma BALANCE Investment", "SALVADOR_INVESTMENT"),
            ("Salvador Palma MT5 Account", "SALVADOR_MT5"),
            ("Fund Commitments Configuration", "FUND_COMMITMENTS"),
            ("Fund Performance Dashboard", "DASHBOARD")
        ]
        
        for verification, category in key_verifications:
            category_findings = [f for f in self.findings if f['category'] == category]
            success_count = len([f for f in category_findings if f['status'] == 'SUCCESS'])
            total_count = len(category_findings)
            
            if success_count > 0:
                print(f"✅ {verification}: {success_count}/{total_count} checks passed")
            else:
                print(f"❌ {verification}: No successful checks")

if __name__ == "__main__":
    tester = ComprehensiveFundPerformanceTester()
    success = tester.run_comprehensive_tests()
    sys.exit(0 if success else 1)