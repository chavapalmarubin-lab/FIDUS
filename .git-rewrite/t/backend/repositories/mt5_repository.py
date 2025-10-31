"""
MT5 Repository for FIDUS Investment Management Platform
Repository for MT5 account and trading data operations
"""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging
from decimal import Decimal

from .base_repository import BaseRepository
from models.mt5_account import (
    MT5Account, MT5AccountCreate, MT5AccountUpdate, 
    MT5Position, MT5Order, MT5Deal, MT5AccountSummary,
    BrokerCode, MT5AccountStatus
)

logger = logging.getLogger(__name__)

class MT5Repository(BaseRepository[MT5Account]):
    """Repository for MT5 account operations"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "mt5_accounts", MT5Account)
    
    async def create_mt5_account(self, account_data: MT5AccountCreate) -> Optional[MT5Account]:
        """Create a new MT5 account"""
        try:
            account_dict = account_data.dict()
            account_dict['status'] = MT5AccountStatus.PENDING
            account_dict['total_allocated'] = Decimal(0)
            account_dict['investment_ids'] = []
            account_dict['sync_status'] = 'pending'
            
            return await self.create(account_dict)
            
        except Exception as e:
            logger.error(f"Error creating MT5 account: {e}")
            raise
    
    async def find_by_mt5_login(self, mt5_login: int) -> Optional[MT5Account]:
        """Find MT5 account by login number"""
        return await self.find_one({'mt5_login': mt5_login})
    
    async def find_by_client_id(self, client_id: str) -> List[MT5Account]:
        """Get all MT5 accounts for a client"""
        return await self.find_many({'client_id': client_id})
    
    async def find_accounts_by_client_id(self, client_id: str) -> List[Dict[str, Any]]:
        """Get all MT5 accounts for a client (CRM endpoint compatible)"""
        try:
            accounts = await self.find_by_client_id(client_id)
            
            # Convert to dict format for CRM endpoints
            result = []
            for account in accounts:
                if hasattr(account, 'dict'):
                    # Pydantic model - convert to dict
                    account_dict = account.dict()
                elif isinstance(account, dict):
                    # Already a dict
                    account_dict = account
                else:
                    # Convert object attributes to dict
                    account_dict = {
                        'account_id': getattr(account, 'account_id', ''),
                        'client_id': getattr(account, 'client_id', ''),
                        'mt5_login': getattr(account, 'mt5_login', 0),
                        'broker_code': getattr(account, 'broker_code', ''),
                        'broker_name': getattr(account, 'broker_name', ''),
                        'mt5_server': getattr(account, 'mt5_server', ''),
                        'fund_code': getattr(account, 'fund_code', ''),
                        'is_active': getattr(account, 'is_active', False),
                        'status': getattr(account, 'status', ''),
                        'balance': getattr(account, 'balance', 0),
                        'equity': getattr(account, 'equity', 0)
                    }
                
                result.append(account_dict)
            
            return result
            
        except Exception as e:
            logger.error(f"Error finding accounts for client {client_id}: {e}")
            return []
    
    async def find_by_fund_code(self, fund_code: str) -> List[MT5Account]:
        """Get all MT5 accounts for a specific fund"""
        return await self.find_many({'fund_code': fund_code})
    
    async def find_active_accounts(self) -> List[MT5Account]:
        """Get all active MT5 accounts"""
        return await self.find_many({
            'is_active': True,
            'status': {'$in': [MT5AccountStatus.ACTIVE, MT5AccountStatus.PENDING]}
        })
    
    async def update_account_balance(
        self, 
        account_id: str, 
        balance: Decimal, 
        equity: Decimal, 
        profit: Decimal,
        margin: Optional[Decimal] = None,
        free_margin: Optional[Decimal] = None,
        margin_level: Optional[Decimal] = None
    ) -> bool:
        """Update MT5 account financial data"""
        try:
            update_data = {
                'balance': float(balance),
                'equity': float(equity),
                'profit': float(profit),
                'last_sync': datetime.now(timezone.utc),
                'sync_status': 'success'
            }
            
            if margin is not None:
                update_data['margin'] = float(margin)
            if free_margin is not None:
                update_data['free_margin'] = float(free_margin)
            if margin_level is not None:
                update_data['margin_level'] = float(margin_level)
            
            result = await self.update_by_id(account_id, update_data)
            return result is not None
            
        except Exception as e:
            logger.error(f"Error updating account balance for {account_id}: {e}")
            # Update sync status to error
            await self.update_by_id(account_id, {
                'sync_status': 'error',
                'last_sync': datetime.now(timezone.utc)
            })
            raise
    
    async def add_investment_to_account(self, account_id: str, investment_id: str, amount: Decimal) -> bool:
        """Add investment to MT5 account"""
        try:
            account = await self.find_by_id(account_id)
            if not account:
                return False
            
            # Update investment list and total allocated
            investment_ids = account.investment_ids.copy()
            if investment_id not in investment_ids:
                investment_ids.append(investment_id)
            
            new_total = account.total_allocated + amount
            
            result = await self.update_by_id(account_id, {
                'investment_ids': investment_ids,
                'total_allocated': float(new_total)
            })
            
            return result is not None
            
        except Exception as e:
            logger.error(f"Error adding investment to account {account_id}: {e}")
            raise
    
    async def remove_investment_from_account(self, account_id: str, investment_id: str, amount: Decimal) -> bool:
        """Remove investment from MT5 account"""
        try:
            account = await self.find_by_id(account_id)
            if not account:
                return False
            
            # Update investment list and total allocated
            investment_ids = account.investment_ids.copy()
            if investment_id in investment_ids:
                investment_ids.remove(investment_id)
            
            new_total = max(Decimal(0), account.total_allocated - amount)
            
            result = await self.update_by_id(account_id, {
                'investment_ids': investment_ids,
                'total_allocated': float(new_total)
            })
            
            return result is not None
            
        except Exception as e:
            logger.error(f"Error removing investment from account {account_id}: {e}")
            raise
    
    async def get_accounts_needing_sync(self, max_age_minutes: int = 5) -> List[MT5Account]:
        """Get accounts that need synchronization"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=max_age_minutes)
            
            return await self.find_many({
                'is_active': True,
                'status': MT5AccountStatus.ACTIVE,
                '$or': [
                    {'last_sync': None},
                    {'last_sync': {'$lt': cutoff_time}},
                    {'sync_status': 'error'}
                ]
            })
            
        except Exception as e:
            logger.error(f"Error getting accounts needing sync: {e}")
            raise
    
    async def get_account_statistics(self, account_id: str) -> Optional[Dict]:
        """Get comprehensive account statistics"""
        try:
            # This would typically aggregate data from positions, orders, and deals
            # For now, return basic account info
            account = await self.find_by_id(account_id)
            if not account:
                return None
            
            stats = {
                'account_id': account_id,
                'mt5_login': account.mt5_login,
                'balance': float(account.balance) if account.balance else 0,
                'equity': float(account.equity) if account.equity else 0,
                'profit': float(account.profit) if account.profit else 0,
                'total_allocated': float(account.total_allocated),
                'investment_count': len(account.investment_ids),
                'last_sync': account.last_sync,
                'sync_status': account.sync_status,
                'is_active': account.is_active,
                'status': account.status
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting account statistics for {account_id}: {e}")
            raise
    
    async def get_broker_statistics(self) -> Dict[str, Any]:
        """Get statistics by broker"""
        try:
            pipeline = [
                {
                    '$group': {
                        '_id': '$broker_code',
                        'account_count': {'$sum': 1},
                        'active_accounts': {
                            '$sum': {'$cond': [{'$eq': ['$is_active', True]}, 1, 0]}
                        },
                        'total_balance': {'$sum': '$balance'},
                        'total_equity': {'$sum': '$equity'},
                        'total_allocated': {'$sum': '$total_allocated'}
                    }
                }
            ]
            
            results = await self.aggregate(pipeline)
            
            broker_stats = {}
            for result in results:
                broker_code = result['_id']
                broker_stats[broker_code] = {
                    'account_count': result['account_count'],
                    'active_accounts': result['active_accounts'],
                    'total_balance': result['total_balance'] or 0,
                    'total_equity': result['total_equity'] or 0,
                    'total_allocated': result['total_allocated'] or 0
                }
            
            return broker_stats
            
        except Exception as e:
            logger.error(f"Error getting broker statistics: {e}")
            raise
    
    async def update_sync_status(self, account_id: str, status: str, error: Optional[str] = None) -> bool:
        """Update account synchronization status"""
        try:
            update_data = {
                'sync_status': status,
                'last_sync': datetime.now(timezone.utc)
            }
            
            if error:
                update_data['sync_error'] = error
            
            result = await self.update_by_id(account_id, update_data)
            return result is not None
            
        except Exception as e:
            logger.error(f"Error updating sync status for {account_id}: {e}")
            raise

class MT5PositionRepository(BaseRepository[MT5Position]):
    """Repository for MT5 position data"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "mt5_positions", MT5Position)
    
    async def get_positions_by_account(self, mt5_login: int) -> List[MT5Position]:
        """Get all positions for an MT5 account"""
        return await self.find_many({'mt5_login': mt5_login})
    
    async def get_open_positions(self) -> List[MT5Position]:
        """Get all currently open positions"""
        return await self.find_many({'status': 'open'})
    
    async def update_position_prices(self, ticket: int, current_price: Decimal, profit: Decimal) -> bool:
        """Update position current price and profit"""
        try:
            result = await self.collection.update_one(
                {'ticket': ticket},
                {
                    '$set': {
                        'price_current': float(current_price),
                        'profit': float(profit),
                        'time_update': datetime.now(timezone.utc)
                    }
                }
            )
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating position {ticket}: {e}")
            raise

class MT5OrderRepository(BaseRepository[MT5Order]):
    """Repository for MT5 pending orders"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "mt5_orders", MT5Order)
    
    async def get_orders_by_account(self, mt5_login: int) -> List[MT5Order]:
        """Get all pending orders for an MT5 account"""
        return await self.find_many({'mt5_login': mt5_login})

class MT5DealRepository(BaseRepository[MT5Deal]):
    """Repository for MT5 historical deals"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "mt5_deals", MT5Deal)
    
    async def get_deals_by_account(
        self, 
        mt5_login: int, 
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[MT5Deal]:
        """Get historical deals for an MT5 account"""
        filter_dict = {'mt5_login': mt5_login}
        
        if from_date or to_date:
            time_filter = {}
            if from_date:
                time_filter['$gte'] = from_date
            if to_date:
                time_filter['$lte'] = to_date
            filter_dict['time'] = time_filter
        
        return await self.find_many(filter_dict, sort=[('time', -1)])
    
    async def get_account_performance(self, mt5_login: int, days: int = 30) -> Dict:
        """Get account performance metrics"""
        try:
            from_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            pipeline = [
                {
                    '$match': {
                        'mt5_login': mt5_login,
                        'time': {'$gte': from_date}
                    }
                },
                {
                    '$group': {
                        '_id': None,
                        'total_trades': {'$sum': 1},
                        'total_profit': {'$sum': '$profit'},
                        'total_volume': {'$sum': '$volume'},
                        'winning_trades': {
                            '$sum': {'$cond': [{'$gt': ['$profit', 0]}, 1, 0]}
                        },
                        'losing_trades': {
                            '$sum': {'$cond': [{'$lt': ['$profit', 0]}, 1, 0]}
                        }
                    }
                }
            ]
            
            results = await self.aggregate(pipeline)
            
            if not results:
                return {
                    'total_trades': 0,
                    'total_profit': 0,
                    'total_volume': 0,
                    'winning_trades': 0,
                    'losing_trades': 0,
                    'win_rate': 0
                }
            
            result = results[0]
            total_trades = result['total_trades']
            win_rate = (result['winning_trades'] / total_trades * 100) if total_trades > 0 else 0
            
            return {
                'total_trades': total_trades,
                'total_profit': result['total_profit'],
                'total_volume': result['total_volume'],
                'winning_trades': result['winning_trades'],
                'losing_trades': result['losing_trades'],
                'win_rate': round(win_rate, 2),
                'average_profit_per_trade': result['total_profit'] / total_trades if total_trades > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting account performance for {mt5_login}: {e}")
            raise