"""
MT5 Account Pool API Endpoints for FIDUS Investment Management Platform
Phase 1: Basic MT5 pool management and allocation endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import logging
from decimal import Decimal

from models.mt5_account_pool import (
    MT5AccountPoolCreate, MT5AccountPoolUpdate, MT5AccountPoolResponse,
    MT5InvestmentMappingCreate, MT5InvestmentMappingUpdate,
    DeallocationRequest, MT5AccountType, BrokerCode, MT5AccountPoolStatus
)
from repositories.mt5_account_pool_repository import (
    MT5AccountPoolRepository, MT5InvestmentMappingRepository
)
from config.database import get_database
# Import auth function from server.py (will be available when router is included)
# Note: get_current_admin_user will be available from server.py context
pass  # Auth function imported via router inclusion in server.py

logger = logging.getLogger(__name__)

# Create router for MT5 pool endpoints
mt5_pool_router = APIRouter(prefix="/api/mt5/pool", tags=["MT5 Account Pool"])

# Dependency to get repositories
async def get_pool_repository():
    db = await get_database()
    return MT5AccountPoolRepository(db)

async def get_mapping_repository():
    db = await get_database()
    return MT5InvestmentMappingRepository(db)

# ==================== MT5 ACCOUNT POOL MANAGEMENT ====================

@mt5_pool_router.post("/accounts", response_model=Dict[str, Any])
async def add_account_to_pool(
    account_data: MT5AccountPoolCreate,
    current_user: dict = Depends(get_current_admin_user),
    repository: MT5AccountPoolRepository = Depends(get_pool_repository)
):
    """
    🔒 ADD MT5 ACCOUNT TO POOL
    ⚠️ CRITICAL: Only enter INVESTOR PASSWORDS - Never trading passwords
    
    Admin-only endpoint to add MT5 accounts to the available pool
    """
    try:
        admin_user_id = current_user.get("user_id") or current_user.get("id")
        
        new_account = await repository.add_account_to_pool(account_data, admin_user_id)
        
        return {
            "success": True,
            "message": f"✅ MT5 account {account_data.mt5_account_number} added to pool successfully",
            "account": {
                "pool_id": new_account.pool_id,
                "mt5_account_number": new_account.mt5_account_number,
                "broker_name": new_account.broker_name,
                "account_type": new_account.account_type,
                "status": new_account.status,
                "created_by": admin_user_id
            },
            "warning": "⚠️ Ensure you entered the INVESTOR password (not trading password)"
        }
        
    except ValueError as ve:
        logger.error(f"Validation error adding account to pool: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error adding account to pool: {e}")
        raise HTTPException(status_code=500, detail="Failed to add MT5 account to pool")

@mt5_pool_router.get("/accounts/available", response_model=List[MT5AccountPoolResponse])
async def get_available_accounts(
    account_type: Optional[MT5AccountType] = None,
    broker: Optional[BrokerCode] = None,
    current_user: dict = Depends(get_current_admin_user),
    repository: MT5AccountPoolRepository = Depends(get_pool_repository)
):
    """Get all available MT5 accounts from pool"""
    try:
        accounts = await repository.get_available_accounts(account_type, broker)
        
        return [
            MT5AccountPoolResponse(
                pool_id=account.pool_id,
                mt5_account_number=account.mt5_account_number,
                broker_name=account.broker_name,
                account_type=account.account_type,
                status=account.status,
                mt5_server=account.mt5_server,
                notes=account.notes,
                is_allocated=False,
                allocated_to_client_id=None,
                allocation_date=None,
                created_at=account.created_at,
                updated_at=account.updated_at
            )
            for account in accounts
        ]
        
    except Exception as e:
        logger.error(f"Error getting available accounts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get available accounts")

@mt5_pool_router.get("/accounts/allocated", response_model=List[Dict[str, Any]])
async def get_allocated_accounts(
    client_id: Optional[str] = None,
    current_user: dict = Depends(get_current_admin_user),
    repository: MT5AccountPoolRepository = Depends(get_pool_repository)
):
    """Get all allocated MT5 accounts"""
    try:
        accounts = await repository.get_allocated_accounts(client_id)
        
        return [
            {
                "pool_id": account.pool_id,
                "mt5_account_number": account.mt5_account_number,
                "broker_name": account.broker_name,
                "account_type": account.account_type,
                "status": account.status,
                "allocated_to_client_id": account.allocated_to_client_id,
                "allocated_to_investment_id": account.allocated_to_investment_id,
                "allocated_amount": float(account.allocated_amount) if account.allocated_amount else 0,
                "allocation_date": account.allocation_date,
                "allocated_by_admin": account.allocated_by_admin,
                "notes": account.notes
            }
            for account in accounts
        ]
        
    except Exception as e:
        logger.error(f"Error getting allocated accounts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get allocated accounts")

@mt5_pool_router.get("/statistics", response_model=Dict[str, Any])
async def get_pool_statistics(
    current_user: dict = Depends(get_current_admin_user),
    repository: MT5AccountPoolRepository = Depends(get_pool_repository)
):
    """Get comprehensive MT5 pool statistics"""
    try:
        stats = await repository.get_pool_statistics()
        
        return {
            "success": True,
            "statistics": stats,
            "summary": {
                "total_accounts": stats['total_accounts'],
                "utilization_rate": round((stats['allocated'] / stats['total_accounts'] * 100), 2) if stats['total_accounts'] > 0 else 0,
                "available_accounts": stats['available'],
                "allocated_accounts": stats['allocated'],
                "pending_deallocations": stats['pending_deallocation']
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting pool statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get pool statistics")

@mt5_pool_router.post("/accounts/{mt5_account_number}/allocate")
async def allocate_account_to_client(
    mt5_account_number: int,
    allocation_data: Dict[str, Any],
    current_user: dict = Depends(get_current_admin_user),
    repository: MT5AccountPoolRepository = Depends(get_pool_repository)
):
    """
    Allocate MT5 account to a client investment
    ⚠️ MANDATORY: Allocation notes required explaining the allocation
    """
    try:
        admin_user_id = current_user.get("user_id") or current_user.get("id")
        
        # Validate required fields
        required_fields = ['client_id', 'investment_id', 'allocated_amount', 'allocation_notes']
        for field in required_fields:
            if field not in allocation_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Validate allocation notes
        allocation_notes = allocation_data['allocation_notes'].strip()
        if len(allocation_notes) < 10:
            raise HTTPException(
                status_code=400, 
                detail="⚠️ MANDATORY: Allocation notes must be at least 10 characters explaining the allocation reason"
            )
        
        # Check account availability
        exclusivity_check = await repository.check_account_exclusivity(mt5_account_number)
        if not exclusivity_check['is_available']:
            raise HTTPException(status_code=409, detail=exclusivity_check['reason'])
        
        # Perform allocation
        success = await repository.allocate_account_to_client(
            mt5_account_number=mt5_account_number,
            client_id=allocation_data['client_id'],
            investment_id=allocation_data['investment_id'],
            allocated_amount=Decimal(str(allocation_data['allocated_amount'])),
            admin_user_id=admin_user_id,
            allocation_notes=allocation_notes
        )
        
        if success:
            return {
                "success": True,
                "message": f"✅ MT5 account {mt5_account_number} allocated successfully",
                "allocation": {
                    "mt5_account_number": mt5_account_number,
                    "client_id": allocation_data['client_id'],
                    "investment_id": allocation_data['investment_id'],
                    "allocated_amount": allocation_data['allocated_amount'],
                    "allocated_by": admin_user_id,
                    "allocation_date": datetime.now(timezone.utc).isoformat()
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to allocate MT5 account")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error allocating MT5 account {mt5_account_number}: {e}")
        raise HTTPException(status_code=500, detail="Failed to allocate MT5 account")

@mt5_pool_router.post("/accounts/{mt5_account_number}/request-deallocation")
async def request_account_deallocation(
    mt5_account_number: int,
    deallocation_data: Dict[str, str],
    current_user: dict = Depends(get_current_admin_user),
    repository: MT5AccountPoolRepository = Depends(get_pool_repository)
):
    """
    Request deallocation of MT5 account
    ⚠️ MANDATORY: Detailed reason notes required
    """
    try:
        admin_user_id = current_user.get("user_id") or current_user.get("id")
        
        # Validate reason notes
        reason_notes = deallocation_data.get('reason_notes', '').strip()
        if len(reason_notes) < 10:
            raise HTTPException(
                status_code=400,
                detail="⚠️ MANDATORY: Deallocation reason must be at least 10 characters explaining why deallocation is needed"
            )
        
        request_id = await repository.request_deallocation(
            mt5_account_number=mt5_account_number,
            admin_user_id=admin_user_id,
            reason_notes=reason_notes
        )
        
        return {
            "success": True,
            "message": f"✅ Deallocation request created for MT5 account {mt5_account_number}",
            "request": {
                "request_id": request_id,
                "mt5_account_number": mt5_account_number,
                "requested_by": admin_user_id,
                "reason_notes": reason_notes,
                "status": "pending_approval",
                "next_step": "Awaiting approval from another admin"
            }
        }
        
    except ValueError as ve:
        logger.error(f"Validation error requesting deallocation: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error requesting deallocation for {mt5_account_number}: {e}")
        raise HTTPException(status_code=500, detail="Failed to request deallocation")

@mt5_pool_router.get("/deallocation-requests/pending")
async def get_pending_deallocation_requests(
    current_user: dict = Depends(get_current_admin_user),
    repository: MT5AccountPoolRepository = Depends(get_pool_repository)
):
    """Get all pending deallocation requests for admin approval"""
    try:
        requests = await repository.get_pending_deallocation_requests()
        
        return {
            "success": True,
            "pending_requests": requests,
            "count": len(requests),
            "message": f"Found {len(requests)} pending deallocation requests"
        }
        
    except Exception as e:
        logger.error(f"Error getting pending deallocation requests: {e}")
        raise HTTPException(status_code=500, detail="Failed to get pending requests")

@mt5_pool_router.post("/deallocation-requests/{request_id}/approve")
async def approve_deallocation_request(
    request_id: str,
    approval_data: Dict[str, str],
    current_user: dict = Depends(get_current_admin_user),
    repository: MT5AccountPoolRepository = Depends(get_pool_repository)
):
    """Approve a deallocation request"""
    try:
        admin_user_id = current_user.get("user_id") or current_user.get("id")
        approval_notes = approval_data.get('approval_notes', '')
        
        success = await repository.approve_deallocation(
            request_id=request_id,
            approving_admin_id=admin_user_id,
            approval_notes=approval_notes
        )
        
        if success:
            return {
                "success": True,
                "message": f"✅ Deallocation request {request_id} approved successfully",
                "approval": {
                    "request_id": request_id,
                    "approved_by": admin_user_id,
                    "approval_date": datetime.now(timezone.utc).isoformat(),
                    "approval_notes": approval_notes
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to approve deallocation")
            
    except ValueError as ve:
        logger.error(f"Validation error approving deallocation: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error approving deallocation request {request_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to approve deallocation")

# ==================== MT5 INVESTMENT MAPPING VALIDATION ====================

@mt5_pool_router.post("/validate-mappings")
async def validate_investment_mappings(
    validation_data: Dict[str, Any],
    current_user: dict = Depends(get_current_admin_user),
    repository: MT5InvestmentMappingRepository = Depends(get_mapping_repository)
):
    """
    Validate MT5 mappings for an investment
    Ensures MT5 allocations sum equals total investment amount
    """
    try:
        investment_id = validation_data.get('investment_id')
        total_investment_amount = Decimal(str(validation_data.get('total_investment_amount')))
        
        if not investment_id or not total_investment_amount:
            raise HTTPException(status_code=400, detail="investment_id and total_investment_amount are required")
        
        validation_result = await repository.validate_investment_mappings(
            investment_id=investment_id,
            total_investment_amount=total_investment_amount
        )
        
        return {
            "success": True,
            "validation_result": validation_result,
            "is_valid": validation_result['is_valid'],
            "message": "✅ Mappings are valid" if validation_result['is_valid'] else "❌ Mappings have errors",
            "summary": {
                "total_investment": float(validation_result['total_investment_amount']),
                "total_mapped": float(validation_result['total_mapped_amount']),
                "difference": float(validation_result['difference']),
                "mappings_count": validation_result['mappings_count']
            }
        }
        
    except Exception as e:
        logger.error(f"Error validating investment mappings: {e}")
        raise HTTPException(status_code=500, detail="Failed to validate mappings")

@mt5_pool_router.get("/accounts/{mt5_account_number}/exclusivity-check")
async def check_account_exclusivity(
    mt5_account_number: int,
    current_user: dict = Depends(get_current_admin_user),
    repository: MT5AccountPoolRepository = Depends(get_pool_repository)
):
    """Check if MT5 account is available for allocation (exclusivity check)"""
    try:
        result = await repository.check_account_exclusivity(mt5_account_number)
        
        return {
            "success": True,
            "mt5_account_number": mt5_account_number,
            "exclusivity_check": result,
            "message": "Available for allocation" if result['is_available'] else f"Not available: {result['reason']}"
        }
        
    except Exception as e:
        logger.error(f"Error checking account exclusivity for {mt5_account_number}: {e}")
        raise HTTPException(status_code=500, detail="Failed to check account exclusivity")

# ==================== HELPER ENDPOINTS ====================

@mt5_pool_router.get("/health")
async def mt5_pool_health_check():
    """Health check for MT5 pool management system"""
    try:
        return {
            "status": "healthy",
            "service": "MT5 Account Pool Management",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0 - Phase 1",
            "features": [
                "MT5 Account Pool Management",
                "Multiple Account Mapping Support", 
                "Allocation/Deallocation Workflow",
                "Account Exclusivity Enforcement",
                "Comprehensive Audit Trail",
                "⚠️ INVESTOR PASSWORD ONLY System"
            ]
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")