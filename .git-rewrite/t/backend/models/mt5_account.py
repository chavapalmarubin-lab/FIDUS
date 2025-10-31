"""
MT5 Account Model for FIDUS Investment Management Platform
Pydantic models for MT5 account data and trading operations
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from enum import Enum

class BrokerCode(str, Enum):
    MULTIBANK = "multibank"
    DOOTECHNOLOGY = "dootechnology"
    VTMARKETS = "vtmarkets"
    MEXATLANTIC = "mexatlantic"
    CUSTOM = "custom"

class MT5AccountStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    CLOSED = "closed"

class OrderType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    BUY_LIMIT = "BUY_LIMIT"
    SELL_LIMIT = "SELL_LIMIT"
    BUY_STOP = "BUY_STOP"
    SELL_STOP = "SELL_STOP"

class MT5AccountBase(BaseModel):
    """Base MT5 account model"""
    account_id: str = Field(..., description="Unique FIDUS account identifier")
    client_id: str = Field(..., description="Reference to user ID")
    mt5_login: int = Field(..., ge=100000, le=99999999, description="MT5 account number")
    broker_code: BrokerCode = Field(..., description="Broker identifier")
    broker_name: str = Field(..., description="Human-readable broker name")
    mt5_server: str = Field(..., description="MT5 server address")
    fund_code: Optional[str] = Field(None, description="Associated FIDUS fund")
    is_active: bool = Field(True, description="Account active status")
    is_demo: bool = Field(False, description="Demo account flag")
    
    @validator('account_id')
    def validate_account_id(cls, v):
        if not v.startswith('mt5_'):
            raise ValueError('Account ID must start with mt5_')
        return v

class MT5AccountCreate(MT5AccountBase):
    """Model for creating MT5 account"""
    encrypted_password: str = Field(..., description="Encrypted MT5 password")
    initial_balance: Optional[Decimal] = Field(None, ge=0, description="Initial account balance")

class MT5Account(MT5AccountBase):
    """Complete MT5 account model"""
    encrypted_password: str = Field(..., description="Encrypted MT5 password")
    status: MT5AccountStatus = Field(MT5AccountStatus.PENDING, description="Account status")
    
    # Account financial data
    balance: Optional[Decimal] = Field(None, description="Current balance")
    equity: Optional[Decimal] = Field(None, description="Current equity")
    margin: Optional[Decimal] = Field(None, description="Used margin")
    free_margin: Optional[Decimal] = Field(None, description="Free margin")
    margin_level: Optional[Decimal] = Field(None, description="Margin level percentage")
    profit: Optional[Decimal] = Field(None, description="Current profit/loss")
    
    # Account metadata
    currency: Optional[str] = Field(None, description="Account currency")
    leverage: Optional[int] = Field(None, description="Account leverage")
    trade_allowed: Optional[bool] = Field(None, description="Trading allowed flag")
    
    # Investment tracking
    total_allocated: Decimal = Field(default=Decimal(0), description="Total amount allocated")
    investment_ids: List[str] = Field(default_factory=list, description="Linked investment IDs")
    
    # Synchronization
    last_sync: Optional[datetime] = Field(None, description="Last data sync timestamp")
    sync_status: str = Field("pending", description="Last sync status")
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v is not None else None
        }

class MT5AccountUpdate(BaseModel):
    """Model for updating MT5 account"""
    broker_name: Optional[str] = None
    mt5_server: Optional[str] = None
    fund_code: Optional[str] = None
    is_active: Optional[bool] = None
    status: Optional[MT5AccountStatus] = None
    total_allocated: Optional[Decimal] = Field(None, ge=0)

class MT5AccountResponse(BaseModel):
    """MT5 account response model"""
    account_id: str
    client_id: str
    mt5_login: int
    broker_code: BrokerCode
    broker_name: str
    mt5_server: str
    fund_code: Optional[str]
    is_active: bool
    is_demo: bool
    status: MT5AccountStatus
    
    # Financial data
    balance: Optional[Decimal]
    equity: Optional[Decimal]
    margin: Optional[Decimal]
    free_margin: Optional[Decimal]
    margin_level: Optional[Decimal]
    profit: Optional[Decimal]
    
    # Metadata
    currency: Optional[str]
    leverage: Optional[int]
    trade_allowed: Optional[bool]
    total_allocated: Decimal
    investment_ids: List[str]
    last_sync: Optional[datetime]
    sync_status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v is not None else None
        }

class MT5Position(BaseModel):
    """MT5 trading position model"""
    ticket: int = Field(..., description="Position ticket number")
    symbol: str = Field(..., description="Trading symbol")
    position_type: str = Field(..., description="BUY or SELL")
    volume: Decimal = Field(..., description="Position volume in lots")
    price_open: Decimal = Field(..., description="Opening price")
    price_current: Decimal = Field(..., description="Current price")
    sl: Optional[Decimal] = Field(None, description="Stop loss price")
    tp: Optional[Decimal] = Field(None, description="Take profit price")
    profit: Decimal = Field(..., description="Current profit/loss")
    swap: Decimal = Field(default=Decimal(0), description="Swap charges")
    commission: Decimal = Field(default=Decimal(0), description="Commission charges")
    comment: Optional[str] = Field(None, description="Position comment")
    magic: Optional[int] = Field(None, description="Magic number")
    time_open: datetime = Field(..., description="Position open time")
    time_update: Optional[datetime] = Field(None, description="Last update time")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v is not None else None
        }

class MT5Order(BaseModel):
    """MT5 pending order model"""
    ticket: int = Field(..., description="Order ticket number")
    symbol: str = Field(..., description="Trading symbol")
    order_type: OrderType = Field(..., description="Order type")
    volume: Decimal = Field(..., description="Order volume in lots")
    price_open: Decimal = Field(..., description="Order price")
    sl: Optional[Decimal] = Field(None, description="Stop loss price")
    tp: Optional[Decimal] = Field(None, description="Take profit price")
    comment: Optional[str] = Field(None, description="Order comment")
    magic: Optional[int] = Field(None, description="Magic number")
    time_setup: datetime = Field(..., description="Order setup time")
    time_expiration: Optional[datetime] = Field(None, description="Order expiration time")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v is not None else None
        }

class MT5Deal(BaseModel):
    """MT5 trade deal (historical) model"""
    ticket: int = Field(..., description="Deal ticket number")
    order: int = Field(..., description="Order ticket that created this deal")
    position: int = Field(..., description="Position ticket")
    symbol: str = Field(..., description="Trading symbol")
    deal_type: str = Field(..., description="Deal type (BUY, SELL, BALANCE, etc.)")
    volume: Decimal = Field(..., description="Deal volume")
    price: Decimal = Field(..., description="Deal price")
    profit: Decimal = Field(..., description="Deal profit/loss")
    swap: Decimal = Field(default=Decimal(0), description="Swap charges")
    commission: Decimal = Field(default=Decimal(0), description="Commission charges")
    comment: Optional[str] = Field(None, description="Deal comment")
    magic: Optional[int] = Field(None, description="Magic number")
    time: datetime = Field(..., description="Deal execution time")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v is not None else None
        }

class MT5AccountSummary(BaseModel):
    """Summary of MT5 account performance"""
    account_id: str
    client_id: str
    mt5_login: int
    
    # Current status
    balance: Decimal
    equity: Decimal
    profit: Decimal
    margin_level: Decimal
    
    # Performance metrics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: Decimal
    
    # Financial metrics
    total_profit: Decimal
    total_loss: Decimal
    net_profit: Decimal
    max_drawdown: Decimal
    
    # Volume metrics
    total_volume: Decimal
    average_trade_size: Decimal
    
    # Time metrics
    first_trade_date: Optional[datetime]
    last_trade_date: Optional[datetime]
    active_days: int
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v is not None else None
        }

class MT5BridgeRequest(BaseModel):
    """Request model for MT5 bridge operations"""
    operation: str = Field(..., description="Operation type")
    parameters: Dict = Field(default_factory=dict, description="Operation parameters")
    timeout: Optional[int] = Field(30, description="Timeout in seconds")

class MT5BridgeResponse(BaseModel):
    """Response model from MT5 bridge"""
    success: bool = Field(..., description="Operation success status")
    data: Optional[Dict] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if failed")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }