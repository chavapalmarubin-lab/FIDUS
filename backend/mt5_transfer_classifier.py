"""
MT5 Transfer Classification Service
Critical Fix: Distinguish between profit withdrawals and inter-account transfers

This module intelligently classifies MT5 balance operations to:
1. Count profit withdrawals (to separation account) for P&L
2. Ignore inter-account transfers (capital movements) for P&L
3. Track external deposits/withdrawals separately

Author: Emergent AI
Priority: CRITICAL
"""

import re
from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Account configuration
SEPARATION_ACCOUNT = 886528
TRADING_ACCOUNTS = [886557, 886066, 886602, 885822]
ALL_ACCOUNTS = TRADING_ACCOUNTS + [SEPARATION_ACCOUNT]


def classify_transfer(deal_comment: str, deal_amount: float, deal_direction: str = 'out') -> Dict[str, Any]:
    """
    Intelligently classify MT5 transfers based on comment field
    
    MT5 Comment Patterns:
    - "Transfer to #\"886528\"" → Profit withdrawal (COUNT for P&L)
    - "Transfer to #\"886066\"" → Inter-account funding (DON'T count)
    - "Transfer from #\"886557\"" → Received capital (DON'T count)
    - "Deposit" → External deposit (DON'T count)
    - "Withdrawal" → External withdrawal (DON'T count)
    
    Args:
        deal_comment: MT5 deal comment string
        deal_amount: Absolute amount of transfer
        deal_direction: 'out' for withdrawal, 'in' for deposit
    
    Returns:
        Dict containing:
        - type: Classification type
        - destination/source: Account number (if applicable)
        - amount: Transfer amount
        - include_in_pnl: Boolean - should this count toward P&L
        - description: Human-readable description
    """
    
    comment = deal_comment.lower().strip()
    amount = abs(deal_amount)
    
    # Pattern 1: Check for account number in comment
    # MT5 formats: 'Transfer to #"886528"' or 'Transfer from #"886066"'
    account_pattern = r'#["\']?(\d+)["\']?'
    match = re.search(account_pattern, comment)
    
    if match:
        target_account = int(match.group(1))
        
        # CASE 1: Transfer TO separation account = PROFIT WITHDRAWAL
        if target_account == SEPARATION_ACCOUNT and deal_direction == 'out':
            return {
                'type': 'profit_withdrawal',
                'destination': target_account,
                'amount': amount,
                'include_in_pnl': True,  # ✅ COUNT THIS
                'description': f'Profit withdrawal to separation account ({target_account})',
                'category': 'profit',
                'color': 'green'
            }
        
        # CASE 2: Transfer FROM separation account back to trading
        elif target_account == SEPARATION_ACCOUNT and deal_direction == 'in':
            return {
                'type': 'profit_return',
                'source': target_account,
                'amount': amount,
                'include_in_pnl': False,  # ❌ DON'T COUNT
                'description': f'Funds returned from separation account ({target_account})',
                'category': 'capital_movement',
                'color': 'blue'
            }
        
        # CASE 3: Transfer TO another trading account = INTER-ACCOUNT FUNDING
        elif target_account in TRADING_ACCOUNTS and deal_direction == 'out':
            return {
                'type': 'inter_account_transfer_out',
                'destination': target_account,
                'amount': amount,
                'include_in_pnl': False,  # ❌ DON'T COUNT
                'description': f'Capital transfer to trading account ({target_account})',
                'category': 'capital_movement',
                'color': 'blue'
            }
        
        # CASE 4: Transfer FROM another trading account = RECEIVED CAPITAL
        elif target_account in TRADING_ACCOUNTS and deal_direction == 'in':
            return {
                'type': 'inter_account_transfer_in',
                'source': target_account,
                'amount': amount,
                'include_in_pnl': False,  # ❌ DON'T COUNT
                'description': f'Received capital from trading account ({target_account})',
                'category': 'capital_movement',
                'color': 'blue'
            }
        
        # CASE 5: Unknown account number
        else:
            return {
                'type': 'unknown_account',
                'account': target_account,
                'amount': amount,
                'include_in_pnl': False,  # ❌ DON'T COUNT (until verified)
                'description': f'Transfer involving unknown account ({target_account})',
                'category': 'unknown',
                'color': 'yellow',
                'needs_review': True
            }
    
    # Pattern 2: External operations (no account number in comment)
    elif 'deposit' in comment:
        return {
            'type': 'external_deposit',
            'amount': amount,
            'include_in_pnl': False,  # ❌ DON'T COUNT (initial funding)
            'description': 'External deposit (initial funding or top-up)',
            'category': 'external',
            'color': 'gray'
        }
    
    elif 'withdrawal' in comment and 'transfer' not in comment:
        return {
            'type': 'external_withdrawal',
            'amount': amount,
            'include_in_pnl': False,  # ❌ DON'T COUNT (removed from broker)
            'description': 'External withdrawal (funds removed from broker)',
            'category': 'external',
            'color': 'gray'
        }
    
    # Pattern 3: Unknown transfer type - needs manual review
    else:
        logger.warning(f"Unknown transfer type: {deal_comment}")
        return {
            'type': 'unknown',
            'amount': amount,
            'include_in_pnl': False,  # ❌ DON'T COUNT (until reviewed)
            'description': f'Unknown transfer type: {deal_comment}',
            'category': 'unknown',
            'color': 'red',
            'needs_review': True,
            'original_comment': deal_comment
        }


