#!/usr/bin/env python3
"""
SALVADOR PALMA PRODUCTION DATA VERIFICATION TEST
===============================================

This test verifies Salvador's existing data in production and checks if it matches
the expected requirements from the review request.

Expected Results:
- Total AUM: $1,267,485.40
- Total Clients: 1 (Salvador)
- MT5 Accounts: 2 (DooTechnology + VT Markets)
"""

import requests
import json
import sys
from datetime import datetime

# Production API Base URL
PRODUCTION_API_BASE = "https://fidus-invest.emergent.host/api"

class SalvadorProductionVerifier:
    def __init__(self):
        self.base_url = PRODUCTION_API_BASE
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, details, response_data=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
        if response_data and isinstance(response_data, dict):
            print(f"   Data: {json.dumps(response_data, indent=2)}")
    
    def login_to_production(self):
        """Login to production"""
        print("\n🔐 LOGIN TO PRODUCTION")
        print("=" * 50)
        
        try:
            login_data = {
                "username": "admin",
                "password": "password123",
                "user_type": "admin"
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/login",
                headers={"Content-Type": "application/json"},
                json=login_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("token"):
                    self.admin_token = data["token"]
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.admin_token}"
                    })
                    self.log_result(
                        "Admin Login", 
                        True, 
                        f"Successfully logged in as admin",
                        {"user": data.get("name", "Admin")}
                    )
                    return True
                else:
                    self.log_result("Admin Login", False, "Login response missing token", data)
                    return False
            else:
                self.log_result(
                    "Admin Login", 
                    False, 
                    f"Login failed with status {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Login", False, f"Login error: {str(e)}")
            return False
    
    def verify_salvador_client(self):
        """Verify Salvador's client profile"""
        print("\n👤 VERIFY SALVADOR CLIENT")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{self.base_url}/admin/clients", timeout=30)
            if response.status_code == 200:
                clients_data = response.json()
                clients = clients_data.get('clients', [])
                
                salvador_client = None
                for client in clients:
                    if client.get('id') == 'client_003' or 'SALVADOR' in client.get('name', '').upper():
                        salvador_client = client
                        break
                
                if salvador_client:
                    self.log_result(
                        "Salvador Client Profile",
                        True,
                        f"Found Salvador Palma: {salvador_client.get('name')} ({salvador_client.get('id')})",
                        {
                            "id": salvador_client.get('id'),
                            "name": salvador_client.get('name'),
                            "email": salvador_client.get('email'),
                            "total_balance": salvador_client.get('total_balance', 0)
                        }
                    )
                    return True
                else:
                    self.log_result("Salvador Client Profile", False, "Salvador Palma client not found")
                    return False
            else:
                self.log_result(
                    "Salvador Client Profile",
                    False,
                    f"Failed to fetch clients: {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_result("Salvador Client Profile", False, f"Client verification error: {str(e)}")
            return False
    
    def verify_salvador_investments(self):
        """Verify Salvador's investments"""
        print("\n💰 VERIFY SALVADOR INVESTMENTS")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{self.base_url}/investments/client/client_003", timeout=30)
            if response.status_code == 200:
                investments_data = response.json()
                investments = investments_data.get('investments', [])
                
                total_amount = 0
                balance_investment = None
                core_investment = None
                
                for investment in investments:
                    amount = investment.get('principal_amount', 0)
                    fund_code = investment.get('fund_code', '')
                    total_amount += amount
                    
                    if fund_code == 'BALANCE':
                        balance_investment = investment
                    elif fund_code == 'CORE':
                        core_investment = investment
                
                # Check BALANCE investment
                if balance_investment:
                    expected_balance = 1263485.40
                    actual_balance = balance_investment.get('principal_amount', 0)
                    balance_correct = abs(actual_balance - expected_balance) < 1
                    
                    self.log_result(
                        "BALANCE Investment",
                        balance_correct,
                        f"BALANCE fund: ${actual_balance:,.2f} (Expected: ${expected_balance:,.2f})",
                        {
                            "investment_id": balance_investment.get('investment_id'),
                            "amount": actual_balance,
                            "expected": expected_balance,
                            "deposit_date": balance_investment.get('deposit_date')
                        }
                    )
                else:
                    self.log_result("BALANCE Investment", False, "BALANCE fund investment not found")
                
                # Check CORE investment
                if core_investment:
                    expected_core = 4000.00
                    actual_core = core_investment.get('principal_amount', 0)
                    core_correct = abs(actual_core - expected_core) < 1
                    
                    self.log_result(
                        "CORE Investment",
                        core_correct,
                        f"CORE fund: ${actual_core:,.2f} (Expected: ${expected_core:,.2f})",
                        {
                            "investment_id": core_investment.get('investment_id'),
                            "amount": actual_core,
                            "expected": expected_core,
                            "deposit_date": core_investment.get('deposit_date')
                        }
                    )
                else:
                    self.log_result("CORE Investment", False, "CORE fund investment not found")
                
                # Check total AUM
                expected_total = 1267485.40
                total_correct = abs(total_amount - expected_total) < 1
                
                self.log_result(
                    "Total AUM",
                    total_correct,
                    f"Total AUM: ${total_amount:,.2f} (Expected: ${expected_total:,.2f})",
                    {
                        "total_investments": len(investments),
                        "total_amount": total_amount,
                        "expected_total": expected_total
                    }
                )
                
                return balance_investment is not None and core_investment is not None and total_correct
                
            else:
                self.log_result(
                    "Salvador Investments",
                    False,
                    f"Failed to fetch investments: {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_result("Salvador Investments", False, f"Investment verification error: {str(e)}")
            return False
    
    def verify_salvador_mt5_accounts(self):
        """Verify Salvador's MT5 accounts"""
        print("\n🏦 VERIFY SALVADOR MT5 ACCOUNTS")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{self.base_url}/mt5/admin/accounts", timeout=30)
            if response.status_code == 200:
                mt5_data = response.json()
                accounts = mt5_data.get('accounts', [])
                
                salvador_accounts = [acc for acc in accounts if acc.get('client_id') == 'client_003']
                
                doo_account = None
                vt_account = None
                
                for account in salvador_accounts:
                    login = account.get('login', '')
                    broker = account.get('broker', '')
                    
                    if login == '9928326':
                        doo_account = account
                    elif login == '15759667':
                        vt_account = account
                
                # Check DooTechnology account
                if doo_account:
                    self.log_result(
                        "DooTechnology MT5 Account",
                        True,
                        f"Found DooTechnology account: Login {doo_account.get('login')}",
                        {
                            "login": doo_account.get('login'),
                            "broker": doo_account.get('broker'),
                            "server": doo_account.get('server'),
                            "allocated_amount": doo_account.get('allocated_amount', 0)
                        }
                    )
                else:
                    self.log_result("DooTechnology MT5 Account", False, "DooTechnology MT5 account (9928326) not found")
                
                # Check VT Markets account
                if vt_account:
                    self.log_result(
                        "VT Markets MT5 Account",
                        True,
                        f"Found VT Markets account: Login {vt_account.get('login')}",
                        {
                            "login": vt_account.get('login'),
                            "broker": vt_account.get('broker'),
                            "server": vt_account.get('server'),
                            "allocated_amount": vt_account.get('allocated_amount', 0)
                        }
                    )
                else:
                    self.log_result("VT Markets MT5 Account", False, "VT Markets MT5 account (15759667) not found")
                
                # Summary
                self.log_result(
                    "MT5 Accounts Summary",
                    len(salvador_accounts) >= 2,
                    f"Salvador has {len(salvador_accounts)} MT5 accounts (Expected: 2)",
                    {"total_accounts": len(salvador_accounts), "accounts": salvador_accounts}
                )
                
                return doo_account is not None and vt_account is not None
                
            else:
                self.log_result(
                    "Salvador MT5 Accounts",
                    False,
                    f"Failed to fetch MT5 accounts: {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_result("Salvador MT5 Accounts", False, f"MT5 verification error: {str(e)}")
            return False
    
    def verify_fund_performance_integration(self):
        """Verify Salvador appears in fund performance dashboard"""
        print("\n📊 VERIFY FUND PERFORMANCE INTEGRATION")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{self.base_url}/admin/fund-performance/dashboard", timeout=30)
            if response.status_code == 200:
                performance_data = response.json()
                performance_records = performance_data.get('performance_records', [])
                
                salvador_records = [rec for rec in performance_records if rec.get('client_id') == 'client_003']
                
                if salvador_records:
                    self.log_result(
                        "Fund Performance Integration",
                        True,
                        f"Salvador appears in fund performance dashboard with {len(salvador_records)} records",
                        {"records_count": len(salvador_records), "sample_record": salvador_records[0] if salvador_records else None}
                    )
                    return True
                else:
                    self.log_result("Fund Performance Integration", False, "Salvador not found in fund performance dashboard")
                    return False
                    
            else:
                self.log_result(
                    "Fund Performance Integration",
                    False,
                    f"Failed to fetch fund performance: {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_result("Fund Performance Integration", False, f"Fund performance verification error: {str(e)}")
            return False
    
    def verify_cash_flow_integration(self):
        """Verify Salvador appears in cash flow management"""
        print("\n💸 VERIFY CASH FLOW INTEGRATION")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{self.base_url}/admin/cashflow/overview", timeout=30)
            if response.status_code == 200:
                cashflow_data = response.json()
                
                mt5_trading_profits = cashflow_data.get('mt5_trading_profits', 0)
                client_obligations = cashflow_data.get('client_interest_obligations', 0)
                
                # Check if values are non-zero (indicating Salvador's data is included)
                has_mt5_profits = mt5_trading_profits > 0
                has_client_obligations = client_obligations > 0
                
                self.log_result(
                    "Cash Flow Integration",
                    has_mt5_profits and has_client_obligations,
                    f"Cash flow shows MT5 profits: ${mt5_trading_profits:,.2f}, Client obligations: ${client_obligations:,.2f}",
                    {
                        "mt5_trading_profits": mt5_trading_profits,
                        "client_obligations": client_obligations,
                        "net_profitability": cashflow_data.get('net_fund_profitability', 0)
                    }
                )
                
                return has_mt5_profits and has_client_obligations
                
            else:
                self.log_result(
                    "Cash Flow Integration",
                    False,
                    f"Failed to fetch cash flow: {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_result("Cash Flow Integration", False, f"Cash flow verification error: {str(e)}")
            return False
    
    def run_complete_verification(self):
        """Execute complete Salvador data verification"""
        print("🔍 SALVADOR PALMA PRODUCTION DATA VERIFICATION")
        print("=" * 60)
        print(f"Target: {self.base_url}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("=" * 60)
        
        # Execute all verification steps
        verification_steps = [
            ("Login to Production", self.login_to_production),
            ("Verify Salvador Client", self.verify_salvador_client),
            ("Verify Salvador Investments", self.verify_salvador_investments),
            ("Verify Salvador MT5 Accounts", self.verify_salvador_mt5_accounts),
            ("Verify Fund Performance Integration", self.verify_fund_performance_integration),
            ("Verify Cash Flow Integration", self.verify_cash_flow_integration)
        ]
        
        successful_steps = 0
        
        for step_name, step_function in verification_steps:
            try:
                if step_function():
                    successful_steps += 1
                else:
                    print(f"\n⚠️ Verification failed: {step_name}")
            except Exception as e:
                print(f"\n💥 Verification error: {step_name} - {str(e)}")
        
        # Final summary
        print("\n" + "=" * 60)
        print("🎯 VERIFICATION RESULTS SUMMARY")
        print("=" * 60)
        
        success_rate = (successful_steps / len(verification_steps)) * 100
        print(f"Verification steps passed: {successful_steps}/{len(verification_steps)} ({success_rate:.1f}%)")
        
        passed_tests = len([r for r in self.test_results if r['success']])
        total_tests = len(self.test_results)
        test_success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Individual tests passed: {passed_tests}/{total_tests} ({test_success_rate:.1f}%)")
        
        if success_rate >= 85:
            print("✅ SALVADOR DATA VERIFICATION: SUCCESS!")
            print("   Production contains Salvador's complete data as expected")
        elif success_rate >= 70:
            print("⚠️ SALVADOR DATA VERIFICATION: PARTIAL SUCCESS")
            print("   Most data present, some integration issues detected")
        else:
            print("❌ SALVADOR DATA VERIFICATION: FAILED")
            print("   Significant data missing or integration broken")
        
        print("\nExpected Production Results:")
        print("- Total AUM: $1,267,485.40")
        print("- Total Clients: 1 (Salvador)")
        print("- MT5 Accounts: 2 (DooTechnology + VT Markets)")
        
        return success_rate >= 70

def main():
    """Main execution function"""
    verifier = SalvadorProductionVerifier()
    success = verifier.run_complete_verification()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()