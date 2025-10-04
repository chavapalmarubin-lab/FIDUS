"""
User Model for FIDUS Investment Management Platform
Pydantic models for user data validation and serialization
"""

from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    CLIENT = "client"
    COMPLIANCE_OFFICER = "compliance_officer"
    MANAGER = "manager"

class KYCStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_REVIEW = "in_review"

class AMLStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_REVIEW = "in_review"

class UserBase(BaseModel):
    """Base user model with common fields"""
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9._-]+$")
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, pattern="^[+]?[0-9\\s\\-\\(\\)]{7,20}$")
    user_type: UserRole
    is_active: bool = True
    is_verified: bool = False
    profile_picture: Optional[str] = None
    kyc_status: KYCStatus = KYCStatus.PENDING
    aml_status: AMLStatus = AMLStatus.PENDING
    notes: Optional[str] = Field(None, max_length=2000)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').replace('-', '').replace('.', '').isalnum():
            raise ValueError('Username must be alphanumeric with optional . _ - characters')
        return v.lower()
    
    @validator('email')
    def email_lowercase(cls, v):
        return v.lower()

class UserCreate(UserBase):
    """Model for creating a new user"""
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserUpdate(BaseModel):
    """Model for updating user information"""
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, pattern="^\\+?[1-9]\\d{1,14}$")
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    profile_picture: Optional[str] = None
    kyc_status: Optional[KYCStatus] = None
    aml_status: Optional[AMLStatus] = None
    notes: Optional[str] = Field(None, max_length=2000)

class UserPasswordUpdate(BaseModel):
    """Model for password updates"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class User(UserBase):
    """Complete user model with all fields"""
    user_id: str = Field(..., alias="_id")
    password_hash: Optional[str] = None  # Never expose in API responses
    login_attempts: int = 0
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class UserResponse(BaseModel):
    """User model for API responses (no sensitive data)"""
    user_id: str
    username: str
    email: str
    full_name: Optional[str]
    phone: Optional[str]
    user_type: UserRole
    is_active: bool
    is_verified: bool
    profile_picture: Optional[str]
    kyc_status: KYCStatus
    aml_status: AMLStatus
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class UserLogin(BaseModel):
    """Model for user login"""
    username: str
    password: str

class UserLoginResponse(BaseModel):
    """Model for login response"""
    success: bool
    message: str
    user: Optional[UserResponse] = None
    token: Optional[str] = None
    expires_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class UserStats(BaseModel):
    """User statistics model"""
    total_users: int
    active_users: int
    verified_users: int
    by_role: dict
    by_kyc_status: dict
    by_aml_status: dict
    recent_registrations: int  # Last 30 days

class UserSearch(BaseModel):
    """User search parameters"""
    query: Optional[str] = None
    user_type: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    kyc_status: Optional[KYCStatus] = None
    aml_status: Optional[AMLStatus] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    limit: int = Field(default=50, le=100)
    skip: int = Field(default=0, ge=0)
    sort_by: str = Field(default="created_at", pattern="^(username|email|created_at|updated_at|last_login)$")
    sort_order: int = Field(default=-1, ge=-1, le=1)  # -1 for desc, 1 for asc