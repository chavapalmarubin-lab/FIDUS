"""
Franchise Admin Authentication API
March 2026 - FIDUS White Label Franchise System

Authentication endpoints for franchise company admins.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
from typing import Optional
import os
import logging
import hashlib
import secrets
import jwt

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/franchise/auth", tags=["Franchise Authentication"])

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'fidus-franchise-secret-key-2026')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Database connection
async def get_database():
    mongo_url = os.environ.get('MONGO_URL')
    if not mongo_url:
        raise HTTPException(status_code=500, detail="Database not configured")
    client = AsyncIOMotorClient(mongo_url)
    return client.fidus_production


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class FranchiseAdminCreate(BaseModel):
    company_id: str
    email: str
    password: str
    first_name: str
    last_name: str
    role: str = "admin"  # admin, manager, viewer


class FranchiseAdminLogin(BaseModel):
    email: str
    password: str
    company_code: Optional[str] = None  # Optional - can login with just email


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def hash_password(password: str) -> str:
    """Hash password with salt."""
    salt = "fidus_franchise_salt_2026"
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return hash_password(password) == hashed


def create_token(admin_data: dict) -> str:
    """Create JWT token for franchise admin."""
    payload = {
        "admin_id": admin_data["admin_id"],
        "company_id": admin_data["company_id"],
        "company_name": admin_data.get("company_name", ""),
        "company_code": admin_data.get("company_code", ""),
        "email": admin_data["email"],
        "role": admin_data.get("role", "admin"),
        "type": "franchise_admin",
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and verify JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "franchise_admin":
            raise HTTPException(status_code=401, detail="Invalid token type")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# =============================================================================
# AUTHENTICATION ENDPOINTS
# =============================================================================

@router.post("/register")
async def register_franchise_admin(admin: FranchiseAdminCreate):
    """
    Register a new admin for a franchise company.
    Only existing FIDUS admins or company super-admins can create new admins.
    """
    try:
        db = await get_database()
        
        # Verify company exists
        company = await db.franchise_companies.find_one({"company_id": admin.company_id})
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Check if email already exists for this company
        existing = await db.franchise_admins.find_one({
            "company_id": admin.company_id,
            "email": admin.email.lower()
        })
        if existing:
            raise HTTPException(status_code=400, detail="Admin with this email already exists")
        
        # Create admin
        import uuid
        admin_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        
        admin_doc = {
            "admin_id": admin_id,
            "company_id": admin.company_id,
            "email": admin.email.lower(),
            "password_hash": hash_password(admin.password),
            "first_name": admin.first_name,
            "last_name": admin.last_name,
            "role": admin.role,
            "status": "active",
            "last_login": None,
            "created_at": now,
            "updated_at": now
        }
        
        await db.franchise_admins.insert_one(admin_doc)
        
        # Update company's admin_users list
        await db.franchise_companies.update_one(
            {"company_id": admin.company_id},
            {"$addToSet": {"admin_users": admin_id}}
        )
        
        logger.info(f"✅ Registered franchise admin: {admin.email} for company {admin.company_id}")
        
        return {
            "success": True,
            "message": f"Admin {admin.first_name} {admin.last_name} registered",
            "admin_id": admin_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering franchise admin: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login")
async def login_franchise_admin(credentials: FranchiseAdminLogin):
    """
    Login for franchise company admin.
    Returns JWT token with company_id for multi-tenant filtering.
    """
    try:
        db = await get_database()
        
        # Find admin by email
        query = {"email": credentials.email.lower()}
        
        # If company_code provided, verify it matches
        if credentials.company_code:
            company = await db.franchise_companies.find_one({
                "company_code": credentials.company_code.lower()
            })
            if company:
                query["company_id"] = company["company_id"]
        
        admin = await db.franchise_admins.find_one(query)
        
        if not admin:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        if not verify_password(credentials.password, admin["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Check if admin is active
        if admin.get("status") != "active":
            raise HTTPException(status_code=401, detail="Account is not active")
        
        # Get company info
        company = await db.franchise_companies.find_one({"company_id": admin["company_id"]})
        if not company:
            raise HTTPException(status_code=401, detail="Company not found")
        
        if company.get("status") != "active":
            raise HTTPException(status_code=401, detail="Company account is suspended")
        
        # Update last login
        await db.franchise_admins.update_one(
            {"admin_id": admin["admin_id"]},
            {"$set": {"last_login": datetime.now(timezone.utc)}}
        )
        
        # Create token
        token_data = {
            "admin_id": admin["admin_id"],
            "company_id": admin["company_id"],
            "company_name": company.get("company_name", ""),
            "company_code": company.get("company_code", ""),
            "email": admin["email"],
            "role": admin.get("role", "admin")
        }
        
        token = create_token(token_data)
        
        logger.info(f"✅ Franchise admin login: {admin['email']} ({company.get('company_name')})")
        
        return {
            "success": True,
            "token": token,
            "admin": {
                "admin_id": admin["admin_id"],
                "email": admin["email"],
                "first_name": admin["first_name"],
                "last_name": admin["last_name"],
                "role": admin.get("role", "admin")
            },
            "company": {
                "company_id": company["company_id"],
                "company_name": company["company_name"],
                "company_code": company["company_code"],
                "subdomain": company.get("subdomain", ""),
                "logo_url": company.get("logo_url", ""),
                "primary_color": company.get("primary_color", "#0ea5e9"),
                "secondary_color": company.get("secondary_color", "#1e293b"),
                "commission_split": company.get("commission_split", {"company": 50, "agent": 50})
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in franchise admin login: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/verify")
async def verify_franchise_token(token: str):
    """
    Verify a franchise admin JWT token.
    """
    try:
        payload = decode_token(token)
        
        db = await get_database()
        
        # Get fresh admin and company data
        admin = await db.franchise_admins.find_one(
            {"admin_id": payload["admin_id"]},
            {"_id": 0, "password_hash": 0}
        )
        
        if not admin:
            raise HTTPException(status_code=401, detail="Admin not found")
        
        if admin.get("status") != "active":
            raise HTTPException(status_code=401, detail="Account is not active")
        
        company = await db.franchise_companies.find_one(
            {"company_id": payload["company_id"]},
            {"_id": 0}
        )
        
        if not company or company.get("status") != "active":
            raise HTTPException(status_code=401, detail="Company not active")
        
        return {
            "success": True,
            "valid": True,
            "admin": admin,
            "company": {
                "company_id": company["company_id"],
                "company_name": company["company_name"],
                "company_code": company["company_code"],
                "logo_url": company.get("logo_url", ""),
                "primary_color": company.get("primary_color", "#0ea5e9"),
                "secondary_color": company.get("secondary_color", "#1e293b")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying franchise token: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/change-password")
async def change_franchise_password(token: str, passwords: PasswordChange):
    """
    Change franchise admin password.
    """
    try:
        payload = decode_token(token)
        
        db = await get_database()
        
        admin = await db.franchise_admins.find_one({"admin_id": payload["admin_id"]})
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        
        # Verify current password
        if not verify_password(passwords.current_password, admin["password_hash"]):
            raise HTTPException(status_code=401, detail="Current password is incorrect")
        
        # Update password
        await db.franchise_admins.update_one(
            {"admin_id": payload["admin_id"]},
            {"$set": {
                "password_hash": hash_password(passwords.new_password),
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        return {
            "success": True,
            "message": "Password changed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing franchise password: {e}")
        raise HTTPException(status_code=500, detail=str(e))



# =============================================================================
# CLIENT AUTHENTICATION ENDPOINTS
# =============================================================================

class FranchiseClientLogin(BaseModel):
    email: str
    password: str


class FranchiseClientRegister(BaseModel):
    company_id: str
    client_id: str  # Existing client_id from franchise_clients
    email: str
    password: str


def create_client_token(client_data: dict) -> str:
    """Create JWT token for franchise client."""
    payload = {
        "client_id": client_data["client_id"],
        "company_id": client_data["company_id"],
        "company_name": client_data.get("company_name", ""),
        "email": client_data["email"],
        "type": "franchise_client",
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


@router.post("/client/register")
async def register_franchise_client_login(reg: FranchiseClientRegister):
    """Register login credentials for an existing franchise client."""
    try:
        db = await get_database()
        
        # Verify client exists
        client = await db.franchise_clients.find_one({"client_id": reg.client_id, "company_id": reg.company_id})
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Check if already registered
        existing = await db.franchise_client_logins.find_one({"client_id": reg.client_id})
        if existing:
            raise HTTPException(status_code=400, detail="Client login already exists")
        
        now = datetime.now(timezone.utc)
        login_doc = {
            "client_id": reg.client_id,
            "company_id": reg.company_id,
            "email": reg.email.lower(),
            "password_hash": hash_password(reg.password),
            "status": "active",
            "created_at": now,
            "updated_at": now
        }
        await db.franchise_client_logins.insert_one(login_doc)
        
        return {"success": True, "message": "Client login created"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering franchise client login: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/client/login")
async def login_franchise_client(credentials: FranchiseClientLogin):
    """Login for franchise client."""
    try:
        db = await get_database()
        
        login = await db.franchise_client_logins.find_one({"email": credentials.email.lower()})
        if not login or not verify_password(credentials.password, login["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        if login.get("status") != "active":
            raise HTTPException(status_code=401, detail="Account is not active")
        
        # Get client info
        client = await db.franchise_clients.find_one(
            {"client_id": login["client_id"]},
            {"_id": 0}
        )
        if not client:
            raise HTTPException(status_code=401, detail="Client record not found")
        
        # Get company info
        company = await db.franchise_companies.find_one(
            {"company_id": login["company_id"]},
            {"_id": 0}
        )
        if not company or company.get("status") != "active":
            raise HTTPException(status_code=401, detail="Company not active")
        
        # Update last login
        await db.franchise_client_logins.update_one(
            {"client_id": login["client_id"]},
            {"$set": {"last_login": datetime.now(timezone.utc)}}
        )
        
        token = create_client_token({
            "client_id": login["client_id"],
            "company_id": login["company_id"],
            "company_name": company.get("company_name", ""),
            "email": login["email"]
        })
        
        return {
            "success": True,
            "token": token,
            "client": {
                "client_id": client["client_id"],
                "first_name": client.get("first_name", ""),
                "last_name": client.get("last_name", ""),
                "email": login["email"],
                "status": client.get("status", "active")
            },
            "company": {
                "company_id": company["company_id"],
                "company_name": company["company_name"],
                "logo_url": company.get("logo_url", ""),
                "primary_color": company.get("primary_color", "#0ea5e9")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in franchise client login: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# AGENT AUTHENTICATION ENDPOINTS
# =============================================================================

class FranchiseAgentLogin(BaseModel):
    email: str
    password: str


class FranchiseAgentRegister(BaseModel):
    company_id: str
    agent_id: str  # Existing agent_id from franchise_referral_agents
    email: str
    password: str


def create_agent_token(agent_data: dict) -> str:
    """Create JWT token for franchise referral agent."""
    payload = {
        "agent_id": agent_data["agent_id"],
        "company_id": agent_data["company_id"],
        "company_name": agent_data.get("company_name", ""),
        "email": agent_data["email"],
        "type": "franchise_agent",
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


@router.post("/agent/register")
async def register_franchise_agent_login(reg: FranchiseAgentRegister):
    """Register login credentials for an existing franchise referral agent."""
    try:
        db = await get_database()
        
        agent = await db.franchise_referral_agents.find_one({"agent_id": reg.agent_id, "company_id": reg.company_id})
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        existing = await db.franchise_agent_logins.find_one({"agent_id": reg.agent_id})
        if existing:
            raise HTTPException(status_code=400, detail="Agent login already exists")
        
        now = datetime.now(timezone.utc)
        login_doc = {
            "agent_id": reg.agent_id,
            "company_id": reg.company_id,
            "email": reg.email.lower(),
            "password_hash": hash_password(reg.password),
            "status": "active",
            "created_at": now,
            "updated_at": now
        }
        await db.franchise_agent_logins.insert_one(login_doc)
        
        return {"success": True, "message": "Agent login created"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering franchise agent login: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent/login")
async def login_franchise_agent(credentials: FranchiseAgentLogin):
    """Login for franchise referral agent."""
    try:
        db = await get_database()
        
        login = await db.franchise_agent_logins.find_one({"email": credentials.email.lower()})
        if not login or not verify_password(credentials.password, login["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        if login.get("status") != "active":
            raise HTTPException(status_code=401, detail="Account is not active")
        
        agent = await db.franchise_referral_agents.find_one(
            {"agent_id": login["agent_id"]},
            {"_id": 0, "password_hash": 0}
        )
        if not agent:
            raise HTTPException(status_code=401, detail="Agent record not found")
        
        company = await db.franchise_companies.find_one(
            {"company_id": login["company_id"]},
            {"_id": 0}
        )
        if not company or company.get("status") != "active":
            raise HTTPException(status_code=401, detail="Company not active")
        
        await db.franchise_agent_logins.update_one(
            {"agent_id": login["agent_id"]},
            {"$set": {"last_login": datetime.now(timezone.utc)}}
        )
        
        token = create_agent_token({
            "agent_id": login["agent_id"],
            "company_id": login["company_id"],
            "company_name": company.get("company_name", ""),
            "email": login["email"]
        })
        
        return {
            "success": True,
            "token": token,
            "agent": {
                "agent_id": agent["agent_id"],
                "first_name": agent.get("first_name", ""),
                "last_name": agent.get("last_name", ""),
                "email": login["email"],
                "commission_tier": agent.get("commission_tier", 50)
            },
            "company": {
                "company_id": company["company_id"],
                "company_name": company["company_name"],
                "logo_url": company.get("logo_url", ""),
                "primary_color": company.get("primary_color", "#0ea5e9")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in franchise agent login: {e}")
        raise HTTPException(status_code=500, detail=str(e))
