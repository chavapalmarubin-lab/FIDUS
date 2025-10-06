"""
Enhanced Investment Creation with Just-In-Time MT5 Account Creation
Models for creating investments with MT5 accounts entered directly during creation
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from enum import Enum
import uuid

from .investment import FundCode, InvestmentStatus, Currency
from .mt5_account_pool import MT5AccountType, BrokerCode

class MT5AccountInput(BaseModel):
    """Model for MT5 account input during investment creation"""
    mt5_account_number: int = Field(..., ge=100000, le=99999999, description="MT5 account login number")
    investor_password: str = Field(..., min_length=1, description="⚠️ INVESTOR PASSWORD ONLY - Not trading password")
    broker_name: BrokerCode = Field(..., description="Broker identifier")
    allocated_amount: Decimal = Field(..., gt=0, description="Amount allocated to this MT5 account")
    allocation_notes: str = Field(..., min_length=10, max_length=2000, description="⚠️ MANDATORY: Notes explaining this allocation")
    mt5_server: Optional[str] = Field(None, description="MT5 server address")
    
    @validator('investor_password')
    def validate_investor_password(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('⚠️ CRITICAL: Investor password is required - This system ONLY accepts INVESTOR passwords')
        return v.strip()
    
    @validator('allocation_notes')
    def validate_allocation_notes(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Allocation notes are mandatory and must be at least 10 characters explaining the allocation reason')
        return v.strip()

class SeparationAccountInput(BaseModel):
    """Model for interest and gains separation account input"""
    mt5_account_number: int = Field(..., ge=100000, le=99999999, description="MT5 account number for separation tracking")
    investor_password: str = Field(..., min_length=1, description="⚠️ INVESTOR PASSWORD ONLY")
    broker_name: BrokerCode = Field(..., description="Broker identifier")
    account_type: MT5AccountType = Field(..., description="Type of separation account")
    mt5_server: Optional[str] = Field(None, description="MT5 server address")
    notes: Optional[str] = Field(None, description="Notes about this separation account")
    
    @validator('investor_password')
    def validate_investor_password(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('⚠️ CRITICAL: Investor password is required for separation accounts')
        return v.strip()

class InvestmentWithMT5Create(BaseModel):
    """Model for creating investment with MT5 accounts in one operation"""
    
    # Investment details
    client_id: str = Field(..., description="Reference to user ID")
    fund_code: FundCode
    principal_amount: Decimal = Field(..., gt=0, description="Total investment amount")
    currency: Currency = Currency.USD
    investment_date: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: Optional[str] = Field(None, max_length=1000)
    
    # MT5 Account allocations (investment accounts)
    mt5_accounts: List[MT5AccountInput] = Field(
        ..., 
        min_items=1, 
        description="List of MT5 accounts with allocations (minimum 1 required)"
    )
    
    # Separation accounts
    interest_separation_account: Optional[SeparationAccountInput] = Field(
        None, 
        description="MT5 account for interest separation tracking"
    )
    gains_separation_account: Optional[SeparationAccountInput] = Field(
        None, 
        description="MT5 account for gains separation tracking"
    )
    
    # Creation metadata
    creation_notes: str = Field(
        ..., 
        min_length=20, 
        max_length=2000, 
        description="⚠️ MANDATORY: Detailed notes explaining this investment and MT5 allocation strategy"
    )
    
    @validator('fund_code')
    def validate_fund_minimum(cls, v, values):
        """Validate minimum investment amounts for each fund"""
        minimums = {
            FundCode.CORE: 10000,
            FundCode.BALANCE: 50000,
            FundCode.DYNAMIC: 250000,
            FundCode.UNLIMITED: 100000
        }
        
        principal_amount = values.get('principal_amount', 0)
        minimum = minimums.get(v, 0)
        
        if float(principal_amount) < minimum:
            raise ValueError(f'Minimum investment for {v} fund is ${minimum:,}')
        
        return v
    
    @validator('mt5_accounts')
    def validate_mt5_allocations(cls, v, values):
        """Validate MT5 allocations sum equals total investment"""
        if not v:
            raise ValueError('At least one MT5 account allocation is required')
        
        principal_amount = values.get('principal_amount', Decimal(0))
        
        # Calculate total allocated amount
        total_allocated = sum(account.allocated_amount for account in v)
        
        # Check for duplicate MT5 accounts
        account_numbers = [account.mt5_account_number for account in v]
        if len(account_numbers) != len(set(account_numbers)):
            duplicates = [acc for acc in account_numbers if account_numbers.count(acc) > 1]
            raise ValueError(f'Duplicate MT5 accounts not allowed: {duplicates}')
        
        # Validate total equals principal amount (1 cent tolerance)
        difference = abs(total_allocated - principal_amount)
        if difference > Decimal('0.01'):
            raise ValueError(
                f'Sum of MT5 allocations (${total_allocated}) must equal total investment amount (${principal_amount}). '
                f'Current difference: ${difference}'
            )
        
        return v
    
    @validator('interest_separation_account')
    def validate_interest_separation(cls, v, values):
        """Validate interest separation account doesn't conflict with investment accounts"""
        if v is None:
            return v
        
        mt5_accounts = values.get('mt5_accounts', [])
        investment_account_numbers = [acc.mt5_account_number for acc in mt5_accounts]
        
        if v.mt5_account_number in investment_account_numbers:
            raise ValueError('Interest separation account cannot be the same as an investment account')
        
        return v
    
    @validator('gains_separation_account')
    def validate_gains_separation(cls, v, values):
        """Validate gains separation account doesn't conflict with other accounts"""
        if v is None:
            return v
        
        mt5_accounts = values.get('mt5_accounts', [])
        investment_account_numbers = [acc.mt5_account_number for acc in mt5_accounts]
        
        if v.mt5_account_number in investment_account_numbers:
            raise ValueError('Gains separation account cannot be the same as an investment account')
        
        interest_account = values.get('interest_separation_account')
        if interest_account and v.mt5_account_number == interest_account.mt5_account_number:
            raise ValueError('Gains separation account cannot be the same as interest separation account')
        
        return v
    
    @validator('creation_notes')
    def validate_creation_notes(cls, v):
        if not v or len(v.strip()) < 20:
            raise ValueError('Creation notes are mandatory and must be at least 20 characters explaining the investment strategy')
        return v.strip()

