"""
Field Transformation Utilities for API Responses
Standardizes field names between MongoDB (snake_case) and API/Frontend (camelCase)

Author: FIDUS Investment Management
Date: October 31, 2025
"""

from typing import Dict, Any, Optional
from datetime import datetime


def transform_mt5_account(db_account: Dict[str, Any]) -> Dict[str, Any]:
    """Transform MongoDB MT5 account to API format (camelCase)
    
    STANDARD FIELDS (as per FIELD_STANDARDS.md):
    - balance (not accountBalance)
    - equity (not accountEquity)  
    - profit (not profitLoss)
    - truePnl (calculated true P&L)
    """
    from bson.decimal128 import Decimal128
    
    def to_float(val):
        if val is None:
            return 0.0
        if isinstance(val, Decimal128):
            return float(val.to_decimal())
        return float(val)
    
    return {
        "accountNumber": db_account.get("account"),
        "balance": to_float(db_account.get("balance")),
        "equity": to_float(db_account.get("equity")),
        "profit": to_float(db_account.get("profit")),
        "truePnl": to_float(db_account.get("true_pnl")),
        "displayedPnl": to_float(db_account.get("displayed_pnl")),
        "usedMargin": to_float(db_account.get("margin")),
        "freeMargin": to_float(db_account.get("margin_free")),
        "marginLevel": to_float(db_account.get("margin_level")),
        "leverage": db_account.get("leverage"),
        "currency": db_account.get("currency"),
        "server": db_account.get("server"),
        "broker": db_account.get("broker"),
        "fundType": db_account.get("fund_type"),
        "fundCode": db_account.get("fund_code"),
        "initialAllocation": to_float(db_account.get("initial_allocation")),
        "clientName": db_account.get("client_name"),
        "clientId": db_account.get("client_id"),
        "manager": db_account.get("manager"),
        "lastUpdate": db_account.get("updated_at").isoformat() if db_account.get("updated_at") else None
    }


def transform_investment(db_investment: Dict[str, Any]) -> Dict[str, Any]:
    """Transform MongoDB investment to API format"""
    from bson.decimal128 import Decimal128
    
    def to_float(val):
        if val is None:
            return 0.0
        if isinstance(val, Decimal128):
            return float(val.to_decimal())
        return float(val)
    
    return {
        "investmentId": str(db_investment.get("_id")),
        "clientId": db_investment.get("client_id"),
        "principalAmount": to_float(db_investment.get("principal_amount")),
        "currentValue": to_float(db_investment.get("current_value")),
        "totalInterestEarned": to_float(db_investment.get("total_interest_earned")),
        "depositDate": db_investment.get("deposit_date").isoformat() if db_investment.get("deposit_date") else None,
        "interestStartDate": db_investment.get("interest_start_date").isoformat() if db_investment.get("interest_start_date") else None,
        "fundCode": db_investment.get("fund_code"),
        "status": db_investment.get("status"),
        "referredBy": db_investment.get("referred_by"),
        "referredByName": db_investment.get("referred_by_name")
    }


def transform_client(db_client: Dict[str, Any]) -> Dict[str, Any]:
    """Transform MongoDB client to API format"""
    return {
        "clientId": str(db_client.get("_id")),
        "email": db_client.get("email"),
        "firstName": db_client.get("first_name"),
        "lastName": db_client.get("last_name"),
        "fullName": db_client.get("full_name"),
        "phoneNumber": db_client.get("phone_number"),
        "totalInvested": db_client.get("total_invested"),
        "totalInterestEarned": db_client.get("total_interest_earned"),
        "totalWithdrawals": db_client.get("total_withdrawals")
    }


def transform_manager(db_manager: Dict[str, Any]) -> Dict[str, Any]:
    """Transform MongoDB money manager to API format"""
    from bson.decimal128 import Decimal128
    
    def to_float(val):
        if val is None:
            return 0.0
        if isinstance(val, Decimal128):
            return float(val.to_decimal())
        return float(val)
    
    return {
        "managerId": db_manager.get("manager_id"),
        "name": db_manager.get("name"),
        "displayName": db_manager.get("display_name"),
        "status": db_manager.get("status"),
        "executionType": db_manager.get("execution_type"),
        "strategyName": db_manager.get("strategy_name"),
        "riskProfile": db_manager.get("risk_profile"),
        "assignedAccounts": db_manager.get("assigned_accounts", []),
        "performanceFeeRate": to_float(db_manager.get("performance_fee_rate")),
        "currentMonthProfit": to_float(db_manager.get("current_month_profit")),
        "currentMonthFeeAccrued": to_float(db_manager.get("current_month_fee_accrued")),
        "profileUrl": db_manager.get("profile_url"),
        "broker": db_manager.get("broker"),
        "notes": db_manager.get("notes")
    }


