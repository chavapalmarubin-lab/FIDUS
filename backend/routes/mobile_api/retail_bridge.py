"""
FIDUS Retail ↔ Morpho Bridge API
=================================
Provides the API endpoints that the FIDUS web dashboard (retail-dashboard.html) 
expects, backed by the existing retail_clients collection + live Morpho/LUCRUM data.

Endpoints:
  POST /api/auth/login        — Login (uses retail_clients collection)
  POST /api/auth/logout       — Logout
  GET  /api/user/profile      — Profile enriched with Morpho live data
  GET  /api/user/challenges   — Trading challenges from Morpho
  GET  /api/transactions      — Transaction history (Morpho deposits/withdrawals)
  POST /api/kyc/upload        — Upload KYC documents locally
  GET  /api/kyc/status        — KYC document upload status
  GET  /api/kyc/admin/pending — Admin: list pending KYC docs
"""

from fastapi import APIRouter, HTTPException, Header, UploadFile, File, Form
from fastapi.responses import FileResponse
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
from pathlib import Path
from typing import Optional
import os
import logging
import hashlib
import secrets
import uuid

logger = logging.getLogger(__name__)

# ── Router with /api prefix (matches what the web dashboard expects) ──
router = APIRouter(prefix="/api", tags=["Retail Morpho Bridge"])

# ── Auth Config ──
SALT = "fidus_retail_salt_2026"

# ── DB ──
_db = None
async def get_db():
    global _db
    if _db is None:
        client = AsyncIOMotorClient(os.environ.get("MONGO_URL"), serverSelectionTimeoutMS=10000)
        _db = client.fidus_production
    return _db

def _hash(pwd):
    return hashlib.sha256(f"{pwd}{SALT}".encode()).hexdigest()

def _gen_token():
    return secrets.token_urlsafe(32)

# ── Morpho Client (lazy import) ──
_morpho = None
def get_morpho():
    global _morpho
    if _morpho is None:
        try:
            from routes.mobile_api.morpho_client import MorphoClient
            key = os.environ.get("MORPHO_API_KEY", "")
            if key:
                _morpho = MorphoClient(api_key=key)
                logger.info("Morpho client initialized for retail bridge")
            else:
                logger.warning("MORPHO_API_KEY not set — Morpho features disabled")
        except Exception as e:
            logger.warning(f"Morpho client init failed: {e}")
    return _morpho


