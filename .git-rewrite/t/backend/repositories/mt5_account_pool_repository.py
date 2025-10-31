"""
MT5 Account Pool Repository for FIDUS Investment Management Platform
Repository for managing MT5 account pool and multiple investment mappings
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging
from decimal import Decimal

from .base_repository import BaseRepository
from models.mt5_account_pool import (
    MT5AccountPool, MT5AccountPoolCreate, MT5AccountPoolUpdate,
    MT5InvestmentMapping, MT5InvestmentMappingCreate, MT5InvestmentMappingUpdate,
    DeallocationRequest, MT5AllocationAuditLog,
    MT5AccountPoolStatus, MT5AccountType, BrokerCode
)

logger = logging.getLogger(__name__)

class MT5AccountPoolRepository(BaseRepository[MT5AccountPool]):
    """Repository for MT5 account pool management"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "mt5_account_pool", MT5AccountPool)
    
    async def add_account_to_pool(
        self, 
        account_data: MT5AccountPoolCreate, 
        admin_user_id: str
    ) -> Optional[MT5AccountPool]:
        """Add new MT5 account to the available pool"""
        try:
            # Check if account already exists
            existing = await self.find_one({'mt5_account_number': account_data.mt5_account_number})
            if existing:
                raise ValueError(f'MT5 account {account_data.mt5_account_number} already exists in pool')
            
            account_dict = account_data.dict()
            account_dict['status'] = MT5AccountPoolStatus.AVAILABLE
            account_dict['created_by_admin'] = admin_user_id
            
            # Encrypt the investor password (you might want to use proper encryption)
            # For now, we'll store it as-is but this should be encrypted in production
            
            new_account = await self.create(account_dict)
            
            # Log the addition
            await self._log_audit_action(
                action_type="pool_add",
                mt5_account_number=account_data.mt5_account_number,
                new_values=account_dict,
                admin_user_id=admin_user_id,
                change_notes=f"Added MT5 account {account_data.mt5_account_number} to pool"
            )
            
            return new_account
            
        except Exception as e:
            logger.error(f"Error adding MT5 account to pool: {e}")
            raise
    
    async def get_available_accounts(
        self, 
        account_type: Optional[MT5AccountType] = None,
        broker: Optional[BrokerCode] = None
    ) -> List[MT5AccountPool]:
        """Get all available MT5 accounts from pool"""
        try:
            filter_dict = {'status': MT5AccountPoolStatus.AVAILABLE}
            
            if account_type:
                filter_dict['account_type'] = account_type
            if broker:
                filter_dict['broker_name'] = broker
            
            return await self.find_many(filter_dict, sort=[('created_at', -1)])
            
        except Exception as e:
            logger.error(f"Error getting available accounts: {e}")
            raise
    
    async def get_allocated_accounts(self, client_id: Optional[str] = None) -> List[MT5AccountPool]:
        """Get all allocated MT5 accounts"""
        try:
            filter_dict = {'status': MT5AccountPoolStatus.ALLOCATED}
            
            if client_id:
                filter_dict['allocated_to_client_id'] = client_id
            
            return await self.find_many(filter_dict, sort=[('allocation_date', -1)])
            
        except Exception as e:
            logger.error(f"Error getting allocated accounts: {e}")
            raise
    
    async def allocate_account_to_client(
        self,
        mt5_account_number: int,
        client_id: str,
        investment_id: str,
        allocated_amount: Decimal,
        admin_user_id: str,
        allocation_notes: str
    ) -> bool:
        """Allocate an available MT5 account to a client"""
        try:
            # Check account is available
            account = await self.find_one({
                'mt5_account_number': mt5_account_number,
                'status': MT5AccountPoolStatus.AVAILABLE
            })
            
            if not account:
                raise ValueError(f'MT5 account {mt5_account_number} not available for allocation')
            
            # Update account status
            allocation_data = {
                'status': MT5AccountPoolStatus.ALLOCATED,
                'allocated_to_client_id': client_id,
                'allocated_to_investment_id': investment_id,
                'allocated_amount': float(allocated_amount),
                'allocation_date': datetime.now(timezone.utc),
                'allocated_by_admin': admin_user_id
            }
            
            result = await self.update_by_id(account.pool_id, allocation_data)
            
            if result:
                # Log the allocation
                await self._log_audit_action(
                    action_type="allocate",
                    mt5_account_number=mt5_account_number,
                    investment_id=investment_id,
                    client_id=client_id,
                    old_values={'status': 'available'},
                    new_values=allocation_data,
                    admin_user_id=admin_user_id,
                    change_notes=allocation_notes
                )
            
            return result is not None
            
        except Exception as e:
            logger.error(f"Error allocating MT5 account {mt5_account_number}: {e}")
            raise
    
    async def request_deallocation(
        self,
        mt5_account_number: int,
        admin_user_id: str,
        reason_notes: str
    ) -> str:
        """Request deallocation of an MT5 account"""
        try:
            # Check account is allocated
            account = await self.find_one({
                'mt5_account_number': mt5_account_number,
                'status': MT5AccountPoolStatus.ALLOCATED
            })
            
            if not account:
                raise ValueError(f'MT5 account {mt5_account_number} not allocated or not found')
            
            # Create deallocation request
            deallocation_data = {
                'mt5_account_number': mt5_account_number,
                'client_id': account.allocated_to_client_id,
                'investment_id': account.allocated_to_investment_id,
                'reason_notes': reason_notes,
                'requested_by_admin': admin_user_id,
                'original_allocated_amount': account.allocated_amount,
                'original_allocation_date': account.allocation_date,
                'original_allocation_notes': f"Originally allocated by {account.allocated_by_admin}"
            }
            
            deallocation_request = DeallocationRequest(**deallocation_data)
            
            # Store in deallocation_requests collection
            dealloc_collection = self.db["deallocation_requests"]
            await dealloc_collection.insert_one(deallocation_request.dict())
            
            # Update account status
            await self.update_by_id(account.pool_id, {
                'status': MT5AccountPoolStatus.PENDING_DEALLOCATION,
                'deallocation_requested_by': admin_user_id,
                'deallocation_request_date': datetime.now(timezone.utc),
                'deallocation_reason': reason_notes
            })
            
            # Log the request
            await self._log_audit_action(
                action_type="deallocation_request",
                mt5_account_number=mt5_account_number,
                investment_id=account.allocated_to_investment_id,
                client_id=account.allocated_to_client_id,
                admin_user_id=admin_user_id,
                change_notes=f"Deallocation requested: {reason_notes}"
            )
            
            return deallocation_request.request_id
            
        except Exception as e:
            logger.error(f"Error requesting deallocation for {mt5_account_number}: {e}")
            raise
    
    async def approve_deallocation(
        self,
        request_id: str,
        approving_admin_id: str,
        approval_notes: Optional[str] = None
    ) -> bool:
        """Approve a deallocation request"""
        try:
            dealloc_collection = self.db["deallocation_requests"]
            
            # Find the request
            request_doc = await dealloc_collection.find_one({
                'request_id': request_id,
                'status': 'pending_approval'
            })
            
            if not request_doc:
                raise ValueError(f'Deallocation request {request_id} not found or not pending')
            
            mt5_account_number = request_doc['mt5_account_number']
            
            # Update request status
            await dealloc_collection.update_one(
                {'request_id': request_id},
                {
                    '$set': {
                        'status': 'approved',
                        'approved_by_admin': approving_admin_id,
                        'approval_date': datetime.now(timezone.utc),
                        'approval_notes': approval_notes or ''
                    }
                }
            )
            
            # Update account status back to available
            account = await self.find_one({'mt5_account_number': mt5_account_number})
            if account:
                await self.update_by_id(account.pool_id, {
                    'status': MT5AccountPoolStatus.AVAILABLE,
                    'allocated_to_client_id': None,
                    'allocated_to_investment_id': None,
                    'allocated_amount': None,
                    'allocation_date': None,
                    'allocated_by_admin': None,
                    'deallocation_approved_by': approving_admin_id,
                    'deallocation_approved_date': datetime.now(timezone.utc)
                })
                
                # Log the approval
                await self._log_audit_action(
                    action_type="deallocation_approved",
                    mt5_account_number=mt5_account_number,
                    admin_user_id=approving_admin_id,
                    change_notes=f"Deallocation approved by {approving_admin_id}: {approval_notes or 'No additional notes'}"
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error approving deallocation request {request_id}: {e}")
            raise
    
    async def get_pending_deallocation_requests(self) -> List[Dict]:
        """Get all pending deallocation requests"""
        try:
            dealloc_collection = self.db["deallocation_requests"]
            cursor = dealloc_collection.find({'status': 'pending_approval'}).sort('request_date', -1)
            return await cursor.to_list(length=None)
            
        except Exception as e:
            logger.error(f"Error getting pending deallocation requests: {e}")
            raise
    
    async def get_account_by_number(self, mt5_account_number: int) -> Optional[MT5AccountPool]:
        """Get MT5 account from pool by account number"""
        return await self.find_one({'mt5_account_number': mt5_account_number})
    
    async def check_account_exclusivity(self, mt5_account_number: int) -> Dict[str, Any]:
        """Check if MT5 account is exclusively available for allocation"""
        try:
            account = await self.get_account_by_number(mt5_account_number)
            
            if not account:
                return {
                    'is_available': False,
                    'reason': 'Account not found in pool',
                    'current_status': None
                }
            
            if account.status == MT5AccountPoolStatus.AVAILABLE:
                return {
                    'is_available': True,
                    'reason': 'Account is available for allocation',
                    'current_status': account.status
                }
            else:
                return {
                    'is_available': False,
                    'reason': f'Account is {account.status}',
                    'current_status': account.status,
                    'allocated_to_client': account.allocated_to_client_id,
                    'allocation_date': account.allocation_date
                }
                
        except Exception as e:
            logger.error(f"Error checking account exclusivity for {mt5_account_number}: {e}")
            raise
    
    async def get_pool_statistics(self) -> Dict[str, Any]:
        """Get comprehensive pool statistics"""
        try:
            pipeline = [
                {
                    '$group': {
                        '_id': '$status',
                        'count': {'$sum': 1}
                    }
                }
            ]
            
            status_counts = await self.aggregate(pipeline)
            
            # Convert to dict
            stats = {
                'total_accounts': 0,
                'available': 0,
                'allocated': 0,
                'pending_deallocation': 0,
                'maintenance': 0,
                'inactive': 0
            }
            
            for stat in status_counts:
                status = stat['_id']
                count = stat['count']
                stats['total_accounts'] += count
                
                if status == MT5AccountPoolStatus.AVAILABLE:
                    stats['available'] = count
                elif status == MT5AccountPoolStatus.ALLOCATED:
                    stats['allocated'] = count
                elif status == MT5AccountPoolStatus.PENDING_DEALLOCATION:
                    stats['pending_deallocation'] = count
                elif status == MT5AccountPoolStatus.MAINTENANCE:
                    stats['maintenance'] = count
                elif status == MT5AccountPoolStatus.INACTIVE:
                    stats['inactive'] = count
            
            # Get broker breakdown
            broker_pipeline = [
                {
                    '$group': {
                        '_id': '$broker_name',
                        'total': {'$sum': 1},
                        'available': {'$sum': {'$cond': [{'$eq': ['$status', 'available']}, 1, 0]}},
                        'allocated': {'$sum': {'$cond': [{'$eq': ['$status', 'allocated']}, 1, 0]}}
                    }
                }
            ]
            
            broker_stats = await self.aggregate(broker_pipeline)
            stats['by_broker'] = {stat['_id']: stat for stat in broker_stats}
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting pool statistics: {e}")
            raise
    
    async def _log_audit_action(
        self,
        action_type: str,
        mt5_account_number: int,
        admin_user_id: str,
        change_notes: str,
        investment_id: Optional[str] = None,
        client_id: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None
    ):
        """Log audit action to audit trail"""
        try:
            audit_log = MT5AllocationAuditLog(
                action_type=action_type,
                mt5_account_number=mt5_account_number,
                investment_id=investment_id,
                client_id=client_id,
                old_values=old_values,
                new_values=new_values,
                change_notes=change_notes,
                admin_user_id=admin_user_id
            )
            
            audit_collection = self.db["mt5_allocation_audit_log"]
            await audit_collection.insert_one(audit_log.dict())
            
        except Exception as e:
            logger.error(f"Error logging audit action: {e}")
            # Don't raise here as audit logging shouldn't break main operations

class MT5InvestmentMappingRepository(BaseRepository[MT5InvestmentMapping]):
    """Repository for MT5 investment mappings"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "mt5_investment_mappings", MT5InvestmentMapping)
    
    async def create_mappings_for_investment(
        self,
        investment_id: str,
        client_id: str,
        fund_code: str,
        mappings: List[MT5InvestmentMappingCreate],
        admin_user_id: str
    ) -> List[MT5InvestmentMapping]:
        """Create multiple MT5 mappings for an investment"""
        try:
            created_mappings = []
            
            for mapping_data in mappings:
                mapping_dict = mapping_data.dict()
                mapping_dict.update({
                    'investment_id': investment_id,
                    'client_id': client_id,
                    'fund_code': fund_code,
                    'allocated_by_admin': admin_user_id,
                    'status': 'active'
                })
                
                mapping = await self.create(mapping_dict)
                if mapping:
                    created_mappings.append(mapping)
            
            return created_mappings
            
        except Exception as e:
            logger.error(f"Error creating MT5 mappings for investment {investment_id}: {e}")
            raise
    
    async def get_mappings_by_investment(self, investment_id: str) -> List[MT5InvestmentMapping]:
        """Get all MT5 mappings for an investment"""
        return await self.find_many({'investment_id': investment_id, 'status': 'active'})
    
    async def get_mappings_by_client(self, client_id: str) -> List[MT5InvestmentMapping]:
        """Get all MT5 mappings for a client"""
        return await self.find_many({'client_id': client_id, 'status': 'active'})
    
    async def validate_investment_mappings(
        self, 
        investment_id: str, 
        total_investment_amount: Decimal
    ) -> Dict[str, Any]:
        """Validate that MT5 mappings sum equals investment amount"""
        try:
            mappings = await self.get_mappings_by_investment(investment_id)
            
            total_mapped = sum(mapping.allocated_amount for mapping in mappings)
            difference = abs(total_mapped - total_investment_amount)
            
            is_valid = difference < Decimal('0.01')  # 1 cent tolerance
            
            mt5_accounts_used = [mapping.mt5_account_number for mapping in mappings]
            duplicate_accounts = [x for x in mt5_accounts_used if mt5_accounts_used.count(x) > 1]
            
            validation_errors = []
            validation_warnings = []
            
            if not is_valid:
                validation_errors.append(
                    f"Total mapped amount (${total_mapped}) does not equal investment amount (${total_investment_amount}). "
                    f"Difference: ${difference}"
                )
            
            if duplicate_accounts:
                validation_errors.append(f"Duplicate MT5 accounts used: {duplicate_accounts}")
            
            if not mappings:
                validation_errors.append("No MT5 mappings found for investment")
            
            return {
                'is_valid': is_valid and not validation_errors,
                'total_investment_amount': total_investment_amount,
                'total_mapped_amount': total_mapped,
                'difference': difference,
                'mt5_accounts_used': mt5_accounts_used,
                'duplicate_accounts': duplicate_accounts,
                'validation_errors': validation_errors,
                'validation_warnings': validation_warnings,
                'mappings_count': len(mappings)
            }
            
        except Exception as e:
            logger.error(f"Error validating investment mappings for {investment_id}: {e}")
            raise
    
    async def update_mapping_allocation(
        self,
        mapping_id: str,
        new_amount: Decimal,
        update_notes: str,
        admin_user_id: str
    ) -> Optional[MT5InvestmentMapping]:
        """Update allocation amount for a mapping"""
        try:
            # Get current mapping
            current = await self.find_by_id(mapping_id)
            if not current:
                raise ValueError(f"Mapping {mapping_id} not found")
            
            old_amount = current.allocated_amount
            
            # Update with new amount and notes
            update_data = {
                'allocated_amount': float(new_amount),
                'allocation_notes': f"{current.allocation_notes}\n\n[UPDATE by {admin_user_id}]: {update_notes}"
            }
            
            result = await self.update_by_id(mapping_id, update_data)
            
            if result:
                # Log the change in audit trail
                pool_repo = MT5AccountPoolRepository(self.db)
                await pool_repo._log_audit_action(
                    action_type="mapping_update",
                    mt5_account_number=current.mt5_account_number,
                    investment_id=current.investment_id,
                    client_id=current.client_id,
                    old_values={'allocated_amount': float(old_amount)},
                    new_values={'allocated_amount': float(new_amount)},
                    admin_user_id=admin_user_id,
                    change_notes=update_notes
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error updating mapping allocation for {mapping_id}: {e}")
            raise