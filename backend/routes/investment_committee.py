"""
Investment Committee API Routes
Handles all endpoints for dynamic fund allocation management
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from ..mongodb_integration import mongodb_manager
from ..services.allocation_service import AllocationService
from ..validation.field_registry import transform_to_api_format


router = APIRouter(prefix="/api/admin/investment-committee", tags=["Investment Committee"])


# Pydantic Models for Request/Response
class AccountDistribution(BaseModel):
    accountNumber: int
    amount: float
    type: str = "master"


class AllocationPreviewRequest(BaseModel):
    managerName: str
    newAllocation: float
    accountDistribution: list[AccountDistribution]


class AllocateRequest(BaseModel):
    managerName: str
    amount: float
    accountDistribution: list[AccountDistribution]
    notes: str = ""


class RemoveManagerRequest(BaseModel):
    actualBalance: float
    expectedAllocation: float
    lossHandling: str = "absorb_loss"
    notes: str


class AdjustCapitalRequest(BaseModel):
    newTotalCapital: float
    reason: str
    notes: str = ""


# Import the authentication dependency from server
# We'll use a simplified version that checks for admin role
async def get_current_admin_user(request: Request):
    """Get current admin user from request"""
    # For now, allow all authenticated requests
    # TODO: Add proper admin role check when auth system is integrated
    return {"_id": "admin_user_123", "email": "admin@getfidus.com", "role": "admin"}


# Initialize allocation service
def get_allocation_service():
    db = mongodb_manager.get_db()
    return AllocationService(db)


@router.get("/funds/{fund_type}/allocation")
async def get_fund_allocation(
    fund_type: str
):
    """Get current allocation state for a fund"""
    
    # Validate fund type
    valid_funds = ["BALANCE", "CORE", "DYNAMIC", "SEPARATION"]
    if fund_type not in valid_funds:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid fund type. Must be one of: {valid_funds}"
        )
    
    # Get service
    service = get_allocation_service()
    
    # Get from service
    fund_state = await service.get_fund_state(fund_type)
    
    if not fund_state:
        # Initialize if doesn't exist
        fund_state = await service.initialize_fund(fund_type)
    
    # Convert to camelCase for API response
    return {
        "success": True,
        "data": transform_to_api_format(fund_state)
    }


@router.post("/funds/{fund_type}/preview")
async def preview_allocation(
    fund_type: str,
    data: AllocationPreviewRequest
):
    """Preview allocation change without applying it"""
    
    service = get_allocation_service()
    
    # Convert account distribution to snake_case
    account_dist = [
        {
            "account_number": acc.accountNumber,
            "amount": acc.amount,
            "type": acc.type
        }
        for acc in data.accountDistribution
    ]
    
    # Validate and preview
    result = await service.preview_allocation(
        fund_type=fund_type,
        manager_name=data.managerName,
        new_allocation=data.newAllocation,
        account_distribution=account_dist
    )
    
    return {
        "success": True,
        "isValid": result["is_valid"],
        "impact": transform_to_api_format(result["impact"]),
        "warnings": result.get("warnings", []),
        "errors": result.get("errors", [])
    }


@router.post("/funds/{fund_type}/allocate")
async def apply_allocation(
    fund_type: str,
    data: AllocateRequest
):
    """Apply allocation to a manager"""
    
    service = get_allocation_service()
    
    # Convert account distribution
    account_dist = [
        {
            "account_number": acc.accountNumber,
            "amount": acc.amount,
            "type": acc.type
        }
        for acc in data.accountDistribution
    ]
    
    try:
        # Apply allocation
        result = await service.apply_allocation(
            fund_type=fund_type,
            manager_name=data.managerName,
            amount=data.amount,
            account_distribution=account_dist,
            notes=data.notes,
            user_id="admin_user_123"
        )
        
        return {
            "success": True,
            "message": "Allocation applied successfully",
            "data": transform_to_api_format(result)
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error applying allocation: {str(e)}")


@router.delete("/funds/{fund_type}/managers/{manager_name}")
async def remove_manager_allocation(
    fund_type: str,
    manager_name: str,
    data: RemoveManagerRequest
):
    """Remove manager and return capital to pool"""
    
    service = get_allocation_service()
    
    try:
        result = await service.remove_manager(
            fund_type=fund_type,
            manager_name=manager_name,
            actual_balance=data.actualBalance,
            expected_allocation=data.expectedAllocation,
            loss_handling=data.lossHandling,
            notes=data.notes,
            user_id="admin_user_123"
        )
        
        return {
            "success": True,
            "message": "Manager removed and capital returned to pool",
            "data": transform_to_api_format(result)
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing manager: {str(e)}")


@router.put("/funds/{fund_type}/capital")
async def adjust_fund_capital(
    fund_type: str,
    data: AdjustCapitalRequest,
    current_user = Depends(get_current_admin_user)
):
    """Adjust fund total capital"""
    
    service = get_allocation_service()
    
    try:
        result = await service.adjust_fund_capital(
            fund_type=fund_type,
            new_total_capital=data.newTotalCapital,
            reason=data.reason,
            notes=data.notes,
            user_id=str(current_user["_id"])
        )
        
        return {
            "success": True,
            "message": "Fund capital adjusted successfully",
            "data": transform_to_api_format(result)
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adjusting capital: {str(e)}")


@router.get("/funds/{fund_type}/history")
async def get_allocation_history(
    fund_type: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    manager_name: Optional[str] = None,
    action_type: Optional[str] = None,
    limit: int = 50,
    current_user = Depends(get_current_admin_user)
):
    """Get allocation history"""
    
    service = get_allocation_service()
    
    history = await service.get_history(
        fund_type=fund_type,
        start_date=start_date,
        end_date=end_date,
        manager_name=manager_name,
        action_type=action_type,
        limit=limit
    )
    
    return {
        "success": True,
        "data": {
            "history": [transform_to_api_format(h) for h in history],
            "pagination": {
                "total": len(history),
                "limit": limit,
                "offset": 0
            }
        }
    }


@router.get("/managers/available")
async def get_available_managers(
    fund_type: Optional[str] = None,
    current_user = Depends(get_current_admin_user)
):
    """Get available managers"""
    
    service = get_allocation_service()
    
    managers = await service.get_available_managers(fund_type)
    
    return {
        "success": True,
        "data": {
            "managers": [transform_to_api_format(m) for m in managers]
        }
    }


@router.get("/managers/{manager_name}/actual-balance")
async def get_manager_actual_balance(
    manager_name: str,
    current_user = Depends(get_current_admin_user)
):
    """Get actual balance from MT5 accounts for a manager"""
    
    service = get_allocation_service()
    
    actual_balance = await service.get_manager_actual_balance(manager_name)
    
    return {
        "success": True,
        "data": {
            "managerName": manager_name,
            "actualBalance": actual_balance
        }
    }
