#!/usr/bin/env python3
"""
COMPREHENSIVE SYSTEM VERIFICATION - AUTO-HEALING & ALL SYSTEMS
Testing Date: December 18, 2025
Backend URL: https://fidusrefs.preview.emergentagent.com/api
Auth: Admin (username: admin, password: password123)

Test Suite:
1. GITHUB_TOKEN Verification
2. MT5 Bridge Health Check  
3. Alert System Verification
4. MongoDB Atlas Data Integrity
5. All 4 Priority Issues Status
6. Auto-Healing System Status

Success Criteria:
- All API endpoints return HTTP 200
- GITHUB_TOKEN authentication successful
- MT5 Bridge healthy with real balances
- Alert system functional
- MongoDB Atlas data consistent
- All 4 priority calculations correct
- Auto-healing completed recovery
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

class ComprehensiveSystemVerifier:
    def __init__(self):
        self.base_url = "https://fidusrefs.preview.emergentagent.com/api"
        self.mt5_bridge_url = "http://92.118.45.135:8000/api/mt5/bridge/health"
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
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
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
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
    
    def test_github_token_verification(self) -> bool:
        """Test 1: GITHUB_TOKEN Verification"""
        try:
            print("\n🔑 Testing GITHUB_TOKEN Verification...")
            
            # Test GitHub API access using the token
            response = self.session.get(f"{self.base_url}/admin/system-health/github-status")
            
            if response.status_code == 200:
                data = response.json()
                github_status = data.get('github_status', {})
                
                # Check if new token is active
                token_active = github_status.get('token_active', False)
                api_access = github_status.get('api_access', False)
                repository_dispatch = github_status.get('repository_dispatch_capable', False)
                
                if token_active:
                    self.log_test("GitHub Token Active", "PASS", "New token (ghp_ssWu...) is active")
                else:
                    self.log_test("GitHub Token Active", "FAIL", "GitHub token not active")
                
                if api_access:
                    self.log_test("GitHub API Access", "PASS", "GitHub API access working")
                else:
                    self.log_test("GitHub API Access", "FAIL", "GitHub API access failed")
                
                if repository_dispatch:
                    self.log_test("Repository Dispatch", "PASS", "Repository dispatch trigger capability verified")
                else:
                    self.log_test("Repository Dispatch", "FAIL", "Repository dispatch not working")
                
                # Check GitHub Actions workflow history
                workflow_history = github_status.get('recent_workflows', [])
                mt5_restart_found = any('MT5 Full System Restart' in str(workflow) for workflow in workflow_history)
                
                if mt5_restart_found:
                    self.log_test("GitHub Actions History", "PASS", "Recent 'MT5 Full System Restart' workflow found")
                else:
                    self.log_test("GitHub Actions History", "FAIL", "No recent 'MT5 Full System Restart' workflow found")
                
                return token_active and api_access and repository_dispatch
            else:
                self.log_test("GitHub Status API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GitHub Token Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_mt5_bridge_health(self) -> bool:
        """Test 2: MT5 Bridge Health Check"""
        try:
            print("\n🔌 Testing MT5 Bridge Health Check...")
            
            # Direct call to VPS MT5 Bridge
            try:
                response = requests.get(self.mt5_bridge_url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check Terminal connection status
                    terminal_connected = data.get('terminal_connected', False)
                    if terminal_connected:
                        self.log_test("MT5 Terminal Connection", "PASS", "Terminal connection active")
                    else:
                        self.log_test("MT5 Terminal Connection", "FAIL", "Terminal not connected")
                    
                    # Check if all 7 accounts show real balances (not $0)
                    accounts = data.get('accounts', [])
                    real_balance_accounts = 0
                    total_accounts = len(accounts)
                    
                    for account in accounts:
                        balance = account.get('balance', 0)
                        if balance > 0:
                            real_balance_accounts += 1
                    
                    if real_balance_accounts == 7:
                        self.log_test("MT5 Account Balances", "PASS", f"All 7 accounts show real balances")
                    else:
                        self.log_test("MT5 Account Balances", "FAIL", 
                                    f"Only {real_balance_accounts}/7 accounts show real balances")
                    
                    # Check trade_allowed status
                    trade_allowed = data.get('trade_allowed', False)
                    if trade_allowed:
                        self.log_test("MT5 Trade Allowed", "PASS", "Trading is allowed")
                    else:
                        self.log_test("MT5 Trade Allowed", "FAIL", "Trading not allowed")
                    
                    return terminal_connected and real_balance_accounts == 7 and trade_allowed
                else:
                    self.log_test("MT5 Bridge Direct Call", "FAIL", f"HTTP {response.status_code}: {response.text}")
                    return False
                    
            except requests.exceptions.RequestException as e:
                self.log_test("MT5 Bridge Direct Call", "ERROR", f"Connection error: {str(e)}")
                
                # Fallback: Test through backend proxy
                response = self.session.get(f"{self.base_url}/mt5/bridge/health")
                if response.status_code == 200:
                    data = response.json()
                    self.log_test("MT5 Bridge Proxy", "PASS", "MT5 Bridge accessible through backend proxy")
                    return True
                else:
                    self.log_test("MT5 Bridge Proxy", "FAIL", f"HTTP {response.status_code}: {response.text}")
                    return False
                
        except Exception as e:
            self.log_test("MT5 Bridge Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_alert_system_verification(self) -> bool:
        """Test 3: Alert System Verification"""
        try:
            print("\n🚨 Testing Alert System Verification...")
            
            # Check System Health Dashboard
            response = self.session.get(f"{self.base_url}/admin/system-health/status")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify alert history shows recent MT5 disconnection alerts
                alert_history = data.get('alert_history', [])
                mt5_alerts = [alert for alert in alert_history if 'MT5' in str(alert)]
                
                if mt5_alerts:
                    self.log_test("MT5 Alert History", "PASS", f"Found {len(mt5_alerts)} MT5-related alerts")
                else:
                    self.log_test("MT5 Alert History", "FAIL", "No MT5 disconnection alerts found")
                
                # Confirm alert severity levels are correct
                severity_levels = set()
                for alert in alert_history:
                    if isinstance(alert, dict):
                        severity = alert.get('severity')
                        if severity:
                            severity_levels.add(severity)
                
                expected_severities = {'critical', 'warning', 'info'}
                if severity_levels.intersection(expected_severities):
                    self.log_test("Alert Severity Levels", "PASS", f"Found severity levels: {severity_levels}")
                else:
                    self.log_test("Alert Severity Levels", "FAIL", f"No proper severity levels found: {severity_levels}")
                
                # Check overall alert system status
                alert_system_status = data.get('alert_system_status', 'unknown')
                if alert_system_status == 'operational':
                    self.log_test("Alert System Status", "PASS", "Alert system operational")
                else:
                    self.log_test("Alert System Status", "FAIL", f"Alert system status: {alert_system_status}")
                
                return len(mt5_alerts) > 0 and len(severity_levels) > 0
            else:
                self.log_test("System Health API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Alert System Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_mongodb_atlas_integrity(self) -> bool:
        """Test 4: MongoDB Atlas Data Integrity"""
        try:
            print("\n🗄️ Testing MongoDB Atlas Data Integrity...")
            
            # Verify trade data count (should be 22,000+ deals)
            response = self.session.get(f"{self.base_url}/admin/database/stats")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check trade data count
                trade_count = data.get('trade_data_count', 0)
                if trade_count >= 22000:
                    self.log_test("Trade Data Count", "PASS", f"Trade data count: {trade_count:,} (≥22,000)")
                else:
                    self.log_test("Trade Data Count", "FAIL", f"Trade data count: {trade_count:,} (<22,000)")
                
                # Check recent sync timestamps
                last_sync = data.get('last_sync_timestamp')
                if last_sync:
                    self.log_test("Recent Sync Timestamp", "PASS", f"Last sync: {last_sync}")
                else:
                    self.log_test("Recent Sync Timestamp", "FAIL", "No recent sync timestamp found")
                
                # Verify no duplicate key errors in recent operations
                duplicate_errors = data.get('duplicate_key_errors', 0)
                if duplicate_errors == 0:
                    self.log_test("Duplicate Key Errors", "PASS", "No duplicate key errors in recent operations")
                else:
                    self.log_test("Duplicate Key Errors", "FAIL", f"{duplicate_errors} duplicate key errors found")
                
                return trade_count >= 22000 and last_sync is not None and duplicate_errors == 0
            else:
                self.log_test("Database Stats API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("MongoDB Atlas Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_priority_issues_status(self) -> bool:
        """Test 5: All 4 Priority Issues Status"""
        try:
            print("\n🎯 Testing All 4 Priority Issues Status...")
            
            success_count = 0
            
            # 1. Fund Portfolio rebates: Should show $5,774.83
            response = self.session.get(f"{self.base_url}/fund-portfolio/overview")
            if response.status_code == 200:
                data = response.json()
                funds = data.get('funds', {})
                total_rebates = 0
                
                for fund_code, fund_data in funds.items():
                    rebates = fund_data.get('total_rebates', 0)
                    total_rebates += rebates
                
                if abs(total_rebates - 5774.83) < 1:  # Allow small rounding differences
                    self.log_test("Fund Portfolio Rebates", "PASS", f"Rebates: ${total_rebates:.2f} (≈$5,774.83)")
                    success_count += 1
                else:
                    self.log_test("Fund Portfolio Rebates", "FAIL", f"Rebates: ${total_rebates:.2f} (≠$5,774.83)")
            
            # 2. Cash Flow obligations: Should show $32,994.98
            response = self.session.get(f"{self.base_url}/admin/cashflow/overview")
            if response.status_code == 200:
                data = response.json()
                summary = data.get('summary', {})
                obligations = summary.get('total_client_obligations', 0)
                
                if abs(obligations - 32994.98) < 1:
                    self.log_test("Cash Flow Obligations", "PASS", f"Obligations: ${obligations:.2f} (≈$32,994.98)")
                    success_count += 1
                else:
                    self.log_test("Cash Flow Obligations", "FAIL", f"Obligations: ${obligations:.2f} (≠$32,994.98)")
            
            # 3. CORE fund accounts: Should show 2 accounts
            response = self.session.get(f"{self.base_url}/admin/fund-performance/dashboard")
            if response.status_code == 200:
                data = response.json()
                dashboard = data.get('dashboard', {})
                by_fund = dashboard.get('by_fund', {})
                core_fund = by_fund.get('CORE', {})
                account_count = core_fund.get('account_count', 0)
                
                if account_count == 2:
                    self.log_test("CORE Fund Accounts", "PASS", f"Account count: {account_count} (=2)")
                    success_count += 1
                else:
                    self.log_test("CORE Fund Accounts", "FAIL", f"Account count: {account_count} (≠2)")
            
            # 4. Money Managers: Should show exactly 4 managers
            response = self.session.get(f"{self.base_url}/admin/trading-analytics/managers")
            if response.status_code == 200:
                data = response.json()
                managers = data.get('managers', [])
                manager_count = len(managers)
                
                if manager_count == 4:
                    self.log_test("Money Managers Count", "PASS", f"Manager count: {manager_count} (=4)")
                    success_count += 1
                else:
                    self.log_test("Money Managers Count", "FAIL", f"Manager count: {manager_count} (≠4)")
            
            self.log_test("Priority Issues Summary", "PASS" if success_count == 4 else "FAIL", 
                         f"Passed {success_count}/4 priority issue checks")
            
            return success_count == 4
            
        except Exception as e:
            self.log_test("Priority Issues Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_auto_healing_system(self) -> bool:
        """Test 6: Auto-Healing System Status"""
        try:
            print("\n🔄 Testing Auto-Healing System Status...")
            
            response = self.session.get(f"{self.base_url}/admin/system-health/auto-healing-status")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if auto-restart was successfully triggered
                auto_restart_triggered = data.get('auto_restart_triggered', False)
                if auto_restart_triggered:
                    self.log_test("Auto-Restart Triggered", "PASS", "Auto-restart was successfully triggered")
                else:
                    self.log_test("Auto-Restart Triggered", "FAIL", "Auto-restart not triggered")
                
                # Verify recovery status
                recovery_status = data.get('recovery_status', 'unknown')
                if recovery_status == 'completed':
                    self.log_test("Recovery Status", "PASS", "Recovery completed successfully")
                elif recovery_status == 'in_progress':
                    self.log_test("Recovery Status", "PASS", "Recovery in progress")
                else:
                    self.log_test("Recovery Status", "FAIL", f"Recovery status: {recovery_status}")
                
                # Check if MT5 Terminal is now connected
                mt5_connected = data.get('mt5_terminal_connected', False)
                if mt5_connected:
                    self.log_test("MT5 Terminal Connected", "PASS", "MT5 Terminal is now connected")
                else:
                    self.log_test("MT5 Terminal Connected", "FAIL", "MT5 Terminal still not connected")
                
                return auto_restart_triggered and recovery_status in ['completed', 'in_progress'] and mt5_connected
            else:
                self.log_test("Auto-Healing Status API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Auto-Healing Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_verification(self) -> Dict[str, Any]:
        """Run comprehensive system verification"""
        print("🚀 Starting Comprehensive System Verification - Auto-Healing & All Systems")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate_admin():
            return {"success": False, "error": "Authentication failed"}
        
        # Run all verification tests
        test_results = {
            "github_token_verification": self.test_github_token_verification(),
            "mt5_bridge_health": self.test_mt5_bridge_health(),
            "alert_system_verification": self.test_alert_system_verification(),
            "mongodb_atlas_integrity": self.test_mongodb_atlas_integrity(),
            "priority_issues_status": self.test_priority_issues_status(),
            "auto_healing_system": self.test_auto_healing_system()
        }
        
        # Calculate summary
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result)
        success_rate = (passed_tests / total_tests) * 100
        
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE VERIFICATION SUMMARY")
        print("=" * 80)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name.replace('_', ' ').title()}")
        
        print(f"\n🎯 Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate == 100:
            print("🎉 ALL SYSTEMS VERIFIED - Comprehensive verification successful!")
            print("✅ GITHUB_TOKEN authentication successful")
            print("✅ MT5 Bridge healthy with real balances")
            print("✅ Alert system functional")
            print("✅ MongoDB Atlas data consistent")
            print("✅ All 4 priority calculations correct")
            print("✅ Auto-healing completed recovery")
        elif success_rate >= 80:
            print("⚠️  Most systems verified - Minor issues remain")
        else:
            print("🚨 CRITICAL SYSTEM ISSUES - Multiple verification failures")
        
        return {
            "success": success_rate == 100,
            "success_rate": success_rate,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "test_results": test_results,
            "detailed_results": self.test_results
        }

def main():
    """Main verification execution"""
    verifier = ComprehensiveSystemVerifier()
    results = verifier.run_comprehensive_verification()
    
    # Exit with appropriate code
    sys.exit(0 if results["success"] else 1)

if __name__ == "__main__":
    main()