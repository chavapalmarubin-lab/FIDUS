"""
MT5 Account Configuration Management API
Backend endpoints for managing MT5 account configurations
NO MOCK DATA - All data from MongoDB
"""

from fastapi import APIRouter, HTTPException, Depends, status, Request
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

# Create router (prefix /admin/mt5/config - /api is added by main api_router)
router = APIRouter(prefix="/admin/mt5/config", tags=["MT5 Admin Config"])

# ============================================
# Import auth function from server
# ============================================

# This will be set during initialization
get_current_admin_user = None

def init_auth(auth_func):
    """Initialize authentication function"""
    global get_current_admin_user
    get_current_admin_user = auth_func

# ============================================
# DATA MODELS
# ============================================

class MT5AccountConfig(BaseModel):
    """Model for creating a new MT5 account configuration"""
    account: int = Field(..., description="MT5 account number", gt=0)
    password: str = Field(..., description="MT5 account password", min_length=1)
    name: str = Field(..., description="Account name/description", min_length=1)
    server: str = Field(default="MEXAtlantic-Real", description="MT5 server")
    fund_type: str = Field(..., description="Fund type: BALANCE, CORE, or SEPARATION")
    target_amount: float = Field(..., description="Target amount", ge=0)
    is_active: bool = Field(default=True, description="Whether account is active")
    
    @validator('fund_type')
    def validate_fund_type(cls, v):
        allowed = ['BALANCE', 'CORE', 'SEPARATION']
        if v not in allowed:
            raise ValueError(f'fund_type must be one of: {", ".join(allowed)}')
        return v

class MT5AccountUpdate(BaseModel):
    """Model for updating an existing MT5 account configuration"""
    name: Optional[str] = Field(None, description="Account name/description", min_length=1)
    fund_type: Optional[str] = Field(None, description="Fund type: BALANCE, CORE, or SEPARATION")
    target_amount: Optional[float] = Field(None, description="Target amount", ge=0)
    is_active: Optional[bool] = Field(None, description="Whether account is active")
    password: Optional[str] = Field(None, description="MT5 account password (leave blank to keep current)", min_length=1)
    
    @validator('fund_type')
    def validate_fund_type(cls, v):
        if v is not None:
            allowed = ['BALANCE', 'CORE', 'SEPARATION']
            if v not in allowed:
                raise ValueError(f'fund_type must be one of: {", ".join(allowed)}')
        return v

class MT5AccountResponse(BaseModel):
    """Response model for MT5 account configuration (without password)"""
    account: int
    name: str
    server: str
    fund_type: str
    target_amount: float
    is_active: bool
    created_at: str
    updated_at: str
    created_by: str
    last_modified_by: str

# ============================================
# DEPENDENCY: Require Admin Authentication
# ============================================

def require_admin(request: Request):
    """
    Require admin authentication for all endpoints
    Uses the get_current_admin_user function from server.py
    """
    if get_current_admin_user is None:
        raise RuntimeException("Authentication not initialized")
    
    return get_current_admin_user(request)

# ============================================
# Database instance - imported from server
# ============================================

db = None

def init_db(database):
    """Initialize database instance"""
    global db
    db = database

def get_db():
    """Get database instance"""
    global db
    if db is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return db

# ============================================
# ENDPOINTS
# ============================================

@router.get("/accounts", response_model=dict)
async def get_all_mt5_config(current_user: dict = Depends(require_admin)):
    """
    Get all MT5 account configurations
    Returns accounts from mt5_account_config collection
    NO MOCK DATA - all data from MongoDB
    """
    try:
        db = get_db()
        
        # Get all accounts, exclude password field
        accounts = await db.mt5_account_config.find(
            {},
            {"password": 0}
        ).sort("account", 1).to_list(length=100)
        
        # Convert ObjectId to string
        for acc in accounts:
            acc["_id"] = str(acc["_id"])
        
        logger.info(f"Retrieved {len(accounts)} MT5 account configurations")
        
        return {
            "success": True,
            "count": len(accounts),
            "accounts": accounts
        }
        
    except Exception as e:
        logger.error(f"Error fetching MT5 account configs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch accounts: {str(e)}"
        )

