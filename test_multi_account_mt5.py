#!/usr/bin/env python3
"""
MULTI-ACCOUNT MT5 TEST SCRIPT
============================

This script demonstrates the solution to MT5's single-session limitation.
It shows how to sequentially login to multiple accounts and collect data efficiently.

USAGE:
1. Save this file on your Windows VPS where MT5 is installed
2. Ensure MetaTrader5 Python package is installed: pip install MetaTrader5
3. Run: python test_multi_account_mt5.py

This script will:
- Initialize MT5 once with the correct path
- Sequential login to each of Alejandro's 4 accounts
- Collect comprehensive data from each account
- Demonstrate proper rate limiting and error handling
- Show how data can be cached to avoid frequent logins
"""

import sys
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any

# Try to import MT5 - graceful handling if not available
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
    print("✅ MetaTrader5 package imported successfully")
except ImportError:
    MT5_AVAILABLE = False
    print("❌ MetaTrader5 package not available")
    print("💡 Install with: pip install MetaTrader5")
    sys.exit(1)

class MultiAccountMT5Tester:
    """Test class for multi-account MT5 data collection"""
    
    def __init__(self):
        # Use the correct MT5 path as provided by the user
        self.mt5_path = r"C:\Program Files\MEX Atlantic MT5 Terminal\terminal64.exe"
        self.mt5_initialized = False
        self.current_login = None
        
        # Alejandro's 4 MT5 accounts
        self.accounts = {
            886557: {
                "login": 886557,
                "password": "FIDUS13@",
                "server": "MEXAtlantic-Real",
                "fund_code": "BALANCE",
                "allocated_amount": 80000.00,
                "description": "Main BALANCE account"
            },
            886066: {
                "login": 886066,
                "password": "FIDUS13@",
                "server": "MEXAtlantic-Real",
                "fund_code": "BALANCE", 
                "allocated_amount": 10000.00,
                "description": "Secondary BALANCE account"
            },
            886602: {
                "login": 886602,
                "password": "FIDUS13@",
                "server": "MEXAtlantic-Real",
                "fund_code": "BALANCE",
                "allocated_amount": 10000.00,
                "description": "Tertiary BALANCE account"
            },
            885822: {
                "login": 885822,
                "password": "FIDUS13@",
                "server": "MEXAtlantic-Real",
                "fund_code": "CORE",
                "allocated_amount": 18151.41,
                "description": "CORE fund account"
            }
        }
        
        # Rate limiting
        self.last_login_time = 0
        self.min_login_interval = 2  # 2 seconds between logins
        
        # Results storage
        self.account_results = []
    
    def initialize_mt5(self) -> bool:
        """Initialize MT5 with the correct path - only once"""
        if self.mt5_initialized:
            return True
        
        print(f"🔧 Initializing MT5...")
        print(f"   Path: {self.mt5_path}")
        
        # Initialize with explicit path
        if mt5.initialize(path=self.mt5_path):
            self.mt5_initialized = True
            version = mt5.version()
            terminal_info = mt5.terminal_info()
            
            print(f"✅ MT5 initialized successfully!")
            print(f"   Version: {version}")
            if terminal_info:
                print(f"   Terminal: {terminal_info.name}")
                print(f"   Company: {terminal_info.company}")
                print(f"   Path: {terminal_info.path}")
            return True
        else:
            error = mt5.last_error()
            print(f"❌ MT5 initialization failed!")
            print(f"   Error: {error}")
            print(f"   Troubleshooting:")
            print(f"   1. Verify MT5 is installed at: {self.mt5_path}")
            print(f"   2. Check file permissions")
            print(f"   3. Try running as Administrator")
            return False
    
    def rate_limit_login(self):
        """Implement rate limiting between logins to avoid IP restrictions"""
        current_time = time.time()
        time_since_last = current_time - self.last_login_time
        
        if time_since_last < self.min_login_interval:
            sleep_time = self.min_login_interval - time_since_last
            print(f"⏱️ Rate limiting: waiting {sleep_time:.1f}s before next login")
            time.sleep(sleep_time)
        
        self.last_login_time = time.time()
    
    def login_to_account(self, account_config: Dict) -> bool:
        """Login to specific account with proper error handling"""
        login = account_config["login"]
        password = account_config["password"]
        server = account_config["server"]
        
        # Skip if already logged into this account
        if self.current_login == login:
            print(f"📋 Already logged into account {login}")
            return True
        
        try:
            # Rate limiting
            self.rate_limit_login()
            
            print(f"🔐 Logging into account {login}...")
            
            # Login (MT5 will automatically switch accounts - no shutdown needed)
            success = mt5.login(login, password=password, server=server)
            
            if success:
                self.current_login = login
                print(f"✅ Login successful for account {login}")
                return True
            else:
                error = mt5.last_error()
                print(f"❌ Login failed for account {login}")
                print(f"   Error: {error}")
                self.current_login = None
                return False
                
        except Exception as e:
            print(f"❌ Login exception for account {login}: {e}")
            self.current_login = None
            return False
    
    def collect_account_data(self, account_config: Dict) -> Dict[str, Any]:
        """Collect comprehensive data from one account"""
        login = account_config["login"]
        
        print(f"\\n📊 Collecting data from account {login} ({account_config['fund_code']})...")
        print(f"   Description: {account_config['description']}")
        print(f"   Allocated: ${account_config['allocated_amount']:,.2f}")
        
        # Login to account
        if not self.login_to_account(account_config):
            return {
                "success": False,
                "login": login,
                "fund_code": account_config["fund_code"],
                "error": "Failed to login"
            }
        
        result = {
            "success": True,
            "login": login,
            "fund_code": account_config["fund_code"],
            "allocated_amount": account_config["allocated_amount"],
            "collected_at": datetime.now().isoformat()
        }
        
        try:
            # 1. Get account information
            print(f"   📈 Getting account info...")
            account_info = mt5.account_info()
            
            if account_info:
                balance = account_info.balance
                equity = account_info.equity
                profit = account_info.profit
                margin = account_info.margin
                margin_free = account_info.margin_free
                
                result["account_info"] = {
                    "balance": balance,
                    "equity": equity,
                    "profit": profit,
                    "margin": margin,
                    "margin_free": margin_free,
                    "currency": account_info.currency,
                    "leverage": account_info.leverage,
                    "server": account_info.server
                }
                
                # Calculate performance
                allocated = account_config["allocated_amount"]
                return_pct = (profit / allocated * 100) if allocated > 0 else 0
                
                result["performance"] = {
                    "return_percentage": return_pct,
                    "equity_vs_allocated": equity - allocated
                }
                
                print(f"   💰 Balance: ${balance:,.2f}")
                print(f"   📊 Equity: ${equity:,.2f}")
                print(f"   📈 Profit: ${profit:,.2f} ({return_pct:+.2f}%)")
                print(f"   💳 Margin Used: ${margin:,.2f}")
                print(f"   💵 Free Margin: ${margin_free:,.2f}")
            else:
                print(f"   ⚠️ Could not retrieve account info")
                result["account_info"] = None
            
            # 2. Get open positions
            print(f"   🎯 Getting open positions...")
            positions = mt5.positions_get()
            
            if positions is not None:
                position_count = len(positions)
                total_position_profit = sum(pos.profit for pos in positions)
                
                positions_data = []
                for pos in positions:
                    positions_data.append({
                        "symbol": pos.symbol,
                        "type": "buy" if pos.type == 0 else "sell",
                        "volume": pos.volume,
                        "profit": pos.profit,
                        "price_open": pos.price_open,
                        "price_current": pos.price_current
                    })
                
                result["positions"] = {
                    "count": position_count,
                    "total_profit": total_position_profit,
                    "positions": positions_data
                }
                
                print(f"   🎯 Open Positions: {position_count}")
                if total_position_profit != 0:
                    print(f"   📊 Position P&L: ${total_position_profit:,.2f}")
            else:
                result["positions"] = {"count": 0, "total_profit": 0, "positions": []}
                print(f"   📊 No open positions")
            
            # 3. Get recent trading history (last 3 days)
            print(f"   📜 Getting recent trading history...")
            from_date = datetime.now() - timedelta(days=3)
            to_date = datetime.now()
            
            deals = mt5.history_deals_get(from_date, to_date)
            
            if deals is not None:
                recent_deals = [deal for deal in deals if deal.profit != 0]
                recent_profit = sum(deal.profit for deal in recent_deals)
                
                result["recent_history"] = {
                    "deals_count": len(recent_deals),
                    "profit_3d": recent_profit,
                    "period_days": 3
                }
                
                print(f"   📜 Recent deals (3d): {len(recent_deals)}")
                if recent_profit != 0:
                    print(f"   💰 Recent profit (3d): ${recent_profit:,.2f}")
            else:
                result["recent_history"] = {"deals_count": 0, "profit_3d": 0}
                print(f"   📜 No recent trading history available")
            
            return result
            
        except Exception as e:
            print(f"   ❌ Error collecting data: {e}")
            result["success"] = False
            result["error"] = str(e)
            return result
    
    def run_multi_account_test(self):
        """Run the complete multi-account test"""
        print("🚀 MULTI-ACCOUNT MT5 TEST")
        print("=" * 80)
        print("This test demonstrates the solution to MT5's single-session limitation")
        print("using sequential login pattern for multiple accounts.")
        print("=" * 80)
        
        # 1. Initialize MT5
        if not self.initialize_mt5():
            print("❌ Cannot continue without MT5 initialization")
            return False
        
        # 2. Sequential data collection
        print(f"\\n📊 SEQUENTIAL DATA COLLECTION")
        print("=" * 50)
        print(f"Collecting data from {len(self.accounts)} MT5 accounts...")
        
        start_time = time.time()
        successful_accounts = 0
        
        for i, (login, account_config) in enumerate(self.accounts.items(), 1):
            print(f"\\n[{i}/{len(self.accounts)}] Processing account {login}...")
            
            result = self.collect_account_data(account_config)
            self.account_results.append(result)
            
            if result["success"]:
                successful_accounts += 1
                print(f"✅ Account {login} data collection successful")
            else:
                print(f"❌ Account {login} data collection failed: {result.get('error', 'Unknown error')}")
        
        collection_time = time.time() - start_time
        
        # 3. Generate summary report
        print(f"\\n📈 COLLECTION SUMMARY")
        print("=" * 50)
        print(f"Accounts processed: {successful_accounts}/{len(self.accounts)}")
        print(f"Collection time: {collection_time:.1f} seconds")
        
        if successful_accounts > 0:
            self.generate_portfolio_report()
        
        return successful_accounts == len(self.accounts)
    
    def generate_portfolio_report(self):
        """Generate comprehensive portfolio report"""
        print(f"\\n💼 PORTFOLIO ANALYSIS")
        print("=" * 50)
        
        total_allocated = 118151.41
        total_equity = 0
        total_profit = 0
        total_positions = 0
        
        balance_fund_equity = 0
        balance_fund_profit = 0
        balance_fund_accounts = 0
        
        core_fund_equity = 0
        core_fund_profit = 0
        core_fund_accounts = 0
        
        for result in self.account_results:
            if not result.get("success") or not result.get("account_info"):
                continue
            
            account_info = result["account_info"]
            fund_code = result["fund_code"]
            
            equity = account_info["equity"]
            profit = account_info["profit"]
            positions_count = result.get("positions", {}).get("count", 0)
            
            total_equity += equity
            total_profit += profit
            total_positions += positions_count
            
            if fund_code == "BALANCE":
                balance_fund_equity += equity
                balance_fund_profit += profit
                balance_fund_accounts += 1
            elif fund_code == "CORE":
                core_fund_equity += equity
                core_fund_profit += profit
                core_fund_accounts += 1
            
            print(f"Account {result['login']} ({fund_code}):")
            print(f"   Equity: ${equity:,.2f} | P&L: ${profit:,.2f} | Positions: {positions_count}")
        
        # Overall portfolio metrics
        overall_return = (total_profit / total_allocated * 100) if total_allocated > 0 else 0
        
        print(f"\\n📊 OVERALL PORTFOLIO:")
        print(f"   Total Allocated: ${total_allocated:,.2f}")
        print(f"   Total Equity: ${total_equity:,.2f}")
        print(f"   Total P&L: ${total_profit:,.2f}")
        print(f"   Overall Return: {overall_return:+.2f}%")
        print(f"   Open Positions: {total_positions}")
        
        # Fund breakdown
        print(f"\\n💰 BY FUND:")
        print(f"   BALANCE Fund ({balance_fund_accounts} accounts):")
        print(f"      Allocated: $100,000.00")
        print(f"      Equity: ${balance_fund_equity:,.2f}")
        print(f"      P&L: ${balance_fund_profit:,.2f}")
        if balance_fund_equity > 0:
            balance_return = (balance_fund_profit / 100000 * 100)
            print(f"      Return: {balance_return:+.2f}%")
        
        print(f"   CORE Fund ({core_fund_accounts} accounts):")
        print(f"      Allocated: $18,151.41")
        print(f"      Equity: ${core_fund_equity:,.2f}")
        print(f"      P&L: ${core_fund_profit:,.2f}")
        if core_fund_equity > 0:
            core_return = (core_fund_profit / 18151.41 * 100)
            print(f"      Return: {core_return:+.2f}%")
        
        # Performance vs expected
        print(f"\\n🎯 PERFORMANCE vs EXPECTED:")
        balance_expected_monthly = 100000 * 0.025  # 2.5%
        core_expected_monthly = 18151.41 * 0.015   # 1.5%
        
        print(f"   BALANCE Expected (monthly): ${balance_expected_monthly:,.2f}")
        print(f"   CORE Expected (monthly): ${core_expected_monthly:,.2f}")
        print(f"   Total Expected: ${balance_expected_monthly + core_expected_monthly:,.2f}/month")
    
    def cleanup(self):
        """Cleanup MT5 connection"""
        if self.mt5_initialized:
            print(f"\\n🔌 Closing MT5 connection...")
            mt5.shutdown()
            self.mt5_initialized = False
            self.current_login = None
            print("✅ MT5 connection closed")

def main():
    """Main test function"""
    tester = MultiAccountMT5Tester()
    
    try:
        success = tester.run_multi_account_test()
        
        if success:
            print(f"\\n🎉 MULTI-ACCOUNT TEST COMPLETED SUCCESSFULLY!")
            print(f"💡 This demonstrates how to handle MT5's single-session limitation")
            print(f"💡 The sequential login pattern works for multiple accounts")
        else:
            print(f"\\n⚠️ MULTI-ACCOUNT TEST COMPLETED WITH ISSUES")
            print(f"💡 Some accounts may have connection problems")
        
        print(f"\\n🚀 NEXT STEPS:")
        print(f"   1. Update your MT5 Bridge Service with this approach")
        print(f"   2. Implement caching to reduce login frequency")
        print(f"   3. Add this to FIDUS Backend for live data")
        
    except Exception as e:
        print(f"\\n❌ TEST FAILED: {e}")
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main()