class MT5AccountAvailabilityCheck(BaseModel):
    """Model for checking MT5 account availability"""
    mt5_account_number: int = Field(..., description="MT5 account number to check")

class MT5AccountAvailabilityResult(BaseModel):
    """Result of MT5 account availability check"""
    mt5_account_number: int
    is_available: bool
    reason: str
    current_allocation: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None
        }

class InvestmentCreationResult(BaseModel):
    """Result of investment creation with MT5 accounts"""
    success: bool
    investment_id: str
    message: str
    
    # Investment details
    investment: Dict[str, Any]
    
    # Created MT5 accounts
    mt5_accounts_created: List[Dict[str, Any]]
    separation_accounts_created: List[Dict[str, Any]]
    
    # Validation summary
    total_investment_amount: Decimal
    total_allocated_amount: Decimal
    allocation_is_valid: bool
    
    # Audit information
    created_by_admin: str
    creation_timestamp: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v is not None else None
        }

class MT5AccountEditRequest(BaseModel):
    """Model for editing MT5 account allocation amount"""
    new_allocated_amount: Decimal = Field(..., gt=0, description="New allocation amount")
    edit_notes: str = Field(..., min_length=10, max_length=1000, description="⚠️ MANDATORY: Reason for editing allocation")
    
    @validator('edit_notes')
    def validate_edit_notes(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Edit notes are mandatory and must be at least 10 characters explaining the change')
        return v.strip()

class InvestmentMT5Summary(BaseModel):
    """Summary view of investment with MT5 allocation details"""
    investment_id: str
    client_id: str
    client_name: str
    fund_code: FundCode
    principal_amount: Decimal
    investment_date: datetime
    status: InvestmentStatus
    
    # MT5 allocation summary
    total_mt5_accounts: int
    total_allocated_amount: Decimal
    allocation_is_valid: bool
    
    # MT5 account details
    investment_accounts: List[Dict[str, Any]]
    interest_separation_account: Optional[Dict[str, Any]]
    gains_separation_account: Optional[Dict[str, Any]]
    
    # Creation metadata
    created_by_admin: str
    created_at: datetime
    creation_notes: str
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v is not None else None
        }