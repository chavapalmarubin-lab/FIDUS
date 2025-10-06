"""
MT5 Account Management API Endpoints for FIDUS Investment Management Platform
Refactored Phase 1: Just-in-time MT5 account creation during investment allocation
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import logging
import uuid
from decimal import Decimal

from models.mt5_account_pool import (
    MT5AccountPoolCreate, MT5AccountPoolUpdate, MT5AccountPoolResponse,
    MT5InvestmentMappingCreate, MT5InvestmentMappingUpdate,
    DeallocationRequest, MT5AccountType, BrokerCode, MT5AccountPoolStatus
)
from models.investment_with_mt5 import (
    InvestmentWithMT5Create, MT5AccountAvailabilityCheck, MT5AccountAvailabilityResult,
    InvestmentCreationResult, InvestmentMT5Summary, MT5AccountInput
)
from repositories.mt5_account_pool_repository import (
    MT5AccountPoolRepository, MT5InvestmentMappingRepository
)
from config.database import get_database
# Import authentication utilities
import jwt
import os

# JWT Configuration
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'fidus-production-secret-2025-secure-key')
JWT_ALGORITHM = 'HS256'

def verify_jwt_token(token: str) -> dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_admin_user(request: Request) -> dict:
    """Get current admin user from JWT token"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No token provided")
    
    token = auth_header.split(" ")[1]
    payload = verify_jwt_token(token)
    
    # Check if user is admin
    if payload.get("type") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return payload

logger = logging.getLogger(__name__)

# Create router for MT5 management endpoints (prefix will be added when including in main router)
mt5_pool_router = APIRouter(tags=["MT5 Account Management"])

# Dependency to get repositories
async def get_pool_repository():
    db = await get_database()
    return MT5AccountPoolRepository(db)

async def get_mapping_repository():
    db = await get_database()
    return MT5InvestmentMappingRepository(db)

# ==================== MT5 ACCOUNT POOL MANAGEMENT ====================

@mt5_pool_router.get("/test")
async def test_endpoint():
    """Simple test endpoint to verify router is working"""
    return {"success": True, "message": "MT5 Pool router is working", "timestamp": datetime.now(timezone.utc).isoformat()}

