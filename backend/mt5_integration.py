"""
MT5 Integration Service for FIDUS Investment Management System
Handles MT5 account creation, management, and real-time performance tracking
"""

import os
import uuid
import asyncio
import logging
import secrets
import string
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json
import random

# Import encryption for secure credential storage
from cryptography.fernet import Fernet

# MongoDB integration
from mongodb_integration import mongodb_manager

class MT5BrokerConfig:
    """Configuration for supported MT5 brokers"""
    BROKERS = {
        "multibank": {
            "name": "Multibank",
            "servers": ["Multibank-Live", "Multibank-Demo"],
            "description": "Multibank Group - Global Trading Platform",
            "supported_instruments": ["EURUSD", "GBPUSD", "USDJPY", "GOLD", "SILVER"],
            "max_accounts_per_client": 4
        },
        "dootechnology": {
            "name": "DooTechnology", 
            "servers": ["DooTechnology-Live", "DooTechnology-Demo"],
            "description": "DooTechnology - Advanced Trading Solutions",
            "supported_instruments": ["EURUSD", "GBPUSD", "USDJPY", "GOLD", "SILVER", "CRUDE"],
            "max_accounts_per_client": 4
        }
    }
    
    @classmethod
    def get_broker_list(cls):
        """Get list of available brokers for dropdown"""
        return [
            {
                "code": code,
                "name": config["name"],
                "description": config["description"],
                "servers": config["servers"]
            }
            for code, config in cls.BROKERS.items()
        ]
    
    @classmethod
    def get_broker_servers(cls, broker_code: str):
        """Get available servers for a specific broker"""
        return cls.BROKERS.get(broker_code, {}).get("servers", [])
    
    @classmethod
    def is_valid_broker(cls, broker_code: str):
        """Check if broker code is valid"""
        return broker_code in cls.BROKERS

