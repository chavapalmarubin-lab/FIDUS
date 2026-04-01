from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import hashlib
import secrets

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'fidus_app')]

# Create the main app
app = FastAPI(title="FIDUS Investment App API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer(auto_error=False)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===== Models =====

class PaymentScheduleItem(BaseModel):
    month: str
    amount: float
    status: str  # 'Funded' or 'Pending'

class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    type: str  # 'deposit', 'withdrawal', 'return'
    amount: float
    description: str
    status: str  # 'completed', 'pending', 'failed'
    created_at: datetime = Field(default_factory=datetime.utcnow)

class NotificationPreferences(BaseModel):
    payment_reminders: bool = True
    deposit_alerts: bool = True
    monthly_reports: bool = True
    push_enabled: bool = True

class TermsAcceptance(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_email: str
    user_name: str
    lucrum_terms_accepted: bool = False
    fidus_terms_accepted: bool = False
    copy_trading_terms_accepted: bool = False
    terms_version: str = "1.0"
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    accepted_at: datetime = Field(default_factory=datetime.utcnow)

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    password_hash: str
    name: str
    phone: Optional[str] = None
    balance: float = 5000.0
    total_earnings: float = 225.0
    monthly_return: float = 75.0
    biometric_enabled: bool = False
    terms_accepted: bool = False
    terms_accepted_at: Optional[datetime] = None
    notification_preferences: NotificationPreferences = Field(default_factory=NotificationPreferences)
    push_token: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    payment_schedule: List[PaymentScheduleItem] = []

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    phone: Optional[str] = None
    balance: float
    totalEarnings: float
    monthlyReturn: float
    biometricEnabled: bool
    termsAccepted: bool
    termsAcceptedAt: Optional[datetime] = None
    notificationPreferences: NotificationPreferences
    paymentSchedule: List[PaymentScheduleItem]

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    token: str
    user: UserResponse

class Session(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    token: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime

class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class UpdateNotificationPreferencesRequest(BaseModel):
    payment_reminders: Optional[bool] = None
    deposit_alerts: Optional[bool] = None
    monthly_reports: Optional[bool] = None

class AcceptTermsRequest(BaseModel):
    lucrum_terms_accepted: bool
    fidus_terms_accepted: bool
    copy_trading_terms_accepted: bool
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class TermsAcceptanceLog(BaseModel):
    id: str
    user_id: str
    user_email: str
    user_name: str
    lucrum_terms_accepted: bool
    fidus_terms_accepted: bool
    copy_trading_terms_accepted: bool
    terms_version: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    accepted_at: datetime

class RegisterPushTokenRequest(BaseModel):
    push_token: str

class TransactionResponse(BaseModel):
    id: str
    type: str
    amount: float
    description: str
    status: str
    createdAt: datetime

class PortfolioDataPoint(BaseModel):
    month: str
    balance: float
    earnings: float

# ===== Helper Functions =====

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token() -> str:
    return secrets.token_urlsafe(32)

def generate_payment_schedule(balance: float) -> List[PaymentScheduleItem]:
    months = ['January', 'February', 'March', 'April', 'May', 'June', 
              'July', 'August', 'September', 'October', 'November', 'December']
    current_month = datetime.now().month - 1  # 0-indexed
    current_year = datetime.now().year
    monthly_return = balance * 0.015
    
    schedule = []
    for i in range(6):
        month_index = (current_month + i) % 12
        year = current_year + ((current_month + i) // 12)
        schedule.append(PaymentScheduleItem(
            month=f"{months[month_index]} {year}",
            amount=monthly_return,
            status='Funded' if i < 3 else 'Pending'
        ))
    
    return schedule

def generate_transaction_history(user_id: str, balance: float) -> List[Transaction]:
    """Generate sample transaction history"""
    transactions = []
    monthly_return = balance * 0.015
    months = ['January', 'February', 'March', 'April', 'May', 'June']
    
    # Initial deposit
    transactions.append(Transaction(
        user_id=user_id,
        type='deposit',
        amount=balance,
        description='Initial deposit via Bank Transfer',
        status='completed',
        created_at=datetime.now() - timedelta(days=180)
    ))
    
    # Monthly returns
    for i, month in enumerate(months[:3]):
        transactions.append(Transaction(
            user_id=user_id,
            type='return',
            amount=monthly_return,
            description=f'{month} 2026 - 1.5% Monthly Return',
            status='completed',
            created_at=datetime.now() - timedelta(days=90 - (i * 30))
        ))
    
    return transactions

def generate_portfolio_history(balance: float) -> List[PortfolioDataPoint]:
    """Generate 12-month portfolio history"""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    current_month = datetime.now().month - 1
    monthly_rate = 0.015
    
    # Start with initial balance 6 months ago
    initial_balance = balance - (balance * monthly_rate * 3)  # Approximate
    history = []
    
    running_balance = initial_balance
    running_earnings = 0
    
    for i in range(6):
        month_index = (current_month - 5 + i) % 12
        month_earnings = running_balance * monthly_rate
        running_balance += month_earnings
        running_earnings += month_earnings
        
        history.append(PortfolioDataPoint(
            month=months[month_index],
            balance=round(running_balance, 2),
            earnings=round(running_earnings, 2)
        ))
    
    return history

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[User]:
    if not credentials:
        return None
    
    token = credentials.credentials
    session = await db.sessions.find_one({"token": token})
    
    if not session:
        return None
    
    if datetime.utcnow() > session.get('expires_at'):
        await db.sessions.delete_one({"token": token})
        return None
    
    user_data = await db.users.find_one({"id": session.get('user_id')})
    if not user_data:
        return None
    
    return User(**user_data)

# ===== Initialization =====

async def init_demo_user():
    """Initialize demo user if not exists"""
    demo_email = "carlos.demo@test.com"
    demo_password = "Fidus26@"
    
    existing = await db.users.find_one({"email": demo_email})
    if not existing:
        balance = 5000.0
        demo_user = User(
            email=demo_email,
            password_hash=hash_password(demo_password),
            name="Carlos",
            phone="+1 555-0123",
            balance=balance,
            total_earnings=225.0,
            monthly_return=balance * 0.015,
            payment_schedule=generate_payment_schedule(balance)
        )
        await db.users.insert_one(demo_user.dict())
        
        # Create transaction history
        transactions = generate_transaction_history(demo_user.id, balance)
        for tx in transactions:
            await db.transactions.insert_one(tx.dict())
        
        logger.info(f"Demo user created: {demo_email}")
    else:
        # Update existing user with new fields if missing
        updates = {}
        if 'notification_preferences' not in existing:
            updates['notification_preferences'] = NotificationPreferences().dict()
        if 'biometric_enabled' not in existing:
            updates['biometric_enabled'] = False
        if 'phone' not in existing:
            updates['phone'] = "+1 555-0123"
        
        if updates:
            await db.users.update_one({"email": demo_email}, {"$set": updates})
            logger.info(f"Updated demo user with new fields")
        
        # Create transactions if missing
        tx_count = await db.transactions.count_documents({"user_id": existing.get('id')})
        if tx_count == 0:
            transactions = generate_transaction_history(existing.get('id'), existing.get('balance', 5000.0))
            for tx in transactions:
                await db.transactions.insert_one(tx.dict())
            logger.info(f"Created transactions for demo user")

@app.on_event("startup")
async def startup_event():
    await init_demo_user()
    logger.info("FIDUS API started successfully")

# ===== API Routes =====

@api_router.get("/")
async def root():
    return {"message": "FIDUS Investment App API", "version": "2.0.0"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@api_router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate user and return token"""
    user_data = await db.users.find_one({"email": request.email.lower()})
    
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if user_data.get('password_hash') != hash_password(request.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create session
    token = generate_token()
    session = Session(
        user_id=user_data['id'],
        token=token,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    await db.sessions.insert_one(session.dict())
    
    # Build response
    user = User(**user_data)
    
    return LoginResponse(
        success=True,
        token=token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            phone=user.phone,
            balance=user.balance,
            totalEarnings=user.total_earnings,
            monthlyReturn=user.monthly_return,
            biometricEnabled=user.biometric_enabled,
            termsAccepted=user.terms_accepted,
            termsAcceptedAt=user.terms_accepted_at,
            notificationPreferences=user.notification_preferences,
            paymentSchedule=user.payment_schedule
        )
    )

@api_router.get("/user/profile", response_model=UserResponse)
async def get_user_profile(user: User = Depends(get_current_user)):
    """Get current user profile"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        phone=user.phone,
        balance=user.balance,
        totalEarnings=user.total_earnings,
        monthlyReturn=user.monthly_return,
        biometricEnabled=user.biometric_enabled,
        termsAccepted=user.terms_accepted,
        termsAcceptedAt=user.terms_accepted_at,
        notificationPreferences=user.notification_preferences,
        paymentSchedule=user.payment_schedule
    )

@api_router.post("/user/accept-terms")
async def accept_terms(request: AcceptTermsRequest, user: User = Depends(get_current_user)):
    """Accept terms and conditions - creates legal log"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not request.lucrum_terms_accepted or not request.fidus_terms_accepted or not request.copy_trading_terms_accepted:
        raise HTTPException(status_code=400, detail="All three terms (LUCRUM, FIDUS, and Copy Trading) must be accepted")
    
    # Create acceptance log for legal records
    acceptance_log = TermsAcceptance(
        user_id=user.id,
        user_email=user.email,
        user_name=user.name,
        lucrum_terms_accepted=request.lucrum_terms_accepted,
        fidus_terms_accepted=request.fidus_terms_accepted,
        copy_trading_terms_accepted=request.copy_trading_terms_accepted,
        terms_version="1.0",
        ip_address=request.ip_address,
        user_agent=request.user_agent,
    )
    await db.terms_acceptances.insert_one(acceptance_log.dict())
    
    # Update user record
    now = datetime.utcnow()
    await db.users.update_one(
        {"id": user.id},
        {"$set": {"terms_accepted": True, "terms_accepted_at": now}}
    )
    
    logger.info(f"Terms accepted by user {user.email} at {now}")
    
    return {
        "success": True,
        "message": "Terms and conditions accepted",
        "acceptedAt": now.isoformat()
    }

@api_router.get("/admin/terms-acceptances", response_model=List[TermsAcceptanceLog])
async def get_terms_acceptances(
    limit: int = 100,
    offset: int = 0,
    user: User = Depends(get_current_user)
):
    """Get all terms acceptance logs (admin only)"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # In production, add admin role check here
    acceptances = await db.terms_acceptances.find().sort("accepted_at", -1).skip(offset).limit(limit).to_list(limit)
    
    return [
        TermsAcceptanceLog(
            id=a['id'],
            user_id=a['user_id'],
            user_email=a['user_email'],
            user_name=a['user_name'],
            lucrum_terms_accepted=a.get('lucrum_terms_accepted', False),
            fidus_terms_accepted=a.get('fidus_terms_accepted', False),
            copy_trading_terms_accepted=a.get('copy_trading_terms_accepted', False),
            terms_version=a['terms_version'],
            ip_address=a.get('ip_address'),
            user_agent=a.get('user_agent'),
            accepted_at=a['accepted_at']
        )
        for a in acceptances
    ]

@api_router.get("/admin/terms-acceptances/count")
async def get_terms_acceptances_count(user: User = Depends(get_current_user)):
    """Get total count of terms acceptances"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    count = await db.terms_acceptances.count_documents({})
    return {"count": count}

@api_router.put("/user/profile")
async def update_profile(request: UpdateProfileRequest, user: User = Depends(get_current_user)):
    """Update user profile"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    updates = {}
    if request.name:
        updates['name'] = request.name
    if request.phone:
        updates['phone'] = request.phone
    
    if updates:
        await db.users.update_one({"id": user.id}, {"$set": updates})
    
    return {"success": True, "message": "Profile updated successfully"}

@api_router.post("/user/change-password")
async def change_password(request: ChangePasswordRequest, user: User = Depends(get_current_user)):
    """Change user password"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if user.password_hash != hash_password(request.current_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    new_hash = hash_password(request.new_password)
    await db.users.update_one({"id": user.id}, {"$set": {"password_hash": new_hash}})
    
    return {"success": True, "message": "Password changed successfully"}

@api_router.put("/user/biometric")
async def toggle_biometric(enabled: bool, user: User = Depends(get_current_user)):
    """Enable/disable biometric authentication"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    await db.users.update_one({"id": user.id}, {"$set": {"biometric_enabled": enabled}})
    
    return {"success": True, "biometricEnabled": enabled}

@api_router.put("/user/notifications")
async def update_notification_preferences(
    request: UpdateNotificationPreferencesRequest, 
    user: User = Depends(get_current_user)
):
    """Update notification preferences"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    updates = {}
    if request.payment_reminders is not None:
        updates['notification_preferences.payment_reminders'] = request.payment_reminders
    if request.deposit_alerts is not None:
        updates['notification_preferences.deposit_alerts'] = request.deposit_alerts
    if request.monthly_reports is not None:
        updates['notification_preferences.monthly_reports'] = request.monthly_reports
    if request.push_enabled is not None:
        updates['notification_preferences.push_enabled'] = request.push_enabled
    
    if updates:
        await db.users.update_one({"id": user.id}, {"$set": updates})
    
    return {"success": True, "message": "Notification preferences updated"}

@api_router.post("/user/push-token")
async def register_push_token(request: RegisterPushTokenRequest, user: User = Depends(get_current_user)):
    """Register push notification token"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    await db.users.update_one({"id": user.id}, {"$set": {"push_token": request.push_token}})
    
    return {"success": True, "message": "Push token registered"}

@api_router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    limit: int = 50,
    offset: int = 0,
    type: Optional[str] = None,
    user: User = Depends(get_current_user)
):
    """Get user transaction history"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    query = {"user_id": user.id}
    if type:
        query["type"] = type
    
    transactions = await db.transactions.find(query).sort("created_at", -1).skip(offset).limit(limit).to_list(limit)
    
    return [
        TransactionResponse(
            id=tx['id'],
            type=tx['type'],
            amount=tx['amount'],
            description=tx['description'],
            status=tx['status'],
            createdAt=tx['created_at']
        )
        for tx in transactions
    ]

@api_router.get("/portfolio/history", response_model=List[PortfolioDataPoint])
async def get_portfolio_history(user: User = Depends(get_current_user)):
    """Get portfolio performance history"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return generate_portfolio_history(user.balance)

@api_router.post("/auth/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout and invalidate session"""
    if credentials:
        await db.sessions.delete_one({"token": credentials.credentials})
    return {"success": True, "message": "Logged out successfully"}

@api_router.get("/user/refresh")
async def refresh_user_data(user: User = Depends(get_current_user)):
    """Refresh user data with latest calculations"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Recalculate monthly return and payment schedule
    monthly_return = user.balance * 0.015
    payment_schedule = generate_payment_schedule(user.balance)
    
    # Update in database
    await db.users.update_one(
        {"id": user.id},
        {"$set": {
            "monthly_return": monthly_return,
            "payment_schedule": [ps.dict() for ps in payment_schedule]
        }}
    )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        phone=user.phone,
        balance=user.balance,
        totalEarnings=user.total_earnings,
        monthlyReturn=monthly_return,
        biometricEnabled=user.biometric_enabled,
        notificationPreferences=user.notification_preferences,
        paymentSchedule=payment_schedule
    )

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
