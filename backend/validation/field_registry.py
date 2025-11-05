"""
FIDUS Platform - Field Registry Validation
Single Source of Truth for all field names and transformations

Version: 1.0
Last Updated: November 5, 2025
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from bson import ObjectId, Decimal128

# ==============================================================================
# ALLOWED ENUM VALUES
# ==============================================================================

ALLOWED_MANAGER_NAMES = [
    "UNO14 Manager",
    "GoldenTrade Manager",
    "Provider1-Assev",
    "alefloreztrader",
    "TradingHub Gold Provider",
    "CP Strategy Provider",
    "GoldenTrade"  # Inactive only
]

ALLOWED_FUND_TYPES = [
    "BALANCE",
    "CORE",
    "DYNAMIC",
    "UNLIMITED",
    "SEPARATION",
    "FIDUS_BALANCE",  # Alternative format
    "FIDUS_CORE",
    "FIDUS_DYNAMIC",
    "FIDUS_UNLIMITED",
    "FIDUS_SEPARATION"
]

ALLOWED_STATUS_VALUES = [
    "active",
    "inactive",
    "pending",
    "approved",
    "cancelled",
    "paid",
    "ready_to_pay"
]

# ==============================================================================
# FIELD MAPPING: MongoDB (snake_case) → API (camelCase)
# ==============================================================================

FIELD_MAPPING = {
    # Common fields
    "_id": "id",
    "created_at": "createdAt",
    "updated_at": "updatedAt",
    
    # MT5 Accounts
    "account": "accountNumber",
    "account_number": "accountNumber",
    "manager": "managerName",
    "manager_name": "managerName",
    "fund_type": "fundType",
    "fund_code": "fundCode",
    "client_id": "clientId",
    "client_name": "clientName",
    "initial_allocation": "initialAllocation",
    "true_pnl": "truePnl",
    "displayed_pnl": "displayedPnl",
    "profit_withdrawals": "profitWithdrawals",
    "inter_account_transfers": "interAccountTransfers",
    "connection_status": "connectionStatus",
    "last_sync_timestamp": "lastSyncTimestamp",
    "data_source": "dataSource",
    "synced_from_vps": "syncedFromVps",
    "free_margin": "freeMargin",
    "margin_level": "marginLevel",
    "num_positions": "numPositions",
    
    # Money Managers
    "manager_id": "managerId",
    "display_name": "displayName",
    "assigned_accounts": "assignedAccounts",
    "strategy_name": "strategyName",
    "strategy_description": "strategyDescription",
    "performance_fee_rate": "performanceFeeRate",
    "performance_fee_type": "performanceFeeType",
    "risk_profile": "riskProfile",
    "profile_type": "profileType",
    "execution_type": "executionType",
    "current_month_profit": "currentMonthProfit",
    "current_month_fee_accrued": "currentMonthFeeAccrued",
    "ytd_fees_paid": "ytdFeesPaid",
    "start_date": "startDate",
    
    # Salespeople
    "salesperson_id": "salespersonId",
    "referral_code": "referralCode",
    "referral_link": "referralLink",
    "total_sales_volume": "totalSalesVolume",
    "total_commissions_earned": "totalCommissionsEarned",
    "commissions_pending": "commissionsPending",
    "commissions_paid_to_date": "commissionsPaidToDate",
    "total_clients_referred": "totalClientsReferred",
    "active_clients": "activeClients",
    "active_investments": "activeInvestments",
    "next_commission_date": "nextCommissionDate",
    "next_commission_amount": "nextCommissionAmount",
    "joined_date": "joinedDate",
    "preferred_payment_method": "preferredPaymentMethod",
    "wallet_details": "walletDetails",
    
    # Commissions
    "commission_id": "commissionId",
    "investment_id": "investmentId",
    "principal_amount": "principalAmount",
    "interest_amount": "interestAmount",
    "commission_amount": "commissionAmount",
    "payment_month": "paymentMonth",
    "payment_date": "paymentDate",
    
    # Investments
    "current_value": "currentValue",
    "deposit_date": "depositDate",
    "interest_start_date": "interestStartDate",
    "referral_salesperson_id": "referralSalespersonId",
    "referred_by_name": "referredByName",
    "total_interest_earned": "totalInterestEarned",
    "total_commissions_due": "totalCommissionsDue",
    
    # Clients
    "referred_by": "referredBy",
    "referral_date": "referralDate",
    "total_commissions_generated": "totalCommissionsGenerated",
    
    # MT5 Deals
    "synced_at": "syncedAt"
}

# ==============================================================================
# MONGODB COLLECTION SCHEMAS
# ==============================================================================

MONGODB_SCHEMAS = {
    "mt5_accounts": {
        "required_fields": ["account", "balance", "equity", "fund_type", "manager"],
        "optional_fields": ["client_id", "client_name", "initial_allocation", "true_pnl"],
        "enum_fields": {
            "manager": ALLOWED_MANAGER_NAMES,
            "fund_type": ALLOWED_FUND_TYPES
        }
    },
    "money_managers": {
        "required_fields": ["manager_id", "name", "status", "assigned_accounts"],
        "optional_fields": ["strategy_name", "performance_fee_rate"],
        "enum_fields": {
            "name": ALLOWED_MANAGER_NAMES,
            "status": ALLOWED_STATUS_VALUES
        }
    },
    "salespeople": {
        "required_fields": ["salesperson_id", "name", "email", "referral_code", "active"],
        "optional_fields": ["phone", "total_sales_volume", "total_commissions_earned"],
        "enum_fields": {
            "active": [True, False]
        }
    },
    "referral_commissions": {
        "required_fields": ["commission_id", "salesperson_id", "investment_id", "status"],
        "optional_fields": ["client_id", "principal_amount", "commission_amount"],
        "enum_fields": {
            "status": ALLOWED_STATUS_VALUES
        }
    },
    "investments": {
        "required_fields": ["investment_id", "client_id", "fund_type", "principal_amount", "status"],
        "optional_fields": ["referral_salesperson_id", "current_value"],
        "enum_fields": {
            "fund_type": ALLOWED_FUND_TYPES,
            "status": ALLOWED_STATUS_VALUES
        }
    }
}

# ==============================================================================
# VALIDATION FUNCTIONS
# ==============================================================================

def validate_manager_name(name: str) -> bool:
    """Validate manager name is from allowed list"""
    return name in ALLOWED_MANAGER_NAMES

def validate_fund_type(fund_type: str) -> bool:
    """Validate fund type is from allowed list"""
    return fund_type in ALLOWED_FUND_TYPES

def validate_status(status: str) -> bool:
    """Validate status is from allowed list"""
    return status in ALLOWED_STATUS_VALUES

def validate_mongodb_document(collection_name: str, document: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate MongoDB document against schema
    
    Returns:
        (is_valid, errors) tuple
    """
    if collection_name not in MONGODB_SCHEMAS:
        return True, []  # No schema defined, skip validation
    
    schema = MONGODB_SCHEMAS[collection_name]
    errors = []
    
    # Check required fields
    for field in schema["required_fields"]:
        if field not in document:
            errors.append(f"Missing required field: {field}")
    
    # Check enum fields
    if "enum_fields" in schema:
        for field, allowed_values in schema["enum_fields"].items():
            if field in document and document[field] not in allowed_values:
                errors.append(f"Invalid value for {field}: {document[field]}. Allowed: {allowed_values}")
    
    return len(errors) == 0, errors

