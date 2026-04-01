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

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    password_hash: str
    name: str
    balance: float = 5000.0
    total_earnings: float = 225.0
    monthly_return: float = 75.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    payment_schedule: List[PaymentScheduleItem] = []

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    balance: float
    totalEarnings: float
    monthlyReturn: float
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
            balance=balance,
            total_earnings=225.0,
            monthly_return=balance * 0.015,
            payment_schedule=generate_payment_schedule(balance)
        )
        await db.users.insert_one(demo_user.dict())
        logger.info(f"Demo user created: {demo_email}")
    else:
        # Update existing user with payment schedule if missing
        if not existing.get('payment_schedule'):
            balance = existing.get('balance', 5000.0)
            await db.users.update_one(
                {"email": demo_email},
                {"$set": {
                    "payment_schedule": [ps.dict() for ps in generate_payment_schedule(balance)]
                }}
            )
            logger.info(f"Updated demo user payment schedule")

@app.on_event("startup")
async def startup_event():
    await init_demo_user()
    logger.info("FIDUS API started successfully")

# ===== API Routes =====

@api_router.get("/")
async def root():
    return {"message": "FIDUS Investment App API", "version": "1.0.0"}

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
            balance=user.balance,
            totalEarnings=user.total_earnings,
            monthlyReturn=user.monthly_return,
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
        balance=user.balance,
        totalEarnings=user.total_earnings,
        monthlyReturn=user.monthly_return,
        paymentSchedule=user.payment_schedule
    )

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
        balance=user.balance,
        totalEarnings=user.total_earnings,
        monthlyReturn=monthly_return,
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
