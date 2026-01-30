"""
FIDUS CENTRAL CALCULATION SERVICE - SINGLE SOURCE OF TRUTH (SSOT)
==================================================================

This is the ONLY place where financial calculations happen.
Every endpoint and every tab uses these functions.

Architecture: SYSTEM_MASTER.md Section 9.3
Data Source: mt5_accounts collection (MT5/MT4 real-time data)
"""

from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# DECIMAL128 CONVERSION - USE EVERYWHERE
# ============================================================================

def convert_decimal128(value):
    """
    Single place for Decimal128 conversion.
    Prevents float * Decimal128 errors across the entire application.
    """
    if value is None:
        return 0.0
    if hasattr(value, 'to_decimal'):
        return float(value.to_decimal())
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


# ============================================================================
# CORE CALCULATIONS - SINGLE SOURCE OF TRUTH
# ============================================================================

async def get_total_equity(db):
    """
    SSOT: Total Equity
    Sum of equity from ALL active MT5/MT4 accounts in the allocation
    
    Used by: Cash Flow, Fund Portfolio, Money Managers, Trading Analytics
    """
    try:
        # CRITICAL: Only include accounts that are part of the active allocation
        # These are the accounts from the FIDUS Allocation Summary
        active_allocation_accounts = [891215, 20043, 2209, 917105, 917106, 2205, 2206]
        
        # Query for these specific accounts
        accounts = await db.mt5_accounts.find({
            "account": {"$in": active_allocation_accounts}
        }, {"_id": 0}).to_list(length=None)
        
        total = sum(convert_decimal128(acc.get('equity', 0)) for acc in accounts)
        logger.info(f"💰 Total Equity (SSOT): ${total:,.2f} from {len(accounts)} active allocation accounts")
        return total
    except Exception as e:
        logger.error(f"Error calculating total equity: {e}")
        return 0.0


async def get_client_money(db):
    """
    SSOT: Client Money (Client Obligations)
    Sum of principal from ALL active investments
    
    Used by: Cash Flow, Investment, Fund Portfolio
    """
    try:
        # CRITICAL: Exclude _id to prevent ObjectId serialization errors
        investments = await db.investments.find({"status": "active"}, {"_id": 0}).to_list(length=None)
        
        total = sum(convert_decimal128(inv.get('principal_amount', 0)) for inv in investments)
        logger.info(f"💰 Client Money (SSOT): ${total:,.2f} from {len(investments)} active investments")
        return total
    except Exception as e:
        logger.error(f"Error calculating client money: {e}")
        return 0.0


async def get_fund_revenue(db):
    """
    SSOT: Fund Revenue
    Formula: Total Equity - Client Money
    
    This is the ONLY place this calculation happens.
    Used by: Cash Flow, Fund Portfolio
    """
    equity = await get_total_equity(db)
    client_money = await get_client_money(db)
    revenue = equity - client_money
    
    logger.info(f"💰 Fund Revenue (SSOT): ${revenue:,.2f} = ${equity:,.2f} - ${client_money:,.2f}")
    return revenue


async def get_account_pnl(db, account_number):
    """
    SSOT: Single Account P&L
    Formula: Current Equity - Initial Allocation
    
    Used by: Trading Analytics, Account Management
    """
    try:
        account = await db.mt5_accounts.find_one({"account": account_number})
        if not account:
            return 0.0
        
        equity = convert_decimal128(account.get('equity', 0))
        allocation = convert_decimal128(account.get('initial_allocation', 0))
        pnl = equity - allocation
        
        return pnl
    except Exception as e:
        logger.error(f"Error calculating account P&L for {account_number}: {e}")
        return 0.0


async def get_manager_pnl(db, manager_name):
    """
    SSOT: Manager P&L
    Formula: Sum of (equity - allocation) for all manager's accounts
    
    Used by: Money Managers, Fund Portfolio
    """
    try:
        # CRITICAL: Exclude _id to prevent ObjectId serialization errors
        accounts = await db.mt5_accounts.find({"manager_name": manager_name}, {"_id": 0}).to_list(length=None)
        
        total_pnl = 0.0
        for acc in accounts:
            equity = convert_decimal128(acc.get('equity', 0))
            allocation = convert_decimal128(acc.get('initial_allocation', 0))
            total_pnl += (equity - allocation)
        
        logger.info(f"💰 Manager {manager_name} P&L (SSOT): ${total_pnl:,.2f} from {len(accounts)} accounts")
        return total_pnl
    except Exception as e:
        logger.error(f"Error calculating manager P&L for {manager_name}: {e}")
        return 0.0


