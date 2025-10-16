"""
MT5 Bridge Service - Full Feature Enhancement (Phase 4B)
Syncs MT5 account data + deal history + equity snapshots + pending orders + terminal status

DEPLOYMENT LOCATION: C:\mt5_bridge_service\mt5_bridge_service_production.py
Python Version: 3.12
Pymongo Version: 4.x compatible

PHASE 4B ENHANCEMENTS:
- Equity snapshots (hourly/daily) for trend analysis
- Pending orders tracking
- Terminal status monitoring
- Comprehensive error logging
- All Phase 4A features included
"""

import MetaTrader5 as mt5
from pymongo import MongoClient, UpdateOne, ASCENDING, DESCENDING
from datetime import datetime, timezone, timedelta
import time
import os
from dotenv import load_dotenv
import sys
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:\\mt5_bridge_service\\mt5_bridge_enhanced.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    logger.error("[ERROR] MONGODB_URI not found in .env file")
    sys.exit(1)

# MT5 Configuration
MT5_PATH = os.getenv('MT5_PATH', 'C:\\Program Files\\MEX Atlantic MT5 Terminal\\terminal64.exe')
UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', '300'))  # 5 minutes (account sync)
DEAL_SYNC_INTERVAL = int(os.getenv('DEAL_SYNC_INTERVAL', '86400'))  # 24 hours (daily)
EQUITY_SNAPSHOT_INTERVAL = int(os.getenv('EQUITY_SNAPSHOT_INTERVAL', '3600'))  # 1 hour
INITIAL_BACKFILL_DAYS = int(os.getenv('INITIAL_BACKFILL_DAYS', '90'))  # 90 days

# Fallback accounts (if MongoDB query fails)
FALLBACK_ACCOUNTS = [
    {"account": 886557, "password": "Fidus13@", "name": "Main Balance Account", "fund_type": "BALANCE", "target_amount": 100000.0},
    {"account": 886066, "password": "Fidus13@", "name": "Secondary Balance Account", "fund_type": "BALANCE", "target_amount": 210000.0},
    {"account": 886602, "password": "Fidus13@", "name": "Tertiary Balance Account", "fund_type": "BALANCE", "target_amount": 50000.0},
    {"account": 885822, "password": "Fidus13@", "name": "Core Account", "fund_type": "CORE", "target_amount": 128151.41},
    {"account": 886528, "password": "Fidus13@", "name": "Separation Account", "fund_type": "SEPARATION", "target_amount": 10000.0},
    {"account": 891215, "password": "Fidus13@", "name": "Interest Earnings Trading", "fund_type": "SEPARATION", "target_amount": 10000.0},
    {"account": 891234, "password": "Fidus13@", "name": "CORE Fund", "fund_type": "CORE", "target_amount": 10000.0}
]

