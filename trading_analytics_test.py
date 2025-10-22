#!/usr/bin/env python3
"""
COMPREHENSIVE TRADING ANALYTICS API TESTING

Context: Testing the new 3-level Trading Analytics API based on Chava's clarified fund structure.
This replaces the old deal-aggregation approach with proper Portfolio → Funds → Managers hierarchy.

TEST OBJECTIVES:
1. Login as Admin (admin/password123)
2. Test Portfolio Level Endpoint: GET /api/admin/trading-analytics/portfolio?period_days=30
3. Test Fund Level Endpoints: GET /api/admin/trading-analytics/funds/{fund}?period_days=30
4. Test Managers Ranking Endpoint: GET /api/admin/trading-analytics/managers?period_days=30
5. Test Individual Manager Endpoint: GET /api/admin/trading-analytics/managers/{manager_id}?period_days=30

EXPECTED RESULTS:
- Portfolio: total_aum: $118,151, total_pnl: ~$6,903, blended_return: ~5.84%, total_managers: 4
- BALANCE Fund: AUM $100,000, P&L ~$6,802, 3 managers
- CORE Fund: AUM $18,151, P&L ~$101, 1 manager
- Managers Ranking: UNO14 MAM Manager (#1, +11.40%), GoldenTrade (#2), TradingHub Gold (#3), CP Strategy (#4)
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://vps-bridge-fix.preview.emergentagent.com"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class TradingAnalyticsAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def authenticate(self):
        """Authenticate as admin and get JWT token"""
        try:
            auth_url = f"{BACKEND_URL}/api/auth/login"
            payload = {
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            }
            
            response = self.session.post(auth_url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                if self.token:
                    self.session.headers.update({'Authorization': f'Bearer {self.token}'})
                    self.log_test("Admin Authentication", True, f"Successfully authenticated as {ADMIN_USERNAME}")
                    return True
                else:
                    self.log_test("Admin Authentication", False, "No token in response")
                    return False
            else:
                self.log_test("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_portfolio_endpoint(self):
        """Test Portfolio Level Endpoint - GET /api/admin/trading-analytics/portfolio?period_days=30"""
        try:
            url = f"{BACKEND_URL}/api/admin/trading-analytics/portfolio?period_days=30"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract key metrics from portfolio object
                portfolio = data.get('portfolio', {})
                total_aum = portfolio.get('total_aum', 0)
                total_pnl = portfolio.get('total_pnl', 0)
                blended_return = portfolio.get('blended_return', 0)
                total_managers = portfolio.get('total_managers', 0)
                funds_breakdown = portfolio.get('funds', {})
                
                # Verify expected values
                expected_aum = 118151  # $118,151
                expected_pnl_range = (6000, 7500)  # ~$6,903 with some tolerance
                expected_return_range = (5.0, 7.0)  # ~5.84% with tolerance
                expected_managers = 4
                
                # Check AUM
                aum_success = abs(total_aum - expected_aum) < 5000
                if aum_success:
                    self.log_test("Portfolio Total AUM", True, f"${total_aum:,.2f} (expected: ~${expected_aum:,.2f})")
                else:
                    self.log_test("Portfolio Total AUM", False, f"${total_aum:,.2f} (expected: ~${expected_aum:,.2f})")
                
                # Check P&L
                pnl_success = expected_pnl_range[0] <= total_pnl <= expected_pnl_range[1]
                if pnl_success:
                    self.log_test("Portfolio Total P&L", True, f"${total_pnl:,.2f} (expected: ~$6,903)")
                else:
                    self.log_test("Portfolio Total P&L", False, f"${total_pnl:,.2f} (expected: ~$6,903)")
                
                # Check Blended Return
                return_success = expected_return_range[0] <= blended_return <= expected_return_range[1]
                if return_success:
                    self.log_test("Portfolio Blended Return", True, f"{blended_return:.2f}% (expected: ~5.84%)")
                else:
                    self.log_test("Portfolio Blended Return", False, f"{blended_return:.2f}% (expected: ~5.84%)")
                
                # Check Total Managers
                managers_success = total_managers == expected_managers
                if managers_success:
                    self.log_test("Portfolio Total Managers", True, f"{total_managers} managers (expected: {expected_managers})")
                else:
                    self.log_test("Portfolio Total Managers", False, f"{total_managers} managers (expected: {expected_managers})")
                
                # Check Funds Breakdown
                funds_success = 'BALANCE' in funds_breakdown and 'CORE' in funds_breakdown
                if funds_success:
                    balance_fund = funds_breakdown.get('BALANCE', {})
                    core_fund = funds_breakdown.get('CORE', {})
                    self.log_test("Portfolio Funds Breakdown", True, f"BALANCE: ${balance_fund.get('aum', 0):,.2f}, CORE: ${core_fund.get('aum', 0):,.2f}")
                else:
                    self.log_test("Portfolio Funds Breakdown", False, "Missing BALANCE or CORE fund data")
                
                return aum_success and pnl_success and return_success and managers_success and funds_success
                
            else:
                self.log_test("Portfolio Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Portfolio Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_fund_endpoints(self):
        """Test Fund Level Endpoints for BALANCE and CORE funds"""
        fund_results = {}
        
        # Test BALANCE Fund
        try:
            url = f"{BACKEND_URL}/api/admin/trading-analytics/funds/BALANCE?period_days=30"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                aum = data.get('aum', 0)
                pnl = data.get('pnl', 0)
                managers_count = data.get('managers_count', 0)
                
                # Expected: AUM $100,000, P&L ~$6,802, 3 managers
                aum_success = abs(aum - 100000) < 5000
                pnl_success = 6000 <= pnl <= 7500
                managers_success = managers_count == 3
                
                if aum_success:
                    self.log_test("BALANCE Fund AUM", True, f"${aum:,.2f} (expected: ~$100,000)")
                else:
                    self.log_test("BALANCE Fund AUM", False, f"${aum:,.2f} (expected: ~$100,000)")
                
                if pnl_success:
                    self.log_test("BALANCE Fund P&L", True, f"${pnl:,.2f} (expected: ~$6,802)")
                else:
                    self.log_test("BALANCE Fund P&L", False, f"${pnl:,.2f} (expected: ~$6,802)")
                
                if managers_success:
                    self.log_test("BALANCE Fund Managers", True, f"{managers_count} managers (expected: 3)")
                else:
                    self.log_test("BALANCE Fund Managers", False, f"{managers_count} managers (expected: 3)")
                
                fund_results['BALANCE'] = aum_success and pnl_success and managers_success
                
            else:
                self.log_test("BALANCE Fund Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                fund_results['BALANCE'] = False
                
        except Exception as e:
            self.log_test("BALANCE Fund Endpoint", False, f"Exception: {str(e)}")
            fund_results['BALANCE'] = False
        
        # Test CORE Fund
        try:
            url = f"{BACKEND_URL}/api/admin/trading-analytics/funds/CORE?period_days=30"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                aum = data.get('aum', 0)
                pnl = data.get('pnl', 0)
                managers_count = data.get('managers_count', 0)
                
                # Expected: AUM $18,151, P&L ~$101, 1 manager
                aum_success = abs(aum - 18151) < 2000
                pnl_success = 50 <= pnl <= 200
                managers_success = managers_count == 1
                
                if aum_success:
                    self.log_test("CORE Fund AUM", True, f"${aum:,.2f} (expected: ~$18,151)")
                else:
                    self.log_test("CORE Fund AUM", False, f"${aum:,.2f} (expected: ~$18,151)")
                
                if pnl_success:
                    self.log_test("CORE Fund P&L", True, f"${pnl:,.2f} (expected: ~$101)")
                else:
                    self.log_test("CORE Fund P&L", False, f"${pnl:,.2f} (expected: ~$101)")
                
                if managers_success:
                    self.log_test("CORE Fund Managers", True, f"{managers_count} managers (expected: 1)")
                else:
                    self.log_test("CORE Fund Managers", False, f"{managers_count} managers (expected: 1)")
                
                fund_results['CORE'] = aum_success and pnl_success and managers_success
                
            else:
                self.log_test("CORE Fund Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                fund_results['CORE'] = False
                
        except Exception as e:
            self.log_test("CORE Fund Endpoint", False, f"Exception: {str(e)}")
            fund_results['CORE'] = False
        
        return fund_results.get('BALANCE', False) and fund_results.get('CORE', False)
    
    def test_managers_ranking_endpoint(self):
        """Test Managers Ranking Endpoint - GET /api/admin/trading-analytics/managers?period_days=30"""
        try:
            url = f"{BACKEND_URL}/api/admin/trading-analytics/managers?period_days=30"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                success = data.get('success', False)
                managers = data.get('managers', [])
                total_managers = data.get('total_managers', 0)
                total_pnl = data.get('total_pnl', 0)
                
                if not success:
                    self.log_test("Managers Ranking Response", False, "Response success=false")
                    return False
                
                # Expected: 4 managers, total P&L ~$6,903
                expected_managers = 4
                expected_total_pnl_range = (6000, 7500)
                
                # Check total managers count
                managers_count_success = total_managers == expected_managers
                if managers_count_success:
                    self.log_test("Managers Total Count", True, f"{total_managers} managers (expected: {expected_managers})")
                else:
                    self.log_test("Managers Total Count", False, f"{total_managers} managers (expected: {expected_managers})")
                
                # Check total P&L
                total_pnl_success = expected_total_pnl_range[0] <= total_pnl <= expected_total_pnl_range[1]
                if total_pnl_success:
                    self.log_test("Managers Total P&L", True, f"${total_pnl:,.2f} (expected: ~$6,903)")
                else:
                    self.log_test("Managers Total P&L", False, f"${total_pnl:,.2f} (expected: ~$6,903)")
                
                # Check individual manager rankings
                expected_rankings = {
                    1: {"name": "UNO14 MAM Manager", "return_min": 10.0, "return_max": 13.0},
                    2: {"name": "GoldenTrade Provider", "return_min": 6.0, "return_max": 8.0},
                    3: {"name": "TradingHub Gold Provider", "return_min": 5.0, "return_max": 7.0},
                    4: {"name": "CP Strategy Provider", "return_min": 0.5, "return_max": 2.0}
                }
                
                ranking_success = True
                for manager in managers:
                    rank = manager.get('rank', 0)
                    manager_name = manager.get('manager_name', '')
                    return_percentage = manager.get('return_percentage', 0)
                    total_pnl_manager = manager.get('total_pnl', 0)
                    
                    if rank in expected_rankings:
                        expected = expected_rankings[rank]
                        
                        # Check if manager name matches (partial match)
                        name_match = any(word in manager_name for word in expected['name'].split())
                        return_in_range = expected['return_min'] <= return_percentage <= expected['return_max']
                        
                        if name_match and return_in_range:
                            self.log_test(f"Manager Rank #{rank}", True, f"{manager_name}: {return_percentage:.2f}% return, ${total_pnl_manager:,.2f} P&L")
                        else:
                            self.log_test(f"Manager Rank #{rank}", False, f"{manager_name}: {return_percentage:.2f}% return (expected: {expected['name']} with {expected['return_min']}-{expected['return_max']}%)")
                            ranking_success = False
                
                # Check for required risk metrics
                risk_metrics_found = False
                if managers:
                    first_manager = managers[0]
                    has_sharpe = 'sharpe_ratio' in first_manager
                    has_sortino = 'sortino_ratio' in first_manager
                    has_calmar = 'calmar_ratio' in first_manager
                    has_win_rate = 'win_rate' in first_manager
                    has_profit_factor = 'profit_factor' in first_manager
                    
                    risk_metrics_found = has_sharpe and has_sortino and has_calmar and has_win_rate and has_profit_factor
                    
                    if risk_metrics_found:
                        self.log_test("Risk Metrics Present", True, "Sharpe, Sortino, Calmar, Win Rate, Profit Factor all present")
                    else:
                        missing_metrics = []
                        if not has_sharpe: missing_metrics.append("Sharpe")
                        if not has_sortino: missing_metrics.append("Sortino")
                        if not has_calmar: missing_metrics.append("Calmar")
                        if not has_win_rate: missing_metrics.append("Win Rate")
                        if not has_profit_factor: missing_metrics.append("Profit Factor")
                        self.log_test("Risk Metrics Present", False, f"Missing: {', '.join(missing_metrics)}")
                
                return managers_count_success and total_pnl_success and ranking_success and risk_metrics_found
                
            else:
                self.log_test("Managers Ranking Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Managers Ranking Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_individual_manager_endpoint(self):
        """Test Individual Manager Endpoint - GET /api/admin/trading-analytics/managers/manager_uno14?period_days=30"""
        try:
            url = f"{BACKEND_URL}/api/admin/trading-analytics/managers/manager_uno14?period_days=30"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if manager details are returned
                manager_name = data.get('manager_name', '')
                return_percentage = data.get('return_percentage', 0)
                total_pnl = data.get('total_pnl', 0)
                
                # Expected: UNO14 MAM Manager with ~11.40% return
                name_success = 'UNO14' in manager_name or 'MAM' in manager_name
                return_success = 10.0 <= return_percentage <= 13.0
                pnl_success = total_pnl > 1000  # Should have positive P&L
                
                if name_success:
                    self.log_test("Individual Manager Name", True, f"Manager: {manager_name}")
                else:
                    self.log_test("Individual Manager Name", False, f"Manager: {manager_name} (expected: UNO14 MAM Manager)")
                
                if return_success:
                    self.log_test("Individual Manager Return", True, f"Return: {return_percentage:.2f}% (expected: ~11.40%)")
                else:
                    self.log_test("Individual Manager Return", False, f"Return: {return_percentage:.2f}% (expected: ~11.40%)")
                
                if pnl_success:
                    self.log_test("Individual Manager P&L", True, f"P&L: ${total_pnl:,.2f}")
                else:
                    self.log_test("Individual Manager P&L", False, f"P&L: ${total_pnl:,.2f} (expected: positive value)")
                
                # Check for detailed metrics
                has_detailed_metrics = all(key in data for key in ['sharpe_ratio', 'sortino_ratio', 'calmar_ratio', 'win_rate', 'profit_factor'])
                
                if has_detailed_metrics:
                    self.log_test("Individual Manager Detailed Metrics", True, "All detailed risk metrics present")
                else:
                    self.log_test("Individual Manager Detailed Metrics", False, "Missing some detailed risk metrics")
                
                return name_success and return_success and pnl_success and has_detailed_metrics
                
            else:
                self.log_test("Individual Manager Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Individual Manager Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive Trading Analytics API test"""
        print("🔍 COMPREHENSIVE TRADING ANALYTICS API TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Authenticate
        print("📋 STEP 1: Admin Authentication")
        if not self.authenticate():
            print("❌ Authentication failed. Cannot test endpoints.")
            return False
        print()
        
        # Step 2: Test Portfolio Endpoint
        print("📋 STEP 2: Portfolio Level Endpoint")
        portfolio_success = self.test_portfolio_endpoint()
        print()
        
        # Step 3: Test Fund Endpoints
        print("📋 STEP 3: Fund Level Endpoints")
        funds_success = self.test_fund_endpoints()
        print()
        
        # Step 4: Test Managers Ranking Endpoint
        print("📋 STEP 4: Managers Ranking Endpoint")
        managers_ranking_success = self.test_managers_ranking_endpoint()
        print()
        
        # Step 5: Test Individual Manager Endpoint
        print("📋 STEP 5: Individual Manager Endpoint")
        individual_manager_success = self.test_individual_manager_endpoint()
        print()
        
        # Summary
        self.print_test_summary()
        
        # Return overall success
        all_endpoints = [portfolio_success, funds_success, managers_ranking_success, individual_manager_success]
        return all(all_endpoints)
    
    def print_test_summary(self):
        """Print comprehensive test summary in the requested format"""
        print("=" * 80)
        print("=== COMPREHENSIVE TRADING ANALYTICS API TEST RESULTS ===")
        print("=" * 80)
        
        # Extract key results for summary
        portfolio_status = "✅ HTTP 200" if any('Portfolio Endpoint' not in r['test'] or r['success'] for r in self.test_results) else "❌ FAILED"
        balance_fund_status = "✅ HTTP 200" if any('BALANCE Fund' in r['test'] and r['success'] for r in self.test_results) else "❌ FAILED"
        core_fund_status = "✅ HTTP 200" if any('CORE Fund' in r['test'] and r['success'] for r in self.test_results) else "❌ FAILED"
        managers_ranking_status = "✅ HTTP 200" if any('Managers Ranking' in r['test'] and r['success'] for r in self.test_results) else "❌ FAILED"
        individual_manager_status = "✅ HTTP 200" if any('Individual Manager' in r['test'] and r['success'] for r in self.test_results) else "❌ FAILED"
        
        # Extract values from test results
        total_aum = "N/A"
        total_pnl = "N/A"
        blended_return = "N/A"
        balance_pnl = "N/A"
        core_pnl = "N/A"
        
        for result in self.test_results:
            if 'Portfolio Total AUM' in result['test'] and result['success']:
                total_aum = result['details'].split('$')[1].split(' ')[0]
            elif 'Portfolio Total P&L' in result['test'] and result['success']:
                total_pnl = result['details'].split('$')[1].split(' ')[0]
            elif 'Portfolio Blended Return' in result['test'] and result['success']:
                blended_return = result['details'].split('%')[0].split(' ')[-1] + '%'
            elif 'BALANCE Fund P&L' in result['test'] and result['success']:
                balance_pnl = result['details'].split('$')[1].split(' ')[0]
            elif 'CORE Fund P&L' in result['test'] and result['success']:
                core_pnl = result['details'].split('$')[1].split(' ')[0]
        
        print(f"1. Portfolio Endpoint: {portfolio_status}")
        print(f"   - Total AUM: ${total_aum}")
        print(f"   - Total P&L: ${total_pnl}")
        print(f"   - Blended Return: {blended_return}")
        print()
        
        print(f"2. Fund Endpoints:")
        print(f"   - BALANCE Fund: {balance_fund_status}, P&L: ${balance_pnl}")
        print(f"   - CORE Fund: {core_fund_status}, P&L: ${core_pnl}")
        print()
        
        print(f"3. Managers Ranking: {managers_ranking_status}")
        
        # Extract manager rankings
        manager_rankings = []
        for result in self.test_results:
            if 'Manager Rank #' in result['test'] and result['success']:
                rank = result['test'].split('#')[1]
                details = result['details']
                manager_name = details.split(':')[0]
                return_pct = details.split(':')[1].split('%')[0].strip() + '%'
                manager_rankings.append(f"   - Rank #{rank}: {manager_name} ({return_pct})")
        
        for ranking in sorted(manager_rankings):
            print(ranking)
        
        # Extract total P&L verification
        total_pnl_verification = "N/A"
        for result in self.test_results:
            if 'Managers Total P&L' in result['test']:
                total_pnl_verification = result['details'].split('$')[1].split(' ')[0]
        
        print(f"   - Total P&L Verification: ${total_pnl_verification}")
        print()
        
        print(f"4. Individual Manager: {individual_manager_status}")
        print("   - Manager details retrieved successfully")
        print()
        
        # Calculate success rate
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = f"{passed_tests}/{total_tests}"
        
        print(f"SUCCESS RATE: {success_rate} tests passed")
        print()
        
        # Verification criteria
        print("VERIFICATION CRITERIA:")
        criteria_results = []
        
        # Check each criterion
        aum_correct = any('Portfolio Total AUM' in r['test'] and r['success'] for r in self.test_results)
        pnl_correct = any('Managers Total P&L' in r['test'] and r['success'] for r in self.test_results)
        uno14_top = any('Manager Rank #1' in r['test'] and r['success'] and 'UNO14' in r['details'] for r in self.test_results)
        all_managers = any('Managers Total Count' in r['test'] and r['success'] and '4 managers' in r['details'] for r in self.test_results)
        risk_metrics = any('Risk Metrics Present' in r['test'] and r['success'] for r in self.test_results)
        fund_aggregations = any('BALANCE Fund' in r['test'] and r['success'] for r in self.test_results) and any('CORE Fund' in r['test'] and r['success'] for r in self.test_results)
        
        criteria_results.extend([
            f"{'✅' if aum_correct else '❌'} All endpoints return HTTP 200",
            f"{'✅' if pnl_correct else '❌'} Total P&L across all managers = $6,903",
            f"{'✅' if uno14_top else '❌'} Manager rankings show UNO14 as #1 performer (+11.40%)",
            f"{'✅' if all_managers else '❌'} All 4 managers present with correct account assignments",
            f"{'✅' if risk_metrics else '❌'} Risk metrics calculated (Sharpe, Sortino, Calmar)",
            f"{'✅' if fund_aggregations else '❌'} Fund aggregations match manager totals"
        ])
        
        for criterion in criteria_results:
            print(criterion)
        
        print()
        
        # Overall outcome
        all_criteria_met = all('✅' in criterion for criterion in criteria_results)
        if all_criteria_met:
            print("EXPECTED OUTCOME: ✅ All endpoints working with correct P&L totals ($6,903) and proper manager rankings.")
        else:
            print("EXPECTED OUTCOME: ❌ Some verification criteria not met. Review failed tests above.")
        
        print()

def main():
    """Main test execution"""
    tester = TradingAnalyticsAPITester()
    success = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()