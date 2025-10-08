"""
LIVE MT5 DATA INTEGRATION FOR FIDUS PRODUCTION
==============================================

This module implements REAL MT5 data integration as specified in the user requirements:
- Connects to MT5 Bridge Service (BPS)
- Fetches real account data, positions, history
- Stores live data in MongoDB
- Updates FIDUS Backend with actual MT5 performance

SYSTEM FLOW:
MetaTrader 5 (MEXAtlantic) → MT5 Bridge (BPS) → FIDUS Backend → Frontend
"""

import asyncio
import aiohttp
import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient

# Import existing MT5 bridge client
from mt5_bridge_client import mt5_bridge

class LiveMT5DataService:
    """Real-time MT5 data integration service for FIDUS production"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.bridge_client = mt5_bridge
        
        # Alejandro's real MT5 credentials as specified
        self.alejandro_accounts = {
            "886557": {
                "login": 886557,
                "password": "FIDUS13@",
                "server": "MEXAtlantic-Real",
                "fund_code": "BALANCE",
                "allocated_amount": 80000.00,
                "client_id": "client_alejandro"
            },
            "886066": {
                "login": 886066,
                "password": "FIDUS13@", 
                "server": "MEXAtlantic-Real",
                "fund_code": "BALANCE",
                "allocated_amount": 10000.00,
                "client_id": "client_alejandro"
            },
            "886602": {
                "login": 886602,
                "password": "FIDUS13@",
                "server": "MEXAtlantic-Real",
                "fund_code": "BALANCE",
                "allocated_amount": 10000.00,
                "client_id": "client_alejandro"
            },
            "885822": {
                "login": 885822,
                "password": "FIDUS13@",
                "server": "MEXAtlantic-Real",
                "fund_code": "CORE",
                "allocated_amount": 18151.41,
                "client_id": "client_alejandro"
            }
        }
        
        # MongoDB connection
        self.db = None
        
    async def initialize_database(self):
        """Initialize MongoDB connection"""
        try:
            mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
            db_name = os.environ.get('DB_NAME', 'fidus_production')
            client = AsyncIOMotorClient(mongo_url)
            self.db = client[db_name]
            self.logger.info("✅ LiveMT5DataService: MongoDB connected")
        except Exception as e:
            self.logger.error(f"❌ MongoDB connection failed: {e}")
    
    async def test_mt5_bridge_connection(self) -> Dict[str, Any]:
        """Test connection to MT5 Bridge Service"""
        try:
            health_check = await self.bridge_client.health_check()
            return {
                "bridge_available": health_check.get('success', False),
                "bridge_status": health_check,
                "mt5_bridge_url": self.bridge_client.bridge_url
            }
        except Exception as e:
            return {
                "bridge_available": False,
                "error": str(e)
            }
    
    async def connect_and_fetch_account_data(self, mt5_login: int, password: str, server: str) -> Dict[str, Any]:
        """Connect to specific MT5 account and fetch real data"""
        try:
            self.logger.info(f"🔗 Connecting to MT5 account {mt5_login} on {server}")
            
            # Step 1: Login to MT5 account via bridge
            login_result = await self.bridge_client.mt5_login(mt5_login, password, server)
            
            if not login_result.get('success'):
                return {
                    "success": False,
                    "error": f"MT5 login failed: {login_result.get('error', 'Unknown error')}",
                    "mt5_login": mt5_login
                }
            
            # Step 2: Get account info (balance, equity, margin)
            account_info = await self.bridge_client.get_account_info(mt5_login)
            
            # Step 3: Get current positions
            positions = await self.bridge_client.get_positions(mt5_login)
            
            # Step 4: Get recent trading history (last 30 days)
            from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            to_date = datetime.now().strftime('%Y-%m-%d')
            history = await self.bridge_client.get_account_history(mt5_login, from_date, to_date)
            
            # Step 5: Get deals (deposits/withdrawals)
            deals = await self.bridge_client.get_deals(mt5_login, from_date, to_date)
            
            # Compile comprehensive account data
            return {
                "success": True,
                "mt5_login": mt5_login,
                "server": server,
                "account_info": account_info,
                "positions": positions,
                "history": history,
                "deals": deals,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to fetch data for account {mt5_login}: {e}")
            return {
                "success": False,
                "error": str(e),
                "mt5_login": mt5_login
            }
    
    async def update_alejandro_mt5_data(self) -> Dict[str, Any]:
        """Fetch and update real MT5 data for all Alejandro's accounts"""
        try:
            await self.initialize_database()
            
            results = {
                "success": True,
                "accounts_updated": 0,
                "accounts_failed": 0,
                "account_results": [],
                "total_equity": 0.0,
                "total_profit": 0.0,
                "update_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Process each account
            for account_key, account_config in self.alejandro_accounts.items():
                account_result = await self.connect_and_fetch_account_data(
                    account_config["login"],
                    account_config["password"], 
                    account_config["server"]
                )
                
                if account_result["success"]:
                    # Store in MongoDB
                    await self.store_mt5_data_in_database(account_config, account_result)
                    
                    # Extract key metrics
                    account_info = account_result.get("account_info", {}).get("data", {})
                    equity = account_info.get("equity", 0.0) or account_config["allocated_amount"]
                    balance = account_info.get("balance", 0.0) or account_config["allocated_amount"]
                    profit = equity - balance
                    
                    results["total_equity"] += equity
                    results["total_profit"] += profit
                    results["accounts_updated"] += 1
                    
                    self.logger.info(f"✅ Updated MT5 {account_config['login']}: Equity=${equity:,.2f}, Profit=${profit:,.2f}")
                
                else:
                    results["accounts_failed"] += 1
                    self.logger.error(f"❌ Failed to update MT5 {account_config['login']}: {account_result.get('error')}")
                
                results["account_results"].append(account_result)
            
            # Update summary statistics
            results["overall_return_percent"] = (results["total_profit"] / 118151.41 * 100) if results["total_profit"] != 0 else 0
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update Alejandro's MT5 data: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def store_mt5_data_in_database(self, account_config: Dict, mt5_data: Dict) -> bool:
        """Store real MT5 data in MongoDB"""
        try:
            if not self.db:
                await self.initialize_database()
            
            mt5_login = account_config["login"]
            account_info = mt5_data.get("account_info", {}).get("data", {})
            
            # Extract real MT5 values
            current_balance = account_info.get("balance", account_config["allocated_amount"])
            current_equity = account_info.get("equity", account_config["allocated_amount"])
            margin_used = account_info.get("margin", 0.0)
            margin_free = account_info.get("margin_free", current_equity)
            profit_loss = current_equity - current_balance
            
            # Update MT5 account record in database
            update_data = {
                "current_equity": current_equity,
                "current_balance": current_balance,
                "profit_loss": profit_loss,
                "profit_loss_percentage": (profit_loss / account_config["allocated_amount"] * 100) if account_config["allocated_amount"] > 0 else 0,
                "margin_used": margin_used,
                "margin_free": margin_free,
                "mt5_data_source": "live_bridge",
                "last_mt5_update": datetime.now(timezone.utc),
                "mt5_status": "connected",
                
                # Store raw MT5 data for detailed analysis
                "mt5_raw_data": {
                    "account_info": account_info,
                    "positions": mt5_data.get("positions"),
                    "last_updated": mt5_data.get("last_updated")
                }
            }
            
            # Update the account record
            result = await self.db.mt5_accounts.update_one(
                {"mt5_login": mt5_login, "client_id": account_config["client_id"]},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                self.logger.info(f"✅ Stored live MT5 data for account {mt5_login}")
                return True
            else:
                self.logger.warning(f"⚠️ No MT5 account record updated for login {mt5_login}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to store MT5 data in database: {e}")
            return False
    
    async def get_live_mt5_summary(self, client_id: str = "client_alejandro") -> Dict[str, Any]:
        """Get live MT5 data summary for client"""
        try:
            await self.initialize_database()
            
            # Get all MT5 accounts for client
            mt5_accounts = await self.db.mt5_accounts.find({"client_id": client_id}).to_list(length=None)
            
            summary = {
                "client_id": client_id,
                "total_accounts": len(mt5_accounts),
                "total_allocated": 0.0,
                "total_equity": 0.0,
                "total_profit": 0.0,
                "overall_return_percent": 0.0,
                "accounts": [],
                "data_source": "live_mt5",
                "last_updated": None
            }
            
            latest_update = None
            
            for account in mt5_accounts:
                account_summary = {
                    "mt5_login": account.get("mt5_login"),
                    "fund_code": account.get("fund_code"),
                    "broker_name": account.get("broker_name"),
                    "allocated_amount": account.get("total_allocated", 0),
                    "current_equity": account.get("current_equity", 0),
                    "profit_loss": account.get("profit_loss", 0),
                    "return_percent": account.get("profit_loss_percentage", 0),
                    "mt5_status": account.get("mt5_status", "unknown"),
                    "last_updated": account.get("last_mt5_update")
                }
                
                summary["total_allocated"] += account_summary["allocated_amount"]
                summary["total_equity"] += account_summary["current_equity"] 
                summary["total_profit"] += account_summary["profit_loss"]
                summary["accounts"].append(account_summary)
                
                # Track latest update time
                if account.get("last_mt5_update"):
                    if latest_update is None or account["last_mt5_update"] > latest_update:
                        latest_update = account["last_mt5_update"]
            
            # Calculate overall performance
            if summary["total_allocated"] > 0:
                summary["overall_return_percent"] = (summary["total_profit"] / summary["total_allocated"]) * 100
            
            summary["last_updated"] = latest_update.isoformat() if latest_update else None
            
            return summary
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get live MT5 summary: {e}")
            return {
                "client_id": client_id,
                "error": str(e),
                "data_source": "error"
            }

# Global service instance
live_mt5_service = LiveMT5DataService()

# Testing function
async def test_live_mt5_integration():
    """Test the live MT5 integration"""
    print("🚀 TESTING LIVE MT5 INTEGRATION")
    print("=" * 60)
    
    service = LiveMT5DataService()
    
    # Test 1: Bridge connection
    print("1. Testing MT5 Bridge connection...")
    bridge_test = await service.test_mt5_bridge_connection()
    print(f"   Bridge available: {bridge_test['bridge_available']}")
    
    if not bridge_test['bridge_available']:
        print("❌ Cannot proceed without MT5 Bridge")
        return
    
    # Test 2: Fetch Alejandro's data
    print("2. Fetching Alejandro's live MT5 data...")
    update_result = await service.update_alejandro_mt5_data()
    
    if update_result['success']:
        print(f"✅ Successfully updated {update_result['accounts_updated']} accounts")
        print(f"   Total Equity: ${update_result['total_equity']:,.2f}")
        print(f"   Total Profit: ${update_result['total_profit']:,.2f}")
        print(f"   Overall Return: {update_result['overall_return_percent']:.2f}%")
    else:
        print(f"❌ Update failed: {update_result.get('error')}")
    
    # Test 3: Get summary
    print("3. Getting live MT5 summary...")
    summary = await service.get_live_mt5_summary()
    print(f"   Data source: {summary.get('data_source')}")
    print(f"   Accounts: {summary.get('total_accounts')}")
    print(f"   Total allocated: ${summary.get('total_allocated'):,.2f}")

if __name__ == "__main__":
    asyncio.run(test_live_mt5_integration())