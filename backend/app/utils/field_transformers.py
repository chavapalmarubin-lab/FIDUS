"""
Field Transformation Utilities for API Responses
Standardizes field names between MongoDB (snake_case) and API/Frontend (camelCase)

Author: FIDUS Investment Management
Date: October 31, 2025
"""

from typing import Dict, Any, Optional
from datetime import datetime


def transform_mt5_account(db_account: Dict[str, Any]) -> Dict[str, Any]:
    """Transform MongoDB MT5 account to API format (camelCase)"""
    return {
        "accountNumber": db_account.get("account"),
        "accountBalance": db_account.get("balance"),
        "accountEquity": db_account.get("equity"),
        "profitLoss": db_account.get("profit"),
        "usedMargin": db_account.get("margin"),
        "freeMargin": db_account.get("margin_free"),
        "marginLevel": db_account.get("margin_level"),
        "accountLeverage": db_account.get("leverage"),
        "currency": db_account.get("currency"),
        "serverName": db_account.get("server"),
        "brokerName": db_account.get("company"),
        "fundType": db_account.get("fund_type"),
        "managerName": db_account.get("manager_name") or db_account.get("money_manager"),
        "targetAmount": db_account.get("target_amount"),
        "lastUpdate": db_account.get("updated_at").isoformat() if db_account.get("updated_at") else None
    }


def transform_investment(db_investment: Dict[str, Any]) -> Dict[str, Any]:
    """Transform MongoDB investment to API format"""
    return {
        "investmentId": str(db_investment.get("_id")),
        "clientId": db_investment.get("client_id"),
        "principalAmount": db_investment.get("principal_amount"),
        "currentValue": db_investment.get("current_value"),
        "interestRate": db_investment.get("interest_rate"),
        "interestEarned": db_investment.get("interest_earned"),
        "investmentDate": db_investment.get("investment_date").isoformat() if db_investment.get("investment_date") else None,
        "maturityDate": db_investment.get("maturity_date").isoformat() if db_investment.get("maturity_date") else None,
        "fundType": db_investment.get("fund_type"),
        "status": db_investment.get("status")
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
    return {
        "managerId": db_manager.get("manager_id"),
        "managerName": db_manager.get("manager_name"),
        "strategy": db_manager.get("strategy"),
        "riskLevel": db_manager.get("risk_level"),
        "assignedAccounts": db_manager.get("assigned_accounts", [])
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
