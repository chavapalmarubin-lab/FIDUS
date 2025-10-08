#!/usr/bin/env python3
"""
COMPREHENSIVE PRODUCTION VALIDATION: Alejandro Mariscal Romero Data Verification
Testing all critical endpoints to verify Alejandro's data matches exact specifications.

**Authentication**: admin/password123
**Target Values**: 
- Total AUM: $118,151.41
- Investments: 2 (BALANCE $100k + CORE $18,151.41)  
- MT5 Accounts: 4 (totaling $118,151.41)

**CRITICAL ENDPOINTS TO TEST**:
1. Admin Overview (Must show correct totals): GET /api/investments/admin/overview
2. Client Investments (Must show exactly 2): GET /api/investments/client/client_alejandro  
3. MT5 Accounts (Must show 4 accounts): GET /api/mt5/accounts/client_alejandro
4. Ready Clients (Must include Alejandro): GET /api/clients/ready-for-investment

**VALIDATION CRITERIA**:
✅ All totals must equal $118,151.41 exactly
✅ No discrepancies between endpoints  
✅ All data consistent across APIs
✅ Ready for production with first real client
"""

import requests
import json
import sys
from datetime import datetime
from decimal import Decimal

# Use the correct backend URL from frontend/.env
BACKEND_URL = "https://trading-platform-76.preview.emergentagent.com/api"