# ================================================================
# AUTH: Login / Logout
# ================================================================

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/auth/login")
async def login(request: LoginRequest):
    """Login using retail_clients collection."""
    db = await get_db()
    email = request.email.lower().strip()
    
    client = await db.retail_clients.find_one({"email": email, "status": "active"})
    if not client or client.get("password_hash") != _hash(request.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create session token
    token = _gen_token()
    session = {
        "token": token,
        "client_id": client["client_id"],
        "email": client["email"],
        "created_at": datetime.now(timezone.utc),
        "expires_at": datetime.now(timezone.utc) + timedelta(days=30),
    }
    await db.retail_sessions.insert_one(session)
    
    name = f"{client.get('first_name', '')} {client.get('last_name', '')}".strip()
    
    return {
        "success": True,
        "token": token,
        "user": {
            "id": client["client_id"],
            "email": client["email"],
            "name": name,
            "phone": client.get("phone", ""),
            "balance": client.get("balance", 0),
            "totalEarnings": client.get("total_returns", 0),
            "monthlyReturn": client.get("balance", 0) * 0.015,
            "biometricEnabled": False,
            "termsAccepted": True,
            "notificationPreferences": {},
            "paymentSchedule": [],
        }
    }


@router.post("/auth/logout")
async def logout(authorization: str = Header(None)):
    if authorization:
        token = authorization.replace("Bearer ", "")
        db = await get_db()
        await db.retail_sessions.delete_one({"token": token})
    return {"success": True, "message": "Logged out"}


# ── Helper: get current user from token ──
async def _get_user(authorization: str = None):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.replace("Bearer ", "")
    db = await get_db()
    session = await db.retail_sessions.find_one({"token": token})
    if not session:
        raise HTTPException(status_code=401, detail="Invalid token")
    if datetime.now(timezone.utc) > session.get("expires_at", datetime.min.replace(tzinfo=timezone.utc)):
        await db.retail_sessions.delete_one({"token": token})
        raise HTTPException(status_code=401, detail="Token expired")
    client = await db.retail_clients.find_one({"client_id": session["client_id"]})
    if not client:
        raise HTTPException(status_code=401, detail="User not found")
    return client, token


# ================================================================
# PROFILE (enriched with Morpho data)
# ================================================================

@router.get("/user/profile")
async def get_profile(authorization: str = Header(None)):
    client, token = await _get_user(authorization)
    
    name = f"{client.get('first_name', '')} {client.get('last_name', '')}".strip()
    balance = client.get("balance", 0)
    
    response = {
        "id": client["client_id"],
        "email": client["email"],
        "name": name,
        "phone": client.get("phone", ""),
        "balance": balance,
        "totalEarnings": client.get("total_returns", 0),
        "monthlyReturn": balance * 0.015,
        "biometricEnabled": False,
        "termsAccepted": True,
        "notificationPreferences": {},
        "paymentSchedule": [],
        "morpho": None,
        "data_source": "local",
    }
    
    # Enrich with Morpho data
    morpho = get_morpho()
    if morpho and morpho.is_configured:
        try:
            morpho_user = await morpho.find_user_by_email(client["email"])
            if morpho_user:
                user_uuid = morpho_user.get("uuid")
                full_user = await morpho.get_user(user_uuid)
                user_detail = full_user.get("data", morpho_user) if full_user else morpho_user
                
                from routes.mobile_api.morpho_client import MorphoClient
                mapped = MorphoClient.map_user_to_fidus(user_detail)
                
                accounts = await morpho.get_user_accounts(user_uuid)
                agg = MorphoClient.aggregate_account_balance(accounts) if accounts else None
                
                morpho_data = {
                    "user_uuid": user_uuid,
                    "balance": agg["total_balance"] if agg else 0,
                    "equity": agg["total_equity"] if agg else 0,
                    "margin": agg["total_margin"] if agg else 0,
                    "free_margin": agg["total_free_margin"] if agg else 0,
                    "account_count": agg["account_count"] if agg else 0,
                    "accounts": agg["accounts"] if agg else [],
                    "kyc": mapped.get("kyc", {}),
                    "activity": mapped.get("activity", {}),
                    "country": mapped.get("country", {}),
                    "is_verified": mapped.get("is_verified", False),
                    "introducer": mapped.get("introducer"),
                }
                
                response["morpho"] = morpho_data
                response["data_source"] = "morpho"
                if agg:
                    response["balance"] = agg["total_balance"]
                    response["monthlyReturn"] = agg["total_balance"] * 0.015
        except Exception as e:
            logger.warning(f"Morpho enrichment failed for {client['email']}: {e}")
    
    return response


# ================================================================
# CHALLENGES
# ================================================================

@router.get("/user/challenges")
async def get_challenges(authorization: str = Header(None)):
    client, _ = await _get_user(authorization)
    
    morpho = get_morpho()
    if not morpho or not morpho.is_configured:
        return {"configured": False, "challenges": [], "templates": []}
    
    try:
        morpho_user = await morpho.find_user_by_email(client["email"])
        if not morpho_user:
            return {"configured": True, "challenges": [], "templates": []}
        
        user_uuid = morpho_user.get("uuid")
        challenges_result = await morpho.list_challenges(user_uuid=user_uuid, limit=50)
        templates_result = await morpho.list_challenge_templates(active=True, visible=True, limit=20)
        
        challenges = []
        if challenges_result and challenges_result.get("data"):
            for ch in challenges_result["data"]:
                template = ch.get("template", {}) or {}
                rules = template.get("rules", {}) or {}
                account = ch.get("account", {}) or {}
                challenges.append({
                    "uuid": ch.get("uuid"),
                    "name": template.get("name", "Challenge"),
                    "status": ch.get("status", {}).get("name", "Unknown") if isinstance(ch.get("status"), dict) else str(ch.get("statusUuid", "Unknown")),
                    "profit_target": rules.get("profitTarget"),
                    "daily_loss_limit": rules.get("dailyLoss"),
                    "overall_loss_limit": rules.get("overallLoss"),
                    "account_balance": float(account.get("balance", 0)),
                    "account_equity": float(account.get("equity", 0)),
                    "account_id": account.get("username", ""),
                    "created_at": ch.get("createdAt"),
                })
        
        templates = []
        if templates_result and templates_result.get("data"):
            for t in templates_result["data"]:
                rules = t.get("rules", {}) or {}
                templates.append({
                    "uuid": t.get("uuid"),
                    "name": t.get("name", ""),
                    "description": t.get("description", ""),
                    "price": float(t.get("price", 0)),
                    "account_size": float(t.get("accountSize", 0)),
                    "leverage": t.get("leverage", ""),
                    "profit_target": rules.get("profitTarget"),
                    "daily_loss_limit": rules.get("dailyLoss"),
                    "overall_loss_limit": rules.get("overallLoss"),
                    "is_active": t.get("isActive", False),
                })
        
        return {"configured": True, "challenges": challenges, "templates": templates, "user_uuid": user_uuid}
    except Exception as e:
        logger.warning(f"Challenges fetch failed for {client['email']}: {e}")
        return {"configured": True, "challenges": [], "templates": [], "error": str(e)}


# ================================================================
# TRANSACTIONS
# ================================================================

@router.get("/transactions")
async def get_transactions(authorization: str = Header(None), limit: int = 50):
    client, _ = await _get_user(authorization)
    
    morpho = get_morpho()
    if morpho and morpho.is_configured:
        try:
            morpho_user = await morpho.find_user_by_email(client["email"])
            if morpho_user:
                user_uuid = morpho_user.get("uuid")
                from routes.mobile_api.morpho_client import MorphoClient
                transactions = []
                
                deposits = await morpho.get_user_deposits(user_uuid, limit=limit)
                if deposits:
                    for d in deposits:
                        mapped = MorphoClient.map_deposit_to_transaction(d)
                        transactions.append({
                            "id": mapped["id"],
                            "type": mapped["type"],
                            "amount": mapped["amount"],
                            "description": mapped["description"],
                            "status": mapped["status"],
                            "createdAt": mapped.get("created_at"),
                        })
                
                withdrawals = await morpho.get_user_withdrawals(user_uuid, limit=limit)
                if withdrawals:
                    for w in withdrawals:
                        mapped = MorphoClient.map_withdrawal_to_transaction(w)
                        transactions.append({
                            "id": mapped["id"],
                            "type": mapped["type"],
                            "amount": mapped["amount"],
                            "description": mapped["description"],
                            "status": mapped["status"],
                            "createdAt": mapped.get("created_at"),
                        })
                
                transactions.sort(key=lambda t: t.get("createdAt") or "", reverse=True)
                return transactions[:limit]
        except Exception as e:
            logger.warning(f"Morpho transactions failed for {client['email']}: {e}")
    
    return []


# ================================================================
# KYC Document Upload
# ================================================================

UPLOAD_DIR = Path(os.environ.get("KYC_UPLOAD_DIR", "/tmp/kyc_uploads"))
UPLOAD_DIR.mkdir(exist_ok=True)
DOC_TYPES = {"id_document", "proof_of_residence"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf", ".heic", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024


async def _get_user_by_token(token: str):
    db = await get_db()
    session = await db.retail_sessions.find_one({"token": token})
    if not session:
        return None
    client = await db.retail_clients.find_one({"client_id": session["client_id"]})
    return client


@router.post("/kyc/upload")
async def upload_kyc_doc(
    file: UploadFile = File(...),
    doc_type: str = Form(...),
    token: str = Form(...),
):
    client = await _get_user_by_token(token)
    if not client:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if doc_type not in DOC_TYPES:
        raise HTTPException(status_code=422, detail=f"Invalid doc type. Must be: {', '.join(DOC_TYPES)}")
    
    filename = file.filename or "document"
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=422, detail=f"File type not allowed. Accepted: {', '.join(ALLOWED_EXTENSIONS)}")
    
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=422, detail="File too large. Max 10 MB.")
    
    user_dir = UPLOAD_DIR / client["client_id"]
    user_dir.mkdir(exist_ok=True)
    
    file_id = str(uuid.uuid4())[:8]
    safe_name = f"{doc_type}_{file_id}{ext}"
    (user_dir / safe_name).write_bytes(contents)
    
    db = await get_db()
    name = f"{client.get('first_name', '')} {client.get('last_name', '')}".strip()
    doc_record = {
        "id": str(uuid.uuid4()),
        "user_id": client["client_id"],
        "user_email": client["email"],
        "user_name": name,
        "doc_type": doc_type,
        "original_filename": filename,
        "stored_filename": safe_name,
        "file_size": len(contents),
        "file_extension": ext,
        "status": "pending_review",
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }
    
    await db.kyc_documents.delete_many({"user_id": client["client_id"], "doc_type": doc_type})
    await db.kyc_documents.insert_one(doc_record)
    
    logger.info(f"KYC uploaded: {client['email']} / {doc_type} / {safe_name}")
    
    return {
        "success": True,
        "message": "Document uploaded successfully",
        "document": {
            "id": doc_record["id"],
            "doc_type": doc_type,
            "filename": filename,
            "size": len(contents),
            "status": "pending_review",
            "uploaded_at": doc_record["uploaded_at"],
        }
    }


