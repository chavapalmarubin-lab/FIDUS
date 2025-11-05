"""
FIDUS Platform - Field Registry Validation Schema
Single Source of Truth for all field names and transformations

Version: 2.0
Last Updated: November 5, 2025

This module provides:
1. Field mapping between MongoDB (snake_case) and API (camelCase)
2. Validation functions for enum values
3. Pydantic models for type safety
4. Transformation functions for data serialization
5. MongoDB document validation
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from bson import ObjectId, Decimal128
from pydantic import BaseModel, Field, validator
from enum import Enum

# ==============================================================================
# ENUM DEFINITIONS
# ==============================================================================

class ManagerName(str, Enum):
    """Allowed manager names from SYSTEM_MASTER.md"""
    UNO14 = "UNO14 Manager"
    GOLDENTRADE = "GoldenTrade Manager"
    PROVIDER1_ASSEV = "Provider1-Assev"
    ALEFLOREZTRADER = "alefloreztrader"
    TRADINGHUB = "TradingHub Gold Provider"
    CP_STRATEGY = "CP Strategy Provider"
    GOLDENTRADE_LEGACY = "GoldenTrade"  # Inactive only

class FundType(str, Enum):
    """Allowed fund types"""
    BALANCE = "BALANCE"
    CORE = "CORE"
    DYNAMIC = "DYNAMIC"
    UNLIMITED = "UNLIMITED"
    SEPARATION = "SEPARATION"
    FIDUS_BALANCE = "FIDUS_BALANCE"
    FIDUS_CORE = "FIDUS_CORE"
    FIDUS_DYNAMIC = "FIDUS_DYNAMIC"
    FIDUS_UNLIMITED = "FIDUS_UNLIMITED"
    FIDUS_SEPARATION = "FIDUS_SEPARATION"

class Status(str, Enum):
    """Allowed status values"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    APPROVED = "approved"
    CANCELLED = "cancelled"
    PAID = "paid"
    READY_TO_PAY = "ready_to_pay"

