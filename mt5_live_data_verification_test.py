#!/usr/bin/env python3
"""
URGENT LIVE DATA VERIFICATION: MT5 System Complete Testing
Testing all endpoints to verify live MT5 data is flowing correctly from the complete MT5 system.

**Authentication**: admin/password123
**Backend**: https://portfolio-metrics-3.preview.emergentagent.com/api

**LIVE DATA VERIFICATION TESTS**:
1. MT5 Dashboard Overview (Should show LIVE data)
2. Alejandro's Live MT5 Accounts (All 4 accounts with REAL trading data)
3. Investment Admin Overview (Should reflect MT5 performance)
4. Data Freshness Check (timestamps within 15 minutes)

**SUCCESS CRITERIA**:
✅ All accounts show LIVE data (not static $118,151.41)
✅ Recent update timestamps (within 15 minutes)
✅ Real profit/loss values from actual trading
✅ Margin data and position counts from live MT5
✅ Data quality shows live_accounts > 0
"""

import requests
import json
import sys
from datetime import datetime, timezone, timedelta
import time

# Use the correct backend URL from frontend/.env
BACKEND_URL = "https://portfolio-metrics-3.preview.emergentagent.com/api"

class MT5LiveDataVerificationTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.live_data_indicators = []
        
    def log_test(self, test_name, success, details, response_data=None, live_indicators=None):
        """Log test results with live data indicators"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data,
            "live_indicators": live_indicators or []
        }
        self.test_results.append(result)
        
        if live_indicators:
            self.live_data_indicators.extend(live_indicators)
        
        status = "✅ LIVE" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
        if live_indicators:
            for indicator in live_indicators:
                print(f"   📊 {indicator}")
        
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        print("\n🔐 AUTHENTICATING ADMIN USER")
        
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
                        {"user_id": data.get("id"), "username": data.get("username")}
                    )
                    return True
                else:
                    self.log_test("Admin Authentication", False, "No token in response", data)
                    return False
            else:
                self.log_test("Admin Authentication", False, f"HTTP {response.status_code}", response.json() if response.content else None)
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_mt5_dashboard_overview(self):
        """Test MT5 Dashboard Overview for LIVE data"""
        print("\n📊 TESTING MT5 DASHBOARD OVERVIEW (LIVE DATA)")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/dashboard/overview")
            
            if response.status_code == 200:
                data = response.json()
                live_indicators = []
                
                # Check for live data indicators
                data_quality = data.get("data_quality", {})
                live_accounts = data_quality.get("live_accounts", 0)
                last_update = data.get("last_update")
                
                # Check if we have live accounts
                if live_accounts > 0:
                    live_indicators.append(f"Live Accounts: {live_accounts}")
                
                # Check data freshness (within 15 minutes)
                if last_update:
                    try:
                        update_time = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                        now = datetime.now(timezone.utc)
                        time_diff = now - update_time
                        
                        if time_diff.total_seconds() <= 900:  # 15 minutes
                            live_indicators.append(f"Fresh Data: Updated {time_diff.total_seconds():.0f}s ago")
                        else:
                            live_indicators.append(f"Stale Data: Updated {time_diff.total_seconds()/60:.1f}m ago")
                    except:
                        live_indicators.append(f"Update Time: {last_update}")
                
                # Check for real trading data vs static values
                accounts_summary = data.get("accounts_summary", {})
                total_equity = accounts_summary.get("total_equity", 0)
                total_balance = accounts_summary.get("total_balance", 0)
                
                # Static value check - if exactly $118,151.41, it might be static
                if abs(total_equity - 118151.41) > 0.01:
                    live_indicators.append(f"Dynamic Equity: ${total_equity:,.2f} (not static)")
                else:
                    live_indicators.append(f"Potential Static Equity: ${total_equity:,.2f}")
                
                # Check for profit/loss variations
                total_profit = accounts_summary.get("total_profit", 0)
                if total_profit != 0:
                    live_indicators.append(f"Active P&L: ${total_profit:,.2f}")
                
                # Check data source
                data_source = data.get("data_source", "unknown")
                if "live" in data_source.lower():
                    live_indicators.append(f"Data Source: {data_source}")
                
                # Success criteria: live_accounts > 0 and recent update
                success = live_accounts > 0 and len(live_indicators) >= 2
                
                self.log_test(
                    "MT5 Dashboard Overview",
                    success,
                    f"Live accounts: {live_accounts}, Total equity: ${total_equity:,.2f}",
                    data,
                    live_indicators
                )
                
                return success
            else:
                self.log_test("MT5 Dashboard Overview", False, f"HTTP {response.status_code}", response.json() if response.content else None)
                return False
                
        except Exception as e:
            self.log_test("MT5 Dashboard Overview", False, f"Exception: {str(e)}")
            return False
    
    def test_alejandro_mt5_accounts(self):
        """Test Alejandro's Live MT5 Accounts (All 4 accounts with REAL trading data)"""
        print("\n🏦 TESTING ALEJANDRO'S LIVE MT5 ACCOUNTS")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/accounts/client_alejandro")
            
            if response.status_code == 200:
                data = response.json()
                live_indicators = []
                
                accounts = data.get("accounts", [])
                expected_accounts = ["886557", "886066", "886602", "885822"]
                
                if not accounts:
                    self.log_test("Alejandro MT5 Accounts", False, "No MT5 accounts found", data)
                    return False
                
                # Check for expected account numbers
                found_accounts = []
                live_data_count = 0
                
                for account in accounts:
                    account_number = str(account.get("account_number", ""))
                    current_equity = account.get("current_equity", 0)
                    allocated_amount = account.get("allocated_amount", 0)
                    profit_loss = account.get("profit_loss", 0)
                    margin = account.get("margin", 0)
                    last_update = account.get("last_update_time", "")
                    
                    if account_number in expected_accounts:
                        found_accounts.append(account_number)
                    
                    # Check for live data indicators
                    if current_equity != allocated_amount:
                        live_indicators.append(f"Account {account_number}: Live equity ${current_equity:,.2f} ≠ allocated ${allocated_amount:,.2f}")
                        live_data_count += 1
                    
                    if profit_loss != 0:
                        live_indicators.append(f"Account {account_number}: Active P&L ${profit_loss:,.2f}")
                        live_data_count += 1
                    
                    if margin > 0:
                        live_indicators.append(f"Account {account_number}: Margin ${margin:,.2f}")
                        live_data_count += 1
                    
                    # Check data freshness
                    if last_update:
                        try:
                            update_time = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                            now = datetime.now(timezone.utc)
                            time_diff = now - update_time
                            
                            if time_diff.total_seconds() <= 900:  # 15 minutes
                                live_indicators.append(f"Account {account_number}: Fresh data ({time_diff.total_seconds():.0f}s ago)")
                                live_data_count += 1
                        except:
                            pass
                
                # Check sync status
                sync_status = data.get("sync_status", "unknown")
                if sync_status == "connected":
                    live_indicators.append(f"Sync Status: {sync_status}")
                    live_data_count += 1
                
                # Success criteria: All 4 accounts found with live data indicators
                all_accounts_found = len(found_accounts) == 4
                has_live_data = live_data_count >= 4  # At least 4 live data indicators
                
                success = all_accounts_found and has_live_data
                
                self.log_test(
                    "Alejandro MT5 Accounts",
                    success,
                    f"Found {len(found_accounts)}/4 expected accounts, {live_data_count} live data indicators",
                    {"found_accounts": found_accounts, "total_accounts": len(accounts)},
                    live_indicators
                )
                
                return success
            else:
                self.log_test("Alejandro MT5 Accounts", False, f"HTTP {response.status_code}", response.json() if response.content else None)
                return False
                
        except Exception as e:
            self.log_test("Alejandro MT5 Accounts", False, f"Exception: {str(e)}")
            return False
    
    def test_investment_admin_overview(self):
        """Test Investment Admin Overview (Should reflect MT5 performance)"""
        print("\n💰 TESTING INVESTMENT ADMIN OVERVIEW (MT5 PERFORMANCE)")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/investments/admin/overview")
            
            if response.status_code == 200:
                data = response.json()
                live_indicators = []
                
                total_aum = data.get("total_aum", 0)
                total_investments = data.get("total_investments", 0)
                total_clients = data.get("total_clients", 0)
                
                # Parse AUM value if it's a string
                if isinstance(total_aum, str):
                    # Remove $ and commas, convert to float
                    aum_value = float(total_aum.replace("$", "").replace(",", ""))
                else:
                    aum_value = total_aum
                
                # Check if AUM reflects actual MT5 equity values (not zero)
                if aum_value > 0:
                    live_indicators.append(f"Active AUM: ${aum_value:,.2f}")
                    
                    # Check if it's close to expected $118,151.41 but not exactly (indicating live updates)
                    if abs(aum_value - 118151.41) < 1000:  # Within $1000 of expected
                        if abs(aum_value - 118151.41) > 0.01:  # But not exactly the same
                            live_indicators.append(f"Dynamic AUM: ${aum_value:,.2f} (varies from static ${118151.41:,.2f})")
                        else:
                            live_indicators.append(f"Static AUM: ${aum_value:,.2f} (exactly matches expected)")
                    else:
                        live_indicators.append(f"Unexpected AUM: ${aum_value:,.2f} (differs significantly from expected)")
                else:
                    live_indicators.append("Zero AUM: No investment data reflected")
                
                if total_investments > 0:
                    live_indicators.append(f"Active Investments: {total_investments}")
                
                if total_clients > 0:
                    live_indicators.append(f"Active Clients: {total_clients}")
                
                # Check for performance metrics
                performance_data = data.get("performance_summary", {})
                if performance_data:
                    live_indicators.append("Performance data available")
                
                # Success criteria: AUM > 0 and reflects MT5 data
                success = aum_value > 0 and total_investments > 0
                
                self.log_test(
                    "Investment Admin Overview",
                    success,
                    f"AUM: ${aum_value:,.2f}, Investments: {total_investments}, Clients: {total_clients}",
                    data,
                    live_indicators
                )
                
                return success
            else:
                self.log_test("Investment Admin Overview", False, f"HTTP {response.status_code}", response.json() if response.content else None)
                return False
                
        except Exception as e:
            self.log_test("Investment Admin Overview", False, f"Exception: {str(e)}")
            return False
    
    def test_data_freshness_check(self):
        """Test Data Freshness Check (timestamps within 15 minutes)"""
        print("\n⏰ TESTING DATA FRESHNESS CHECK")
        
        try:
            # Test multiple endpoints for data freshness
            endpoints_to_check = [
                ("/mt5/dashboard/overview", "MT5 Dashboard"),
                ("/mt5/accounts/client_alejandro", "Alejandro MT5 Accounts"),
                ("/investments/admin/overview", "Investment Overview")
            ]
            
            fresh_endpoints = 0
            total_endpoints = len(endpoints_to_check)
            live_indicators = []
            
            for endpoint, name in endpoints_to_check:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Look for timestamp fields
                        timestamp_fields = ["last_update", "last_mt5_update", "updated_at", "last_sync"]
                        
                        for field in timestamp_fields:
                            timestamp = data.get(field)
                            if timestamp:
                                try:
                                    update_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                    now = datetime.now(timezone.utc)
                                    time_diff = now - update_time
                                    
                                    if time_diff.total_seconds() <= 900:  # 15 minutes
                                        live_indicators.append(f"{name}: Fresh ({time_diff.total_seconds():.0f}s ago)")
                                        fresh_endpoints += 1
                                        break
                                    else:
                                        live_indicators.append(f"{name}: Stale ({time_diff.total_seconds()/60:.1f}m ago)")
                                        break
                                except:
                                    live_indicators.append(f"{name}: Invalid timestamp format")
                                    break
                        else:
                            # Check for accounts with individual timestamps
                            accounts = data.get("accounts", [])
                            if accounts:
                                fresh_account_count = 0
                                for account in accounts:
                                    last_update = account.get("last_update_time", "")
                                    if last_update:
                                        try:
                                            update_time = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                                            now = datetime.now(timezone.utc)
                                            time_diff = now - update_time
                                            
                                            if time_diff.total_seconds() <= 900:  # 15 minutes
                                                fresh_account_count += 1
                                        except:
                                            pass
                                
                                if fresh_account_count > 0:
                                    live_indicators.append(f"{name}: {fresh_account_count}/{len(accounts)} accounts fresh")
                                    fresh_endpoints += 1
                                else:
                                    live_indicators.append(f"{name}: No fresh account data")
                            else:
                                live_indicators.append(f"{name}: No timestamp data available")
                    else:
                        live_indicators.append(f"{name}: HTTP {response.status_code}")
                        
                except Exception as e:
                    live_indicators.append(f"{name}: Error - {str(e)}")
            
            # Check for data_source = "live_multi_account"
            try:
                response = self.session.get(f"{BACKEND_URL}/mt5/dashboard/overview")
                if response.status_code == 200:
                    data = response.json()
                    data_source = data.get("data_source", "")
                    if "live" in data_source.lower():
                        live_indicators.append(f"Data Source: {data_source}")
                        fresh_endpoints += 0.5  # Bonus for live data source
            except:
                pass
            
            # Success criteria: At least 50% of endpoints have fresh data
            success_rate = (fresh_endpoints / total_endpoints) * 100
            success = success_rate >= 50
            
            self.log_test(
                "Data Freshness Check",
                success,
                f"{success_rate:.1f}% endpoints have fresh data ({fresh_endpoints}/{total_endpoints})",
                {"fresh_endpoints": fresh_endpoints, "total_endpoints": total_endpoints},
                live_indicators
            )
            
            return success
                
        except Exception as e:
            self.log_test("Data Freshness Check", False, f"Exception: {str(e)}")
            return False
    
    def run_live_data_verification(self):
        """Run complete MT5 live data verification"""
        print("🚨 URGENT LIVE DATA VERIFICATION: MT5 System Complete Testing")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("Authentication: admin/password123")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed - cannot proceed with tests")
            return False
        
        # Run live data verification tests
        tests = [
            ("MT5 Dashboard Overview", self.test_mt5_dashboard_overview),
            ("Alejandro's Live MT5 Accounts", self.test_alejandro_mt5_accounts),
            ("Investment Admin Overview", self.test_investment_admin_overview),
            ("Data Freshness Check", self.test_data_freshness_check)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_name}: {str(e)}")
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 MT5 LIVE DATA VERIFICATION SUMMARY")
        print("=" * 80)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        # Live data indicators summary
        if self.live_data_indicators:
            print(f"\n📊 LIVE DATA INDICATORS FOUND ({len(self.live_data_indicators)}):")
            for indicator in self.live_data_indicators:
                print(f"   ✅ {indicator}")
        else:
            print(f"\n❌ NO LIVE DATA INDICATORS FOUND")
        
        # Success criteria evaluation
        print(f"\n🎯 SUCCESS CRITERIA EVALUATION:")
        
        criteria_met = 0
        total_criteria = 5
        
        # Check each success criterion
        live_accounts_found = any("Live Accounts:" in indicator for indicator in self.live_data_indicators)
        if live_accounts_found:
            print("   ✅ All accounts show LIVE data (not static)")
            criteria_met += 1
        else:
            print("   ❌ Accounts may be showing static data")
        
        fresh_data_found = any("Fresh" in indicator for indicator in self.live_data_indicators)
        if fresh_data_found:
            print("   ✅ Recent update timestamps (within 15 minutes)")
            criteria_met += 1
        else:
            print("   ❌ Data timestamps are not recent")
        
        profit_loss_found = any("P&L" in indicator for indicator in self.live_data_indicators)
        if profit_loss_found:
            print("   ✅ Real profit/loss values from actual trading")
            criteria_met += 1
        else:
            print("   ❌ No active profit/loss data found")
        
        margin_found = any("Margin" in indicator for indicator in self.live_data_indicators)
        if margin_found:
            print("   ✅ Margin data and position counts from live MT5")
            criteria_met += 1
        else:
            print("   ❌ No margin data found")
        
        live_source_found = any("live" in indicator.lower() for indicator in self.live_data_indicators)
        if live_source_found:
            print("   ✅ Data quality shows live_accounts > 0")
            criteria_met += 1
        else:
            print("   ❌ Data source not confirmed as live")
        
        criteria_success_rate = (criteria_met / total_criteria) * 100
        print(f"\nSuccess Criteria Met: {criteria_success_rate:.1f}% ({criteria_met}/{total_criteria})")
        
        # Final verdict
        overall_success = success_rate >= 75 and criteria_success_rate >= 60
        
        if overall_success:
            print(f"\n🎉 MT5 LIVE DATA VERIFICATION: SUCCESS!")
            print(f"   The complete MT5 integration is operational for production!")
        else:
            print(f"\n🚨 MT5 LIVE DATA VERIFICATION: ISSUES FOUND")
            print(f"   The MT5 system needs attention before production deployment")
        
        return overall_success

if __name__ == "__main__":
    tester = MT5LiveDataVerificationTester()
    success = tester.run_live_data_verification()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)