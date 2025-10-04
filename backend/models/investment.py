"""
Investment Model for FIDUS Investment Management Platform
Pydantic models for investment data validation and serialization
"""

from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from enum import Enum
import uuid

class FundCode(str, Enum):
    CORE = "CORE"
    BALANCE = "BALANCE"
    DYNAMIC = "DYNAMIC"
    UNLIMITED = "UNLIMITED"

class InvestmentStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    PENDING = "pending"
    SUSPENDED = "suspended"

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"

class InvestmentBase(BaseModel):
    """Base investment model with common fields"""
    client_id: str = Field(..., description="Reference to user ID")
    fund_code: FundCode
    principal_amount: Decimal = Field(..., gt=0, description="Investment amount")
    currency: Currency = Currency.USD
    investment_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: InvestmentStatus = InvestmentStatus.PENDING
    performance_fee_rate: Optional[Decimal] = Field(None, ge=0, le=1)
    management_fee_rate: Optional[Decimal] = Field(None, ge=0, le=1)
    notes: Optional[str] = Field(None, max_length=1000)
    
    @validator('principal_amount')
    def validate_principal_amount(cls, v):
        if v <= 0:
            raise ValueError('Principal amount must be greater than 0')
        return v

class InvestmentCreate(InvestmentBase):
    """Model for creating a new investment"""
    
    @validator('fund_code')
    def validate_fund_minimum(cls, v, values):
        """Validate minimum investment amounts for each fund"""
        minimums = {
            FundCode.CORE: 5000,
            FundCode.BALANCE: 10000,
            FundCode.DYNAMIC: 15000,
            FundCode.UNLIMITED: 25000
        }
        
        principal_amount = values.get('principal_amount', 0)
        minimum = minimums.get(v, 0)
        
        if float(principal_amount) < minimum:
            raise ValueError(f'Minimum investment for {v} fund is ${minimum:,}')
        
        return v

class InvestmentUpdate(BaseModel):
    """Model for updating investment information"""
    status: Optional[InvestmentStatus] = None
    current_value: Optional[Decimal] = Field(None, gt=0)
    performance_fee_rate: Optional[Decimal] = Field(None, ge=0, le=1)
    management_fee_rate: Optional[Decimal] = Field(None, ge=0, le=1)
    notes: Optional[str] = Field(None, max_length=1000)
    mt5_account_id: Optional[str] = None

class Investment(InvestmentBase):
    """Complete investment model with all fields"""
    investment_id: str = Field(default_factory=lambda: f"inv_{uuid.uuid4().hex[:16]}")
    current_value: Optional[Decimal] = None
    profit_loss: Optional[Decimal] = Field(default=0)
    profit_loss_percentage: Optional[Decimal] = Field(default=0)
    mt5_account_id: Optional[str] = None
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
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v is not None else None
        }

class InvestmentResponse(BaseModel):
    """Investment model for API responses"""
    investment_id: str
    client_id: str
    fund_code: FundCode
    principal_amount: Decimal
    current_value: Optional[Decimal]
    profit_loss: Optional[Decimal]
    profit_loss_percentage: Optional[Decimal]
    currency: Currency
    status: InvestmentStatus
    investment_date: datetime
    performance_fee_rate: Optional[Decimal]
    management_fee_rate: Optional[Decimal]
    mt5_account_id: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v is not None else None
        }

class InvestmentStats(BaseModel):
    """Investment statistics model"""
    total_investments: int
    total_aum: Decimal
    active_investments: int
    closed_investments: int
    pending_investments: int
    by_fund: dict
    by_currency: dict
    average_investment_size: Decimal
    total_profit_loss: Decimal
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None
        }

class InvestmentSearch(BaseModel):
    """Investment search parameters"""
    client_id: Optional[str] = None
    fund_code: Optional[FundCode] = None
    status: Optional[InvestmentStatus] = None
    currency: Optional[Currency] = None
    min_amount: Optional[Decimal] = Field(None, gt=0)
    max_amount: Optional[Decimal] = Field(None, gt=0)
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    investment_after: Optional[datetime] = None
    investment_before: Optional[datetime] = None
    limit: int = Field(default=50, le=100)
    skip: int = Field(default=0, ge=0)
    sort_by: str = Field(default="created_at", regex="^(investment_id|client_id|fund_code|principal_amount|current_value|investment_date|created_at|updated_at)$")
    sort_order: int = Field(default=-1, ge=-1, le=1)  # -1 for desc, 1 for asc
    
    @validator('max_amount')
    def validate_amount_range(cls, v, values):
        min_amount = values.get('min_amount')
        if min_amount is not None and v is not None and v <= min_amount:
            raise ValueError('max_amount must be greater than min_amount')
        return v

class ClientInvestmentSummary(BaseModel):
    """Summary of investments for a specific client"""
    client_id: str
    total_investments: int
    total_principal: Decimal
    total_current_value: Decimal
    total_profit_loss: Decimal
    total_profit_loss_percentage: Decimal
    by_fund: dict
    active_investments: List[InvestmentResponse]
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None
        }

class InvestmentPerformance(BaseModel):
    """Investment performance tracking model"""
    investment_id: str
    date: datetime
    value: Decimal
    profit_loss: Decimal
    profit_loss_percentage: Decimal
    notes: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v is not None else None
        }

class FundConfiguration(BaseModel):
    """Fund configuration model"""
    fund_code: FundCode
    name: str
    description: str
    minimum_investment: Decimal
    currency: Currency
    performance_fee_rate: Decimal
    management_fee_rate: Decimal
    is_active: bool = True
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None
        }