@mt5_pool_router.post("/validate-account-availability")
async def validate_account_availability(
    availability_check: Dict[str, int],
    current_user: dict = Depends(get_current_admin_user),
    repository: MT5AccountPoolRepository = Depends(get_pool_repository)
):
    """
    Check if MT5 account is available for allocation during investment creation
    ⚠️ Real-time validation to prevent conflicts
    """
    try:
        mt5_account_number = availability_check.get('mt5_account_number')
        if not mt5_account_number:
            raise HTTPException(status_code=400, detail="mt5_account_number is required")
        
        # Check if account already exists and is allocated
        existing_account = await repository.get_account_by_number(mt5_account_number)
        
        if existing_account and existing_account.status == "allocated":
            return {
                "mt5_account_number": mt5_account_number,
                "is_available": False,
                "reason": f"⚠️ MT5 Account {mt5_account_number} is already allocated to {existing_account.allocated_to_client_id}",
                "current_allocation": {
                    "client_id": existing_account.allocated_to_client_id,
                    "investment_id": existing_account.allocated_to_investment_id,
                    "allocated_amount": float(existing_account.allocated_amount) if existing_account.allocated_amount else 0,
                    "allocation_date": existing_account.allocation_date
                }
            }
        else:
            return {
                "mt5_account_number": mt5_account_number,
                "is_available": True,
                "reason": "✅ Account available for allocation",
                "current_allocation": None
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating account availability: {e}")
        raise HTTPException(status_code=500, detail="Failed to validate account availability")

@mt5_pool_router.post("/create-investment-with-mt5", response_model=InvestmentCreationResult)
async def create_investment_with_mt5_accounts(
    investment_data: InvestmentWithMT5Create,
    current_user: dict = Depends(get_current_admin_user),
    pool_repository: MT5AccountPoolRepository = Depends(get_pool_repository),
    mapping_repository: MT5InvestmentMappingRepository = Depends(get_mapping_repository)
):
    """
    🚀 CREATE INVESTMENT WITH MT5 ACCOUNTS (JUST-IN-TIME)
    ⚠️ CRITICAL: Only enter INVESTOR PASSWORDS for all MT5 accounts
    
    Creates investment and associated MT5 accounts in one operation
    """
    try:
        admin_user_id = current_user.get("user_id") or current_user.get("id")
        
        # Step 1: Validate all MT5 accounts are available
        unavailable_accounts = []
        for mt5_account in investment_data.mt5_accounts:
            existing = await pool_repository.get_account_by_number(mt5_account.mt5_account_number)
            if existing and existing.status == "allocated":
                unavailable_accounts.append({
                    'account': mt5_account.mt5_account_number,
                    'allocated_to': existing.allocated_to_client_id
                })
        
        # Also check separation accounts
        if investment_data.interest_separation_account:
            existing = await pool_repository.get_account_by_number(investment_data.interest_separation_account.mt5_account_number)
            if existing and existing.status == "allocated":
                unavailable_accounts.append({
                    'account': investment_data.interest_separation_account.mt5_account_number,
                    'allocated_to': existing.allocated_to_client_id
                })
        
        if investment_data.gains_separation_account:
            existing = await pool_repository.get_account_by_number(investment_data.gains_separation_account.mt5_account_number)
            if existing and existing.status == "allocated":
                unavailable_accounts.append({
                    'account': investment_data.gains_separation_account.mt5_account_number,
                    'allocated_to': existing.allocated_to_client_id
                })
        
        if unavailable_accounts:
            conflicts = [f"MT5 Account {acc['account']} (allocated to {acc['allocated_to']})" for acc in unavailable_accounts]
            raise HTTPException(
                status_code=409, 
                detail=f"⚠️ The following MT5 accounts are already allocated: {', '.join(conflicts)}. Please use different accounts."
            )
        
        # Step 2: Generate investment ID
        investment_id = f"inv_{uuid.uuid4().hex[:16]}"
        
        # Step 3: Create MT5 account records
        created_mt5_accounts = []
        created_separation_accounts = []
        
        # Create investment MT5 accounts
        for mt5_account in investment_data.mt5_accounts:
            account_data = MT5AccountPoolCreate(
                mt5_account_number=mt5_account.mt5_account_number,
                broker_name=mt5_account.broker_name,
                account_type=MT5AccountType.INVESTMENT,
                investor_password=mt5_account.investor_password,
                mt5_server=mt5_account.mt5_server,
                notes=f"Investment allocation: {mt5_account.allocation_notes}"
            )
            
            # Create the MT5 account record
            new_account = await pool_repository.add_account_to_pool(account_data, admin_user_id)
            
            # Immediately allocate it
            await pool_repository.allocate_account_to_client(
                mt5_account_number=mt5_account.mt5_account_number,
                client_id=investment_data.client_id,
                investment_id=investment_id,
                allocated_amount=mt5_account.allocated_amount,
                admin_user_id=admin_user_id,
                allocation_notes=mt5_account.allocation_notes
            )
            
            created_mt5_accounts.append({
                'mt5_account_number': mt5_account.mt5_account_number,
                'broker_name': mt5_account.broker_name.value,
                'allocated_amount': float(mt5_account.allocated_amount),
                'allocation_notes': mt5_account.allocation_notes
            })
        
        # Create separation accounts if provided
        for sep_account, account_type in [
            (investment_data.interest_separation_account, MT5AccountType.INTEREST_SEPARATION),
            (investment_data.gains_separation_account, MT5AccountType.GAINS_SEPARATION)
        ]:
            if sep_account:
                sep_data = MT5AccountPoolCreate(
                    mt5_account_number=sep_account.mt5_account_number,
                    broker_name=sep_account.broker_name,
                    account_type=account_type,
                    investor_password=sep_account.investor_password,
                    mt5_server=sep_account.mt5_server,
                    notes=f"{account_type.value} account for {investment_data.client_id}: {sep_account.notes or 'Separation tracking'}"
                )
                
                await pool_repository.add_account_to_pool(sep_data, admin_user_id)
                await pool_repository.allocate_account_to_client(
                    mt5_account_number=sep_account.mt5_account_number,
                    client_id=investment_data.client_id,
                    investment_id=investment_id,
                    allocated_amount=Decimal(0),  # Separation accounts don't have allocation amounts
                    admin_user_id=admin_user_id,
                    allocation_notes=f"{account_type.value} tracking for investment {investment_id}"
                )
                
                created_separation_accounts.append({
                    'mt5_account_number': sep_account.mt5_account_number,
                    'broker_name': sep_account.broker_name.value,
                    'account_type': account_type.value,
                    'notes': sep_account.notes
                })
        
        # Step 4: Create investment mappings
        mapping_creates = []
        for mt5_account in investment_data.mt5_accounts:
            mapping_creates.append(MT5InvestmentMappingCreate(
                investment_id=investment_id,
                mt5_account_number=mt5_account.mt5_account_number,
                allocated_amount=mt5_account.allocated_amount,
                allocation_notes=mt5_account.allocation_notes
            ))
        
        await mapping_repository.create_mappings_for_investment(
            investment_id=investment_id,
            client_id=investment_data.client_id,
            fund_code=investment_data.fund_code.value,
            mappings=mapping_creates,
            admin_user_id=admin_user_id
        )
        
        # Step 5: Prepare response
        total_allocated = sum(acc.allocated_amount for acc in investment_data.mt5_accounts)
        
        return InvestmentCreationResult(
            success=True,
            investment_id=investment_id,
            message=f"✅ Investment {investment_id} created successfully with {len(created_mt5_accounts)} MT5 accounts",
            investment={
                'investment_id': investment_id,
                'client_id': investment_data.client_id,
                'fund_code': investment_data.fund_code.value,
                'principal_amount': float(investment_data.principal_amount),
                'currency': investment_data.currency.value,
                'investment_date': investment_data.investment_date,
                'creation_notes': investment_data.creation_notes
            },
            mt5_accounts_created=created_mt5_accounts,
            separation_accounts_created=created_separation_accounts,
            total_investment_amount=investment_data.principal_amount,
            total_allocated_amount=total_allocated,
            allocation_is_valid=abs(total_allocated - investment_data.principal_amount) < Decimal('0.01'),
            created_by_admin=admin_user_id,
            creation_timestamp=datetime.now(timezone.utc)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating investment with MT5 accounts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create investment: {str(e)}")

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