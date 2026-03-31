"""
FIDUS Retail — Backend API
Client registration, login, dashboard, payment calendar.
Product: FIDUS CORE 1.5% monthly, no lock-in, minimum $100.
"""

from fastapi import APIRouter, HTTPException, Header
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
import os, logging, hashlib, jwt, uuid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/retail", tags=["Retail"])

JWT_SECRET = os.environ.get("JWT_SECRET", "fidus-retail-secret-2026")
SALT = "fidus_retail_salt_2026"


_db = None
async def get_db():
    global _db
    if _db is None:
        client = AsyncIOMotorClient(os.environ.get("MONGO_URL"), serverSelectionTimeoutMS=10000)
        _db = client.fidus_production
    return _db


def _hash(pwd):
    return hashlib.sha256(f"{pwd}{SALT}".encode()).hexdigest()


def _token(data: dict) -> str:
    payload = {**data, "type": "retail_client", "exp": datetime.now(timezone.utc) + timedelta(hours=48)}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def _decode(authorization: str) -> dict:
    if not authorization:
        raise HTTPException(status_code=401, detail="Auth required")
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        if payload.get("type") != "retail_client":
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


class RetailLogin(BaseModel):
    email: str
    password: str


class RetailRegister(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    phone: str = ""
    lucrum_account: str = ""


@router.post("/register")
async def register_retail_client(reg: RetailRegister):
    """Register a new retail client."""
    db = await get_db()
    existing = await db.retail_clients.find_one({"email": reg.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    now = datetime.now(timezone.utc)
    client_id = str(uuid.uuid4())
    doc = {
        "client_id": client_id,
        "first_name": reg.first_name,
        "last_name": reg.last_name,
        "email": reg.email.lower(),
        "password_hash": _hash(reg.password),
        "phone": reg.phone,
        "lucrum_account": reg.lucrum_account,
        "balance": 0,
        "total_deposited": 0,
        "total_returns": 0,
        "product": "FIDUS_CORE",
        "return_rate": 1.5,
        "status": "active",
        "created_at": now,
        "updated_at": now
    }
    await db.retail_clients.insert_one(doc)
    return {"success": True, "client_id": client_id, "message": "Account created"}


@router.post("/login")
async def login_retail(creds: RetailLogin):
    """Login for retail clients."""
    db = await get_db()
    client = await db.retail_clients.find_one({"email": creds.email.lower(), "status": "active"})
    if not client or client.get("password_hash") != _hash(creds.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    await db.retail_clients.update_one(
        {"client_id": client["client_id"]},
        {"$set": {"last_login": datetime.now(timezone.utc)}}
    )

    token = _token({
        "client_id": client["client_id"],
        "email": client["email"],
        "name": f"{client['first_name']} {client['last_name']}"
    })

    return {
        "success": True,
        "token": token,
        "client": {
            "client_id": client["client_id"],
            "first_name": client["first_name"],
            "last_name": client["last_name"],
            "email": client["email"],
            "name": f"{client['first_name']} {client['last_name']}"
        }
    }


@router.get("/dashboard")
async def get_retail_dashboard(authorization: str = Header(None)):
    """Retail client dashboard — balance, returns, payment calendar."""
    payload = _decode(authorization)
    db = await get_db()

    client = await db.retail_clients.find_one(
        {"client_id": payload["client_id"]},
        {"_id": 0, "password_hash": 0}
    )
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    balance = client.get("balance", 0)
    rate = client.get("return_rate", 1.5) / 100
    monthly = balance * rate
    total_returns = client.get("total_returns", 0)

    # Payment schedule (next 12 months)
    now = datetime.now(timezone.utc)
    payments = []
    for i in range(12):
        from dateutil.relativedelta import relativedelta
        pay_date = now + relativedelta(months=i+1, day=28)
        payments.append({
            "month": pay_date.strftime("%Y-%m"),
            "date": pay_date.strftime("%B %d, %Y"),
            "amount": round(monthly, 2),
            "status": "projected"
        })

    # Fund health
    fund_health = []
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')}/api/public/fund-health-calendar") as resp:
                data = await resp.json()
                fund_health = data.get("months", [])
    except:
        fund_health = []

    return {
        "success": True,
        "client": {
            "first_name": client.get("first_name"),
            "last_name": client.get("last_name"),
            "email": client.get("email"),
            "name": f"{client.get('first_name', '')} {client.get('last_name', '')}",
            "product": client.get("product", "FIDUS_CORE"),
            "status": client.get("status"),
        },
        "balance": balance,
        "total_returns": total_returns,
        "total_deposited": client.get("total_deposited", 0),
        "monthly_return": round(monthly, 2),
        "return_rate": client.get("return_rate", 1.5),
        "payments": payments,
        "fund_health": fund_health
    }



# ═══════════════════════════════════════════
# RETAIL ADMIN ENDPOINTS
# ═══════════════════════════════════════════

ADMIN_JWT_SECRET = os.environ.get("JWT_SECRET", "fidus-retail-admin-2026")


class RetailAdminLogin(BaseModel):
    email: str
    password: str


def _admin_token(data: dict) -> str:
    payload = {**data, "type": "retail_admin", "exp": datetime.now(timezone.utc) + timedelta(hours=24)}
    return jwt.encode(payload, ADMIN_JWT_SECRET, algorithm="HS256")


def _decode_admin(authorization: str) -> dict:
    if not authorization:
        raise HTTPException(status_code=401, detail="Auth required")
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, ADMIN_JWT_SECRET, algorithms=["HS256"])
        if payload.get("type") != "retail_admin":
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/admin/login")
async def login_retail_admin(creds: RetailAdminLogin):
    """Login for retail admin."""
    db = await get_db()
    admin = await db.retail_admins.find_one({"email": creds.email.lower(), "status": "active"})
    if not admin or admin.get("password_hash") != _hash(creds.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = _admin_token({"admin_id": admin.get("admin_id", ""), "email": admin["email"], "name": admin.get("name", "")})
    return {
        "success": True,
        "token": token,
        "admin": {"name": admin.get("name", ""), "email": admin["email"]}
    }


@router.get("/admin/dashboard")
async def get_retail_admin_dashboard(authorization: str = Header(None)):
    """Full admin dashboard — all clients, AUM, calendar, fund performance from 2210."""
    _decode_admin(authorization)
    db = await get_db()

    clients = await db.retail_clients.find(
        {}, {"_id": 0, "password_hash": 0}
    ).sort("balance", -1).to_list(1000)

    # Keep datetime objects for calculations, serialize later

    total_aum = sum(c.get("balance", 0) for c in clients)
    all_clients = [c for c in clients if c.get("status") in ("active", "incubation")]
    active = [c for c in clients if c.get("status") == "active"]
    incubation = [c for c in clients if c.get("status") == "incubation"]
    monthly_client_payout = total_aum * 0.015
    avg_bal = total_aum / len(clients) if clients else 0

    # ── FUND PERFORMANCE from Account 2210 (FIDUS DEMO) ──
    # Apply 2210's daily RETURN RATES to retail AUM (not raw P&L)
    acc_2210 = await db.mt5_accounts.find_one({"account": 2210}, {"_id": 0, "equity": 1, "initial_allocation": 1, "allocation_start_date": 1})
    fund_equity = float(acc_2210.get("equity", 0)) if acc_2210 else 0
    fund_initial = float(acc_2210.get("initial_allocation", 0)) if acc_2210 else 0
    fund_pnl = fund_equity - fund_initial if fund_initial > 0 else 0
    fund_return_pct = (fund_pnl / fund_initial * 100) if fund_initial > 0 else 0

    # Get daily P&L from 2210 to compute daily return rates
    alloc_date_2210 = acc_2210.get("allocation_start_date") if acc_2210 else None
    if alloc_date_2210 and hasattr(alloc_date_2210, 'tzinfo') and alloc_date_2210.tzinfo is None:
        alloc_date_2210 = alloc_date_2210.replace(tzinfo=timezone.utc)
    since_2210 = alloc_date_2210 or datetime(2026, 3, 23, 0, 0, 0, tzinfo=timezone.utc)

    daily_pipeline = [
        {"$match": {"account": 2210, "type": {"$ne": 2}, "time": {"$gte": since_2210}}},
        {"$addFields": {"day": {"$dateToString": {"format": "%Y-%m-%d", "date": "$time"}}}},
        {"$group": {"_id": "$day", "daily_pnl": {"$sum": "$profit"}}},
        {"$sort": {"_id": 1}}
    ]
    daily_data = list(await db.mt5_deals_history.aggregate(daily_pipeline).to_list(100))

    # Apply 2210's daily rates to retail AUM
    running_2210 = fund_initial
    retail_running = total_aum
    retail_total_pnl = 0
    daily_retail = []
    for d in daily_data:
        rate = float(d["daily_pnl"]) / running_2210 if running_2210 > 0 else 0
        running_2210 += float(d["daily_pnl"])
        retail_daily_pnl = retail_running * rate
        retail_running += retail_daily_pnl
        retail_total_pnl += retail_daily_pnl
        daily_retail.append({"date": d["_id"], "rate_pct": round(rate * 100, 4), "retail_pnl": round(retail_daily_pnl, 2), "retail_equity": round(retail_running, 2)})

    # Performance fee on RETAIL gains (not 2210 gains)
    performance_fee_pct = 30
    performance_fee = retail_total_pnl * (performance_fee_pct / 100) if retail_total_pnl > 0 else 0
    net_after_perf_fee = retail_total_pnl - performance_fee
    client_payout = total_aum * 0.015  # 1.5% monthly to clients
    fidus_revenue = net_after_perf_fee - client_payout if net_after_perf_fee > client_payout else max(0, net_after_perf_fee)

    # Safely compute days_since_start
    alloc_date = acc_2210.get("allocation_start_date") if acc_2210 else None
    if alloc_date and hasattr(alloc_date, 'tzinfo') and alloc_date.tzinfo is None:
        alloc_date = alloc_date.replace(tzinfo=timezone.utc)
    days_since = (datetime.now(timezone.utc) - alloc_date).days if alloc_date else 0

    fund_performance = {
        "source_account": 2210,
        "source_name": "FIDUS DEMO",
        "fund_equity": round(fund_equity, 2),
        "fund_initial": round(fund_initial, 2),
        "fund_pnl": round(fund_pnl, 2),
        "fund_return_pct": round(fund_return_pct, 2),
        "retail_aum": round(total_aum, 2),
        "retail_gross_return": round(retail_total_pnl, 2),
        "retail_equity": round(retail_running, 2),
        "retail_return_pct": round((retail_total_pnl / total_aum * 100) if total_aum > 0 else 0, 2),
        "performance_fee_pct": performance_fee_pct,
        "performance_fee": round(performance_fee, 2),
        "net_after_fee": round(net_after_perf_fee, 2),
        "client_payout_monthly": round(client_payout, 2),
        "fidus_net_revenue": round(fidus_revenue, 2),
        "days_since_start": days_since,
        "daily_performance": daily_retail,
    }

    # Payment calendar (next 12 months) — include incubation clients after their incubation ends
    from dateutil.relativedelta import relativedelta
    now = datetime.now(timezone.utc)
    calendar = []
    for i in range(12):
        pay_date = now + relativedelta(months=i + 1, day=28)
        month_clients = []
        month_total = 0
        for c in all_clients:
            bal = c.get("balance", 0)
            if bal <= 0:
                continue
            # Check if incubation has ended by this payment date
            inc_end = c.get("incubation_end_date")
            if inc_end:
                if isinstance(inc_end, str):
                    inc_end = datetime.fromisoformat(inc_end.replace('Z', '+00:00'))
                if inc_end.tzinfo is None:
                    inc_end = inc_end.replace(tzinfo=timezone.utc)
                if pay_date < inc_end:
                    continue  # Still in incubation
            amt = bal * 0.015
            month_total += amt
            month_clients.append({"name": f"{c.get('first_name','')} {c.get('last_name','')}", "amount": round(amt, 2), "balance": bal})

        calendar.append({
            "month": pay_date.strftime("%Y-%m"),
            "month_name": pay_date.strftime("%B %Y"),
            "pay_date": pay_date.strftime("%B %d, %Y"),
            "total_due": round(month_total, 2),
            "client_count": len(month_clients),
            "aum": total_aum,
            "clients": sorted(month_clients, key=lambda x: x["amount"], reverse=True)
        })

        calendar.append({
            "month": pay_date.strftime("%Y-%m"),
            "month_name": pay_date.strftime("%B %Y"),
            "pay_date": pay_date.strftime("%B %d, %Y"),
            "total_due": round(month_total, 2),
            "client_count": len(month_clients),
            "aum": total_aum,
            "clients": sorted(month_clients, key=lambda x: x["amount"], reverse=True)
        })

    # Serialize datetime fields in clients before returning
    for cl in clients:
        for k in list(cl.keys()):
            if isinstance(cl[k], datetime):
                cl[k] = cl[k].isoformat()

    return {
        "success": True,
        "stats": {
            "total_aum": total_aum,
            "total_clients": len(clients),
            "active_clients": len(active),
            "incubation_clients": len(incubation),
            "monthly_revenue": round(monthly_client_payout, 2),
            "avg_balance": round(avg_bal, 2)
        },
        "fund_performance": fund_performance,
        "clients": clients,
        "payment_calendar": calendar
    }


class AddRetailClient(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str = ""
    password: str
    balance: float = 0


@router.post("/admin/add-client")
async def admin_add_retail_client(req: AddRetailClient, authorization: str = Header(None)):
    """Admin adds a retail client with balance."""
    _decode_admin(authorization)
    db = await get_db()

    existing = await db.retail_clients.find_one({"email": req.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    now = datetime.now(timezone.utc)
    client_id = str(uuid.uuid4())
    doc = {
        "client_id": client_id,
        "first_name": req.first_name,
        "last_name": req.last_name,
        "email": req.email.lower(),
        "password_hash": _hash(req.password),
        "phone": req.phone,
        "balance": req.balance,
        "total_deposited": req.balance,
        "total_returns": 0,
        "product": "FIDUS_CORE",
        "return_rate": 1.5,
        "status": "active",
        "created_at": now,
        "updated_at": now
    }
    await db.retail_clients.insert_one(doc)

    return {
        "success": True,
        "client_id": client_id,
        "email": req.email.lower(),
        "password": req.password,
        "message": f"Client {req.first_name} {req.last_name} added"
    }