class MT5ConnectionStatus(Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    CONNECTING = "connecting"

@dataclass
class MT5AccountInfo:
    account_id: str
    client_id: str
    fund_code: str
    broker_code: str  # NEW: Broker identifier
    broker_name: str  # NEW: Human-readable broker name
    mt5_login: int
    mt5_server: str
    total_allocated: float
    current_equity: float
    profit_loss: float
    profit_loss_percentage: float
    investment_ids: List[str]
    status: str
    created_at: str
    updated_at: str

@dataclass
class MT5PerformanceData:
    account_id: str
    equity: float
    balance: float
    margin: float
    free_margin: float
    margin_level: float
    profit: float
    positions_count: int
    timestamp: str

class MT5IntegrationService:
    """MT5 Integration Service with Multibank broker integration"""
    
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.fernet = Fernet(self.encryption_key)
        self.connected_accounts: Dict[str, Dict] = {}
        self.performance_cache: Dict[str, MT5PerformanceData] = {}
        
        # Multibank MT5 server configurations
        self.server_configs = {
            "CORE": "Multibank-Core-01.multibank.fx",
            "BALANCE": "Multibank-Balance-01.multibank.fx", 
            "DYNAMIC": "Multibank-Dynamic-01.multibank.fx",
            "UNLIMITED": "Multibank-Unlimited-01.multibank.fx"
        }
        
        logging.info("MT5 Integration Service initialized")
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for MT5 credentials"""
        key_file = "/app/backend/.mt5_key"
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Restrict file permissions
            return key
    
    def _generate_mt5_login(self) -> int:
        """Generate unique MT5 login number"""
        # In production, this would request from Multibank API
        return random.randint(10000000, 99999999)
    
    def _generate_mt5_password(self) -> str:
        """Generate secure MT5 password"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(12))
    
    def _get_mt5_server(self, fund_code: str, broker_code: str = "multibank") -> str:
        """Get MT5 server for specific fund and broker"""
        broker_config = MT5BrokerConfig.BROKERS.get(broker_code, {})
        default_servers = broker_config.get("servers", ["Multibank-Live"])
        
        # Map fund codes to server preferences
        server_mapping = {
            "multibank": {
                "CORE": "Multibank-Live",
                "BALANCE": "Multibank-Live", 
                "DYNAMIC": "Multibank-Live",
                "UNLIMITED": "Multibank-Live"
            },
            "dootechnology": {
                "CORE": "DooTechnology-Live",
                "BALANCE": "DooTechnology-Live",
                "DYNAMIC": "DooTechnology-Live", 
                "UNLIMITED": "DooTechnology-Live"
            }
        }
        
        broker_mapping = server_mapping.get(broker_code, {})
        return broker_mapping.get(fund_code, default_servers[0])
    
    def _encrypt_password(self, password: str) -> str:
        """Encrypt MT5 password for secure storage"""
        return self.fernet.encrypt(password.encode()).decode()
    
    def _decrypt_password(self, encrypted_password: str) -> str:
        """Decrypt MT5 password for authentication"""
        return self.fernet.decrypt(encrypted_password.encode()).decode()
    
    async def get_or_create_mt5_account(self, client_id: str, fund_code: str, 
                                      investment_data: Dict[str, Any], 
                                      broker_code: str = "multibank") -> Optional[str]:
        """Get existing MT5 account for client+fund+broker or create new one"""
        try:
            # Validate broker
            if not MT5BrokerConfig.is_valid_broker(broker_code):
                logging.error(f"Invalid broker code: {broker_code}")
                return None
            
            broker_config = MT5BrokerConfig.BROKERS[broker_code]
            
            # Check if client already has MT5 account for this fund with same broker
            existing_accounts = mongodb_manager.get_client_mt5_accounts(client_id)
            
            for account in existing_accounts:
                if (account['fund_code'] == fund_code and 
                    account.get('broker_code') == broker_code):
                    # Add investment to existing account
                    account_id = account['account_id']
                    
                    success = mongodb_manager.update_mt5_account_allocation(
                        account_id, 
                        investment_data['principal_amount'],
                        investment_data['investment_id']
                    )
                    
                    if success:
                        logging.info(f"Added ${investment_data['principal_amount']} to existing MT5 account {account_id} on {broker_config['name']}")
                        return account_id
                    else:
                        logging.error(f"Failed to update MT5 account allocation for {account_id}")
                        return None
            
            # Create new MT5 account
            account_id = f"mt5_{client_id}_{fund_code}_{broker_code}_{str(uuid.uuid4())[:8]}"
            mt5_login = self._generate_mt5_login()
            mt5_password = self._generate_mt5_password()
            mt5_server = self._get_mt5_server(fund_code, broker_code)
            
            # Store encrypted credentials
            encrypted_password = self._encrypt_password(mt5_password)
            mongodb_manager.store_mt5_credentials(account_id, encrypted_password)
            
            # Create MT5 account record
            mt5_account_data = {
                'account_id': account_id,
                'client_id': client_id,
                'fund_code': fund_code,
                'broker_code': broker_code,
                'broker_name': broker_config["name"],
                'mt5_login': mt5_login,
                'mt5_server': mt5_server,
                'total_allocated': investment_data['principal_amount'],
                'current_equity': investment_data['principal_amount'],
                'profit_loss': 0.0,
                'investment_ids': [investment_data['investment_id']],
                'status': 'active'
            }
            
            created_account_id = mongodb_manager.create_mt5_account(mt5_account_data)
            
            if created_account_id:
                # Attempt to connect to MT5 (mock for now)
                await self._mock_mt5_connection(account_id, mt5_login, mt5_password, mt5_server)
                
                logging.info(f"Created new MT5 account {account_id} for client {client_id} fund {fund_code} on {broker_config['name']}")
                return created_account_id
            
            return None
            
        except Exception as e:
            logging.error(f"Error creating/getting MT5 account: {str(e)}")
            return None
    
    async def _mock_mt5_connection(self, account_id: str, login: int, password: str, server: str) -> bool:
        """Mock MT5 connection (replace with real MT5 API in production)"""
        try:
            # Simulate connection delay
            await asyncio.sleep(0.5)
            
            # Mock connection success
            self.connected_accounts[account_id] = {
                'login': login,
                'server': server,
                'connected_at': datetime.now(timezone.utc),
                'status': MT5ConnectionStatus.CONNECTED
            }
            
            # Initialize mock performance data
            initial_equity = mongodb_manager.db.mt5_accounts.find_one(
                {'account_id': account_id}
            )['total_allocated']
            
            self.performance_cache[account_id] = MT5PerformanceData(
                account_id=account_id,
                equity=initial_equity,
                balance=initial_equity,
                margin=0.0,
                free_margin=initial_equity,
                margin_level=0.0 if initial_equity == 0 else 100.0,
                profit=0.0,
                positions_count=0,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            logging.info(f"Mock MT5 connection established for account {account_id}")
            return True
            
        except Exception as e:
            logging.error(f"Mock MT5 connection failed for account {account_id}: {str(e)}")
            return False
    
    async def get_account_performance(self, account_id: str) -> Optional[MT5PerformanceData]:
        """Get real-time account performance data"""
        try:
            # Check if account is connected
            if account_id not in self.connected_accounts:
                # Try to reconnect
                account = mongodb_manager.db.mt5_accounts.find_one({'account_id': account_id})
                if account:
                    encrypted_password = mongodb_manager.get_mt5_credentials(account_id)
                    if encrypted_password:
                        password = self._decrypt_password(encrypted_password)
                        await self._mock_mt5_connection(
                            account_id, 
                            account['mt5_login'], 
                            password, 
                            account['mt5_server']
                        )
            
            # Get performance data (mock implementation)
            performance = await self._get_mock_performance_data(account_id)
            
            if performance:
                # Update database with latest performance
                mongodb_manager.update_mt5_account_performance(account_id, performance.equity)
                self.performance_cache[account_id] = performance
            
            return performance
            
        except Exception as e:
            logging.error(f"Error getting account performance for {account_id}: {str(e)}")
            return None
    
    async def _get_mock_performance_data(self, account_id: str) -> Optional[MT5PerformanceData]:
        """Generate mock performance data (replace with real MT5 API calls)"""
        try:
            # Get account info from database
            account = mongodb_manager.db.mt5_accounts.find_one({'account_id': account_id})
            if not account:
                return None
            
            base_equity = account['total_allocated']
            
            # Generate mock performance with some volatility
            # Simulate realistic trading performance
            time_elapsed_hours = (datetime.now(timezone.utc) - account['created_at']).total_seconds() / 3600
            
            # Mock performance factors
            daily_volatility = 0.02  # 2% daily volatility
            trend_factor = 0.001     # Slight positive trend per hour
            
            # Generate performance with some randomness
            random_factor = random.uniform(-daily_volatility, daily_volatility) / 24  # Hourly volatility
            trend_adjustment = trend_factor * time_elapsed_hours
            
            performance_multiplier = 1 + trend_adjustment + random_factor
            current_equity = base_equity * performance_multiplier
            
            # Ensure some minimum variation
            current_equity = max(base_equity * 0.95, min(base_equity * 1.15, current_equity))
            
            profit = current_equity - base_equity
            
            # Mock margin calculations (for demonstration)
            used_margin = random.uniform(0, current_equity * 0.3) if current_equity > 0 else 0
            free_margin = current_equity - used_margin
            margin_level = (current_equity / used_margin * 100) if used_margin > 0 else 0
            
            # Mock position count
            positions_count = random.randint(0, 5)
            
            performance_data = MT5PerformanceData(
                account_id=account_id,
                equity=round(current_equity, 2),
                balance=round(base_equity, 2),
                margin=round(used_margin, 2),
                free_margin=round(free_margin, 2),
                margin_level=round(margin_level, 2),
                profit=round(profit, 2),
                positions_count=positions_count,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            return performance_data
            
        except Exception as e:
            logging.error(f"Error generating mock performance data: {str(e)}")
            return None
    
    async def get_all_accounts_performance(self) -> Dict[str, MT5PerformanceData]:
        """Get performance data for all active MT5 accounts"""
        try:
            all_accounts = mongodb_manager.get_all_mt5_accounts()
            performance_data = {}
            
            for account in all_accounts:
                account_id = account['account_id']
                performance = await self.get_account_performance(account_id)
                
                if performance:
                    performance_data[account_id] = performance
            
            return performance_data
            
        except Exception as e:
            logging.error(f"Error getting all accounts performance: {str(e)}")
            return {}
    
    async def update_client_mt5_credentials(self, client_id: str, fund_code: str, 
                                          new_login: int, new_password: str, 
                                          new_server: str) -> bool:
        """Update MT5 credentials for existing account (admin function)"""
        try:
            # Find the MT5 account
            accounts = mongodb_manager.get_client_mt5_accounts(client_id)
            target_account = None
            
            for account in accounts:
                if account['fund_code'] == fund_code:
                    target_account = account
                    break
            
            if not target_account:
                logging.error(f"No MT5 account found for client {client_id} fund {fund_code}")
                return False
            
            account_id = target_account['account_id']
            
            # Encrypt new password
            encrypted_password = self._encrypt_password(new_password)
            
            # Update credentials in database
            success = mongodb_manager.store_mt5_credentials(account_id, encrypted_password)
            
            if success:
                # Update MT5 account record
                mongodb_manager.db.mt5_accounts.update_one(
                    {'account_id': account_id},
                    {
                        '$set': {
                            'mt5_login': new_login,
                            'mt5_server': new_server,
                            'updated_at': datetime.now(timezone.utc)
                        }
                    }
                )
                
                # Reconnect with new credentials
                await self._mock_mt5_connection(account_id, new_login, new_password, new_server)
                
                logging.info(f"Updated MT5 credentials for account {account_id}")
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"Error updating MT5 credentials: {str(e)}")
            return False
    
    def get_connection_status(self, account_id: str) -> MT5ConnectionStatus:
        """Get connection status for MT5 account"""
        if account_id in self.connected_accounts:
            return self.connected_accounts[account_id]['status']
        return MT5ConnectionStatus.DISCONNECTED
    
    async def disconnect_account(self, account_id: str) -> bool:
        """Disconnect MT5 account"""
        try:
            if account_id in self.connected_accounts:
                del self.connected_accounts[account_id]
            
            if account_id in self.performance_cache:
                del self.performance_cache[account_id]
            
            logging.info(f"Disconnected MT5 account {account_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error disconnecting MT5 account {account_id}: {str(e)}")
            return False
    
    async def get_account_summary(self, client_id: str) -> Dict[str, Any]:
        """Get comprehensive MT5 account summary for client"""
        try:
            accounts = mongodb_manager.get_client_mt5_accounts(client_id)
            summary = {
                'total_accounts': len(accounts),
                'total_allocated': 0,
                'total_equity': 0,
                'total_profit_loss': 0,
                'accounts': []
            }
            
            for account in accounts:
                # Get real-time performance
                performance = await self.get_account_performance(account['account_id'])
                
                if performance:
                    account['current_equity'] = performance.equity
                    account['profit_loss'] = performance.profit
                    account['profit_loss_percentage'] = (performance.profit / account['total_allocated'] * 100) if account['total_allocated'] > 0 else 0
                
                summary['total_allocated'] += account['total_allocated']
                summary['total_equity'] += account['current_equity']
                summary['total_profit_loss'] += account['profit_loss']
                summary['accounts'].append(account)
            
            # Calculate overall performance percentage
            summary['overall_performance_percentage'] = (
                summary['total_profit_loss'] / summary['total_allocated'] * 100
            ) if summary['total_allocated'] > 0 else 0
            
            return summary
            
        except Exception as e:
            logging.error(f"Error getting account summary for client {client_id}: {str(e)}")
            return {}

# Global MT5 integration service instance
mt5_service = MT5IntegrationService()