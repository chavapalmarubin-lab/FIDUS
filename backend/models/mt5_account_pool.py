"""
MT5 Account Pool Management Models for FIDUS Investment Management Platform
New models to support multiple MT5 account mappings per investment product
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from enum import Enum
import uuid

class MT5AccountType(str, Enum):
    INVESTMENT = "investment"
    INTEREST_SEPARATION = "interest_separation"
    GAINS_SEPARATION = "gains_separation"

class MT5AccountPoolStatus(str, Enum):
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    PENDING_DEALLOCATION = "pending_deallocation"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"

class BrokerCode(str, Enum):
    MULTIBANK = "multibank"
    DOOTECHNOLOGY = "dootechnology"
    VTMARKETS = "vtmarkets"

class MT5AccountPoolBase(BaseModel):
    """Base model for MT5 account pool management"""
    mt5_account_number: int = Field(..., ge=100000, le=99999999, description="MT5 account login number")
    broker_name: BrokerCode = Field(..., description="Broker identifier")
    account_type: MT5AccountType = Field(MT5AccountType.INVESTMENT, description="Account purpose")
    investor_password: str = Field(..., min_length=1, description="⚠️ INVESTOR PASSWORD ONLY - Not trading password")
    mt5_server: Optional[str] = Field(None, description="MT5 server address")
    notes: Optional[str] = Field(None, max_length=1000, description="Account notes and comments")
    
    @validator('investor_password')
    def validate_investor_password(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('⚠️ CRITICAL: Investor password is required - This system ONLY accepts INVESTOR passwords')
        return v.strip()

class MT5AccountPoolCreate(MT5AccountPoolBase):
    """Model for adding new MT5 account to pool"""
    pass

class MT5AccountPool(MT5AccountPoolBase):
    """Complete MT5 account pool model"""
    pool_id: str = Field(default_factory=lambda: f"pool_{uuid.uuid4().hex[:16]}")
    status: MT5AccountPoolStatus = Field(MT5AccountPoolStatus.AVAILABLE, description="Current allocation status")
    
    # Allocation tracking
    allocated_to_client_id: Optional[str] = Field(None, description="Client ID if allocated")
    allocated_to_investment_id: Optional[str] = Field(None, description="Investment ID if allocated")
    allocated_amount: Optional[Decimal] = Field(None, ge=0, description="Allocated amount")
    allocation_date: Optional[datetime] = Field(None, description="When account was allocated")
    allocated_by_admin: Optional[str] = Field(None, description="Admin who allocated the account")
    
    # Deallocation tracking
    deallocation_requested_by: Optional[str] = Field(None, description="Admin who requested deallocation")
    deallocation_request_date: Optional[datetime] = Field(None, description="When deallocation was requested")
    deallocation_reason: Optional[str] = Field(None, description="Reason for deallocation")
    deallocation_approved_by: Optional[str] = Field(None, description="Admin who approved deallocation")
    deallocation_approved_date: Optional[datetime] = Field(None, description="When deallocation was approved")
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by_admin: Optional[str] = Field(None, description="Admin who added account to pool")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v is not None else None
        }

class MT5AccountPoolUpdate(BaseModel):
    """Model for updating MT5 account pool entry"""
    broker_name: Optional[BrokerCode] = None
    account_type: Optional[MT5AccountType] = None
    investor_password: Optional[str] = Field(None, description="⚠️ INVESTOR PASSWORD ONLY - Update with care")
    mt5_server: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=1000)
    status: Optional[MT5AccountPoolStatus] = None
    
    @validator('investor_password')
    def validate_investor_password_update(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError('⚠️ CRITICAL: Investor password cannot be empty - This system ONLY accepts INVESTOR passwords')
        return v.strip() if v else None

class MT5InvestmentMapping(BaseModel):
    """Model for mapping MT5 accounts to investments"""
    mapping_id: str = Field(default_factory=lambda: f"map_{uuid.uuid4().hex[:16]}")
    investment_id: str = Field(..., description="FIDUS investment identifier")
    client_id: str = Field(..., description="Client identifier")
    fund_code: str = Field(..., description="Fund code (CORE, BALANCE, DYNAMIC, UNLIMITED)")
    
    # MT5 Account allocation
    mt5_account_number: int = Field(..., description="MT5 account number from pool")
    allocated_amount: Decimal = Field(..., gt=0, description="Amount allocated to this MT5 account")
    
    # Allocation metadata
    allocation_notes: str = Field(..., min_length=1, max_length=2000, description="⚠️ MANDATORY: Notes explaining this allocation")
    allocated_by_admin: str = Field(..., description="Admin user who made this allocation")
    allocation_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Status tracking
    status: str = Field("active", description="Mapping status")
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @validator('allocation_notes')
    def validate_allocation_notes(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Allocation notes are mandatory and must be at least 10 characters explaining the allocation reason')
        return v.strip()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v is not None else None
        }

class MT5InvestmentMappingCreate(BaseModel):
    """Model for creating MT5 investment mapping"""
    investment_id: str = Field(..., description="FIDUS investment identifier")
    mt5_account_number: int = Field(..., description="MT5 account number from pool")
    allocated_amount: Decimal = Field(..., gt=0, description="Amount allocated to this MT5 account")
    allocation_notes: str = Field(..., min_length=1, max_length=2000, description="⚠️ MANDATORY: Notes explaining this allocation")
    
    @validator('allocation_notes')
    def validate_allocation_notes_create(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Allocation notes are mandatory and must be at least 10 characters explaining the allocation reason')
        return v.strip()

class MT5InvestmentMappingUpdate(BaseModel):
    """Model for updating MT5 investment mapping"""
    allocated_amount: Optional[Decimal] = Field(None, gt=0)
    allocation_notes: str = Field(..., min_length=1, max_length=2000, description="⚠️ MANDATORY: Notes explaining this change")
    status: Optional[str] = None
    
    @validator('allocation_notes')
    def validate_update_notes(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Update notes are mandatory and must be at least 10 characters explaining the change reason')
        return v.strip()

class DeallocationRequest(BaseModel):
    """Model for MT5 account deallocation requests"""
    request_id: str = Field(default_factory=lambda: f"dealloc_{uuid.uuid4().hex[:16]}")
    mt5_account_number: int = Field(..., description="MT5 account number to deallocate")
    client_id: str = Field(..., description="Client ID for the allocation")
    investment_id: str = Field(..., description="Investment ID for the allocation")
    
    # Request details
    reason_notes: str = Field(..., min_length=10, max_length=2000, description="⚠️ MANDATORY: Detailed reason for deallocation")
    requested_by_admin: str = Field(..., description="Admin requesting deallocation")
    request_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Approval workflow
    status: str = Field("pending_approval", description="Request status")
    approved_by_admin: Optional[str] = Field(None, description="Admin who approved/rejected")
    approval_date: Optional[datetime] = Field(None, description="Approval/rejection date")
    approval_notes: Optional[str] = Field(None, max_length=1000, description="Additional notes from approver")
    
    # Original allocation info (for audit)
    original_allocated_amount: Decimal = Field(..., description="Original allocation amount")
    original_allocation_date: datetime = Field(..., description="Original allocation date")
    original_allocation_notes: str = Field(..., description="Original allocation notes")
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @validator('reason_notes')
    def validate_reason_notes(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Deallocation reason is mandatory and must be at least 10 characters')
        return v.strip()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v is not None else None
        }

class MT5AllocationAuditLog(BaseModel):
    """Audit log for all MT5 allocation changes"""
    audit_id: str = Field(default_factory=lambda: f"audit_{uuid.uuid4().hex[:16]}")
    
    # What changed
    action_type: str = Field(..., description="Type of action (create, update, delete, allocate, deallocate)")
    mt5_account_number: int = Field(..., description="MT5 account affected")
    investment_id: Optional[str] = Field(None, description="Investment affected")
    client_id: Optional[str] = Field(None, description="Client affected")
    
    # Change details
    old_values: Optional[Dict[str, Any]] = Field(None, description="Previous values")
    new_values: Optional[Dict[str, Any]] = Field(None, description="New values")
    change_notes: str = Field(..., description="⚠️ MANDATORY: Notes explaining the change")
    
    # Who and when
    admin_user_id: str = Field(..., description="Admin who made the change")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Additional context
    ip_address: Optional[str] = Field(None, description="IP address of admin")
    user_agent: Optional[str] = Field(None, description="Browser/client info")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class InvestmentSummary(BaseModel):
    """Summary view of investment with multiple MT5 mappings"""
    investment_id: str
    client_id: str
    fund_code: str
    total_investment_amount: Decimal
    
    # MT5 Account mappings
    mt5_mappings: List[Dict[str, Any]] = Field(default_factory=list)
    total_mapped_amount: Decimal = Field(default=Decimal(0))
    mapping_validation_status: str = Field("pending", description="valid, invalid, or pending")
    
    # Client separation accounts
    interest_separation_account: Optional[int] = Field(None, description="MT5 account for interest tracking")
    gains_separation_account: Optional[int] = Field(None, description="MT5 account for gains tracking")
    
    created_at: datetime
    updated_at: datetime
    
    @property
    def is_mapping_valid(self) -> bool:
        """Check if MT5 mappings sum equals total investment"""
        return abs(self.total_mapped_amount - self.total_investment_amount) < Decimal('0.01')
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v is not None else None
        }

# Response Models for API

class MT5AccountPoolResponse(BaseModel):
    """API response for MT5 account pool"""
    pool_id: str
    mt5_account_number: int
    broker_name: BrokerCode
    account_type: MT5AccountType
    status: MT5AccountPoolStatus
    mt5_server: Optional[str]
    notes: Optional[str]
    
    # Allocation info (masked for security)
    is_allocated: bool
    allocated_to_client_id: Optional[str]
    allocation_date: Optional[datetime]
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class InvestmentWithMappingsResponse(BaseModel):
    """API response for investment with MT5 mappings"""
    investment_id: str
    client_id: str
    fund_code: str
    principal_amount: Decimal
    
    # MT5 mappings (admin view only)
    mt5_mappings: List[Dict[str, Any]]
    total_mapped_amount: Decimal
    mapping_is_valid: bool
    
    # Separation accounts
    interest_separation_account: Optional[int]
    gains_separation_account: Optional[int]
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None
        }