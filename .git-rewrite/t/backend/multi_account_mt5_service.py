"""
MULTI-ACCOUNT MT5 SERVICE FOR FIDUS
===================================

Solves the MT5 single-session limitation using sequential login pattern.
Cycles through Alejandro's 4 MT5 accounts to collect data efficiently.

APPROACH:
1. Initialize MT5 once with correct path
2. Sequential login to each account (no shutdown needed between logins)
3. Collect all data for that account
4. Move to next account
5. Cache data to avoid frequent reconnections
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta
import time
import os
from motor.motor_asyncio import AsyncIOMotorClient

# MT5 imports (will be imported when needed to avoid issues if not installed)
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("⚠️ MetaTrader5 package not available - using simulation mode")

class MultiAccountMT5Service:
    """
    Manages multiple MT5 accounts using sequential login pattern.
    Optimized for Alejandro's 4 accounts with proper caching and error handling.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.mt5_initialized = False
        self.current_login = None
        
        # Alejandro's 4 MT5 accounts as specified
        self.alejandro_accounts = {
            886557: {
                "login": 886557,
                "password": "FIDUS13@",
                "server": "MEXAtlantic-Real",
                "fund_code": "BALANCE",
                "allocated_amount": 80000.00,
                "client_id": "client_alejandro",
                "description": "Main BALANCE account"
            },
            886066: {
                "login": 886066,
                "password": "FIDUS13@",
                "server": "MEXAtlantic-Real", 
                "fund_code": "BALANCE",
                "allocated_amount": 10000.00,
                "client_id": "client_alejandro",
                "description": "Secondary BALANCE account"
            },
            886602: {
                "login": 886602,
                "password": "FIDUS13@",
                "server": "MEXAtlantic-Real",
                "fund_code": "BALANCE", 
                "allocated_amount": 10000.00,
                "client_id": "client_alejandro",
                "description": "Tertiary BALANCE account"
            },
            885822: {
                "login": 885822,
                "password": "FIDUS13@",
                "server": "MEXAtlantic-Real",
                "fund_code": "CORE",
                "allocated_amount": 18151.41,
                "client_id": "client_alejandro",
                "description": "CORE fund account"
            }
        }
        
        # Data cache to avoid frequent logins
        self.account_data_cache = {}
        self.last_update_time = None
        self.cache_duration_minutes = 5  # Cache data for 5 minutes
        
        # Rate limiting
        self.last_login_time = 0
        self.min_login_interval = 2  # Minimum 2 seconds between logins
        
        # MongoDB connection
        self.db = None
        
        # MT5 path configuration
        self.mt5_path = r"C:\Program Files\MEX Atlantic MT5 Terminal\terminal64.exe"
    
    async def initialize_mt5(self) -> bool:
        """Initialize MT5 with correct path - only once per service lifetime"""
        if not MT5_AVAILABLE:
            self.logger.warning("MT5 package not available - using simulation mode")
            return False
            
        if self.mt5_initialized:
            return True
        
        try:
            self.logger.info(f"🔧 Initializing MT5 with path: {self.mt5_path}")
            
            # Initialize with explicit path
            if mt5.initialize(path=self.mt5_path):
                self.mt5_initialized = True
                version = mt5.version()
                terminal_info = mt5.terminal_info()
                
                self.logger.info(f"✅ MT5 initialized successfully!")
                self.logger.info(f"   Version: {version}")
                if terminal_info:
                    self.logger.info(f"   Terminal: {terminal_info.name}")
                    self.logger.info(f"   Company: {terminal_info.company}")
                
                return True
            else:
                error = mt5.last_error()
                self.logger.error(f"❌ MT5 initialization failed: {error}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ MT5 initialization exception: {e}")
            return False
    
    def _rate_limit_login(self):
        """Implement rate limiting between account logins"""
        current_time = time.time()
        time_since_last_login = current_time - self.last_login_time
        
        if time_since_last_login < self.min_login_interval:
            sleep_time = self.min_login_interval - time_since_last_login
            self.logger.info(f"⏱️ Rate limiting: sleeping {sleep_time:.1f}s before next login")
            time.sleep(sleep_time)
        
        self.last_login_time = time.time()
    
    async def login_to_account(self, account_config: Dict) -> bool:
        """Login to specific MT5 account with rate limiting"""
        if not self.mt5_initialized:
            if not await self.initialize_mt5():
                return False
        
        login = account_config["login"]
        password = account_config["password"]
        server = account_config["server"]
        
        # Skip login if already logged into this account
        if self.current_login == login:
            self.logger.info(f"📋 Already logged into account {login}")
            return True
        
        try:
            # Rate limit to avoid IP restrictions
            self._rate_limit_login()
            
            self.logger.info(f"🔐 Logging into MT5 account {login} on {server}")
            
            # Attempt login (no shutdown needed - MT5 will switch accounts)
            success = mt5.login(login, password=password, server=server)
            
            if success:
                self.current_login = login
                self.logger.info(f"✅ Successfully logged into account {login}")
                return True
            else:
                error = mt5.last_error()
                self.logger.error(f"❌ Login failed for account {login}: {error}")
                self.current_login = None
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Login exception for account {login}: {e}")
            self.current_login = None
            return False
    
    async def collect_account_data(self, account_config: Dict) -> Dict[str, Any]:
        """Collect comprehensive data from a single MT5 account"""
        login = account_config["login"]
        
        try:
            # Login to the account
            if not await self.login_to_account(account_config):
                return {
                    "success": False,
                    "login": login,
                    "error": "Failed to login to account"
                }
            
            account_data = {
                "success": True,
                "login": login,
                "fund_code": account_config["fund_code"],
                "allocated_amount": account_config["allocated_amount"],
                "collected_at": datetime.now(timezone.utc).isoformat()
            }
            
            # 1. Get account info (balance, equity, margin)
            self.logger.info(f"📊 Collecting account info for {login}")
            account_info = mt5.account_info()
            
            if account_info:
                account_data["account_info"] = {
                    "balance": account_info.balance,
                    "equity": account_info.equity,
                    "margin": account_info.margin,
                    "margin_free": account_info.margin_free,
                    "margin_level": account_info.margin_level,
                    "profit": account_info.profit,
                    "currency": account_info.currency,
                    "leverage": account_info.leverage,
                    "server": account_info.server,
                    "name": account_info.name,
                    "company": account_info.company
                }
                
                # Calculate performance metrics
                profit = account_info.profit
                allocated = account_config["allocated_amount"]
                return_pct = (profit / allocated * 100) if allocated > 0 else 0
                
                account_data["performance"] = {
                    "profit_loss": profit,
                    "return_percentage": return_pct,
                    "equity_vs_allocated": account_info.equity - allocated
                }
                
                self.logger.info(f"   Balance: ${account_info.balance:,.2f}")
                self.logger.info(f"   Equity: ${account_info.equity:,.2f}")
                self.logger.info(f"   P&L: ${profit:,.2f} ({return_pct:.2f}%)")
            else:
                account_data["account_info"] = None
                self.logger.warning(f"⚠️ Could not get account info for {login}")
            
            # 2. Get open positions
            self.logger.info(f"📈 Collecting positions for {login}")
            positions = mt5.positions_get()
            
            if positions is not None:
                positions_list = []
                total_position_profit = 0
                
                for pos in positions:
                    position_data = {
                        "ticket": pos.ticket,
                        "symbol": pos.symbol,
                        "type": pos.type,
                        "type_str": "buy" if pos.type == 0 else "sell",
                        "volume": pos.volume,
                        "price_open": pos.price_open,
                        "price_current": pos.price_current,
                        "profit": pos.profit,
                        "swap": pos.swap,
                        "commission": pos.commission,
                        "sl": pos.sl,
                        "tp": pos.tp,
                        "time": pos.time,
                        "comment": pos.comment
                    }
                    positions_list.append(position_data)
                    total_position_profit += pos.profit
                
                account_data["positions"] = {
                    "count": len(positions_list),
                    "positions": positions_list,
                    "total_profit": total_position_profit
                }
                
                self.logger.info(f"   Open positions: {len(positions_list)}")
                if positions_list:
                    self.logger.info(f"   Position P&L: ${total_position_profit:,.2f}")
            else:
                account_data["positions"] = {
                    "count": 0,
                    "positions": [],
                    "total_profit": 0
                }
            
            # 3. Get recent trading history (last 7 days for performance)
            self.logger.info(f"📜 Collecting recent history for {login}")
            from_date = datetime.now() - timedelta(days=7)
            to_date = datetime.now()
            
            deals = mt5.history_deals_get(from_date, to_date)
            
            if deals is not None:
                recent_profit = sum(deal.profit for deal in deals if deal.profit != 0)
                deal_count = len([deal for deal in deals if deal.profit != 0])
                
                account_data["recent_history"] = {
                    "deals_count": deal_count,
                    "recent_profit_7d": recent_profit,
                    "period": "7_days"
                }
                
                self.logger.info(f"   Recent deals (7d): {deal_count}")
                if recent_profit != 0:
                    self.logger.info(f"   Recent profit (7d): ${recent_profit:,.2f}")
            else:
                account_data["recent_history"] = {
                    "deals_count": 0,
                    "recent_profit_7d": 0,
                    "period": "7_days"
                }
            
            return account_data
            
        except Exception as e:
            self.logger.error(f"❌ Failed to collect data for account {login}: {e}")
            return {
                "success": False,
                "login": login,
                "error": str(e)
            }
    
    async def collect_all_alejandro_data(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Collect data from all 4 of Alejandro's MT5 accounts using sequential login.
        Uses caching to avoid frequent logins.
        """
        # Check cache first
        if not force_refresh and self._is_cache_valid():
            self.logger.info("📋 Using cached MT5 data")
            return self._get_cached_summary()
        
        self.logger.info("🚀 Collecting live data from all 4 MT5 accounts")
        
        results = {
            "success": True,
            "client_id": "client_alejandro", 
            "accounts_collected": 0,
            "accounts_failed": 0,
            "account_data": [],
            "summary": {},
            "collection_started": datetime.now(timezone.utc).isoformat(),
            "collection_completed": None
        }
        
        # Sequential collection from each account
        for login, account_config in self.alejandro_accounts.items():
            self.logger.info(f"📊 Processing account {login} ({account_config['fund_code']})...")
            
            account_result = await self.collect_account_data(account_config)
            results["account_data"].append(account_result)
            
            if account_result["success"]:
                results["accounts_collected"] += 1
                self.logger.info(f"✅ Successfully collected data from account {login}")
            else:
                results["accounts_failed"] += 1
                self.logger.error(f"❌ Failed to collect data from account {login}")
        
        # Calculate summary statistics
        results["summary"] = self._calculate_portfolio_summary(results["account_data"])
        results["collection_completed"] = datetime.now(timezone.utc).isoformat()
        
        # Cache the results
        self.account_data_cache = results
        self.last_update_time = datetime.now(timezone.utc)
        
        self.logger.info(f"📈 Collection complete: {results['accounts_collected']}/4 accounts successful")
        
        return results
    
    def _calculate_portfolio_summary(self, account_data_list: List[Dict]) -> Dict[str, Any]:
        """Calculate portfolio-wide summary statistics"""
        summary = {
            "total_allocated": 118151.41,  # Fixed total for Alejandro
            "total_equity": 0.0,
            "total_balance": 0.0,
            "total_profit": 0.0,
            "total_positions": 0,
            "overall_return_pct": 0.0,
            "by_fund": {
                "BALANCE": {"allocated": 100000.00, "equity": 0.0, "profit": 0.0, "accounts": 0},
                "CORE": {"allocated": 18151.41, "equity": 0.0, "profit": 0.0, "accounts": 0}
            }
        }
        
        for account_data in account_data_list:
            if not account_data.get("success"):
                continue
                
            account_info = account_data.get("account_info")
            if not account_info:
                continue
            
            equity = account_info.get("equity", 0)
            balance = account_info.get("balance", 0)
            profit = account_info.get("profit", 0)
            positions_count = account_data.get("positions", {}).get("count", 0)
            fund_code = account_data.get("fund_code", "")
            
            summary["total_equity"] += equity
            summary["total_balance"] += balance
            summary["total_profit"] += profit
            summary["total_positions"] += positions_count
            
            # By fund breakdown
            if fund_code in summary["by_fund"]:
                summary["by_fund"][fund_code]["equity"] += equity
                summary["by_fund"][fund_code]["profit"] += profit
                summary["by_fund"][fund_code]["accounts"] += 1
        
        # Calculate overall return
        if summary["total_allocated"] > 0:
            summary["overall_return_pct"] = (summary["total_profit"] / summary["total_allocated"]) * 100
        
        return summary
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        if not self.last_update_time or not self.account_data_cache:
            return False
        
        time_diff = datetime.now(timezone.utc) - self.last_update_time
        return time_diff.total_seconds() < (self.cache_duration_minutes * 60)
    
    def _get_cached_summary(self) -> Dict[str, Any]:
        """Get cached data with updated timestamp"""
        cached_data = self.account_data_cache.copy()
        cached_data["data_source"] = "cache"
        cached_data["cached_at"] = self.last_update_time.isoformat()
        return cached_data
    
    async def initialize_database(self):
        """Initialize MongoDB connection for storing live data"""
        try:
            mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
            db_name = os.environ.get('DB_NAME', 'fidus_production')
            client = AsyncIOMotorClient(mongo_url)
            self.db = client[db_name]
            self.logger.info("✅ MultiAccountMT5Service: MongoDB connected")
        except Exception as e:
            self.logger.error(f"❌ MongoDB connection failed: {e}")
    
    async def store_live_data_in_mongodb(self, account_data_list: List[Dict]) -> bool:
        """Store collected live MT5 data in MongoDB"""
        try:
            if not self.db:
                await self.initialize_database()
            
            for account_data in account_data_list:
                if not account_data.get("success"):
                    continue
                
                login = account_data.get("login")
                account_info = account_data.get("account_info", {})
                performance = account_data.get("performance", {})
                
                if not account_info:
                    continue
                
                # Update MT5 account record with live data
                update_data = {
                    "current_equity": account_info.get("equity", 0),
                    "current_balance": account_info.get("balance", 0),
                    "profit_loss": account_info.get("profit", 0),
                    "profit_loss_percentage": performance.get("return_percentage", 0),
                    "margin_used": account_info.get("margin", 0),
                    "margin_free": account_info.get("margin_free", 0),
                    "margin_level": account_info.get("margin_level", 0),
                    
                    # Meta data
                    "mt5_data_source": "live_multi_account",
                    "last_mt5_update": datetime.now(timezone.utc),
                    "mt5_status": "connected",
                    
                    # Store raw data for analysis
                    "mt5_live_data": {
                        "account_info": account_info,
                        "positions": account_data.get("positions", {}),
                        "recent_history": account_data.get("recent_history", {}),
                        "collected_at": account_data.get("collected_at")
                    }
                }
                
                result = await self.db.mt5_accounts.update_one(
                    {"mt5_login": login, "client_id": "client_alejandro"},
                    {"$set": update_data}
                )
                
                if result.modified_count > 0:
                    self.logger.info(f"✅ Stored live data for MT5 account {login}")
                else:
                    self.logger.warning(f"⚠️ No record updated for MT5 login {login}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to store live data in MongoDB: {e}")
            return False
    
    def cleanup(self):
        """Cleanup MT5 connection"""
        if MT5_AVAILABLE and self.mt5_initialized:
            try:
                mt5.shutdown()
                self.mt5_initialized = False
                self.current_login = None
                self.logger.info("🔌 MT5 connection closed")
            except Exception as e:
                self.logger.error(f"❌ MT5 cleanup error: {e}")

# Global service instance
multi_account_mt5_service = MultiAccountMT5Service()

# Testing function
async def test_multi_account_collection():
    """Test the multi-account MT5 data collection"""
    print("🚀 TESTING MULTI-ACCOUNT MT5 DATA COLLECTION")
    print("=" * 60)
    
    service = MultiAccountMT5Service()
    
    try:
        # Test data collection
        results = await service.collect_all_alejandro_data(force_refresh=True)
        
        print(f"📊 Collection Results:")
        print(f"   Accounts collected: {results['accounts_collected']}/4")
        print(f"   Accounts failed: {results['accounts_failed']}/4")
        
        if results["summary"]:
            summary = results["summary"]
            print(f"   Total Equity: ${summary['total_equity']:,.2f}")
            print(f"   Total Profit: ${summary['total_profit']:,.2f}")
            print(f"   Overall Return: {summary['overall_return_pct']:.2f}%")
            print(f"   Open Positions: {summary['total_positions']}")
        
        # Test caching
        print(f"\n🔄 Testing cache...")
        cached_results = await service.collect_all_alejandro_data(force_refresh=False)
        print(f"   Cache working: {cached_results.get('data_source') == 'cache'}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        service.cleanup()

if __name__ == "__main__":
    asyncio.run(test_multi_account_collection())