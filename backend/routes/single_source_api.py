"""
Single Source of Truth API Endpoints
November 24, 2025 - SSOT Architecture Implementation

All endpoints query the single mt5_accounts collection (master source).
No duplicate data - all tabs derive from this one source.

Architecture:
- mt5_accounts = Single source of truth for ALL account data
- money_managers = Manager metadata ONLY (no account lists, no balances)
- All aggregations computed on-the-fly from mt5_accounts
- Join with money_managers ONLY for metadata (profile URLs, fees, etc.)
"""

from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2", tags=["Single Source of Truth V2"])


async def get_database():
    """Dependency to get MongoDB database"""
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    return client['fidus_production']


@router.get("/accounts/all")
async def get_all_accounts():
    """
    ACCOUNTS MANAGEMENT TAB - Get all 15 accounts (Single Source of Truth).
    
    This is the primary data source - all other endpoints derive from this.
    This endpoint powers the Accounts Management tab where admins can edit assignments.
    
    Returns all 15 accounts with complete metadata:
    - Platform (MT4/MT5)
    - Broker (MEXAtlantic/LUCRUM Capital) 
    - Fund assignments (editable)
    - Manager assignments (editable)
    - Status (editable)
    - Initial allocation (starting capital)
    - Real-time balances and positions (read-only, from VPS bridges)
    - Calculated P&L (balance - initial_allocation)
    """
    try:
        db = await get_database()
        
        # Get ALL accounts from mt5_accounts (Single Source of Truth)
        accounts = await db.mt5_accounts.find(
            {},
            {"_id": 0}
        ).sort("account", 1).to_list(100)
        
        # Calculate P&L for each account
        for account in accounts:
            initial_allocation = account.get('initial_allocation', 0)
            balance = account.get('balance', 0)
            account['pnl'] = balance - initial_allocation
        
        # Calculate totals
        total_balance = sum(acc.get('balance', 0) for acc in accounts)
        total_equity = sum(acc.get('equity', 0) for acc in accounts)
        active_accounts = [acc for acc in accounts if acc.get('status') == 'active']
        
        # Platform breakdown
        platforms = {}
        for acc in accounts:
            platform = acc.get('platform', 'MT5')
            if platform not in platforms:
                platforms[platform] = {'count': 0, 'balance': 0}
            platforms[platform]['count'] += 1
            platforms[platform]['balance'] += acc.get('balance', 0)
        
        # Broker breakdown
        brokers = {}
        for acc in accounts:
            broker = acc.get('broker', 'MEXAtlantic')
            if broker not in brokers:
                brokers[broker] = {'count': 0, 'balance': 0}
            brokers[broker]['count'] += 1
            brokers[broker]['balance'] += acc.get('balance', 0)
        
        return {
            "success": True,
            "accounts": accounts,
            "summary": {
                "total_accounts": len(accounts),
                "active_accounts": len(active_accounts),
                "total_balance": total_balance,
                "total_equity": total_equity,
                "platforms": platforms,
                "brokers": brokers,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting master accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/derived/fund-portfolio")
async def get_fund_portfolio_derived():
    """
    FUND PORTFOLIO TAB - Get fund portfolio data (derived from mt5_accounts).
    
    Groups mt5_accounts by fund_type and calculates aggregations.
    This is a READ-ONLY derived view - edits happen in Accounts Management tab.
    
    Returns:
    - Accounts grouped by fund_type (CORE, BALANCE, SEPARATION, etc.)
    - Total balance, equity per fund
    - Manager assignments per fund
    """
    try:
        db = await get_database()
        
        # Aggregate by fund type - derive from mt5_accounts
        pipeline = [
            {"$match": {"status": "active"}},  # Only active accounts
            {"$group": {
                "_id": "$fund_type",
                "account_count": {"$sum": 1},
                "accounts": {"$push": {
                    "account": "$account",
                    "platform": "$platform", 
                    "broker": "$broker",
                    "manager_name": "$manager_name",
                    "balance": "$balance",
                    "equity": "$equity",
                    "initial_allocation": "$initial_allocation"
                }},
                "total_allocation": {"$sum": "$initial_allocation"},
                "total_balance": {"$sum": "$balance"},
                "total_equity": {"$sum": "$equity"},
                "managers": {"$addToSet": "$manager_name"}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        funds = await db.mt5_accounts.aggregate(pipeline).to_list(100)
        
        # Format for frontend
        fund_data = {}
        total_allocation = 0
        total_aum = 0
        
        for fund in funds:
            fund_type = fund['_id']
            allocation = fund.get('total_allocation', 0)
            balance = fund['total_balance']
            pnl = balance - allocation
            
            fund_data[fund_type] = {
                "fund_type": fund_type,
                "account_count": fund['account_count'],
                "accounts": fund['accounts'],
                "total_allocation": allocation,
                "total_balance": balance,
                "total_equity": fund['total_equity'],
                "total_pnl": pnl,
                "managers": fund['managers'],
                "manager_count": len(fund['managers'])
            }
            total_allocation += allocation
            total_aum += balance
        
        total_pnl = total_aum - total_allocation
        
        return {
            "success": True,
            "funds": fund_data,
            "summary": {
                "total_allocation": total_allocation,
                "total_aum": total_aum,
                "total_pnl": total_pnl,
                "fund_count": len(fund_data),
                "total_accounts": sum(f['account_count'] for f in fund_data.values()),
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting fund portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/derived/money-managers")
async def get_money_managers_derived():
    """
    MONEY MANAGERS TAB - Get money managers data (derived from mt5_accounts + joined with money_managers).
    
    Groups mt5_accounts by manager_name and joins with money_managers collection for metadata.
    This is a READ-ONLY derived view - account assignments edited in Accounts Management tab.
    
    Returns:
    - Accounts grouped by manager_name
    - Total balance, equity per manager
    - Manager metadata (profile_url, rating_url, execution_method, fees) from money_managers collection
    """
    try:
        db = await get_database()
        
        # Aggregate by manager - derive from mt5_accounts + join money_managers for metadata
        pipeline = [
            {"$match": {"status": "active"}},  # Only active accounts
            {"$group": {
                "_id": "$manager_name",
                "account_count": {"$sum": 1},
                "accounts": {"$push": {
                    "account": "$account",
                    "platform": "$platform",
                    "broker": "$broker", 
                    "fund_type": "$fund_type",
                    "balance": "$balance",
                    "equity": "$equity",
                    "initial_allocation": "$initial_allocation",
                    "status": "$status"
                }},
                "total_allocation": {"$sum": "$initial_allocation"},
                "total_balance": {"$sum": "$balance"},
                "total_equity": {"$sum": "$equity"},
                "funds": {"$addToSet": "$fund_type"},
                "platforms": {"$addToSet": "$platform"},
                "brokers": {"$addToSet": "$broker"},
                "active_accounts": {
                    "$sum": {"$cond": [{"$eq": ["$status", "active"]}, 1, 0]}
                }
            }},
            # Join with money_managers collection for metadata ONLY
            {"$lookup": {
                "from": "money_managers",
                "localField": "_id",
                "foreignField": "name",
                "as": "manager_metadata"
            }},
            {"$unwind": {
                "path": "$manager_metadata",
                "preserveNullAndEmptyArrays": True  # Keep managers even if no metadata exists
            }},
            {"$sort": {"total_balance": -1}}
        ]
        
        managers = await db.mt5_accounts.aggregate(pipeline).to_list(100)
        
        # Format for frontend
        manager_data = {}
        total_balance = 0
        
        for manager in managers:
            manager_name = manager['_id']
            metadata = manager.get('manager_metadata', {})
            
            manager_data[manager_name] = {
                "manager_name": manager_name,
                "account_count": manager['account_count'],
                "active_accounts": manager['active_accounts'],
                "accounts": manager['accounts'],
                "total_balance": manager['total_balance'],
                "total_equity": manager['total_equity'],
                "funds": manager['funds'],
                "platforms": manager['platforms'], 
                "brokers": manager['brokers'],
                # Metadata from money_managers collection
                "profile_url": metadata.get('profile_url'),
                "rating_url": metadata.get('rating_url'),
                "execution_method": metadata.get('execution_method', 'Unknown'),
                "performance_fee_rate": metadata.get('performance_fee_rate', 0),
                "notes": metadata.get('notes', ''),
                "performance": {
                    "total_pnl": manager['total_equity'] - manager['total_balance'],
                    "roi_percentage": (manager['total_equity'] - manager['total_balance']) / manager['total_balance'] * 100 if manager['total_balance'] > 0 else 0
                }
            }
            total_balance += manager['total_balance']
        
        return {
            "success": True,
            "managers": manager_data,
            "summary": {
                "total_managers": len(manager_data),
                "active_managers": sum(1 for m in manager_data.values() if m['active_accounts'] > 0),
                "total_balance": total_balance,
                "avg_accounts_per_manager": sum(m['account_count'] for m in manager_data.values()) / len(manager_data) if manager_data else 0,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting money managers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/derived/cash-flow")
async def get_cash_flow_derived():
    """
    CASH FLOW TAB - Get cash flow data (derived from mt5_accounts).
    
    Returns all active accounts for cash flow analysis.
    This is a READ-ONLY derived view.
    """
    try:
        db = await get_database()
        
        # Get all active accounts
        accounts = await db.mt5_accounts.find(
            {"status": "active"},
            {"_id": 0}
        ).sort("account", 1).to_list(100)
        
        # Calculate cash flow metrics
        total_balance = sum(acc.get('balance', 0) for acc in accounts)
        total_equity = sum(acc.get('equity', 0) for acc in accounts)
        
        return {
            "success": True,
            "accounts": accounts,
            "summary": {
                "total_accounts": len(accounts),
                "total_balance": total_balance,
                "total_equity": total_equity,
                "total_pnl": total_equity - total_balance,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting cash flow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/derived/trading-analytics")
async def get_trading_analytics_derived():
    """
    TRADING ANALYTICS TAB - Get trading analytics (derived from mt5_accounts).
    
    Analyzes all active accounts for performance metrics.
    This is a READ-ONLY derived view.
    """
    try:
        db = await get_database()
        
        # Get all active accounts with positions data
        accounts = await db.mt5_accounts.find(
            {"status": "active"},
            {"_id": 0}
        ).to_list(100)
        
        # Calculate analytics
        total_balance = sum(acc.get('balance', 0) for acc in accounts)
        total_equity = sum(acc.get('equity', 0) for acc in accounts)
        total_margin = sum(acc.get('margin', 0) for acc in accounts)
        total_positions = sum(len(acc.get('positions', [])) for acc in accounts)
        
        # Performance by fund
        fund_performance = {}
        for acc in accounts:
            fund_type = acc.get('fund_type')
            if fund_type not in fund_performance:
                fund_performance[fund_type] = {
                    'accounts': 0, 'balance': 0, 'equity': 0, 'positions': 0
                }
            fund_performance[fund_type]['accounts'] += 1
            fund_performance[fund_type]['balance'] += acc.get('balance', 0)
            fund_performance[fund_type]['equity'] += acc.get('equity', 0) 
            fund_performance[fund_type]['positions'] += len(acc.get('positions', []))
        
        # Performance by manager
        manager_performance = {}
        for acc in accounts:
            manager = acc.get('manager_name')
            if manager not in manager_performance:
                manager_performance[manager] = {
                    'accounts': 0, 'balance': 0, 'equity': 0, 'positions': 0
                }
            manager_performance[manager]['accounts'] += 1
            manager_performance[manager]['balance'] += acc.get('balance', 0)
            manager_performance[manager]['equity'] += acc.get('equity', 0)
            manager_performance[manager]['positions'] += len(acc.get('positions', []))
        
        return {
            "success": True,
            "analytics": {
                "overview": {
                    "total_accounts": len(accounts),
                    "total_balance": total_balance,
                    "total_equity": total_equity,
                    "total_margin": total_margin,
                    "total_positions": total_positions,
                    "margin_utilization": (total_margin / total_equity * 100) if total_equity > 0 else 0,
                    "overall_pnl": total_equity - total_balance,
                    "overall_roi": ((total_equity - total_balance) / total_balance * 100) if total_balance > 0 else 0
                },
                "by_fund": fund_performance,
                "by_manager": manager_performance,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting trading analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/accounts/{account_number}/assign")
async def update_account_assignment(
    account_number: int,
    assignment_data: Dict[str, Any]
):
    """
    ACCOUNTS MANAGEMENT TAB - Update account assignment (fund_type, manager_name, status).
    
    This is the ONLY place where assignments are edited in the Single Source of Truth.
    All other tabs (Fund Portfolio, Money Managers, etc.) automatically reflect these changes.
    
    Allowed editable fields:
    - fund_type: CORE, BALANCE, SEPARATION, DYNAMIC, UNLIMITED
    - manager_name: Must match a manager in money_managers collection
    - status: active or inactive
    """
    try:
        db = await get_database()
        
        # Validate allowed fields
        allowed_fields = ['fund_type', 'manager_name', 'status']
        update_doc = {}
        
        for field, value in assignment_data.items():
            if field in allowed_fields:
                update_doc[field] = value
            else:
                raise HTTPException(status_code=400, detail=f"Field '{field}' is not allowed for assignment updates")
        
        if not update_doc:
            raise HTTPException(status_code=400, detail="No valid assignment fields provided")
        
        # Add timestamp
        update_doc['last_allocation_update'] = datetime.now(timezone.utc).isoformat()
        
        # Update the account in mt5_accounts (Single Source of Truth)
        result = await db.mt5_accounts.update_one(
            {"account": account_number},
            {"$set": update_doc}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail=f"Account {account_number} not found")
        
        # Get updated account
        updated_account = await db.mt5_accounts.find_one(
            {"account": account_number},
            {"_id": 0}
        )
        
        logger.info(f"✅ Account {account_number} assignment updated: {update_doc}")
        
        return {
            "success": True,
            "message": f"Account {account_number} assignment updated successfully",
            "account": updated_account,
            "updated_fields": list(update_doc.keys())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating account assignment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/ssot")
async def validate_ssot_architecture():
    """
    SSOT HEALTH CHECK - Validate that Single Source of Truth architecture is working correctly.
    
    Checks:
    1. All 15 accounts exist in mt5_accounts
    2. Required fields are populated
    3. money_managers collection has NO account lists (SSOT rule)
    4. Data completeness across platforms, brokers, funds, managers
    """
    try:
        db = await get_database()
        
        # Check 1: Count all accounts
        total_accounts = await db.mt5_accounts.count_documents({})
        
        # Check 2: Validate required fields
        accounts = await db.mt5_accounts.find({}).to_list(100)
        
        required_fields = ['account', 'platform', 'broker', 'fund_type', 'manager_name', 'status']
        validation_results = []
        
        for acc in accounts:
            account_validation = {"account": acc.get('account'), "issues": []}
            
            for field in required_fields:
                if not acc.get(field):
                    account_validation["issues"].append(f"Missing {field}")
            
            if account_validation["issues"]:
                validation_results.append(account_validation)
        
        # Check 3: Verify money_managers has NO account lists (SSOT violation)
        managers_with_accounts = await db.money_managers.count_documents({'assigned_accounts': {'$exists': True}})
        ssot_violation = managers_with_accounts > 0
        
        # Check 4: Data completeness
        platforms = await db.mt5_accounts.distinct("platform", {})
        brokers = await db.mt5_accounts.distinct("broker", {})
        funds = await db.mt5_accounts.distinct("fund_type", {})
        managers = await db.mt5_accounts.distinct("manager_name", {})
        
        return {
            "success": True,
            "ssot_architecture_status": "HEALTHY" if not ssot_violation and len(validation_results) == 0 else "ISSUES_DETECTED",
            "validation": {
                "total_accounts": total_accounts,
                "expected_accounts": 15,
                "accounts_valid": total_accounts == 15,
                "issues_found": len(validation_results),
                "accounts_with_issues": validation_results if validation_results else None,
                "ssot_violation": {
                    "violated": ssot_violation,
                    "managers_with_account_lists": managers_with_accounts,
                    "message": "❌ SSOT VIOLATION: money_managers should NOT store account lists" if ssot_violation else "✅ SSOT COMPLIANT: money_managers has metadata only"
                },
                "data_completeness": {
                    "platforms": sorted(platforms),
                    "platform_count": len(platforms),
                    "brokers": sorted(brokers),
                    "broker_count": len(brokers),
                    "fund_types": sorted(funds),
                    "fund_count": len(funds),
                    "managers": sorted(managers),
                    "manager_count": len(managers)
                }
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error validating SSOT architecture: {e}")
        raise HTTPException(status_code=500, detail=str(e))