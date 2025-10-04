"""
MT5 Service for FIDUS Investment Management Platform
Handles MT5 account management and real-time data synchronization
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal

from mt5_bridge_client import mt5_bridge
from repositories.mt5_repository import MT5Repository, MT5PositionRepository, MT5OrderRepository, MT5DealRepository
from repositories.user_repository import UserRepository
from models.mt5_account import MT5Account, MT5AccountCreate, BrokerCode, MT5AccountStatus
from config.database import connection_manager

logger = logging.getLogger(__name__)

class MT5Service:
    """Service for MT5 operations and data synchronization"""
    
    def __init__(self):
        self.mt5_repo = None
        self.position_repo = None
        self.order_repo = None
        self.deal_repo = None
        self.user_repo = None
        self.sync_running = False
        self.sync_interval = 300  # 5 minutes
        
    async def initialize(self):
        """Initialize repositories"""
        db = await connection_manager.get_database()
        self.mt5_repo = MT5Repository(db)
        self.position_repo = MT5PositionRepository(db)
        self.order_repo = MT5OrderRepository(db)
        self.deal_repo = MT5DealRepository(db)
        self.user_repo = UserRepository(db)
        
        logger.info("MT5 Service initialized")
    
    async def create_mt5_account(
        self, 
        client_id: str, 
        mt5_login: int, 
        password: str, 
        server: str, 
        broker_code: BrokerCode,
        fund_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create and link MT5 account to client"""
        try:
            # Verify client exists
            client = await self.user_repo.find_by_id(client_id)
            if not client:
                return {"success": False, "error": "Client not found"}
            
            # Check if MT5 account already exists
            existing = await self.mt5_repo.find_by_mt5_login(mt5_login)
            if existing:
                return {"success": False, "error": "MT5 account already registered"}
            
            # Test MT5 connection via bridge
            login_result = await self.test_mt5_connection(mt5_login, password, server)
            if not login_result.get("success"):
                return {"success": False, "error": f"MT5 connection failed: {login_result.get('error')}"}
            
            # Create account record
            from cryptography.fernet import Fernet
            import os
            
            # Encrypt password (you should have encryption key in environment)
            encryption_key = os.environ.get('MT5_ENCRYPTION_KEY')
            if not encryption_key:
                # Generate key for demo - in production, use proper key management
                encryption_key = Fernet.generate_key().decode()
                logger.warning("Generated temporary encryption key - use proper key management in production")
            
            fernet = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
            encrypted_password = fernet.encrypt(password.encode()).decode()
            
            account_data = MT5AccountCreate(
                account_id=f"mt5_{mt5_login}_{client_id[:8]}",
                client_id=client_id,
                mt5_login=mt5_login,
                broker_code=broker_code,
                broker_name=self._get_broker_name(broker_code),
                mt5_server=server,
                fund_code=fund_code,
                encrypted_password=encrypted_password,
                is_demo=self._is_demo_server(server)
            )
            
            mt5_account = await self.mt5_repo.create_mt5_account(account_data)
            
            if mt5_account:
                # Perform initial sync
                await self.sync_account_data(mt5_account.account_id)
                
                logger.info(f"Created MT5 account {mt5_login} for client {client_id}")
                return {
                    "success": True,
                    "account_id": mt5_account.account_id,
                    "mt5_login": mt5_login,
                    "broker": broker_code,
                    "server": server
                }
            else:
                return {"success": False, "error": "Failed to create account record"}
                
        except Exception as e:
            logger.error(f"Error creating MT5 account: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_mt5_connection(self, mt5_login: int, password: str, server: str) -> Dict[str, Any]:
        """Test MT5 connection via bridge"""
        try:
            # First check if bridge is healthy
            health = await mt5_bridge.health_check()
            if not health.get("success", False):
                return {"success": False, "error": "MT5 Bridge service not available"}
            
            # Test login
            login_result = await mt5_bridge.mt5_login(mt5_login, password, server)
            
            if login_result.get("success"):
                # Get account info to verify
                account_info = await mt5_bridge.get_account_info(mt5_login)
                return {
                    "success": True,
                    "account_info": account_info,
                    "bridge_healthy": True
                }
            else:
                return {
                    "success": False,
                    "error": login_result.get("error", "Login failed"),
                    "bridge_healthy": True
                }
                
        except Exception as e:
            logger.error(f"Error testing MT5 connection: {e}")
            return {"success": False, "error": str(e), "bridge_healthy": False}
    
    async def sync_account_data(self, account_id: str) -> Dict[str, Any]:
        """Synchronize MT5 account data"""
        try:
            account = await self.mt5_repo.find_by_id(account_id)
            if not account:
                return {"success": False, "error": "Account not found"}
            
            if not account.is_active:
                return {"success": False, "error": "Account not active"}
            
            # Decrypt password for bridge connection
            from cryptography.fernet import Fernet
            import os
            
            encryption_key = os.environ.get('MT5_ENCRYPTION_KEY')
            if not encryption_key:
                return {"success": False, "error": "Encryption key not configured"}
            
            fernet = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
            password = fernet.decrypt(account.encrypted_password.encode()).decode()
            
            # Login to MT5 via bridge
            login_result = await mt5_bridge.mt5_login(account.mt5_login, password, account.mt5_server)
            if not login_result.get("success"):
                await self.mt5_repo.update_sync_status(account_id, "error", login_result.get("error"))
                return {"success": False, "error": f"Login failed: {login_result.get('error')}"}
            
            # Get account information
            account_info = await mt5_bridge.get_account_info(account.mt5_login)
            if account_info.get("error"):
                await self.mt5_repo.update_sync_status(account_id, "error", account_info.get("error"))
                return {"success": False, "error": account_info.get("error")}
            
            # Update account balance and equity
            balance = Decimal(str(account_info.get("balance", 0)))
            equity = Decimal(str(account_info.get("equity", 0)))
            profit = Decimal(str(account_info.get("profit", 0)))
            margin = Decimal(str(account_info.get("margin", 0))) if account_info.get("margin") else None
            free_margin = Decimal(str(account_info.get("free_margin", 0))) if account_info.get("free_margin") else None
            margin_level = Decimal(str(account_info.get("margin_level", 0))) if account_info.get("margin_level") else None
            
            await self.mt5_repo.update_account_balance(
                account_id, balance, equity, profit, margin, free_margin, margin_level
            )
            
            # Update account metadata if needed
            update_data = {}
            if account.currency != account_info.get("currency"):
                update_data["currency"] = account_info.get("currency")
            if account.leverage != account_info.get("leverage"):
                update_data["leverage"] = account_info.get("leverage")
            if account.trade_allowed != account_info.get("trade_allowed"):
                update_data["trade_allowed"] = account_info.get("trade_allowed")
            
            if update_data:
                await self.mt5_repo.update_by_id(account_id, update_data)
            
            # Sync positions (optional - can be done separately for performance)
            # positions_result = await self._sync_positions(account)
            
            logger.info(f"Synced account {account_id}: Balance ${balance}, Equity ${equity}")
            
            return {
                "success": True,
                "account_id": account_id,
                "balance": float(balance),
                "equity": float(equity),
                "profit": float(profit),
                "sync_time": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error syncing account {account_id}: {e}")
            await self.mt5_repo.update_sync_status(account_id, "error", str(e))
            return {"success": False, "error": str(e)}
    
    async def sync_all_accounts(self) -> Dict[str, Any]:
        """Synchronize all active MT5 accounts"""
        try:
            accounts = await self.mt5_repo.find_active_accounts()
            results = {
                "total_accounts": len(accounts),
                "success_count": 0,
                "error_count": 0,
                "errors": []
            }
            
            for account in accounts:
                try:
                    sync_result = await self.sync_account_data(account.account_id)
                    if sync_result.get("success"):
                        results["success_count"] += 1
                    else:
                        results["error_count"] += 1
                        results["errors"].append({
                            "account_id": account.account_id,
                            "error": sync_result.get("error")
                        })
                except Exception as e:
                    results["error_count"] += 1
                    results["errors"].append({
                        "account_id": account.account_id,
                        "error": str(e)
                    })
            
            logger.info(f"Sync completed: {results['success_count']} success, {results['error_count']} errors")
            return results
            
        except Exception as e:
            logger.error(f"Error in sync_all_accounts: {e}")
            return {"success": False, "error": str(e)}
    
    async def start_background_sync(self):
        """Start background synchronization task"""
        if self.sync_running:
            logger.warning("Background sync already running")
            return
        
        self.sync_running = True
        logger.info("Starting MT5 background synchronization")
        
        while self.sync_running:
            try:
                # Check if MT5 bridge is healthy
                health = await mt5_bridge.health_check()
                
                if health.get("success") and health.get("mt5_connected"):
                    await self.sync_all_accounts()
                else:
                    logger.warning(f"MT5 Bridge not healthy, skipping sync: {health}")
                
            except Exception as e:
                logger.error(f"Error in background sync: {e}")
            
            # Wait for next sync interval
            await asyncio.sleep(self.sync_interval)
    
    def stop_background_sync(self):
        """Stop background synchronization"""
        self.sync_running = False
        logger.info("Stopped MT5 background synchronization")
    
    async def get_client_mt5_accounts(self, client_id: str) -> List[Dict[str, Any]]:
        """Get all MT5 accounts for a client with current data"""
        try:
            accounts = await self.mt5_repo.find_by_client_id(client_id)
            
            result = []
            for account in accounts:
                account_data = {
                    "account_id": account.account_id,
                    "mt5_login": account.mt5_login,
                    "broker_code": account.broker_code,
                    "broker_name": account.broker_name,
                    "server": account.mt5_server,
                    "fund_code": account.fund_code,
                    "is_active": account.is_active,
                    "is_demo": account.is_demo,
                    "status": account.status,
                    "balance": float(account.balance) if account.balance else 0,
                    "equity": float(account.equity) if account.equity else 0,
                    "profit": float(account.profit) if account.profit else 0,
                    "currency": account.currency,
                    "leverage": account.leverage,
                    "total_allocated": float(account.total_allocated),
                    "investment_count": len(account.investment_ids),
                    "last_sync": account.last_sync.isoformat() if account.last_sync else None,
                    "sync_status": account.sync_status
                }
                result.append(account_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting client MT5 accounts: {e}")
            raise
    
    def _get_broker_name(self, broker_code: BrokerCode) -> str:
        """Get human-readable broker name"""
        broker_names = {
            BrokerCode.MULTIBANK: "Multibank",
            BrokerCode.DOOTECHNOLOGY: "DooTechnology",
            BrokerCode.VTMARKETS: "VT Markets",
            BrokerCode.CUSTOM: "Custom Broker"
        }
        return broker_names.get(broker_code, "Unknown Broker")
    
    def _is_demo_server(self, server: str) -> bool:
        """Determine if server is demo based on server name"""
        demo_keywords = ["demo", "test", "trial", "practice"]
        return any(keyword in server.lower() for keyword in demo_keywords)

# Global MT5 service instance
mt5_service = MT5Service()