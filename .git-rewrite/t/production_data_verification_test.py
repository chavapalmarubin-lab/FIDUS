#!/usr/bin/env python3
"""
PRODUCTION DATA VERIFICATION TEST
=================================

This test verifies what data actually exists in the production environment
and checks if the frontend should be showing non-zero values.

Based on backend logs showing "✅ Retrieved 2 investments for client client_003",
Salvador's data appears to exist in production. This test will verify:

1. What clients exist in production
2. What investments exist for Salvador
3. What MT5 accounts exist
4. What the frontend should be displaying
5. Why the frontend might be showing $0 values

GOAL: Determine if the issue is missing data or frontend display problems.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration - PRODUCTION ENVIRONMENT
PRODUCTION_URL = "https://fidus-invest.emergent.host/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class ProductionDataVerification:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.verification_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log verification result"""
        status = "✅ VERIFIED" if success else "❌ ISSUE"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.verification_results.append(result)
        print(f"{status}: {test_name}")
        print(f"   {message}")
        if details:
            print(f"   Details: {json.dumps(details, indent=2)}")
        print()
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{PRODUCTION_URL}/auth/login", json={
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                if self.admin_token:
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    return True
            return False
        except:
            return False
    
    def verify_production_clients(self):
        """Verify what clients exist in production"""
        try:
            response = self.session.get(f"{PRODUCTION_URL}/admin/clients")
            if response.status_code == 200:
                clients = response.json()
                
                if isinstance(clients, list):
                    client_count = len(clients)
                    salvador_client = None
                    
                    for client in clients:
                        if client.get('id') == 'client_003' or 'SALVADOR' in client.get('name', '').upper():
                            salvador_client = client
                            break
                    
                    if salvador_client:
                        self.log_result("Production Clients", True, 
                                      f"Found {client_count} clients including Salvador Palma",
                                      {"salvador_client": salvador_client, "total_clients": client_count})
                        return True
                    else:
                        self.log_result("Production Clients", False, 
                                      f"Salvador Palma not found among {client_count} clients",
                                      {"all_clients": clients})
                        return False
                else:
                    self.log_result("Production Clients", False, 
                                  "Unexpected clients response format",
                                  {"response": clients})
                    return False
            else:
                self.log_result("Production Clients", False, 
                              f"Failed to get clients: HTTP {response.status_code}",
                              {"response": response.text})
                return False
        except Exception as e:
            self.log_result("Production Clients", False, f"Exception: {str(e)}")
            return False
    
    def verify_salvador_investments(self):
        """Verify Salvador's investments in production"""
        try:
            response = self.session.get(f"{PRODUCTION_URL}/investments/client/client_003")
            if response.status_code == 200:
                investments = response.json()
                
                if isinstance(investments, list) and len(investments) > 0:
                    total_amount = sum(inv.get('principal_amount', 0) for inv in investments)
                    
                    # Look for specific investments
                    balance_investment = None
                    core_investment = None
                    
                    for inv in investments:
                        if inv.get('fund_code') == 'BALANCE':
                            balance_investment = inv
                        elif inv.get('fund_code') == 'CORE':
                            core_investment = inv
                    
                    investment_details = {
                        "total_investments": len(investments),
                        "total_amount": total_amount,
                        "balance_investment": balance_investment,
                        "core_investment": core_investment,
                        "all_investments": investments
                    }
                    
                    if total_amount > 1000000:  # Should be around $1.26M
                        self.log_result("Salvador Investments", True, 
                                      f"Found {len(investments)} investments totaling ${total_amount:,.2f}",
                                      investment_details)
                        return True
                    else:
                        self.log_result("Salvador Investments", False, 
                                      f"Investment amounts seem low: ${total_amount:,.2f}",
                                      investment_details)
                        return False
                else:
                    self.log_result("Salvador Investments", False, 
                                  f"No investments found for Salvador (got {len(investments) if isinstance(investments, list) else 'non-list'})",
                                  {"response": investments})
                    return False
            else:
                self.log_result("Salvador Investments", False, 
                              f"Failed to get Salvador's investments: HTTP {response.status_code}",
                              {"response": response.text})
                return False
        except Exception as e:
            self.log_result("Salvador Investments", False, f"Exception: {str(e)}")
            return False
    
    def verify_mt5_accounts(self):
        """Verify MT5 accounts in production"""
        try:
            response = self.session.get(f"{PRODUCTION_URL}/mt5/admin/accounts")
            if response.status_code == 200:
                mt5_accounts = response.json()
                
                if isinstance(mt5_accounts, list):
                    salvador_accounts = [acc for acc in mt5_accounts if acc.get('client_id') == 'client_003']
                    total_accounts = len(mt5_accounts)
                    salvador_account_count = len(salvador_accounts)
                    
                    account_details = {
                        "total_mt5_accounts": total_accounts,
                        "salvador_accounts": salvador_account_count,
                        "salvador_account_details": salvador_accounts,
                        "all_accounts": mt5_accounts
                    }
                    
                    if salvador_account_count >= 1:
                        self.log_result("MT5 Accounts", True, 
                                      f"Found {salvador_account_count} MT5 accounts for Salvador (Total: {total_accounts})",
                                      account_details)
                        return True
                    else:
                        self.log_result("MT5 Accounts", False, 
                                      f"No MT5 accounts found for Salvador (Total accounts: {total_accounts})",
                                      account_details)
                        return False
                else:
                    self.log_result("MT5 Accounts", False, 
                                  "Unexpected MT5 accounts response format",
                                  {"response": mt5_accounts})
                    return False
            else:
                self.log_result("MT5 Accounts", False, 
                              f"Failed to get MT5 accounts: HTTP {response.status_code}",
                              {"response": response.text})
                return False
        except Exception as e:
            self.log_result("MT5 Accounts", False, f"Exception: {str(e)}")
            return False
    
    def verify_fund_performance_dashboard(self):
        """Verify fund performance dashboard data"""
        try:
            response = self.session.get(f"{PRODUCTION_URL}/admin/fund-performance/dashboard")
            if response.status_code == 200:
                fund_data = response.json()
                
                # Look for Salvador's data in fund performance
                salvador_entries = []
                total_aum = 0
                
                if isinstance(fund_data, dict):
                    # Check various possible structures
                    if 'performance_data' in fund_data:
                        performance_data = fund_data['performance_data']
                        if isinstance(performance_data, list):
                            salvador_entries = [entry for entry in performance_data 
                                              if entry.get('client_id') == 'client_003']
                    
                    # Look for total AUM
                    total_aum = fund_data.get('total_aum', 0) or fund_data.get('total_assets', 0)
                
                dashboard_details = {
                    "fund_performance_data": fund_data,
                    "salvador_entries": salvador_entries,
                    "total_aum": total_aum
                }
                
                if len(salvador_entries) > 0 or total_aum > 1000000:
                    self.log_result("Fund Performance Dashboard", True, 
                                  f"Salvador data found in fund performance (AUM: ${total_aum:,.2f})",
                                  dashboard_details)
                    return True
                else:
                    self.log_result("Fund Performance Dashboard", False, 
                                  f"Salvador missing from fund performance (AUM: ${total_aum:,.2f})",
                                  dashboard_details)
                    return False
            else:
                self.log_result("Fund Performance Dashboard", False, 
                              f"Failed to get fund performance: HTTP {response.status_code}",
                              {"response": response.text})
                return False
        except Exception as e:
            self.log_result("Fund Performance Dashboard", False, f"Exception: {str(e)}")
            return False
    
    def verify_cash_flow_management(self):
        """Verify cash flow management data"""
        try:
            response = self.session.get(f"{PRODUCTION_URL}/admin/cashflow/overview")
            if response.status_code == 200:
                cashflow_data = response.json()
                
                # Look for non-zero values
                mt5_profits = cashflow_data.get('mt5_trading_profits', 0)
                client_obligations = cashflow_data.get('client_obligations', 0) or cashflow_data.get('client_interest_obligations', 0)
                total_assets = cashflow_data.get('total_fund_assets', 0)
                
                cashflow_details = {
                    "cashflow_data": cashflow_data,
                    "mt5_trading_profits": mt5_profits,
                    "client_obligations": client_obligations,
                    "total_fund_assets": total_assets
                }
                
                if mt5_profits > 0 or client_obligations > 0 or total_assets > 1000000:
                    self.log_result("Cash Flow Management", True, 
                                  f"Non-zero cash flow values found (Assets: ${total_assets:,.2f})",
                                  cashflow_details)
                    return True
                else:
                    self.log_result("Cash Flow Management", False, 
                                  "All cash flow values are zero",
                                  cashflow_details)
                    return False
            else:
                self.log_result("Cash Flow Management", False, 
                              f"Failed to get cash flow data: HTTP {response.status_code}",
                              {"response": response.text})
                return False
        except Exception as e:
            self.log_result("Cash Flow Management", False, f"Exception: {str(e)}")
            return False
    
    def verify_client_data_endpoint(self):
        """Verify Salvador's client data endpoint"""
        try:
            response = self.session.get(f"{PRODUCTION_URL}/client/client_003/data")
            if response.status_code == 200:
                client_data = response.json()
                
                # Look for balance information
                balance_info = client_data.get('balance', {})
                total_balance = balance_info.get('total_balance', 0)
                
                client_details = {
                    "client_data": client_data,
                    "balance_info": balance_info,
                    "total_balance": total_balance
                }
                
                if total_balance > 1000000:
                    self.log_result("Salvador Client Data", True, 
                                  f"Salvador's total balance: ${total_balance:,.2f}",
                                  client_details)
                    return True
                else:
                    self.log_result("Salvador Client Data", False, 
                                  f"Salvador's balance seems low: ${total_balance:,.2f}",
                                  client_details)
                    return False
            else:
                self.log_result("Salvador Client Data", False, 
                              f"Failed to get Salvador's client data: HTTP {response.status_code}",
                              {"response": response.text})
                return False
        except Exception as e:
            self.log_result("Salvador Client Data", False, f"Exception: {str(e)}")
            return False
    
    def run_production_verification(self):
        """Run complete production data verification"""
        print("🔍 PRODUCTION DATA VERIFICATION - COMPREHENSIVE ANALYSIS")
        print("=" * 70)
        print(f"Production URL: {PRODUCTION_URL}")
        print(f"Verification Time: {datetime.now().isoformat()}")
        print()
        print("GOAL: Determine what data exists in production and why frontend shows $0")
        print("Backend logs show: '✅ Retrieved 2 investments for client client_003'")
        print()
        
        # Authenticate
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed.")
            return False
        
        print("🔐 Admin authentication successful. Starting verification...")
        print()
        
        # Run all verifications
        verifications = [
            self.verify_production_clients,
            self.verify_salvador_investments,
            self.verify_mt5_accounts,
            self.verify_fund_performance_dashboard,
            self.verify_cash_flow_management,
            self.verify_client_data_endpoint
        ]
        
        verification_results = []
        for verification_func in verifications:
            try:
                result = verification_func()
                verification_results.append(result)
            except Exception as e:
                print(f"❌ EXCEPTION in {verification_func.__name__}: {str(e)}")
                verification_results.append(False)
        
        # Generate comprehensive summary
        self.generate_verification_summary(verification_results)
        
        return sum(verification_results) >= 3  # At least half successful
    
    def generate_verification_summary(self, verification_results):
        """Generate comprehensive verification summary"""
        print("\n" + "=" * 70)
        print("🔍 PRODUCTION DATA VERIFICATION SUMMARY")
        print("=" * 70)
        
        total_verifications = len(self.verification_results)
        successful_verifications = sum(1 for result in self.verification_results if result['success'])
        failed_verifications = total_verifications - successful_verifications
        success_rate = (successful_verifications / total_verifications * 100) if total_verifications > 0 else 0
        
        print(f"Total Verifications: {total_verifications}")
        print(f"Successful: {successful_verifications}")
        print(f"Issues Found: {failed_verifications}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Show verification results
        verification_names = [
            "Production Clients",
            "Salvador Investments", 
            "MT5 Accounts",
            "Fund Performance Dashboard",
            "Cash Flow Management",
            "Salvador Client Data"
        ]
        
        print("📋 VERIFICATION RESULTS:")
        for i, (name, result) in enumerate(zip(verification_names, verification_results), 1):
            status = "✅ VERIFIED" if result else "❌ ISSUE"
            print(f"   {i}. {name} - {status}")
        print()
        
        # Show issues found
        if failed_verifications > 0:
            print("❌ ISSUES IDENTIFIED:")
            for result in self.verification_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Critical assessment
        successful_count = sum(verification_results)
        
        print("🎯 ROOT CAUSE ANALYSIS:")
        if successful_count >= 4:
            print("✅ SALVADOR'S DATA EXISTS IN PRODUCTION")
            print("   Salvador's client profile and investments are present in the database.")
            print("   The issue is likely in the frontend data display or API integration.")
            print()
            print("🔧 RECOMMENDED ACTIONS:")
            print("   1. Check frontend API calls and data processing")
            print("   2. Verify frontend environment variables (REACT_APP_BACKEND_URL)")
            print("   3. Check browser console for JavaScript errors")
            print("   4. Verify API response data is being processed correctly")
            print("   5. Check if frontend is using correct API endpoints")
        elif successful_count >= 2:
            print("⚠️  PARTIAL DATA EXISTS IN PRODUCTION")
            print("   Some Salvador data found but integration issues detected.")
            print("   Mixed data availability suggests API or database integration problems.")
            print()
            print("🔧 RECOMMENDED ACTIONS:")
            print("   1. Fix identified API integration issues")
            print("   2. Verify database connectivity and data consistency")
            print("   3. Check backend logs for specific error patterns")
            print("   4. Test individual API endpoints manually")
        else:
            print("❌ SALVADOR'S DATA MISSING FROM PRODUCTION")
            print("   Critical data missing despite backend logs showing retrievals.")
            print("   This suggests database connectivity or data corruption issues.")
            print()
            print("🔧 RECOMMENDED ACTIONS:")
            print("   1. Investigate database connectivity issues")
            print("   2. Check if backend is connecting to correct database")
            print("   3. Verify database contains expected data")
            print("   4. Consider emergency data restoration")
        
        print("\n🌐 FRONTEND VERIFICATION:")
        print("   Visit: https://fidus-invest.emergent.host/")
        print("   Expected if data exists:")
        print("   - Total AUM: $1,267,485.40 (not $0)")
        print("   - Total Clients: 1 (not 0)")
        print("   - Total Accounts: 2 (not 0)")
        
        print("\n" + "=" * 70)

def main():
    """Main execution function"""
    verifier = ProductionDataVerification()
    success = verifier.run_production_verification()
    
    if not success:
        print("\n❌ PRODUCTION VERIFICATION FOUND CRITICAL ISSUES")
        sys.exit(1)
    else:
        print("\n✅ PRODUCTION VERIFICATION COMPLETED")

if __name__ == "__main__":
    main()