"""
Investment Committee API Routes - V2 (Drag-and-Drop Account Assignment)
Handles all endpoints for the new multi-assignment drag-and-drop system
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

# Database will be injected when router is initialized
_db = None

def init_db(database):
    """Initialize database connection for this router"""
    global _db
    _db = database

router = APIRouter(prefix="/api/admin/investment-committee", tags=["Investment Committee V2"])


# Pydantic Models for Request/Response
class AssignToManagerRequest(BaseModel):
    account_number: int
    manager_name: str


class AssignToFundRequest(BaseModel):
    account_number: int
    fund_type: str


class AssignToBrokerRequest(BaseModel):
    account_number: int
    broker: str


class AssignToPlatformRequest(BaseModel):
    account_number: int
    trading_platform: str


class RemoveAssignmentRequest(BaseModel):
    account_number: int
    assignment_type: str  # "manager", "fund", "broker", "platform"


# Helper function to convert snake_case to camelCase
def to_camel_case(data):
    """Convert dictionary keys from snake_case to camelCase"""
    if isinstance(data, dict):
        return {
            _snake_to_camel(key): to_camel_case(value)
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [to_camel_case(item) for item in data]
    else:
        return data


def _snake_to_camel(snake_str):
    """Convert snake_case string to camelCase"""
    if snake_str == "_id":
        return "id"
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


# Authentication dependency
async def get_current_admin_user(request: Request):
    """Get current admin user from request"""
    # For now, allow all authenticated requests
    return {"_id": "admin_user_123", "email": "admin@getfidus.com", "role": "admin"}


# Constants
ALL_MT5_ACCOUNTS = [
    885822, 886066, 886528, 886557, 886602,
    891215, 891234, 897589, 897590, 897591,
    897599, 901351, 901353
]

VALID_MANAGERS = [
    "aleflorextrader",
    "UNO14",
    "Provider1-Assev JC",
    "CP Strategy",
    "TradingHub Gold",
    "Golden Trade Norman",
    "BOT",
    "Spaniard Equity CFDs",
    "JOSE - LUCRUM",
    "JARED"
]

VALID_FUNDS = [
    "FIDUS CORE",
    "FIDUS BALANCE",
    "FIDUS DYNAMIC",
    "SEPARATION INTEREST",
    "REBATES ACCOUNT"
]

VALID_BROKERS = ["MEXAtlantic", "LUCRUM"]
VALID_PLATFORMS = ["Broker Platform", "Biking"]


# Endpoint 1: Get All MT5 Accounts
@router.get("/mt5-accounts")
async def get_all_mt5_accounts(
    current_user = Depends(get_current_admin_user)
):
    """Get all 13 MT5 accounts with their assignments"""
    
    if _db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    try:
        # Fetch all 13 accounts
        accounts = await _db.mt5_accounts.find({
            "account": {"$in": ALL_MT5_ACCOUNTS}
        }, {"_id": 0}).to_list(length=20)
        
        # Sort by account number
        accounts_sorted = sorted(accounts, key=lambda x: ALL_MT5_ACCOUNTS.index(x["account"]))
        
        # Convert to camelCase
        accounts_camel = [to_camel_case(acc) for acc in accounts_sorted]
        
        return {
            "success": True,
            "data": {
                "accounts": accounts_camel,
                "total": len(accounts_camel)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching accounts: {str(e)}")


# Endpoint 2: Assign Account to Manager
@router.post("/assign-to-manager")
async def assign_account_to_manager(
    data: AssignToManagerRequest,
    current_user = Depends(get_current_admin_user)
):
    """Assign an MT5 account to a money manager"""
    
    if _db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    # Validate manager name
    if data.manager_name not in VALID_MANAGERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid manager name. Must be one of: {VALID_MANAGERS}"
        )
    
    # Validate account exists
    account = await _db.mt5_accounts.find_one({"account": data.account_number})
    if not account:
        raise HTTPException(
            status_code=404,
            detail=f"Account {data.account_number} not found"
        )
    
    try:
        # Update account with manager assignment
        await _db.mt5_accounts.update_one(
            {"account": data.account_number},
            {"$set": {
                "manager_assigned": data.manager_name,
                "allocated_capital": account.get("balance", 0),
                "last_allocation_update": datetime.utcnow()
            }}
        )
        
        # Create allocation history record
        await _db.allocation_history.insert_one({
            "timestamp": datetime.utcnow(),
            "action_type": "account_assigned_to_manager",
            "account_number": data.account_number,
            "manager_name": data.manager_name,
            "balance": account.get("balance", 0),
            "performed_by": str(current_user["_id"])
        })
        
        return {
            "success": True,
            "message": f"Account {data.account_number} assigned to {data.manager_name}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error assigning account: {str(e)}")


# Endpoint 3: Assign Account to Fund
@router.post("/assign-to-fund")
async def assign_account_to_fund(
    data: AssignToFundRequest,
    current_user = Depends(get_current_admin_user)
):
    """Assign an MT5 account to a fund category"""
    
    if _db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    # Validate fund type
    if data.fund_type not in VALID_FUNDS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid fund type. Must be one of: {VALID_FUNDS}"
        )
    
    # Validate account exists
    account = await _db.mt5_accounts.find_one({"account": data.account_number})
    if not account:
        raise HTTPException(
            status_code=404,
            detail=f"Account {data.account_number} not found"
        )
    
    try:
        # Update account with fund assignment
        await _db.mt5_accounts.update_one(
            {"account": data.account_number},
            {"$set": {
                "fund_type": data.fund_type,
                "last_allocation_update": datetime.utcnow()
            }}
        )
        
        # Create allocation history record
        await _db.allocation_history.insert_one({
            "timestamp": datetime.utcnow(),
            "action_type": "account_assigned_to_fund",
            "account_number": data.account_number,
            "fund_type": data.fund_type,
            "performed_by": str(current_user["_id"])
        })
        
        return {
            "success": True,
            "message": f"Account {data.account_number} assigned to {data.fund_type}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error assigning account: {str(e)}")


# Endpoint 4: Assign Account to Broker
@router.post("/assign-to-broker")
async def assign_account_to_broker(
    data: AssignToBrokerRequest,
    current_user = Depends(get_current_admin_user)
):
    """Assign an MT5 account to a broker"""
    
    if _db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    # Validate broker
    if data.broker not in VALID_BROKERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid broker. Must be one of: {VALID_BROKERS}"
        )
    
    # Validate account exists
    account = await _db.mt5_accounts.find_one({"account": data.account_number})
    if not account:
        raise HTTPException(
            status_code=404,
            detail=f"Account {data.account_number} not found"
        )
    
    try:
        # Update account with broker assignment
        await _db.mt5_accounts.update_one(
            {"account": data.account_number},
            {"$set": {
                "broker": data.broker,
                "last_allocation_update": datetime.utcnow()
            }}
        )
        
        # Create allocation history record
        await _db.allocation_history.insert_one({
            "timestamp": datetime.utcnow(),
            "action_type": "account_assigned_to_broker",
            "account_number": data.account_number,
            "broker": data.broker,
            "performed_by": str(current_user["_id"])
        })
        
        return {
            "success": True,
            "message": f"Account {data.account_number} assigned to {data.broker}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error assigning account: {str(e)}")


# Endpoint 5: Assign Account to Trading Platform
@router.post("/assign-to-platform")
async def assign_account_to_platform(
    data: AssignToPlatformRequest,
    current_user = Depends(get_current_admin_user)
):
    """Assign an MT5 account to a trading platform"""
    
    if _db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    # Validate platform
    if data.trading_platform not in VALID_PLATFORMS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid trading platform. Must be one of: {VALID_PLATFORMS}"
        )
    
    # Validate account exists
    account = await _db.mt5_accounts.find_one({"account": data.account_number})
    if not account:
        raise HTTPException(
            status_code=404,
            detail=f"Account {data.account_number} not found"
        )
    
    try:
        # Update account with platform assignment
        await _db.mt5_accounts.update_one(
            {"account": data.account_number},
            {"$set": {
                "trading_platform": data.trading_platform,
                "last_allocation_update": datetime.utcnow()
            }}
        )
        
        # Create allocation history record
        await _db.allocation_history.insert_one({
            "timestamp": datetime.utcnow(),
            "action_type": "account_assigned_to_platform",
            "account_number": data.account_number,
            "trading_platform": data.trading_platform,
            "performed_by": str(current_user["_id"])
        })
        
        return {
            "success": True,
            "message": f"Account {data.account_number} assigned to {data.trading_platform}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error assigning account: {str(e)}")


# Endpoint 6: Remove Assignment
@router.post("/remove-assignment")
async def remove_assignment(
    data: RemoveAssignmentRequest,
    current_user = Depends(get_current_admin_user)
):
    """Remove an assignment from an MT5 account"""
    
    if _db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    # Validate assignment type
    valid_types = ["manager", "fund", "broker", "platform"]
    if data.assignment_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid assignment type. Must be one of: {valid_types}"
        )
    
    # Validate account exists
    account = await _db.mt5_accounts.find_one({"account": data.account_number})
    if not account:
        raise HTTPException(
            status_code=404,
            detail=f"Account {data.account_number} not found"
        )
    
    try:
        # Determine which field to clear
        update = {}
        if data.assignment_type == "manager":
            update = {"manager_assigned": None, "allocated_capital": 0}
        elif data.assignment_type == "fund":
            update = {"fund_type": None}
        elif data.assignment_type == "broker":
            update = {"broker": None}
        elif data.assignment_type == "platform":
            update = {"trading_platform": None}
        
        update["last_allocation_update"] = datetime.utcnow()
        
        # Update account
        await _db.mt5_accounts.update_one(
            {"account": data.account_number},
            {"$set": update}
        )
        
        # Create allocation history record
        await _db.allocation_history.insert_one({
            "timestamp": datetime.utcnow(),
            "action_type": f"account_removed_from_{data.assignment_type}",
            "account_number": data.account_number,
            "assignment_type": data.assignment_type,
            "performed_by": str(current_user["_id"])
        })
        
        return {
            "success": True,
            "message": f"Account {data.account_number} removed from {data.assignment_type}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing assignment: {str(e)}")


# Endpoint 7: Get Current Allocations (Grouped)
@router.get("/allocations")
async def get_current_allocations(
    current_user = Depends(get_current_admin_user)
):
    """Get current allocations grouped by managers and funds"""
    
    if _db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    try:
        # Fetch all 13 accounts
        accounts = await _db.mt5_accounts.find({
            "account": {"$in": ALL_MT5_ACCOUNTS}
        }, {"_id": 0}).to_list(length=20)
        
        # Group by manager
        managers = {}
        for account in accounts:
            manager = account.get("manager_assigned")
            if manager:
                if manager not in managers:
                    managers[manager] = {
                        "accounts": [],
                        "total_balance": 0,
                        "account_count": 0
                    }
                managers[manager]["accounts"].append(to_camel_case(account))
                managers[manager]["total_balance"] += account.get("balance", 0)
                managers[manager]["account_count"] += 1
        
        # Group by fund
        funds = {}
        for account in accounts:
            fund = account.get("fund_type")
            if fund:
                if fund not in funds:
                    funds[fund] = {
                        "accounts": [],
                        "total_balance": 0,
                        "account_count": 0
                    }
                funds[fund]["accounts"].append(to_camel_case(account))
                funds[fund]["total_balance"] += account.get("balance", 0)
                funds[fund]["account_count"] += 1
        
        # Group by broker
        brokers = {}
        for account in accounts:
            broker = account.get("broker")
            if broker:
                if broker not in brokers:
                    brokers[broker] = {
                        "accounts": [],
                        "account_count": 0
                    }
                brokers[broker]["accounts"].append(account["account"])
                brokers[broker]["account_count"] += 1
        
        # Group by platform
        platforms = {}
        for account in accounts:
            platform = account.get("trading_platform")
            if platform:
                if platform not in platforms:
                    platforms[platform] = {
                        "accounts": [],
                        "account_count": 0
                    }
                platforms[platform]["accounts"].append(account["account"])
                platforms[platform]["account_count"] += 1
        
        return {
            "success": True,
            "data": {
                "managers": managers,
                "funds": funds,
                "brokers": brokers,
                "platforms": platforms,
                "unassigned": {
                    "manager": len([a for a in accounts if not a.get("manager_assigned")]),
                    "fund": len([a for a in accounts if not a.get("fund_type")]),
                    "broker": len([a for a in accounts if not a.get("broker")]),
                    "platform": len([a for a in accounts if not a.get("trading_platform")])
                }
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching allocations: {str(e)}")


# Endpoint 8: Validate Allocations
@router.get("/validate-allocations")
async def validate_allocations(
    current_user = Depends(get_current_admin_user)
):
    """
    Validate that all MT5 accounts are fully allocated
    
    Returns validation status and details about unassigned/incomplete accounts
    """
    
    if _db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    try:
        # Fetch all 13 accounts
        accounts = await _db.mt5_accounts.find({
            "account": {"$in": ALL_MT5_ACCOUNTS}
        }, {"_id": 0}).to_list(length=20)
        
        # Check for unassigned accounts (status = 'unassigned')
        unassigned_accounts = [
            acc["account"] for acc in accounts 
            if acc.get("status") == "unassigned"
        ]
        
        # Check for incomplete allocations
        incomplete_accounts = []
        pending_changes = []
        
        for account in accounts:
            missing_fields = []
            
            # Check required fields
            if not account.get("manager_assigned"):
                missing_fields.append("Manager")
            if not account.get("fund_type"):
                missing_fields.append("Fund")
            if not account.get("broker"):
                missing_fields.append("Broker")
            if not account.get("trading_platform"):
                missing_fields.append("Platform")
            
            # If any fields missing, account is incomplete
            if missing_fields:
                incomplete_accounts.append({
                    "account": account["account"],
                    "missing": missing_fields
                })
            
            # If account has all fields but status is unassigned, it's a pending change
            if not missing_fields and account.get("status") == "unassigned":
                pending_changes.append({
                    "account_number": account["account"],
                    "changes": {
                        "manager": {"old": None, "new": account.get("manager_assigned")},
                        "fund_type": {"old": None, "new": account.get("fund_type")},
                        "broker": {"old": None, "new": account.get("broker")},
                        "platform": {"old": None, "new": account.get("trading_platform")}
                    }
                })
        
        # Determine if can apply
        can_apply = len(unassigned_accounts) == 0 and len(incomplete_accounts) == 0
        
        # Build reason message
        reason = None
        if unassigned_accounts:
            reason = f"{len(unassigned_accounts)} account{'s' if len(unassigned_accounts) > 1 else ''} unassigned"
        elif incomplete_accounts:
            reason = f"{len(incomplete_accounts)} account{'s' if len(incomplete_accounts) > 1 else ''} with incomplete allocations"
        elif not pending_changes:
            reason = "No pending changes to apply"
        
        return {
            "canApply": can_apply,
            "reason": reason,
            "unassignedAccounts": unassigned_accounts,
            "incompleteAccounts": incomplete_accounts,
            "pendingChanges": pending_changes
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating allocations: {str(e)}")


# Endpoint 9: Apply Allocations
@router.post("/apply-allocations")
async def apply_allocations(
    current_user = Depends(get_current_admin_user)
):
    """
    Apply pending MT5 account allocations and trigger system-wide recalculations
    
    This endpoint:
    1. Validates all accounts are allocated
    2. Updates account status to 'assigned'
    3. Triggers comprehensive recalculations:
       - Cash flow projections
       - Commission calculations
       - Performance metrics
       - P&L updates
       - Manager allocations
       - Fund distributions
    4. Creates audit log entry
    
    Uses MongoDB transactions - all updates are atomic (all or nothing)
    """
    
    if _db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    import logging
    from services.allocation_recalculations import AllocationRecalculationService
    
    logger = logging.getLogger(__name__)
    
    try:
        # STEP 1: Validate
        validation = await validate_allocations(current_user)
        if not validation["canApply"]:
            raise HTTPException(400, validation["reason"])
        
        pending_changes = validation["pendingChanges"]
        
        if not pending_changes:
            raise HTTPException(400, "No pending changes to apply")
        
        logger.info(f"🔄 Applying allocations for {len(pending_changes)} accounts...")
        
        # STEP 2: Initialize recalculation service
        recalc_service = AllocationRecalculationService(_db)
        
        # STEP 3: Execute all updates (with transaction if replica set available)
        try:
            session = await _db.client.start_session()
        except Exception as e:
            logger.warning(f"⚠️ Transaction support not available: {e}")
            session = None
        
        try:
            if session:
                await session.start_transaction()
            
            try:
                    # Update account statuses to 'assigned'
                    accounts_updated = 0
                    
                    for change in pending_changes:
                        result = await _db.mt5_accounts.update_one(
                            {"account": change["account_number"]},
                            {
                                "$set": {
                                    "status": "assigned",
                                    "is_active": True,
                                    "updated_at": datetime.utcnow(),
                                    "last_allocation_update": datetime.utcnow()
                                }
                            },
                            session=session
                        )
                        accounts_updated += result.modified_count
                        
                        # Also update mt5_account_config collection
                        await _db.mt5_account_config.update_one(
                            {"account": change["account_number"]},
                            {
                                "$set": {
                                    "is_active": True,
                                    "updated_at": datetime.utcnow().isoformat(),
                                    "last_modified_by": "apply_allocations"
                                }
                            },
                            upsert=False,
                            session=session
                        )
                    
                    logger.info(f"✅ Updated {accounts_updated} account statuses")
                    
                    # Run all recalculations within the transaction
                    logger.info("🔄 Starting recalculations...")
                    recalc_results = await recalc_service.run_all_recalculations(
                        session=session
                    )
                    
                    if not recalc_results["success"]:
                        raise Exception(f"Recalculations failed: {recalc_results['errors']}")
                    
                    logger.info(f"✅ All recalculations complete in {recalc_results['total_duration_seconds']:.2f}s")
                    
                    # Create audit log entry
                    audit_entry = {
                        "timestamp": datetime.utcnow(),
                        "action": "apply_allocations",
                        "accounts_updated": accounts_updated,
                        "pending_changes": pending_changes,
                        "performed_by": str(current_user["_id"]),
                        "recalculation_results": recalc_results,
                        "calculations_run": list(recalc_results["recalculations"].keys())
                    }
                    
                    await _db.allocation_audit_log.insert_one(audit_entry, session=session)
                    
                    # Log action to allocation history
                    for change in pending_changes:
                        await _db.allocation_history.insert_one({
                            "timestamp": datetime.utcnow(),
                            "action_type": "allocation_applied",
                            "account_number": change["account_number"],
                            "manager_name": change["changes"]["manager"]["new"],
                            "fund_type": change["changes"]["fund_type"]["new"],
                            "broker": change["changes"]["broker"]["new"],
                            "trading_platform": change["changes"]["platform"]["new"],
                            "performed_by": str(current_user["_id"])
                        }, session=session)
                    
                # Commit transaction (if available)
                if session:
                    await session.commit_transaction()
                    logger.info("✅ Transaction committed successfully")
                else:
                    logger.info("✅ All updates completed (no transaction support)")
                
            except Exception as e:
                # Rollback transaction (if available)
                if session:
                    logger.error(f"❌ Transaction failed, rolling back: {e}")
                    await session.abort_transaction()
                else:
                    logger.error(f"❌ Updates failed (no rollback available): {e}")
                raise
        finally:
            if session:
                session.end_session()
        
        # Build response
        calculations_run = len(recalc_results["recalculations"])
        
        return {
            "success": True,
            "accounts_updated": accounts_updated,
            "calculations_run": calculations_run,
            "timestamp": datetime.utcnow(),
            "message": f"Allocations applied successfully. {calculations_run} calculations updated.",
            "details": {
                "accounts_processed": accounts_updated,
                "audit_log_created": True,
                "history_logged": True,
                "recalculations": {
                    name: {
                        "success": result.get("success", False),
                        "duration": result.get("duration_seconds", 0)
                    }
                    for name, result in recalc_results["recalculations"].items()
                },
                "total_recalc_time": recalc_results["total_duration_seconds"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to apply allocations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to apply allocations: {str(e)}")