class ConnectionStatus(str, Enum):
    """MT5 connection status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"

# ==============================================================================
# ALLOWED ENUM VALUES (for backward compatibility)
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
    "BALANCE", "CORE", "DYNAMIC", "UNLIMITED", "SEPARATION",
    "FIDUS_BALANCE", "FIDUS_CORE", "FIDUS_DYNAMIC", "FIDUS_UNLIMITED", "FIDUS_SEPARATION"
]

ALLOWED_STATUS_VALUES = [
    "active", "inactive", "pending", "approved", "cancelled", "paid", "ready_to_pay"
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
    "manager_name": "managerName",  # Deprecated but mapped
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
    "last_sync": "lastSync",  # Deprecated but mapped
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
    "amount": "principalAmount",  # Deprecated, map to principalAmount
    "current_value": "currentValue",
    "deposit_date": "depositDate",
    "investment_date": "startDate",  # Deprecated, map to startDate
    "interest_start_date": "interestStartDate",
    "referral_salesperson_id": "referralSalespersonId",
    "referred_by": "referredBy",
    "referred_by_name": "referredByName",
    "total_interest_earned": "totalInterestEarned",
    "total_commissions_due": "totalCommissionsDue",
    
    # Clients
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
        "deprecated_fields": ["manager_name", "last_sync"],
        "enum_fields": {
            "manager": ALLOWED_MANAGER_NAMES,
            "fund_type": ALLOWED_FUND_TYPES,
            "connection_status": ["active", "inactive", "error"]
        }
    },
    "money_managers": {
        "required_fields": ["manager_id", "name", "status", "assigned_accounts"],
        "optional_fields": ["strategy_name", "performance_fee_rate"],
        "deprecated_fields": ["manager_name"],
        "enum_fields": {
            "name": ALLOWED_MANAGER_NAMES,
            "status": ALLOWED_STATUS_VALUES
        }
    },
    "salespeople": {
        "required_fields": ["salesperson_id", "name", "email", "referral_code", "active"],
        "optional_fields": ["phone", "total_sales_volume", "total_commissions_earned"],
        "deprecated_fields": [],
        "enum_fields": {
            "active": [True, False]
        }
    },
    "referral_commissions": {
        "required_fields": ["commission_id", "salesperson_id", "investment_id", "status"],
        "optional_fields": ["client_id", "principal_amount", "commission_amount"],
        "deprecated_fields": [],
        "enum_fields": {
            "status": ALLOWED_STATUS_VALUES,
            "fund_type": ALLOWED_FUND_TYPES
        }
    },
    "investments": {
        "required_fields": ["investment_id", "client_id", "fund_type", "principal_amount", "status"],
        "optional_fields": ["referral_salesperson_id", "current_value"],
        "deprecated_fields": ["amount", "referred_by", "investment_date"],
        "enum_fields": {
            "fund_type": ALLOWED_FUND_TYPES,
            "status": ALLOWED_STATUS_VALUES
        }
    },
    "clients": {
        "required_fields": ["name", "email", "status"],
        "optional_fields": ["phone", "referred_by", "referral_code"],
        "deprecated_fields": [],
        "enum_fields": {
            "status": ALLOWED_STATUS_VALUES
        }
    }
}

# ==============================================================================
# PYDANTIC MODELS FOR TYPE SAFETY
# ==============================================================================

class MT5AccountModel(BaseModel):
    """Pydantic model for MT5 account"""
    accountNumber: int
    balance: float
    equity: float
    managerName: str
    fundType: str
    fundCode: str
    broker: str
    currency: str
    leverage: int
    profit: float
    truePnl: float
    displayedPnl: float
    connectionStatus: str
    lastSyncTimestamp: Optional[datetime] = None
    
    class Config:
        # Ignore _id field when converting from MongoDB
        fields = {'id': {'exclude': True}}

class SalespersonModel(BaseModel):
    """Pydantic model for salesperson"""
    salespersonId: str
    name: str
    email: str
    phone: Optional[str] = None
    referralCode: str
    referralLink: str
    active: bool
    totalSalesVolume: float
    totalCommissionsEarned: float
    commissionsPending: float
    totalClientsReferred: int
    joinedDate: Optional[datetime] = None

class CommissionModel(BaseModel):
    """Pydantic model for commission"""
    commissionId: str
    salespersonId: str
    investmentId: str
    clientId: str
    fundType: str
    principalAmount: float
    interestAmount: float
    commissionAmount: float
    paymentMonth: str
    paymentDate: datetime
    status: str

class InvestmentModel(BaseModel):
    """Pydantic model for investment"""
    investmentId: str
    clientId: str
    fundType: str
    fundCode: str
    principalAmount: float
    currentValue: float
    status: str
    startDate: datetime
    referralSalespersonId: Optional[str] = None

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

def normalize_fund_type(fund_type: str) -> str:
    """Normalize fund type to short form (without FIDUS_ prefix)"""
    if fund_type.startswith("FIDUS_"):
        return fund_type.replace("FIDUS_", "")
    return fund_type

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
    
    # Check for deprecated fields
    if "deprecated_fields" in schema:
        for field in schema["deprecated_fields"]:
            if field in document:
                errors.append(f"Deprecated field found: {field}. This field should be removed.")
    
    # Check enum fields
    if "enum_fields" in schema:
        for field, allowed_values in schema["enum_fields"].items():
            if field in document and document[field] not in allowed_values:
                errors.append(f"Invalid value for {field}: {document[field]}. Allowed: {allowed_values}")
    
    return len(errors) == 0, errors

def validate_api_response(collection_name: str, response: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate API response has correct field names (camelCase)
    
    Returns:
        (is_valid, errors) tuple
    """
    errors = []
    
    # Check for snake_case fields (should not exist in API response)
    for key in response.keys():
        if '_' in key and key != '__typename':  # Allow GraphQL __typename
            errors.append(f"Snake_case field found in API response: {key}. Should be camelCase.")
    
    return len(errors) == 0, errors

# ==============================================================================
# TRANSFORMATION FUNCTIONS
# ==============================================================================

def snake_to_camel(snake_str: str) -> str:
    """Convert snake_case to camelCase"""
    if not snake_str or snake_str.startswith('_'):
        return snake_str
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def camel_to_snake(camel_str: str) -> str:
    """Convert camelCase to snake_case"""
    import re
    return re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()

