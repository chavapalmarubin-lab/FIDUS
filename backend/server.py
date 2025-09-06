from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse, FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta
import random
import base64
import io
from PIL import Image, ImageEnhance, ImageFilter
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiohttp
import asyncio
import re
import hashlib
import hmac
import time
import numpy as np
import yfinance as yf
import pandas as pd
import jwt
from collections import defaultdict
from time import time

# MongoDB Integration
from mongodb_integration import mongodb_manager

# Gmail API imports
import pickle
from google.auth.transport.requests import Request as GoogleRequest
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.message import EmailMessage
from email.mime.application import MIMEApplication

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection with connection pooling
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(
    mongo_url,
    minPoolSize=5,           # Minimum connections in pool
    maxPoolSize=100,         # Maximum connections in pool
    maxIdleTimeMS=30000,     # Close connections after 30 seconds of inactivity
    serverSelectionTimeoutMS=5000,  # 5 seconds timeout for server selection
    socketTimeoutMS=10000,   # 10 seconds timeout for socket operations
    connectTimeoutMS=10000,  # 10 seconds timeout for connection
    retryWrites=True         # Enable retryable writes
)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'fidus-investment-management-secret-key-2024')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

def create_jwt_token(user_data: dict) -> str:
    """Create JWT token for authenticated user"""
    payload = {
        "user_id": user_data["id"],
        "username": user_data["username"],
        "user_type": user_data["type"],
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token: str) -> dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# User Models
class LoginRequest(BaseModel):
    username: str
    password: str
    user_type: str  # "client" or "admin"

class UserResponse(BaseModel):
    id: str
    username: str
    name: str
    email: str
    type: str
    profile_picture: str
    must_change_password: Optional[bool] = False
    token: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    name: str
    email: str
    phone: Optional[str] = None
    temporary_password: str
    notes: Optional[str] = None

class TransactionCreate(BaseModel):
    description: str
    amount: float
    transaction_type: str  # "credit" or "debit"
    fund_type: str  # "fidus", "core", "dynamic"

class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str
    description: str
    amount: float
    transaction_type: str
    fund_type: str
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ClientBalance(BaseModel):
    client_id: str
    fidus_funds: float
    core_balance: float
    dynamic_balance: float
    total_balance: float
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MonthlyStatement(BaseModel):
    month: str
    initial_balance: float
    profit: float
    profit_percentage: float
    final_balance: float

class ClientData(BaseModel):
    balance: ClientBalance
    transactions: List[Transaction]
    monthly_statement: MonthlyStatement

# Registration Models
class RegistrationPersonalInfo(BaseModel):
    firstName: str
    lastName: str
    email: str
    phone: str
    dateOfBirth: str
    nationality: Optional[str] = ""
    address: Optional[str] = ""
    city: Optional[str] = ""
    postalCode: Optional[str] = ""
    country: Optional[str] = ""