@router.post("/accounts", status_code=status.HTTP_201_CREATED)
async def add_mt5_account(
    account: MT5AccountConfig,
    current_user: dict = Depends(require_admin)
):
    """
    Add a new MT5 account to the configuration
    The VPS bridge will automatically pick it up on next reload (every 50 min)
    NO MOCK DATA - saves real config to MongoDB
    """
    try:
        db = get_db()
        
        # Validate account doesn't already exist
        existing = await db.mt5_account_config.find_one({"account": account.account})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Account {account.account} already exists"
            )
        
        # Create account config document
        now = datetime.now(timezone.utc).isoformat()
        account_doc = account.dict()
        account_doc["created_at"] = now
        account_doc["updated_at"] = now
        account_doc["created_by"] = current_user["email"]
        account_doc["last_modified_by"] = current_user["email"]
        
        # Insert into MongoDB
        result = await db.mt5_account_config.insert_one(account_doc)
        
        logger.info(f"Added new MT5 account config: {account.account} - {account.name}")
        
        return {
            "success": True,
            "message": "Account added successfully. Will be synced by VPS bridge within 50 minutes.",
            "account_id": str(result.inserted_id),
            "account": account.account
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding MT5 account config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add account: {str(e)}"
        )

@router.put("/accounts/{account_number}")
async def update_mt5_account(
    account_number: int,
    updates: MT5AccountUpdate,
    current_user: dict = Depends(require_admin)
):
    """
    Update an existing MT5 account configuration
    Changes take effect on next VPS bridge reload (every 50 min)
    NO MOCK DATA - updates real config in MongoDB
    """
    try:
        db = get_db()
        
        # Check if account exists
        existing = await db.mt5_account_config.find_one({"account": account_number})
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account {account_number} not found"
            )
        
        # Build update document with only provided fields
        update_doc = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "last_modified_by": current_user["email"]
        }
        
        # Add non-null fields from request
        update_data = updates.dict(exclude_unset=True, exclude_none=True)
        update_doc.update(update_data)
        
        # Update in MongoDB
        result = await db.mt5_account_config.update_one(
            {"account": account_number},
            {"$set": update_doc}
        )
        
        logger.info(f"Updated MT5 account config: {account_number}")
        
        return {
            "success": True,
            "message": "Account updated successfully. Changes will take effect within 50 minutes.",
            "modified_count": result.modified_count,
            "account": account_number
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating MT5 account config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update account: {str(e)}"
        )

@router.delete("/accounts/{account_number}")
async def delete_mt5_account(
    account_number: int,
    current_user: dict = Depends(require_admin)
):
    """
    Remove an MT5 account from configuration (soft delete - sets is_active=false)
    The VPS bridge will stop syncing this account on next reload
    NO MOCK DATA - updates real config in MongoDB
    """
    try:
        db = get_db()
        
        # Soft delete (set is_active = False)
        result = await db.mt5_account_config.update_one(
            {"account": account_number},
            {"$set": {
                "is_active": False,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "last_modified_by": current_user["email"]
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account {account_number} not found"
            )
        
        logger.info(f"Deactivated MT5 account config: {account_number}")
        
        return {
            "success": True,
            "message": "Account deactivated successfully. Will stop syncing within 50 minutes.",
            "account": account_number
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating MT5 account config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate account: {str(e)}"
        )

@router.post("/accounts/{account_number}/activate")
async def activate_mt5_account(
    account_number: int,
    current_user: dict = Depends(require_admin)
):
    """
    Reactivate a previously deactivated MT5 account
    NO MOCK DATA - updates real config in MongoDB
    """
    try:
        db = get_db()
        
        # Set is_active = True
        result = await db.mt5_account_config.update_one(
            {"account": account_number},
            {"$set": {
                "is_active": True,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "last_modified_by": current_user["email"]
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account {account_number} not found"
            )
        
        logger.info(f"Activated MT5 account config: {account_number}")
        
        return {
            "success": True,
            "message": "Account activated successfully. Will resume syncing within 50 minutes.",
            "account": account_number
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating MT5 account config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate account: {str(e)}"
        )

@router.get("/accounts/{account_number}")
async def get_mt5_account(
    account_number: int,
    current_user: dict = Depends(require_admin)
):
    """
    Get a specific MT5 account configuration
    NO MOCK DATA - data from MongoDB
    """
    try:
        db = get_db()
        
        # Get account, exclude password
        account = await db.mt5_account_config.find_one(
            {"account": account_number},
            {"password": 0}
        )
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account {account_number} not found"
            )
        
        # Convert ObjectId to string
        account["_id"] = str(account["_id"])
        
        return {
            "success": True,
            "account": account
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching MT5 account config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch account: {str(e)}"
        )
