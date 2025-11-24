import zmq
import json
import pymongo
from datetime import datetime, timezone
import time
import os
import sys
import logging
from threading import Thread
import signal
import traceback

# Configuration
MONGODB_URI = "mongodb+srv://emergent-ops:BpzaxqxDCjz1yWY4@fidus.ylp9be2.mongodb.net/fidus_production?retryWrites=true&w=majority&appName=FIDUS"
MONGODB_DATABASE = "fidus_production"

# ZeroMQ Configuration (must match MT4 EA)
ZEROMQ_PROTOCOL = "tcp"
ZEROMQ_HOST = "localhost" 
ZEROMQ_PUSH_PORT = 32768
ZEROMQ_PULL_PORT = 32769
ZEROMQ_PUB_PORT = 32770

# MT4 Account Configuration
MT4_ACCOUNT = {
    "login": 33200931,
    "password": ""[CLEANED_PASSWORD]"",
    "server": "MEXAtlantic-Real",
    "fund_type": "MONEY_MANAGER",
    "name": "Money Manager MT4 Account",
    "platform": "MT4"
}

# Setup logging
def setup_logging():
    """Setup comprehensive logging"""
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, 'mt4_bridge.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

class MT4BridgeService:
    def __init__(self):
        self.mongo_client = None
        self.db = None
        self.accounts_collection = None
        self.config_collection = None
        self.running = False
        self.last_data_time = None
        
        # ZeroMQ Context and Sockets
        self.context = zmq.Context()
        self.pull_socket = None
        self.push_socket = None
        self.sub_socket = None
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
        self.running = False
    
    def connect_mongodb(self):
        """Connect to MongoDB Atlas"""
        try:
            logger.info("Connecting to MongoDB Atlas...")
            self.mongo_client = pymongo.MongoClient(
                MONGODB_URI,
                serverSelectionTimeoutMS=10000,  # 10 second timeout
                connectTimeoutMS=10000,
                socketTimeoutMS=10000
            )
            
            # Test connection
            self.mongo_client.admin.command('ping')
            self.db = self.mongo_client[MONGODB_DATABASE]
            
            # Use the same collection as MT5 accounts for unified data
            self.accounts_collection = self.db['mt5_accounts']
            self.config_collection = self.db['mt5_account_config']
            
            logger.info("MongoDB connected successfully!")
            logger.info(f"Database: {MONGODB_DATABASE}")
            logger.info(f"Collections: mt5_accounts, mt5_account_config")
            
            return True
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            logger.error(f"Connection string: {MONGODB_URI[:50]}...")
            return False
    
    def setup_zeromq(self):
        """Setup ZeroMQ sockets to communicate with MT4 EA"""
        try:
            logger.info("Setting up ZeroMQ sockets...")
            
            # Set socket options for reliability
            socket_options = {
                zmq.LINGER: 1000,  # 1 second linger
                zmq.RCVTIMEO: 5000,  # 5 second receive timeout
                zmq.SNDTIMEO: 5000,  # 5 second send timeout
            }
            
            # PULL socket to receive data from MT4
            self.pull_socket = self.context.socket(zmq.PULL)
            for opt, val in socket_options.items():
                self.pull_socket.setsockopt(opt, val)
            
            pull_address = f"{ZEROMQ_PROTOCOL}://{ZEROMQ_HOST}:{ZEROMQ_PUSH_PORT}"
            self.pull_socket.connect(pull_address)
            logger.info(f"PULL socket connected to {pull_address}")
            
            # PUSH socket to send commands to MT4
            self.push_socket = self.context.socket(zmq.PUSH)
            for opt, val in socket_options.items():
                self.push_socket.setsockopt(opt, val)
            
            push_address = f"{ZEROMQ_PROTOCOL}://{ZEROMQ_HOST}:{ZEROMQ_PULL_PORT}"
            self.push_socket.connect(push_address)
            logger.info(f"PUSH socket connected to {push_address}")
            
            # SUB socket to monitor MT4 broadcasts
            self.sub_socket = self.context.socket(zmq.SUB)
            sub_address = f"{ZEROMQ_PROTOCOL}://{ZEROMQ_HOST}:{ZEROMQ_PUB_PORT}"
            self.sub_socket.connect(sub_address)
            self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")
            logger.info(f"SUB socket connected to {sub_address}")
            
            return True
        except Exception as e:
            logger.error(f"ZeroMQ setup failed: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def save_account_data(self, account_data):
        """Save MT4 account data to MongoDB (same collection as MT5) using EXACT Python MT5 API field names"""
        try:
            # Validate required fields (using Python MT5 API field names)
            required_fields = ['account', 'name', 'server', 'balance', 'equity', 
                             'margin', 'free_margin', 'profit', 'currency', 
                             'leverage', 'credit']
            
            for field in required_fields:
                if field not in account_data:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Add metadata to match MT5 format - using EXACT Python MT5 API field names
            current_time = datetime.now(timezone.utc)
            
            document = {
                # Core fields - EXACT Python MetaTrader5 API field names
                'account': account_data['account'],
                'name': account_data['name'],  # Client name goes in 'name' field
                'server': account_data['server'],
                'balance': float(account_data['balance']),
                'equity': float(account_data['equity']),
                'margin': float(account_data['margin']),
                'free_margin': float(account_data['free_margin']),  # NOT freeMargin
                'profit': float(account_data['profit']),
                'currency': account_data['currency'],
                'leverage': int(account_data['leverage']),
                'credit': float(account_data['credit']),
                
                # FIDUS custom fields
                'fund_type': MT4_ACCOUNT['fund_type'],  # NOT fundType
                'platform': 'MT4',
                'updated_at': current_time.isoformat(),
                '_id': f"MT4_{MT4_ACCOUNT['login']}"  # Document ID format
            }
            
            # Upsert to MongoDB (same collection as MT5 accounts) - NO DUPLICATES
            filter_query = {'account': MT4_ACCOUNT['login'], 'platform': 'MT4'}
            update_query = {'$set': document}
            
            result = self.accounts_collection.update_one(
                filter_query,
                update_query,
                upsert=True  # Updates existing or creates new - no duplicates
            )
            
            # Also update the config collection
            config_doc = {
                'account_number': account_data['account'],
                'server': account_data['server'],
                'fund_type': document['fund_type'],
                'platform': 'MT4',
                'enabled': True,
                'updated_at': current_time.isoformat()
            }
            
            self.config_collection.update_one(
                {'account_number': MT4_ACCOUNT['login']},
                {'$set': config_doc},
                upsert=True
            )
            
            # Update last data time
            self.last_data_time = current_time
            
            # Log success
            balance = document['balance']
            equity = document['equity']
            profit = document['profit']
            
            logger.info(f"✅ MT4 Account {MT4_ACCOUNT['login']} data saved")
            logger.info(f"   Balance: ${balance:,.2f} | Equity: ${equity:,.2f} | Profit: ${profit:,.2f}")
            
            if result.upserted_id:
                logger.info("   Created new document")
            else:
                logger.info("   Updated existing document")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save account data: {e}")
            logger.error(f"Account data: {account_data}")
            logger.error(traceback.format_exc())
            return False
    
    def receive_data_loop(self):
        """Main loop to receive data from MT4"""
        logger.info("🚀 Starting MT4 data receive loop...")
        logger.info(f"   Listening for data from MT4 account {MT4_ACCOUNT['login']}")
        logger.info(f"   Update interval: 300 seconds (5 minutes)")
        
        consecutive_errors = 0
        max_consecutive_errors = 10
        
        while self.running:
            try:
                # Non-blocking receive with timeout
                if self.pull_socket.poll(1000):  # 1 second timeout
                    message = self.pull_socket.recv_string(zmq.NOBLOCK)
                    logger.debug(f"📨 Received: {message[:200]}...")
                    
                    # Parse JSON
                    account_data = json.loads(message)
                    
                    # Validate it's our account
                    if account_data.get('account') == MT4_ACCOUNT['login']:
                        # Save to MongoDB
                        if self.save_account_data(account_data):
                            consecutive_errors = 0  # Reset error counter on success
                        else:
                            consecutive_errors += 1
                    else:
                        logger.warning(f"Received data for unexpected account: {account_data.get('account')}")
                
                # Check for stale data
                if self.last_data_time:
                    time_since_last = datetime.now(timezone.utc) - self.last_data_time
                    if time_since_last.total_seconds() > 900:  # 15 minutes
                        logger.warning(f"⚠️  No data received for {time_since_last.total_seconds():.0f} seconds")
                
                # Health check - send ping to MT4
                if consecutive_errors == 0:
                    try:
                        self.push_socket.send_string("PING", zmq.NOBLOCK)
                    except zmq.Again:
                        pass  # Socket not ready, skip ping
                        
            except zmq.Again:
                # No message available, continue
                continue
            except zmq.ZMQError as e:
                consecutive_errors += 1
                logger.error(f"ZMQ Error ({consecutive_errors}/{max_consecutive_errors}): {e}")
                if consecutive_errors >= max_consecutive_errors:
                    logger.error("Too many consecutive ZMQ errors. Restarting sockets...")
                    self.restart_sockets()
                    consecutive_errors = 0
                time.sleep(5)
            except json.JSONDecodeError as e:
                consecutive_errors += 1
                logger.error(f"JSON decode error: {e}")
                logger.error(f"Raw message: {message}")
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Error in receive loop: {e}")
                logger.error(traceback.format_exc())
                time.sleep(5)
        
        logger.info("📴 Data receive loop stopped")
    
    def restart_sockets(self):
        """Restart ZeroMQ sockets on error"""
        try:
            logger.info("🔄 Restarting ZeroMQ sockets...")
            
            # Close existing sockets
            if self.pull_socket:
                self.pull_socket.close()
            if self.push_socket:
                self.push_socket.close()
            if self.sub_socket:
                self.sub_socket.close()
            
            # Wait a moment
            time.sleep(2)
            
            # Recreate sockets
            self.setup_zeromq()
            logger.info("✅ ZeroMQ sockets restarted")
            
        except Exception as e:
            logger.error(f"Failed to restart sockets: {e}")
    
    def send_command(self, command):
        """Send command to MT4 EA"""
        try:
            self.push_socket.send_string(command, zmq.NOBLOCK)
            logger.info(f"📤 Sent command: {command}")
            return True
        except zmq.Again:
            logger.warning("Cannot send command - socket not ready")
            return False
        except Exception as e:
            logger.error(f"Failed to send command: {e}")
            return False
    
    def health_check(self):
        """Perform health checks"""
        logger.info("🔍 Performing health checks...")
        
        # Check MongoDB connection
        try:
            self.mongo_client.admin.command('ping')
            logger.info("✅ MongoDB: Connected")
        except Exception as e:
            logger.error(f"❌ MongoDB: {e}")
        
        # Check data freshness
        if self.last_data_time:
            age = datetime.now(timezone.utc) - self.last_data_time
            if age.total_seconds() < 600:  # 10 minutes
                logger.info(f"✅ Data: Fresh ({age.total_seconds():.0f}s ago)")
            else:
                logger.warning(f"⚠️  Data: Stale ({age.total_seconds():.0f}s ago)")
        else:
            logger.warning("⚠️  Data: No data received yet")
        
        # Send ping to MT4
        self.send_command("GET_ACCOUNT_INFO")
    
    def run(self):
        """Main service run method"""
        logger.info("=" * 60)
        logger.info("🚀 MT4 BRIDGE SERVICE STARTING")
        logger.info("=" * 60)
        logger.info(f"Account: {MT4_ACCOUNT['login']}")
        logger.info(f"Server: {MT4_ACCOUNT['server']}")
        logger.info(f"Platform: MT4")
        logger.info(f"Fund Type: {MT4_ACCOUNT['fund_type']}")
        logger.info("=" * 60)
        
        # Connect to MongoDB
        if not self.connect_mongodb():
            logger.error("❌ Failed to connect to MongoDB. Exiting.")
            return False
        
        # Setup ZeroMQ
        if not self.setup_zeromq():
            logger.error("❌ Failed to setup ZeroMQ. Exiting.")
            return False
        
        # Start receiving data
        self.running = True
        
        logger.info("✅ MT4 Bridge Service is running!")
        logger.info("📡 Waiting for data from MT4 EA...")
        logger.info("💡 Make sure the MT4_Python_Bridge.mq4 EA is attached to a chart")
        
        try:
            # Start health check thread
            def health_check_loop():
                while self.running:
                    time.sleep(300)  # Every 5 minutes
                    if self.running:
                        self.health_check()
            
            health_thread = Thread(target=health_check_loop, daemon=True)
            health_thread.start()
            
            # Start main data receive loop
            self.receive_data_loop()
            
        except KeyboardInterrupt:
            logger.info("⚠️  Service interrupted by user")
        except Exception as e:
            logger.error(f"💥 Unexpected error: {e}")
            logger.error(traceback.format_exc())
        finally:
            self.shutdown()
        
        return True
    
    def shutdown(self):
        """Cleanup on shutdown"""
        logger.info("🛑 Shutting down MT4 Bridge Service...")
        
        self.running = False
        
        # Close ZeroMQ sockets
        try:
            if self.pull_socket:
                self.pull_socket.close()
                logger.info("   PULL socket closed")
            if self.push_socket:
                self.push_socket.close()
                logger.info("   PUSH socket closed")
            if self.sub_socket:
                self.sub_socket.close()
                logger.info("   SUB socket closed")
            if self.context:
                self.context.term()
                logger.info("   ZeroMQ context terminated")
        except Exception as e:
            logger.error(f"Error closing ZeroMQ: {e}")
        
        # Close MongoDB connection
        try:
            if self.mongo_client:
                self.mongo_client.close()
                logger.info("   MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB: {e}")
        
        logger.info("✅ MT4 Bridge Service stopped cleanly")

def main():
    """Main entry point"""
    try:
        service = MT4BridgeService()
        success = service.run()
        return 0 if success else 1
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)