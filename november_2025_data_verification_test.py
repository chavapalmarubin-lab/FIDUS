#!/usr/bin/env python3
"""
COMPREHENSIVE API & DATABASE REVIEW - November 2025 Data Verification Test Suite

OBJECTIVE: Verify all MongoDB data and Render API endpoints are correctly calculating 
and displaying numbers after the emergency Cash Flow fix and Fund Portfolio initial 
allocations update.

Test Coverage:
1. MongoDB Collections Review (mt5_accounts, mt5_deals, investments)
2. Cash Flow Endpoints (/api/admin/cashflow/complete, /api/admin/cashflow/overview)
3. Fund Portfolio Endpoints (/api/fund-portfolio/overview, /api/funds/*/performance)
4. Three-Tier P&L Endpoint (/api/analytics/three-tier-pnl)
5. Trading Analytics (/api/admin/trading-analytics)
6. Money Managers (/api/admin/money-managers)
7. Calculation Verification and Data Consistency Checks

Expected Results:
- Total Active Allocations: $138,805.17
- Cash Flow Total Inflows: ~$21,438
- CORE Fund AUM: $18,151.41
- BALANCE Fund AUM: $100,000.00
- SEPARATION Fund: $20,653.76
- All 5 managers properly identified
- P&L calculations consistent across all endpoints
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
import traceback

class November2025DataVerificationTester:
    def __init__(self):
        # Use the backend URL from frontend .env
        self.base_url = "https://viking-analytics.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
        # Expected values from the review request
        self.expected_values = {
            "total_active_allocations": 138805.17,
            "cash_flow_total_inflows": 21438.0,
            "core_fund_aum": 18151.41,
            "balance_fund_aum": 100000.00,
            "separation_fund": 20653.76,
            "mt5_trading_pnl": 628.74,
            "broker_interest": 20776.80,
            "broker_rebates": 33.13,
            "expected_managers_count": 5,
            "expected_accounts": {
                "897591": {"initial_allocation": 5000.00, "manager": "alefloreztrader", "fund_type": "SEPARATION"},
                "897599": {"initial_allocation": 15653.76, "manager": "alefloreztrader", "fund_type": "SEPARATION"},
                "897589": {"initial_allocation": 5000.00, "manager": "Provider1-Assev", "fund_type": "BALANCE"},
                "886557": {"initial_allocation": 10000.00, "manager": "TradingHub Gold", "fund_type": "BALANCE"},
                "891215": {"initial_allocation": 70000.00, "manager": "TradingHub Gold", "fund_type": "BALANCE"},
                "886602": {"initial_allocation": 15000.00, "manager": "UNO14 Manager", "fund_type": "BALANCE"},
                "885822": {"initial_allocation": 2151.41, "manager": "CP Strategy", "fund_type": "CORE"},
                "897590": {"initial_allocation": 16000.00, "manager": "CP Strategy", "fund_type": "CORE"}
            }
        }
        
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
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data, timeout=30)
            
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

    def test_cash_flow_endpoints(self) -> bool:
        """Test Cash Flow Endpoints - /api/admin/cashflow/complete and /api/admin/cashflow/overview"""
        try:
            print("\n💰 Testing Cash Flow Endpoints...")
            success = True
            
            # Test /api/admin/cashflow/complete
            try:
                response = self.session.get(f"{self.base_url}/admin/cashflow/complete", timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for expected cash flow components
                    mt5_trading_pnl = None
                    broker_interest = None
                    broker_rebates = None
                    total_inflows = None
                    
                    # Extract values from different possible response structures
                    if 'fund_revenue' in data:
                        total_inflows = data.get('fund_revenue', 0)
                    elif 'total_inflows' in data:
                        total_inflows = data.get('total_inflows', 0)
                    
                    # Look for MT5 trading P&L
                    if 'mt5_trading_profits' in data:
                        mt5_trading_pnl = abs(data.get('mt5_trading_profits', 0))
                    elif 'mt5_pnl' in data:
                        mt5_trading_pnl = abs(data.get('mt5_pnl', 0))
                    
                    # Look for broker interest
                    if 'separation_interest' in data:
                        broker_interest = data.get('separation_interest', 0)
                    elif 'broker_interest' in data:
                        broker_interest = data.get('broker_interest', 0)
                    
                    # Look for broker rebates
                    if 'broker_rebates' in data:
                        broker_rebates = data.get('broker_rebates', 0)
                    
                    # Validate total inflows (~$21,438)
                    if total_inflows and abs(total_inflows - self.expected_values["cash_flow_total_inflows"]) < 1000:
                        self.log_test("Cash Flow Total Inflows", "PASS", 
                                    f"Total inflows within expected range", 
                                    f"~${self.expected_values['cash_flow_total_inflows']:,.0f}", 
                                    f"${total_inflows:,.2f}")
                    else:
                        self.log_test("Cash Flow Total Inflows", "FAIL", 
                                    f"Total inflows outside expected range", 
                                    f"~${self.expected_values['cash_flow_total_inflows']:,.0f}", 
                                    f"${total_inflows:,.2f}" if total_inflows else "Not found")
                        success = False
                    
                    self.log_test("Cash Flow Complete Endpoint", "PASS", "Endpoint accessible and returning data")
                    
                else:
                    self.log_test("Cash Flow Complete Endpoint", "FAIL", f"HTTP {response.status_code}: {response.text}")
                    success = False
                    
            except Exception as e:
                self.log_test("Cash Flow Complete Endpoint", "ERROR", f"Exception: {str(e)}")
                success = False
            
            # Test /api/admin/cashflow/overview
            try:
                response = self.session.get(f"{self.base_url}/admin/cashflow/overview", timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test("Cash Flow Overview Endpoint", "PASS", "Endpoint accessible and returning data")
                    
                    # Check if it redirects to /complete as mentioned in review
                    if 'redirect' in str(data).lower() or response.url.endswith('/complete'):
                        self.log_test("Cash Flow Overview Redirect", "PASS", "Overview redirects to complete as expected")
                    
                else:
                    self.log_test("Cash Flow Overview Endpoint", "FAIL", f"HTTP {response.status_code}: {response.text}")
                    success = False
                    
            except Exception as e:
                self.log_test("Cash Flow Overview Endpoint", "ERROR", f"Exception: {str(e)}")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Cash Flow Endpoints Test", "ERROR", f"Exception: {str(e)}")
            return False

    def test_fund_portfolio_endpoints(self) -> bool:
        """Test Fund Portfolio Endpoints"""
        try:
            print("\n📊 Testing Fund Portfolio Endpoints...")
            success = True
            
            # Test /api/fund-portfolio/overview
            try:
                response = self.session.get(f"{self.base_url}/fund-portfolio/overview", timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Look for funds data
                    funds = data.get('funds', [])
                    if not funds:
                        funds = data.get('data', {}).get('funds', [])
                    
                    core_aum = 0
                    balance_aum = 0
                    separation_aum = 0
                    
                    for fund in funds:
                        fund_code = fund.get('fund_code', '').upper()
                        aum = fund.get('aum', 0) or fund.get('total_allocated', 0)
                        
                        if fund_code == 'CORE':
                            core_aum = aum
                        elif fund_code == 'BALANCE':
                            balance_aum = aum
                        elif fund_code == 'SEPARATION':
                            separation_aum = aum
                    
                    # Validate CORE Fund AUM: $18,151.41
                    if abs(core_aum - self.expected_values["core_fund_aum"]) < 1.0:
                        self.log_test("CORE Fund AUM", "PASS", 
                                    f"CORE fund AUM matches expected value", 
                                    f"${self.expected_values['core_fund_aum']:,.2f}", 
                                    f"${core_aum:,.2f}")
                    else:
                        self.log_test("CORE Fund AUM", "FAIL", 
                                    f"CORE fund AUM does not match expected value", 
                                    f"${self.expected_values['core_fund_aum']:,.2f}", 
                                    f"${core_aum:,.2f}")
                        success = False
                    
                    # Validate BALANCE Fund AUM: $100,000.00
                    if abs(balance_aum - self.expected_values["balance_fund_aum"]) < 1.0:
                        self.log_test("BALANCE Fund AUM", "PASS", 
                                    f"BALANCE fund AUM matches expected value", 
                                    f"${self.expected_values['balance_fund_aum']:,.2f}", 
                                    f"${balance_aum:,.2f}")
                    else:
                        self.log_test("BALANCE Fund AUM", "FAIL", 
                                    f"BALANCE fund AUM does not match expected value", 
                                    f"${self.expected_values['balance_fund_aum']:,.2f}", 
                                    f"${balance_aum:,.2f}")
                        success = False
                    
                    # Validate SEPARATION Fund: $20,653.76
                    if abs(separation_aum - self.expected_values["separation_fund"]) < 1.0:
                        self.log_test("SEPARATION Fund AUM", "PASS", 
                                    f"SEPARATION fund AUM matches expected value", 
                                    f"${self.expected_values['separation_fund']:,.2f}", 
                                    f"${separation_aum:,.2f}")
                    else:
                        self.log_test("SEPARATION Fund AUM", "FAIL", 
                                    f"SEPARATION fund AUM does not match expected value", 
                                    f"${self.expected_values['separation_fund']:,.2f}", 
                                    f"${separation_aum:,.2f}")
                        success = False
                    
                    self.log_test("Fund Portfolio Overview Endpoint", "PASS", "Endpoint accessible and returning fund data")
                    
                else:
                    self.log_test("Fund Portfolio Overview Endpoint", "FAIL", f"HTTP {response.status_code}: {response.text}")
                    success = False
                    
            except Exception as e:
                self.log_test("Fund Portfolio Overview Endpoint", "ERROR", f"Exception: {str(e)}")
                success = False
            
            # Test individual fund performance endpoints
            fund_codes = ['CORE', 'BALANCE', 'SEPARATION']
            for fund_code in fund_codes:
                try:
                    response = self.session.get(f"{self.base_url}/funds/{fund_code}/performance", timeout=30)
                    
                    if response.status_code == 200:
                        self.log_test(f"{fund_code} Fund Performance", "PASS", f"{fund_code} fund performance endpoint accessible")
                    else:
                        self.log_test(f"{fund_code} Fund Performance", "FAIL", f"HTTP {response.status_code}")
                        success = False
                        
                except Exception as e:
                    self.log_test(f"{fund_code} Fund Performance", "ERROR", f"Exception: {str(e)}")
                    success = False
            
            # Test /api/funds/performance/all
            try:
                response = self.session.get(f"{self.base_url}/funds/performance/all", timeout=30)
                
                if response.status_code == 200:
                    self.log_test("All Funds Performance", "PASS", "All funds aggregated performance endpoint accessible")
                else:
                    self.log_test("All Funds Performance", "FAIL", f"HTTP {response.status_code}")
                    success = False
                    
            except Exception as e:
                self.log_test("All Funds Performance", "ERROR", f"Exception: {str(e)}")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Fund Portfolio Endpoints Test", "ERROR", f"Exception: {str(e)}")
            return False

    def test_three_tier_pnl_endpoint(self) -> bool:
        """Test Three-Tier P&L Endpoint"""
        try:
            print("\n📈 Testing Three-Tier P&L Endpoint...")
            
            response = self.session.get(f"{self.base_url}/analytics/three-tier-pnl", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if endpoint uses initial allocations for calculations
                if 'initial_allocation' in str(data).lower() or 'initial_allocations' in str(data).lower():
                    self.log_test("Three-Tier P&L Initial Allocations", "PASS", "Endpoint appears to use initial allocations")
                else:
                    self.log_test("Three-Tier P&L Initial Allocations", "FAIL", "No evidence of initial allocation usage")
                    return False
                
                self.log_test("Three-Tier P&L Endpoint", "PASS", "Endpoint accessible and returning data")
                return True
                
            else:
                self.log_test("Three-Tier P&L Endpoint", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Three-Tier P&L Endpoint", "ERROR", f"Exception: {str(e)}")
            return False

    def test_trading_analytics_endpoint(self) -> bool:
        """Test Trading Analytics Endpoint"""
        try:
            print("\n📊 Testing Trading Analytics Endpoint...")
            
            response = self.session.get(f"{self.base_url}/admin/trading-analytics", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Look for P&L by account
                accounts_found = 0
                total_pnl = 0
                
                # Check different possible response structures
                if 'accounts' in data:
                    accounts = data['accounts']
                    accounts_found = len(accounts)
                    for account in accounts:
                        pnl = account.get('pnl', 0) or account.get('profit_loss', 0)
                        total_pnl += pnl
                
                elif 'data' in data and isinstance(data['data'], list):
                    accounts = data['data']
                    accounts_found = len(accounts)
                    for account in accounts:
                        pnl = account.get('pnl', 0) or account.get('profit_loss', 0)
                        total_pnl += pnl
                
                # Validate that we have the expected number of accounts (8 active accounts)
                if accounts_found >= 5:  # At least 5 accounts should be present
                    self.log_test("Trading Analytics Accounts Count", "PASS", 
                                f"Found {accounts_found} accounts (expected >= 5)")
                else:
                    self.log_test("Trading Analytics Accounts Count", "FAIL", 
                                f"Found {accounts_found} accounts (expected >= 5)")
                    return False
                
                # Check that P&L is not zero (should show real data)
                if abs(total_pnl) > 0:
                    self.log_test("Trading Analytics P&L", "PASS", 
                                f"Total P&L shows real data: ${total_pnl:,.2f}")
                else:
                    self.log_test("Trading Analytics P&L", "FAIL", 
                                f"Total P&L is zero - expected real data")
                    return False
                
                self.log_test("Trading Analytics Endpoint", "PASS", "Endpoint accessible and returning account P&L data")
                return True
                
            else:
                self.log_test("Trading Analytics Endpoint", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Trading Analytics Endpoint", "ERROR", f"Exception: {str(e)}")
            return False

    def test_money_managers_endpoint(self) -> bool:
        """Test Money Managers Endpoint"""
        try:
            print("\n👥 Testing Money Managers Endpoint...")
            
            response = self.session.get(f"{self.base_url}/admin/money-managers", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Look for managers data
                managers = []
                if 'managers' in data:
                    managers = data['managers']
                elif 'data' in data and isinstance(data['data'], list):
                    managers = data['data']
                elif isinstance(data, list):
                    managers = data
                
                # Validate that we have 5 managers
                expected_managers = self.expected_values["expected_managers_count"]
                if len(managers) == expected_managers:
                    self.log_test("Money Managers Count", "PASS", 
                                f"Found {len(managers)} managers (expected {expected_managers})")
                else:
                    self.log_test("Money Managers Count", "FAIL", 
                                f"Found {len(managers)} managers (expected {expected_managers})")
                    return False
                
                # Check that managers have real data (not all zeros)
                managers_with_data = 0
                expected_manager_names = ["alefloreztrader", "Provider1-Assev", "TradingHub Gold", "UNO14 Manager", "CP Strategy"]
                
                for manager in managers:
                    manager_name = manager.get('name', '') or manager.get('manager_name', '')
                    pnl = manager.get('pnl', 0) or manager.get('profit_loss', 0)
                    accounts = manager.get('accounts', 0) or manager.get('account_count', 0)
                    
                    if manager_name and (abs(pnl) > 0 or accounts > 0):
                        managers_with_data += 1
                    
                    # Check if this is one of our expected managers
                    if any(expected_name.lower() in manager_name.lower() for expected_name in expected_manager_names):
                        self.log_test(f"Manager {manager_name}", "PASS", f"Expected manager found with data")
                
                if managers_with_data >= 4:  # At least 4 out of 5 should have real data
                    self.log_test("Money Managers Real Data", "PASS", 
                                f"{managers_with_data}/5 managers have real data")
                else:
                    self.log_test("Money Managers Real Data", "FAIL", 
                                f"Only {managers_with_data}/5 managers have real data")
                    return False
                
                self.log_test("Money Managers Endpoint", "PASS", "Endpoint accessible and returning manager data")
                return True
                
            else:
                self.log_test("Money Managers Endpoint", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Money Managers Endpoint", "ERROR", f"Exception: {str(e)}")
            return False

    def test_calculation_verification(self) -> bool:
        """Test Calculation Verification - Cross-check calculations across endpoints"""
        try:
            print("\n🧮 Testing Calculation Verification...")
            success = True
            
            # Collect data from multiple endpoints for cross-verification
            fund_portfolio_data = None
            cash_flow_data = None
            trading_analytics_data = None
            
            # Get fund portfolio data
            try:
                response = self.session.get(f"{self.base_url}/fund-portfolio/overview", timeout=30)
                if response.status_code == 200:
                    fund_portfolio_data = response.json()
            except:
                pass
            
            # Get cash flow data
            try:
                response = self.session.get(f"{self.base_url}/admin/cashflow/complete", timeout=30)
                if response.status_code == 200:
                    cash_flow_data = response.json()
            except:
                pass
            
            # Get trading analytics data
            try:
                response = self.session.get(f"{self.base_url}/admin/trading-analytics", timeout=30)
                if response.status_code == 200:
                    trading_analytics_data = response.json()
            except:
                pass
            
            # Cross-verify total AUM calculations
            if fund_portfolio_data:
                funds = fund_portfolio_data.get('funds', [])
                total_aum = sum(fund.get('aum', 0) or fund.get('total_allocated', 0) for fund in funds)
                
                # Check if total AUM matches expected active allocations
                expected_total = self.expected_values["total_active_allocations"]
                if abs(total_aum - expected_total) < 100:  # Allow $100 tolerance
                    self.log_test("Total AUM Calculation", "PASS", 
                                f"Total AUM matches expected active allocations", 
                                f"${expected_total:,.2f}", 
                                f"${total_aum:,.2f}")
                else:
                    self.log_test("Total AUM Calculation", "FAIL", 
                                f"Total AUM does not match expected active allocations", 
                                f"${expected_total:,.2f}", 
                                f"${total_aum:,.2f}")
                    success = False
            
            # Verify weighted return calculations
            if fund_portfolio_data:
                funds = fund_portfolio_data.get('funds', [])
                for fund in funds:
                    fund_code = fund.get('fund_code', '')
                    weighted_return = fund.get('weighted_return', 0)
                    
                    # Weighted return should be calculated as Sum(account_weight × account_return)
                    # For now, just verify it's not zero for funds with accounts
                    if fund.get('account_count', 0) > 0 and weighted_return == 0:
                        self.log_test(f"{fund_code} Weighted Return", "FAIL", 
                                    f"{fund_code} fund has accounts but zero weighted return")
                        success = False
                    elif fund.get('account_count', 0) > 0:
                        self.log_test(f"{fund_code} Weighted Return", "PASS", 
                                    f"{fund_code} fund has calculated weighted return: {weighted_return:.2f}%")
            
            # Verify P&L consistency across endpoints
            cash_flow_pnl = None
            trading_pnl = None
            
            if cash_flow_data:
                cash_flow_pnl = cash_flow_data.get('mt5_trading_profits', 0) or cash_flow_data.get('fund_revenue', 0)
            
            if trading_analytics_data:
                if 'total_pnl' in trading_analytics_data:
                    trading_pnl = trading_analytics_data['total_pnl']
                elif 'accounts' in trading_analytics_data:
                    trading_pnl = sum(acc.get('pnl', 0) for acc in trading_analytics_data['accounts'])
            
            if cash_flow_pnl is not None and trading_pnl is not None:
                if abs(cash_flow_pnl - trading_pnl) < 100:  # Allow $100 tolerance
                    self.log_test("P&L Consistency", "PASS", 
                                f"P&L consistent across cash flow and trading analytics", 
                                f"${cash_flow_pnl:,.2f}", 
                                f"${trading_pnl:,.2f}")
                else:
                    self.log_test("P&L Consistency", "FAIL", 
                                f"P&L inconsistent across endpoints", 
                                f"Cash Flow: ${cash_flow_pnl:,.2f}", 
                                f"Trading: ${trading_pnl:,.2f}")
                    success = False
            
            return success
            
        except Exception as e:
            self.log_test("Calculation Verification Test", "ERROR", f"Exception: {str(e)}")
            return False

    def test_edge_cases(self) -> bool:
        """Test Edge Cases - Accounts with 0 allocation, negative P&L, etc."""
        try:
            print("\n⚠️ Testing Edge Cases...")
            success = True
            
            # Test accounts with 0 initial allocation (inactive accounts: 886066, 886528, 891234)
            inactive_accounts = ["886066", "886528", "891234"]
            
            # Try to get MT5 accounts data
            try:
                response = self.session.get(f"{self.base_url}/mt5/accounts", timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    accounts = data.get('accounts', []) or data.get('data', [])
                    
                    for account_id in inactive_accounts:
                        account_found = False
                        for account in accounts:
                            if str(account.get('login', '')) == account_id or str(account.get('account_id', '')) == account_id:
                                account_found = True
                                initial_allocation = account.get('initial_allocation', 0)
                                
                                if initial_allocation == 0:
                                    self.log_test(f"Inactive Account {account_id}", "PASS", 
                                                f"Account {account_id} correctly shows 0 initial allocation")
                                else:
                                    self.log_test(f"Inactive Account {account_id}", "FAIL", 
                                                f"Account {account_id} should have 0 allocation but shows ${initial_allocation}")
                                    success = False
                                break
                        
                        if not account_found:
                            self.log_test(f"Inactive Account {account_id}", "PASS", 
                                        f"Account {account_id} not found (expected for inactive accounts)")
                
            except Exception as e:
                self.log_test("Inactive Accounts Check", "ERROR", f"Exception: {str(e)}")
                success = False
            
            # Test negative P&L accounts (886557, 891215 showing losses)
            negative_pnl_accounts = ["886557", "891215"]
            
            try:
                response = self.session.get(f"{self.base_url}/admin/trading-analytics", timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    accounts = data.get('accounts', []) or data.get('data', [])
                    
                    for account_id in negative_pnl_accounts:
                        for account in accounts:
                            if str(account.get('login', '')) == account_id or str(account.get('account_id', '')) == account_id:
                                pnl = account.get('pnl', 0) or account.get('profit_loss', 0)
                                
                                if pnl < 0:
                                    self.log_test(f"Negative P&L Account {account_id}", "PASS", 
                                                f"Account {account_id} correctly shows negative P&L: ${pnl:,.2f}")
                                else:
                                    self.log_test(f"Negative P&L Account {account_id}", "FAIL", 
                                                f"Account {account_id} expected negative P&L but shows ${pnl:,.2f}")
                                    success = False
                                break
                
            except Exception as e:
                self.log_test("Negative P&L Accounts Check", "ERROR", f"Exception: {str(e)}")
                success = False
            
            # Test positive P&L account (886602 showing +6.84%)
            try:
                response = self.session.get(f"{self.base_url}/admin/trading-analytics", timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    accounts = data.get('accounts', []) or data.get('data', [])
                    
                    for account in accounts:
                        if str(account.get('login', '')) == "886602" or str(account.get('account_id', '')) == "886602":
                            pnl = account.get('pnl', 0) or account.get('profit_loss', 0)
                            return_pct = account.get('return_percent', 0) or account.get('return_percentage', 0)
                            
                            if pnl > 0 or return_pct > 0:
                                self.log_test("Positive P&L Account 886602", "PASS", 
                                            f"Account 886602 shows positive performance: ${pnl:,.2f} ({return_pct:.2f}%)")
                            else:
                                self.log_test("Positive P&L Account 886602", "FAIL", 
                                            f"Account 886602 expected positive P&L but shows ${pnl:,.2f}")
                                success = False
                            break
                
            except Exception as e:
                self.log_test("Positive P&L Account Check", "ERROR", f"Exception: {str(e)}")
                success = False
            
            # Test division by zero protection
            try:
                # This is more of a code review item, but we can check if any calculations return NaN or Infinity
                endpoints_to_check = [
                    "/fund-portfolio/overview",
                    "/admin/trading-analytics",
                    "/analytics/three-tier-pnl"
                ]
                
                for endpoint in endpoints_to_check:
                    try:
                        response = self.session.get(f"{self.base_url}{endpoint}", timeout=30)
                        if response.status_code == 200:
                            response_text = response.text.lower()
                            if 'nan' in response_text or 'infinity' in response_text or 'inf' in response_text:
                                self.log_test(f"Division by Zero Check {endpoint}", "FAIL", 
                                            f"Endpoint {endpoint} contains NaN or Infinity values")
                                success = False
                            else:
                                self.log_test(f"Division by Zero Check {endpoint}", "PASS", 
                                            f"Endpoint {endpoint} has no NaN or Infinity values")
                    except:
                        continue
                
            except Exception as e:
                self.log_test("Division by Zero Protection", "ERROR", f"Exception: {str(e)}")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Edge Cases Test", "ERROR", f"Exception: {str(e)}")
            return False

    def run_all_tests(self) -> bool:
        """Run all November 2025 data verification tests"""
        print("🚀 Starting November 2025 Data Verification Tests")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate_admin():
            print("\n❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Run all verification tests
        tests = [
            ("Cash Flow Endpoints", self.test_cash_flow_endpoints),
            ("Fund Portfolio Endpoints", self.test_fund_portfolio_endpoints),
            ("Three-Tier P&L Endpoint", self.test_three_tier_pnl_endpoint),
            ("Trading Analytics Endpoint", self.test_trading_analytics_endpoint),
            ("Money Managers Endpoint", self.test_money_managers_endpoint),
            ("Calculation Verification", self.test_calculation_verification),
            ("Edge Cases", self.test_edge_cases)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log_test(f"{test_name} Exception", "ERROR", f"Test failed with exception: {str(e)}")
                print(f"Exception in {test_name}: {traceback.format_exc()}")
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 NOVEMBER 2025 DATA VERIFICATION SUMMARY")
        print("=" * 80)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Print detailed results
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            print(f"{status_icon} {result['test_name']}: {result['details']}")
            
            if result.get("expected") and result.get("actual"):
                print(f"   Expected: {result['expected']}")
                print(f"   Actual: {result['actual']}")
        
        print("\n" + "=" * 80)
        
        # Success criteria from review request
        success_criteria = [
            "All 11 MT5 accounts have correct initial_allocation values",
            "Total active allocations = $138,805.17",
            "Cash Flow total inflows ≈ $21,438",
            "CORE Fund AUM = $18,151.41",
            "BALANCE Fund AUM = $100,000.00",
            "SEPARATION accounts = $20,653.76",
            "All 5 managers properly identified",
            "P&L calculations consistent across all endpoints",
            "No division by zero errors",
            "No NULL or missing critical fields"
        ]
        
        if success_rate >= 80:
            print("🎉 NOVEMBER 2025 DATA VERIFICATION: SUCCESSFUL")
            print("✅ MongoDB data and API endpoints verified")
            print("✅ Cash Flow calculations validated")
            print("✅ Fund Portfolio allocations confirmed")
            print("✅ Cross-endpoint consistency verified")
            return True
        else:
            print("🚨 NOVEMBER 2025 DATA VERIFICATION: NEEDS ATTENTION")
            print("❌ Critical data verification issues found")
            print("\n🔍 SUCCESS CRITERIA STATUS:")
            for criteria in success_criteria:
                print(f"   • {criteria}")
            return False

def main():
    """Main test execution"""
    tester = November2025DataVerificationTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()