def categorize_deal_history(deals: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Categorize all deals from MT5 history into profit withdrawals vs other transfers
    
    Args:
        deals: List of MT5 deal records with comment, amount, time
    
    Returns:
        Dict containing:
        - profit_withdrawals: List of profit withdrawal deals
        - inter_account_transfers: List of capital movement deals
        - external_operations: List of external deposits/withdrawals
        - unknown_operations: List of deals needing review
        - totals: Summary totals for each category
    """
    
    profit_withdrawals = []
    inter_account_transfers = []
    external_operations = []
    unknown_operations = []
    
    for deal in deals:
        # Determine direction (out vs in)
        direction = 'out' if deal['amount'] < 0 else 'in'
        
        # Classify the transfer
        classification = classify_transfer(
            deal['comment'],
            deal['amount'],
            direction
        )
        
        # Create enriched deal record
        enriched_deal = {
            **deal,
            'classification': classification,
            'direction': direction
        }
        
        # Sort into appropriate category
        if classification['type'] in ['profit_withdrawal', 'profit_return']:
            profit_withdrawals.append(enriched_deal)
            
        elif classification['type'] in ['inter_account_transfer_out', 'inter_account_transfer_in']:
            inter_account_transfers.append(enriched_deal)
            
        elif classification['type'] in ['external_deposit', 'external_withdrawal']:
            external_operations.append(enriched_deal)
            
        else:
            unknown_operations.append(enriched_deal)
    
    # Calculate totals
    # CRITICAL: Only profit withdrawals (to separation account) count for P&L
    total_profit_withdrawals = sum(
        abs(d['amount']) for d in profit_withdrawals
        if d['classification']['type'] == 'profit_withdrawal'  # Only withdrawals TO separation
    )
    
    total_profit_returns = sum(
        abs(d['amount']) for d in profit_withdrawals
        if d['classification']['type'] == 'profit_return'  # Returns FROM separation
    )
    
    net_profit_withdrawals = total_profit_withdrawals - total_profit_returns
    
    total_inter_account = sum(abs(d['amount']) for d in inter_account_transfers)
    total_external = sum(abs(d['amount']) for d in external_operations)
    
    return {
        # Categorized transfers
        'profit_withdrawals': profit_withdrawals,
        'inter_account_transfers': inter_account_transfers,
        'external_operations': external_operations,
        'unknown_operations': unknown_operations,
        
        # Totals for P&L calculation
        'totals': {
            'profit_withdrawals': total_profit_withdrawals,  # ✅ USE THIS for P&L
            'profit_returns': total_profit_returns,
            'net_profit_withdrawals': net_profit_withdrawals,  # withdrawals - returns
            'inter_account': total_inter_account,  # ❌ DON'T use for P&L
            'external': total_external,  # ❌ DON'T use for P&L
            'unknown': sum(abs(d['amount']) for d in unknown_operations)
        },
        
        # Counts
        'counts': {
            'profit_withdrawals': len(profit_withdrawals),
            'inter_account': len(inter_account_transfers),
            'external': len(external_operations),
            'unknown': len(unknown_operations),
            'total': len(deals)
        },
        
        # Flags
        'needs_review': len(unknown_operations) > 0,
        'has_inter_account_transfers': len(inter_account_transfers) > 0,
        'last_classified': datetime.utcnow().isoformat()
    }


def calculate_true_pnl(current_profit: float, deal_history_categorized: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate TRUE P&L including profit withdrawals
    
    CRITICAL FORMULA:
    True P&L = Current Displayed P&L + Net Profit Withdrawals (to separation account ONLY)
    
    DO NOT include:
    - Inter-account transfers (capital movements between trading accounts)
    - External deposits (initial funding)
    - External withdrawals (funds removed from broker)
    
    Args:
        current_profit: Current P&L displayed in MT5 (from open positions)
        deal_history_categorized: Output from categorize_deal_history()
    
    Returns:
        Dict with complete P&L breakdown
    """
    
    totals = deal_history_categorized['totals']
    
    # Net profit withdrawals = withdrawals - returns
    net_profit_withdrawals = totals['net_profit_withdrawals']
    
    # TRUE P&L = displayed + net profit withdrawals
    true_pnl = current_profit + net_profit_withdrawals
    
    return {
        'displayed_pnl': current_profit,
        'profit_withdrawals': totals['profit_withdrawals'],
        'profit_returns': totals['profit_returns'],
        'net_profit_withdrawals': net_profit_withdrawals,
        'true_pnl': true_pnl,
        
        # For reference (not counted)
        'inter_account_transfers': totals['inter_account'],
        'external_operations': totals['external'],
        
        # Calculation formula
        'calculation': f"{current_profit:.2f} (displayed) + {net_profit_withdrawals:.2f} (net profit withdrawals) = {true_pnl:.2f}",
        
        # Breakdown
        'breakdown': {
            'current_open_positions': current_profit,
            'historical_profits_withdrawn': net_profit_withdrawals,
            'capital_movements_ignored': totals['inter_account']
        },
        
        # Flags
        'has_withdrawals': totals['profit_withdrawals'] > 0,
        'has_inter_account': totals['inter_account'] > 0,
        'needs_review': deal_history_categorized['needs_review']
    }


# Test function with known data from screenshots
def test_classification():
    """
    Test with real data from MT5 screenshots
    """
    
    # Test Case 1: Account 886602 (from screenshot)
    print("=" * 80)
    print("TEST CASE 1: Account 886602")
    print("=" * 80)
    
    deals_886602 = [
        {
            'comment': 'Transfer to #"886528"',
            'amount': -646.52,
            'time': '2025-10-12 18:00:00'
        }
    ]
    
    result = categorize_deal_history(deals_886602)
    pnl = calculate_true_pnl(0.00, result)
    
    print(f"Total Withdrawals: ${result['totals']['profit_withdrawals']:.2f}")
    print(f"Inter-Account: ${result['totals']['inter_account']:.2f}")
    print(f"Displayed P&L: ${pnl['displayed_pnl']:.2f}")
    print(f"True P&L: ${pnl['true_pnl']:.2f}")
    print(f"Expected: $646.52 - {'PASS' if abs(pnl['true_pnl'] - 646.52) < 0.01 else 'FAIL'}")
    print()
    
    # Test Case 2: Account 886557 (complex case with inter-account transfer)
    print("=" * 80)
    print("TEST CASE 2: Account 886557 (Complex)")
    print("=" * 80)
    
    deals_886557 = [
        {'comment': 'Transfer to #"886528"', 'amount': -684.74, 'time': '2025-10-07 01:09:51'},
        {'comment': 'Transfer to #"886528"', 'amount': -662.99, 'time': '2025-10-08 03:18:17'},
        {'comment': 'Transfer to #"886528"', 'amount': -1354.85, 'time': '2025-10-09 00:29:06'},
        {'comment': 'Transfer to #"886528"', 'amount': -299.63, 'time': '2025-10-10 01:07:31'},
        {'comment': 'Transfer to #"886066"', 'amount': -10000.00, 'time': '2025-10-03 21:11:50'},  # Inter-account
    ]
    
    result = categorize_deal_history(deals_886557)
    pnl = calculate_true_pnl(3042.59, result)
    
    print(f"Total Withdrawals: ${result['totals']['profit_withdrawals']:.2f}")
    print(f"Inter-Account: ${result['totals']['inter_account']:.2f}")
    print(f"Displayed P&L: ${pnl['displayed_pnl']:.2f}")
    print(f"Net Profit Withdrawals: ${pnl['net_profit_withdrawals']:.2f}")
    print(f"True P&L: ${pnl['true_pnl']:.2f}")
    print(f"Expected Profit Withdrawals: $3,002.21 - {'PASS' if abs(result['totals']['profit_withdrawals'] - 3002.21) < 0.01 else 'FAIL'}")
    print(f"Expected True P&L: $6,044.80 - {'PASS' if abs(pnl['true_pnl'] - 6044.80) < 0.01 else 'FAIL'}")
    print()
    
    print("Classification Test: ", "✅ PASS" if result['counts']['inter_account'] == 1 else "❌ FAIL")
    print("Separation Test: ", "✅ PASS" if result['counts']['profit_withdrawals'] == 4 else "❌ FAIL")


if __name__ == "__main__":
    test_classification()