async def get_fund_pnl(db, fund_type):
    """
    SSOT: Fund Type P&L
    Formula: Sum of (equity - allocation) for all fund's accounts
    
    Used by: Fund Portfolio, Cash Flow
    """
    try:
        # CRITICAL: Exclude _id to prevent ObjectId serialization errors
        accounts = await db.mt5_accounts.find({"fund_type": fund_type}, {"_id": 0}).to_list(length=None)
        
        total_pnl = 0.0
        for acc in accounts:
            equity = convert_decimal128(acc.get('equity', 0))
            allocation = convert_decimal128(acc.get('initial_allocation', 0))
            total_pnl += (equity - allocation)
        
        logger.info(f"💰 Fund {fund_type} P&L (SSOT): ${total_pnl:,.2f} from {len(accounts)} accounts")
        return total_pnl
    except Exception as e:
        logger.error(f"Error calculating fund P&L for {fund_type}: {e}")
        return 0.0


async def get_all_accounts_summary(db):
    """
    SSOT: All Accounts Summary
    Returns complete account data with P&L calculations
    
    Used by: Account Management, Investment Committee, Fund Portfolio
    """
    try:
        # CRITICAL: Only include accounts from the active allocation
        active_allocation_accounts = [891215, 20043, 2209, 917105, 917106, 2205, 2206]
        
        accounts = await db.mt5_accounts.find({
            "account": {"$in": active_allocation_accounts}
        }, {"_id": 0}).to_list(length=None)
        
        summary = []
        total_equity = 0.0
        total_balance = 0.0
        total_allocation = 0.0
        
        for acc in accounts:
            equity = convert_decimal128(acc.get('equity', 0))
            balance = convert_decimal128(acc.get('balance', 0))
            allocation = convert_decimal128(acc.get('initial_allocation', 0))
            pnl = equity - allocation
            
            total_equity += equity
            total_balance += balance
            total_allocation += allocation
            
            summary.append({
                'account': str(acc.get('account', '')),
                'manager_name': acc.get('manager_name', ''),
                'fund_type': acc.get('fund_type', ''),
                'broker': acc.get('broker', ''),
                'platform': acc.get('platform', 'MT5'),
                'equity': round(equity, 2),
                'balance': round(balance, 2),
                'initial_allocation': round(allocation, 2),
                'pnl': round(pnl, 2),
                'status': acc.get('status', 'active')
            })
        
        return {
            'accounts': summary,
            'totals': {
                'total_equity': round(total_equity, 2),
                'total_balance': round(total_balance, 2),
                'total_allocation': round(total_allocation, 2),
                'total_pnl': round(total_equity - total_allocation, 2),
                'total_accounts': len(summary)
            }
        }
    except Exception as e:
        logger.error(f"Error getting accounts summary: {e}")
        return {'accounts': [], 'totals': {}}


async def get_all_investments_summary(db):
    """
    SSOT: All Investments Summary
    Returns complete investment data grouped by client
    
    Used by: Investment Tab, Cash Flow
    """
    try:
        # CRITICAL: Exclude _id to prevent ObjectId serialization errors
        investments = await db.investments.find({"status": "active"}, {"_id": 0}).to_list(length=None)
        
        clients = {}
        total_aum = 0.0
        
        for inv in investments:
            client_id = inv.get('client_id')
            client_name = inv.get('client_name', 'Unknown')
            principal = convert_decimal128(inv.get('principal_amount', 0))
            
            total_aum += principal
            
            if client_id not in clients:
                clients[client_id] = {
                    'client_id': client_id,
                    'client_name': client_name,
                    'investments': [],
                    'total_invested': 0.0
                }
            
            clients[client_id]['investments'].append({
                'investment_id': inv.get('investment_id'),
                'fund_type': inv.get('fund_type', ''),
                'principal_amount': round(principal, 2),
                'status': inv.get('status', 'active')
            })
            clients[client_id]['total_invested'] += principal
        
        return {
            'clients': list(clients.values()),
            'totals': {
                'total_aum': round(total_aum, 2),
                'total_clients': len(clients),
                'total_investments': len(investments)
            }
        }
    except Exception as e:
        logger.error(f"Error getting investments summary: {e}")
        return {'clients': [], 'totals': {}}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def verify_ssot_consistency(db):
    """
    Verify that calculations are consistent across the system.
    Run this in tests to ensure SSOT is working.
    """
    equity = await get_total_equity(db)
    client_money = await get_client_money(db)
    revenue = await get_fund_revenue(db)
    
    calculated_revenue = equity - client_money
    
    if abs(revenue - calculated_revenue) > 0.01:
        logger.error(f"SSOT INCONSISTENCY: Revenue mismatch {revenue} vs {calculated_revenue}")
        return False
    
    logger.info("✅ SSOT Verification Passed")
    return True
