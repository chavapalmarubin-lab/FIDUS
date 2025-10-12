#!/usr/bin/env python3
"""
Fund Performance Calculator
Calculates weighted performance for funds with multiple MT5 accounts
"""

import logging
from typing import Dict, List, Any
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


async def calculate_fund_weighted_performance(db, fund_code: str) -> Dict[str, Any]:
    """
    Calculate weighted performance for a fund with multiple accounts
    
    Args:
        db: MongoDB database instance
        fund_code: Fund code (CORE, BALANCE, DYNAMIC, UNLIMITED)
        
    Returns:
        Dictionary with weighted performance data
    """
    try:
        logger.info(f"📊 Calculating weighted performance for {fund_code} fund")
        
        # Get all MT5 accounts for this fund
        mt5_cursor = db.mt5_accounts.find({
            'fund_code': fund_code
        })
        accounts = await mt5_cursor.to_list(length=None)
        
        if not accounts:
            logger.warning(f"No accounts found for {fund_code} fund")
            return {
                'success': True,
                'fund_code': fund_code,
                'total_aum': 0,
                'weighted_return': 0,
                'account_count': 0,
                'accounts': [],
                'message': 'No accounts allocated yet'
            }
        
        # Calculate total AUM (initial deposits)
        total_aum = sum(acc.get('balance', 0) for acc in accounts)
        
        # Calculate weighted return
        weighted_return = 0
        total_true_pnl = 0
        account_details = []
        
        for acc in accounts:
            account_num = acc.get('account')
            initial_deposit = acc.get('balance', 0)  # Current balance as allocation
            current_equity = acc.get('equity', 0)
            true_pnl = acc.get('true_pnl', 0)
            profit_withdrawals = acc.get('profit_withdrawals', 0)
            
            # Skip if no allocation
            if initial_deposit == 0:
                continue
            
            # Individual return percentage
            return_pct = (true_pnl / initial_deposit) * 100 if initial_deposit > 0 else 0
            
            # Weight in fund
            weight = (initial_deposit / total_aum) * 100 if total_aum > 0 else 0
            
            # Contribution to fund performance
            contribution = (initial_deposit / total_aum) * return_pct if total_aum > 0 else 0
            weighted_return += contribution
            total_true_pnl += true_pnl
            
            # Determine status
            if return_pct > 5:
                status = 'excellent'
            elif return_pct > 0:
                status = 'positive'
            elif return_pct > -2:
                status = 'underperforming'
            else:
                status = 'poor'
            
            # Get manager name from account or use default
            manager_name = acc.get('manager_name', acc.get('broker', 'Unknown Manager'))
            
            account_details.append({
                'account_id': account_num,
                'account_name': f"{account_num} - {fund_code}",
                'manager_name': manager_name,
                'initial_deposit': round(initial_deposit, 2),
                'current_equity': round(current_equity, 2),
                'profit_withdrawals': round(profit_withdrawals, 2),
                'true_pnl': round(true_pnl, 2),
                'return_pct': round(return_pct, 2),
                'weight': round(weight, 2),
                'contribution': round(contribution, 2),
                'status': status
            })
        
        # Sort by contribution (highest to lowest)
        account_details.sort(key=lambda x: x['contribution'], reverse=True)
        
        # Find best/worst performers
        best_performer = max(account_details, key=lambda x: x['return_pct']) if account_details else None
        worst_performer = min(account_details, key=lambda x: x['return_pct']) if account_details else None
        largest_contributor = max(account_details, key=lambda x: abs(x['contribution'])) if account_details else None
        
        logger.info(f"✅ {fund_code} Fund: Weighted Return = {weighted_return:.2f}%, Total TRUE P&L = ${total_true_pnl:,.2f}")
        
        return {
            'success': True,
            'fund_code': fund_code,
            'total_aum': round(total_aum, 2),
            'weighted_return': round(weighted_return, 2),
            'total_true_pnl': round(total_true_pnl, 2),
            'account_count': len(account_details),
            'accounts': account_details,
            'best_performer': {
                'account_id': best_performer['account_id'],
                'return_pct': best_performer['return_pct']
            } if best_performer else None,
            'worst_performer': {
                'account_id': worst_performer['account_id'],
                'return_pct': worst_performer['return_pct']
            } if worst_performer else None,
            'largest_contributor': {
                'account_id': largest_contributor['account_id'],
                'contribution': largest_contributor['contribution']
            } if largest_contributor else None,
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error calculating weighted performance for {fund_code}: {str(e)}")
        return {
            'success': False,
            'fund_code': fund_code,
            'error': str(e),
            'total_aum': 0,
            'weighted_return': 0,
            'account_count': 0,
            'accounts': []
        }


async def get_all_funds_performance(db) -> Dict[str, Any]:
    """
    Get weighted performance for all funds
    
    Args:
        db: MongoDB database instance
        
    Returns:
        Dictionary with all funds' performance data
    """
    try:
        fund_codes = ['CORE', 'BALANCE', 'DYNAMIC', 'UNLIMITED']
        funds_performance = {}
        
        for fund_code in fund_codes:
            performance = await calculate_fund_weighted_performance(db, fund_code)
            funds_performance[fund_code] = performance
        
        # Calculate portfolio totals
        total_aum = sum(f.get('total_aum', 0) for f in funds_performance.values())
        total_true_pnl = sum(f.get('total_true_pnl', 0) for f in funds_performance.values())
        
        # Portfolio weighted return
        portfolio_weighted_return = 0
        for fund_code, fund_data in funds_performance.items():
            if total_aum > 0:
                fund_weight = fund_data.get('total_aum', 0) / total_aum
                fund_return = fund_data.get('weighted_return', 0)
                portfolio_weighted_return += fund_weight * fund_return
        
        return {
            'success': True,
            'funds': funds_performance,
            'portfolio_totals': {
                'total_aum': round(total_aum, 2),
                'total_true_pnl': round(total_true_pnl, 2),
                'weighted_return': round(portfolio_weighted_return, 2)
            },
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting all funds performance: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
