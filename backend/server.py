from fastapi import FastAPI, APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import random

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

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

def calculate_balances(transactions: List[dict]) -> dict:
    """Calculate balances from transactions"""
    balances = {"fidus_funds": 0, "core_balance": 0, "dynamic_balance": 0}
    
    for trans in transactions:
        fund_type = trans["fund_type"]
        amount = trans["amount"]
        
        if fund_type == "fidus":
            balances["fidus_funds"] += amount
        elif fund_type == "core":
            balances["core_balance"] += amount
        elif fund_type == "dynamic":
            balances["dynamic_balance"] += amount
    
    # Add base amounts to make realistic
    balances["fidus_funds"] += 124567
    balances["core_balance"] += 275376.44
    balances["dynamic_balance"] += 150000.00
    
    balances["total_balance"] = sum(balances.values())
    
    return balances

# Authentication endpoints
@api_router.post("/auth/login", response_model=UserResponse)
async def login(login_data: LoginRequest):
    """Simple authentication - in production, use proper password hashing"""
    username = login_data.username
    password = login_data.password
    user_type = login_data.user_type
    
    # Simple demo authentication
    if username in MOCK_USERS and password == "password123":
        user_data = MOCK_USERS[username]
        if user_data["type"] == user_type:
            return UserResponse(**user_data)
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Client endpoints
@api_router.get("/client/{client_id}/data", response_model=ClientData)
async def get_client_data(client_id: str):
    """Get complete client data including balance, transactions, and monthly statement"""
    if client_id not in [user["id"] for user in MOCK_USERS.values() if user["type"] == "client"]:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Generate or retrieve transactions
    transactions = generate_mock_transactions(client_id)
    balances = calculate_balances(transactions)
    
    # Create balance object
    client_balance = ClientBalance(
        client_id=client_id,
        **balances
    )
    
    # Generate monthly statement
    monthly_statement = MonthlyStatement(
        month="April 2024",
        initial_balance=320041.96,
        profit=51.19,
        profit_percentage=51.19,
        final_balance=332681.44
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
            balances = calculate_balances(transactions)
            clients.append({
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "total_balance": balances["total_balance"],
                "last_activity": transactions[0]["date"] if transactions else datetime.now(timezone.utc)
            })
    
    return {"clients": clients}

@api_router.get("/admin/portfolio-summary")
async def get_portfolio_summary():
    """Get portfolio summary for admin dashboard"""
    total_aum = 2500000  # Mock AUM
    allocation = {
        "CORE": 33.33,
        "BALANCE": 33.33, 
        "DYNAMIC": 33.34
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

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()