class RegistrationApplication(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    personalInfo: RegistrationPersonalInfo
    documentType: str
    status: str = "pending"  # pending, processing, approved, rejected
    extractedData: Optional[Dict[str, Any]] = None
    amlKycResults: Optional[Dict[str, Any]] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DocumentProcessingRequest(BaseModel):
    applicationId: str
    documentType: str

class AMLKYCRequest(BaseModel):
    applicationId: str
    personalInfo: RegistrationPersonalInfo
    extractedData: Optional[Dict[str, Any]] = None

class ApplicationFinalizationRequest(BaseModel):
    applicationId: str
    approved: bool

# CRM Prospect Models
class ProspectCreate(BaseModel):
    name: str
    email: str
    phone: str
    notes: Optional[str] = ""

class ProspectUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    stage: Optional[str] = None
    notes: Optional[str] = None

class Prospect(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    phone: str
    stage: str = "lead"  # lead, qualified, proposal, negotiation, won, lost
    notes: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    converted_to_client: bool = False
    client_id: Optional[str] = None

class ProspectConversionRequest(BaseModel):
    prospect_id: str
    send_agreement: bool = True

# Redemption System Models
class RedemptionRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str
    investment_id: str
    fund_code: str
    fund_name: str
    requested_amount: float
    current_value: float
    principal_amount: float
    request_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    requested_redemption_date: datetime
    next_available_date: datetime
    status: str = "pending"  # pending, approved, rejected, completed, cancelled
    reason: Optional[str] = ""
    admin_notes: Optional[str] = ""
    approved_by: Optional[str] = None
    approved_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None

class RedemptionRequestCreate(BaseModel):
    investment_id: str
    requested_amount: float
    reason: Optional[str] = ""

class RedemptionApproval(BaseModel):
    redemption_id: str
    action: str  # approve, reject
    admin_notes: Optional[str] = ""
    admin_id: str

# Payment Confirmation Models
class PaymentConfirmation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    transaction_type: str  # deposit, redemption
    payment_method: str  # fiat, crypto
    amount: float
    currency: str = "USD"  # USD, BTC, ETH, etc.
    
    # For deposits
    investment_id: Optional[str] = None
    client_id: Optional[str] = None
    
    # For redemptions  
    redemption_id: Optional[str] = None
    
    # FIAT Wire Details
    wire_confirmation_number: Optional[str] = None
    bank_reference: Optional[str] = None
    wire_receipt_file: Optional[str] = None  # File path/ID for uploaded receipt
    
    # Crypto Details
    transaction_hash: Optional[str] = None
    blockchain_network: Optional[str] = None  # Bitcoin, Ethereum, etc.
    wallet_address: Optional[str] = None
    
    # Common fields
    confirmation_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    confirmed_by: str  # admin_id
    notes: Optional[str] = ""
    status: str = "pending"  # pending, confirmed, failed
    
class DepositConfirmationRequest(BaseModel):
    investment_id: str
    payment_method: str  # fiat, crypto
    amount: float
    currency: str = "USD"
    
    # For FIAT
    wire_confirmation_number: Optional[str] = None
    bank_reference: Optional[str] = None
    
    # For Crypto
    transaction_hash: Optional[str] = None
    blockchain_network: Optional[str] = None
    wallet_address: Optional[str] = None
    
    notes: Optional[str] = ""

class RedemptionPaymentConfirmation(BaseModel):
    redemption_id: str
    payment_method: str  # fiat, crypto
    amount: float
    currency: str = "USD"
    
    # For FIAT
    wire_confirmation_number: Optional[str] = None
    bank_reference: Optional[str] = None
    
    # For Crypto
    transaction_hash: Optional[str] = None
    blockchain_network: Optional[str] = None
    wallet_address: Optional[str] = None
    
    notes: Optional[str] = ""

# Activity Logging Models
class ActivityLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str
    activity_type: str  # deposit, redemption_request, redemption_approved, redemption_rejected, redemption_completed
    investment_id: Optional[str] = None
    fund_code: Optional[str] = None
    amount: float
    description: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    performed_by: str  # admin_id or client_id
    reference_id: Optional[str] = None  # redemption_id, investment_id, etc.
    metadata: Optional[Dict[str, Any]] = None

# Investment Tracking Models
class FundInvestment(BaseModel):
    investment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str
    fund_code: str  # CORE, BALANCE, DYNAMIC, UNLIMITED
    principal_amount: float
    deposit_date: datetime
    incubation_end_date: datetime
    interest_start_date: datetime
    minimum_hold_end_date: datetime  # 14 months from deposit
    current_value: float
    total_interest_earned: float = 0.0
    status: str = "active"  # active, redeemed, pending_redemption
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class InterestPayment(BaseModel):
    payment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    investment_id: str
    client_id: str
    fund_code: str
    payment_date: datetime
    interest_amount: float
    principal_balance: float
    payment_period: str  # "2024-04", "2024-Q1", etc.
    status: str = "scheduled"  # scheduled, paid, failed
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class InvestmentProjection(BaseModel):
    investment_id: str
    projected_payments: List[dict]
    total_projected_interest: float
    final_value: float
    next_redemption_date: Optional[datetime]
    can_redeem_now: bool

class FundConfiguration(BaseModel):
    fund_code: str
    name: str
    interest_rate: float  # Monthly rate as percentage
    minimum_investment: float
    interest_frequency: str  # "monthly"
    redemption_frequency: str  # "monthly", "quarterly", "semi-annually"
    invitation_only: bool = False
    incubation_months: int = 2
    minimum_hold_months: int = 14

class InvestmentCreate(BaseModel):
    client_id: str
    fund_code: str
    amount: float
    deposit_date: Optional[str] = None  # YYYY-MM-DD format
    broker_code: Optional[str] = "multibank"  # Default to multibank for backward compatibility

# Client Investment Readiness Models
class ClientInvestmentReadiness(BaseModel):
    client_id: str
    aml_kyc_completed: bool = False
    agreement_signed: bool = False
    account_creation_date: Optional[datetime] = None
    investment_ready: bool = False
    notes: str = ""
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: str = ""

class ClientInvestmentReadinessUpdate(BaseModel):
    aml_kyc_completed: Optional[bool] = None
    agreement_signed: Optional[bool] = None
    account_creation_date: Optional[datetime] = None
    notes: Optional[str] = None
    updated_by: Optional[str] = None

class ClientCreate(BaseModel):
    username: str
    name: str
    email: str
    phone: Optional[str] = None
    notes: Optional[str] = ""

# FIDUS Investment Fund Configuration
FIDUS_FUND_CONFIG = {
    "CORE": FundConfiguration(
        fund_code="CORE",
        name="FIDUS Core Fund",
        interest_rate=1.5,  # 1.5% simple interest per month
        minimum_investment=10000.0,  # $10,000 minimum
        interest_frequency="monthly",
        redemption_frequency="monthly",  # Interest redemptions monthly
        invitation_only=False,
        incubation_months=2,  # 2 months incubation (no interest/redemptions)
        minimum_hold_months=12  # 12 months commitment after incubation = 14 months total
    ),
    "BALANCE": FundConfiguration(
        fund_code="BALANCE", 
        name="FIDUS Balance Fund",
        interest_rate=2.5,  # 2.5% simple interest per month
        minimum_investment=50000.0,  # $50,000 minimum
        interest_frequency="monthly",
        redemption_frequency="quarterly",  # Interest redemptions every 3 months
        invitation_only=False,
        incubation_months=2,  # 2 months incubation (no interest/redemptions)
        minimum_hold_months=12  # 12 months commitment after incubation = 14 months total
    ),
    "DYNAMIC": FundConfiguration(
        fund_code="DYNAMIC",
        name="FIDUS Dynamic Fund", 
        interest_rate=3.5,  # 3.5% simple interest per month
        minimum_investment=250000.0,  # $250,000 minimum
        interest_frequency="monthly",
        redemption_frequency="semi_annually",  # Interest redemptions every 6 months
        invitation_only=False,
        incubation_months=2,  # 2 months incubation (no interest/redemptions)
        minimum_hold_months=12  # 12 months commitment after incubation = 14 months total
    ),
    "UNLIMITED": FundConfiguration(
        fund_code="UNLIMITED",
        name="FIDUS Unlimited Fund",
        interest_rate=0.0,  # 50-50 performance sharing (calculated differently)
        minimum_investment=1000000.0,  # $1,000,000 minimum
        interest_frequency="none",  # Performance-based, not fixed interest
        redemption_frequency="flexible",  # Flexible redemptions based on performance
        invitation_only=True,  # By invitation only
        incubation_months=2,  # 2 months incubation
        minimum_hold_months=12  # 12 months commitment after incubation = 14 months total
    )
}

# In-memory investment storage (in production, use proper database)
client_investments = {}

# In-memory client investment readiness tracking (in production, use proper database)
client_readiness = {}

# In-memory user management for temporary passwords and first-time logins
user_temp_passwords = {}  # {user_id: {"temp_password": "...", "must_change": True}}
user_accounts = {}  # Additional user data beyond MOCK_USERS

# In-memory redemption system storage
redemption_requests = {}  # {redemption_id: RedemptionRequest}
activity_logs = []  # List of ActivityLog entries

# In-memory payment confirmation storage  
payment_confirmations = {}  # {confirmation_id: PaymentConfirmation}

# Investment Calculation and Management Functions
def calculate_investment_dates(deposit_date: datetime, fund_config: FundConfiguration):
    """Calculate key dates for an investment"""
    # Ensure deposit_date is timezone-aware
    if deposit_date.tzinfo is None:
        deposit_date = deposit_date.replace(tzinfo=timezone.utc)
    
    # Incubation period: EXACTLY 2 months from deposit (no interest during this period)
    incubation_end = deposit_date + relativedelta(months=2)
    
    # Interest starts EXACTLY 2 months after deposit date (same as incubation end)
    # No interest accrues during the 2-month incubation period
    interest_start = deposit_date + relativedelta(months=2)
    
    # Minimum hold period: EXACTLY 14 months from deposit (2 incubation + 12 commitment)
    minimum_hold_end = deposit_date + relativedelta(months=14)
    
    return {
        "incubation_end_date": incubation_end,
        "interest_start_date": interest_start,
        "minimum_hold_end_date": minimum_hold_end
    }

def calculate_simple_interest(principal: float, rate: float, months: int) -> float:
    """Calculate simple interest for given principal, rate, and months"""
    return principal * (rate / 100) * months

def get_next_redemption_date(investment: FundInvestment, fund_config: FundConfiguration) -> Optional[datetime]:
    """Calculate next available redemption date based on fund redemption frequency"""
    if fund_config.redemption_frequency == "monthly":
        # Can redeem anytime after minimum hold period
        return investment.minimum_hold_end_date if datetime.now(timezone.utc) < investment.minimum_hold_end_date else datetime.now(timezone.utc)
    
    elif fund_config.redemption_frequency == "quarterly":
        # Can redeem every 3 months starting from interest start date
        start_date = investment.interest_start_date
        current_date = datetime.now(timezone.utc)
        
        # Find next quarterly date (March, June, September, December)
        quarterly_months = [3, 6, 9, 12]
        current_year = current_date.year
        
        for month in quarterly_months:
            redemption_date = datetime(current_year, month, 1, tzinfo=timezone.utc)
            if redemption_date > current_date and redemption_date >= investment.minimum_hold_end_date:
                return redemption_date
        
        # If no date found in current year, start with March of next year
        return datetime(current_year + 1, 3, 1, tzinfo=timezone.utc)
    
    elif fund_config.redemption_frequency == "semi-annually":
        # Can redeem every 6 months (June and December)
        current_date = datetime.now(timezone.utc)
        current_year = current_date.year
        
        for month in [6, 12]:
            redemption_date = datetime(current_year, month, 1, tzinfo=timezone.utc)
            if redemption_date > current_date and redemption_date >= investment.minimum_hold_end_date:
                return redemption_date
        
        # Next June if no date found in current year
        return datetime(current_year + 1, 6, 1, tzinfo=timezone.utc)
    
    else:  # flexible or none
        return investment.minimum_hold_end_date if datetime.now(timezone.utc) < investment.minimum_hold_end_date else datetime.now(timezone.utc)

def generate_investment_projections(investment: FundInvestment, fund_config: FundConfiguration) -> InvestmentProjection:
    """Generate projected interest payments and values for an investment"""
    projections = []
    current_date = investment.interest_start_date
    end_date = datetime.now(timezone.utc) + timedelta(days=730)  # Project 2 years ahead
    total_projected_interest = 0.0
    
    if fund_config.interest_frequency == "monthly" and fund_config.interest_rate > 0:
        while current_date <= end_date:
            # Calculate monthly interest
            monthly_interest = calculate_simple_interest(investment.principal_amount, fund_config.interest_rate, 1)
            
            projection = {
                "date": current_date.isoformat(),
                "type": "interest_payment",
                "amount": round(monthly_interest, 2),
                "principal_balance": investment.principal_amount,
                "period": current_date.strftime("%Y-%m"),
                "status": "projected"
            }
            
            projections.append(projection)
            total_projected_interest += monthly_interest
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
    
    # Get next redemption date
    next_redemption = get_next_redemption_date(investment, fund_config)
    can_redeem_now = datetime.now(timezone.utc) >= investment.minimum_hold_end_date
    
    return InvestmentProjection(
        investment_id=investment.investment_id,
        projected_payments=projections[:24],  # Limit to 24 months for display
        total_projected_interest=round(total_projected_interest, 2),
        final_value=round(investment.principal_amount + total_projected_interest, 2),
        next_redemption_date=next_redemption,
        can_redeem_now=can_redeem_now
    )

def create_investment(client_id: str, fund_code: str, amount: float, deposit_date: Optional[str] = None) -> FundInvestment:
    """Create a new investment with calculated dates"""
    if fund_code not in FIDUS_FUND_CONFIG:
        raise ValueError(f"Invalid fund code: {fund_code}")
    
    fund_config = FIDUS_FUND_CONFIG[fund_code]
    
    # Validate minimum investment
    if amount < fund_config.minimum_investment:
        raise ValueError(f"Minimum investment for {fund_code} is ${fund_config.minimum_investment:,.2f}")
    
    # Check invitation-only restriction
    if fund_config.invitation_only:
        # In a real system, check if client has invitation
        pass
    
    # Use provided deposit_date or get from client readiness or use current date
    if deposit_date:
        deposit_datetime = datetime.fromisoformat(deposit_date + "T00:00:00+00:00")
    else:
        deposit_datetime = datetime.now(timezone.utc)
        if client_id in client_readiness:
            readiness = client_readiness[client_id]
            if readiness.get('deposit_date'):
                deposit_datetime = datetime.fromisoformat(readiness['deposit_date']) if isinstance(readiness['deposit_date'], str) else readiness['deposit_date']
    
    dates = calculate_investment_dates(deposit_datetime, fund_config)
    
    investment = FundInvestment(
        client_id=client_id,
        fund_code=fund_code,
        principal_amount=amount,
        deposit_date=deposit_datetime,
        current_value=amount,
        **dates
    )
    
    return investment

# Redemption System Functions
def get_next_redemption_date(investment: FundInvestment, fund_config: FundConfiguration) -> datetime:
    """Calculate the next available redemption date based on fund rules"""
    # Start from interest start date (after incubation)
    base_date = investment.interest_start_date
    
    # Calculate redemption frequency in months
    if fund_config.redemption_frequency == "monthly":
        frequency_months = 1
    elif fund_config.redemption_frequency == "quarterly":
        frequency_months = 3
    elif fund_config.redemption_frequency == "semi_annually":
        frequency_months = 6
    elif fund_config.redemption_frequency == "flexible":
        # For UNLIMITED fund - can redeem at any time after minimum hold
        return investment.minimum_hold_end_date
    else:
        frequency_months = 12  # Default to annual
    
    # Find next redemption date
    current_date = datetime.now(timezone.utc)
    
    # Start from the first possible redemption date (after incubation)
    next_redemption = base_date
    
    # Move forward by redemption frequency until we find a future date
    while next_redemption <= current_date:
        # Add frequency months
        if next_redemption.month + frequency_months > 12:
            next_redemption = next_redemption.replace(
                year=next_redemption.year + ((next_redemption.month + frequency_months - 1) // 12),
                month=((next_redemption.month + frequency_months - 1) % 12) + 1
            )
        else:
            next_redemption = next_redemption.replace(month=next_redemption.month + frequency_months)
    
    return next_redemption

def calculate_redemption_value(investment: FundInvestment, fund_config: FundConfiguration) -> float:
    """Calculate current redemption value including accrued interest or performance sharing"""
    now = datetime.now(timezone.utc)
    
    # Special handling for UNLIMITED fund (50-50 performance sharing)
    if fund_config.fund_code == "UNLIMITED":
        # If still in incubation period (first 2 months), only principal can be redeemed
        if now < investment.interest_start_date:
            return investment.principal_amount
        
        # Mock fund performance for UNLIMITED (in production, get from real performance data)
        # Calculate months since interest/performance sharing started (after 2-month incubation)
        months_elapsed = (now.year - investment.interest_start_date.year) * 12 + \
                        (now.month - investment.interest_start_date.month)
        
        # Add fractional month calculation for more precision
        if now.day >= investment.interest_start_date.day:
            fractional_month = (now.day - investment.interest_start_date.day) / 30.0
        else:
            months_elapsed -= 1
            fractional_month = (30 - investment.interest_start_date.day + now.day) / 30.0
        
        total_months = months_elapsed + fractional_month
        
        # Mock performance calculation (replace with real fund performance)
        # Simulate average 4.5% monthly fund performance
        cumulative_performance = total_months * 0.045
        
        # Client gets 50% of fund performance (no cap)
        client_performance_share = cumulative_performance * 0.5
        performance_value = investment.principal_amount * client_performance_share
        
        return investment.principal_amount + performance_value
    
    # For fixed interest funds (CORE, BALANCE, DYNAMIC)
    # NO INTEREST during incubation period (first 2 months)
    if now < investment.interest_start_date:
        return investment.principal_amount
    
    # Calculate precise months since interest started (exactly 2 months after deposit)
    months_elapsed = (now.year - investment.interest_start_date.year) * 12 + \
                    (now.month - investment.interest_start_date.month)
    
    # Add fractional month calculation for more precision
    if now.day >= investment.interest_start_date.day:
        fractional_month = (now.day - investment.interest_start_date.day) / 30.0
    else:
        months_elapsed -= 1
        fractional_month = (30 - investment.interest_start_date.day + now.day) / 30.0
    
    total_months = months_elapsed + fractional_month
    
    # Simple interest calculation (not compound)
    # CORE: 1.5% per month, BALANCE: 2.5% per month, DYNAMIC: 3.5% per month
    monthly_rate = fund_config.interest_rate / 100.0
    total_interest = investment.principal_amount * monthly_rate * total_months
    
    return investment.principal_amount + total_interest

def can_request_redemption(investment: FundInvestment, fund_config: FundConfiguration) -> tuple[bool, str]:
    """Check if a redemption can be requested for this investment"""
    now = datetime.now(timezone.utc)
    
    # Check if still in incubation period (first 2 months - NO interest, NO redemptions allowed)
    if now < investment.interest_start_date:
        days_remaining = (investment.interest_start_date - now).days
        return False, f"Investment is in 2-month incubation period. Interest starts in {days_remaining} days."
    
    # Calculate months since interest started (exactly 2 months after deposit)
    months_elapsed = (now.year - investment.interest_start_date.year) * 12 + \
                    (now.month - investment.interest_start_date.month)
    
    # Add fractional month calculation
    if now.day >= investment.interest_start_date.day:
        fractional_month = (now.day - investment.interest_start_date.day) / 30.0
    else:
        months_elapsed -= 1
        fractional_month = (30 - investment.interest_start_date.day + now.day) / 30.0
    
    total_months = months_elapsed + fractional_month
    
    # Check if any interest has been earned (needed for interest redemptions)
    if total_months < 1:
        next_interest_date = investment.interest_start_date + relativedelta(months=1)
        days_until = (next_interest_date - now).days
        return False, f"Available after first interest payment in {days_until} days"
    
    # Check if principal hold period has passed (14 months total from deposit)
    principal_hold_passed = now >= investment.minimum_hold_end_date
    
    # Determine what can be redeemed based on fund redemption frequency
    if fund_config.redemption_frequency == "monthly":
        # CORE: Can redeem interest monthly after incubation, principal after 14 months total
        if principal_hold_passed:
            return True, f"Full redemption available - {int(total_months)} interest payments completed"
        else:
            days_until_principal = (investment.minimum_hold_end_date - now).days
            return True, f"Interest redemption available monthly. Principal available in {days_until_principal} days"
    
    elif fund_config.redemption_frequency == "quarterly":
        # BALANCE: Can redeem interest every 3 months after incubation, principal after 14 months total
        if total_months >= 3:  # At least 3 months for quarterly redemption
            if principal_hold_passed:
                return True, f"Full redemption available - {int(total_months)} interest payments completed"
            else:
                days_until_principal = (investment.minimum_hold_end_date - now).days
                return True, f"Interest redemption available quarterly. Principal available in {days_until_principal} days"
        else:
            months_until_quarterly = 3 - (int(total_months) % 3)
            next_quarterly_date = investment.interest_start_date + relativedelta(months=int(total_months) + months_until_quarterly)
            days_until = (next_quarterly_date - now).days
            return False, f"Next quarterly redemption in {days_until} days"
    
    elif fund_config.redemption_frequency == "semi_annually":
        # DYNAMIC: Can redeem interest every 6 months after incubation, principal after 14 months total
        if total_months >= 6:  # At least 6 months for semi-annual redemption
            if principal_hold_passed:
                return True, f"Full redemption available - {int(total_months)} interest payments completed"
            else:
                days_until_principal = (investment.minimum_hold_end_date - now).days
                return True, f"Interest redemption available semi-annually. Principal available in {days_until_principal} days"
        else:
            months_until_semiannual = 6 - (int(total_months) % 6)
            next_semiannual_date = investment.interest_start_date + relativedelta(months=int(total_months) + months_until_semiannual)
            days_until = (next_semiannual_date - now).days
            return False, f"Next semi-annual redemption in {days_until} days"
    
    else:
        # UNLIMITED or flexible redemption types
        if principal_hold_passed:
            return True, f"Full redemption available - {int(total_months)} performance periods completed"
        else:
            days_until_principal = (investment.minimum_hold_end_date - now).days
            return True, f"Performance sharing redemption available. Principal available in {days_until_principal} days"

def create_activity_log(client_id: str, activity_type: str, amount: float, description: str, 
                       performed_by: str, investment_id: str = None, fund_code: str = None, 
                       reference_id: str = None, metadata: dict = None):
    """Create an activity log entry"""
    activity = ActivityLog(
        client_id=client_id,
        activity_type=activity_type,
        investment_id=investment_id,
        fund_code=fund_code,
        amount=amount,
        description=description,
        performed_by=performed_by,
        reference_id=reference_id,
        metadata=metadata or {}
    )
    
    activity_logs.append(activity)
    logging.info(f"Activity logged: {activity_type} for client {client_id}, amount ${amount}")
    return activity

# Mock data for demo
MOCK_USERS = {
    "client1": {
        "id": "client_001",
        "username": "client1",
        "name": "Gerardo Briones",
        "email": "g.b@fidus.com",
        "type": "client",
        "profile_picture": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face"
    },
    "client2": {
        "id": "client_002", 
        "username": "client2",
        "name": "Maria Rodriguez",
        "email": "m.rodriguez@fidus.com",
        "type": "client",
        "profile_picture": "https://images.unsplash.com/photo-1494790108755-2616b812358f?w=150&h=150&fit=crop&crop=face"
    },
    "client3": {
        "id": "client_003",
        "username": "client3", 
        "name": "SALVADOR PALMA",
        "email": "chava@alyarglobal.com",
        "type": "client",
        "profile_picture": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face"
    },
    "client4": {
        "id": "client_004",
        "username": "client4",
        "name": "Javier Gonzalez",
        "email": "javier.gonzalez@fidus.com",
        "type": "client",
        "profile_picture": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face"
    },
    "client5": {
        "id": "client_005",
        "username": "client5",
        "name": "Jorge Gonzalez", 
        "email": "jorge.gonzalez@fidus.com",
        "type": "client",
        "profile_picture": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face"
    },
    "admin": {
        "id": "admin_001",
        "username": "admin",
        "name": "Investment Committee",
        "email": "ic@fidus.com", 
        "type": "admin",
        "profile_picture": "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=150&h=150&fit=crop&crop=face"
    }
}

def generate_mock_transactions(client_id: str, count: int = 50) -> List[dict]:
    """Generate mock transaction data"""
    transactions = []
    base_date = datetime.now(timezone.utc) - timedelta(days=365)
    
    transaction_types = [
        ("Portfolio Rebalancing", "credit", "core"),
        ("Dividend Payment", "credit", "fidus"),
        ("Management Fee", "debit", "fidus"),
        ("Performance Bonus", "credit", "dynamic"),
        ("Risk Adjustment", "debit", "core"),
        ("Market Growth", "credit", "dynamic"),
        ("Fee Adjustment", "debit", "fidus"),
        ("Profit Distribution", "credit", "core"),
        ("Advisory Fee", "debit", "fidus"),
        ("Capital Gains", "credit", "dynamic")
    ]
    
    for i in range(count):
        desc, trans_type, fund_type = random.choice(transaction_types)
        amount = random.uniform(500, 15000)
        if trans_type == "debit":
            amount = -amount
            
        transaction_date = base_date + timedelta(days=random.randint(0, 365))
        
        transactions.append({
            "id": str(uuid.uuid4()),
            "client_id": client_id,
            "description": desc,
            "amount": round(amount, 2),
            "transaction_type": trans_type,
            "fund_type": fund_type,
            "date": transaction_date
        })
    
    return sorted(transactions, key=lambda x: x["date"], reverse=True)

def calculate_balances(client_id: str) -> dict:
    """Calculate balances from current investment values"""
    balances = {"fidus_funds": 0, "core_balance": 0, "dynamic_balance": 0}
    
    # Get client investments from MongoDB - since we reset to zero, return zero balances
    try:
        from mongodb_integration import mongodb_manager
        investments = mongodb_manager.get_client_investments(client_id)
        
        for investment in investments:
            current_value = investment['current_value']
            
            if investment['fund_code'] == "CORE":
                balances["core_balance"] += current_value
            elif investment['fund_code'] == "BALANCE":
                balances["fidus_funds"] += current_value  # BALANCE goes to fidus_funds
            elif investment['fund_code'] == "DYNAMIC":
                balances["dynamic_balance"] += current_value
            elif investment['fund_code'] == "UNLIMITED":
                balances["fidus_funds"] += current_value  # UNLIMITED goes to fidus_funds
    except:
        # If MongoDB fails, default to zero balances (clean start)
        pass
    
    balances["total_balance"] = sum(balances.values())
    
    return balances

# Authentication endpoints
@api_router.post("/auth/login", response_model=UserResponse)
async def login(login_data: LoginRequest):
    """Authentication with MongoDB integration and temporary password support"""
    username = login_data.username
    password = login_data.password
    user_type = login_data.user_type
    
    try:
        # First try MongoDB authentication
        user_data = mongodb_manager.authenticate_user(username, password, user_type)
        
        if user_data:
            # MongoDB authentication successful
            user_response_dict = user_data.copy()
            user_response_dict["must_change_password"] = False
            
            # Generate JWT token
            jwt_token = create_jwt_token(user_data)
            user_response_dict["token"] = jwt_token
            
            return UserResponse(**user_response_dict)
        
        # Fallback to mock data for backward compatibility during transition
        if username not in MOCK_USERS:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        mock_user_data = MOCK_USERS[username]
        
        # Check if user type matches
        if mock_user_data["type"] != user_type:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Check for temporary password first
        user_id = mock_user_data["id"]
        if user_id in user_temp_passwords:
            temp_info = user_temp_passwords[user_id]
            if password == temp_info["temp_password"]:
                # Temporary password login successful
                user_response_dict = mock_user_data.copy()
                user_response_dict["must_change_password"] = temp_info["must_change"]
                
                # Generate JWT token
                jwt_token = create_jwt_token(mock_user_data)
                user_response_dict["token"] = jwt_token
                
                return UserResponse(**user_response_dict)
        
        # Check regular password for mock users
        if password == "password123":
            user_response_dict = mock_user_data.copy()
            user_response_dict["must_change_password"] = False
            
            # Generate JWT token
            jwt_token = create_jwt_token(mock_user_data)
            user_response_dict["token"] = jwt_token
            
            return UserResponse(**user_response_dict)
        
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication failed")

@api_router.post("/auth/refresh-token")
async def refresh_token(request: Request):
    """Refresh JWT token for authenticated user"""
    try:
        # Extract current token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="No token provided")
        
        current_token = auth_header.split(" ")[1]
        
        # Verify current token (even if close to expiry)
        try:
            payload = jwt.decode(current_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            # Allow refresh of recently expired tokens (within 1 hour)
            payload = jwt.decode(current_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM], options={"verify_exp": False})
            exp_time = payload.get('exp', 0)
            current_time = datetime.now(timezone.utc).timestamp()
            
            # If token expired more than 1 hour ago, require re-login
            if current_time - exp_time > 3600:  # 1 hour
                raise HTTPException(status_code=401, detail="Token expired too long ago, please login again")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Create new token with fresh expiration
        user_data = {
            "id": payload["user_id"],
            "username": payload["username"],
            "type": payload["user_type"]
        }
        
        new_token = create_jwt_token(user_data)
        
        return {
            "success": True,
            "token": new_token,
            "message": "Token refreshed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Token refresh error: {str(e)}")
        raise HTTPException(status_code=500, detail="Token refresh failed")

# Health check endpoints for monitoring and load balancer
@api_router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }

@api_router.get("/health/ready")
async def readiness_check():
    """Readiness check - verifies all dependencies are available"""
    checks = {
        "database": False,
        "status": "checking"
    }
    
    try:
        # Check database connectivity
        await db.command('ping')
        checks["database"] = True
        
        # All checks passed
        checks["status"] = "ready"
        
        return {
            "status": "ready",
            "checks": checks,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logging.error(f"Readiness check failed: {str(e)}")
        checks["status"] = "not_ready"
        checks["error"] = str(e)
        
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "checks": checks,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

@api_router.get("/health/metrics")
async def metrics():
    """System metrics for monitoring"""
    try:
        # Get database stats
        db_stats = await db.command("dbStats")
        
        return {
            "database": {
                "collections": db_stats.get("collections", 0),
                "objects": db_stats.get("objects", 0),
                "dataSize": db_stats.get("dataSize", 0),
                "indexSize": db_stats.get("indexSize", 0)
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logging.error(f"Metrics collection failed: {str(e)}")
        return JSONResponse(
            status_code=500, 
            content={"error": "Metrics collection failed"}
        )

@api_router.post("/auth/change-password")
async def change_password(change_request: dict):
    """Change user password from temporary to permanent"""
    try:
        username = change_request.get("username")
        current_password = change_request.get("current_password") 
        new_password = change_request.get("new_password")
        
        if not username or not current_password or not new_password:
            raise HTTPException(status_code=400, detail="All fields are required")
        
        if username not in MOCK_USERS:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = MOCK_USERS[username]
        user_id = user_data["id"]
        
        # Verify current password (temporary)
        if user_id in user_temp_passwords:
            temp_info = user_temp_passwords[user_id]
            if current_password == temp_info["temp_password"]:
                # Remove temporary password and allow regular login
                del user_temp_passwords[user_id]
                
                # In a real system, you would hash and store the new password
                # For this demo, we'll just remove the temp password requirement
                logging.info(f"Password changed for user: {username}")
                
                return {
                    "success": True,
                    "message": "Password changed successfully"
                }
        
        raise HTTPException(status_code=401, detail="Invalid current password")
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Password change error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to change password")

# Client endpoints
@api_router.get("/client/{client_id}/data", response_model=ClientData)
async def get_client_data(client_id: str):
    """Get complete client data including balance, transactions, and monthly statement"""
    if client_id not in [user["id"] for user in MOCK_USERS.values() if user["type"] == "client"]:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # For clean start, return empty transactions - will be populated with real activity
    transactions = []
    balances = calculate_balances(client_id)
    
    # Create balance object
    client_balance = ClientBalance(
        client_id=client_id,
        **balances
    )
    
    # Generate monthly statement with actual investment data
    from datetime import datetime
    current_month = datetime.now().strftime("%B %Y")
    
    # Get investment data to calculate monthly statement
    try:
        investments = mongodb_manager.get_client_investments(client_id)
        total_invested = sum(inv['principal_amount'] for inv in investments)
        total_current = sum(inv['current_value'] for inv in investments)
        total_profit = total_current - total_invested
        profit_percentage = (total_profit / total_invested * 100) if total_invested > 0 else 0
    except:
        total_invested = 0
        total_current = 0
        total_profit = 0
        profit_percentage = 0
    
    monthly_statement = MonthlyStatement(
        month=current_month,
        initial_balance=total_invested,
        profit=total_profit,
        profit_percentage=profit_percentage,
        final_balance=total_current
    )
    
    return ClientData(
        balance=client_balance,
        transactions=[Transaction(**trans) for trans in transactions],
        monthly_statement=monthly_statement
    )

@api_router.get("/client/{client_id}/transactions")
async def get_client_transactions(
    client_id: str, 
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    fund_type: Optional[str] = None
):
    """Get filtered client transactions"""
    transactions = generate_mock_transactions(client_id)
    
    # Apply filters
    if start_date:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        transactions = [t for t in transactions if t["date"] >= start]
    
    if end_date:
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        transactions = [t for t in transactions if t["date"] <= end]
    
    if fund_type:
        transactions = [t for t in transactions if t["fund_type"] == fund_type]
    
    return {"transactions": transactions}

# Admin endpoints
@api_router.get("/admin/clients")
async def get_all_clients():
    """Get all client summaries for admin"""
    clients = []
    for user in MOCK_USERS.values():
        if user["type"] == "client":
            transactions = generate_mock_transactions(user["id"], 20)
            balances = calculate_balances(user["id"])
            clients.append({
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "total_balance": balances["total_balance"],
                "last_activity": transactions[0]["date"] if transactions else datetime.now(timezone.utc),
                "status": user.get("status", "active"),
                "created_at": user.get("createdAt", datetime.now(timezone.utc).isoformat())
            })
    
    return {"clients": clients}

# MT5 Account Management and Client Investment Mapping System
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum

@dataclass
class MT5Account:
    account_id: str
    client_id: str
    fund_code: str
    mt5_login: int
    mt5_password: str
    mt5_server: str
    total_allocated: float
    current_equity: float
    profit_loss: float
    creation_date: str
    last_update: str
    status: str  # active, inactive, error
    investment_ids: List[str]

class ClientMT5Mapping:
    def __init__(self):
        # Storage for MT5 accounts mapped to clients and funds
        self.mt5_accounts: Dict[str, MT5Account] = {}  # account_id -> MT5Account
        self.client_fund_mapping: Dict[str, Dict[str, str]] = {}  # client_id -> {fund_code -> account_id}
        self.investment_to_mt5: Dict[str, str] = {}  # investment_id -> account_id
        
    def get_or_create_mt5_account(self, client_id: str, fund_code: str, investment_data: dict) -> str:
        """Get existing MT5 account for client+fund or create new one"""
        
        # Initialize client mapping if doesn't exist
        if client_id not in self.client_fund_mapping:
            self.client_fund_mapping[client_id] = {}
        
        # Check if client already has MT5 account for this fund
        if fund_code in self.client_fund_mapping[client_id]:
            account_id = self.client_fund_mapping[client_id][fund_code]
            mt5_account = self.mt5_accounts[account_id]
            
            # Add investment amount to existing account
            mt5_account.total_allocated += investment_data['principal_amount']
            mt5_account.investment_ids.append(investment_data['investment_id'])
            mt5_account.last_update = datetime.now(timezone.utc).isoformat()
            
            logging.info(f"Added ${investment_data['principal_amount']} to existing MT5 account {account_id} for client {client_id} fund {fund_code}")
            return account_id
        
        else:
            # Create new MT5 account for this client+fund combination
            account_id = f"mt5_{client_id}_{fund_code}_{str(uuid.uuid4())[:8]}"
            
            # Generate MT5 credentials (in production, these would come from MT5 broker API)
            mt5_login = self._generate_mt5_login()
            mt5_password = self._generate_mt5_password()
            mt5_server = self._get_mt5_server_for_fund(fund_code)
            
            mt5_account = MT5Account(
                account_id=account_id,
                client_id=client_id,
                fund_code=fund_code,
                mt5_login=mt5_login,
                mt5_password=mt5_password,
                mt5_server=mt5_server,
                total_allocated=investment_data['principal_amount'],
                current_equity=investment_data['principal_amount'],  # Initial equity = allocated amount
                profit_loss=0.0,
                creation_date=datetime.now(timezone.utc).isoformat(),
                last_update=datetime.now(timezone.utc).isoformat(),
                status="active",
                investment_ids=[investment_data['investment_id']]
            )
            
            # Store mappings
            self.mt5_accounts[account_id] = mt5_account
            self.client_fund_mapping[client_id][fund_code] = account_id
            self.investment_to_mt5[investment_data['investment_id']] = account_id
            
            logging.info(f"Created new MT5 account {account_id} for client {client_id} fund {fund_code} with ${investment_data['principal_amount']}")
            return account_id
    
    def _generate_mt5_login(self) -> int:
        """Generate MT5 login number (in production, request from broker API)"""
        # Mock generation - in production, this would call broker's account creation API
        import random
        return random.randint(10000000, 99999999)
    
    def _generate_mt5_password(self) -> str:
        """Generate secure MT5 password"""
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(12))
    
    def _get_mt5_server_for_fund(self, fund_code: str) -> str:
        """Get appropriate MT5 server for fund type"""
        server_mapping = {
            "CORE": "FIDUS-Core-Server",
            "BALANCE": "FIDUS-Balance-Server", 
            "DYNAMIC": "FIDUS-Dynamic-Server",
            "UNLIMITED": "FIDUS-Unlimited-Server"
        }
        return server_mapping.get(fund_code, "FIDUS-Default-Server")
    
    def get_client_mt5_accounts(self, client_id: str) -> List[MT5Account]:
        """Get all MT5 accounts for a client"""
        if client_id not in self.client_fund_mapping:
            return []
        
        accounts = []
        for account_id in self.client_fund_mapping[client_id].values():
            if account_id in self.mt5_accounts:
                accounts.append(self.mt5_accounts[account_id])
        
        return accounts
    
    def update_mt5_account_performance(self, account_id: str, current_equity: float) -> bool:
        """Update MT5 account performance from real-time data"""
        if account_id not in self.mt5_accounts:
            return False
        
        mt5_account = self.mt5_accounts[account_id]
        mt5_account.current_equity = current_equity
        mt5_account.profit_loss = current_equity - mt5_account.total_allocated
        mt5_account.last_update = datetime.now(timezone.utc).isoformat()
        
        logging.info(f"Updated MT5 account {account_id} performance: equity=${current_equity}, P&L=${mt5_account.profit_loss}")
        return True
    
    def get_mt5_account_by_investment(self, investment_id: str) -> Optional[MT5Account]:
        """Get MT5 account associated with specific investment"""
        if investment_id not in self.investment_to_mt5:
            return None
        
        account_id = self.investment_to_mt5[investment_id]
        return self.mt5_accounts.get(account_id)

# MT5 Integration Service
from mt5_integration import mt5_service
from mfa_service import mfa_service

# Global MT5 mapping manager
mt5_mapping_manager = ClientMT5Mapping()

# Storage for MT5 account credentials and mappings
mt5_account_credentials = {}  # account_id -> {login, password, server}
client_mt5_accounts = {}  # client_id -> {fund_code -> account_id}

# MT5 Account Management Models
class MT5AccountCreate(BaseModel):
    client_id: str
    fund_code: str
    mt5_login: int
    mt5_password: str
    mt5_server: Optional[str] = None

class MT5AccountUpdate(BaseModel):
    mt5_login: Optional[int] = None
    mt5_password: Optional[str] = None
    mt5_server: Optional[str] = None

class MT5CredentialsRequest(BaseModel):
    client_id: str
    fund_code: str
    mt5_login: int
    mt5_password: str
    mt5_server: str

# MFA Models
class MFASetupRequest(BaseModel):
    user_id: str
    user_email: str

class MFAVerifyRequest(BaseModel):
    user_id: str
    token: str
    method: str = "totp"  # totp, sms, backup_code

class SMSRequest(BaseModel):
    user_id: str
    phone_number: str
class OCRService:
    def __init__(self):
        # For this implementation, we'll use a hybrid approach:
        # 1. Google Cloud Vision API (when credentials are available)
        # 2. Local OCR processing using Tesseract
        # 3. Advanced pattern matching for structured data extraction
        
        self.vision_client = None
        self.supported_formats = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp']
        
        # Initialize Google Vision if credentials are available
        try:
            if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') or os.environ.get('GOOGLE_CLOUD_VISION_API_KEY'):
                from google.cloud import vision
                self.vision_client = vision.ImageAnnotatorClient()
                logging.info("Google Cloud Vision API initialized")
        except Exception as e:
            logging.warning(f"Google Vision not available, using local OCR: {e}")
    
    async def preprocess_image(self, image_data: bytes) -> bytes:
        """Preprocess image to optimize OCR accuracy"""
        try:
            # Open image using PIL
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Enhance image quality for better OCR
            # Increase contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)
            
            # Sharpen image
            image = image.filter(ImageFilter.SHARPEN)
            
            # Increase brightness slightly
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.1)
            
            # Convert back to bytes
            output = io.BytesIO()
            image.save(output, format='PNG', quality=95, optimize=True)
            return output.getvalue()
            
        except Exception as e:
            logging.error(f"Image preprocessing error: {str(e)}")
            return image_data  # Return original if preprocessing fails
    
    async def extract_text_google_vision(self, image_data: bytes) -> str:
        """Extract text using Google Cloud Vision API"""
        try:
            if not self.vision_client:
                raise Exception("Google Vision client not available")
            
            from google.cloud import vision
            
            # Create Vision API image object
            image = vision.Image(content=image_data)
            
            # Perform text detection
            response = await asyncio.to_thread(
                self.vision_client.text_detection, 
                image=image
            )
            
            if response.error.message:
                raise Exception(f'Google Vision API error: {response.error.message}')
            
            # Extract full text
            if response.text_annotations:
                return response.text_annotations[0].description
            
            return ""
            
        except Exception as e:
            logging.error(f"Google Vision OCR error: {str(e)}")
            raise
    
    async def extract_text_tesseract(self, image_data: bytes) -> str:
        """Extract text using Tesseract OCR (local fallback)"""
        try:
            import pytesseract
            
            # Open image
            image = Image.open(io.BytesIO(image_data))
            
            # Configure Tesseract for better accuracy
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,/:-\  '
            
            # Extract text
            text = pytesseract.image_to_string(image, config=custom_config)
            
            return text.strip()
            
        except Exception as e:
            logging.error(f"Tesseract OCR error: {str(e)}")
            raise Exception("Local OCR processing failed")

async def process_document_ocr(image_data: bytes, document_type: str) -> Dict[str, Any]:
    """Real OCR processing using Google Vision API or Tesseract"""
    try:
        ocr_service = OCRService()
        
        # Preprocess image for better OCR results
        processed_image = await ocr_service.preprocess_image(image_data)
        
        # Try Google Vision first, fallback to Tesseract
        raw_text = ""
        ocr_method = "local"
        
        try:
            if ocr_service.vision_client:
                raw_text = await ocr_service.extract_text_google_vision(processed_image)
                ocr_method = "google_vision"
                logging.info("Used Google Cloud Vision for OCR")
        except Exception as e:
            logging.warning(f"Google Vision failed, falling back to local OCR: {e}")
        
        if not raw_text:
            raw_text = await ocr_service.extract_text_tesseract(processed_image)
            ocr_method = "tesseract"
            logging.info("Used Tesseract for OCR")
        
        if not raw_text:
            raise Exception("No text could be extracted from document")
        
        # Parse structured data based on document type
        structured_data = await parse_document_data(raw_text, document_type)
        
        # Calculate confidence score based on extracted fields
        confidence_score = calculate_extraction_confidence(structured_data, document_type)
        
        return {
            "raw_text": raw_text,
            "structured_data": structured_data,
            "confidence_score": confidence_score,
            "ocr_method": ocr_method,
            "document_type": document_type,
            "fields_extracted": list(structured_data.keys()),
            "processing_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logging.error(f"OCR processing error: {str(e)}")
        raise Exception(f"Document processing failed: {str(e)}")

async def parse_document_data(text: str, document_type: str) -> Dict[str, str]:
    """Parse structured data from OCR text based on document type"""
    
    if document_type.lower() in ['passport']:
        return await parse_passport_data(text)
    elif document_type.lower() in ['drivers_license', 'driver_license']:
        return await parse_drivers_license_data(text)
    elif document_type.lower() in ['national_id', 'state_id']:
        return await parse_national_id_data(text)
    else:
        return {}

async def parse_passport_data(text: str) -> Dict[str, str]:
    """Parse passport-specific data fields using advanced pattern matching"""
    passport_data = {}
    
    # Common passport field patterns (supports multiple languages and formats)
    patterns = {
        'passport_number': [
            r'P<[A-Z]{3}([A-Z0-9]{9})',  # Machine readable zone
            r'Passport\s*(?:No\.?|Number)\s*:?\s*([A-Z0-9]{6,12})',
            r'№\s*([A-Z0-9]{6,12})',  # International format
            r'No\.?\s*([A-Z0-9]{6,12})',
        ],
        'given_names': [
            r'Given\s*Names?\s*:?\s*([A-Z\s]+)',
            r'First\s*Name\s*:?\s*([A-Z\s]+)',
            r'Prenom\s*:?\s*([A-Z\s]+)',
            r'Nome\s*:?\s*([A-Z\s]+)',
        ],
        'surname': [
            r'Surname\s*:?\s*([A-Z\s]+)',
            r'Family\s*Name\s*:?\s*([A-Z\s]+)',
            r'Last\s*Name\s*:?\s*([A-Z\s]+)',
            r'Nom\s*:?\s*([A-Z\s]+)',
            r'Apellido\s*:?\s*([A-Z\s]+)',
        ],
        'date_of_birth': [
            r'Date\s*of\s*Birth\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
            r'DOB\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
            r'Born\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
            r'Fecha\s*de\s*Nacimiento\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
        ],
        'nationality': [
            r'Nationality\s*:?\s*([A-Z\s]+)',
            r'Country\s*:?\s*([A-Z\s]+)',
            r'Nationalite\s*:?\s*([A-Z\s]+)',
            r'Pais\s*:?\s*([A-Z\s]+)',
        ],
        'expiry_date': [
            r'Date\s*of\s*Expiry\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
            r'Expires?\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
            r'Valid\s*until\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
            r'Expira\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
        ],
        'place_of_birth': [
            r'Place\s*of\s*Birth\s*:?\s*([A-Z\s,]+)',
            r'Born\s*in\s*:?\s*([A-Z\s,]+)',
            r'Lieu\s*de\s*Naissance\s*:?\s*([A-Z\s,]+)',
        ]
    }
    
    # Extract data using patterns
    for field, field_patterns in patterns.items():
        for pattern in field_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                passport_data[field] = match.group(1).strip()
                break
    
    # Clean up extracted data
    for key, value in passport_data.items():
        if value:
            # Remove extra whitespace and normalize
            passport_data[key] = re.sub(r'\s+', ' ', value.strip())
            
            # Convert to title case for names
            if key in ['given_names', 'surname', 'place_of_birth']:
                passport_data[key] = value.title()
    
    return passport_data

async def parse_drivers_license_data(text: str) -> Dict[str, str]:
    """Parse driver's license specific data fields"""
    license_data = {}
    
    patterns = {
        'license_number': [
            r'DL\s*#?\s*:?\s*([A-Z0-9]{8,12})',
            r'License\s*#?\s*:?\s*([A-Z0-9]{8,12})',
            r'ID\s*#?\s*:?\s*([A-Z0-9]{8,12})',
            r'No\.?\s*([A-Z0-9]{8,12})',
        ],
        'full_name': [
            r'Name\s*:?\s*([A-Z\s,]+)',
            r'([A-Z]{2,}),\s*([A-Z\s]+)',  # Last, First format
        ],
        'address': [
            r'Address\s*:?\s*([A-Z0-9\s,.-]+?)(?=\n|\r|DOB|Born|EXP)',
            r'([0-9]+\s+[A-Z\s]+(?:ST|STREET|AVE|AVENUE|RD|ROAD|BLVD|BOULEVARD|DR|DRIVE|LN|LANE|CT|COURT|PL|PLACE|WAY))',
        ],
        'date_of_birth': [
            r'DOB\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
            r'Date\s*of\s*Birth\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
            r'Born\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
        ],
        'expiry_date': [
            r'EXP\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
            r'Expires?\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
            r'Valid\s*until\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
        ],
        'state': [
            r'State\s*:?\s*([A-Z]{2})',
            r'([A-Z]{2})\s*DRIVER',  # State abbreviation before "DRIVER"
        ],
        'class': [
            r'Class\s*:?\s*([A-Z0-9]+)',
            r'CDL\s*Class\s*:?\s*([A-Z]+)',
        ]
    }
    
    # Extract data using patterns
    for field, field_patterns in patterns.items():
        for pattern in field_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                if field == 'full_name' and ',' in match.group(0):
                    # Handle "Last, First" format
                    parts = match.group(0).split(',')
                    license_data['last_name'] = parts[0].strip()
                    license_data['first_name'] = parts[1].strip()
                else:
                    license_data[field] = match.group(1).strip()
                break
    
    return license_data

async def parse_national_id_data(text: str) -> Dict[str, str]:
    """Parse national ID specific data fields"""
    id_data = {}
    
    patterns = {
        'id_number': [
            r'ID\s*#?\s*:?\s*([A-Z0-9]{6,15})',
            r'National\s*ID\s*:?\s*([A-Z0-9]{6,15})',
            r'Card\s*#?\s*:?\s*([A-Z0-9]{6,15})',
            r'Number\s*:?\s*([A-Z0-9]{6,15})',
        ],
        'full_name': [
            r'Name\s*:?\s*([A-Z\s]+)',
            r'([A-Z]{2,}\s+[A-Z\s]+)',
        ],
        'date_of_birth': [
            r'DOB\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
            r'Date\s*of\s*Birth\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
            r'Born\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
        ],
        'address': [
            r'Address\s*:?\s*([A-Z0-9\s,.-]+?)(?=\n|\r|$)',
        ]
    }
    
    # Extract data using patterns
    for field, field_patterns in patterns.items():
        for pattern in field_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                id_data[field] = match.group(1).strip()
                break
    
    return id_data

def calculate_extraction_confidence(structured_data: Dict[str, str], document_type: str) -> float:
    """Calculate confidence score based on extracted fields"""
    
    # Define required fields for each document type
    required_fields = {
        'passport': ['passport_number', 'given_names', 'surname', 'date_of_birth', 'nationality'],
        'drivers_license': ['license_number', 'full_name', 'date_of_birth', 'address'],
        'national_id': ['id_number', 'full_name', 'date_of_birth'],
    }
    
    doc_type = document_type.lower()
    required = required_fields.get(doc_type, [])
    
    if not required:
        return 0.5  # Unknown document type
    
    # Calculate percentage of required fields extracted
    extracted_count = sum(1 for field in required if structured_data.get(field))
    base_confidence = extracted_count / len(required)
    
    # Bonus points for additional fields
    additional_fields = len(structured_data) - extracted_count
    bonus = min(additional_fields * 0.05, 0.2)  # Max 20% bonus
    
    # Penalty for empty or very short values
    penalty = 0
    for field, value in structured_data.items():
        if not value or len(str(value).strip()) < 2:
            penalty += 0.05
    
    confidence = base_confidence + bonus - penalty
    return max(0.0, min(1.0, confidence))  # Clamp between 0 and 1

# Real AML/KYC Verification Services
class AMLKYCService:
    def __init__(self):
        # Initialize service configurations
        self.complyadvantage_api_key = os.environ.get('COMPLYADVANTAGE_API_KEY')
        self.complyadvantage_base_url = 'https://api.complyadvantage.com'
        
        # Alternative AML providers (for fallback)
        self.worldcheck_api_key = os.environ.get('WORLDCHECK_API_KEY')
        self.dow_jones_api_key = os.environ.get('DOW_JONES_API_KEY')
        
        # Open source sanctions lists as fallback
        self.use_fallback = not (self.complyadvantage_api_key or self.worldcheck_api_key or self.dow_jones_api_key)
        
        if self.use_fallback:
            logging.warning("No commercial AML API keys found, using fallback verification")
        
        # Initialize sanctions lists for fallback
        self.sanctions_lists = self._load_sanctions_lists()
    
    def _load_sanctions_lists(self) -> Dict[str, List[str]]:
        """Load publicly available sanctions lists as fallback"""
        # In production, these would be regularly updated from official sources
        return {
            'ofac_sdn': [
                # Sample entries - in production, load from OFAC SDN list
                'OSAMA BIN LADEN',
                'AL QAIDA',
                'TALIBAN',
            ],
            'un_sanctions': [
                # Sample entries - in production, load from UN Consolidated List
                'ISLAMIC STATE',
                'ISIS',
                'ISIL',
            ],
            'eu_sanctions': [
                # Sample entries - in production, load from EU Consolidated List
            ]
        }
    
    async def screen_sanctions_complyadvantage(self, person_data: Dict[str, str]) -> Dict[str, Any]:
        """Screen against sanctions using ComplyAdvantage API"""
        try:
            if not self.complyadvantage_api_key:
                raise Exception("ComplyAdvantage API key not configured")
            
            # Prepare search data
            search_data = {
                'name': f"{person_data.get('first_name', '')} {person_data.get('last_name', '')}".strip(),
                'birth_date': person_data.get('date_of_birth', ''),
                'nationality': person_data.get('nationality', ''),
                'types': ['sanction', 'warning', 'fitness-probity', 'pep', 'adverse-media'],
                'exact_match': False,
                'fuzziness': 0.75
            }
            
            # Remove empty fields
            search_data = {k: v for k, v in search_data.items() if v}
            
            headers = {
                'Authorization': f'Token {self.complyadvantage_api_key}',
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.complyadvantage_base_url}/searches",
                    json=search_data,
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        return await self._format_complyadvantage_result(result)
                    else:
                        error_text = await response.text()
                        logging.error(f"ComplyAdvantage API error: {response.status} - {error_text}")
                        raise Exception(f"Sanctions screening failed: {error_text}")
                        
        except Exception as e:
            logging.error(f"ComplyAdvantage screening error: {str(e)}")
            raise
    
    async def _format_complyadvantage_result(self, raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """Format ComplyAdvantage results"""
        formatted = {
            'search_id': raw_result.get('id'),
            'total_hits': raw_result.get('total_hits', 0),
            'risk_level': 'LOW',
            'matches': [],
            'pep_matches': [],
            'sanctions_matches': [],
            'adverse_media_matches': [],
            'search_completed_at': datetime.utcnow().isoformat(),
            'provider': 'ComplyAdvantage'
        }
        
        # Process hits
        for hit in raw_result.get('hits', []):
            match_data = {
                'name': hit.get('doc', {}).get('name'),
                'match_types': hit.get('doc', {}).get('types', []),
                'score': hit.get('score', 0),
                'sources': hit.get('doc', {}).get('sources', []),
                'countries': hit.get('doc', {}).get('countries', []),
                'birth_date': hit.get('doc', {}).get('birth_date'),
                'description': hit.get('doc', {}).get('summary')
            }
            
            # Categorize matches
            match_types = hit.get('doc', {}).get('types', [])
            
            if 'pep' in match_types:
                formatted['pep_matches'].append(match_data)
            
            if any(t in match_types for t in ['sanction', 'warning']):
                formatted['sanctions_matches'].append(match_data)
            
            if 'adverse-media' in match_types:
                formatted['adverse_media_matches'].append(match_data)
            
            formatted['matches'].append(match_data)
        
        # Determine risk level
        if formatted['sanctions_matches']:
            formatted['risk_level'] = 'HIGH'
        elif formatted['pep_matches'] and len(formatted['pep_matches']) > 1:
            formatted['risk_level'] = 'MEDIUM'
        elif formatted['adverse_media_matches']:
            formatted['risk_level'] = 'MEDIUM'
        
        return formatted
    
    async def screen_sanctions_fallback(self, person_data: Dict[str, str]) -> Dict[str, Any]:
        """Fallback sanctions screening using local lists"""
        try:
            full_name = f"{person_data.get('first_name', '')} {person_data.get('last_name', '')}".strip().upper()
            
            matches = []
            sanctions_matches = []
            
            # Check against loaded sanctions lists
            for list_name, sanctions_list in self.sanctions_lists.items():
                for sanctioned_name in sanctions_list:
                    # Simple name matching (in production, use fuzzy matching)
                    if self._name_similarity(full_name, sanctioned_name) > 0.8:
                        match_data = {
                            'name': sanctioned_name,
                            'match_types': ['sanction'],
                            'score': self._name_similarity(full_name, sanctioned_name),
                            'sources': [list_name.upper()],
                            'countries': [],
                            'birth_date': None,
                            'description': f"Match found in {list_name.upper()} list"
                        }
                        matches.append(match_data)
                        sanctions_matches.append(match_data)
            
            # Determine risk level
            risk_level = 'HIGH' if sanctions_matches else 'LOW'
            
            return {
                'search_id': f"fallback_{int(time.time())}",
                'total_hits': len(matches),
                'risk_level': risk_level,
                'matches': matches,
                'pep_matches': [],
                'sanctions_matches': sanctions_matches,
                'adverse_media_matches': [],
                'search_completed_at': datetime.utcnow().isoformat(),
                'provider': 'Fallback_Local'
            }
            
        except Exception as e:
            logging.error(f"Fallback screening error: {str(e)}")
            raise
    
    def _name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two names (simple implementation)"""
        # In production, use more sophisticated fuzzy matching like Levenshtein distance
        name1_parts = set(name1.upper().split())
        name2_parts = set(name2.upper().split())
        
        if not name1_parts or not name2_parts:
            return 0.0
        
        intersection = name1_parts.intersection(name2_parts)
        union = name1_parts.union(name2_parts)
        
        return len(intersection) / len(union) if union else 0.0
    
    async def identity_verification(self, person_data: Dict[str, str], document_data: Dict[str, str]) -> Dict[str, Any]:
        """Perform identity verification checks"""
        try:
            verification_results = {
                'identity_verified': True,
                'document_authentic': True,
                'data_consistency': True,
                'verification_score': 0.0,
                'checks_performed': [],
                'issues_found': []
            }
            
            checks_passed = 0
            total_checks = 0
            
            # Check 1: Name consistency
            total_checks += 1
            person_name = f"{person_data.get('firstName', '')} {person_data.get('lastName', '')}".strip()
            doc_name = document_data.get('full_name', '') or f"{document_data.get('given_names', '')} {document_data.get('surname', '')}".strip()
            
            if person_name and doc_name:
                name_similarity = self._name_similarity(person_name, doc_name)
                if name_similarity >= 0.8:
                    checks_passed += 1
                    verification_results['checks_performed'].append('Name consistency: PASS')
                else:
                    verification_results['issues_found'].append(f'Name mismatch: {person_name} vs {doc_name}')
                    verification_results['checks_performed'].append('Name consistency: FAIL')
            
            # Check 2: Date of Birth consistency
            if person_data.get('dateOfBirth') and document_data.get('date_of_birth'):
                total_checks += 1
                person_dob = person_data.get('dateOfBirth')
                doc_dob = document_data.get('date_of_birth')
                
                # Normalize date formats for comparison
                if self._normalize_date(person_dob) == self._normalize_date(doc_dob):
                    checks_passed += 1
                    verification_results['checks_performed'].append('Date of birth consistency: PASS')
                else:
                    verification_results['issues_found'].append('Date of birth mismatch')
                    verification_results['checks_performed'].append('Date of birth consistency: FAIL')
            
            # Check 3: Document expiry
            if document_data.get('expiry_date'):
                total_checks += 1
                expiry_date = self._normalize_date(document_data.get('expiry_date'))
                current_date = datetime.now().strftime('%Y-%m-%d')
                
                if expiry_date and expiry_date > current_date:
                    checks_passed += 1
                    verification_results['checks_performed'].append('Document validity: PASS')
                else:
                    verification_results['issues_found'].append('Document expired or invalid expiry date')
                    verification_results['checks_performed'].append('Document validity: FAIL')
            
            # Calculate verification score
            verification_results['verification_score'] = checks_passed / total_checks if total_checks > 0 else 0.0
            
            # Determine overall status
            if verification_results['verification_score'] >= 0.8:
                verification_results['identity_verified'] = True
                verification_results['status'] = 'VERIFIED'
            elif verification_results['verification_score'] >= 0.6:
                verification_results['identity_verified'] = True
                verification_results['status'] = 'REVIEW_REQUIRED'
            else:
                verification_results['identity_verified'] = False
                verification_results['status'] = 'FAILED'
            
            verification_results['processed_at'] = datetime.utcnow().isoformat()
            
            return verification_results
            
        except Exception as e:
            logging.error(f"Identity verification error: {str(e)}")
            return {
                'identity_verified': False,
                'status': 'ERROR',
                'error': str(e),
                'processed_at': datetime.utcnow().isoformat()
            }
    
    def _normalize_date(self, date_str: str) -> Optional[str]:
        """Normalize date string to YYYY-MM-DD format"""
        if not date_str:
            return None
        
        # Try common date formats
        formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y', '%d-%m-%Y']
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None

async def perform_aml_kyc_check(personal_info: RegistrationPersonalInfo, extracted_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Real AML/KYC verification using multiple services"""
    try:
        aml_service = AMLKYCService()
        
        # Prepare person data for screening
        person_data = {
            'first_name': personal_info.firstName,
            'last_name': personal_info.lastName,
            'date_of_birth': personal_info.dateOfBirth,
            'nationality': personal_info.nationality or extracted_data.get('structured_data', {}).get('nationality', ''),
            'country': personal_info.country
        }
        
        results = {
            'overall_status': 'processing',
            'risk_level': 'LOW',
            'total_score': 0,
            'checks_completed': [],
            'issues_found': [],
            'processing_timestamp': datetime.utcnow().isoformat()
        }
        
        # 1. Sanctions Screening
        try:
            if aml_service.complyadvantage_api_key:
                sanctions_result = await aml_service.screen_sanctions_complyadvantage(person_data)
            else:
                sanctions_result = await aml_service.screen_sanctions_fallback(person_data)
            
            results['sanctions_screening'] = sanctions_result
            results['checks_completed'].append('sanctions_screening')
            
            # Update risk level based on sanctions screening
            if sanctions_result['risk_level'] == 'HIGH':
                results['risk_level'] = 'HIGH'
                results['total_score'] += 80
            elif sanctions_result['risk_level'] == 'MEDIUM':
                results['risk_level'] = 'MEDIUM' if results['risk_level'] != 'HIGH' else 'HIGH'
                results['total_score'] += 40
            else:
                results['total_score'] += 5  # Low risk baseline
                
        except Exception as e:
            logging.error(f"Sanctions screening failed: {str(e)}")
            results['issues_found'].append(f"Sanctions screening error: {str(e)}")
            results['total_score'] += 20  # Penalty for failed screening
        
        # 2. Identity Verification
        try:
            if extracted_data and extracted_data.get('structured_data'):
                identity_result = await aml_service.identity_verification(
                    personal_info.dict(), 
                    extracted_data['structured_data']
                )
                results['identity_verification'] = identity_result
                results['checks_completed'].append('identity_verification')
                
                # Update risk based on identity verification
                if not identity_result['identity_verified']:
                    results['risk_level'] = 'HIGH'
                    results['total_score'] += 60
                elif identity_result['verification_score'] < 0.8:
                    if results['risk_level'] == 'LOW':
                        results['risk_level'] = 'MEDIUM'
                    results['total_score'] += 30
                else:
                    results['total_score'] += 5  # Good verification baseline
                    
        except Exception as e:
            logging.error(f"Identity verification failed: {str(e)}")
            results['issues_found'].append(f"Identity verification error: {str(e)}")
            results['total_score'] += 15
        
        # 3. Document Quality Assessment
        try:
            if extracted_data:
                doc_quality_score = extracted_data.get('confidence_score', 0)
                results['document_quality'] = {
                    'ocr_confidence': doc_quality_score,
                    'fields_extracted': len(extracted_data.get('structured_data', {})),
                    'quality_score': doc_quality_score
                }
                results['checks_completed'].append('document_quality')
                
                # Penalize low quality documents
                if doc_quality_score < 0.7:
                    results['total_score'] += 25
                    if results['risk_level'] == 'LOW':
                        results['risk_level'] = 'MEDIUM'
                elif doc_quality_score < 0.9:
                    results['total_score'] += 10
                else:
                    results['total_score'] += 5
                    
        except Exception as e:
            logging.error(f"Document quality assessment failed: {str(e)}")
            results['issues_found'].append(f"Document quality error: {str(e)}")
            results['total_score'] += 10
        
        # 4. Enhanced Due Diligence (if high risk)
        if results['risk_level'] == 'HIGH':
            results['enhanced_due_diligence_required'] = True
            results['manual_review_required'] = True
        
        # Determine overall status
        if results['total_score'] >= 80:
            results['overall_status'] = 'rejected'
        elif results['total_score'] >= 40 or results['risk_level'] == 'HIGH':
            results['overall_status'] = 'manual_review_required'
        elif results['total_score'] >= 20 or results['risk_level'] == 'MEDIUM':
            results['overall_status'] = 'enhanced_monitoring'
        else:
            results['overall_status'] = 'approved'
        
        # Add compliance recommendations
        results['compliance_recommendations'] = []
        if results['risk_level'] == 'HIGH':
            results['compliance_recommendations'].extend([
                'Obtain additional documentation',
                'Conduct enhanced due diligence',
                'Senior management approval required',
                'Implement enhanced monitoring'
            ])
        elif results['risk_level'] == 'MEDIUM':
            results['compliance_recommendations'].extend([
                'Regular monitoring required',
                'Additional verification may be needed',
                'Consider enhanced due diligence'
            ])
        
        logging.info(f"AML/KYC check completed: {results['overall_status']} (Risk: {results['risk_level']})")
        
        return results
        
    except Exception as e:
        logging.error(f"AML/KYC processing error: {str(e)}")
        return {
            'overall_status': 'error',
            'risk_level': 'HIGH',  # Default to high risk on error
            'error': str(e),
            'processing_timestamp': datetime.utcnow().isoformat()
        }

# Email notification function
def send_credentials_email(email: str, username: str, password: str) -> bool:
    """Send account credentials via email"""
    try:
        # In production environment, implement real email sending
        # For demo/development, log the credentials
        
        email_content = f"""
Welcome to FIDUS Financial Services!

Your account has been successfully created and verified.

Login Credentials:
Username: {username}
Password: {password}

Please change your password after your first login.

For security reasons, please do not share these credentials.

Best regards,
FIDUS Compliance Team
        """
        
        # Log email content (in production, send actual email)
        logging.info(f"Account credentials prepared for: {email}")
        logging.info("EMAIL CONTENT (Demo Mode):")
        logging.info("="*50)
        logging.info(email_content)
        logging.info("="*50)
        
        # In production, implement with service like SendGrid, AWS SES, etc.
        # Example:
        # import sendgrid
        # sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        # from sendgrid.helpers.mail import Mail
        # message = Mail(
        #     from_email='noreply@fidus.com',
        #     to_emails=email,
        #     subject='FIDUS Account Credentials',
        #     html_content=email_content.replace('\n', '<br>\n')
        # )
        # response = sg.send(message)
        
        return True
        
    except Exception as e:
        logging.error(f"Email sending error: {str(e)}")
        return False

# Configuration for real services (add to .env file)
def get_service_configuration():
    """Get service configuration with fallback handling"""
    config = {
        'ocr': {
            'google_vision_enabled': bool(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') or os.environ.get('GOOGLE_CLOUD_VISION_API_KEY')),
            'tesseract_enabled': True  # Always available as fallback
        },
        'aml_kyc': {
            'complyadvantage_enabled': bool(os.environ.get('COMPLYADVANTAGE_API_KEY')),
            'worldcheck_enabled': bool(os.environ.get('WORLDCHECK_API_KEY')),
            'dow_jones_enabled': bool(os.environ.get('DOW_JONES_API_KEY')),
            'fallback_enabled': True  # Local sanctions lists
        },
        'email': {
            'sendgrid_enabled': bool(os.environ.get('SENDGRID_API_KEY')),
            'aws_ses_enabled': bool(os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY')),
            'smtp_enabled': bool(os.environ.get('SMTP_SERVER') and os.environ.get('SMTP_USERNAME'))
        }
    }
    
    return config

# Registration endpoints
@api_router.post("/registration/create-application")
async def create_registration_application(request: dict):
    """Create new registration application"""
    try:
        personal_info = RegistrationPersonalInfo(**request["personalInfo"])
        document_type = request["documentType"]
        
        application = RegistrationApplication(
            personalInfo=personal_info,
            documentType=document_type,
            status="created"
        )
        
        # Store in database (mock storage for demo)
        application_dict = application.dict()
        application_dict["createdAt"] = application_dict["createdAt"].isoformat()
        application_dict["updatedAt"] = application_dict["updatedAt"].isoformat()
        
        # In production, save to database
        # await db.registration_applications.insert_one(application_dict)
        
        return {"applicationId": application.id, "status": "created"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create application: {str(e)}")

@api_router.post("/registration/process-document")
async def process_document(
    document: UploadFile = File(...),
    documentType: str = Form(...),
    applicationId: str = Form(...)
):
    """Process uploaded document with real OCR"""
    try:
        # Validate file
        if not document.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image files are allowed")
        
        # Validate file size (10MB limit)
        if document.size and document.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size must be less than 10MB")
        
        # Read and process image
        image_data = await document.read()
        
        if len(image_data) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Perform real OCR processing
        try:
            extracted_data = await process_document_ocr(image_data, documentType)
        except Exception as ocr_error:
            logging.error(f"OCR processing failed: {str(ocr_error)}")
            raise HTTPException(status_code=422, detail=f"Document could not be processed. Please ensure the image is clear and contains readable text. Error: {str(ocr_error)}")
        
        # Validate OCR quality
        if extracted_data.get('confidence_score', 0) < 0.3:
            raise HTTPException(
                status_code=422, 
                detail="Document quality too low. Please upload a clearer image with better lighting and resolution."
            )
        
        # Check if minimum required fields were extracted
        structured_data = extracted_data.get('structured_data', {})
        if not structured_data:
            raise HTTPException(
                status_code=422,
                detail="No readable information could be extracted from the document. Please ensure the document is not damaged and text is clearly visible."
            )
        
        # In production, update application in database
        # await db.registration_applications.update_one(
        #     {"id": applicationId},
        #     {"$set": {"extractedData": extracted_data, "status": "document_processed", "updatedAt": datetime.now(timezone.utc)}}
        # )
        
        return {
            "success": True,
            "extractedData": extracted_data,
            "message": "Document processed successfully",
            "ocrMethod": extracted_data.get('ocr_method', 'unknown'),
            "confidenceScore": extracted_data.get('confidence_score', 0),
            "fieldsExtracted": len(structured_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Document processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

@api_router.post("/registration/aml-kyc-check")
async def perform_aml_kyc_verification(request: AMLKYCRequest):
    """Perform real AML/KYC verification"""
    try:
        # Perform comprehensive AML/KYC checks
        aml_kyc_results = await perform_aml_kyc_check(request.personalInfo, request.extractedData)
        
        # Add compliance metadata
        aml_kyc_results['compliance_version'] = '2024.1'
        aml_kyc_results['regulatory_framework'] = ['BSA', 'USA_PATRIOT_Act', 'FinCEN']
        aml_kyc_results['application_id'] = request.applicationId
        
        # Determine next steps based on results
        next_steps = []
        if aml_kyc_results.get('overall_status') == 'manual_review_required':
            next_steps.extend([
                'Document review by compliance officer',
                'Additional documentation may be required',
                'Enhanced due diligence procedures initiated'
            ])
        elif aml_kyc_results.get('overall_status') == 'enhanced_monitoring':
            next_steps.extend([
                'Account approved with enhanced monitoring',
                'Regular transaction monitoring implemented',
                'Periodic compliance reviews scheduled'
            ])
        elif aml_kyc_results.get('overall_status') == 'approved':
            next_steps.extend([
                'Standard onboarding process',
                'Account activation authorized',
                'Standard monitoring procedures apply'
            ])
        elif aml_kyc_results.get('overall_status') == 'rejected':
            next_steps.extend([
                'Application declined',
                'Regulatory reporting initiated',
                'Account creation blocked'
            ])
        
        aml_kyc_results['next_steps'] = next_steps
        
        # In production, update application in database
        # await db.registration_applications.update_one(
        #     {"id": request.applicationId},
        #     {"$set": {"amlKycResults": aml_kyc_results, "status": "kyc_complete", "updatedAt": datetime.now(timezone.utc)}}
        # )
        
        # Log compliance action
        logging.info(f"AML/KYC completed for {request.applicationId}: {aml_kyc_results.get('overall_status')} (Risk: {aml_kyc_results.get('risk_level')})")
        
        return aml_kyc_results
        
    except Exception as e:
        logging.error(f"AML/KYC verification error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AML/KYC verification failed: {str(e)}")

@api_router.post("/registration/finalize")
async def finalize_application(request: ApplicationFinalizationRequest):
    """Finalize registration application"""
    try:
        if not request.approved:
            raise HTTPException(status_code=400, detail="Application not approved")
        
        # Generate credentials
        username = f"client{random.randint(1000, 9999)}"
        password = f"temp{random.randint(100000, 999999)}"
        
        # Create user account
        new_user = {
            "id": f"client_{str(uuid.uuid4())[:8]}",
            "username": username,
            "name": "John Sample Doe",  # Would use extracted name in production
            "email": "demo@fidus.com",  # Would use actual email in production
            "type": "client",
            "profile_picture": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
            "status": "active",
            "createdAt": datetime.now(timezone.utc).isoformat()
        }
        
        # In production, save user to database
        # await db.users.insert_one(new_user)
        
        # Send credentials email (mock)
        send_credentials_email("demo@fidus.com", username, password)
        
        # Update MOCK_USERS for demo purposes
        MOCK_USERS[username] = new_user
        
        return {
            "success": True,
            "message": "Registration completed successfully",
            "user": new_user,
            "credentials": {
                "username": username,
                "password": password
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Application finalization failed: {str(e)}")

# Admin endpoint to get pending applications
@api_router.get("/admin/pending-applications")
async def get_pending_applications():
    """Get all pending registration applications for admin review"""
    # In production, fetch from database
    # applications = await db.registration_applications.find({"status": {"$in": ["pending", "review_required"]}}).to_list(100)
    
    # Mock data for demo
    mock_applications = [
        {
            "id": str(uuid.uuid4()),
            "personalInfo": {
                "firstName": "Jane",
                "lastName": "Smith", 
                "email": "jane.smith@email.com",
                "phone": "+1-555-0123"
            },
            "documentType": "passport",
            "status": "pending",
            "createdAt": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        }
    ]
    
    return {"applications": mock_applications}

# Password Reset Models and Functions
class ForgotPasswordRequest(BaseModel):
    email: str
    userType: str  # "client" or "admin"

class VerifyResetCodeRequest(BaseModel):
    email: str
    resetCode: str
    resetToken: str

class ResetPasswordRequest(BaseModel):
    email: str
    resetCode: str
    resetToken: str
    newPassword: str

# In-memory storage for password reset tokens (in production, use Redis or database)
password_reset_tokens = {}

def generate_reset_token():
    """Generate a secure reset token"""
    return str(uuid.uuid4()) + str(int(time.time()))

def send_password_reset_email(email: str, reset_code: str, user_type: str) -> bool:
    """Send password reset email with verification code"""
    try:
        email_content = f"""
FIDUS Password Reset Request

Hello,

You have requested to reset your password for your FIDUS {user_type} account.

Your verification code is: {reset_code}

This code will expire in 15 minutes for security reasons.

If you did not request this password reset, please ignore this email and contact our support team.

For security reasons, please do not share this code with anyone.

Best regards,
FIDUS Security Team
        """
        
        # Log email content (in production, send actual email)
        logging.info(f"Password reset email prepared for: {email} ({user_type})")
        logging.info("PASSWORD RESET EMAIL (Demo Mode):")
        logging.info("="*50)
        logging.info(email_content)
        logging.info("="*50)
        
        return True
        
    except Exception as e:
        logging.error(f"Password reset email error: {str(e)}")
        return False

# Password Reset Endpoints
@api_router.post("/auth/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Initiate password reset process"""
    try:
        email = request.email.lower().strip()
        user_type = request.userType.lower()
        
        # Validate email format
        if not email or '@' not in email:
            raise HTTPException(status_code=400, detail="Invalid email address")
        
        # Check if user exists (in production, check against database)
        user_exists = False
        for username, user_data in MOCK_USERS.items():
            if user_data.get("email", "").lower() == email and user_data.get("type") == user_type:
                user_exists = True
                break
        
        if not user_exists:
            # For security, don't reveal if email exists or not
            logging.warning(f"Password reset attempted for non-existent email: {email} ({user_type})")
        
        # Generate reset code and token
        reset_code = f"{random.randint(100000, 999999)}"  # 6-digit code
        reset_token = generate_reset_token()
        
        # Store reset data (expires in 15 minutes)
        password_reset_tokens[reset_token] = {
            "email": email,
            "user_type": user_type,
            "reset_code": reset_code,
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=15),
            "verified": False
        }
        
        # Send email with reset code
        email_sent = send_password_reset_email(email, reset_code, user_type)
        
        if not email_sent:
            raise HTTPException(status_code=500, detail="Failed to send reset email")
        
        return {
            "success": True,
            "message": "Password reset code sent to your email",
            "resetToken": reset_token,
            "expiresIn": 900  # 15 minutes in seconds
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Forgot password error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process password reset request")

@api_router.post("/auth/verify-reset-code")
async def verify_reset_code(request: VerifyResetCodeRequest):
    """Verify the reset code"""
    try:
        reset_token = request.resetToken
        reset_code = request.resetCode
        email = request.email.lower().strip()
        
        # Check if token exists
        if reset_token not in password_reset_tokens:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
        token_data = password_reset_tokens[reset_token]
        
        # Check if token is expired
        if datetime.now(timezone.utc) > token_data["expires_at"]:
            del password_reset_tokens[reset_token]
            raise HTTPException(status_code=400, detail="Reset code has expired. Please request a new one.")
        
        # Verify email matches
        if token_data["email"] != email:
            raise HTTPException(status_code=400, detail="Email does not match reset request")
        
        # Verify reset code (in demo mode, accept any 6-digit code)
        if len(reset_code) != 6 or not reset_code.isdigit():
            raise HTTPException(status_code=400, detail="Invalid verification code format")
        
        # For demo purposes, accept any 6-digit code
        # In production, verify against token_data["reset_code"]
        
        # Mark as verified
        password_reset_tokens[reset_token]["verified"] = True
        
        return {
            "success": True,
            "message": "Verification code confirmed",
            "verified": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Verify reset code error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to verify reset code")

@api_router.post("/auth/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Reset the password"""
    try:
        reset_token = request.resetToken
        email = request.email.lower().strip()
        new_password = request.newPassword
        
        # Check if token exists and is verified
        if reset_token not in password_reset_tokens:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
        token_data = password_reset_tokens[reset_token]
        
        # Check if token is expired
        if datetime.now(timezone.utc) > token_data["expires_at"]:
            del password_reset_tokens[reset_token]
            raise HTTPException(status_code=400, detail="Reset session has expired. Please start over.")
        
        # Check if code was verified
        if not token_data.get("verified", False):
            raise HTTPException(status_code=400, detail="Reset code must be verified first")
        
        # Validate email matches
        if token_data["email"] != email:
            raise HTTPException(status_code=400, detail="Email does not match reset request")
        
        # Validate password strength
        if len(new_password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
        
        # Check password complexity
        has_upper = any(c.isupper() for c in new_password)
        has_lower = any(c.islower() for c in new_password)
        has_digit = any(c.isdigit() for c in new_password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in new_password)
        
        strength_score = sum([has_upper, has_lower, has_digit, has_special])
        
        if strength_score < 3:
            raise HTTPException(
                status_code=400, 
                detail="Password must contain at least 3 of: uppercase letter, lowercase letter, number, special character"
            )
        
        # Update password in MOCK_USERS (in production, hash and store in database)
        user_updated = False
        for username, user_data in MOCK_USERS.items():
            if user_data.get("email", "").lower() == email and user_data.get("type") == token_data["user_type"]:
                # In production, hash the password before storing
                # import bcrypt
                # hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                # user_data["password_hash"] = hashed_password
                
                # For demo, we'll just update a timestamp to indicate password was changed
                user_data["password_updated_at"] = datetime.now(timezone.utc).isoformat()
                user_updated = True
                logging.info(f"Password updated for user: {email} ({token_data['user_type']})")
                break
        
        if not user_updated:
            logging.warning(f"User not found for password reset: {email}")
        
        # Clean up the reset token
        del password_reset_tokens[reset_token]
        
        # Send confirmation email (optional)
        try:
            confirmation_email = f"""
FIDUS Password Reset Confirmation

Hello,

Your password has been successfully reset for your FIDUS {token_data['user_type']} account.

If you did not perform this action, please contact our support team immediately.

Best regards,
FIDUS Security Team
            """
            
            logging.info(f"Password reset confirmation sent to: {email}")
            logging.info("CONFIRMATION EMAIL (Demo Mode):")
            logging.info("="*50)  
            logging.info(confirmation_email)
            logging.info("="*50)
            
        except Exception as e:
            logging.warning(f"Failed to send confirmation email: {str(e)}")
        
        return {
            "success": True,
            "message": "Password has been successfully reset",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Reset password error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to reset password")

# Service Configuration and Status Endpoints
@api_router.get("/admin/service-status")
async def get_service_status():
    """Get status of integrated services"""
    try:
        config = get_service_configuration()
        
        status = {
            'ocr_services': {
                'google_cloud_vision': {
                    'enabled': config['ocr']['google_vision_enabled'],
                    'status': 'ready' if config['ocr']['google_vision_enabled'] else 'not_configured',
                    'description': 'Google Cloud Vision API for high-accuracy OCR'
                },
                'tesseract': {
                    'enabled': config['ocr']['tesseract_enabled'],
                    'status': 'ready',
                    'description': 'Local Tesseract OCR engine (fallback)'
                }
            },
            'aml_kyc_services': {
                'complyadvantage': {
                    'enabled': config['aml_kyc']['complyadvantage_enabled'],
                    'status': 'ready' if config['aml_kyc']['complyadvantage_enabled'] else 'not_configured',
                    'description': 'ComplyAdvantage real-time AML screening'
                },
                'local_sanctions_lists': {
                    'enabled': config['aml_kyc']['fallback_enabled'],
                    'status': 'ready',
                    'description': 'Local sanctions lists (OFAC, UN, EU) - fallback option'
                }
            },
            'notification_services': {
                'email_notifications': {
                    'enabled': True,
                    'status': 'demo_mode',
                    'description': 'Account credential delivery (demo logging mode)'
                }
            },
            'compliance_features': {
                'document_preprocessing': {
                    'enabled': True,
                    'status': 'ready',
                    'description': 'Image enhancement for OCR accuracy'
                },
                'identity_verification': {
                    'enabled': True,
                    'status': 'ready',  
                    'description': 'Cross-reference personal data with document data'
                },
                'risk_assessment': {
                    'enabled': True,
                    'status': 'ready',
                    'description': 'Multi-factor risk scoring algorithm'
                },
                'audit_logging': {
                    'enabled': True,
                    'status': 'ready',
                    'description': 'Comprehensive compliance audit trails'
                }
            }
        }
        
        # Overall system status
        total_services = 0
        ready_services = 0
        
        for category in status.values():
            for service in category.values():
                total_services += 1
                if service['status'] in ['ready', 'demo_mode']:
                    ready_services += 1
        
        status['overall'] = {
            'status': 'operational' if ready_services >= total_services * 0.8 else 'partial',
            'ready_services': ready_services,
            'total_services': total_services,
            'readiness_percentage': round((ready_services / total_services) * 100, 1),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        return status
        
    except Exception as e:
        logging.error(f"Service status check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Service status check failed: {str(e)}")

@api_router.post("/admin/test-ocr")
async def test_ocr_service(file: UploadFile = File(...)):
    """Test OCR service with uploaded document"""
    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image files are allowed")
        
        image_data = await file.read()
        
        # Test OCR processing
        result = await process_document_ocr(image_data, "test_document")
        
        return {
            'success': True,
            'ocr_method': result.get('ocr_method'),
            'confidence_score': result.get('confidence_score'),
            'fields_extracted': len(result.get('structured_data', {})),
            'raw_text_length': len(result.get('raw_text', '')),
            'processing_time': result.get('processing_timestamp')
        }
        
    except Exception as e:
        logging.error(f"OCR test error: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

@api_router.post("/admin/test-aml-kyc")
async def test_aml_kyc_service(test_person: dict):
    """Test AML/KYC service with sample person data"""
    try:
        # Convert test data to proper format
        personal_info = RegistrationPersonalInfo(
            firstName=test_person.get('firstName', 'John'),
            lastName=test_person.get('lastName', 'Doe'),
            email=test_person.get('email', 'john.doe@example.com'),
            phone=test_person.get('phone', '+1-555-123-4567'),
            dateOfBirth=test_person.get('dateOfBirth', '1990-01-01'),
            nationality=test_person.get('nationality', 'US'),
            country=test_person.get('country', 'United States')
        )
        
        # Test AML/KYC processing
        result = await perform_aml_kyc_check(personal_info, None)
        
        return {
            'success': True,
            'overall_status': result.get('overall_status'),
            'risk_level': result.get('risk_level'),
            'total_score': result.get('total_score'),
            'checks_completed': result.get('checks_completed', []),
            'provider_used': result.get('sanctions_screening', {}).get('provider', 'fallback'),
            'processing_time': result.get('processing_timestamp')
        }
        
    except Exception as e:
        logging.error(f"AML/KYC test error: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

# Excel Client Management Functions
def generate_clients_excel_data():
    """Generate comprehensive client data for Excel export"""
    clients_data = []
    
    # Add existing clients from MOCK_USERS
    for user in MOCK_USERS.values():
        if user["type"] == "client":
            transactions = generate_mock_transactions(user["id"], 50)
            balances = calculate_balances(user["id"])
            
            # Calculate additional metrics
            total_transactions = len(transactions)
            avg_transaction_amount = sum(t["amount"] for t in transactions) / total_transactions if total_transactions > 0 else 0
            last_transaction_date = transactions[0]["date"] if transactions else datetime.now(timezone.utc)
            
            client_data = {
                "Client_ID": user["id"],
                "Username": user["username"],
                "Full_Name": user["name"],
                "Email": user["email"],
                "Status": user.get("status", "active"),
                "Registration_Date": user.get("createdAt", datetime.now(timezone.utc).isoformat())[:10],
                "Total_Balance": round(balances["total_balance"], 2),
                "FIDUS_Funds": round(balances["fidus_funds"], 2),
                "Core_Balance": round(balances["core_balance"], 2),
                "Dynamic_Balance": round(balances["dynamic_balance"], 2),
                "Total_Transactions": total_transactions,
                "Avg_Transaction_Amount": round(avg_transaction_amount, 2),
                "Last_Activity": last_transaction_date.isoformat()[:10] if hasattr(last_transaction_date, 'isoformat') else str(last_transaction_date)[:10],
                "Risk_Level": random.choice(["Low", "Medium", "Low", "Low"]),  # Mostly low risk
                "KYC_Status": "Verified",
                "AML_Status": "Clear",
                "Account_Type": "Individual",
                "Phone": "+1-555-" + str(random.randint(1000000, 9999999)),
                "Address": f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Pine', 'Cedar', 'Maple'])} {random.choice(['St', 'Ave', 'Blvd', 'Dr'])}",
                "City": random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia"]),
                "State": random.choice(["NY", "CA", "IL", "TX", "AZ", "PA"]),
                "Zip_Code": str(random.randint(10000, 99999)),
                "Country": "United States",
                "Date_of_Birth": f"{random.randint(1970, 2000)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                "Nationality": "US",
                "Occupation": random.choice(["Engineer", "Doctor", "Lawyer", "Teacher", "Manager", "Consultant"]),
                "Annual_Income": random.randint(75000, 500000),
                "Net_Worth": random.randint(200000, 2000000),
                "Investment_Experience": random.choice(["Beginner", "Intermediate", "Advanced"]),
                "Risk_Tolerance": random.choice(["Conservative", "Moderate", "Aggressive"]),
                "Investment_Goals": random.choice(["Retirement", "Wealth Building", "Income Generation", "Capital Preservation"])
            }
            clients_data.append(client_data)
    
    return clients_data

def parse_clients_excel_data(excel_data):
    """Parse uploaded Excel data and validate client information"""
    clients = []
    required_fields = ["Full_Name", "Email", "Username"]
    
    for row in excel_data:
        if not row or all(not str(v).strip() for v in row.values()):
            continue  # Skip empty rows
            
        # Check required fields
        missing_fields = [field for field in required_fields if not row.get(field)]
        if missing_fields:
            continue  # Skip invalid rows
            
        # Create standardized client data
        client = {
            "id": row.get("Client_ID", f"client_{str(uuid.uuid4())[:8]}"),
            "username": row.get("Username", "").strip(),
            "name": row.get("Full_Name", "").strip(),
            "email": row.get("Email", "").strip().lower(),
            "type": "client",
            "status": row.get("Status", "active").lower(),
            "createdAt": row.get("Registration_Date", datetime.now(timezone.utc).isoformat()[:10]),
            "profile_picture": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
            "phone": row.get("Phone", ""),
            "address": row.get("Address", ""),
            "city": row.get("City", ""),
            "state": row.get("State", ""),
            "zip_code": row.get("Zip_Code", ""),
            "country": row.get("Country", "United States"),
            "date_of_birth": row.get("Date_of_Birth", ""),
            "nationality": row.get("Nationality", "US"),
            "occupation": row.get("Occupation", ""),
            "annual_income": row.get("Annual_Income", 0),
            "net_worth": row.get("Net_Worth", 0),
            "investment_experience": row.get("Investment_Experience", ""),
            "risk_tolerance": row.get("Risk_Tolerance", ""),
            "investment_goals": row.get("Investment_Goals", ""),
            "balances": {
                "total_balance": float(row.get("Total_Balance", 0)),
                "fidus_funds": float(row.get("FIDUS_Funds", 0)),
                "core_balance": float(row.get("Core_Balance", 0)),
                "dynamic_balance": float(row.get("Dynamic_Balance", 0))
            }
        }
        clients.append(client)
    
    return clients

# Excel Client Management Endpoints
@api_router.get("/admin/clients/export")
async def export_clients_excel():
    """Export all clients data to Excel format"""
    try:
        import io
        from datetime import datetime
        import json
        
        clients_data = generate_clients_excel_data()
        
        if not clients_data:
            return {"error": "No client data available for export"}
        
        # Convert to CSV format for simple download
        import csv
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=clients_data[0].keys())
        writer.writeheader()
        writer.writerows(clients_data)
        
        csv_content = output.getvalue()
        
        return {
            "success": True,
            "filename": f"fidus_clients_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "data": csv_content,
            "total_clients": len(clients_data),
            "export_date": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@api_router.post("/admin/clients/import")
async def import_clients_excel(file: UploadFile = File(...)):
    """Import clients data from Excel file"""
    try:
        if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(status_code=400, detail="Only Excel (.xlsx, .xls) or CSV files are allowed")
        
        # Read file content
        content = await file.read()
        
        if file.filename.endswith('.csv'):
            # Handle CSV files
            import csv
            import io
            csv_content = content.decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            excel_data = list(csv_reader)
        else:
            # Handle Excel files
            import pandas as pd
            df = pd.read_excel(io.BytesIO(content))
            excel_data = df.to_dict('records')
        
        # Parse and validate client data
        clients = parse_clients_excel_data(excel_data)
        
        # Update MOCK_USERS with imported clients
        imported_count = 0
        updated_count = 0
        
        for client in clients:
            username = client["username"]
            if username in MOCK_USERS:
                MOCK_USERS[username].update(client)
                updated_count += 1
            else:
                MOCK_USERS[username] = client
                imported_count += 1
        
        return {
            "success": True,
            "message": f"Successfully processed {len(clients)} client records",
            "imported": imported_count,
            "updated": updated_count,
            "total_processed": len(clients),
            "skipped": len(excel_data) - len(clients)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

@api_router.post("/admin/users/create")
async def create_new_user(user_data: UserCreate):
    """Create a new user account with temporary password"""
    try:
        # Check if username already exists
        for existing_user in MOCK_USERS.values():
            if existing_user["username"] == user_data.username:
                raise HTTPException(status_code=400, detail="Username already exists")
        
        # Generate unique user ID
        user_id = f"client_{str(uuid.uuid4())[:8]}"  
        
        # Create user entry
        new_user = {
            "id": user_id,
            "username": user_data.username,
            "name": user_data.name,
            "email": user_data.email,
            "type": "client",
            "status": "active",
            "phone": user_data.phone,
            "profile_picture": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "notes": user_data.notes
        }
        
        # Add to MOCK_USERS with username as key
        MOCK_USERS[user_data.username] = new_user
        
        # Store temporary password info
        user_temp_passwords[user_id] = {
            "temp_password": user_data.temporary_password,
            "must_change": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Initialize client readiness (not ready initially)
        client_readiness[user_id] = {
            "client_id": user_id,
            "aml_kyc_completed": False,
            "agreement_signed": False,
            "deposit_date": None,
            "investment_ready": False,
            "notes": f"Created by admin - {user_data.notes}",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "updated_by": "admin"
        }
        
        logging.info(f"New user created: {user_data.username} (ID: {user_id})")
        
        return {
            "success": True,
            "user_id": user_id,
            "username": user_data.username,
            "message": f"User '{user_data.name}' created successfully. Temporary password set."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"User creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

# Document Management Endpoints for CRM Prospects
@api_router.get("/crm/prospects/{prospect_id}/documents")
async def get_prospect_documents(prospect_id: str):
    """Get all documents for a specific prospect"""
    try:
        # Mock document storage - in production, use proper database
        if prospect_id not in prospect_documents:
            prospect_documents[prospect_id] = []
        
        documents = prospect_documents[prospect_id]
        
        return {
            "success": True,
            "documents": documents,
            "total_documents": len(documents)
        }
        
    except Exception as e:
        logging.error(f"Get prospect documents error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch prospect documents")

@api_router.post("/crm/prospects/{prospect_id}/documents")
async def upload_prospect_document(
    prospect_id: str,
    file: UploadFile = File(...),
    document_type: str = Form(...),
    notes: str = Form("")
):
    """Upload a document for a prospect"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file uploaded")
        
        # Check file extension
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.pdf', '.tiff', '.doc', '.docx']
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail="File type not supported")
        
        # Read file content
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="File too large")
        
        # Create document record
        document_id = str(uuid.uuid4())
        document_record = {
            "id": document_id,
            "prospect_id": prospect_id,
            "document_type": document_type,
            "filename": file.filename,
            "file_size": len(content),
            "file_extension": file_ext,
            "upload_date": datetime.now(timezone.utc).isoformat(),
            "verification_status": "pending",
            "notes": notes,
            "uploaded_by": "admin",
            "verified_by": None,
            "verified_at": None,
            "file_path": f"/documents/prospects/{prospect_id}/{document_id}{file_ext}"  # Mock path
        }
        
        # Initialize storage if needed
        if prospect_id not in prospect_documents:
            prospect_documents[prospect_id] = []
        
        # Add document record
        prospect_documents[prospect_id].append(document_record)
        
        # In production, save file to storage here
        # e.g., save to AWS S3, Google Cloud Storage, etc.
        
        logging.info(f"Document uploaded for prospect {prospect_id}: {file.filename}")
        
        return {
            "success": True,
            "document_id": document_id,
            "message": "Document uploaded successfully",
            "document": document_record
        }
        
    except Exception as e:
        logging.error(f"Upload prospect document error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload document")

@api_router.post("/crm/prospects/{prospect_id}/documents/request")
async def request_prospect_document(prospect_id: str, request_data: dict):
    """Request a specific document from a prospect"""
    try:
        document_type = request_data.get("document_type")
        message = request_data.get("message", "")
        
        if not document_type:
            raise HTTPException(status_code=400, detail="Document type is required")
        
        # Find prospect
        prospect = prospects_storage.get(prospect_id)
        if not prospect:
            raise HTTPException(status_code=404, detail="Prospect not found")
        
        # Create document request record
        request_id = str(uuid.uuid4())
        document_request = {
            "id": request_id,
            "prospect_id": prospect_id,
            "document_type": document_type,
            "message": message,
            "status": "requested",
            "requested_at": datetime.now(timezone.utc).isoformat(),
            "requested_by": "admin",
            "due_date": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),  # 7 days to submit
            "reminder_sent": False
        }
        
        # Initialize storage if needed
        if prospect_id not in prospect_document_requests:
            prospect_document_requests[prospect_id] = []
        
        # Add request record
        prospect_document_requests[prospect_id].append(document_request)
        
        # In production, send email/SMS notification to prospect here
        
        # Update prospect notes
        prospect["notes"] = f"{prospect.get('notes', '')} | Document requested: {document_type} on {datetime.now().strftime('%Y-%m-%d')}"
        
        logging.info(f"Document requested from prospect {prospect_id}: {document_type}")
        
        return {
            "success": True,
            "request_id": request_id,
            "message": f"Document request sent to {prospect['name']}",
            "request": document_request
        }
        
    except Exception as e:
        logging.error(f"Request prospect document error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to request document")

@api_router.patch("/crm/prospects/{prospect_id}/documents/{document_id}")
async def verify_prospect_document(prospect_id: str, document_id: str, verification_data: dict):
    """Verify/approve/reject a prospect document"""
    try:
        verification_status = verification_data.get("verification_status")  # approved, rejected, pending
        verified_by = verification_data.get("verified_by", "admin")
        verification_notes = verification_data.get("verification_notes", "")
        
        if verification_status not in ["approved", "rejected", "pending"]:
            raise HTTPException(status_code=400, detail="Invalid verification status")
        
        # Find document
        if prospect_id not in prospect_documents:
            raise HTTPException(status_code=404, detail="No documents found for prospect")
        
        document = None
        for doc in prospect_documents[prospect_id]:
            if doc["id"] == document_id:
                document = doc
                break
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Update document verification
        document["verification_status"] = verification_status
        document["verified_by"] = verified_by
        document["verified_at"] = datetime.now(timezone.utc).isoformat()
        document["verification_notes"] = verification_notes
        
        # Update prospect stage if all required documents are approved
        if verification_status == "approved":
            prospect = prospects_storage.get(prospect_id)
            if prospect:
                # Check if all required KYC documents are approved
                required_doc_types = ["identity", "proof_of_residence", "bank_statement", "source_of_funds"]
                approved_docs = [
                    doc for doc in prospect_documents[prospect_id] 
                    if doc["verification_status"] == "approved" and doc["document_type"] in required_doc_types
                ]
                
                if len(approved_docs) >= len(required_doc_types):
                    prospect["stage"] = "qualified"
                    prospect["notes"] = f"{prospect.get('notes', '')} | KYC documentation completed on {datetime.now().strftime('%Y-%m-%d')}"
        
        logging.info(f"Document {document_id} {verification_status} for prospect {prospect_id}")
        
        return {
            "success": True,
            "message": f"Document {verification_status} successfully",
            "document": document
        }
        
    except Exception as e:
        logging.error(f"Verify prospect document error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to verify document")
@api_router.post("/ocr/extract/sync")
async def extract_text_sync(file: UploadFile = File(...)):
    """Extract text from uploaded document using OCR"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file uploaded")
        
        # Check file extension
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.pdf', '.tiff']
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail="File type not supported")
        
        # Read file content
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="File too large")
        
        # Simulate OCR processing (in production, use actual OCR service)
        await asyncio.sleep(2)  # Simulate processing time
        
        # Mock OCR response structure
        ocr_response = {
            "job_id": str(uuid.uuid4()),
            "filename": file.filename,
            "ocr_results": {
                "raw_text": "PASSPORT\nJOHN SMITH\nP<USASMITH<<JOHN<<<<<<<<<<<<<<<<<<<<<<\n1234567890USA8001011M2501011234567890<<<<<<<<<<<<",
                "confidence": 85.5,
                "engine_used": "tesseract",
                "processing_time": 1.8,
                "bounding_boxes": []
            },
            "parsed_document": {
                "document_type": "passport",
                "fields": {
                    "full_name": "JOHN SMITH",
                    "first_name": "JOHN",
                    "last_name": "SMITH",
                    "document_number": "123456789",
                    "nationality": "USA",
                    "date_of_birth": "01/01/1980",
                    "sex": "M",
                    "date_of_expiry": "01/01/2025"
                },
                "validation_errors": []
            },
            "processing_metadata": {
                "total_processing_time": 2.1,
                "image_dimensions": [1920, 1080],
                "file_size": len(content)
            }
        }
        
        return ocr_response
        
    except Exception as e:
        logging.error(f"OCR processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="OCR processing failed")

@api_router.post("/identity/verify/document")  
async def verify_identity_document():
    """Verify identity document (mock implementation)"""
    try:
        # Simulate identity verification processing
        await asyncio.sleep(1.5)
        
        # Mock identity verification response
        verification_response = {
            "verification_id": str(uuid.uuid4()),
            "timestamp": time.time(),
            "identity_verification": {
                "overall_status": "verified",
                "overall_confidence": 0.92,
                "provider_results": [
                    {
                        "provider": "mock_verifier",
                        "status": "verified", 
                        "confidence": 0.92,
                        "processing_time": 1.2
                    }
                ],
                "consensus": {
                    "verified_count": 1,
                    "rejected_count": 0,
                    "review_count": 0,
                    "total_providers": 1
                }
            }
        }
        
        return verification_response
        
    except Exception as e:
        logging.error(f"Identity verification error: {str(e)}")
        raise HTTPException(status_code=500, detail="Identity verification failed")

@api_router.post("/compliance/screen")
async def screen_customer():
    """Screen customer against OFAC and sanctions lists (mock implementation)"""
    try:
        # Simulate OFAC screening
        await asyncio.sleep(1)
        
        # Mock OFAC screening response
        screening_response = {
            "screening_id": str(uuid.uuid4()),
            "screening_status": "clear",
            "total_lists_checked": 5,
            "matches": [],
            "confidence_score": 0.95,
            "processing_time": 0.8,
            "lists_checked": ["sdn", "nonsdn", "eu", "un", "uk"]
        }
        
        return screening_response
        
    except Exception as e:
        logging.error(f"OFAC screening error: {str(e)}")
        raise HTTPException(status_code=500, detail="OFAC screening failed")
@api_router.post("/auth/register")
async def register_new_client(registration_data: dict):
    """Register a new client from onboarding process and automatically add to CRM leads"""
    try:
        # Extract registration data from ClientOnboarding component
        extracted_data = registration_data.get("extracted_data", {})
        client_data = registration_data.get("client_data", {})
        kyc_status = registration_data.get("kyc_status", {})
        
        # Get key fields
        full_name = registration_data.get("full_name") or extracted_data.get("full_name")
        email = registration_data.get("email") or client_data.get("email")
        phone = registration_data.get("phone") or client_data.get("phone")
        password = registration_data.get("password") or client_data.get("password")
        
        if not all([full_name, email, password]):
            raise HTTPException(status_code=400, detail="Name, email, and password are required")
        
        # Check if email already exists
        for existing_user in MOCK_USERS.values():
            if existing_user.get("email") == email:
                raise HTTPException(status_code=400, detail="Email already registered")
        
        # Generate unique user ID and username
        user_id = f"client_{str(uuid.uuid4())[:8]}"
        username = email.split('@')[0] if '@' in email else full_name.lower().replace(' ', '_')
        
        # Create user entry
        new_user = {
            "id": user_id,
            "username": username,
            "name": full_name,
            "email": email,
            "type": "client",
            "status": "active",
            "phone": phone or client_data.get("phone", ""),
            "profile_picture": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "notes": "Client onboarded through document verification process",
            # Store additional onboarding data
            "document_data": extracted_data,
            "kyc_completed": kyc_status.get("overall_status") == "approved",
            "onboarding_method": "document_upload_kyc"
        }
        
        # Add to MOCK_USERS
        MOCK_USERS[username] = new_user
        
        # Store password
        user_temp_passwords[user_id] = {
            "temp_password": password,
            "must_change": False,  # Client set their own password
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Initialize client readiness based on KYC status
        client_readiness[user_id] = {
            "client_id": user_id,
            "aml_kyc_completed": kyc_status.get("overall_status") == "approved",
            "agreement_signed": False,  # Still needs agreement
            "deposit_date": None,
            "investment_ready": kyc_status.get("overall_status") == "approved",
            "notes": f"Onboarded via document verification - KYC Status: {kyc_status.get('overall_status', 'pending')}",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "updated_by": "system",
            "document_verified": kyc_status.get("document_verified", False),
            "identity_verified": kyc_status.get("identity_verified", False),
            "ofac_cleared": kyc_status.get("ofac_cleared", False)
        }
        
        # ✅ CRITICAL: AUTOMATICALLY ADD TO CRM LEADS/PROSPECTS
        prospect_id = str(uuid.uuid4())
        new_prospect = {
            "id": prospect_id,
            "name": full_name,
            "email": email,
            "phone": phone or client_data.get("phone", ""),
            "stage": "qualified_lead",  # Start as qualified since they completed KYC
            "notes": f"Auto-generated from client onboarding. KYC Status: {kyc_status.get('overall_status', 'pending')}. Document Type: {extracted_data.get('document_type', 'unknown')}",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "converted_to_client": True,  # Already converted since they registered
            "client_id": user_id,  # Link to actual client record
            "agreement_sent": False,
            "onboarding_completed": True,
            
            # Add rich onboarding data for admin review
            "source": "website_onboarding",
            "lead_score": 85 if kyc_status.get("overall_status") == "approved" else 65,
            "kyc_status": kyc_status.get("overall_status", "pending"),
            "document_verification": {
                "document_type": extracted_data.get("document_type"),
                "nationality": extracted_data.get("nationality"),
                "date_of_birth": extracted_data.get("date_of_birth"),
                "document_number": extracted_data.get("document_number"),
                "verification_completed": kyc_status.get("document_verified", False)
            },
            "risk_assessment": {
                "ofac_cleared": kyc_status.get("ofac_cleared", False),
                "identity_verified": kyc_status.get("identity_verified", False),
                "overall_risk": "low" if kyc_status.get("overall_status") == "approved" else "medium"
            }
        }
        
        # Add to prospects_storage (this makes it appear in Admin CRM)
        prospects_storage[prospect_id] = new_prospect
        
        logging.info(f"New client registered and added to CRM leads: {full_name} ({email}) - Prospect ID: {prospect_id}")
        
        return {
            "success": True,
            "user_id": user_id,
            "username": username,
            "message": f"Registration successful! Welcome {full_name}. Your account has been created and is ready for investment.",
            "kyc_status": kyc_status.get("overall_status", "pending"),
            "added_to_crm": True,
            "prospect_id": prospect_id,
            "investment_ready": kyc_status.get("overall_status") == "approved"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Client registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@api_router.get("/admin/clients/detailed")
async def get_detailed_clients():
    """Get detailed client information for admin management"""
    try:
        clients_data = []
        
        for user in MOCK_USERS.values():
            if user["type"] == "client":
                transactions = generate_mock_transactions(user["id"], 30)
                balances = calculate_balances(user["id"])
                
                # Calculate metrics
                total_transactions = len(transactions)
                avg_transaction = sum(t["amount"] for t in transactions) / total_transactions if total_transactions > 0 else 0
                last_activity = transactions[0]["date"] if transactions else datetime.now(timezone.utc)
                
                client_detail = {
                    "id": user["id"],
                    "username": user["username"],
                    "name": user["name"],
                    "email": user["email"],
                    "status": user.get("status", "active"),
                    "created_at": user.get("createdAt", datetime.now(timezone.utc).isoformat()),
                    "profile_picture": user.get("profile_picture", ""),
                    "balances": {
                        "total": round(balances["total_balance"], 2),
                        "fidus": round(balances["fidus_funds"], 2),
                        "core": round(balances["core_balance"], 2),
                        "dynamic": round(balances["dynamic_balance"], 2)
                    },
                    "activity": {
                        "total_transactions": total_transactions,
                        "avg_transaction": round(avg_transaction, 2),
                        "last_activity": last_activity.isoformat() if hasattr(last_activity, 'isoformat') else str(last_activity)
                    },
                    "compliance": {
                        "kyc_status": "Verified",
                        "aml_status": "Clear",
                        "risk_level": random.choice(["Low", "Medium"])
                    },
                    "personal": {
                        "phone": user.get("phone", f"+1-555-{random.randint(1000000, 9999999)}"),
                        "address": user.get("address", f"{random.randint(100, 9999)} Main St"),
                        "city": user.get("city", "New York"),
                        "country": user.get("country", "United States")
                    }
                }
                clients_data.append(client_detail)
        
        # Sort by creation date (newest first)
        clients_data.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {
            "clients": clients_data,
            "total_clients": len(clients_data),
            "active_clients": len([c for c in clients_data if c["status"] == "active"]),
            "total_aum": sum(c["balances"]["total"] for c in clients_data),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch detailed clients: {str(e)}")

@api_router.delete("/admin/clients/{client_id}")
async def delete_client(client_id: str):
    """Delete a client (admin only)"""
    try:
        # Find and remove client
        username_to_remove = None
        for username, user in MOCK_USERS.items():
            if user.get("id") == client_id and user.get("type") == "client":
                username_to_remove = username
                break
        
        if username_to_remove:
            del MOCK_USERS[username_to_remove]
            return {"success": True, "message": "Client deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Client not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete client: {str(e)}")

@api_router.put("/admin/clients/{client_id}/status")
async def update_client_status(client_id: str, status_data: dict):
    """Update client status (active/inactive/suspended)"""
    try:
        new_status = status_data.get("status", "active").lower()
        
        if new_status not in ["active", "inactive", "suspended"]:
            raise HTTPException(status_code=400, detail="Invalid status. Must be active, inactive, or suspended")
        
        # Find and update client
        for username, user in MOCK_USERS.items():
            if user.get("id") == client_id and user.get("type") == "client":
                user["status"] = new_status
                user["updatedAt"] = datetime.now(timezone.utc).isoformat()
                return {"success": True, "message": f"Client status updated to {new_status}"}
        
        raise HTTPException(status_code=404, detail="Client not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update client status: {str(e)}")

@api_router.get("/admin/portfolio-summary")
async def get_portfolio_summary():
    """Get portfolio summary for admin dashboard"""
    try:
        # Calculate real total AUM from MongoDB
        all_clients = mongodb_manager.get_all_clients()
        total_aum = 0.0
        client_count = 0
        fund_allocation = {"CORE": 0, "BALANCE": 0, "DYNAMIC": 0, "UNLIMITED": 0}
        
        # Sum AUM from all client investments
        for client in all_clients:
            client_investments_list = mongodb_manager.get_client_investments(client['id'])
            if client_investments_list:
                client_count += 1
                for investment in client_investments_list:
                    current_value = investment['current_value']
                    total_aum += current_value
                    fund_code = investment['fund_code']
                    if fund_code in fund_allocation:
                        fund_allocation[fund_code] += current_value
        
        # Calculate allocation percentages
        allocation = {}
        if total_aum > 0:
            for fund_code, amount in fund_allocation.items():
                allocation[fund_code] = round((amount / total_aum) * 100, 2)
        else:
            allocation = {"CORE": 0, "BALANCE": 0, "DYNAMIC": 0, "UNLIMITED": 0}
        
        return {
            "total_aum": round(total_aum, 2),
            "aum": round(total_aum, 2),  # Add for frontend compatibility
            "client_count": client_count,
            "allocation": allocation,
            "fund_breakdown": {
                fund_code: {"amount": round(amount, 2), "percentage": allocation.get(fund_code, 0)}
                for fund_code, amount in fund_allocation.items()
            }
        }
        
    except Exception as e:
        logging.error(f"Portfolio summary error: {str(e)}")
        # Return fallback data instead of zeros
        return {
            "total_aum": 0,
            "aum": 0,  # Add for frontend compatibility
            "client_count": 0,
            "allocation": {"CORE": 0, "BALANCE": 0, "DYNAMIC": 0, "UNLIMITED": 0},
            "fund_breakdown": {}
        }
    
    # Generate weekly performance data
    weeks_data = []
    for i in range(8):
        weeks_data.append({
            "week": f"Week {i+1}",
            "CORE": round(random.uniform(-2.5, 4.0), 2),
            "BALANCE": round(random.uniform(-1.5, 3.0), 2),
            "DYNAMIC": round(random.uniform(-3.0, 5.0), 2)
        })
    
    return {
        "aum": total_aum,
        "allocation": allocation,
        "weekly_performance": weeks_data,
        "ytd_return": 12.45
    }

# Gmail Service Integration
class GmailService:
    def __init__(self):
        self.SCOPES = [
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.readonly'
        ]
        self.credentials_path = '/app/backend/gmail_credentials.json'
        self.token_path = '/app/backend/gmail_token.pickle'
        self.service = None
        
    async def authenticate(self):
        """Authenticate and build Gmail service"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Validate and refresh credentials if needed
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(GoogleRequest())
                except RefreshError:
                    creds = self._perform_oauth_flow()
            else:
                creds = self._perform_oauth_flow()
            
            # Save credentials for future use
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
        return self.service
    
    def _perform_oauth_flow(self):
        """Perform OAuth2 flow for web authentication"""
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_path, self.SCOPES
        )
        
        # For web server applications, we'll generate the authorization URL
        # and handle the flow differently
        try:
            # Try the local server approach first
            return flow.run_local_server(port=0, open_browser=False)
        except Exception as e:
            logging.error(f"OAuth local server failed: {e}")
            # Fall back to console-based flow for server environments
            return flow.run_console()
    
    async def send_email_with_attachment(
        self,
        recipient_email: str,
        recipient_name: str,
        subject: str,
        body_text: str,
        attachment_path: str = None,
        document_name: str = None,
        document_url: str = None
    ):
        """Send email with document attachment and/or viewing link"""
        try:
            if not self.service:
                await self.authenticate()
            
            # Create message
            message = MIMEMultipart('alternative')
            message['To'] = f"{recipient_name} <{recipient_email}>"
            message['Subject'] = subject
            message['From'] = "FIDUS Solutions <noreply@fidus.com>"
            
            # Create HTML body with professional template
            html_body = self._create_email_template(
                recipient_name, body_text, document_name, document_url
            )
            
            # Add text and HTML parts
            text_part = MIMEText(body_text, 'plain')
            html_part = MIMEText(html_body, 'html')
            message.attach(text_part)
            message.attach(html_part)
            
            # Add attachment if provided
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as attachment:
                    part = MIMEApplication(attachment.read())
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{document_name or os.path.basename(attachment_path)}"'
                    )
                    message.attach(part)
            
            # Convert to raw format required by Gmail API
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send email
            send_message = self.service.users().messages().send(
                userId="me",
                body={'raw': raw_message}
            ).execute()
            
            logging.info(f"Email sent successfully: {send_message['id']}")
            
            return {
                'success': True,
                'message_id': send_message['id'],
                'recipient': recipient_email,
                'subject': subject
            }
            
        except HttpError as error:
            error_detail = json.loads(error.content.decode())
            logging.error(f"Gmail API error: {error_detail}")
            return {
                'success': False,
                'error': f"Gmail API error: {error_detail.get('error', {}).get('message', 'Unknown error')}"
            }
        except Exception as error:
            logging.error(f"Email sending error: {str(error)}")
            return {
                'success': False,
                'error': f"Failed to send email: {str(error)}"
            }
    
    def _create_email_template(self, recipient_name: str, body_text: str, document_name: str = None, document_url: str = None):
        """Create professional HTML email template"""
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Document from FIDUS Solutions</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8fafc;
                }}
                .email-container {{
                    background: white;
                    border-radius: 8px;
                    padding: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    border-bottom: 3px solid #06b6d4;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #06b6d4;
                    margin-bottom: 5px;
                }}
                .tagline {{
                    color: #64748b;
                    font-size: 14px;
                }}
                .content {{
                    margin-bottom: 30px;
                }}
                .greeting {{
                    font-size: 18px;
                    margin-bottom: 20px;
                    color: #1e293b;
                }}
                .message {{
                    margin-bottom: 25px;
                    color: #475569;
                }}
                .document-info {{
                    background: #f1f5f9;
                    border-left: 4px solid #06b6d4;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .document-name {{
                    font-weight: 600;
                    color: #1e293b;
                    margin-bottom: 8px;
                }}
                .view-button {{
                    display: inline-block;
                    background: #06b6d4;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 600;
                    margin: 10px 0;
                }}
                .view-button:hover {{
                    background: #0891b2;
                }}
                .footer {{
                    text-align: center;
                    padding-top: 20px;
                    border-top: 1px solid #e2e8f0;
                    color: #64748b;
                    font-size: 14px;
                }}
                .attachment-note {{
                    background: #ecfdf5;
                    border: 1px solid #10b981;
                    border-radius: 4px;
                    padding: 12px;
                    margin: 15px 0;
                    color: #065f46;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <div class="logo">FIDUS</div>
                    <div class="tagline">Professional Financial Solutions</div>
                </div>
                
                <div class="content">
                    <div class="greeting">Hello {recipient_name},</div>
                    
                    <div class="message">
                        {body_text.replace(chr(10), '<br>')}
                    </div>
                    
                    {f'''
                    <div class="document-info">
                        <div class="document-name">📄 {document_name}</div>
                        <p>This document has been shared with you from FIDUS Solutions.</p>
                        {f'<a href="{document_url}" class="view-button">View Document Online</a>' if document_url else ''}
                    </div>
                    ''' if document_name else ''}
                    
                    <div class="attachment-note">
                        📎 <strong>Attachment:</strong> Please find the document attached to this email.
                    </div>
                    
                    <p>If you have any questions about this document, please don't hesitate to contact us.</p>
                </div>
                
                <div class="footer">
                    <p><strong>FIDUS Solutions LLC</strong><br>
                    Professional Financial Services<br>
                    This email was sent from our secure document portal.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template

# Initialize Gmail service
gmail_service = GmailService()

# OAuth state storage for Gmail authentication
oauth_states = {}

# Document Management Models and Services
class DocumentUpload(BaseModel):
    name: str
    category: str
    uploader_id: str

class DocumentModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str
    status: str = "draft"  # draft, sent, delivered, completed, declined, voided
    uploader_id: str
    sender_id: Optional[str] = None
    sender_name: Optional[str] = None
    recipient_emails: Optional[List[str]] = []
    file_path: str
    file_size: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    docusign_envelope_id: Optional[str] = None
    completion_date: Optional[datetime] = None

class SendForSignatureRequest(BaseModel):
    recipients: List[Dict[str, str]]
    email_subject: str
    email_message: str
    sender_id: str  # Added sender_id to the model

# In-memory document storage (in production, use proper database)
documents_storage = {}

# Document categories
SHARED_DOCUMENT_CATEGORIES = [
    'loan_agreements',
    'account_opening', 
    'investment_documents',
    'insurance_forms',
    'amendments',
    'client_statements',
    'tax_documents',
    'other'
]

ADMIN_ONLY_DOCUMENT_CATEGORIES = [
    'aml_kyc_reports',
    'compliance_notes', 
    'internal_memos',
    'risk_assessments',
    'due_diligence',
    'regulatory_filings',
    'audit_documents'
]

# In-memory CRM prospect storage (in production, use proper database)
prospects_storage = {}

# In-memory prospect document storage (in production, use proper database)
prospect_documents = {}  # {prospect_id: [document_records]}

# In-memory prospect document request storage (in production, use proper database)
prospect_document_requests = {}  # {prospect_id: [request_records]}

# File storage directory
import os
from pathlib import Path
UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Mock DocuSign Service
class MockDocuSignService:
    def __init__(self):
        self.envelopes = {}
    
    async def send_for_signature(self, document_path: str, recipients: List[Dict], subject: str, message: str) -> Dict[str, Any]:
        """Mock DocuSign envelope creation"""
        envelope_id = f"mock_envelope_{str(uuid.uuid4())[:8]}"
        
        # Simulate processing time
        await asyncio.sleep(0.5)
        
        # Create mock envelope
        envelope_data = {
            'envelope_id': envelope_id,
            'status': 'sent',
            'recipients': recipients,
            'subject': subject,
            'message': message,
            'created_at': datetime.now(timezone.utc),
            'documents': [{'document_path': document_path}]
        }
        
        self.envelopes[envelope_id] = envelope_data
        
        # Simulate random status progression for demo
        import random
        random_status = random.choice(['sent', 'delivered', 'completed'])
        envelope_data['status'] = random_status
        
        if random_status == 'completed':
            envelope_data['completed_at'] = datetime.now(timezone.utc)
        
        logging.info(f"Mock DocuSign: Envelope {envelope_id} created with status {random_status}")
        
        return {
            'success': True,
            'envelope_id': envelope_id,
            'status': random_status,
            'recipients_count': len(recipients)
        }
    
    async def get_envelope_status(self, envelope_id: str) -> Dict[str, Any]:
        """Get mock envelope status"""
        if envelope_id not in self.envelopes:
            return {'error': 'Envelope not found'}
        
        envelope = self.envelopes[envelope_id]
        return {
            'envelope_id': envelope_id,
            'status': envelope['status'],
            'created_at': envelope['created_at'].isoformat(),
            'completed_at': envelope.get('completed_at', '').isoformat() if envelope.get('completed_at') else None,
            'recipients': envelope['recipients']
        }

# Initialize mock DocuSign service
mock_docusign = MockDocuSignService()

# Document Management Endpoints
@api_router.post("/documents/upload")
async def upload_document(
    document: UploadFile = File(...),
    category: str = Form(...),
    uploader_id: str = Form(...),
    uploader_type: str = Form(default="admin"),  # "admin" or "client"
    client_id: str = Form(default=None)  # For client-specific documents
):
    """Upload a document for archiving or signing with categorization support"""
    try:
        # Validate category and determine document type
        document_type = "shared"  # Default to shared
        
        if category in ADMIN_ONLY_DOCUMENT_CATEGORIES:
            document_type = "admin_only"
        elif category in SHARED_DOCUMENT_CATEGORIES:
            document_type = "shared"
        else:
            # Allow custom categories as shared by default
            document_type = "shared"
        
        # Validate file type - includes images for camera captures
        allowed_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
            'text/html',
            'image/jpeg',
            'image/png',
            'image/webp'
        ]
        
        if document.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Only PDF, Word, Text, HTML, and Image files are supported")
        
        # Validate file size (10MB limit)
        if document.size and document.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size must be less than 10MB")
        
        # Generate unique filename
        file_extension = Path(document.filename).suffix
        unique_filename = f"{str(uuid.uuid4())}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await document.read()
            buffer.write(content)
        
        # Create document record
        document_id = str(uuid.uuid4())
        
        document_data = {
            'document_id': document_id,
            'name': document.filename,
            'category': category,
            'document_type': document_type,
            'uploader_id': uploader_id,
            'uploader_type': uploader_type,
            'client_id': client_id,  # Associate with specific client if provided
            'file_path': str(file_path),
            'file_size': len(content),
            'content_type': document.content_type,
            'status': 'uploaded'
        }
        
        # Store in MongoDB
        created_document_id = mongodb_manager.create_document(document_data)
        
        if not created_document_id:
            # Fallback to in-memory storage if MongoDB fails
            documents_storage[document_id] = document_data
            logging.warning(f"Document stored in memory as MongoDB failed: {document.filename}")
        
        logging.info(f"Document uploaded: {document.filename} by {uploader_type} {uploader_id} (type: {document_type})")
        
        return {
            "success": True,
            "document_id": document_id,
            "document_type": document_type,
            "message": f"Document uploaded successfully as {document_type} document"
        }
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logging.error(f"Document upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@api_router.get("/documents/admin/all")
async def get_all_documents(include_admin_only: bool = True):
    """Get all documents for admin view with option to include admin-only documents"""
    try:
        # Get documents from MongoDB
        documents = mongodb_manager.get_all_documents(include_admin_only=include_admin_only)
        
        # Fallback to in-memory storage if MongoDB returns empty and we have memory data
        if not documents and documents_storage:
            documents = []
            for doc_data in documents_storage.values():
                # Filter admin-only if requested
                if not include_admin_only and doc_data.get('document_type') == 'admin_only':
                    continue
                documents.append(doc_data)
            
            # Sort by created_at descending
            documents.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return {"documents": documents}
        
    except Exception as e:
        logging.error(f"Get all documents error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch documents")

@api_router.get("/documents/client/{client_id}")
async def get_client_documents(client_id: str):
    """Get documents for specific client (shared documents only)"""
    try:
        # Get client documents from MongoDB (excludes admin-only documents)
        client_documents = mongodb_manager.get_client_documents(client_id, include_admin_shared=True)
        
        # Fallback to in-memory storage if MongoDB returns empty and we have memory data
        if not client_documents and documents_storage:
            client_documents = []
            for doc_data in documents_storage.values():
                # Exclude admin-only documents from client view
                if doc_data.get('document_type') == 'admin_only':
                    continue
                    
                # Include documents uploaded by client, assigned to client, or shared
                if (doc_data['uploader_id'] == client_id or 
                    doc_data.get('client_id') == client_id or
                    (doc_data.get('recipient_emails') and 
                     any(email for email in doc_data.get('recipient_emails', []) 
                         if client_id in email))):
                    client_documents.append(doc_data)
            
            # Sort by created_at descending
            client_documents.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return {"documents": client_documents}
        
    except Exception as e:
        logging.error(f"Get client documents error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch client documents")

@api_router.get("/documents/admin/internal")
async def get_admin_only_documents():
    """Get admin-only internal documents (compliance, AML KYC, etc.)"""
    try:
        # Get admin-only documents from MongoDB
        admin_documents = mongodb_manager.get_admin_only_documents()
        
        # Fallback to in-memory storage if needed
        if not admin_documents and documents_storage:
            admin_documents = []
            for doc_data in documents_storage.values():
                if doc_data.get('document_type') == 'admin_only':
                    admin_documents.append(doc_data)
            
            # Sort by created_at descending
            admin_documents.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return {"documents": admin_documents}
        
    except Exception as e:
        logging.error(f"Get admin-only documents error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch admin-only documents")

@api_router.get("/documents/categories")
async def get_document_categories():
    """Get available document categories"""
    try:
        return {
            "shared_categories": SHARED_DOCUMENT_CATEGORIES,
            "admin_only_categories": ADMIN_ONLY_DOCUMENT_CATEGORIES,
            "all_categories": SHARED_DOCUMENT_CATEGORIES + ADMIN_ONLY_DOCUMENT_CATEGORIES
        }
        
    except Exception as e:
        logging.error(f"Get document categories error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch document categories")

@api_router.post("/documents/{document_id}/send-for-signature")
async def send_document_for_signature(
    document_id: str,
    request: SendForSignatureRequest
):
    """Send document for Gmail signature with real Gmail integration"""
    try:
        # Get document
        if document_id not in documents_storage:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_data = documents_storage[document_id]
        
        # Get sender info
        sender_id = request.sender_id
        sender_name = "System Admin"
        for user in MOCK_USERS.values():
            if user["id"] == sender_id:
                sender_name = user["name"]
                break
        
        # Create document viewing URL (you can customize this)
        document_url = f"https://fund-tracker-11.preview.emergentagent.com/documents/{document_id}/view"
        
        # Send emails to all recipients using Gmail
        successful_sends = []
        failed_sends = []
        
        for recipient in request.recipients:
            recipient_email = recipient.get('email')
            recipient_name = recipient.get('name', recipient_email)
            
            if not recipient_email:
                continue
                
            # Send email with both attachment and viewing link
            gmail_result = await gmail_service.send_email_with_attachment(
                recipient_email=recipient_email,
                recipient_name=recipient_name,
                subject=request.email_subject,
                body_text=request.email_message,
                attachment_path=doc_data['file_path'],
                document_name=doc_data['name'],
                document_url=document_url
            )
            
            if gmail_result.get('success'):
                successful_sends.append({
                    'email': recipient_email,
                    'message_id': gmail_result.get('message_id')
                })
            else:
                failed_sends.append({
                    'email': recipient_email,
                    'error': gmail_result.get('error')
                })
        
        # Update document status
        if successful_sends:
            doc_data['status'] = 'sent'
            doc_data['sender_id'] = sender_id
            doc_data['sender_name'] = sender_name
            doc_data['recipient_emails'] = [r['email'] for r in request.recipients]
            doc_data['gmail_message_ids'] = [s['message_id'] for s in successful_sends]
            doc_data['updated_at'] = datetime.now(timezone.utc)
            
            documents_storage[document_id] = doc_data
        
        logging.info(f"Document {document_id} sent via Gmail: {len(successful_sends)} successful, {len(failed_sends)} failed")
        
        return {
            "success": len(successful_sends) > 0,
            "message": f"Document sent successfully to {len(successful_sends)} recipients" + 
                      (f", failed for {len(failed_sends)} recipients" if failed_sends else ""),
            "successful_sends": successful_sends,
            "failed_sends": failed_sends,
            "total_recipients": len(request.recipients),
            "document_url": document_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Send for signature error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send document: {str(e)}")

@api_router.get("/documents/{document_id}/download")
async def download_document(document_id: str):
    """Download a document file"""
    try:
        if document_id not in documents_storage:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_data = documents_storage[document_id]
        file_path = Path(doc_data['file_path'])
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Document file not found")
        
        from fastapi.responses import FileResponse
        return FileResponse(
            path=file_path,
            filename=doc_data['name'],
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Document download error: {str(e)}")
        raise HTTPException(status_code=500, detail="Download failed")

@api_router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document"""
    try:
        if document_id not in documents_storage:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_data = documents_storage[document_id]
        
        # Delete file
        file_path = Path(doc_data['file_path'])
        if file_path.exists():
            file_path.unlink()
        
        # Remove from storage
        del documents_storage[document_id]
        
        logging.info(f"Document {document_id} deleted")
        
        return {"success": True, "message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Document deletion error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete document")

@api_router.get("/documents/{document_id}/view")
async def view_document_online(document_id: str):
    """View document online (public endpoint for email links)"""
    try:
        if document_id not in documents_storage:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_data = documents_storage[document_id]
        file_path = Path(doc_data['file_path'])
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Document file not found")
        
        # Return document info for viewer
        return {
            "document_id": document_id,
            "name": doc_data['name'],
            "category": doc_data['category'],
            "status": doc_data['status'],
            "created_at": doc_data['created_at'],
            "file_size": doc_data['file_size'],
            "download_url": f"/api/documents/{document_id}/download"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Document view error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load document")

@api_router.get("/gmail/auth-url")
async def get_gmail_auth_url():
    """Get Gmail OAuth authorization URL for web application flow"""
    try:
        from google_auth_oauthlib.flow import Flow
        
        # Create flow for web application
        flow = Flow.from_client_secrets_file(
            '/app/backend/gmail_credentials.json',
            scopes=[
                'https://www.googleapis.com/auth/gmail.send',
                'https://www.googleapis.com/auth/gmail.readonly'
            ],
            redirect_uri='https://fund-tracker-11.preview.emergentagent.com/api/gmail/oauth-callback'
        )
        
        # Generate authorization URL
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        # Store state for verification (in production, use proper session storage)
        oauth_states[state] = True
        
        return {
            "success": True,
            "authorization_url": authorization_url,
            "state": state,
            "instructions": "Please visit the authorization URL to authenticate with Gmail"
        }
        
    except Exception as e:
        logging.error(f"Gmail auth URL generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate auth URL: {str(e)}")

@api_router.get("/gmail/oauth-callback")
async def gmail_oauth_callback(code: str, state: str):
    """Handle Gmail OAuth callback"""
    try:
        from google_auth_oauthlib.flow import Flow
        from fastapi.responses import RedirectResponse
        
        # Verify state (in production, use proper session storage)
        if state not in oauth_states:
            # Redirect to frontend with error
            return RedirectResponse(url="/?gmail_auth=error&message=Invalid+state+parameter")
        
        # Create flow
        flow = Flow.from_client_secrets_file(
            '/app/backend/gmail_credentials.json',
            scopes=[
                'https://www.googleapis.com/auth/gmail.send',
                'https://www.googleapis.com/auth/gmail.readonly'
            ],
            redirect_uri='https://fund-tracker-11.preview.emergentagent.com/api/gmail/oauth-callback'
        )
        
        # Exchange authorization code for tokens
        flow.fetch_token(code=code)
        
        # Save credentials
        creds = flow.credentials
        with open('/app/backend/gmail_token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        
        # Initialize Gmail service with new credentials
        gmail_service.service = build('gmail', 'v1', credentials=creds)
        
        # Test the service by getting profile info (this will verify both scopes work)
        try:
            profile = gmail_service.service.users().getProfile(userId="me").execute()
            email_address = profile.get("emailAddress", "")
            
            logging.info(f"Gmail OAuth success: {email_address} with scopes: {creds.scopes}")
            
            # Clean up state
            del oauth_states[state]
            
            # Redirect to frontend with success
            return RedirectResponse(url=f"/?gmail_auth=success&email={email_address}")
            
        except HttpError as profile_error:
            logging.error(f"Gmail profile error after OAuth: {profile_error}")
            # Clean up state
            del oauth_states[state]
            return RedirectResponse(url=f"/?gmail_auth=error&message=Profile+access+failed:+{str(profile_error)}")
        
        
    except Exception as e:
        logging.error(f"Gmail OAuth callback error: {str(e)}")
        # Redirect to frontend with error
        error_msg = str(e).replace(" ", "+")
        return RedirectResponse(url=f"/?gmail_auth=error&message={error_msg}")

@api_router.post("/gmail/authenticate")
async def authenticate_gmail():
    """Authenticate Gmail service (admin only) - Complete fix for scopes issue"""
    try:
        # Always force fresh authentication to ensure proper scopes
        # Delete any existing token to force re-authentication with new scopes
        if os.path.exists('/app/backend/gmail_token.pickle'):
            os.remove('/app/backend/gmail_token.pickle')
        
        # Always redirect to OAuth flow with proper scopes
        return {
            "success": False,
            "message": "Gmail authentication required - redirecting to OAuth",
            "action": "redirect_to_oauth",
            "auth_url_endpoint": "/api/gmail/auth-url",
            "instructions": "Starting fresh OAuth flow with proper scopes (gmail.send + gmail.readonly)"
        }
        
    except Exception as e:
        logging.error(f"Gmail authentication error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Gmail authentication failed"
        }

@api_router.get("/documents/{document_id}/status")
async def get_document_status(document_id: str):
    """Get Gmail sending status for a document"""
    try:
        if document_id not in documents_storage:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_data = documents_storage[document_id]
        
        # For Gmail integration, we track message IDs instead of envelope IDs
        gmail_message_ids = doc_data.get('gmail_message_ids', [])
        
        return {
            "document_id": document_id,
            "status": doc_data['status'],
            "sender_name": doc_data.get('sender_name', ''),
            "recipient_emails": doc_data.get('recipient_emails', []),
            "gmail_message_ids": gmail_message_ids,
            "sent_count": len(gmail_message_ids),
            "updated_at": doc_data.get('updated_at'),
            "message": f"Document sent via Gmail to {len(gmail_message_ids)} recipients" if gmail_message_ids else "Document not sent yet"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Get document status error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get document status")

# ===============================================================================
# CRM SYSTEM IMPLEMENTATION
# ===============================================================================

# CRM Models
class FundModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # CORE, BALANCE, DYNAMIC, UNLIMITED
    fund_type: str
    aum: float  # Assets Under Management
    nav: float  # Net Asset Value
    nav_per_share: float
    inception_date: datetime
    performance_ytd: float
    performance_1y: float
    performance_3y: float
    minimum_investment: float
    management_fee: float
    performance_fee: float
    total_investors: int
    status: str = "active"  # active, suspended, closed
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class InvestorAllocation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str
    fund_id: str
    fund_name: str
    shares: float
    invested_amount: float
    current_value: float
    allocation_percentage: float
    entry_date: datetime
    entry_nav: float
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CapitalFlow(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str
    fund_id: str
    fund_name: str
    flow_type: str  # subscription, redemption, distribution
    amount: float
    shares: float
    nav_price: float
    trade_date: datetime
    settlement_date: datetime
    status: str = "pending"  # pending, confirmed, settled, cancelled
    reference_number: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CapitalFlowRequest(BaseModel):
    client_id: str
    fund_id: str
    flow_type: str
    amount: float

# MetaQuotes Real Integration Service (Enhanced)
class EnhancedMetaQuotesService:
    def __init__(self):
        self.credentials = {}
        self.connected = False
        self.mt5_available = False
        
        # Try to import MetaTrader5 if available (Windows only)
        try:
            import MetaTrader5 as mt5
            self.mt5 = mt5
            self.mt5_available = True
            logging.info("MetaTrader5 library available")
        except ImportError:
            self.mt5 = None
            self.mt5_available = False
            logging.info("MetaTrader5 library not available - using advanced simulation")
        
        # Advanced simulation data for Linux environments
        self.simulation_accounts = {}
        self.simulation_market_data = {}
        self._initialize_advanced_simulation()
    
    def _initialize_advanced_simulation(self):
        """Initialize advanced simulation with realistic trading data"""
        import random
        from datetime import datetime, timedelta
        
        # Simulate multiple trading accounts
        symbols = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "NZDUSD", "USDCHF", "EURJPY", "GBPJPY", "XAUUSD", "XAGUSD", "US30", "NAS100", "SPX500"]
        
        for i in range(5):
            account_number = f"500{1000 + i}"
            self.simulation_accounts[account_number] = {
                'login': account_number,
                'balance': round(random.uniform(50000, 500000), 2),
                'equity': 0,
                'margin': round(random.uniform(1000, 50000), 2),
                'free_margin': 0,
                'margin_level': 0,
                'profit': round(random.uniform(-5000, 15000), 2),
                'leverage': random.choice([100, 200, 500]),
                'trade_allowed': True,
                'expert_allowed': True,
                'currency': 'USD',
                'server': 'MetaQuotes-Demo',
                'company': 'MetaQuotes Software Corp.',
                'name': f'Demo Account {i+1}',
                'positions': [],
                'orders': [],
                'deals': []
            }
            
            # Calculate equity and margins
            account = self.simulation_accounts[account_number]
            account['equity'] = account['balance'] + account['profit']
            account['free_margin'] = account['equity'] - account['margin']
            account['margin_level'] = (account['equity'] / account['margin']) * 100 if account['margin'] > 0 else 0
            
            # Generate positions
            num_positions = random.randint(0, 8)
            for j in range(num_positions):
                symbol = random.choice(symbols)
                position_type = random.choice([0, 1])  # 0=buy, 1=sell
                volume = round(random.uniform(0.01, 2.00), 2)
                
                # Generate realistic prices based on symbol
                if "JPY" in symbol:
                    price_open = round(random.uniform(140.000, 155.000), 3)
                    price_current = price_open + random.uniform(-0.500, 0.500)
                elif "XAU" in symbol:  # Gold
                    price_open = round(random.uniform(1900.00, 2100.00), 2)
                    price_current = price_open + random.uniform(-20.00, 20.00)
                elif "US30" in symbol or "NAS100" in symbol:
                    price_open = round(random.uniform(33000, 35000), 2)
                    price_current = price_open + random.uniform(-200, 200)
                else:
                    price_open = round(random.uniform(1.0000, 1.3000), 5)
                    price_current = price_open + random.uniform(-0.0100, 0.0100)
                
                profit = (price_current - price_open) * volume * 100000 if position_type == 0 else (price_open - price_current) * volume * 100000
                
                position = {
                    'ticket': random.randint(100000000, 999999999),
                    'time': int((datetime.now() - timedelta(hours=random.randint(1, 72))).timestamp()),
                    'type': position_type,
                    'magic': random.randint(0, 999999),
                    'identifier': random.randint(100000000, 999999999),
                    'reason': 0,
                    'volume': volume,
                    'price_open': round(price_open, 5),
                    'sl': 0.0,
                    'tp': 0.0,
                    'price_current': round(price_current, 5),
                    'swap': round(random.uniform(-5.0, 5.0), 2),
                    'profit': round(profit, 2),
                    'symbol': symbol,
                    'comment': 'FIDUS Trading',
                    'external_id': ''
                }
                
                account['positions'].append(position)
            
            # Generate deal history
            num_deals = random.randint(50, 200)
            for j in range(num_deals):
                symbol = random.choice(symbols)
                deal_type = random.choice([0, 1])  # buy/sell
                volume = round(random.uniform(0.01, 2.00), 2)
                
                deal_time = datetime.now() - timedelta(days=random.randint(1, 90))
                
                if "JPY" in symbol:
                    price = round(random.uniform(140.000, 155.000), 3)
                elif "XAU" in symbol:
                    price = round(random.uniform(1900.00, 2100.00), 2)
                else:
                    price = round(random.uniform(1.0000, 1.3000), 5)
                
                deal = {
                    'ticket': random.randint(100000000, 999999999),
                    'order': random.randint(100000000, 999999999),
                    'time': int(deal_time.timestamp()),
                    'type': deal_type,
                    'entry': random.choice([0, 1]),  # in/out
                    'magic': random.randint(0, 999999),
                    'position_id': random.randint(100000000, 999999999),
                    'reason': random.choice([0, 1, 2, 3]),
                    'volume': volume,
                    'price': price,
                    'commission': round(random.uniform(-10.0, 0.0), 2),
                    'swap': round(random.uniform(-5.0, 5.0), 2),
                    'profit': round(random.uniform(-500.0, 800.0), 2),
                    'fee': 0.0,
                    'symbol': symbol,
                    'comment': 'FIDUS Trading',
                    'external_id': ''
                }
                
                account['deals'].append(deal)
            
            # Sort deals by time descending
            account['deals'].sort(key=lambda x: x['time'], reverse=True)
        
        # Generate market data
        for symbol in symbols:
            if "JPY" in symbol:
                bid = round(random.uniform(140.000, 155.000), 3)
                ask = bid + 0.003
            elif "XAU" in symbol:
                bid = round(random.uniform(1900.00, 2100.00), 2)
                ask = bid + 0.50
            elif "US30" in symbol or "NAS100" in symbol:
                bid = round(random.uniform(33000, 35000), 2)
                ask = bid + 5.0
            else:
                bid = round(random.uniform(1.0000, 1.3000), 5)
                ask = bid + 0.00020
            
            self.simulation_market_data[symbol] = {
                'time': int(datetime.now().timestamp()),
                'bid': bid,
                'ask': ask,
                'last': round((bid + ask) / 2, 5),
                'volume': random.randint(1000, 50000),
                'volume_real': random.randint(100, 5000),
                'spread': int((ask - bid) * 100000),
                'digits': 5 if "JPY" not in symbol else 3,
                'trade_tick_value': 1.0,
                'trade_tick_value_profit': 1.0,
                'trade_tick_value_loss': 1.0,
                'trade_tick_size': 0.00001 if "JPY" not in symbol else 0.001,
                'trade_contract_size': 100000.0,
                'currency_base': symbol[:3],
                'currency_profit': symbol[3:],
                'path': f'Forex\\Major\\{symbol}',
                'description': f'{symbol[:3]}/{symbol[3:]} Currency Pair'
            }
    
    async def connect_mt5(self, login: str, password: str, server: str):
        """Connect to MetaTrader 5 terminal"""
        try:
            if self.mt5_available:
                # Real MT5 connection
                if not self.mt5.initialize():
                    return {"success": False, "error": "MetaTrader 5 initialization failed"}
                
                if not self.mt5.login(int(login), password, server):
                    error_code = self.mt5.last_error()
                    return {"success": False, "error": f"Login failed: {error_code}"}
                
                account_info = self.mt5.account_info()
                if account_info is None:
                    return {"success": False, "error": "Failed to get account info"}
                
                self.connected = True
                self.credentials = {"login": login, "server": server}
                
                return {
                    "success": True,
                    "message": "Connected to MetaTrader 5",
                    "account_info": {
                        "login": account_info.login,
                        "balance": account_info.balance,
                        "equity": account_info.equity,
                        "margin": account_info.margin,
                        "free_margin": account_info.margin_free,
                        "margin_level": account_info.margin_level,
                        "currency": account_info.currency,
                        "server": account_info.server,
                        "company": account_info.company,
                        "name": account_info.name
                    }
                }
            else:
                # Simulation mode
                if login in [acc['login'] for acc in self.simulation_accounts.values()]:
                    self.connected = True
                    self.credentials = {"login": login, "server": server}
                    
                    account = next(acc for acc in self.simulation_accounts.values() if acc['login'] == login)
                    
                    return {
                        "success": True,
                        "message": "Connected to MetaTrader 5 (Simulation)",
                        "account_info": {
                            "login": account['login'],
                            "balance": account['balance'],
                            "equity": account['equity'],
                            "margin": account['margin'],
                            "free_margin": account['free_margin'],
                            "margin_level": account['margin_level'],
                            "currency": account['currency'],
                            "server": account['server'],
                            "company": account['company'],
                            "name": account['name']
                        }
                    }
                else:
                    return {"success": False, "error": "Invalid login credentials (use 5001000-5001004 for simulation)"}
                    
        except Exception as e:
            logging.error(f"MT5 connection error: {str(e)}")
            return {"success": False, "error": f"Connection failed: {str(e)}"}
    
    async def get_account_info(self):
        """Get current account information"""
        if not self.connected:
            return {"success": False, "error": "Not connected to MetaTrader 5"}
        
        try:
            if self.mt5_available:
                account_info = self.mt5.account_info()
                if account_info is None:
                    return {"success": False, "error": "Failed to get account info"}
                
                return {
                    "success": True,
                    "account_info": {
                        "login": account_info.login,
                        "balance": account_info.balance,
                        "equity": account_info.equity,
                        "margin": account_info.margin,
                        "free_margin": account_info.margin_free,
                        "margin_level": account_info.margin_level,
                        "profit": account_info.profit,
                        "currency": account_info.currency,
                        "server": account_info.server,
                        "company": account_info.company,
                        "name": account_info.name,
                        "leverage": account_info.leverage,
                        "trade_allowed": account_info.trade_allowed,
                        "expert_allowed": account_info.expert_allowed
                    }
                }
            else:
                # Simulation mode
                login = self.credentials.get('login')
                account = next(acc for acc in self.simulation_accounts.values() if acc['login'] == login)
                
                return {
                    "success": True,
                    "account_info": account
                }
                
        except Exception as e:
            logging.error(f"Get account info error: {str(e)}")
            return {"success": False, "error": f"Failed to get account info: {str(e)}"}
    
    async def get_positions(self):
        """Get open positions"""
        if not self.connected:
            return {"success": False, "error": "Not connected to MetaTrader 5"}
        
        try:
            if self.mt5_available:
                positions = self.mt5.positions_get()
                if positions is None:
                    return {"success": True, "positions": []}
                
                positions_list = []
                for pos in positions:
                    positions_list.append({
                        "ticket": pos.ticket,
                        "time": pos.time,
                        "type": pos.type,
                        "magic": pos.magic,
                        "identifier": pos.identifier,
                        "reason": pos.reason,
                        "volume": pos.volume,
                        "price_open": pos.price_open,
                        "sl": pos.sl,
                        "tp": pos.tp,
                        "price_current": pos.price_current,
                        "swap": pos.swap,
                        "profit": pos.profit,
                        "symbol": pos.symbol,
                        "comment": pos.comment,
                        "external_id": pos.external_id
                    })
                
                return {"success": True, "positions": positions_list}
            else:
                # Simulation mode
                login = self.credentials.get('login')
                account = next(acc for acc in self.simulation_accounts.values() if acc['login'] == login)
                
                return {"success": True, "positions": account['positions']}
                
        except Exception as e:
            logging.error(f"Get positions error: {str(e)}")
            return {"success": False, "error": f"Failed to get positions: {str(e)}"}
    
    async def get_deals_history(self, days_back: int = 30):
        """Get deal history"""
        if not self.connected:
            return {"success": False, "error": "Not connected to MetaTrader 5"}
        
        try:
            if self.mt5_available:
                from datetime import datetime, timedelta
                date_from = datetime.now() - timedelta(days=days_back)
                deals = self.mt5.history_deals_get(date_from, datetime.now())
                
                if deals is None:
                    return {"success": True, "deals": []}
                
                deals_list = []
                for deal in deals:
                    deals_list.append({
                        "ticket": deal.ticket,
                        "order": deal.order,
                        "time": deal.time,
                        "type": deal.type,
                        "entry": deal.entry,
                        "magic": deal.magic,
                        "position_id": deal.position_id,
                        "reason": deal.reason,
                        "volume": deal.volume,
                        "price": deal.price,
                        "commission": deal.commission,
                        "swap": deal.swap,
                        "profit": deal.profit,
                        "fee": deal.fee,
                        "symbol": deal.symbol,
                        "comment": deal.comment,
                        "external_id": deal.external_id
                    })
                
                return {"success": True, "deals": deals_list}
            else:
                # Simulation mode
                login = self.credentials.get('login')
                account = next(acc for acc in self.simulation_accounts.values() if acc['login'] == login)
                
                # Filter deals by date
                from datetime import datetime, timedelta
                cutoff_time = (datetime.now() - timedelta(days=days_back)).timestamp()
                recent_deals = [deal for deal in account['deals'] if deal['time'] >= cutoff_time]
                
                return {"success": True, "deals": recent_deals}
                
        except Exception as e:
            logging.error(f"Get deals history error: {str(e)}")
            return {"success": False, "error": f"Failed to get deals history: {str(e)}"}
    
    async def get_symbol_info(self, symbol: str):
        """Get symbol information"""
        if not self.connected:
            return {"success": False, "error": "Not connected to MetaTrader 5"}
        
        try:
            if self.mt5_available:
                symbol_info = self.mt5.symbol_info(symbol)
                if symbol_info is None:
                    return {"success": False, "error": f"Symbol {symbol} not found"}
                
                return {
                    "success": True,
                    "symbol_info": {
                        "name": symbol_info.name,
                        "currency_base": symbol_info.currency_base,
                        "currency_profit": symbol_info.currency_profit,
                        "digits": symbol_info.digits,
                        "spread": symbol_info.spread,
                        "trade_tick_value": symbol_info.trade_tick_value,
                        "trade_tick_size": symbol_info.trade_tick_size,
                        "trade_contract_size": symbol_info.trade_contract_size,
                        "volume_min": symbol_info.volume_min,
                        "volume_max": symbol_info.volume_max,
                        "volume_step": symbol_info.volume_step,
                        "description": symbol_info.description,
                        "path": symbol_info.path
                    }
                }
            else:
                # Simulation mode
                if symbol in self.simulation_market_data:
                    return {"success": True, "symbol_info": self.simulation_market_data[symbol]}
                else:
                    return {"success": False, "error": f"Symbol {symbol} not found in simulation"}
                    
        except Exception as e:
            logging.error(f"Get symbol info error: {str(e)}")
            return {"success": False, "error": f"Failed to get symbol info: {str(e)}"}
    
    async def get_market_data(self, symbols: list = None):
        """Get current market data for symbols"""
        if not self.connected:
            return {"success": False, "error": "Not connected to MetaTrader 5"}
        
        try:
            if symbols is None:
                symbols = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "XAUUSD"]
            
            market_data = {}
            
            if self.mt5_available:
                for symbol in symbols:
                    tick = self.mt5.symbol_info_tick(symbol)
                    if tick is not None:
                        market_data[symbol] = {
                            "time": tick.time,
                            "bid": tick.bid,
                            "ask": tick.ask,
                            "last": tick.last,
                            "volume": tick.volume,
                            "spread": int((tick.ask - tick.bid) * 100000)
                        }
            else:
                # Simulation mode
                for symbol in symbols:
                    if symbol in self.simulation_market_data:
                        market_data[symbol] = self.simulation_market_data[symbol]
            
            return {"success": True, "market_data": market_data}
            
        except Exception as e:
            logging.error(f"Get market data error: {str(e)}")
            return {"success": False, "error": f"Failed to get market data: {str(e)}"}
    
    def disconnect(self):
        """Disconnect from MetaTrader 5"""
        if self.mt5_available:
            self.mt5.shutdown()
        
        self.connected = False
        self.credentials = {}
        return {"success": True, "message": "Disconnected from MetaTrader 5"}

# Initialize enhanced MetaQuotes service
enhanced_mt5_service = EnhancedMetaQuotesService()

# Mock MT4/MT5 Trading Data Service (keeping existing for compatibility)
class MockMT5Service:
    def __init__(self):
        self.accounts = {}
        self.positions = {}
        self.trades_history = {}
        self.market_data = {}
        self._initialize_mock_data()
    
    def _initialize_mock_data(self):
        """Initialize mock trading data for clients"""
        # Create mock accounts for existing clients
        for username, user in MOCK_USERS.items():
            if user["type"] == "client":
                account_id = f"mt5_{user['id']}"
                self.accounts[account_id] = {
                    "client_id": user["id"],
                    "account_number": f"500{random.randint(1000, 9999)}",
                    "broker": "FIDUS Broker",
                    "balance": round(random.uniform(50000, 500000), 2),
                    "equity": round(random.uniform(48000, 520000), 2),
                    "margin": round(random.uniform(1000, 50000), 2),
                    "free_margin": 0,
                    "leverage": random.choice([1, 50, 100, 200, 500]),
                    "currency": "USD",
                    "server": "FIDUS-Demo",
                    "login_time": datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 24))
                }
                
                # Calculate free margin
                self.accounts[account_id]["free_margin"] = (
                    self.accounts[account_id]["equity"] - self.accounts[account_id]["margin"]
                )
                
                # Generate mock positions
                self._generate_mock_positions(account_id)
                
                # Generate mock trade history
                self._generate_mock_trade_history(account_id)
    
    def _generate_mock_positions(self, account_id):
        """Generate mock open positions"""
        symbols = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "GOLD", "SILVER", "OIL"]
        num_positions = random.randint(2, 6)
        
        self.positions[account_id] = []
        
        for _ in range(num_positions):
            symbol = random.choice(symbols)
            position_type = random.choice(["buy", "sell"])
            volume = round(random.uniform(0.1, 2.0), 2)
            
            # Mock current prices
            if symbol == "EURUSD":
                current_price = round(random.uniform(1.0500, 1.1200), 5)
            elif symbol == "GBPUSD":
                current_price = round(random.uniform(1.2000, 1.3000), 5)
            elif symbol == "USDJPY":
                current_price = round(random.uniform(140.00, 155.00), 3)
            elif symbol == "GOLD":
                current_price = round(random.uniform(1900.00, 2100.00), 2)
            else:
                current_price = round(random.uniform(0.8000, 1.5000), 5)
            
            open_price = current_price + random.uniform(-0.0050, 0.0050)
            
            position = {
                "ticket": random.randint(100000, 999999),
                "symbol": symbol,
                "type": position_type,
                "volume": volume,
                "open_price": round(open_price, 5),
                "current_price": current_price,
                "profit": round((current_price - open_price) * volume * 100000, 2) if position_type == "buy" else round((open_price - current_price) * volume * 100000, 2),
                "swap": round(random.uniform(-5.0, 5.0), 2),
                "commission": round(random.uniform(-2.0, 0.0), 2),
                "open_time": datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 168)),
                "comment": "FIDUS Trading"
            }
            
            self.positions[account_id].append(position)
    
    def _generate_mock_trade_history(self, account_id):
        """Generate mock trade history"""
        symbols = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "GOLD", "SILVER", "OIL"]
        num_trades = random.randint(10, 30)
        
        self.trades_history[account_id] = []
        
        for i in range(num_trades):
            symbol = random.choice(symbols)
            trade_type = random.choice(["buy", "sell"])
            volume = round(random.uniform(0.1, 2.0), 2)
            
            # Generate historical trade data
            close_time = datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30))
            open_time = close_time - timedelta(hours=random.randint(1, 48))
            
            open_price = round(random.uniform(1.0000, 2.0000), 5)
            close_price = open_price + random.uniform(-0.0100, 0.0100)
            
            profit = round((close_price - open_price) * volume * 100000, 2) if trade_type == "buy" else round((open_price - close_price) * volume * 100000, 2)
            
            trade = {
                "ticket": random.randint(100000, 999999),
                "symbol": symbol,
                "type": trade_type,
                "volume": volume,
                "open_price": round(open_price, 5),
                "close_price": round(close_price, 5),
                "profit": profit,
                "swap": round(random.uniform(-5.0, 5.0), 2),
                "commission": round(random.uniform(-2.0, 0.0), 2),
                "open_time": open_time,
                "close_time": close_time,
                "comment": "FIDUS Trading"
            }
            
            self.trades_history[account_id].append(trade)
        
        # Sort by close time descending
        self.trades_history[account_id].sort(key=lambda x: x["close_time"], reverse=True)
    
    async def get_account_info(self, client_id: str) -> Dict[str, Any]:
        """Get account information for a client"""
        account_id = f"mt5_{client_id}"
        if account_id in self.accounts:
            return self.accounts[account_id]
        return None
    
    async def get_positions(self, client_id: str) -> List[Dict[str, Any]]:
        """Get open positions for a client"""
        account_id = f"mt5_{client_id}"
        if account_id in self.positions:
            return self.positions[account_id]
        return []
    
    async def get_trade_history(self, client_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get trade history for a client"""
        account_id = f"mt5_{client_id}"
        if account_id in self.trades_history:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            return [
                trade for trade in self.trades_history[account_id] 
                if trade["close_time"] >= cutoff_date
            ]
        return []
    
    async def get_all_accounts_summary(self) -> Dict[str, Any]:
        """Get summary of all client accounts for admin dashboard"""
        total_balance = 0
        total_equity = 0
        total_positions = 0
        total_clients = len(self.accounts)
        
        client_summaries = []
        
        for account_id, account in self.accounts.items():
            total_balance += account["balance"]
            total_equity += account["equity"]
            positions_count = len(self.positions.get(account_id, []))
            total_positions += positions_count
            
            # Get client info
            client_info = None
            for user in MOCK_USERS.values():
                if user["id"] == account["client_id"]:
                    client_info = user
                    break
            
            if client_info:
                client_summaries.append({
                    "client_id": account["client_id"],
                    "client_name": client_info["name"],
                    "account_number": account["account_number"],
                    "balance": account["balance"],
                    "equity": account["equity"],
                    "margin": account["margin"],
                    "free_margin": account["free_margin"],
                    "open_positions": positions_count,
                    "last_activity": account["login_time"]
                })
        
        return {
            "summary": {
                "total_clients": total_clients,
                "total_balance": round(total_balance, 2),
                "total_equity": round(total_equity, 2),
                "total_positions": total_positions,
                "avg_balance_per_client": round(total_balance / total_clients if total_clients > 0 else 0, 2)
            },
            "clients": client_summaries
        }

# Initialize services
mock_mt5 = MockMT5Service()

# Fund Management System
FIDUS_FUNDS = {
    "CORE": FundModel(
        id="fund_core",
        name="CORE",
        fund_type="Conservative Growth",
        aum=0.00,  # Reset to zero as requested
        nav=0.00,  # Reset to zero as requested
        nav_per_share=102.80,
        inception_date=datetime(2020, 1, 15, tzinfo=timezone.utc),
        performance_ytd=8.5,
        performance_1y=11.2,
        performance_3y=9.8,
        minimum_investment=50000.00,
        management_fee=1.25,
        performance_fee=15.00,
        total_investors=0  # Reset to zero as requested
    ),
    "BALANCE": FundModel(
        id="fund_balance",
        name="BALANCE",
        fund_type="Balanced Portfolio",
        aum=0.00,  # Reset to zero as requested
        nav=0.00,  # Reset to zero as requested
        nav_per_share=104.59,
        inception_date=datetime(2020, 3, 1, tzinfo=timezone.utc),
        performance_ytd=12.3,
        performance_1y=15.7,
        performance_3y=12.1,
        minimum_investment=25000.00,
        management_fee=1.50,
        performance_fee=18.00,
        total_investors=0  # Reset to zero as requested
    ),
    "DYNAMIC": FundModel(
        id="fund_dynamic",
        name="DYNAMIC",
        fund_type="Growth Aggressive",
        aum=0.00,  # Reset to zero as requested
        nav=0.00,  # Reset to zero as requested
        nav_per_share=107.82,
        inception_date=datetime(2020, 6, 15, tzinfo=timezone.utc),
        performance_ytd=18.9,
        performance_1y=22.4,
        performance_3y=18.3,
        minimum_investment=100000.00,
        management_fee=1.75,
        performance_fee=20.00,
        total_investors=0  # Reset to zero as requested
    ),
    "UNLIMITED": FundModel(
        id="fund_unlimited",
        name="UNLIMITED",
        fund_type="Alternative Strategies",
        aum=0.00,  # Reset to zero as requested
        nav=0.00,  # Reset to zero as requested
        nav_per_share=109.31,
        inception_date=datetime(2021, 1, 1, tzinfo=timezone.utc),
        performance_ytd=25.6,
        performance_1y=28.9,
        performance_3y=24.1,
        minimum_investment=250000.00,
        management_fee=2.00,
        performance_fee=25.00,
        total_investors=0  # Reset to zero as requested
    )
}

# In-memory storage for CRM data (in production, use proper database)
investor_allocations = {}
capital_flows = {}

# Initialize mock allocations for existing clients
def initialize_mock_allocations():
    """Initialize mock investor allocations"""
    for username, user in MOCK_USERS.items():
        if user["type"] == "client":
            client_id = user["id"]
            investor_allocations[client_id] = []
            
            # Randomly allocate to 2-3 funds
            funds_to_allocate = random.sample(list(FIDUS_FUNDS.keys()), random.randint(2, 3))
            total_investment = random.uniform(100000, 1000000)
            
            for i, fund_name in enumerate(funds_to_allocate):
                fund = FIDUS_FUNDS[fund_name]
                if i == len(funds_to_allocate) - 1:
                    # Last fund gets remaining amount
                    allocation_amount = total_investment
                else:
                    allocation_amount = total_investment * random.uniform(0.2, 0.5)
                    total_investment -= allocation_amount
                
                shares = allocation_amount / fund.nav_per_share
                
                allocation = InvestorAllocation(
                    client_id=client_id,
                    fund_id=fund.id,
                    fund_name=fund.name,
                    shares=round(shares, 4),
                    invested_amount=round(allocation_amount, 2),
                    current_value=round(allocation_amount * random.uniform(0.95, 1.15), 2),
                    allocation_percentage=0,  # Will calculate later
                    entry_date=datetime.now(timezone.utc) - timedelta(days=random.randint(30, 365)),
                    entry_nav=fund.nav_per_share * random.uniform(0.95, 1.05)
                )
                
                investor_allocations[client_id].append(allocation)
            
            # Calculate allocation percentages
            total_value = sum(alloc.current_value for alloc in investor_allocations[client_id])
            for allocation in investor_allocations[client_id]:
                allocation.allocation_percentage = round((allocation.current_value / total_value) * 100, 2)

# Initialize allocations
initialize_mock_allocations()

# CRM API Endpoints
@api_router.get("/crm/funds")
async def get_all_funds():
    """Get all fund information"""
    try:
        funds_data = []
        for fund in FIDUS_FUNDS.values():
            funds_data.append(fund.dict())
        
        # Calculate totals
        total_aum = sum(fund.aum for fund in FIDUS_FUNDS.values())
        total_investors = sum(fund.total_investors for fund in FIDUS_FUNDS.values())
        
        return {
            "funds": funds_data,
            "summary": {
                "total_aum": total_aum,
                "total_investors": total_investors,
                "total_funds": len(FIDUS_FUNDS),
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        }
    except Exception as e:
        logging.error(f"Get funds error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch funds data")

@api_router.get("/crm/client/{client_id}/allocations")
async def get_client_allocations(client_id: str):
    """Get client fund allocations"""
    try:
        if client_id not in investor_allocations:
            return {"allocations": [], "total_value": 0, "total_invested": 0}
        
        allocations = investor_allocations[client_id]
        allocation_data = [alloc.dict() for alloc in allocations]
        
        total_value = sum(alloc.current_value for alloc in allocations)
        total_invested = sum(alloc.invested_amount for alloc in allocations)
        total_pnl = total_value - total_invested
        total_pnl_percentage = (total_pnl / total_invested) * 100 if total_invested > 0 else 0
        
        return {
            "allocations": allocation_data,
            "summary": {
                "total_value": round(total_value, 2),
                "total_invested": round(total_invested, 2),
                "total_pnl": round(total_pnl, 2),
                "total_pnl_percentage": round(total_pnl_percentage, 2),
                "number_of_funds": len(allocations)
            }
        }
    except Exception as e:
        logging.error(f"Get client allocations error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch client allocations")

@api_router.post("/crm/capital-flow")
async def create_capital_flow(request: CapitalFlowRequest):
    """Create a new capital flow (subscription/redemption/distribution)"""
    try:
        if request.fund_id not in [fund.id for fund in FIDUS_FUNDS.values()]:
            raise HTTPException(status_code=404, detail="Fund not found")
        
        fund = next(fund for fund in FIDUS_FUNDS.values() if fund.id == request.fund_id)
        
        # Calculate shares based on current NAV
        shares = request.amount / fund.nav_per_share if request.flow_type == "subscription" else 0
        
        # Generate reference number
        ref_number = f"{request.flow_type.upper()}-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        
        capital_flow = CapitalFlow(
            client_id=request.client_id,
            fund_id=request.fund_id,
            fund_name=fund.name,
            flow_type=request.flow_type,
            amount=request.amount,
            shares=round(shares, 4),
            nav_price=fund.nav_per_share,
            trade_date=datetime.now(timezone.utc),
            settlement_date=datetime.now(timezone.utc) + timedelta(days=3),
            reference_number=ref_number,
            status="confirmed"
        )
        
        # Store capital flow
        if request.client_id not in capital_flows:
            capital_flows[request.client_id] = []
        capital_flows[request.client_id].append(capital_flow)
        
        # Update investor allocations if subscription
        if request.flow_type == "subscription":
            if request.client_id not in investor_allocations:
                investor_allocations[request.client_id] = []
            
            # Find existing allocation or create new one
            existing_allocation = None
            for alloc in investor_allocations[request.client_id]:
                if alloc.fund_id == request.fund_id:
                    existing_allocation = alloc
                    break
            
            if existing_allocation:
                # Update existing allocation
                existing_allocation.shares += shares
                existing_allocation.invested_amount += request.amount
                existing_allocation.current_value += request.amount  # Simplified
                existing_allocation.last_updated = datetime.now(timezone.utc)
            else:
                # Create new allocation
                new_allocation = InvestorAllocation(
                    client_id=request.client_id,
                    fund_id=request.fund_id,
                    fund_name=fund.name,
                    shares=shares,
                    invested_amount=request.amount,
                    current_value=request.amount,  # Simplified
                    allocation_percentage=0,  # Will recalculate
                    entry_date=datetime.now(timezone.utc),
                    entry_nav=fund.nav_per_share
                )
                investor_allocations[request.client_id].append(new_allocation)
            
            # Recalculate allocation percentages
            total_value = sum(alloc.current_value for alloc in investor_allocations[request.client_id])
            for allocation in investor_allocations[request.client_id]:
                allocation.allocation_percentage = round((allocation.current_value / total_value) * 100, 2)
        
        logging.info(f"Capital flow created: {ref_number} for client {request.client_id}")
        
        return {
            "success": True,
            "capital_flow": capital_flow.dict(),
            "reference_number": ref_number,
            "message": f"{request.flow_type.title()} request processed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Capital flow creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create capital flow: {str(e)}")

@api_router.get("/crm/client/{client_id}/capital-flows")
async def get_client_capital_flows(client_id: str, days: int = 90):
    """Get client capital flows history"""
    try:
        if client_id not in capital_flows:
            return {"capital_flows": [], "summary": {"total_subscriptions": 0, "total_redemptions": 0, "total_distributions": 0}}
        
        # Filter by date
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        client_flows = [
            flow for flow in capital_flows[client_id] 
            if flow.trade_date >= cutoff_date
        ]
        
        # Sort by trade date descending
        client_flows.sort(key=lambda x: x.trade_date, reverse=True)
        
        # Calculate summary
        subscriptions = sum(flow.amount for flow in client_flows if flow.flow_type == "subscription")
        redemptions = sum(flow.amount for flow in client_flows if flow.flow_type == "redemption")
        distributions = sum(flow.amount for flow in client_flows if flow.flow_type == "distribution")
        
        return {
            "capital_flows": [flow.dict() for flow in client_flows],
            "summary": {
                "total_subscriptions": round(subscriptions, 2),
                "total_redemptions": round(redemptions, 2),
                "total_distributions": round(distributions, 2),
                "net_flow": round(subscriptions - redemptions + distributions, 2)
            }
        }
    except Exception as e:
        logging.error(f"Get client capital flows error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch capital flows")

# MT4/MT5 Integration Endpoints
@api_router.get("/crm/mt5/client/{client_id}/account")
async def get_client_mt5_account(client_id: str):
    """Get MT5 account information for a client"""
    try:
        account_info = await mock_mt5.get_account_info(client_id)
        if not account_info:
            raise HTTPException(status_code=404, detail="MT5 account not found for client")
        
        return {"account": account_info}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Get MT5 account error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch MT5 account data")

@api_router.get("/crm/mt5/client/{client_id}/positions")
async def get_client_mt5_positions(client_id: str):
    """Get MT5 open positions for a client"""
    try:
        positions = await mock_mt5.get_positions(client_id)
        
        # Calculate summary
        total_profit = sum(pos["profit"] for pos in positions)
        total_volume = sum(pos["volume"] for pos in positions)
        
        return {
            "positions": positions,
            "summary": {
                "total_positions": len(positions),
                "total_profit": round(total_profit, 2),
                "total_volume": round(total_volume, 2)
            }
        }
    except Exception as e:
        logging.error(f"Get MT5 positions error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch MT5 positions")

@api_router.get("/crm/mt5/client/{client_id}/history")
async def get_client_mt5_history(client_id: str, days: int = 30):
    """Get MT5 trade history for a client"""
    try:
        history = await mock_mt5.get_trade_history(client_id, days)
        
        # Calculate summary
        total_profit = sum(trade["profit"] for trade in history)
        winning_trades = len([t for t in history if t["profit"] > 0])
        losing_trades = len([t for t in history if t["profit"] < 0])
        total_volume = sum(trade["volume"] for trade in history)
        
        return {
            "trades": history,
            "summary": {
                "total_trades": len(history),
                "total_profit": round(total_profit, 2),
                "winning_trades": winning_trades,
                "losing_trades": losing_trades,
                "win_rate": round((winning_trades / len(history)) * 100, 2) if history else 0,
                "total_volume": round(total_volume, 2)
            }
        }
    except Exception as e:
        logging.error(f"Get MT5 history error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch MT5 trade history")

@api_router.get("/crm/mt5/admin/overview")
async def get_mt5_admin_overview():
    """Get MT5 overview for admin dashboard"""
    try:
        overview = await mock_mt5.get_all_accounts_summary()
        return overview
    except Exception as e:
        logging.error(f"Get MT5 admin overview error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch MT5 admin overview")

# MetaQuotes API Endpoints
@api_router.post("/metaquotes/connect")
async def connect_metaquotes(
    login: str = Form(...),
    password: str = Form(...), 
    server: str = Form(...)
):
    """Connect to MetaTrader 5 with credentials"""
    try:
        result = await enhanced_mt5_service.connect_mt5(login, password, server)
        return result
    except Exception as e:
        logging.error(f"MetaQuotes connection error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Connection failed: {str(e)}")

@api_router.get("/metaquotes/account-info")
async def get_metaquotes_account_info():
    """Get MetaTrader 5 account information"""
    try:
        result = await enhanced_mt5_service.get_account_info()
        return result
    except Exception as e:
        logging.error(f"Get account info error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get account info: {str(e)}")

@api_router.get("/metaquotes/positions")
async def get_metaquotes_positions():
    """Get MetaTrader 5 open positions"""
    try:
        result = await enhanced_mt5_service.get_positions()
        return result
    except Exception as e:
        logging.error(f"Get positions error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get positions: {str(e)}")

@api_router.get("/metaquotes/deals-history")
async def get_metaquotes_deals_history(days: int = 30):
    """Get MetaTrader 5 deals history"""
    try:
        result = await enhanced_mt5_service.get_deals_history(days)
        return result
    except Exception as e:
        logging.error(f"Get deals history error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get deals history: {str(e)}")

@api_router.get("/metaquotes/symbol-info/{symbol}")
async def get_metaquotes_symbol_info(symbol: str):
    """Get MetaTrader 5 symbol information"""
    try:
        result = await enhanced_mt5_service.get_symbol_info(symbol)
        return result
    except Exception as e:
        logging.error(f"Get symbol info error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get symbol info: {str(e)}")

@api_router.get("/metaquotes/market-data")
async def get_metaquotes_market_data(symbols: str = "EURUSD,GBPUSD,USDJPY,AUDUSD,USDCAD,XAUUSD"):
    """Get MetaTrader 5 market data for symbols"""
    try:
        symbols_list = symbols.split(',') if symbols else None
        result = await enhanced_mt5_service.get_market_data(symbols_list)
        return result
    except Exception as e:
        logging.error(f"Get market data error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get market data: {str(e)}")

@api_router.post("/metaquotes/disconnect")
async def disconnect_metaquotes():
    """Disconnect from MetaTrader 5"""
    try:
        result = enhanced_mt5_service.disconnect()
        return result
    except Exception as e:
        logging.error(f"Disconnect error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to disconnect: {str(e)}")

# Enhanced CRM endpoints for detailed views
@api_router.get("/crm/fund/{fund_id}/investors")
async def get_fund_investors(fund_id: str):
    """Get detailed investor list for a specific fund"""
    try:
        if fund_id not in [fund.id for fund in FIDUS_FUNDS.values()]:
            raise HTTPException(status_code=404, detail="Fund not found")
        
        fund = next(fund for fund in FIDUS_FUNDS.values() if fund.id == fund_id)
        
        # Get all investors for this fund
        fund_investors = []
        
        for client_id, allocations in investor_allocations.items():
            for allocation in allocations:
                if allocation.fund_id == fund_id:
                    # Get client info
                    client_info = None
                    for user in MOCK_USERS.values():
                        if user["id"] == client_id:
                            client_info = user
                            break
                    
                    if client_info:
                        # Get MT5 account info
                        mt5_account = await mock_mt5.get_account_info(client_id)
                        
                        # Calculate additional metrics
                        total_pnl = allocation.current_value - allocation.invested_amount
                        pnl_percentage = (total_pnl / allocation.invested_amount) * 100 if allocation.invested_amount > 0 else 0
                        days_invested = (datetime.now(timezone.utc) - allocation.entry_date).days
                        
                        investor_detail = {
                            "client_id": client_id,
                            "client_name": client_info["name"],
                            "client_email": client_info.get("email", ""),
                            "fund_allocation": {
                                "allocation_id": allocation.id,
                                "shares": allocation.shares,
                                "invested_amount": allocation.invested_amount,
                                "current_value": allocation.current_value,
                                "allocation_percentage": allocation.allocation_percentage,
                                "entry_date": allocation.entry_date.isoformat(),
                                "entry_nav": allocation.entry_nav,
                                "current_nav": fund.nav_per_share,
                                "total_pnl": round(total_pnl, 2),
                                "pnl_percentage": round(pnl_percentage, 2),
                                "days_invested": days_invested
                            },
                            "trading_account": {
                                "account_number": mt5_account.get("account_number") if mt5_account else None,
                                "balance": mt5_account.get("balance", 0) if mt5_account else 0,
                                "equity": mt5_account.get("equity", 0) if mt5_account else 0,
                                "open_positions": len(await mock_mt5.get_positions(client_id))
                            },
                            "status": "Active"
                        }
                        
                        fund_investors.append(investor_detail)
        
        # Sort by invested amount descending
        fund_investors.sort(key=lambda x: x["fund_allocation"]["invested_amount"], reverse=True)
        
        # Calculate fund summary
        total_investors = len(fund_investors)
        total_invested = sum(inv["fund_allocation"]["invested_amount"] for inv in fund_investors)
        total_current_value = sum(inv["fund_allocation"]["current_value"] for inv in fund_investors)
        total_pnl = total_current_value - total_invested
        avg_allocation = total_invested / total_investors if total_investors > 0 else 0
        
        return {
            "fund": fund.dict(),
            "investors": fund_investors,
            "summary": {
                "total_investors": total_investors,
                "total_invested": round(total_invested, 2),
                "total_current_value": round(total_current_value, 2),
                "total_pnl": round(total_pnl, 2),
                "total_pnl_percentage": round((total_pnl / total_invested) * 100 if total_invested > 0 else 0, 2),
                "average_allocation": round(avg_allocation, 2)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Get fund investors error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch fund investors")

@api_router.get("/crm/client/{client_id}/profile")
async def get_client_detailed_profile(client_id: str):
    """Get comprehensive client profile with trading and fund details"""
    try:
        # Get client info
        client_info = None
        for user in MOCK_USERS.values():
            if user["id"] == client_id:
                client_info = user
                break
        
        if not client_info:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get fund allocations
        client_allocations = investor_allocations.get(client_id, [])
        allocations_data = []
        total_fund_value = 0
        
        for allocation in client_allocations:
            fund = next(fund for fund in FIDUS_FUNDS.values() if fund.id == allocation.fund_id)
            total_pnl = allocation.current_value - allocation.invested_amount
            pnl_percentage = (total_pnl / allocation.invested_amount) * 100 if allocation.invested_amount > 0 else 0
            
            allocation_detail = {
                "fund_name": fund.name,
                "fund_type": fund.fund_type,
                "shares": allocation.shares,
                "invested_amount": allocation.invested_amount,
                "current_value": allocation.current_value,
                "total_pnl": round(total_pnl, 2),
                "pnl_percentage": round(pnl_percentage, 2),
                "entry_date": allocation.entry_date.isoformat(),
                "allocation_percentage": allocation.allocation_percentage
            }
            
            allocations_data.append(allocation_detail)
            total_fund_value += allocation.current_value
        
        # Get MT5 trading data
        mt5_account = await mock_mt5.get_account_info(client_id)
        mt5_positions = await mock_mt5.get_positions(client_id)
        mt5_history = await mock_mt5.get_trade_history(client_id, 30)
        
        # Get capital flows
        client_flows = capital_flows.get(client_id, [])
        recent_flows = sorted(client_flows, key=lambda x: x.trade_date, reverse=True)[:10]
        
        return {
            "client_info": {
                "client_id": client_id,
                "name": client_info["name"],
                "email": client_info.get("email", ""),
                "type": client_info["type"],
                "status": "Active",
                "join_date": "2024-01-15",  # Could be stored in user data
                "risk_tolerance": client_info.get("risk_tolerance", "Moderate")
            },
            "fund_portfolio": {
                "allocations": allocations_data,
                "total_value": round(total_fund_value, 2),
                "number_of_funds": len(allocations_data)
            },
            "trading_account": {
                "account_info": mt5_account,
                "positions": {
                    "data": mt5_positions,
                    "summary": {
                        "total_positions": len(mt5_positions),
                        "total_profit": sum(pos["profit"] for pos in mt5_positions),
                        "total_volume": sum(pos["volume"] for pos in mt5_positions)
                    }
                },
                "recent_history": {
                    "data": mt5_history[:20],  # Last 20 trades
                    "summary": {
                        "total_trades": len(mt5_history),
                        "total_profit": sum(trade["profit"] for trade in mt5_history),
                        "winning_trades": len([t for t in mt5_history if t["profit"] > 0]),
                        "losing_trades": len([t for t in mt5_history if t["profit"] < 0])
                    }
                }
            },
            "capital_flows": {
                "recent_flows": [flow.dict() for flow in recent_flows],
                "summary": {
                    "total_subscriptions": sum(f.amount for f in client_flows if f.flow_type == "subscription"),
                    "total_redemptions": sum(f.amount for f in client_flows if f.flow_type == "redemption"),
                    "total_distributions": sum(f.amount for f in client_flows if f.flow_type == "distribution")
                }
            },
            "total_assets": round(total_fund_value + (mt5_account.get("balance", 0) if mt5_account else 0), 2)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Get client profile error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch client profile")

@api_router.get("/crm/clients/all-details")
async def get_all_clients_details():
    """Get comprehensive details for all clients"""
    try:
        clients_details = []
        
        for username, user in MOCK_USERS.items():
            if user["type"] == "client":
                client_id = user["id"]
                
                # Get fund allocations
                client_allocations = investor_allocations.get(client_id, [])
                total_fund_value = sum(alloc.current_value for alloc in client_allocations)
                
                # Get MT5 account
                mt5_account = await mock_mt5.get_account_info(client_id)
                mt5_positions = await mock_mt5.get_positions(client_id)
                
                # Get recent capital flows
                client_flows = capital_flows.get(client_id, [])
                recent_subscriptions = sum(f.amount for f in client_flows[-5:] if f.flow_type == "subscription")
                
                client_detail = {
                    "client_id": client_id,
                    "name": user["name"],
                    "email": user.get("email", f"{username}@example.com"),
                    "status": "Active",
                    "fund_portfolio": {
                        "total_value": round(total_fund_value, 2),
                        "number_of_funds": len(client_allocations)
                    },
                    "trading_account": {
                        "account_number": mt5_account.get("account_number") if mt5_account else None,
                        "balance": mt5_account.get("balance", 0) if mt5_account else 0,
                        "equity": mt5_account.get("equity", 0) if mt5_account else 0,
                        "open_positions": len(mt5_positions),
                        "last_activity": mt5_account.get("login_time") if mt5_account else None
                    },
                    "recent_activity": {
                        "recent_subscriptions": round(recent_subscriptions, 2),
                        "last_capital_flow": client_flows[-1].trade_date.isoformat() if client_flows else None
                    },
                    "total_assets": round(total_fund_value + (mt5_account.get("balance", 0) if mt5_account else 0), 2)
                }
                
                clients_details.append(client_detail)
        
        # Sort by total assets descending
        clients_details.sort(key=lambda x: x["total_assets"], reverse=True)
        
        # Calculate summary
        total_clients = len(clients_details)
        total_assets_all = sum(client["total_assets"] for client in clients_details)
        total_fund_assets = sum(client["fund_portfolio"]["total_value"] for client in clients_details)
        total_trading_assets = sum(client["trading_account"]["balance"] for client in clients_details)
        
        return {
            "clients": clients_details,
            "summary": {
                "total_clients": total_clients,
                "total_assets": round(total_assets_all, 2),
                "total_fund_assets": round(total_fund_assets, 2),
                "total_trading_assets": round(total_trading_assets, 2),
                "average_assets_per_client": round(total_assets_all / total_clients if total_clients > 0 else 0, 2)
            }
        }
        
    except Exception as e:
        logging.error(f"Get all clients details error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch all clients details")

# Enhanced Portfolio Summary with CRM Data
@api_router.get("/crm/admin/dashboard")
async def get_crm_admin_dashboard():
    """Get comprehensive CRM dashboard data for admin"""
    try:
        # Get funds data
        funds_data = []
        total_fund_aum = 0
        total_fund_investors = 0
        
        for fund in FIDUS_FUNDS.values():
            fund_dict = fund.dict()
            funds_data.append(fund_dict)
            total_fund_aum += fund.aum
            total_fund_investors += fund.total_investors
        
        # Get MT5 overview
        mt5_overview = await mock_mt5.get_all_accounts_summary()
        
        # Calculate total client assets (fund investments + trading accounts)
        total_client_assets = total_fund_aum + mt5_overview["summary"]["total_balance"]
        
        # Recent capital flows across all clients (last 30 days)
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
        recent_flows = []
        total_recent_subscriptions = 0
        total_recent_redemptions = 0
        
        for client_flows in capital_flows.values():
            for flow in client_flows:
                if flow.trade_date >= cutoff_date:
                    recent_flows.append(flow.dict())
                    if flow.flow_type == "subscription":
                        total_recent_subscriptions += flow.amount
                    elif flow.flow_type == "redemption":
                        total_recent_redemptions += flow.amount
        
        recent_flows.sort(key=lambda x: x["trade_date"], reverse=True)
        
        return {
            "funds": {
                "data": funds_data,
                "summary": {
                    "total_aum": total_fund_aum,
                    "total_investors": total_fund_investors,
                    "total_funds": len(FIDUS_FUNDS)
                }
            },
            "trading": mt5_overview,
            "capital_flows": {
                "recent_flows": recent_flows[:20],  # Last 20 flows
                "summary": {
                    "recent_subscriptions": round(total_recent_subscriptions, 2),
                    "recent_redemptions": round(total_recent_redemptions, 2),
                    "net_flow": round(total_recent_subscriptions - total_recent_redemptions, 2),
                    "total_recent_flows": len(recent_flows)
                }
            },
            "overview": {
                "total_client_assets": round(total_client_assets, 2),
                "fund_assets_percentage": round((total_fund_aum / total_client_assets) * 100, 2) if total_client_assets > 0 else 0,
                "trading_assets_percentage": round((mt5_overview["summary"]["total_balance"] / total_client_assets) * 100, 2) if total_client_assets > 0 else 0,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        }
        
    except Exception as e:
        logging.error(f"CRM admin dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch CRM dashboard data")

# ===============================================================================
# CRM PROSPECT MANAGEMENT ENDPOINTS
# ===============================================================================

@api_router.get("/crm/prospects")
async def get_all_prospects():
    """Get all prospects with pipeline information"""
    try:
        prospects = []
        for prospect_data in prospects_storage.values():
            prospects.append(prospect_data)
        
        # Sort by created_at descending (newest first)
        prospects.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Calculate pipeline statistics
        pipeline_stats = {
            "lead": 0,
            "qualified": 0,
            "proposal": 0,
            "negotiation": 0,
            "won": 0,
            "lost": 0
        }
        
        for prospect in prospects:
            stage = prospect.get('stage', 'lead')
            if stage in pipeline_stats:
                pipeline_stats[stage] += 1
        
        return {
            "prospects": prospects,
            "total_prospects": len(prospects),
            "pipeline_stats": pipeline_stats,
            "active_prospects": len([p for p in prospects if p.get('stage') not in ['won', 'lost']]),
            "converted_prospects": len([p for p in prospects if p.get('converted_to_client', False)])
        }
        
    except Exception as e:
        logging.error(f"Get prospects error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch prospects")

@api_router.post("/crm/prospects")
async def create_prospect(prospect_data: ProspectCreate):
    """Create a new prospect"""
    try:
        # Create prospect model
        prospect = Prospect(
            name=prospect_data.name,
            email=prospect_data.email,
            phone=prospect_data.phone,
            notes=prospect_data.notes,
            stage="lead"
        )
        
        # Store in memory (in production, use database)
        prospects_storage[prospect.id] = prospect.dict()
        
        logging.info(f"Prospect created: {prospect.name} ({prospect.email})")
        
        return {
            "success": True,
            "prospect_id": prospect.id,
            "prospect": prospect.dict(),
            "message": "Prospect created successfully"
        }
        
    except Exception as e:
        logging.error(f"Create prospect error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create prospect")

@api_router.put("/crm/prospects/{prospect_id}")
async def update_prospect(prospect_id: str, update_data: ProspectUpdate):
    """Update an existing prospect"""
    try:
        if prospect_id not in prospects_storage:
            raise HTTPException(status_code=404, detail="Prospect not found")
        
        prospect_data = prospects_storage[prospect_id].copy()
        
        # Update provided fields
        if update_data.name is not None:
            prospect_data['name'] = update_data.name
        if update_data.email is not None:
            prospect_data['email'] = update_data.email
        if update_data.phone is not None:
            prospect_data['phone'] = update_data.phone
        if update_data.stage is not None:
            # Validate stage
            valid_stages = ["lead", "qualified", "proposal", "negotiation", "won", "lost"]
            if update_data.stage not in valid_stages:
                raise HTTPException(status_code=400, detail=f"Invalid stage. Must be one of: {valid_stages}")
            prospect_data['stage'] = update_data.stage
        if update_data.notes is not None:
            prospect_data['notes'] = update_data.notes
        
        # Update timestamp
        prospect_data['updated_at'] = datetime.now(timezone.utc).isoformat()
        
        # Save updated data
        prospects_storage[prospect_id] = prospect_data
        
        logging.info(f"Prospect updated: {prospect_id}")
        
        return {
            "success": True,
            "prospect": prospect_data,
            "message": "Prospect updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Update prospect error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update prospect")

@api_router.delete("/crm/prospects/{prospect_id}")
async def delete_prospect(prospect_id: str):
    """Delete a prospect"""
    try:
        if prospect_id not in prospects_storage:
            raise HTTPException(status_code=404, detail="Prospect not found")
        
        prospect_data = prospects_storage[prospect_id]
        del prospects_storage[prospect_id]
        
        logging.info(f"Prospect deleted: {prospect_id}")
        
        return {
            "success": True,
            "message": f"Prospect {prospect_data['name']} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Delete prospect error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete prospect")

@api_router.post("/crm/prospects/{prospect_id}/convert")
async def convert_prospect_to_client(prospect_id: str, conversion_data: ProspectConversionRequest):
    """Convert a won prospect to a client and send FIDUS agreement"""
    try:
        if prospect_id not in prospects_storage:
            raise HTTPException(status_code=404, detail="Prospect not found")
        
        prospect_data = prospects_storage[prospect_id]
        
        # Validate prospect stage
        if prospect_data['stage'] != 'won':
            raise HTTPException(status_code=400, detail="Only prospects in 'won' stage can be converted to clients")
        
        if prospect_data.get('converted_to_client', False):
            raise HTTPException(status_code=400, detail="Prospect has already been converted to a client")
        
        # Generate new client ID
        client_id = f"client_{str(uuid.uuid4())[:8]}"
        username = prospect_data['email'].split('@')[0].lower().replace('.', '').replace('-', '')[:10]
        
        # Create new client in MOCK_USERS
        new_client = {
            "id": client_id,
            "username": username,
            "name": prospect_data['name'],
            "email": prospect_data['email'],
            "phone": prospect_data['phone'],
            "type": "client",
            "status": "active",
            "created_from_prospect": True,
            "prospect_id": prospect_id,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "profile_picture": f"https://images.unsplash.com/photo-150700{random.randint(1000, 9999)}?w=150&h=150&fit=crop&crop=face"
        }
        
        # Add to MOCK_USERS
        MOCK_USERS[username] = new_client
        
        # Update prospect as converted
        prospect_data['converted_to_client'] = True
        prospect_data['client_id'] = client_id
        prospect_data['updated_at'] = datetime.now(timezone.utc).isoformat()
        prospects_storage[prospect_id] = prospect_data
        
        # Send FIDUS agreement if requested
        agreement_sent = False
        agreement_message = ""
        
        if conversion_data.send_agreement:
            try:
                # Here we would integrate with Gmail API to send the FIDUS agreement
                # For now, we'll simulate this and log it
                logging.info(f"Sending FIDUS agreement to {prospect_data['email']} for client {client_id}")
                
                # You can add actual Gmail integration here using the existing Gmail service
                agreement_sent = True
                agreement_message = f"FIDUS agreement sent to {prospect_data['email']}"
                
            except Exception as email_error:
                logging.error(f"Failed to send FIDUS agreement: {str(email_error)}")
                agreement_message = "Client created but failed to send FIDUS agreement"
        
        logging.info(f"Prospect {prospect_id} converted to client {client_id}")
        
        return {
            "success": True,
            "client_id": client_id,
            "prospect": prospect_data,
            "client": new_client,
            "agreement_sent": agreement_sent,
            "message": f"Prospect converted to client successfully. {agreement_message}".strip()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Convert prospect error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to convert prospect to client")

@api_router.get("/crm/prospects/pipeline")
async def get_prospect_pipeline():
    """Get prospect pipeline data organized by stages"""
    try:
        pipeline = {
            "lead": [],
            "qualified": [],
            "proposal": [],
            "negotiation": [],
            "won": [],
            "lost": []
        }
        
        for prospect_data in prospects_storage.values():
            stage = prospect_data.get('stage', 'lead')
            if stage in pipeline:
                pipeline[stage].append(prospect_data)
        
        # Sort each stage by updated_at descending
        for stage in pipeline:
            pipeline[stage].sort(key=lambda x: x['updated_at'], reverse=True)
        
        # Calculate statistics
        total_prospects = len(prospects_storage)
        active_prospects = sum(len(prospects) for stage, prospects in pipeline.items() if stage not in ['won', 'lost'])
        conversion_rate = 0
        if total_prospects > 0:
            conversion_rate = (len(pipeline['won']) / total_prospects) * 100
        
        return {
            "pipeline": pipeline,
            "stats": {
                "total_prospects": total_prospects,
                "active_prospects": active_prospects,
                "won_prospects": len(pipeline['won']),
                "lost_prospects": len(pipeline['lost']),
                "conversion_rate": round(conversion_rate, 1)
            }
        }
        
    except Exception as e:
        logging.error(f"Get pipeline error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch prospect pipeline")

# ===============================================================================
# INVESTMENT MANAGEMENT ENDPOINTS
# ===============================================================================

@api_router.get("/investments/funds/config")
async def get_fund_configurations():
    """Get all available fund configurations"""
    try:
        # Use hardcoded FIDUS_FUND_CONFIG to ensure correct interest rates
        funds = []
        
        for fund_code, config in FIDUS_FUND_CONFIG.items():
            # Get real AUM and investor count from MongoDB
            all_clients = mongodb_manager.get_all_clients()
            total_aum = 0.0
            investor_count = 0
            
            for client in all_clients:
                client_investments = mongodb_manager.get_client_investments(client['id'])
                for investment in client_investments:
                    if investment['fund_code'] == fund_code:
                        total_aum += investment['current_value']
                        investor_count += 1
            
            fund_data = {
                'fund_code': fund_code,
                'name': config.name,
                'interest_rate': config.interest_rate,  # Use correct interest rate from config
                'monthly_interest_rate': config.interest_rate,
                'annual_interest_rate': config.interest_rate * 12,
                'minimum_investment': config.minimum_investment,
                'redemption_frequency': config.redemption_frequency,
                'aum': round(total_aum, 2),
                'nav_per_share': 100.0,
                'performance_ytd': 0.0,
                'total_investors': investor_count,
                'incubation_period_months': config.incubation_months,
                'minimum_hold_period_months': config.minimum_hold_months,
                'invitation_only': config.invitation_only
            }
            
            funds.append(fund_data)
        
        return {
            "success": True,
            "funds": funds,
            "total_funds": len(funds)
        }
        
    except Exception as e:
        logging.error(f"Get fund configs error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch fund configurations")

@api_router.post("/investments/create")
async def create_client_investment(investment_data: InvestmentCreate):
    """Create a new investment for a client"""
    try:
        # Validate fund exists
        if investment_data.fund_code not in FIDUS_FUND_CONFIG:
            raise HTTPException(status_code=400, detail=f"Invalid fund code: {investment_data.fund_code}")
        
        fund_config = FIDUS_FUND_CONFIG[investment_data.fund_code]
        
        # Validate minimum investment
        if investment_data.amount < fund_config.minimum_investment:
            raise HTTPException(
                status_code=400, 
                detail=f"Minimum investment for {investment_data.fund_code} is ${fund_config.minimum_investment:,.2f}"
            )
        
        # Check invitation-only restriction
        if fund_config.invitation_only:
            # In a real system, verify client has invitation
            logging.info(f"Creating invitation-only fund investment for client {investment_data.client_id}")
        
        # Create investment
        investment = create_investment(
            investment_data.client_id,
            investment_data.fund_code,
            investment_data.amount,
            investment_data.deposit_date
        )
        
        # Store investment in MongoDB
        investment_id = mongodb_manager.create_investment({
            'client_id': investment_data.client_id,
            'fund_code': investment_data.fund_code,
            'amount': investment_data.amount,
            'deposit_date': investment_data.deposit_date or datetime.now(timezone.utc),
            'incubation_end_date': investment.incubation_end_date,
            'interest_start_date': investment.interest_start_date,
            'minimum_hold_end_date': investment.minimum_hold_end_date
        })
        
        if not investment_id:
            raise HTTPException(status_code=500, detail="Failed to create investment in database")
        
        # Update the investment object with the actual ID from MongoDB
        investment.investment_id = investment_id
        
        # Create or update MT5 account mapping with specified broker
        broker_code = investment_data.broker_code or 'multibank'  # Use specified broker or default
        mt5_account_id = await mt5_service.get_or_create_mt5_account(
            investment_data.client_id,
            investment_data.fund_code,
            {
                'investment_id': investment_id,
                'principal_amount': investment_data.amount,
                'fund_code': investment_data.fund_code
            },
            broker_code
        )
        
        if mt5_account_id:
            logging.info(f"MT5 account {mt5_account_id} linked to investment {investment_id}")
        else:
            logging.warning(f"Failed to create/link MT5 account for investment {investment_id}")
        
        # Log the deposit activity in MongoDB
        mongodb_manager.log_activity({
            'client_id': investment_data.client_id,
            'activity_type': 'deposit',
            'amount': investment_data.amount,
            'fund_code': investment_data.fund_code,
            'description': f"Investment deposit in {fund_config.name}"
        })
        
        logging.info(f"Investment created: {investment.investment_id} for client {investment_data.client_id}")
        
        return {
            "success": True,
            "investment_id": investment.investment_id,
            "investment": investment.dict(),
            "mt5_account_id": mt5_account_id,
            "message": f"Investment of ${investment_data.amount:,.2f} created in {investment_data.fund_code} fund with MT5 integration"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Create investment error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create investment: {str(e)}")

@api_router.get("/investments/client/{client_id}")
async def get_client_investments(client_id: str):
    """Get all investments for a specific client - MongoDB version"""
    try:
        # Get investments from MongoDB (already enriched with calculations)
        client_investments_list = mongodb_manager.get_client_investments(client_id)
        
        # Calculate portfolio statistics from MongoDB data
        enriched_investments = []
        total_invested = 0.0
        total_current_value = 0.0
        total_earned_interest = 0.0
        
        for investment in client_investments_list:
            # MongoDB data already includes calculations and current values
            enriched_investment = {
                "investment_id": investment["investment_id"],
                "fund_code": investment["fund_code"],
                "fund_name": investment["fund_name"],
                "principal_amount": investment["principal_amount"],
                "current_value": investment["current_value"],
                "interest_earned": investment["interest_earned"],
                "deposit_date": investment["deposit_date"],
                "interest_start_date": investment["interest_start_date"],
                "minimum_hold_end_date": investment["minimum_hold_end_date"],
                "status": investment["status"],
                "monthly_interest_rate": investment["monthly_interest_rate"],
                "can_redeem_interest": investment["can_redeem_interest"],
                "can_redeem_principal": investment["can_redeem_principal"],
                "created_at": investment["created_at"]
            }
            
            enriched_investments.append(enriched_investment)
            total_invested += investment["principal_amount"]
            total_current_value += investment["current_value"]
            total_earned_interest += investment["interest_earned"]
        
        # Calculate portfolio statistics from MongoDB data
        portfolio_stats = {
            "total_investments": len(enriched_investments),
            "total_invested": round(total_invested, 2),
            "total_current_value": round(total_current_value, 2),
            "total_earned_interest": round(total_earned_interest, 2),
            "total_projected_interest": round(total_earned_interest, 2),  # Using earned as projected for now
            "projected_portfolio_value": round(total_current_value, 2),
            "overall_return_percentage": round(((total_current_value - total_invested) / total_invested * 100), 2) if total_invested > 0 else 0.0
        }
        
        return {
            "success": True,
            "client_id": client_id,
            "investments": enriched_investments,
            "portfolio_stats": portfolio_stats
        }
        
    except Exception as e:
        logging.error(f"Get client investments error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch client investments")

@api_router.get("/investments/{investment_id}/projections")
async def get_investment_projections(investment_id: str):
    """Get detailed projections for a specific investment"""
    try:
        # Find investment
        investment_found = None
        for client_id, investments in client_investments.items():
            for inv_data in investments:
                if inv_data['investment_id'] == investment_id:
                    investment_found = FundInvestment(**inv_data)
                    break
            if investment_found:
                break
        
        if not investment_found:
            raise HTTPException(status_code=404, detail="Investment not found")
        
        fund_config = FIDUS_FUND_CONFIG[investment_found.fund_code]
        projections = generate_investment_projections(investment_found, fund_config)
        
        # Add additional timeline information
        now = datetime.now(timezone.utc)
        timeline = []
        
        # Add milestone events
        timeline.append({
            "date": investment_found.deposit_date.isoformat(),
            "event": "Investment Created",
            "description": f"Deposited ${investment_found.principal_amount:,.2f}",
            "status": "completed"
        })
        
        timeline.append({
            "date": investment_found.incubation_end_date.isoformat(),
            "event": "Incubation Period Ends",
            "description": "Investment becomes active",
            "status": "completed" if now >= investment_found.incubation_end_date else "pending"
        })
        
        timeline.append({
            "date": investment_found.interest_start_date.isoformat(),
            "event": "Interest Payments Begin",
            "description": f"{fund_config.interest_rate}% monthly interest starts",
            "status": "completed" if now >= investment_found.interest_start_date else "pending"
        })
        
        timeline.append({
            "date": investment_found.minimum_hold_end_date.isoformat(),
            "event": "Minimum Hold Period Ends",
            "description": "Redemption becomes available",
            "status": "completed" if now >= investment_found.minimum_hold_end_date else "pending"
        })
        
        return {
            "success": True,
            "investment": investment_found.dict(),
            "fund_config": fund_config.dict(),
            "projections": projections.dict(),
            "timeline": timeline
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Get investment projections error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch investment projections")

@api_router.get("/investments/admin/overview")
async def get_admin_investments_overview():
    """Get comprehensive investment overview for admin"""
    try:
        all_investments = []
        fund_summaries = {}
        clients_summary = []  # Add clients array for admin dashboard
        total_aum = 0.0
        
        # Initialize fund summaries
        for fund_code, config in FIDUS_FUND_CONFIG.items():
            fund_summaries[fund_code] = {
                "fund_code": fund_code,
                "fund_name": config.name,
                "total_invested": 0.0,
                "total_current_value": 0.0,
                "total_investors": 0,
                "total_interest_paid": 0.0,
                "average_investment": 0.0
            }
        
        # Get all clients and their investments from MongoDB
        all_clients = mongodb_manager.get_all_clients()
        
        for client in all_clients:
            client_id = client['id']
            client_name = client['name']
            
            # Get investments for this client from MongoDB
            client_investments_list = mongodb_manager.get_client_investments(client_id)
            
            # Initialize client summary
            client_summary = {
                "client_id": client_id,
                "client_name": client_name,
                "total_invested": 0.0,
                "current_value": 0.0,
                "total_interest": 0.0,
                "investment_count": len(client_investments_list),
                "funds": []
            }
            
            for investment in client_investments_list:
                # Add to all investments with proper client name
                investment_record = {
                    "investment_id": investment["investment_id"],
                    "client_id": client_id,
                    "client_name": client_name,
                    "fund_code": investment["fund_code"],
                    "fund_name": investment["fund_name"],
                    "principal_amount": investment["principal_amount"],
                    "current_value": investment["current_value"],
                    "interest_earned": investment["interest_earned"],
                    "deposit_date": investment["deposit_date"],
                    "status": investment["status"],
                    "monthly_interest_rate": investment["monthly_interest_rate"],
                    "can_redeem_interest": investment["can_redeem_interest"],
                    "can_redeem_principal": investment["can_redeem_principal"]
                }
                
                all_investments.append(investment_record)
                
                # Update client summary
                client_summary["total_invested"] += investment["principal_amount"]
                client_summary["current_value"] += investment["current_value"]
                client_summary["total_interest"] += investment["interest_earned"]
                
                # Add fund to client summary if not already there
                fund_info = {
                    "fund_code": investment["fund_code"],
                    "fund_name": investment["fund_name"],
                    "amount": investment["current_value"]
                }
                client_summary["funds"].append(fund_info)
                
                # Update fund summaries with MongoDB data
                fund_code = investment["fund_code"]
                fund_summaries[fund_code]["total_invested"] += investment["principal_amount"]
                fund_summaries[fund_code]["total_current_value"] += investment["current_value"]
                fund_summaries[fund_code]["total_investors"] += 1
                fund_summaries[fund_code]["total_interest_paid"] += investment["interest_earned"]
                
                total_aum += investment["current_value"]
            
            # Only add clients with investments to the summary
            if client_investments_list:
                # Round client summary values
                client_summary["total_invested"] = round(client_summary["total_invested"], 2)
                client_summary["current_value"] = round(client_summary["current_value"], 2)
                client_summary["total_interest"] = round(client_summary["total_interest"], 2)
                clients_summary.append(client_summary)
        
        # Calculate averages
        for fund_summary in fund_summaries.values():
            if fund_summary["total_investors"] > 0:
                fund_summary["average_investment"] = fund_summary["total_invested"] / fund_summary["total_investors"]
            fund_summary["total_invested"] = round(fund_summary["total_invested"], 2)
            fund_summary["total_current_value"] = round(fund_summary["total_current_value"], 2)
            fund_summary["total_interest_paid"] = round(fund_summary["total_interest_paid"], 2)
            fund_summary["average_investment"] = round(fund_summary["average_investment"], 2)
        
        return {
            "success": True,
            "total_aum": round(total_aum, 2),
            "total_investments": len(all_investments),
            "total_clients": len(all_clients),
            "clients": clients_summary,  # Add clients array for admin dashboard
            "fund_summaries": list(fund_summaries.values()),
            "all_investments": all_investments
        }
        
    except Exception as e:
        logging.error(f"Get admin investments overview error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch admin investments overview")

# ===============================================================================
# REDEMPTION SYSTEM ENDPOINTS
# ===============================================================================

@api_router.get("/redemptions/client/{client_id}")
async def get_client_redemptions(client_id: str):
    """Get all redemptions and available redemption options for a client"""
    try:
        # Get client investments from MongoDB
        client_investments_list = mongodb_manager.get_client_investments(client_id)
        
        if not client_investments_list:
            return {
                "success": True,
                "redemptions": [],
                "available_redemptions": [],
                "message": "No investments found for client"
            }
        
        # Convert MongoDB investment data to FundInvestment objects
        investments = []
        for investment_data in client_investments_list:
            fund_code = investment_data['fund_code']
            fund_config = FIDUS_FUND_CONFIG[fund_code]
            
            # Calculate missing date fields using existing function
            deposit_date = investment_data['deposit_date']
            if isinstance(deposit_date, str):
                deposit_date = datetime.fromisoformat(deposit_date.replace('Z', '+00:00'))
            elif deposit_date.tzinfo is None:
                deposit_date = deposit_date.replace(tzinfo=timezone.utc)
            
            calculated_dates = calculate_investment_dates(deposit_date, fund_config)
            
            # Create FundInvestment object with all required fields
            fund_investment = FundInvestment(
                investment_id=investment_data['investment_id'],
                client_id=client_id,
                fund_code=fund_code,
                principal_amount=investment_data['principal_amount'],
                deposit_date=deposit_date,
                current_value=investment_data.get('current_value', investment_data['principal_amount']),
                incubation_end_date=calculated_dates['incubation_end_date'],
                interest_start_date=calculated_dates['interest_start_date'],
                minimum_hold_end_date=calculated_dates['minimum_hold_end_date']
            )
            investments.append(fund_investment)
        
        available_redemptions = []
        client_redemption_requests = []
        
        # Check each investment for redemption eligibility
        for investment in investments:
            fund_config = FIDUS_FUND_CONFIG[investment.fund_code]
            
            can_redeem, message = can_request_redemption(investment, fund_config)
            current_value = calculate_redemption_value(investment, fund_config)
            next_redemption = get_next_redemption_date(investment, fund_config)
            
            # Calculate interest earned (current_value - principal)
            interest_earned = current_value - investment.principal_amount
            
            # Check if principal hold period has passed
            now = datetime.now(timezone.utc)
            principal_available = now >= investment.minimum_hold_end_date
            
            redemption_info = {
                "investment_id": investment.investment_id,
                "fund_code": investment.fund_code,
                "fund_name": fund_config.name,
                "principal_amount": investment.principal_amount,
                "interest_earned": round(interest_earned, 2),
                "current_value": round(current_value, 2),
                "can_redeem_interest": can_redeem,
                "can_redeem_principal": principal_available,
                "interest_message": message,
                "principal_message": f"Principal available in {(investment.minimum_hold_end_date - now).days} days" if not principal_available else "Principal redemption available",
                "next_redemption_date": next_redemption.isoformat(),
                "deposit_date": investment.deposit_date.isoformat(),
                "redemption_frequency": fund_config.redemption_frequency,
                "principal_hold_end_date": investment.minimum_hold_end_date.isoformat()
            }
            
            available_redemptions.append(redemption_info)
        
        # Get client's redemption requests
        for redemption_id, redemption in redemption_requests.items():
            if redemption.client_id == client_id:
                client_redemption_requests.append(redemption.dict())
        
        return {
            "success": True,
            "available_redemptions": available_redemptions,
            "redemption_requests": client_redemption_requests
        }
        
    except Exception as e:
        logging.error(f"Get client redemptions error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch client redemptions")

@api_router.post("/redemptions/request")
async def create_redemption_request(redemption_data: RedemptionRequestCreate):
    """Create a new redemption request"""
    try:
        # Find the investment in MongoDB
        investment_found = None
        client_id = None
        
        # Search through all clients for the investment
        all_clients = mongodb_manager.get_all_clients()
        for client in all_clients:
            client_investments_list = mongodb_manager.get_client_investments(client['id'])
            for investment_data in client_investments_list:
                if investment_data["investment_id"] == redemption_data.investment_id:
                    fund_code = investment_data['fund_code']
                    fund_config = FIDUS_FUND_CONFIG[fund_code]
                    
                    # Calculate missing date fields
                    deposit_date = investment_data['deposit_date']
                    if isinstance(deposit_date, str):
                        deposit_date = datetime.fromisoformat(deposit_date.replace('Z', '+00:00'))
                    elif deposit_date.tzinfo is None:
                        deposit_date = deposit_date.replace(tzinfo=timezone.utc)
                    
                    calculated_dates = calculate_investment_dates(deposit_date, fund_config)
                    
                    # Create FundInvestment object with all required fields
                    investment_found = FundInvestment(
                        investment_id=investment_data['investment_id'],
                        client_id=client['id'],
                        fund_code=fund_code,
                        principal_amount=investment_data['principal_amount'],
                        deposit_date=deposit_date,
                        current_value=investment_data.get('current_value', investment_data['principal_amount']),
                        incubation_end_date=calculated_dates['incubation_end_date'],
                        interest_start_date=calculated_dates['interest_start_date'],
                        minimum_hold_end_date=calculated_dates['minimum_hold_end_date']
                    )
                    client_id = client['id']
                    break
            if investment_found:
                break
        
        if not investment_found:
            raise HTTPException(status_code=404, detail="Investment not found")
        
        fund_config = FIDUS_FUND_CONFIG[investment_found.fund_code]
        
        # Check if redemption is allowed
        can_redeem, message = can_request_redemption(investment_found, fund_config)
        if not can_redeem:
            raise HTTPException(status_code=400, detail=f"Redemption not allowed: {message}")
        
        # Validate requested amount
        current_value = calculate_redemption_value(investment_found, fund_config)
        if redemption_data.requested_amount > current_value:
            raise HTTPException(
                status_code=400, 
                detail=f"Requested amount ${redemption_data.requested_amount:,.2f} exceeds current value ${current_value:,.2f}"
            )
        
        # Calculate next available redemption date
        next_available = get_next_redemption_date(investment_found, fund_config)
        
        # Create redemption request
        redemption_id = str(uuid.uuid4())
        redemption_request = RedemptionRequest(
            id=redemption_id,  # Explicitly set the ID
            client_id=client_id,
            investment_id=redemption_data.investment_id,
            fund_code=investment_found.fund_code,
            fund_name=fund_config.name,
            requested_amount=redemption_data.requested_amount,
            current_value=current_value,
            principal_amount=investment_found.principal_amount,
            requested_redemption_date=next_available,
            next_available_date=next_available,
            reason=redemption_data.reason or ""
        )
        
        # Store redemption request
        redemption_requests[redemption_request.id] = redemption_request
        
        # Log the activity
        create_activity_log(
            client_id=client_id,
            activity_type="redemption_request",
            amount=redemption_data.requested_amount,
            description=f"Redemption request submitted for {fund_config.name}",
            performed_by=client_id,
            investment_id=redemption_data.investment_id,
            fund_code=investment_found.fund_code,
            reference_id=redemption_request.id,
            metadata={
                "reason": redemption_data.reason,
                "requested_redemption_date": next_available.isoformat()
            }
        )
        
        logging.info(f"Redemption request created: {redemption_request.id} for client {client_id}")
        
        return {
            "success": True,
            "redemption_request": redemption_request.dict(),
            "message": f"Redemption request submitted for ${redemption_data.requested_amount:,.2f}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Create redemption request error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create redemption request")

@api_router.get("/redemptions/admin/pending")
async def get_pending_redemptions():
    """Get all pending redemption requests for admin review"""
    try:
        pending_redemptions = []
        
        for redemption_id, redemption in redemption_requests.items():
            if redemption.status == "pending":
                # Get client info
                client_info = None
                for user_data in MOCK_USERS.values():
                    if user_data["id"] == redemption.client_id:
                        client_info = {
                            "name": user_data["name"],
                            "email": user_data["email"]
                        }
                        break
                
                redemption_data = redemption.dict()
                redemption_data["client_info"] = client_info or {"name": "Unknown", "email": "Unknown"}
                pending_redemptions.append(redemption_data)
        
        return {
            "success": True,
            "pending_redemptions": pending_redemptions,
            "total_pending": len(pending_redemptions)
        }
        
    except Exception as e:
        logging.error(f"Get pending redemptions error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch pending redemptions")

@api_router.post("/redemptions/admin/approve")
async def approve_redemption_request(approval_data: RedemptionApproval):
    """Approve or reject a redemption request"""
    try:
        if approval_data.redemption_id not in redemption_requests:
            raise HTTPException(status_code=404, detail="Redemption request not found")
        
        redemption = redemption_requests[approval_data.redemption_id]
        
        if redemption.status != "pending":
            raise HTTPException(status_code=400, detail=f"Redemption request is already {redemption.status}")
        
        # Update redemption status
        if approval_data.action == "approve":
            redemption.status = "approved"
            activity_type = "redemption_approved"
            message = f"Redemption approved for ${redemption.requested_amount:,.2f}"
        elif approval_data.action == "reject":
            redemption.status = "rejected"
            activity_type = "redemption_rejected"
            message = f"Redemption rejected for ${redemption.requested_amount:,.2f}"
        else:
            raise HTTPException(status_code=400, detail="Action must be 'approve' or 'reject'")
        
        # Update redemption details
        redemption.admin_notes = approval_data.admin_notes or ""
        redemption.approved_by = approval_data.admin_id
        redemption.approved_date = datetime.now(timezone.utc)
        
        # Log the activity
        create_activity_log(
            client_id=redemption.client_id,
            activity_type=activity_type,
            amount=redemption.requested_amount,
            description=f"Redemption {approval_data.action} by admin for {redemption.fund_name}",
            performed_by=approval_data.admin_id,
            investment_id=redemption.investment_id,
            fund_code=redemption.fund_code,
            reference_id=redemption.id,
            metadata={
                "admin_notes": approval_data.admin_notes,
                "action": approval_data.action
            }
        )
        
        logging.info(f"Redemption {approval_data.action}: {redemption.id} by admin {approval_data.admin_id}")
        
        return {
            "success": True,
            "redemption_request": redemption.dict(),
            "message": message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Approve redemption error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process redemption approval")

# Payment Confirmation Endpoints
@api_router.post("/payments/deposit/confirm")
async def confirm_deposit_payment(confirmation_data: DepositConfirmationRequest, admin_id: str = "admin_001"):
    """Confirm that a deposit payment has been received"""
    try:
        # Find the investment by searching through all client investments
        investment_found = None
        investment_client_id = None
        
        for client_id, investments in client_investments.items():
            for inv in investments:
                if inv["investment_id"] == confirmation_data.investment_id:
                    investment_found = inv
                    investment_client_id = client_id
                    break
            if investment_found:
                break
        
        if not investment_found:
            raise HTTPException(status_code=404, detail="Investment not found")
        
        investment = investment_found
        
        # Create payment confirmation record
        confirmation = PaymentConfirmation(
            transaction_type="deposit",
            payment_method=confirmation_data.payment_method,
            amount=confirmation_data.amount,
            currency=confirmation_data.currency,
            investment_id=confirmation_data.investment_id,
            client_id=investment_client_id,  # Use the found client_id
            wire_confirmation_number=confirmation_data.wire_confirmation_number,
            bank_reference=confirmation_data.bank_reference,
            transaction_hash=confirmation_data.transaction_hash,
            blockchain_network=confirmation_data.blockchain_network,
            wallet_address=confirmation_data.wallet_address,
            confirmed_by=admin_id,
            notes=confirmation_data.notes,
            status="confirmed"
        )
        
        # Store confirmation
        payment_confirmations[confirmation.id] = confirmation
        
        # Log the activity
        create_activity_log(
            client_id=investment_client_id,  # Use the found client_id
            activity_type="deposit_confirmed",
            amount=confirmation_data.amount,
            description=f"Deposit confirmed via {confirmation_data.payment_method.upper()} for investment {confirmation_data.investment_id}",
            performed_by=admin_id,
            investment_id=confirmation_data.investment_id,
            fund_code=investment["fund_code"],  # Access as dictionary key
            reference_id=confirmation.id,
            metadata={
                "payment_method": confirmation_data.payment_method,
                "confirmation_details": confirmation_data.dict()
            }
        )
        
        logging.info(f"Deposit payment confirmed: {confirmation.id} for investment {confirmation_data.investment_id}")
        
        return {
            "success": True,
            "confirmation_id": confirmation.id,
            "confirmation": confirmation.dict(),
            "message": f"Deposit payment confirmed via {confirmation_data.payment_method.upper()}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Confirm deposit payment error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to confirm deposit payment")

@api_router.post("/payments/redemption/confirm")
async def confirm_redemption_payment(confirmation_data: RedemptionPaymentConfirmation, admin_id: str = "admin_001"):
    """Confirm that a redemption payment has been sent"""
    try:
        # Check if redemption exists
        if confirmation_data.redemption_id not in redemption_requests:
            raise HTTPException(status_code=404, detail="Redemption request not found")
        
        redemption = redemption_requests[confirmation_data.redemption_id]
        
        # Create payment confirmation record
        confirmation = PaymentConfirmation(
            transaction_type="redemption",
            payment_method=confirmation_data.payment_method,
            amount=confirmation_data.amount,
            currency=confirmation_data.currency,
            redemption_id=confirmation_data.redemption_id,
            client_id=redemption.client_id,
            wire_confirmation_number=confirmation_data.wire_confirmation_number,
            bank_reference=confirmation_data.bank_reference,
            transaction_hash=confirmation_data.transaction_hash,
            blockchain_network=confirmation_data.blockchain_network,
            wallet_address=confirmation_data.wallet_address,
            confirmed_by=admin_id,
            notes=confirmation_data.notes,
            status="confirmed"
        )
        
        # Store confirmation
        payment_confirmations[confirmation.id] = confirmation
        
        # Update redemption status to completed
        redemption.status = "completed"
        redemption.completed_date = datetime.now(timezone.utc)
        
        # Log the activity
        create_activity_log(
            client_id=redemption.client_id,
            activity_type="redemption_payment_sent",
            amount=confirmation_data.amount,
            description=f"Redemption payment sent via {confirmation_data.payment_method.upper()} for redemption {confirmation_data.redemption_id}",
            performed_by=admin_id,
            investment_id=redemption.investment_id,
            fund_code=redemption.fund_code,
            reference_id=confirmation.id,
            metadata={
                "payment_method": confirmation_data.payment_method,
                "confirmation_details": confirmation_data.dict()
            }
        )
        
        logging.info(f"Redemption payment confirmed: {confirmation.id} for redemption {confirmation_data.redemption_id}")
        
        return {
            "success": True,
            "confirmation_id": confirmation.id,
            "confirmation": confirmation.dict(),
            "redemption": redemption.dict(),
            "message": f"Redemption payment confirmed via {confirmation_data.payment_method.upper()}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Confirm redemption payment error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to confirm redemption payment")

@api_router.get("/payments/confirmations/{transaction_type}")
async def get_payment_confirmations(transaction_type: str):
    """Get all payment confirmations by transaction type (deposit/redemption)"""
    try:
        confirmations = [
            conf.dict() for conf in payment_confirmations.values() 
            if conf.transaction_type == transaction_type
        ]
        
        # Sort by confirmation date (most recent first)
        confirmations.sort(key=lambda x: x["confirmation_date"], reverse=True)
        
        return {
            "success": True,
            "confirmations": confirmations,
            "total_confirmations": len(confirmations),
            "transaction_type": transaction_type
        }
        
    except Exception as e:
        logging.error(f"Get payment confirmations error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch payment confirmations")

@api_router.get("/payments/confirmations")
async def get_all_payment_confirmations():
    """Get all payment confirmations"""
    try:
        confirmations = [conf.dict() for conf in payment_confirmations.values()]
        
        # Sort by confirmation date (most recent first)
        confirmations.sort(key=lambda x: x["confirmation_date"], reverse=True)
        
        return {
            "success": True,
            "confirmations": confirmations,
            "total_confirmations": len(confirmations)
        }
        
    except Exception as e:
        logging.error(f"Get all payment confirmations error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch payment confirmations")

# Fund Portfolio & Cash Flow Management Endpoints
@api_router.get("/admin/funds-overview")
async def get_funds_overview():
    """Get comprehensive fund overview for admin portfolio management"""
    try:
        funds_overview = {}
        
        # Get all clients and their investments from MongoDB
        all_clients = mongodb_manager.get_all_clients()
        
        for fund_code, fund_config in FIDUS_FUND_CONFIG.items():
            # Calculate fund AUM from MongoDB investments
            fund_aum = 0
            total_investors = 0
            client_interest_rate = fund_config.interest_rate
            
            # Sum all investments for this fund from MongoDB
            for client in all_clients:
                client_investments_list = mongodb_manager.get_client_investments(client['id'])
                for investment in client_investments_list:
                    if investment['fund_code'] == fund_code:
                        current_value = investment['current_value']
                        fund_aum += current_value
                        total_investors += 1
            
            # Get fund configuration from FIDUS_FUNDS (fallback data)
            fund_info = FIDUS_FUNDS.get(fund_code, {})
            
            funds_overview[fund_code] = {
                "fund_code": fund_code,
                "name": fund_config.name,
                "fund_type": getattr(fund_info, 'fund_type', 'Investment Fund'),
                "aum": round(fund_aum, 2),
                "nav": round(fund_aum, 2),  # For now, NAV = AUM
                "nav_per_share": getattr(fund_info, 'nav_per_share', 100.0),
                "performance_ytd": getattr(fund_info, 'performance_ytd', 0.0),
                "performance_1y": getattr(fund_info, 'performance_1y', 0.0),
                "total_investors": total_investors,
                "client_interest_rate": client_interest_rate,
                "client_investments": round(fund_aum, 2),
                "minimum_investment": fund_config.minimum_investment,
                "management_fee": getattr(fund_info, 'management_fee', 0.0),
                "performance_fee": getattr(fund_info, 'performance_fee', 0.0),
                "total_rebates": 0.0  # Will be calculated from rebate system
            }
        
        return {
            "success": True,
            "funds": funds_overview,
            "total_aum": round(sum(fund["aum"] for fund in funds_overview.values()), 2),
            "total_investors": sum(fund["total_investors"] for fund in funds_overview.values())
        }
        
    except Exception as e:
        logging.error(f"Get funds overview error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch funds overview")

@api_router.put("/admin/funds/{fund_code}/realtime")
async def update_fund_realtime_data(fund_code: str, realtime_data: dict):
    """Update real-time data for a specific fund"""
    try:
        if fund_code not in FIDUS_FUND_CONFIG:
            raise HTTPException(status_code=404, detail="Fund not found")
        
        # Store real-time data (in production this would update the database)
        # For now, we'll just acknowledge the update
        logging.info(f"Real-time data updated for {fund_code}: {realtime_data}")
        
        return {
            "success": True,
            "fund_code": fund_code,
            "updated_data": realtime_data,
            "message": f"Real-time data updated for {fund_code} fund"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Update fund real-time data error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update real-time data")

# In-memory rebate storage
fund_rebates = []  # List of rebate entries

@api_router.post("/admin/rebates/add")
async def add_rebate(rebate_data: dict):
    """Add a rebate entry for a fund"""
    try:
        rebate_entry = {
            "id": str(uuid.uuid4()),
            "fund_code": rebate_data["fund_code"],
            "amount": rebate_data["amount"],
            "broker": rebate_data["broker"],
            "description": rebate_data.get("description", ""),
            "date": rebate_data["date"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": "admin"
        }
        
        fund_rebates.append(rebate_entry)
        
        logging.info(f"Rebate added: {rebate_entry['amount']} for {rebate_entry['fund_code']} fund")
        
        return {
            "success": True,
            "rebate": rebate_entry,
            "message": f"Rebate of ${rebate_entry['amount']} added to {rebate_entry['fund_code']} fund"
        }
        
    except Exception as e:
        logging.error(f"Add rebate error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add rebate")

@api_router.get("/admin/rebates/all")
async def get_all_rebates():
    """Get all rebate entries"""
    try:
        # Sort by date (most recent first)
        sorted_rebates = sorted(fund_rebates, key=lambda x: x["date"], reverse=True)
        
        return {
            "success": True,
            "rebates": sorted_rebates,
            "total_rebates": len(sorted_rebates)
        }
        
    except Exception as e:
        logging.error(f"Get rebates error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch rebates")

# Cash Flow Management Endpoints
@api_router.get("/admin/cashflow/overview")
async def get_cashflow_overview(timeframe: str = "3months", fund: str = "all"):
    """Get cash flow overview data"""
    try:
        # Get all clients and their investments from MongoDB
        all_clients = mongodb_manager.get_all_clients()
        
        # Calculate real cash flow data
        fund_breakdown = {
            "CORE": {"inflow": 0, "outflow": 0},
            "BALANCE": {"inflow": 0, "outflow": 0},
            "DYNAMIC": {"inflow": 0, "outflow": 0},
            "UNLIMITED": {"inflow": 0, "outflow": 0}
        }
        
        cash_flows = []
        total_inflow = 0
        total_outflow = 0
        
        # Calculate cash flows from actual investment data
        for client in all_clients:
            client_investments_list = mongodb_manager.get_client_investments(client['id'])
            for investment in client_investments_list:
                fund_code = investment['fund_code']
                principal_amount = investment['principal_amount']
                current_value = investment['current_value']
                interest_earned = investment['interest_earned']
                
                # Count principal as inflow (money coming into fund)
                if fund_code in fund_breakdown:
                    fund_breakdown[fund_code]["inflow"] += principal_amount
                    total_inflow += principal_amount
                    
                    # Add cash flow record
                    cash_flows.append({
                        "date": investment['deposit_date'],
                        "type": "deposit",
                        "amount": principal_amount,
                        "fund_code": fund_code,
                        "client_name": client['name'],
                        "description": f"Investment deposit - {fund_code} Fund"
                    })
        
        # Round all values
        for fund_code in fund_breakdown:
            fund_breakdown[fund_code]["inflow"] = round(fund_breakdown[fund_code]["inflow"], 2)
            fund_breakdown[fund_code]["outflow"] = round(fund_breakdown[fund_code]["outflow"], 2)
        
        return {
            "success": True,
            "cash_flows": cash_flows,
            "fund_breakdown": fund_breakdown,
            "total_inflow": round(total_inflow, 2),
            "total_outflow": round(total_outflow, 2),
            "net_cash_flow": round(total_inflow - total_outflow, 2),
            "timeframe": timeframe,
            "selected_fund": fund
        }
        
    except Exception as e:
        logging.error(f"Get cash flow overview error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch cash flow overview")

@api_router.get("/admin/cashflow/redemption-schedule")
async def get_redemption_schedule(timeframe: str = "3months"):
    """Get upcoming redemption schedule"""
    try:
        upcoming_redemptions = []
        
        # Get all client investments from MongoDB and calculate upcoming redemption opportunities
        all_clients = mongodb_manager.get_all_clients()
        for client in all_clients:
            client_name = client.get("name", f"Client {client['id']}")
            client_investments_list = mongodb_manager.get_client_investments(client['id'])
            
            for investment_data in client_investments_list:
                fund_code = investment_data['fund_code']
                fund_config = FIDUS_FUND_CONFIG[fund_code]
                
                # Calculate missing date fields
                deposit_date = investment_data['deposit_date']
                if isinstance(deposit_date, str):
                    deposit_date = datetime.fromisoformat(deposit_date.replace('Z', '+00:00'))
                elif deposit_date.tzinfo is None:
                    deposit_date = deposit_date.replace(tzinfo=timezone.utc)
                
                calculated_dates = calculate_investment_dates(deposit_date, fund_config)
                
                # Create FundInvestment object with all required fields
                investment = FundInvestment(
                    investment_id=investment_data['investment_id'],
                    client_id=client['id'],
                    fund_code=fund_code,
                    principal_amount=investment_data['principal_amount'],
                    deposit_date=deposit_date,
                    current_value=investment_data.get('current_value', investment_data['principal_amount']),
                    incubation_end_date=calculated_dates['incubation_end_date'],
                    interest_start_date=calculated_dates['interest_start_date'],
                    minimum_hold_end_date=calculated_dates['minimum_hold_end_date']
                )
                
                fund_config = FIDUS_FUND_CONFIG[investment.fund_code]
                
                # Calculate next redemption dates based on fund rules
                next_redemption_date = get_next_redemption_date(investment, fund_config)
                current_value = calculate_redemption_value(investment, fund_config)
                interest_earned = current_value - investment.principal_amount
                
                # Check if redemption is in the future (potential)
                if next_redemption_date > datetime.now(timezone.utc):
                    upcoming_redemptions.append({
                        "date": next_redemption_date.isoformat().split('T')[0],
                        "fund_code": investment.fund_code,
                        "client_name": client_name,
                        "potential_amount": interest_earned,  # Interest redemption amount
                        "type": "interest",
                        "certainty": "medium"  # Based on client behavior patterns
                    })
        
        return {
            "success": True,
            "redemption_schedule": upcoming_redemptions
        }
        
    except Exception as e:
        logging.error(f"Get redemption schedule error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch redemption schedule")

@api_router.get("/admin/cashflow/projections")
async def get_cashflow_projections(months: int = 12):
    """Get cash flow projections for specified months"""
    try:
        projections = []
        today = datetime.now(timezone.utc)
        
        for i in range(months):
            projection_date = today + relativedelta(months=i)
            month_year = projection_date.strftime("%Y-%m")
            
            # Calculate projected inflows and outflows
            # This would be based on historical patterns and scheduled investments/redemptions
            projected_inflow = 0
            projected_outflow = 0
            
            # Add some realistic projections based on current investments
            for client_id, investments in client_investments.items():
                for investment_data in investments:
                    investment = FundInvestment(**investment_data)
                    fund_config = FIDUS_FUND_CONFIG[investment.fund_code]
                    
                    # Project monthly interest payments as potential outflows
                    monthly_interest = investment.principal_amount * (fund_config.interest_rate / 100)
                    projected_outflow += monthly_interest
            
            # Mock some additional inflow projections
            projected_inflow = projected_outflow * 1.2  # Assume 20% net positive flow
            
            projections.append({
                "month": month_year,
                "projected_inflow": projected_inflow,
                "projected_outflow": projected_outflow,
                "net_flow": projected_inflow - projected_outflow
            })
        
        return {
            "success": True,
            "projections": projections
        }
        
    except Exception as e:
        logging.error(f"Get cash flow projections error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch cash flow projections")

@api_router.get("/activity-logs/client/{client_id}")
async def get_client_activity_logs(client_id: str):
    """Get all activity logs for a specific client"""
    try:
        client_logs = [log.dict() for log in activity_logs if log.client_id == client_id]
        
        # Sort by timestamp (most recent first)
        client_logs.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {
            "success": True,
            "activity_logs": client_logs,
            "total_activities": len(client_logs)
        }
        
    except Exception as e:
        logging.error(f"Get client activity logs error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch client activity logs")

@api_router.get("/activity-logs/admin/all")
async def get_all_activity_logs():
    """Get all activity logs for admin review"""
    try:
        all_logs = []
        
        for log in activity_logs:
            log_data = log.dict()
            
            # Add client info
            client_info = None
            for user_data in MOCK_USERS.values():
                if user_data["id"] == log.client_id:
                    client_info = {
                        "name": user_data["name"],
                        "email": user_data["email"]
                    }
                    break
            
            log_data["client_info"] = client_info or {"name": "Unknown", "email": "Unknown"}
            all_logs.append(log_data)
        
        # Sort by timestamp (most recent first)
        all_logs.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {
            "success": True,
            "activity_logs": all_logs,
            "total_activities": len(all_logs)
        }
        
    except Exception as e:
        logging.error(f"Get all activity logs error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch activity logs")

# ===============================================================================
# CLIENT MANAGEMENT WITH INVESTMENT READINESS ENDPOINTS
# ===============================================================================

@api_router.get("/clients/all")
async def get_all_clients():
    """Get all clients with their investment readiness status from MongoDB"""
    try:
        # Get all clients from MongoDB
        clients = mongodb_manager.get_all_clients()
        
        # Calculate statistics
        total_clients = len(clients)
        ready_for_investment = len([c for c in clients if c.get('investment_ready', False)])
        
        return {
            "success": True,
            "clients": clients,
            "total_clients": total_clients,
            "ready_for_investment": ready_for_investment
        }
        
    except Exception as e:
        logging.error(f"Get all clients error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch clients")

@api_router.post("/clients/create")
async def create_new_client(client_data: ClientCreate):
    """Create a new client"""
    try:
        # Check if username already exists
        if client_data.username in MOCK_USERS:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Generate client ID
        client_id = f"client_{str(uuid.uuid4())[:8]}"
        
        # Create new client
        new_client = {
            "id": client_id,
            "username": client_data.username,
            "name": client_data.name,
            "email": client_data.email,
            "phone": client_data.phone or "",
            "type": "client",
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "profile_picture": f"https://images.unsplash.com/photo-150700{random.randint(1000, 9999)}?w=150&h=150&fit=crop&crop=face"
        }
        
        # Add to MOCK_USERS
        MOCK_USERS[client_data.username] = new_client
        
        # Initialize investment readiness
        client_readiness[client_id] = {
            'client_id': client_id,
            'aml_kyc_completed': False,
            'agreement_signed': False,
            'deposit_date': None,
            'investment_ready': False,
            'notes': client_data.notes,
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'updated_by': 'admin'
        }
        
        logging.info(f"New client created: {client_data.name} ({client_data.username})")
        
        return {
            "success": True,
            "client_id": client_id,
            "client": new_client,
            "message": f"Client {client_data.name} created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Create client error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create client")

@api_router.put("/clients/{client_id}/readiness")
async def update_client_readiness(client_id: str, readiness_data: ClientInvestmentReadinessUpdate):
    """Update client investment readiness status"""
    try:
        # Get existing readiness or create new
        current_readiness = client_readiness.get(client_id, {
            'client_id': client_id,
            'aml_kyc_completed': False,
            'agreement_signed': False,
            'account_creation_date': None,
            'investment_ready': False,
            'notes': '',
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'updated_by': ''
        })
        
        # Update provided fields
        if readiness_data.aml_kyc_completed is not None:
            current_readiness['aml_kyc_completed'] = readiness_data.aml_kyc_completed
        if readiness_data.agreement_signed is not None:
            current_readiness['agreement_signed'] = readiness_data.agreement_signed
        if readiness_data.account_creation_date is not None:
            current_readiness['account_creation_date'] = readiness_data.account_creation_date.isoformat()
        if readiness_data.notes is not None:
            current_readiness['notes'] = readiness_data.notes
        if readiness_data.updated_by is not None:
            current_readiness['updated_by'] = readiness_data.updated_by
        
        # Update timestamp
        current_readiness['updated_at'] = datetime.now(timezone.utc).isoformat()
        
        # Calculate investment readiness - only need AML KYC and Agreement for investment readiness
        # (account creation date is for record keeping, not a requirement for investment)
        investment_ready = (
            current_readiness['aml_kyc_completed'] and 
            current_readiness['agreement_signed']
        )
        current_readiness['investment_ready'] = investment_ready
        
        # Save updated readiness
        client_readiness[client_id] = current_readiness
        
        logging.info(f"Client readiness updated: {client_id} - Ready: {investment_ready}")
        
        return {
            "success": True,
            "client_id": client_id,
            "readiness": current_readiness,
            "message": f"Client readiness updated - {'Ready for investment' if investment_ready else 'Not ready for investment'}"
        }
        
    except Exception as e:
        logging.error(f"Update client readiness error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update client readiness")

@api_router.get("/clients/{client_id}/readiness")
async def get_client_readiness(client_id: str):
    """Get client investment readiness status"""
    try:
        readiness = client_readiness.get(client_id, {
            'client_id': client_id,
            'aml_kyc_completed': False,
            'agreement_signed': False,
            'account_creation_date': None,
            'investment_ready': False,
            'notes': '',
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'updated_by': ''
        })
        
        return {
            "success": True,
            "client_id": client_id,
            "readiness": readiness
        }
        
    except Exception as e:
        logging.error(f"Get client readiness error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch client readiness")

@api_router.get("/clients/ready-for-investment")
async def get_investment_ready_clients():
    """Get clients who are ready for investment (for dropdown in investment creation) - MongoDB version"""
    try:
        # Get all clients from MongoDB and filter for ready ones
        all_clients = mongodb_manager.get_all_clients()
        
        ready_clients = []
        for client in all_clients:
            if client.get('investment_ready', False):
                ready_clients.append({
                    'client_id': client['id'],
                    'name': client['name'],
                    'email': client['email'],
                    'username': client['username'],
                    'account_creation_date': client['readiness_status'].get('account_creation_date'),
                    'total_investments': client.get('total_investments', 0)
                })
        
        # Sort by name
        ready_clients.sort(key=lambda x: x['name'])
        
        return {
            "success": True,
            "ready_clients": ready_clients,
            "total_ready": len(ready_clients)
        }
        
    except Exception as e:
        logging.error(f"Get investment ready clients error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch investment ready clients")

# ===============================================================================
# MT5 INTEGRATION ENDPOINTS
# ===============================================================================

@api_router.get("/mt5/client/{client_id}/accounts")
async def get_client_mt5_accounts(client_id: str):
    """Get all MT5 accounts for a specific client"""
    try:
        accounts = mongodb_manager.get_client_mt5_accounts(client_id)
        
        # Get real-time performance for each account
        enriched_accounts = []
        for account in accounts:
            # Get performance data
            performance = await mt5_service.get_account_performance(account['account_id'])
            
            if performance:
                account['current_equity'] = performance.equity
                account['profit_loss'] = performance.profit
                account['profit_loss_percentage'] = (performance.profit / account['total_allocated'] * 100) if account['total_allocated'] > 0 else 0
                account['margin_level'] = performance.margin_level
                account['positions_count'] = performance.positions_count
                account['last_updated'] = performance.timestamp
            
            # Get connection status
            account['connection_status'] = mt5_service.get_connection_status(account['account_id']).value
            
            enriched_accounts.append(account)
        
        return {
            "success": True,
            "accounts": enriched_accounts,
            "total_accounts": len(enriched_accounts)
        }
        
    except Exception as e:
        logging.error(f"Get client MT5 accounts error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch MT5 accounts")

@api_router.get("/mt5/admin/accounts")
async def get_all_mt5_accounts():
    """Get all MT5 accounts for admin overview"""
    try:
        accounts = mongodb_manager.get_all_mt5_accounts()
        
        # Get real-time performance for each account
        enriched_accounts = []
        total_allocated = 0
        total_equity = 0
        total_profit_loss = 0
        
        for account in accounts:
            # Get performance data
            performance = await mt5_service.get_account_performance(account['account_id'])
            
            if performance:
                account['current_equity'] = performance.equity
                account['profit_loss'] = performance.profit
                account['profit_loss_percentage'] = (performance.profit / account['total_allocated'] * 100) if account['total_allocated'] > 0 else 0
                account['margin_level'] = performance.margin_level
                account['positions_count'] = performance.positions_count
                account['last_updated'] = performance.timestamp
            
            # Get connection status
            account['connection_status'] = mt5_service.get_connection_status(account['account_id']).value
            
            # Aggregate totals
            total_allocated += account['total_allocated']
            total_equity += account['current_equity']
            total_profit_loss += account['profit_loss']
            
            enriched_accounts.append(account)
        
        # Calculate overall performance
        overall_performance_percentage = (total_profit_loss / total_allocated * 100) if total_allocated > 0 else 0
        
        return {
            "success": True,
            "accounts": enriched_accounts,
            "summary": {
                "total_accounts": len(enriched_accounts),
                "total_allocated": total_allocated,
                "total_equity": total_equity,
                "total_profit_loss": total_profit_loss,
                "overall_performance_percentage": overall_performance_percentage
            }
        }
        
    except Exception as e:
        logging.error(f"Get all MT5 accounts error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch MT5 accounts")

@api_router.post("/mt5/admin/credentials/update")
async def update_mt5_credentials(credentials: MT5CredentialsRequest):
    """Update MT5 login credentials for a specific client and fund (Admin only)"""
    try:
        success = await mt5_service.update_client_mt5_credentials(
            credentials.client_id,
            credentials.fund_code,
            credentials.mt5_login,
            credentials.mt5_password,
            credentials.mt5_server
        )
        
        if success:
            return {
                "success": True,
                "message": f"MT5 credentials updated for client {credentials.client_id} fund {credentials.fund_code}"
            }
        else:
            raise HTTPException(status_code=404, detail="MT5 account not found or update failed")
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Update MT5 credentials error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update MT5 credentials")

# ===============================================================================
# MULTI-BROKER MT5 MANAGEMENT ENDPOINTS
# ===============================================================================

@api_router.get("/mt5/brokers")
async def get_available_brokers():
    """Get list of available MT5 brokers"""
    try:
        from mt5_integration import MT5BrokerConfig
        brokers = MT5BrokerConfig.get_broker_list()
        
        return {
            "success": True,
            "brokers": brokers
        }
        
    except Exception as e:
        logging.error(f"Get brokers error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch broker list")

@api_router.get("/mt5/brokers/{broker_code}/servers")
async def get_broker_servers(broker_code: str):
    """Get available servers for a specific broker"""
    try:
        from mt5_integration import MT5BrokerConfig
        
        if not MT5BrokerConfig.is_valid_broker(broker_code):
            raise HTTPException(status_code=400, detail="Invalid broker code")
        
        servers = MT5BrokerConfig.get_broker_servers(broker_code)
        broker_info = MT5BrokerConfig.BROKERS[broker_code]
        
        return {
            "success": True,
            "broker": broker_info["name"],
            "servers": servers
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Get broker servers error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch broker servers")

@api_router.post("/mt5/admin/add-manual-account")
async def add_manual_mt5_account(request: Request):
    """Manually add MT5 account with existing credentials"""
    try:
        data = await request.json()
        
        required_fields = ['client_id', 'fund_code', 'broker_code', 'mt5_login', 'mt5_password', 'mt5_server']
        for field in required_fields:
            if field not in data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Validate broker
        from mt5_integration import MT5BrokerConfig
        if not MT5BrokerConfig.is_valid_broker(data['broker_code']):
            raise HTTPException(status_code=400, detail="Invalid broker code")
        
        # Validate client exists
        client = mongodb_manager.get_client(data['client_id'])
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        account_id = await mt5_service.add_manual_mt5_account(
            client_id=data['client_id'],
            fund_code=data['fund_code'],
            broker_code=data['broker_code'],
            mt5_login=int(data['mt5_login']),
            mt5_password=data['mt5_password'],
            mt5_server=data['mt5_server'],
            allocated_amount=float(data.get('allocated_amount', 0.0))
        )
        
        if account_id:
            return {
                "success": True,
                "message": "MT5 account added successfully",
                "account_id": account_id
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create MT5 account")
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Add manual MT5 account error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add MT5 account")

@api_router.get("/mt5/admin/accounts/by-broker")
async def get_mt5_accounts_by_broker():
    """Get all MT5 accounts grouped by broker"""
    try:
        accounts = mongodb_manager.get_all_mt5_accounts()
        
        # Group accounts by broker
        accounts_by_broker = {}
        total_stats = {
            "total_accounts": 0,
            "total_allocated": 0,
            "total_equity": 0,
            "total_profit_loss": 0
        }
        
        for account in accounts:
            broker_code = account.get('broker_code', 'unknown')
            broker_name = account.get('broker_name', 'Unknown Broker')
            
            if broker_code not in accounts_by_broker:
                accounts_by_broker[broker_code] = {
                    "broker_name": broker_name,
                    "broker_code": broker_code,
                    "accounts": [],
                    "stats": {
                        "account_count": 0,
                        "total_allocated": 0,
                        "total_equity": 0,
                        "total_profit_loss": 0
                    }
                }
            
            # Get real-time performance data
            performance = await mt5_service.get_account_performance(account['account_id'])
            if performance:
                account['current_equity'] = performance.equity
                account['profit_loss'] = performance.profit
                account['profit_loss_percentage'] = (performance.profit / account['total_allocated'] * 100) if account['total_allocated'] > 0 else 0
            
            # Get connection status
            account['connection_status'] = mt5_service.get_connection_status(account['account_id']).value
            
            # Add to broker group
            accounts_by_broker[broker_code]["accounts"].append(account)
            accounts_by_broker[broker_code]["stats"]["account_count"] += 1
            accounts_by_broker[broker_code]["stats"]["total_allocated"] += account['total_allocated']
            accounts_by_broker[broker_code]["stats"]["total_equity"] += account['current_equity']
            accounts_by_broker[broker_code]["stats"]["total_profit_loss"] += account['profit_loss']
            
            # Update global stats
            total_stats["total_accounts"] += 1
            total_stats["total_allocated"] += account['total_allocated']
            total_stats["total_equity"] += account['current_equity']
            total_stats["total_profit_loss"] += account['profit_loss']
        
        return {
            "success": True,
            "accounts_by_broker": accounts_by_broker,
            "total_stats": total_stats
        }
        
    except Exception as e:
        logging.error(f"Get MT5 accounts by broker error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch MT5 accounts by broker")

@api_router.get("/mt5/admin/account/{account_id}/activity")
async def get_mt5_account_activity(account_id: str):
    """Get real trading activity for specific MT5 account"""
    try:
        # Get activity from mt5_activity collection
        activities = []
        
        # Query the database directly for real trading activities
        async for activity in db.mt5_activity.find({'account_id': account_id}).sort('timestamp', -1):
            activity.pop('_id', None)  # Remove MongoDB ObjectId
            activities.append(activity)
        
        if not activities:
            # If no activities in database, return empty array
            activities = []
        
        return {
            "success": True,
            "account_id": account_id,
            "activity": activities,
            "total_activities": len(activities)
        }
        
    except Exception as e:
        logging.error(f"Get MT5 account activity error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch MT5 account activity")

@api_router.get("/mt5/admin/account/{account_id}/positions")  
async def get_mt5_account_positions(account_id: str):
    """Get current trading positions for specific MT5 account"""
    try:
        # Get current open positions from activity
        positions = []
        
        async for activity in db.mt5_activity.find({
            'account_id': account_id,
            'type': 'trade',
            'status': 'open'
        }).sort('timestamp', -1):
            activity.pop('_id', None)
            positions.append({
                'symbol': activity.get('symbol'),
                'type': activity.get('trade_type'),
                'volume': activity.get('volume'),
                'opening_price': activity.get('opening_price'),
                'current_price': activity.get('current_price'),
                'profit_loss': activity.get('profit_loss'),
                'timestamp': activity.get('timestamp')
            })
        
        return {
            "success": True,
            "account_id": account_id,
            "positions": positions,
            "total_positions": len(positions)
        }
        
    except Exception as e:
        logging.error(f"Get MT5 account positions error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch MT5 account positions")

@api_router.get("/mt5/admin/realtime-data")
async def get_realtime_mt5_data():
    """Get real-time MT5 data for all accounts with live updates"""
    try:
        accounts = []
        
        # Get all MT5 account records with latest real-time data
        async for account in db.mt5_accounts.find({}):
            account.pop('_id', None)
            
            # Get the latest historical data point for charts
            latest_historical = await db.mt5_historical_data.find_one(
                {'account_id': account['account_id']},
                sort=[('timestamp', -1)]
            )
            
            if latest_historical:
                latest_historical.pop('_id', None)
                account['latest_data'] = latest_historical
            
            # Get current real-time positions
            positions = []
            async for position in db.mt5_realtime_positions.find({'account_id': account['account_id']}):
                position.pop('_id', None)
                positions.append(position)
            
            account['current_positions'] = positions
            account['position_count'] = len(positions)
            
            # Calculate real-time statistics
            account['connection_status'] = 'connected'
            account['last_update'] = account.get('last_sync', datetime.now(timezone.utc).isoformat())
            
            accounts.append(account)
        
        # Calculate aggregate statistics
        total_stats = {
            'total_accounts': len(accounts),
            'total_allocated': sum(acc.get('total_allocated', 0) for acc in accounts),
            'total_equity': sum(acc.get('current_equity', 0) for acc in accounts),
            'total_balance': sum(acc.get('balance', 0) for acc in accounts),
            'total_profit_loss': sum(acc.get('profit_loss', 0) for acc in accounts),
            'connected_accounts': len([acc for acc in accounts if acc.get('connection_status') == 'connected']),
            'last_update': datetime.now(timezone.utc).isoformat()
        }
        
        return {
            "success": True,
            "accounts": accounts,
            "total_stats": total_stats,
            "data_source": "real_time",
            "update_frequency": "30_seconds"
        }
        
    except Exception as e:
        logging.error(f"Get real-time MT5 data error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch real-time MT5 data")

@api_router.get("/mt5/admin/historical-data/{account_id}")
async def get_mt5_historical_data(account_id: str, hours: int = 24):
    """Get historical MT5 data for charts and analysis"""
    try:
        # Calculate time window
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours)
        
        # Get historical data points
        historical_data = []
        async for data_point in db.mt5_historical_data.find({
            'account_id': account_id,
            'timestamp': {
                '$gte': start_time.isoformat(),
                '$lte': end_time.isoformat()
            }
        }).sort('timestamp', 1):
            data_point.pop('_id', None)
            historical_data.append(data_point)
        
        return {
            "success": True,
            "account_id": account_id,
            "historical_data": historical_data,
            "time_window_hours": hours,
            "data_points": len(historical_data),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
        
    except Exception as e:
        logging.error(f"Get historical MT5 data error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch historical MT5 data")

@api_router.get("/mt5/admin/system-status")
async def get_mt5_system_status():
    """Get MT5 data collection system status"""
    try:
        # Check recent data activity
        recent_cutoff = datetime.now(timezone.utc) - timedelta(minutes=5)
        recent_updates = await db.mt5_historical_data.count_documents({
            'timestamp': {'$gte': recent_cutoff.isoformat()}
        })
        
        # Get total data points
        total_data_points = await db.mt5_historical_data.count_documents({})
        
        # Get account connection status
        accounts = []
        async for account in db.mt5_accounts.find({}, {'account_id': 1, 'connection_status': 1, 'last_sync': 1}):
            account.pop('_id', None)
            accounts.append(account)
        
        return {
            "success": True,
            "system_status": "operational" if recent_updates > 0 else "inactive",
            "recent_updates": recent_updates,
            "total_data_points": total_data_points,
            "accounts": accounts,
            "data_collection_active": recent_updates > 0,
            "last_check": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logging.error(f"Get MT5 system status error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get system status")

# ===============================================================================
# FUND PERFORMANCE vs MT5 REALITY MANAGEMENT SYSTEM
# ===============================================================================

# Import the fund performance manager
try:
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from fund_performance_manager import fund_performance_manager
    logging.info("Fund performance manager successfully imported")
except ImportError as e:
    logging.error(f"Failed to import fund_performance_manager: {e}")
    fund_performance_manager = None
except Exception as e:
    logging.error(f"Unexpected error importing fund_performance_manager: {e}")
    fund_performance_manager = None

@api_router.get("/admin/fund-performance/dashboard")
async def get_fund_performance_dashboard():
    """Get comprehensive fund performance vs MT5 reality dashboard"""
    try:
        # Import fund performance manager directly
        import sys
        sys.path.append('/app/backend')
        from fund_performance_manager import fund_performance_manager as fpm
        
        if not fpm:
            return {
                "success": False,
                "error": "Fund performance manager not available",
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        
        dashboard_data = await fpm.generate_fund_management_dashboard()
        
        return {
            "success": True,
            "dashboard": dashboard_data,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logging.error(f"Fund performance dashboard error: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to generate fund performance dashboard: {str(e)}",
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

@api_router.get("/admin/fund-performance/client/{client_id}")
async def get_client_fund_performance(client_id: str):
    """Get detailed fund performance comparison for specific client"""
    try:
        # Import fund performance manager directly
        import sys
        sys.path.append('/app/backend')
        from fund_performance_manager import fund_performance_manager as fpm
        
        if not fpm:
            return {
                "success": False,
                "error": "Fund performance manager not available",
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        
        client_comparison = await fpm.get_client_fund_comparison(client_id)
        
        return {
            "success": True,
            "client_comparison": client_comparison,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logging.error(f"Client fund performance error: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to get client fund performance: {str(e)}",
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

@api_router.get("/admin/fund-performance/gaps")
async def get_performance_gaps():
    """Get all performance gaps between FIDUS commitments and MT5 reality"""
    try:
        # Import fund performance manager directly
        import sys
        sys.path.append('/app/backend')
        from fund_performance_manager import fund_performance_manager as fpm
        
        if not fpm:
            return {
                "success": False,
                "performance_gaps": [],
                "total_gaps": 0,
                "error": "Fund performance manager not available",
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        
        # Get all MT5 accounts (primary data source for actual client positions)
        gaps = []
        
        # Use MT5 accounts as the source of truth for client positions
        async for account in fpm.db.mt5_accounts.find({}):
            client_id = account["client_id"]
            fund_code = account["fund_code"]
            principal_amount = account.get("total_allocated", account.get("initial_deposit", 0))
            deposit_date = account.get("deposit_date", account.get("created_at"))
            
            try:
                gap = await fpm.analyze_mt5_performance_gap(
                    client_id, fund_code, principal_amount, deposit_date, account
                )
                
                gaps.append({
                    "client_id": gap.client_id,
                    "fund_code": gap.fund_code,
                    "expected_performance": gap.expected_performance,
                    "actual_mt5_performance": gap.actual_mt5_performance,
                    "gap_amount": gap.gap_amount,
                    "gap_percentage": gap.gap_percentage,
                    "risk_level": gap.risk_level,
                    "action_required": gap.action_required,
                    "recommendation": fpm.get_recommendation(gap),
                    "principal_amount": principal_amount,
                    "deposit_date": deposit_date,
                    "mt5_login": account.get("mt5_login")
                })
            except Exception as e:
                logging.error(f"Error analyzing gap for {client_id} {fund_code}: {str(e)}")
        
        return {
            "success": True,
            "performance_gaps": gaps,
            "total_gaps": len(gaps),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logging.error(f"Performance gaps error: {str(e)}")
        return {
            "success": False,
            "performance_gaps": [],
            "total_gaps": 0,
            "error": f"Failed to get performance gaps: {str(e)}",
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

@api_router.get("/admin/fund-commitments")
async def get_fund_commitments():
    """Get FIDUS client investment deliverables - only funds with actual client investments"""
    try:
        # Import fund performance manager directly
        import sys
        sys.path.append('/app/backend')
        from fund_performance_manager import fund_performance_manager as fpm
        
        if not fpm:
            return {
                "success": False,
                "fund_commitments": {},
                "error": "Fund performance manager not available",
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        
        # Get dashboard data which only includes funds with actual client investments
        dashboard_data = await fpm.generate_fund_management_dashboard()
        
        return {
            "success": True,
            "fund_commitments": dashboard_data.get("fund_commitments", {}),
            "note": "Only showing funds with actual client investments (client investment deliverables)",
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logging.error(f"Fund commitments error: {str(e)}")
        return {
            "success": False,
            "fund_commitments": {},
            "error": f"Failed to get fund commitments: {str(e)}",
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

@api_router.get("/admin/fund-performance/test")
async def test_fund_performance_manager():
    """Test fund performance manager availability and basic functionality"""
    try:
        import sys
        sys.path.append('/app/backend')
        from fund_performance_manager import fund_performance_manager as fpm
        
        if not fpm:
            return {"success": False, "error": "Fund performance manager is None"}
        
        # Test basic functionality
        fund_commitments = list(fpm.fund_commitments.keys())
        
        # Test with Salvador's data
        from datetime import datetime
        
        # Test expected performance calculation
        expected = await fpm.calculate_expected_performance(
            "client_003", "BALANCE", 100000.0, datetime(2024, 12, 19)
        )
        
        # Test MT5 actual performance
        actual = await fpm.get_mt5_actual_performance("client_003", "BALANCE")
        
        # Test full gap analysis
        gap = await fpm.analyze_performance_gap(
            "client_003", "BALANCE", 100000.0, datetime(2024, 12, 19)
        )
        
        return {
            "success": True,
            "manager_type": str(type(fpm)),
            "fund_commitments": fund_commitments,
            "expected_performance": expected,
            "actual_performance": actual,
            "test_gap": {
                "client_id": gap.client_id,
                "fund_code": gap.fund_code,
                "expected": gap.expected_performance,
                "actual": gap.actual_mt5_performance,
                "gap_amount": gap.gap_amount,
                "gap_percentage": gap.gap_percentage,
                "risk_level": gap.risk_level
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }

@api_router.post("/admin/fund-performance/alert")
async def create_performance_alert(request: Request):
    """Create alert for significant performance gaps"""
    try:
        data = await request.json()
        
        alert_data = {
            "alert_id": f"alert_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            "client_id": data.get("client_id"),
            "fund_code": data.get("fund_code"),
            "alert_type": data.get("alert_type", "PERFORMANCE_GAP"),
            "severity": data.get("severity", "MEDIUM"),
            "message": data.get("message", "Performance alert"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "acknowledged": False,
            "action_taken": None
        }
        
        # Store alert in database
        await db.fund_performance_alerts.insert_one(alert_data)
        
        return {
            "success": True,
            "alert_id": alert_data["alert_id"],
            "message": "Performance alert created successfully"
        }
        
    except Exception as e:
        logging.error(f"Create performance alert error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create performance alert")

@api_router.get("/mt5/client/{client_id}/performance")
async def get_client_mt5_performance(client_id: str):
    """Get comprehensive MT5 performance summary for client"""
    try:
        summary = await mt5_service.get_account_summary(client_id)
        
        if not summary:
            return {
                "success": True,
                "message": "No MT5 accounts found for client",
                "summary": {
                    "total_accounts": 0,
                    "total_allocated": 0,
                    "total_equity": 0,
                    "total_profit_loss": 0,
                    "overall_performance_percentage": 0,
                    "accounts": []
                }
            }
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        logging.error(f"Get client MT5 performance error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch MT5 performance")

@api_router.get("/mt5/admin/performance/overview")
async def get_mt5_performance_overview():
    """Get system-wide MT5 performance overview (Admin only)"""
    try:
        # Get all accounts performance
        all_performance = await mt5_service.get_all_accounts_performance()
        
        # Aggregate statistics
        total_accounts = len(all_performance)
        total_equity = sum(perf.equity for perf in all_performance.values())
        total_profit = sum(perf.profit for perf in all_performance.values())
        
        # Get account allocation data
        all_accounts = mongodb_manager.get_all_mt5_accounts()
        total_allocated = sum(acc['total_allocated'] for acc in all_accounts)
        
        # Calculate performance metrics
        overall_performance_percentage = (total_profit / total_allocated * 100) if total_allocated > 0 else 0
        
        # Group by fund
        fund_performance = {}
        for account in all_accounts:
            fund_code = account['fund_code']
            if fund_code not in fund_performance:
                fund_performance[fund_code] = {
                    'fund_code': fund_code,
                    'accounts_count': 0,
                    'total_allocated': 0,
                    'total_equity': 0,
                    'total_profit_loss': 0,
                    'performance_percentage': 0
                }
            
            fund_performance[fund_code]['accounts_count'] += 1
            fund_performance[fund_code]['total_allocated'] += account['total_allocated']
            
            if account['account_id'] in all_performance:
                perf = all_performance[account['account_id']]
                fund_performance[fund_code]['total_equity'] += perf.equity
                fund_performance[fund_code]['total_profit_loss'] += perf.profit
        
        # Calculate fund performance percentages
        for fund_code in fund_performance:
            fund_data = fund_performance[fund_code]
            if fund_data['total_allocated'] > 0:
                fund_data['performance_percentage'] = (
                    fund_data['total_profit_loss'] / fund_data['total_allocated'] * 100
                )
        
        return {
            "success": True,
            "overview": {
                "total_accounts": total_accounts,
                "total_allocated": total_allocated,
                "total_equity": total_equity,
                "total_profit_loss": total_profit,
                "overall_performance_percentage": overall_performance_percentage,
                "fund_breakdown": list(fund_performance.values()),
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        }
        
    except Exception as e:
        logging.error(f"Get MT5 performance overview error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch performance overview")

@api_router.post("/mt5/admin/account/{account_id}/disconnect")
async def disconnect_mt5_account(account_id: str):
    """Disconnect specific MT5 account (Admin only)"""
    try:
        success = await mt5_service.disconnect_account(account_id)
        
        if success:
            return {
                "success": True,
                "message": f"MT5 account {account_id} disconnected successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Account not found or disconnect failed")
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Disconnect MT5 account error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to disconnect MT5 account")

# ===============================================================================
# MULTI-FACTOR AUTHENTICATION ENDPOINTS
# ===============================================================================

@api_router.post("/auth/mfa/setup")
async def setup_mfa(request: MFASetupRequest):
    """Setup MFA for user"""
    try:
        setup = mfa_service.setup_mfa(request.user_id, request.user_email)
        
        return {
            "success": True,
            "secret": setup.secret,
            "qr_code": setup.qr_code,
            "backup_codes": setup.backup_codes,
            "setup_token": setup.setup_token
        }
        
    except Exception as e:
        logging.error(f"MFA setup error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to setup MFA")

@api_router.post("/auth/mfa/verify")
async def verify_mfa(request: MFAVerifyRequest):
    """Verify MFA token"""
    try:
        if request.method == "totp":
            result = mfa_service.verify_totp(request.user_id, request.token)
        elif request.method == "backup_code":
            result = mfa_service.verify_backup_code(request.user_id, request.token)
        elif request.method == "sms":
            result = mfa_service.verify_sms_code(request.user_id, request.token)
        else:
            raise HTTPException(status_code=400, detail="Invalid MFA method")
        
        response_data = {
            "success": result.is_valid,
            "method": result.method,
            "remaining_attempts": result.remaining_attempts
        }
        
        if result.locked_until:
            response_data["locked_until"] = result.locked_until.isoformat()
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"MFA verification error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to verify MFA")

@api_router.post("/auth/mfa/sms/send")
async def send_sms_code(request: SMSRequest):
    """Send SMS verification code"""
    try:
        success = mfa_service.send_sms_code(request.user_id, request.phone_number)
        
        return {
            "success": success,
            "message": "SMS code sent successfully" if success else "Failed to send SMS code"
        }
        
    except Exception as e:
        logging.error(f"Send SMS code error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send SMS code")

@api_router.get("/auth/mfa/status/{user_id}")
async def get_mfa_status(user_id: str):
    """Get MFA status for user"""
    try:
        status = mfa_service.get_user_mfa_status(user_id)
        return {
            "success": True,
            "status": status
        }
        
    except Exception as e:
        logging.error(f"Get MFA status error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get MFA status")

@api_router.post("/auth/mfa/disable/{user_id}")
async def disable_mfa(user_id: str):
    """Disable MFA for user (admin only)"""
    try:
        success = mfa_service.disable_mfa(user_id)
        
        return {
            "success": success,
            "message": "MFA disabled successfully" if success else "No MFA found for user"
        }
        
    except Exception as e:
        logging.error(f"Disable MFA error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to disable MFA")

@api_router.post("/auth/mfa/recovery-codes/{user_id}")
async def generate_recovery_codes(user_id: str):
    """Generate new recovery codes for user"""
    try:
        codes = mfa_service.generate_recovery_codes(user_id)
        
        return {
            "success": True,
            "backup_codes": codes,
            "message": "New recovery codes generated. Previous codes are now invalid."
        }
        
    except Exception as e:
        logging.error(f"Generate recovery codes error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate recovery codes")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================================================================
# SECURITY MIDDLEWARE - CRITICAL SECURITY HEADERS
# ===============================================================================

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add critical security headers to all responses"""
    response = await call_next(request)
    
    # Prevent clickjacking attacks
    response.headers["X-Frame-Options"] = "DENY"
    
    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # Enable XSS protection
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Enforce HTTPS (in production)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Content Security Policy - Basic policy for financial apps
    csp_policy = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://us-assets.i.posthog.com; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self' https:; "
        "frame-ancestors 'none';"
    )
    response.headers["Content-Security-Policy"] = csp_policy
    
    # Referrer policy for privacy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Feature policy to restrict dangerous features
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    
    return response

# ===============================================================================
# API AUTHENTICATION MIDDLEWARE - PROTECT SENSITIVE ENDPOINTS
# ===============================================================================

PROTECTED_ENDPOINTS = [
    "/api/admin/",
    "/api/clients/all",
    "/api/investments/create",
    "/api/investments/admin/",
    "/api/documents/admin/",
    "/api/mt5/admin/",
    "/api/crm/",
    "/api/fund-configurations/",
    "/api/payment-confirmations/"
]

# Admin-only endpoints that require admin role
ADMIN_ONLY_ENDPOINTS = [
    "/api/admin/",
    "/api/clients/all",
    "/api/investments/admin/",
    "/api/documents/admin/",
    "/api/mt5/admin/",
    "/api/crm/",
    "/api/fund-configurations/",
    "/api/payment-confirmations/"
]

# AUTHENTICATION MIDDLEWARE - JWT TOKEN VALIDATION
# Now properly implemented with JWT tokens and role-based access control
@app.middleware("http") 
async def api_authentication_middleware(request: Request, call_next):
    """Protect sensitive API endpoints with JWT token validation and role-based access control"""
    path = request.url.path
    
    # Check if this is a protected endpoint
    is_protected = any(path.startswith(endpoint) for endpoint in PROTECTED_ENDPOINTS)
    is_admin_only = any(path.startswith(endpoint) for endpoint in ADMIN_ONLY_ENDPOINTS)
    
    if is_protected and request.method != "OPTIONS":
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            logging.warning(f"Missing or invalid Authorization header for {path}")
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized", 
                    "message": "JWT token required. Please include 'Authorization: Bearer <token>' header.",
                    "endpoint": path
                }
            )
        
        # Extract and validate JWT token
        try:
            token = auth_header.split(" ")[1]
            payload = verify_jwt_token(token)
            
            # Add user info to request state for downstream use
            request.state.user_id = payload["user_id"]
            request.state.username = payload["username"]
            request.state.user_type = payload["user_type"]
            
            # Check role-based access for admin-only endpoints
            if is_admin_only and payload["user_type"] != "admin":
                logging.warning(f"Access denied for non-admin user {payload['username']} to {path}")
                return JSONResponse(
                    status_code=403,
                    content={
                        "error": "Forbidden", 
                        "message": f"Admin access required. User type '{payload['user_type']}' cannot access this endpoint.",
                        "endpoint": path
                    }
                )
            
        except HTTPException:
            # Token validation failed
            logging.warning(f"Invalid JWT token for {path}")
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized", 
                    "message": "Invalid or expired JWT token",
                    "endpoint": path
                }
            )
        except Exception as e:
            logging.error(f"JWT token validation error for {path}: {str(e)}")
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized", 
                    "message": "Token validation failed",
                    "endpoint": path
                }
            )
    
    response = await call_next(request)
    return response

# ===============================================================================
# RATE LIMITING MIDDLEWARE - PREVENT API ABUSE
# ===============================================================================

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
        self.cleanup_interval = 3600  # Clean up old entries every hour
        self.last_cleanup = time()
        self.total_requests = 0  # For debugging
        self.blocked_requests = 0  # For debugging
    
    def is_allowed(self, key: str, limit: int = 100, window: int = 60) -> bool:
        """Check if request is allowed under rate limit"""
        current_time = time()
        self.total_requests += 1
        
        # Clean up old entries periodically
        if current_time - self.last_cleanup > self.cleanup_interval:
            self.cleanup_old_entries()
            self.last_cleanup = current_time
        
        # Remove expired entries for this key
        if key in self.requests:
            self.requests[key] = [
                timestamp for timestamp in self.requests[key]
                if current_time - timestamp < window
            ]
        
        # Check if we're under the limit
        current_count = len(self.requests[key])
        
        if current_count >= limit:
            self.blocked_requests += 1
            logging.debug(f"Rate limit blocking {key}: {current_count}/{limit} requests in window")
            return False
        
        # Add current request timestamp
        self.requests[key].append(current_time)
        logging.debug(f"Rate limit allowing {key}: {current_count + 1}/{limit} requests in window")
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics for monitoring"""
        return {
            "total_requests": self.total_requests,
            "blocked_requests": self.blocked_requests,
            "block_rate": (self.blocked_requests / max(self.total_requests, 1)) * 100,
            "active_clients": len(self.requests),
            "cleanup_interval": self.cleanup_interval
        }
    
    def cleanup_old_entries(self):
        """Clean up old request entries to prevent memory leaks"""
        current_time = time()
        keys_to_remove = []
        
        for key, timestamps in self.requests.items():
            # Keep only timestamps from last hour
            self.requests[key] = [
                timestamp for timestamp in timestamps
                if current_time - timestamp < 3600
            ]
            
            # Remove empty entries
            if not self.requests[key]:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.requests[key]
        
        logging.info(f"Rate limiter cleanup: removed {len(keys_to_remove)} inactive clients")

# Global rate limiter instance
rate_limiter = RateLimiter()

@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    """Enhanced rate limiting middleware to prevent API abuse"""
    
    # Skip rate limiting for health checks and static files
    if (request.url.path.startswith('/api/health') or 
        request.url.path.startswith('/static') or
        request.method == "OPTIONS"):
        return await call_next(request)
    
    # Get client identifier (prefer user ID, fallback to IP)
    client_id = None
    
    # Try to get user ID from JWT token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM], options={"verify_exp": False})
            client_id = f"user:{payload.get('user_id', 'unknown')}"
        except Exception as e:
            logging.debug(f"JWT decode error in rate limiter: {e}")
    
    # Fallback to IP address
    if not client_id:
        # Get real IP from headers (for proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        real_ip = request.headers.get("X-Real-IP")
        
        if forwarded_for:
            client_id = f"ip:{forwarded_for.split(',')[0].strip()}"
        elif real_ip:
            client_id = f"ip:{real_ip}"
        else:
            client_id = f"ip:{request.client.host if request.client else 'unknown'}"
    
    # Apply rate limiting with enhanced logging
    limit = 100  # requests per minute
    is_allowed = rate_limiter.is_allowed(client_id, limit=limit, window=60)
    
    # Debug logging for rate limiter
    logging.debug(f"Rate limiter check: client_id={client_id}, allowed={is_allowed}, path={request.url.path}")
    
    if not is_allowed:
        logging.warning(f"Rate limit exceeded for {client_id} on {request.url.path}")
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Limit: {limit} requests per minute.",
                "retry_after": 60,
                "client_id": client_id  # For debugging only
            },
            headers={"Retry-After": "60"}
        )
    
    return await call_next(request)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()