class AlejandroProductionValidator:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
        # Expected values for validation
        self.EXPECTED_TOTAL_AUM = 118151.41
        self.EXPECTED_INVESTMENTS = 2
        self.EXPECTED_MT5_ACCOUNTS = 4
        self.EXPECTED_BALANCE_AMOUNT = 100000.00
        self.EXPECTED_CORE_AMOUNT = 18151.41
        
    def log_test(self, test_name, success, details, response_data=None, critical=False):
        """Log test results with critical flag"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "critical": critical,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        critical_marker = " 🚨 CRITICAL" if critical else ""
        print(f"{status}{critical_marker} {test_name}: {details}")
        
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
    
    def authenticate_admin(self):
        """Authenticate as admin with credentials admin/password123"""
        print("\n🔐 ADMIN AUTHENTICATION")
        
        try:
            login_data = {
                "username": "admin",
                "password": "password123", 
                "user_type": "admin"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("token"):
                    self.admin_token = data["token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    
                    self.log_test(
                        "Admin Authentication",
                        True,
                        f"Successfully authenticated as {data.get('name', 'admin')}",
                        {"user_id": data.get("id"), "username": data.get("username")},
                        critical=True
                    )
                    return True
                else:
                    self.log_test("Admin Authentication", False, "No token in response", data, critical=True)
                    return False
            else:
                self.log_test("Admin Authentication", False, f"HTTP {response.status_code}", response.json() if response.content else None, critical=True)
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}", critical=True)
            return False
    
    def validate_admin_overview(self):
        """Test admin overview endpoint - Must show total_aum=$118,151.41, total_investments=2, total_clients=1"""
        print("\n📊 ADMIN OVERVIEW VALIDATION")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/investments/admin/overview")
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract values
                total_aum = data.get("total_aum", 0)
                total_investments = data.get("total_investments", 0)
                total_clients = data.get("total_clients", 0)
                
                # Convert AUM to float for comparison (handle string format like "$118,151.41")
                if isinstance(total_aum, str):
                    total_aum_clean = total_aum.replace("$", "").replace(",", "")
                    try:
                        total_aum = float(total_aum_clean)
                    except ValueError:
                        total_aum = 0
                
                # Validate exact values
                aum_correct = abs(total_aum - self.EXPECTED_TOTAL_AUM) < 0.01  # Allow for floating point precision
                investments_correct = total_investments == self.EXPECTED_INVESTMENTS
                clients_correct = total_clients >= 1  # At least Alejandro
                
                all_correct = aum_correct and investments_correct and clients_correct
                
                details = f"AUM: ${total_aum:,.2f} (Expected: ${self.EXPECTED_TOTAL_AUM:,.2f}), Investments: {total_investments} (Expected: {self.EXPECTED_INVESTMENTS}), Clients: {total_clients} (Expected: ≥1)"
                
                if all_correct:
                    self.log_test("Admin Overview - Exact Match", True, details, data, critical=True)
                else:
                    issues = []
                    if not aum_correct:
                        issues.append(f"AUM mismatch: ${total_aum:,.2f} ≠ ${self.EXPECTED_TOTAL_AUM:,.2f}")
                    if not investments_correct:
                        issues.append(f"Investment count mismatch: {total_investments} ≠ {self.EXPECTED_INVESTMENTS}")
                    if not clients_correct:
                        issues.append(f"Client count too low: {total_clients} < 1")
                    
                    self.log_test("Admin Overview - Value Mismatch", False, f"Issues: {'; '.join(issues)}", data, critical=True)
                
                return all_correct
            else:
                self.log_test("Admin Overview", False, f"HTTP {response.status_code}", response.json() if response.content else None, critical=True)
                return False
                
        except Exception as e:
            self.log_test("Admin Overview", False, f"Exception: {str(e)}", critical=True)
            return False
    
    def validate_client_investments(self):
        """Test client investments - Must show exactly 2 investments (BALANCE $100k, CORE $18,151.41)"""
        print("\n💰 CLIENT INVESTMENTS VALIDATION")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/investments/client/client_alejandro")
            
            if response.status_code == 200:
                data = response.json()
                investments = data.get("investments", [])
                
                if len(investments) != self.EXPECTED_INVESTMENTS:
                    self.log_test(
                        "Client Investments - Count Mismatch",
                        False,
                        f"Expected {self.EXPECTED_INVESTMENTS} investments, found {len(investments)}",
                        data,
                        critical=True
                    )
                    return False
                
                # Find BALANCE and CORE investments
                balance_investment = next((inv for inv in investments if inv.get("fund_code") == "BALANCE"), None)
                core_investment = next((inv for inv in investments if inv.get("fund_code") == "CORE"), None)
                
                if not balance_investment:
                    self.log_test("Client Investments - Missing BALANCE", False, "BALANCE fund investment not found", data, critical=True)
                    return False
                
                if not core_investment:
                    self.log_test("Client Investments - Missing CORE", False, "CORE fund investment not found", data, critical=True)
                    return False
                
                # Validate amounts
                balance_amount = balance_investment.get("current_value", 0) or balance_investment.get("principal_amount", 0)
                core_amount = core_investment.get("current_value", 0) or core_investment.get("principal_amount", 0)
                
                balance_correct = abs(balance_amount - self.EXPECTED_BALANCE_AMOUNT) < 0.01
                core_correct = abs(core_amount - self.EXPECTED_CORE_AMOUNT) < 0.01
                
                total_value = balance_amount + core_amount
                total_correct = abs(total_value - self.EXPECTED_TOTAL_AUM) < 0.01
                
                if balance_correct and core_correct and total_correct:
                    self.log_test(
                        "Client Investments - Exact Match",
                        True,
                        f"BALANCE: ${balance_amount:,.2f}, CORE: ${core_amount:,.2f}, Total: ${total_value:,.2f}",
                        {"balance_amount": balance_amount, "core_amount": core_amount, "total": total_value},
                        critical=True
                    )
                    return True
                else:
                    issues = []
                    if not balance_correct:
                        issues.append(f"BALANCE: ${balance_amount:,.2f} ≠ ${self.EXPECTED_BALANCE_AMOUNT:,.2f}")
                    if not core_correct:
                        issues.append(f"CORE: ${core_amount:,.2f} ≠ ${self.EXPECTED_CORE_AMOUNT:,.2f}")
                    if not total_correct:
                        issues.append(f"Total: ${total_value:,.2f} ≠ ${self.EXPECTED_TOTAL_AUM:,.2f}")
                    
                    self.log_test(
                        "Client Investments - Amount Mismatch",
                        False,
                        f"Issues: {'; '.join(issues)}",
                        data,
                        critical=True
                    )
                    return False
                
            else:
                self.log_test("Client Investments", False, f"HTTP {response.status_code}", response.json() if response.content else None, critical=True)
                return False
                
        except Exception as e:
            self.log_test("Client Investments", False, f"Exception: {str(e)}", critical=True)
            return False
    
    def validate_mt5_accounts(self):
        """Test MT5 accounts - Must show 4 accounts totaling $118,151.41"""
        print("\n🏦 MT5 ACCOUNTS VALIDATION")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/accounts/client_alejandro")
            
            if response.status_code == 200:
                data = response.json()
                accounts = data.get("accounts", [])
                
                if len(accounts) != self.EXPECTED_MT5_ACCOUNTS:
                    self.log_test(
                        "MT5 Accounts - Count Mismatch",
                        False,
                        f"Expected {self.EXPECTED_MT5_ACCOUNTS} MT5 accounts, found {len(accounts)}",
                        data,
                        critical=True
                    )
                    return False
                
                # Calculate total balance across all MT5 accounts
                total_balance = 0
                mexatlantic_count = 0
                account_details = []
                
                for account in accounts:
                    balance = account.get("balance", 0) or account.get("current_balance", 0)
                    total_balance += balance
                    
                    broker_name = account.get("broker_name", "")
                    if "MEXAtlantic" in broker_name:
                        mexatlantic_count += 1
                    
                    account_details.append({
                        "account_number": account.get("mt5_account_number", "N/A"),
                        "broker": broker_name,
                        "balance": balance
                    })
                
                # Validate total balance
                balance_correct = abs(total_balance - self.EXPECTED_TOTAL_AUM) < 0.01
                
                if balance_correct:
                    self.log_test(
                        "MT5 Accounts - Exact Match",
                        True,
                        f"4 accounts totaling ${total_balance:,.2f} ({mexatlantic_count} MEXAtlantic)",
                        {"total_balance": total_balance, "mexatlantic_count": mexatlantic_count, "accounts": account_details},
                        critical=True
                    )
                    return True
                else:
                    self.log_test(
                        "MT5 Accounts - Balance Mismatch",
                        False,
                        f"Total balance ${total_balance:,.2f} ≠ ${self.EXPECTED_TOTAL_AUM:,.2f}",
                        data,
                        critical=True
                    )
                    return False
                
            else:
                self.log_test("MT5 Accounts", False, f"HTTP {response.status_code}", response.json() if response.content else None, critical=True)
                return False
                
        except Exception as e:
            self.log_test("MT5 Accounts", False, f"Exception: {str(e)}", critical=True)
            return False
    
    def validate_ready_clients(self):
        """Test ready clients - Must include Alejandro"""
        print("\n👥 READY CLIENTS VALIDATION")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/clients/ready-for-investment")
            
            if response.status_code == 200:
                data = response.json()
                ready_clients = data.get("ready_clients", [])
                
                # Check if Alejandro is in the list
                alejandro_found = any(
                    client.get("client_id") == "client_alejandro" or 
                    "Alejandro" in client.get("name", "") 
                    for client in ready_clients
                )
                
                if alejandro_found:
                    alejandro_client = next(
                        client for client in ready_clients 
                        if client.get("client_id") == "client_alejandro" or "Alejandro" in client.get("name", "")
                    )
                    self.log_test(
                        "Ready Clients - Alejandro Found",
                        True,
                        f"Alejandro found: {alejandro_client.get('name')} ({alejandro_client.get('client_id')})",
                        alejandro_client,
                        critical=True
                    )
                    return True
                else:
                    self.log_test(
                        "Ready Clients - Alejandro Missing",
                        False,
                        f"Alejandro not found in {len(ready_clients)} ready clients",
                        data,
                        critical=True
                    )
                    return False
                
            else:
                self.log_test("Ready Clients", False, f"HTTP {response.status_code}", response.json() if response.content else None, critical=True)
                return False
                
        except Exception as e:
            self.log_test("Ready Clients", False, f"Exception: {str(e)}", critical=True)
            return False
    
    def validate_data_consistency(self):
        """Cross-validate data consistency between endpoints"""
        print("\n🔍 DATA CONSISTENCY VALIDATION")
        
        # This test runs after all individual tests to check for consistency
        admin_overview_result = next((r for r in self.test_results if "Admin Overview" in r["test"] and r["success"]), None)
        client_investments_result = next((r for r in self.test_results if "Client Investments" in r["test"] and r["success"]), None)
        mt5_accounts_result = next((r for r in self.test_results if "MT5 Accounts" in r["test"] and r["success"]), None)
        
        if not all([admin_overview_result, client_investments_result, mt5_accounts_result]):
            self.log_test(
                "Data Consistency",
                False,
                "Cannot validate consistency - some individual tests failed",
                critical=True
            )
            return False
        
        # All individual tests passed, so data is consistent
        self.log_test(
            "Data Consistency",
            True,
            "All endpoints show consistent data: $118,151.41 total across admin overview, client investments, and MT5 accounts",
            critical=True
        )
        return True
    
    def run_production_validation(self):
        """Run complete production validation for Alejandro's data"""
        print("🚨 COMPREHENSIVE PRODUCTION VALIDATION: Alejandro Mariscal Romero")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print(f"Expected Total AUM: ${self.EXPECTED_TOTAL_AUM:,.2f}")
        print(f"Expected Investments: {self.EXPECTED_INVESTMENTS} (BALANCE ${self.EXPECTED_BALANCE_AMOUNT:,.2f} + CORE ${self.EXPECTED_CORE_AMOUNT:,.2f})")
        print(f"Expected MT5 Accounts: {self.EXPECTED_MT5_ACCOUNTS}")
        print("=" * 80)
        
        # Authentication is required for all tests
        if not self.authenticate_admin():
            print("\n❌ CRITICAL FAILURE: Admin authentication failed - cannot proceed with validation")
            return False
        
        # Run all validation tests
        validation_tests = [
            ("Admin Overview", self.validate_admin_overview),
            ("Client Investments", self.validate_client_investments),
            ("MT5 Accounts", self.validate_mt5_accounts),
            ("Ready Clients", self.validate_ready_clients),
            ("Data Consistency", self.validate_data_consistency)
        ]
        
        passed_tests = 0
        critical_failures = []
        
        for test_name, test_func in validation_tests:
            try:
                if test_func():
                    passed_tests += 1
                else:
                    critical_failures.append(test_name)
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_name}: {str(e)}")
                critical_failures.append(test_name)
        
        # Final validation summary
        print("\n" + "=" * 80)
        print("🎯 PRODUCTION VALIDATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(validation_tests)
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"Validation Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        if success_rate == 100:
            print("\n✅ PRODUCTION READY: All validation criteria met")
            print("   - Total AUM: $118,151.41 ✓")
            print("   - Investments: 2 (BALANCE $100k + CORE $18,151.41) ✓")
            print("   - MT5 Accounts: 4 totaling $118,151.41 ✓")
            print("   - Ready for investment dropdown: Alejandro included ✓")
            print("   - Data consistency: All endpoints aligned ✓")
            print("\n🚀 READY FOR GO-LIVE WITH FIRST REAL CLIENT")
        else:
            print(f"\n❌ NOT PRODUCTION READY: {len(critical_failures)} critical failures")
            print("\n🚨 CRITICAL FAILURES:")
            for failure in critical_failures:
                print(f"   - {failure}")
            
            print("\n📋 REQUIRED ACTIONS:")
            if "Admin Overview" in critical_failures:
                print("   - Fix admin overview totals to show exactly $118,151.41")
            if "Client Investments" in critical_failures:
                print("   - Create/fix Alejandro's 2 investments (BALANCE $100k + CORE $18,151.41)")
            if "MT5 Accounts" in critical_failures:
                print("   - Create/fix Alejandro's 4 MT5 accounts totaling $118,151.41")
            if "Ready Clients" in critical_failures:
                print("   - Fix ready-for-investment endpoint to include Alejandro")
            if "Data Consistency" in critical_failures:
                print("   - Ensure all endpoints return consistent data")
        
        return success_rate == 100

if __name__ == "__main__":
    validator = AlejandroProductionValidator()
    production_ready = validator.run_production_validation()
    
    # Exit with appropriate code
    sys.exit(0 if production_ready else 1)