class MT5BridgeEnhanced:
    def __init__(self):
        self.db = None
        self.mt5_accounts = []
        self.last_deal_sync = None
        self.last_equity_snapshot = None
        self.terminal_initialized = False
        self.error_count = 0
        self.last_error_log_time = None
        
    def connect_mongodb(self):
        """Connect to MongoDB with pymongo 4.x compatibility"""
        try:
            logger.info("[CONNECT] Connecting to MongoDB...")
            client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            
            # Test connection
            client.admin.command('ping')
            
            # Get database
            self.db = client.get_database()
            
            # Verify connection
            try:
                list(self.db.list_collection_names())
                logger.info("[OK] MongoDB connected successfully")
                self.ensure_indexes()
                return True
            except Exception as e:
                logger.error(f"[ERROR] MongoDB connection test failed: {e}")
                return False
                
        except Exception as e:
            logger.error(f"[ERROR] MongoDB connection error: {e}")
            self.log_error("mongodb_connection", str(e))
            self.db = None
            return False
    
    def ensure_indexes(self):
        """Create indexes for all collections"""
        try:
            if self.db is None:
                return
            
            # Deal history indexes
            deals_coll = self.db.mt5_deals_history
            deals_coll.create_index([("account_number", ASCENDING)])
            deals_coll.create_index([("time", DESCENDING)])
            deals_coll.create_index([("type", ASCENDING)])
            deals_coll.create_index([("symbol", ASCENDING)])
            deals_coll.create_index([("account_number", ASCENDING), ("time", DESCENDING)])
            deals_coll.create_index([("ticket", ASCENDING)], unique=True)
            
            # Equity snapshots indexes
            equity_coll = self.db.mt5_equity_snapshots
            equity_coll.create_index([("account_number", ASCENDING)])
            equity_coll.create_index([("timestamp", DESCENDING)])
            equity_coll.create_index([("account_number", ASCENDING), ("timestamp", DESCENDING)])
            
            # Pending orders indexes
            orders_coll = self.db.mt5_pending_orders
            orders_coll.create_index([("account_number", ASCENDING)])
            orders_coll.create_index([("ticket", ASCENDING)])
            orders_coll.create_index([("time_setup", DESCENDING)])
            
            # Terminal status index
            status_coll = self.db.mt5_terminal_status
            status_coll.create_index([("timestamp", DESCENDING)])
            
            # Error logs index
            errors_coll = self.db.mt5_error_logs
            errors_coll.create_index([("timestamp", DESCENDING)])
            errors_coll.create_index([("error_type", ASCENDING)])
            
            logger.info("[OK] All indexes created/verified")
            
        except Exception as e:
            logger.warning(f"[WARNING] Error creating indexes: {e}")
    
    def log_error(self, error_type, error_message, account_number=None, details=None):
        """Log error to MongoDB for monitoring"""
        try:
            if self.db is None:
                return
            
            error_doc = {
                "timestamp": datetime.now(timezone.utc),
                "error_type": error_type,
                "error_message": error_message,
                "account_number": account_number,
                "details": details or {},
                "traceback": traceback.format_exc() if sys.exc_info()[0] is not None else None
            }
            
            self.db.mt5_error_logs.insert_one(error_doc)
            self.error_count += 1
            self.last_error_log_time = datetime.now(timezone.utc)
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to log error to MongoDB: {e}")
    
    def log_terminal_status(self):
        """Log terminal connection status"""
        try:
            if self.db is None:
                return
            
            # Get terminal info
            terminal_info = mt5.terminal_info()
            
            if terminal_info:
                status_doc = {
                    "timestamp": datetime.now(timezone.utc),
                    "connected": terminal_info.connected,
                    "trade_allowed": terminal_info.trade_allowed,
                    "email_enabled": terminal_info.email_enabled,
                    "ftp_enabled": terminal_info.ftp_enabled,
                    "notifications_enabled": terminal_info.notifications_enabled,
                    "mqid": terminal_info.mqid,
                    "build": terminal_info.build,
                    "maxbars": terminal_info.maxbars,
                    "ping_last": terminal_info.ping_last,
                    "community_account": terminal_info.community_account,
                    "community_connection": terminal_info.community_connection,
                    "terminal_initialized": self.terminal_initialized,
                    "active_accounts": len(self.mt5_accounts),
                    "total_errors_today": self.error_count,
                    "last_error_time": self.last_error_log_time
                }
                
                self.db.mt5_terminal_status.insert_one(status_doc)
                logger.info("[OK] Terminal status logged")
            else:
                logger.warning("[WARNING] Unable to retrieve terminal info")
                
        except Exception as e:
            logger.error(f"[ERROR] Error logging terminal status: {e}")
    
    def load_mt5_accounts_from_mongodb(self):
        """Load MT5 accounts from mt5_account_config collection"""
        try:
            if self.db is None:
                logger.warning("[WARNING] MongoDB not connected, using fallback accounts")
                self.mt5_accounts = FALLBACK_ACCOUNTS
                return
            
            logger.info("[LOAD] Loading MT5 accounts from mt5_account_config collection...")
            
            cursor = self.db.mt5_account_config.find(
                {"is_active": True},
                {"account": 1, "password": 1, "name": 1, "fund_type": 1, "target_amount": 1, "_id": 0}
            )
            
            accounts = list(cursor)
            
            if len(accounts) > 0:
                self.mt5_accounts = accounts
                logger.info(f"[OK] Loaded {len(accounts)} active accounts from MongoDB")
            else:
                logger.warning("[WARNING] No active accounts found, using fallback")
                self.mt5_accounts = FALLBACK_ACCOUNTS
                
        except Exception as e:
            logger.error(f"[ERROR] Error loading accounts from MongoDB: {e}")
            self.log_error("load_accounts", str(e))
            self.mt5_accounts = FALLBACK_ACCOUNTS
    
    def initialize_mt5(self):
        """Initialize MT5 terminal"""
        try:
            if not mt5.initialize(path=MT5_PATH):
                error = mt5.last_error()
                logger.error(f"[ERROR] MT5 initialize() failed, error code: {error}")
                self.log_error("mt5_initialization", f"Error code: {error}")
                self.terminal_initialized = False
                return False
            
            version = mt5.version()
            logger.info(f"[OK] MT5 Terminal initialized: v{version}")
            self.terminal_initialized = True
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] MT5 initialization error: {e}")
            self.log_error("mt5_initialization", str(e))
            self.terminal_initialized = False
            return False
    
    def collect_equity_snapshot(self, account_config):
        """Collect current equity snapshot for an account"""
        account_number = account_config["account"]
        password = account_config["password"]
        server = "MEXAtlantic-Real"
        
        try:
            # Login to MT5 account
            authorized = mt5.login(account_number, password=password, server=server)
            
            if not authorized:
                error = mt5.last_error()
                logger.error(f"[ERROR] Login failed for equity snapshot {account_number}: {error}")
                self.log_error("equity_snapshot_login", f"Error: {error}", account_number)
                return None
            
            # Get account info
            account_info = mt5.account_info()
            if account_info is None:
                logger.error(f"[ERROR] Failed to get account info for equity snapshot {account_number}")
                return None
            
            # Create snapshot
            snapshot = {
                "account_number": account_number,
                "account_name": account_config["name"],
                "fund_type": account_config["fund_type"],
                "timestamp": datetime.now(timezone.utc),
                "balance": account_info.balance,
                "equity": account_info.equity,
                "profit": account_info.profit,
                "margin": account_info.margin,
                "free_margin": account_info.margin_free,
                "margin_level": account_info.margin_level if account_info.margin_level else 0,
                "leverage": account_info.leverage,
                "credit": account_info.credit
            }
            
            return snapshot
            
        except Exception as e:
            logger.error(f"[ERROR] Error collecting equity snapshot for {account_number}: {e}")
            self.log_error("equity_snapshot", str(e), account_number)
            return None
    
    def collect_pending_orders(self, account_config):
        """Collect pending orders for an account"""
        account_number = account_config["account"]
        password = account_config["password"]
        server = "MEXAtlantic-Real"
        
        try:
            # Login to MT5 account
            authorized = mt5.login(account_number, password=password, server=server)
            
            if not authorized:
                error = mt5.last_error()
                logger.error(f"[ERROR] Login failed for pending orders {account_number}: {error}")
                self.log_error("pending_orders_login", f"Error: {error}", account_number)
                return []
            
            # Get pending orders
            orders = mt5.orders_get()
            
            if orders is None:
                return []
            
            if len(orders) == 0:
                return []
            
            # Convert to dict format
            order_list = []
            for order in orders:
                order_dict = {
                    "ticket": order.ticket,
                    "account_number": account_number,
                    "account_name": account_config["name"],
                    "fund_type": account_config["fund_type"],
                    "time_setup": datetime.fromtimestamp(order.time_setup, tz=timezone.utc),
                    "time_expiration": datetime.fromtimestamp(order.time_expiration, tz=timezone.utc) if order.time_expiration > 0 else None,
                    "type": order.type,
                    "type_name": self.get_order_type_name(order.type),
                    "state": order.state,
                    "state_name": self.get_order_state_name(order.state),
                    "symbol": order.symbol,
                    "volume_initial": order.volume_initial,
                    "volume_current": order.volume_current,
                    "price_open": order.price_open,
                    "sl": order.sl,
                    "tp": order.tp,
                    "price_current": order.price_current,
                    "price_stoplimit": order.price_stoplimit,
                    "magic": order.magic,
                    "comment": order.comment,
                    "external_id": order.external_id,
                    "synced_at": datetime.now(timezone.utc)
                }
                order_list.append(order_dict)
            
            logger.info(f"[OK] Collected {len(order_list)} pending orders for {account_number}")
            return order_list
            
        except Exception as e:
            logger.error(f"[ERROR] Error collecting pending orders for {account_number}: {e}")
            self.log_error("pending_orders", str(e), account_number)
            return []
    
    def get_order_type_name(self, order_type):
        """Convert order type code to name"""
        types = {
            0: "BUY",
            1: "SELL",
            2: "BUY_LIMIT",
            3: "SELL_LIMIT",
            4: "BUY_STOP",
            5: "SELL_STOP",
            6: "BUY_STOP_LIMIT",
            7: "SELL_STOP_LIMIT",
            8: "CLOSE_BY"
        }
        return types.get(order_type, f"UNKNOWN_{order_type}")
    
    def get_order_state_name(self, state):
        """Convert order state code to name"""
        states = {
            0: "STARTED",
            1: "PLACED",
            2: "CANCELED",
            3: "PARTIAL",
            4: "FILLED",
            5: "REJECTED",
            6: "EXPIRED",
            7: "REQUEST_ADD",
            8: "REQUEST_MODIFY",
            9: "REQUEST_CANCEL"
        }
        return states.get(state, f"UNKNOWN_{state}")
    
    def check_if_backfill_needed(self, account_number):
        """Check if initial 90-day backfill is needed for this account"""
        try:
            if self.db is None:
                return True
            
            # Check if we have any deals for this account
            deal_count = self.db.mt5_deals_history.count_documents({"account_number": account_number})
            
            if deal_count == 0:
                logger.info(f"[BACKFILL] Account {account_number} needs initial backfill (no deals found)")
                return True
            
            # Check if we have recent deals (within last 7 days)
            recent_date = datetime.now(timezone.utc) - timedelta(days=7)
            recent_count = self.db.mt5_deals_history.count_documents({
                "account_number": account_number,
                "time": {"$gte": recent_date}
            })
            
            if recent_count == 0:
                logger.info(f"[BACKFILL] Account {account_number} needs backfill (no recent deals)")
                return True
            
            logger.info(f"[OK] Account {account_number} has {deal_count} deals, skipping backfill")
            return False
            
        except Exception as e:
            logger.error(f"[ERROR] Error checking backfill status: {e}")
            self.log_error("backfill_check", str(e), account_number)
            return True
    
    def collect_deals(self, account_config, start_date, end_date):
        """Collect deal history for an account within date range"""
        account_number = account_config["account"]
        password = account_config["password"]
        server = "MEXAtlantic-Real"
        
        try:
            # Login to MT5 account
            authorized = mt5.login(account_number, password=password, server=server)
            
            if not authorized:
                error = mt5.last_error()
                logger.error(f"[ERROR] Login failed for {account_number}: {error}")
                self.log_error("deal_collection_login", f"Error: {error}", account_number)
                return []
            
            # Get deal history
            deals = mt5.history_deals_get(start_date, end_date)
            
            if deals is None:
                logger.warning(f"[WARNING] No deals found for {account_number} ({start_date.date()} to {end_date.date()})")
                return []
            
            if len(deals) == 0:
                logger.info(f"[STATS] Account {account_number}: No deals in range")
                return []
            
            # Convert MT5 deals to dict format for MongoDB
            deal_list = []
            for deal in deals:
                # Get symbol info for spread calculation
                symbol_info = mt5.symbol_info(deal.symbol)
                spread = symbol_info.spread if symbol_info else 0
                
                deal_dict = {
                    "ticket": deal.ticket,
                    "order": deal.order,
                    "time": datetime.fromtimestamp(deal.time, tz=timezone.utc),
                    "type": deal.type,
                    "entry": deal.entry,
                    "symbol": deal.symbol,
                    "volume": deal.volume,
                    "price": deal.price,
                    "profit": deal.profit,
                    "commission": deal.commission,
                    "swap": deal.swap,
                    "position_id": deal.position_id,
                    "magic": deal.magic,
                    "comment": deal.comment,
                    "external_id": deal.external_id,
                    "account_number": account_number,
                    "account_name": account_config["name"],
                    "fund_type": account_config["fund_type"],
                    "spread": spread,  # NEW: Spread at execution time
                    "synced_at": datetime.now(timezone.utc)
                }
                deal_list.append(deal_dict)
            
            logger.info(f"[OK] Collected {len(deal_list)} deals for {account_number}")
            return deal_list
            
        except Exception as e:
            logger.error(f"[ERROR] Error collecting deals for {account_number}: {e}")
            self.log_error("deal_collection", str(e), account_number)
            return []
    
    def sync_deals_to_mongodb(self, deals):
        """Store deals in MongoDB using bulk upsert"""
        if self.db is None or len(deals) == 0:
            return 0
        
        try:
            operations = []
            for deal in deals:
                operations.append(
                    UpdateOne(
                        {"ticket": deal["ticket"]},
                        {"$set": deal},
                        upsert=True
                    )
                )
            
            result = self.db.mt5_deals_history.bulk_write(operations)
            
            inserted = result.upserted_count
            modified = result.modified_count
            
            logger.info(f"[SAVE] Stored {inserted} new deals, updated {modified} existing deals")
            return inserted + modified
            
        except Exception as e:
            logger.error(f"[ERROR] Error storing deals to MongoDB: {e}")
            self.log_error("deal_storage", str(e))
            return 0
    
    def sync_equity_snapshots_to_mongodb(self, snapshots):
        """Store equity snapshots in MongoDB"""
        if self.db is None or len(snapshots) == 0:
            return 0
        
        try:
            result = self.db.mt5_equity_snapshots.insert_many(snapshots)
            logger.info(f"[SAVE] Stored {len(result.inserted_ids)} equity snapshots")
            return len(result.inserted_ids)
            
        except Exception as e:
            logger.error(f"[ERROR] Error storing equity snapshots: {e}")
            self.log_error("equity_snapshot_storage", str(e))
            return 0
    
    def sync_pending_orders_to_mongodb(self, orders):
        """Replace pending orders in MongoDB (clear old, insert new)"""
        if self.db is None:
            return 0
        
        try:
            # Clear existing pending orders for these accounts
            account_numbers = list(set([order["account_number"] for order in orders]))
            if account_numbers:
                self.db.mt5_pending_orders.delete_many({"account_number": {"$in": account_numbers}})
            
            # Insert new orders
            if len(orders) > 0:
                result = self.db.mt5_pending_orders.insert_many(orders)
                logger.info(f"[SAVE] Stored {len(result.inserted_ids)} pending orders")
                return len(result.inserted_ids)
            else:
                logger.info("[STATS] No pending orders to store")
                return 0
            
        except Exception as e:
            logger.error(f"[ERROR] Error storing pending orders: {e}")
            self.log_error("pending_orders_storage", str(e))
            return 0
    
    def backfill_deal_history(self, account_config):
        """Perform initial 90-day backfill for an account"""
        account_number = account_config["account"]
        
        # Check if backfill is needed
        if not self.check_if_backfill_needed(account_number):
            return 0
        
        logger.info(f"[BACKFILL] Starting {INITIAL_BACKFILL_DAYS}-day backfill for account {account_number}")
        
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=INITIAL_BACKFILL_DAYS)
        
        deals = self.collect_deals(account_config, start_date, end_date)
        
        if len(deals) > 0:
            synced = self.sync_deals_to_mongodb(deals)
            logger.info(f"[OK] Backfill complete for {account_number}: {synced} deals")
            return synced
        else:
            logger.info(f"[STATS] No deals to backfill for {account_number}")
            return 0
    
    def sync_daily_deals(self, account_config):
        """Sync deals from last 24 hours (daily incremental)"""
        account_number = account_config["account"]
        
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=1)
        
        logger.info(f"[SYNC] Syncing daily deals for {account_number} ({start_date.date()} to {end_date.date()})")
        
        deals = self.collect_deals(account_config, start_date, end_date)
        
        if len(deals) > 0:
            synced = self.sync_deals_to_mongodb(deals)
            return synced
        else:
            logger.info(f"[STATS] No new deals for {account_number}")
            return 0
    
    def sync_account(self, account_config):
        """Sync a single MT5 account (basic account data)"""
        account_number = account_config["account"]
        password = account_config["password"]
        server = "MEXAtlantic-Real"
        
        try:
            # Login to MT5 account
            authorized = mt5.login(account_number, password=password, server=server)
            
            if not authorized:
                error = mt5.last_error()
                logger.error(f"[ERROR] Login failed for {account_number}: {error}")
                self.log_error("account_sync_login", f"Error: {error}", account_number)
                return False
            
            # Get account info
            account_info = mt5.account_info()
            if account_info is None:
                logger.error(f"[ERROR] Failed to get account info for {account_number}")
                return False
            
            # Get positions
            positions = mt5.positions_get()
            if positions is None:
                positions = []
            
            # Calculate metrics
            balance = account_info.balance
            equity = account_info.equity
            profit = account_info.profit
            margin = account_info.margin
            free_margin = account_info.margin_free
            margin_level = account_info.margin_level if account_info.margin_level else 0
            
            # Prepare update data
            update_data = {
                "account": account_number,
                "name": account_config["name"],
                "fund_type": account_config["fund_type"],
                "target_amount": account_config["target_amount"],
                "server": server,
                "broker": "MEXAtlantic",
                "balance": balance,
                "equity": equity,
                "margin": margin,
                "free_margin": free_margin,
                "margin_level": margin_level,
                "profit": profit,
                "num_positions": len(positions),
                "updated_at": datetime.now(timezone.utc),
                "connection_status": "active",
                "last_sync": datetime.now(timezone.utc)
            }
            
            # Update in MongoDB (upsert)
            if self.db is not None:
                self.db.mt5_accounts.update_one(
                    {"account": account_number},
                    {"$set": update_data},
                    upsert=True
                )
            
            logger.info(f"[OK] Synced {account_number}: Balance=${balance:.2f}, Equity=${equity:.2f}, P&L=${profit:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Error syncing account {account_number}: {e}")
            self.log_error("account_sync", str(e), account_number)
            return False
    
    def sync_all_accounts(self):
        """Sync all configured MT5 accounts (basic data)"""
        logger.info("=" * 80)
        logger.info(f"[SYNC] Starting account sync cycle at {datetime.now()}")
        
        success_count = 0
        fail_count = 0
        
        for account_config in self.mt5_accounts:
            if self.sync_account(account_config):
                success_count += 1
            else:
                fail_count += 1
            time.sleep(1)
        
        logger.info(f"[OK] Account sync complete: {success_count} successful, {fail_count} failed")
        logger.info("=" * 80)
    
    def sync_all_deals(self):
        """Sync deal history for all accounts (backfill + daily)"""
        logger.info("=" * 80)
        logger.info(f"💼 Starting deal history sync at {datetime.now()}")
        
        total_deals = 0
        
        for account_config in self.mt5_accounts:
            # Backfill if needed
            backfill_count = self.backfill_deal_history(account_config)
            total_deals += backfill_count
            
            # Daily incremental sync
            daily_count = self.sync_daily_deals(account_config)
            total_deals += daily_count
            
            time.sleep(2)  # Delay between accounts
        
        self.last_deal_sync = datetime.now(timezone.utc)
        logger.info(f"[OK] Deal sync complete: {total_deals} deals processed")
        logger.info("=" * 80)
    
    def sync_all_equity_snapshots(self):
        """Collect equity snapshots for all accounts"""
        logger.info("=" * 80)
        logger.info(f"[SNAPSHOT] Starting equity snapshot collection at {datetime.now()}")
        
        snapshots = []
        
        for account_config in self.mt5_accounts:
            snapshot = self.collect_equity_snapshot(account_config)
            if snapshot:
                snapshots.append(snapshot)
            time.sleep(1)
        
        if len(snapshots) > 0:
            self.sync_equity_snapshots_to_mongodb(snapshots)
        
        self.last_equity_snapshot = datetime.now(timezone.utc)
        logger.info(f"[OK] Equity snapshot complete: {len(snapshots)} snapshots collected")
        logger.info("=" * 80)
    
    def sync_all_pending_orders(self):
        """Collect pending orders for all accounts"""
        logger.info("=" * 80)
        logger.info(f"[ORDERS] Starting pending orders collection at {datetime.now()}")
        
        all_orders = []
        
        for account_config in self.mt5_accounts:
            orders = self.collect_pending_orders(account_config)
            all_orders.extend(orders)
            time.sleep(1)
        
        if len(all_orders) > 0:
            self.sync_pending_orders_to_mongodb(all_orders)
        else:
            logger.info("[STATS] No pending orders found across all accounts")
        
        logger.info(f"[OK] Pending orders sync complete: {len(all_orders)} orders collected")
        logger.info("=" * 80)
    
    def should_sync_deals(self):
        """Check if it's time to sync deals (daily)"""
        if self.last_deal_sync is None:
            return True
        
        time_since_last = datetime.now(timezone.utc) - self.last_deal_sync
        return time_since_last.total_seconds() >= DEAL_SYNC_INTERVAL
    
    def should_sync_equity_snapshots(self):
        """Check if it's time to collect equity snapshots (hourly)"""
        if self.last_equity_snapshot is None:
            return True
        
        time_since_last = datetime.now(timezone.utc) - self.last_equity_snapshot
        return time_since_last.total_seconds() >= EQUITY_SNAPSHOT_INTERVAL
    
    def run(self):
        """Main service loop"""
        logger.info("[START] MT5 Bridge Service - Enhanced (Phase 4B) Starting...")
        logger.info(f"[TIME]  Account sync interval: {UPDATE_INTERVAL} seconds ({UPDATE_INTERVAL/60:.1f} minutes)")
        logger.info(f"💼 Deal sync interval: {DEAL_SYNC_INTERVAL} seconds ({DEAL_SYNC_INTERVAL/3600:.1f} hours)")
        logger.info(f"[SNAPSHOT] Equity snapshot interval: {EQUITY_SNAPSHOT_INTERVAL} seconds ({EQUITY_SNAPSHOT_INTERVAL/3600:.1f} hours)")
        logger.info(f"[BACKFILL] Initial backfill: {INITIAL_BACKFILL_DAYS} days")
        
        # Connect to MongoDB
        if not self.connect_mongodb():
            logger.error("[ERROR] Failed to connect to MongoDB - exiting")
            sys.exit(1)
        
        # Load accounts
        self.load_mt5_accounts_from_mongodb()
        
        # Initialize MT5
        if not self.initialize_mt5():
            logger.error("[ERROR] Failed to initialize MT5 - exiting")
            sys.exit(1)
        
        # Log initial terminal status
        self.log_terminal_status()
        
        # Perform initial syncs
        logger.info("[TARGET] Performing initial data sync...")
        self.sync_all_deals()
        self.sync_all_equity_snapshots()
        self.sync_all_pending_orders()
        
        logger.info("[OK] Service initialized successfully - starting sync loop")
        
        # Main sync loop
        cycle_count = 0
        while True:
            try:
                cycle_count += 1
                logger.info(f"\n{'='*80}")
                logger.info(f"[STATS] SYNC CYCLE #{cycle_count}")
                
                # Reload accounts from MongoDB (in case config changed)
                self.load_mt5_accounts_from_mongodb()
                
                # Sync account data (every cycle - 5 minutes)
                self.sync_all_accounts()
                
                # Sync pending orders (every cycle - 5 minutes)
                self.sync_all_pending_orders()
                
                # Sync equity snapshots (hourly check)
                if self.should_sync_equity_snapshots():
                    logger.info("[SNAPSHOT] Hourly equity snapshot triggered")
                    self.sync_all_equity_snapshots()
                
                # Sync deals (daily check)
                if self.should_sync_deals():
                    logger.info("💼 Daily deal sync triggered")
                    self.sync_all_deals()
                
                # Log terminal status (every 12 cycles = 1 hour)
                if cycle_count % 12 == 0:
                    self.log_terminal_status()
                
                # Wait for next cycle
                logger.info(f"[WAIT] Next sync in {UPDATE_INTERVAL} seconds...")
                time.sleep(UPDATE_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("\n[WARNING] Service stopped by user (Ctrl+C)")
                break
            except Exception as e:
                logger.error(f"[ERROR] Unexpected error in main loop: {e}")
                self.log_error("main_loop", str(e))
                logger.info(f"[WAIT] Retrying in {UPDATE_INTERVAL} seconds...")
                time.sleep(UPDATE_INTERVAL)
        
        # Cleanup
        mt5.shutdown()
        logger.info("[OK] MT5 Bridge Service stopped")

if __name__ == "__main__":
    try:
        bridge = MT5BridgeEnhanced()
        bridge.run()
    except Exception as e:
        logger.error(f"[ERROR] Fatal error: {e}")
        sys.exit(1)