@router.get("/kyc/status")
async def kyc_status(token: str):
    client = await _get_user_by_token(token)
    if not client:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    db = await get_db()
    docs = await db.kyc_documents.find({"user_id": client["client_id"]}).to_list(10)
    
    documents = {}
    for doc in docs:
        documents[doc["doc_type"]] = {
            "id": doc["id"],
            "doc_type": doc["doc_type"],
            "original_filename": doc["original_filename"],
            "status": doc["status"],
            "uploaded_at": doc["uploaded_at"],
            "file_size": doc["file_size"],
        }
    
    return {
        "user_id": client["client_id"],
        "user_email": client["email"],
        "documents": documents,
        "id_document_uploaded": "id_document" in documents,
        "proof_of_residence_uploaded": "proof_of_residence" in documents,
        "all_uploaded": "id_document" in documents and "proof_of_residence" in documents,
    }


@router.get("/kyc/admin/pending")
async def admin_pending_kyc():
    db = await get_db()
    docs = await db.kyc_documents.find({}).sort("uploaded_at", -1).to_list(200)
    
    users_map = {}
    for doc in docs:
        uid = doc["user_id"]
        if uid not in users_map:
            users_map[uid] = {
                "user_id": uid,
                "user_email": doc.get("user_email", ""),
                "user_name": doc.get("user_name", ""),
                "documents": [],
            }
        users_map[uid]["documents"].append({
            "id": doc["id"],
            "doc_type": doc["doc_type"],
            "original_filename": doc["original_filename"],
            "status": doc["status"],
            "uploaded_at": doc["uploaded_at"],
            "file_size": doc["file_size"],
        })
    
    return {
        "total_users": len(users_map),
        "total_documents": len(docs),
        "users": list(users_map.values()),
    }


# ================================================================
# HEALTH
# ================================================================

@router.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}