# ==============================================================================
# TRANSFORMATION FUNCTIONS
# ==============================================================================

def snake_to_camel(snake_str: str) -> str:
    """Convert snake_case to camelCase"""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def transform_value(value: Any) -> Any:
    """Transform MongoDB value to API-safe value"""
    if isinstance(value, ObjectId):
        return str(value)
    elif isinstance(value, Decimal128):
        return float(value.to_decimal())
    elif isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, dict):
        return transform_to_api_format(value)
    elif isinstance(value, list):
        return [transform_value(item) for item in value]
    return value

def transform_to_api_format(mongo_doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform MongoDB document to API format
    
    - Converts snake_case to camelCase
    - Handles ObjectId, Decimal128, datetime serialization
    - Removes internal fields
    """
    api_doc = {}
    
    for mongo_field, value in mongo_doc.items():
        # Skip internal fields
        if mongo_field.startswith('_') and mongo_field != '_id':
            continue
        
        # Get API field name from mapping or convert
        api_field = FIELD_MAPPING.get(mongo_field, snake_to_camel(mongo_field))
        
        # Transform value
        api_doc[api_field] = transform_value(value)
    
    return api_doc

def transform_from_api_format(api_doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform API format to MongoDB format
    
    - Converts camelCase to snake_case
    - For insert/update operations
    """
    # Create reverse mapping
    reverse_mapping = {v: k for k, v in FIELD_MAPPING.items()}
    
    mongo_doc = {}
    for api_field, value in api_doc.items():
        # Get MongoDB field name
        mongo_field = reverse_mapping.get(api_field, api_field)
        mongo_doc[mongo_field] = value
    
    return mongo_doc

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_allowed_manager_names() -> List[str]:
    """Get list of allowed manager names"""
    return ALLOWED_MANAGER_NAMES.copy()

def get_allowed_fund_types() -> List[str]:
    """Get list of allowed fund types"""
    return ALLOWED_FUND_TYPES.copy()

def get_api_field_name(mongo_field: str) -> str:
    """Get API field name for MongoDB field"""
    return FIELD_MAPPING.get(mongo_field, snake_to_camel(mongo_field))

def get_mongo_field_name(api_field: str) -> str:
    """Get MongoDB field name for API field"""
    reverse_mapping = {v: k for k, v in FIELD_MAPPING.items()}
    return reverse_mapping.get(api_field, api_field)

# ==============================================================================
# EXPORT
# ==============================================================================

__all__ = [
    "ALLOWED_MANAGER_NAMES",
    "ALLOWED_FUND_TYPES",
    "ALLOWED_STATUS_VALUES",
    "FIELD_MAPPING",
    "MONGODB_SCHEMAS",
    "validate_manager_name",
    "validate_fund_type",
    "validate_status",
    "validate_mongodb_document",
    "transform_to_api_format",
    "transform_from_api_format",
    "get_allowed_manager_names",
    "get_allowed_fund_types",
    "get_api_field_name",
    "get_mongo_field_name"
]