def transform_pnl_data(pnl_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Transform PnL calculator output to API format"""
    return {
        "accountNumber": pnl_dict.get("account_number"),
        "calculationDate": pnl_dict.get("calculation_date"),
        
        # Capital In
        "initialAllocation": pnl_dict.get("initial_allocation"),
        "totalDeposits": pnl_dict.get("total_deposits"),
        "depositCount": pnl_dict.get("deposit_count"),
        "totalCapitalIn": pnl_dict.get("total_capital_in"),
        
        # Capital Out
        "currentEquity": pnl_dict.get("current_equity"),
        "totalWithdrawals": pnl_dict.get("total_withdrawals"),
        "withdrawalCount": pnl_dict.get("withdrawal_count"),
        "totalCapitalOut": pnl_dict.get("total_capital_out"),
        
        # P&L Metrics
        "truePnl": pnl_dict.get("true_pnl"),
        "returnPercentage": pnl_dict.get("return_percentage"),
        "isProfitable": pnl_dict.get("is_profitable"),
        "status": pnl_dict.get("status")
    }


def transform_fund_pnl(fund_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Transform fund P&L calculator output to API format"""
    return {
        "fundType": fund_dict.get("fund_type"),
        "totalAccounts": fund_dict.get("total_accounts"),
        "calculationDate": fund_dict.get("calculation_date"),
        
        "totalInitialAllocation": fund_dict.get("total_initial_allocation"),
        "totalDeposits": fund_dict.get("total_deposits"),
        "totalCapitalIn": fund_dict.get("total_capital_in"),
        
        "totalCurrentEquity": fund_dict.get("total_current_equity"),
        "totalWithdrawals": fund_dict.get("total_withdrawals"),
        "totalCapitalOut": fund_dict.get("total_capital_out"),
        
        "fundTruePnl": fund_dict.get("fund_true_pnl"),
        "fundReturnPercentage": fund_dict.get("fund_return_percentage"),
        "isProfitable": fund_dict.get("is_profitable"),
        
        "accounts": [transform_pnl_data(acc) for acc in fund_dict.get("accounts", [])]
    }


def transform_salesperson(db_salesperson: Dict[str, Any]) -> Dict[str, Any]:
    """Transform MongoDB salesperson to API format"""
    from bson.decimal128 import Decimal128
    
    def to_float(val):
        if val is None:
            return 0.0
        if isinstance(val, Decimal128):
            return float(val.to_decimal())
        return float(val)
    
    return {
        "id": str(db_salesperson.get("_id")),
        "referralCode": db_salesperson.get("referral_code"),
        "name": db_salesperson.get("name"),
        "email": db_salesperson.get("email"),
        "phone": db_salesperson.get("phone"),
        "active": db_salesperson.get("active", True),
        "totalSalesVolume": to_float(db_salesperson.get("total_sales_volume")),
        "totalClientsReferred": db_salesperson.get("total_clients_referred", 0),
        "totalCommissionsEarned": to_float(db_salesperson.get("total_commissions_earned")),
        "commissionsPaidToDate": to_float(db_salesperson.get("commissions_paid_to_date")),
        "commissionsPending": to_float(db_salesperson.get("commissions_pending")),
        "activeClients": db_salesperson.get("active_clients", 0),
        "activeInvestments": db_salesperson.get("active_investments", 0),
        "createdAt": db_salesperson.get("created_at").isoformat() if db_salesperson.get("created_at") else None,
        "updatedAt": db_salesperson.get("updated_at").isoformat() if db_salesperson.get("updated_at") else None
    }


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float with default"""
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int with default"""
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def format_currency(amount: Optional[float], decimals: int = 2) -> str:
    """Format amount as currency string"""
    if amount is None:
        return "$0.00"
    return f"${amount:,.{decimals}f}"


def format_percentage(value: Optional[float], decimals: int = 2) -> str:
    """Format value as percentage string"""
    if value is None:
        return "0.00%"
    return f"{value:.{decimals}f}%"
