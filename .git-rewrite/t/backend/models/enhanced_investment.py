"""
Enhanced Investment Model for FIDUS Investment Management Platform
Supports multiple MT5 account mappings per investment product
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from enum import Enum
import uuid

from .investment import FundCode, InvestmentStatus, Currency

# Import from the new MT5 pool models
from .mt5_account_pool import MT5InvestmentMapping

class EnhancedInvestmentBase(BaseModel):
    """Enhanced investment base model with multiple MT5 mapping support"""
    client_id: str = Field(..., description="Reference to user ID")
    fund_code: FundCode
    principal_amount: Decimal = Field(..., gt=0, description="Total investment amount")
    currency: Currency = Currency.USD
    investment_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: InvestmentStatus = InvestmentStatus.PENDING
    performance_fee_rate: Optional[Decimal] = Field(None, ge=0, le=1)
    management_fee_rate: Optional[Decimal] = Field(None, ge=0, le=1)
    notes: Optional[str] = Field(None, max_length=1000)
    
    # New fields for separation accounts
    interest_separation_mt5_account: Optional[int] = Field(None, description="MT5 account for interest tracking")
    gains_separation_mt5_account: Optional[int] = Field(None, description="MT5 account for gains tracking")
    
    @validator('principal_amount')
    def validate_principal_amount(cls, v):
        if v <= 0:
            raise ValueError('Principal amount must be greater than 0')
        return v

class EnhancedInvestmentCreate(EnhancedInvestmentBase):
    """Model for creating enhanced investment with MT5 mappings"""
    
    # MT5 Account mappings - list of MT5 accounts with allocations
    mt5_mappings: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of MT5 accounts with allocation amounts"
    )
    
    @validator('fund_code')
    def validate_fund_minimum(cls, v, values):
        """Validate minimum investment amounts for each fund"""
        minimums = {
            FundCode.CORE: 10000,      # Updated as per requirements
            FundCode.BALANCE: 50000,   # Updated as per requirements  
            FundCode.DYNAMIC: 250000,  # Updated as per requirements
            FundCode.UNLIMITED: 100000 # TBD - placeholder
        }
        
        principal_amount = values.get('principal_amount', 0)
        minimum = minimums.get(v, 0)
        
        if float(principal_amount) < minimum:
            raise ValueError(f'Minimum investment for {v} fund is ${minimum:,}')
        
        return v
    
    @validator('mt5_mappings')
    def validate_mt5_mappings(cls, v, values):
        """Validate MT5 mappings sum equals total investment"""
        if not v:
            raise ValueError('At least one MT5 account mapping is required')
        
        principal_amount = values.get('principal_amount', Decimal(0))
        
        # Calculate total mapped amount
        total_mapped = Decimal(0)
        mt5_accounts_used = set()
        
        for mapping in v:
            if not isinstance(mapping, dict):
                raise ValueError('Each MT5 mapping must be a dictionary')
            
            required_fields = ['mt5_account_number', 'allocated_amount', 'allocation_notes']
            for field in required_fields:
                if field not in mapping:
                    raise ValueError(f'MT5 mapping missing required field: {field}')
            
            # Check account number format
            mt5_account = mapping['mt5_account_number']
            if not isinstance(mt5_account, int) or mt5_account < 100000:
                raise ValueError('MT5 account number must be a valid integer >= 100000')
            
            # Check for duplicate MT5 accounts
            if mt5_account in mt5_accounts_used:
                raise ValueError(f'MT5 account {mt5_account} cannot be used multiple times in the same investment')
            mt5_accounts_used.add(mt5_account)
            
            # Check allocation amount
            allocated_amount = Decimal(str(mapping['allocated_amount']))
            if allocated_amount <= 0:
                raise ValueError('MT5 allocation amount must be greater than 0')
            
            # Check allocation notes
            notes = mapping.get('allocation_notes', '').strip()
            if not notes or len(notes) < 10:
                raise ValueError('⚠️ MANDATORY: Each MT5 allocation requires notes (min 10 characters) explaining the allocation')
            
            total_mapped += allocated_amount
        
        # Validate total equals principal amount (allow 1 cent tolerance)
        if abs(total_mapped - principal_amount) > Decimal('0.01'):
            raise ValueError(
                f'Sum of MT5 allocations (${total_mapped}) must equal total investment amount (${principal_amount}). '
                f'Current difference: ${abs(total_mapped - principal_amount)}'
            )
        
        return v

class EnhancedInvestment(EnhancedInvestmentBase):
    """Complete enhanced investment model"""
    investment_id: str = Field(default_factory=lambda: f"inv_{uuid.uuid4().hex[:16]}")
    current_value: Optional[Decimal] = None
    profit_loss: Optional[Decimal] = Field(default=0)
    profit_loss_percentage: Optional[Decimal] = Field(default=0)
    
    # MT5 mapping tracking
    mt5_mappings_count: int = Field(default=0, description="Number of MT5 accounts mapped")
    total_mapped_amount: Decimal = Field(default=Decimal(0), description="Sum of all MT5 allocations")
    mapping_validation_status: str = Field("pending", description="Mapping validation status")
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @property
    def calculated_profit_loss(self) -> Decimal:
        """Calculate profit/loss from current value and principal"""
        if self.current_value is None:
            return Decimal(0)
        return self.current_value - self.principal_amount
    
    @property
    def calculated_profit_loss_percentage(self) -> Decimal:
        """Calculate profit/loss percentage"""
        if self.current_value is None or self.principal_amount == 0:
            return Decimal(0)
        return ((self.current_value - self.principal_amount) / self.principal_amount) * 100
    
    @property
    def is_mapping_valid(self) -> bool:
        """Check if MT5 mappings sum equals total investment"""
        return abs(self.total_mapped_amount - self.principal_amount) < Decimal('0.01')
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v is not None else None
        }

class MT5MappingValidationResult(BaseModel):
    """Result of MT5 mapping validation"""
    is_valid: bool
    total_investment_amount: Decimal
    total_mapped_amount: Decimal
    difference: Decimal
    mt5_accounts_used: List[int]
    duplicate_accounts: List[int]
    validation_errors: List[str]
    validation_warnings: List[str]
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None
        }

class ClientInvestmentView(BaseModel):
    """Client-facing investment view (hides MT5 details)"""
    investment_id: str
    fund_code: FundCode
    fund_name: str
    principal_amount: Decimal
    current_value: Optional[Decimal]
    profit_loss: Optional[Decimal]
    profit_loss_percentage: Optional[Decimal]
    currency: Currency
    status: InvestmentStatus
    investment_date: datetime
    
    # Product information
    expected_monthly_return: Optional[Decimal]
    redemption_schedule: str
    contract_term_months: int = 14
    incubation_period_months: int = 2
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v is not None else None
        }

class AdminInvestmentView(BaseModel):
    """Admin-facing investment view (shows all MT5 details)"""
    investment_id: str
    client_id: str
    client_name: str
    fund_code: FundCode
    principal_amount: Decimal
    current_value: Optional[Decimal]
    profit_loss: Optional[Decimal]
    profit_loss_percentage: Optional[Decimal]
    currency: Currency
    status: InvestmentStatus
    investment_date: datetime
    
    # MT5 mapping details (admin only)
    mt5_mappings: List[Dict[str, Any]]
    mt5_mappings_count: int
    total_mapped_amount: Decimal
    mapping_is_valid: bool
    mapping_validation_status: str
    
    # Separation accounts
    interest_separation_mt5_account: Optional[int]
    gains_separation_mt5_account: Optional[int]
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    notes: Optional[str]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v is not None else None
        }

class ProductConfiguration(BaseModel):
    """Product configuration with updated requirements"""
    fund_code: FundCode
    fund_name: str
    minimum_investment: Decimal
    monthly_return_rate: Decimal
    redemption_schedule: str
    contract_term_months: int = 14
    incubation_period_months: int = 2
    is_active: bool = True
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None
        }

# Updated product configurations
FIDUS_PRODUCTS = {
    FundCode.CORE: ProductConfiguration(
        fund_code=FundCode.CORE,
        fund_name="FIDUS CORE",
        minimum_investment=Decimal("10000"),
        monthly_return_rate=Decimal("0.015"),  # 1.5%
        redemption_schedule="Monthly redemptions",
        contract_term_months=14,
        incubation_period_months=2
    ),
    FundCode.BALANCE: ProductConfiguration(
        fund_code=FundCode.BALANCE,
        fund_name="FIDUS BALANCE", 
        minimum_investment=Decimal("50000"),
        monthly_return_rate=Decimal("0.025"),  # 2.5%
        redemption_schedule="Quarterly redemptions",
        contract_term_months=14,
        incubation_period_months=2
    ),
    FundCode.DYNAMIC: ProductConfiguration(
        fund_code=FundCode.DYNAMIC,
        fund_name="FIDUS DYNAMIC",
        minimum_investment=Decimal("250000"),
        monthly_return_rate=Decimal("0.035"),  # 3.5%
        redemption_schedule="Semi-annual redemptions",
        contract_term_months=14,
        incubation_period_months=2
    ),
    FundCode.UNLIMITED: ProductConfiguration(
        fund_code=FundCode.UNLIMITED,
        fund_name="FIDUS UNLIMITED",
        minimum_investment=Decimal("100000"),  # TBD placeholder
        monthly_return_rate=Decimal("0.040"),  # TBD placeholder
        redemption_schedule="TBD",
        contract_term_months=14,
        incubation_period_months=2
    )
}