def transform_value(value: Any) -> Any:
    """
    Transform MongoDB value to API-safe value
    
    Handles:
    - ObjectId → String
    - Decimal128 → Float
    - datetime → ISO 8601 string
    - Nested dicts → Recursive transform
    - Lists → Transform each item
    """
    if value is None:
        return None
    elif isinstance(value, ObjectId):
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
    
    Rules:
    1. Convert snake_case to camelCase
    2. Handle ObjectId, Decimal128, datetime serialization
    3. Remove internal fields (except _id → id)
    4. Apply field mapping from FIELD_MAPPING
    
    Example:
        mongo_doc = {
            "_id": ObjectId("..."),
            "account": 886557,
            "manager": "UNO14 Manager",
            "true_pnl": Decimal128("2829.69"),
            "created_at": datetime(...)
        }
        
        Result:
        {
            "id": "...",
            "accountNumber": 886557,
            "managerName": "UNO14 Manager",
            "truePnl": 2829.69,
            "createdAt": "2025-11-05T14:30:00.000Z"
        }
    """
    if not isinstance(mongo_doc, dict):
        return mongo_doc
    
    api_doc = {}
    
    for mongo_field, value in mongo_doc.items():
        # Skip internal fields (except _id)
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
    
    Rules:
    1. Convert camelCase to snake_case
    2. Use reverse field mapping
    3. For insert/update operations
    
    Example:
        api_doc = {
            "accountNumber": 886557,
            "managerName": "UNO14 Manager",
            "truePnl": 2829.69
        }
        
        Result:
        {
            "account": 886557,
            "manager": "UNO14 Manager",
            "true_pnl": 2829.69
        }
    """
    # Create reverse mapping
    reverse_mapping = {v: k for k, v in FIELD_MAPPING.items()}
    
    mongo_doc = {}
    for api_field, value in api_doc.items():
        # Get MongoDB field name
        mongo_field = reverse_mapping.get(api_field, camel_to_snake(api_field))
        mongo_doc[mongo_field] = value
    
    return mongo_doc

# ==============================================================================
# COLLECTION-SPECIFIC TRANSFORMERS
# ==============================================================================

def transform_mt5_account(account: Dict[str, Any]) -> Dict[str, Any]:
    """Transform MT5 account with special handling"""
    transformed = transform_to_api_format(account)
    
    # Ensure deprecated fields are not included
    transformed.pop('managerName', None) if 'manager_name' in account else None
    transformed.pop('lastSync', None) if 'last_sync' in account else None
    
    return transformed

def transform_salesperson(salesperson: Dict[str, Any]) -> Dict[str, Any]:
    """Transform salesperson with Decimal128 handling"""
    transformed = transform_to_api_format(salesperson)
    
    # Ensure financial fields are floats with 2 decimals
    for field in ['totalSalesVolume', 'totalCommissionsEarned', 'commissionsPending']:
        if field in transformed and transformed[field] is not None:
            transformed[field] = round(float(transformed[field]), 2)
    
    return transformed

def transform_investment(investment: Dict[str, Any]) -> Dict[str, Any]:
    """Transform investment with deprecated field handling"""
    transformed = transform_to_api_format(investment)
    
    # Ensure deprecated fields are not included
    if 'amount' in investment and 'principal_amount' not in investment:
        transformed['principalAmount'] = transform_value(investment['amount'])
    
    return transformed

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
    return reverse_mapping.get(api_field, camel_to_snake(api_field))

def get_deprecated_fields(collection_name: str) -> List[str]:
    """Get list of deprecated fields for a collection"""
    if collection_name in MONGODB_SCHEMAS:
        return MONGODB_SCHEMAS[collection_name].get("deprecated_fields", [])
    return []

# ==============================================================================
# MIGRATION HELPERS
# ==============================================================================

def should_remove_field(collection_name: str, field_name: str) -> bool:
    """Check if field should be removed during migration"""
    deprecated = get_deprecated_fields(collection_name)
    return field_name in deprecated

def get_migration_unset_fields(collection_name: str) -> Dict[str, str]:
    """
    Get MongoDB $unset operation for deprecated fields
    
    Returns:
        {"field1": "", "field2": ""} for use in updateMany({}, {$unset: ...})
    """
    deprecated = get_deprecated_fields(collection_name)
    return {field: "" for field in deprecated}

# ==============================================================================
# EXPORT
# ==============================================================================

__all__ = [
    # Enums
    "ManagerName",
    "FundType",
    "Status",
    "ConnectionStatus",
    # Enum Lists
    "ALLOWED_MANAGER_NAMES",
    "ALLOWED_FUND_TYPES",
    "ALLOWED_STATUS_VALUES",
    # Field Mapping
    "FIELD_MAPPING",
    "MONGODB_SCHEMAS",
    # Pydantic Models
    "MT5AccountModel",
    "SalespersonModel",
    "CommissionModel",
    "InvestmentModel",
    # Validation Functions
    "validate_manager_name",
    "validate_fund_type",
    "validate_status",
    "normalize_fund_type",
    "validate_mongodb_document",
    "validate_api_response",
    # Transformation Functions
    "snake_to_camel",
    "camel_to_snake",
    "transform_value",
    "transform_to_api_format",
    "transform_from_api_format",
    "transform_mt5_account",
    "transform_salesperson",
    "transform_investment",
    # Helper Functions
    "get_allowed_manager_names",
    "get_allowed_fund_types",
    "get_api_field_name",
    "get_mongo_field_name",
    "get_deprecated_fields",
    # Migration Helpers
    "should_remove_field",
    "get_migration_unset_fields"
]
