"""
Morpho API Routes for FIDUS App
================================
These routes proxy requests to the Morpho API and transform
the responses into a format the FIDUS mobile app understands.

All routes are prefixed under /api/morpho/...
When the MORPHO_API_KEY is not configured, endpoints return
{"configured": false} so the frontend can fall back gracefully.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
from datetime import datetime
import logging

from morpho_client import morpho, MorphoClient

logger = logging.getLogger(__name__)
morpho_router = APIRouter(prefix="/morpho")


# ------------------------------------------------------------------ #
#  Status & Health
# ------------------------------------------------------------------ #

@morpho_router.get("/status")
async def morpho_status():
    """
    Check if Morpho API integration is configured and reachable.
    Returns configuration status and optionally tests connectivity.
    """
    configured = morpho.is_configured
    result = {
        "configured": configured,
        "base_url": morpho.base_url if configured else None,
    }

    if configured:
        # Try a lightweight API call to verify connectivity
        try:
            test = await morpho.list_users(page=1, limit=1)
            result["connected"] = test is not None
            if test and "meta" in test:
                result["total_users"] = test["meta"].get("total", 0)
        except Exception as e:
            result["connected"] = False
            result["error"] = str(e)
    else:
        result["connected"] = False
        result["message"] = "MORPHO_API_KEY not configured. Add it to backend/.env to enable Lucrum integration."

    return result


# ------------------------------------------------------------------ #
#  User Lookup
# ------------------------------------------------------------------ #

@morpho_router.get("/user/lookup")
async def lookup_morpho_user(
    email: Optional[str] = Query(None, description="User email to look up"),
    uuid: Optional[str] = Query(None, description="Morpho user UUID"),
):
    """
    Look up a user in Morpho by email or UUID.
    Maps the response to FIDUS-compatible format.
    """
    if not morpho.is_configured:
        return {"configured": False, "data": None}

    if uuid:
        raw = await morpho.get_user(uuid)
        if raw and "data" in raw:
            return {
                "configured": True,
                "data": MorphoClient.map_user_to_fidus(raw["data"]),
                "raw": raw["data"],
            }
    elif email:
        user = await morpho.find_user_by_email(email)
        if user:
            return {
                "configured": True,
                "data": MorphoClient.map_user_to_fidus(user),
                "raw": user,
            }

    return {"configured": True, "data": None, "message": "User not found"}


# ------------------------------------------------------------------ #
#  Accounts (Balance, Equity, Margin)
# ------------------------------------------------------------------ #

@morpho_router.get("/accounts")
async def get_morpho_accounts(
    user_uuid: Optional[str] = Query(None, description="Morpho user UUID"),
    email: Optional[str] = Query(None, description="User email to look up accounts for"),
):
    """
    Get trading accounts from Morpho.
    Can look up by Morpho user UUID or by email (will resolve UUID first).
    Returns aggregated balance across all accounts.
    """
    if not morpho.is_configured:
        return {"configured": False, "data": None}

    # Resolve user UUID from email if needed
    resolved_uuid = user_uuid
    if not resolved_uuid and email:
        user = await morpho.find_user_by_email(email)
        if user:
            resolved_uuid = user.get("uuid")

    if not resolved_uuid:
        return {"configured": True, "data": None, "message": "User not found"}

    accounts = await morpho.get_user_accounts(resolved_uuid)
    if accounts is None:
        return {"configured": True, "data": None, "message": "Could not fetch accounts"}

    aggregated = MorphoClient.aggregate_account_balance(accounts)
    return {
        "configured": True,
        "data": aggregated,
        "user_uuid": resolved_uuid,
    }


# ------------------------------------------------------------------ #
#  Deposits
# ------------------------------------------------------------------ #

@morpho_router.get("/deposits")
async def get_morpho_deposits(
    user_uuid: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
):
    """
    Get deposit history from Morpho.
    Returns deposits mapped to FIDUS transaction format.
    """
    if not morpho.is_configured:
        return {"configured": False, "data": None}

    resolved_uuid = user_uuid
    if not resolved_uuid and email:
        user = await morpho.find_user_by_email(email)
        if user:
            resolved_uuid = user.get("uuid")

    if not resolved_uuid:
        return {"configured": True, "data": None, "message": "User not found"}

    result = await morpho.list_deposits(
        user_uuid=resolved_uuid, status=status, page=page, limit=limit
    )
    if result is None:
        return {"configured": True, "data": None, "message": "Could not fetch deposits"}

    deposits = result.get("data", [])
    mapped = [MorphoClient.map_deposit_to_transaction(d) for d in deposits]

    return {
        "configured": True,
        "data": mapped,
        "meta": result.get("meta", {}),
        "user_uuid": resolved_uuid,
    }


# ------------------------------------------------------------------ #
#  Withdrawals
# ------------------------------------------------------------------ #

@morpho_router.get("/withdrawals")
async def get_morpho_withdrawals(
    user_uuid: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
):
    """
    Get withdrawal history from Morpho.
    Returns withdrawals mapped to FIDUS transaction format.
    """
    if not morpho.is_configured:
        return {"configured": False, "data": None}

    resolved_uuid = user_uuid
    if not resolved_uuid and email:
        user = await morpho.find_user_by_email(email)
        if user:
            resolved_uuid = user.get("uuid")

    if not resolved_uuid:
        return {"configured": True, "data": None, "message": "User not found"}

    result = await morpho.list_withdrawals(
        user_uuid=resolved_uuid, status=status, page=page, limit=limit
    )
    if result is None:
        return {"configured": True, "data": None, "message": "Could not fetch withdrawals"}

    withdrawals = result.get("data", [])
    mapped = [MorphoClient.map_withdrawal_to_transaction(w) for w in withdrawals]

    return {
        "configured": True,
        "data": mapped,
        "meta": result.get("meta", {}),
        "user_uuid": resolved_uuid,
    }


# ------------------------------------------------------------------ #
#  Combined Transactions (Deposits + Withdrawals merged & sorted)
# ------------------------------------------------------------------ #

@morpho_router.get("/transactions")
async def get_morpho_transactions(
    user_uuid: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
):
    """
    Get combined deposits + withdrawals from Morpho, sorted by date descending.
    This replaces the mock transaction list when Morpho is configured.
    """
    if not morpho.is_configured:
        return {"configured": False, "data": None}

    resolved_uuid = user_uuid
    if not resolved_uuid and email:
        user = await morpho.find_user_by_email(email)
        if user:
            resolved_uuid = user.get("uuid")

    if not resolved_uuid:
        return {"configured": True, "data": None, "message": "User not found"}

    # Fetch both deposits and withdrawals
    deposits_result = await morpho.list_deposits(user_uuid=resolved_uuid, limit=limit)
    withdrawals_result = await morpho.list_withdrawals(user_uuid=resolved_uuid, limit=limit)

    transactions = []

    if deposits_result and "data" in deposits_result:
        for d in deposits_result["data"]:
            transactions.append(MorphoClient.map_deposit_to_transaction(d))

    if withdrawals_result and "data" in withdrawals_result:
        for w in withdrawals_result["data"]:
            transactions.append(MorphoClient.map_withdrawal_to_transaction(w))

    # Sort by created_at descending
    transactions.sort(
        key=lambda t: t.get("created_at", ""),
        reverse=True,
    )

    return {
        "configured": True,
        "data": transactions[:limit],
        "total_deposits": len(deposits_result.get("data", [])) if deposits_result else 0,
        "total_withdrawals": len(withdrawals_result.get("data", [])) if withdrawals_result else 0,
        "user_uuid": resolved_uuid,
    }


# ------------------------------------------------------------------ #
#  Challenges
# ------------------------------------------------------------------ #

@morpho_router.get("/challenges")
async def get_morpho_challenges(
    user_uuid: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
):
    """
    Get trading challenges from Morpho for a user.
    """
    if not morpho.is_configured:
        return {"configured": False, "data": None}

    resolved_uuid = user_uuid
    if not resolved_uuid and email:
        user = await morpho.find_user_by_email(email)
        if user:
            resolved_uuid = user.get("uuid")

    if not resolved_uuid:
        return {"configured": True, "data": None, "message": "User not found"}

    result = await morpho.list_challenges(
        user_uuid=resolved_uuid, status=status, page=page, limit=limit
    )
    if result is None:
        return {"configured": True, "data": None, "message": "Could not fetch challenges"}

    return {
        "configured": True,
        "data": result.get("data", []),
        "meta": result.get("meta", {}),
        "user_uuid": resolved_uuid,
    }


# ------------------------------------------------------------------ #
#  Full User Dashboard (aggregated view)
# ------------------------------------------------------------------ #

@morpho_router.get("/dashboard")
async def get_morpho_dashboard(
    email: Optional[str] = Query(None),
    user_uuid: Optional[str] = Query(None),
):
    """
    Get a complete dashboard snapshot from Morpho for a user.
    Aggregates: user profile, accounts (balance/equity), recent transactions.
    This is the single endpoint the frontend can call to get all Morpho data.
    """
    if not morpho.is_configured:
        return {"configured": False, "data": None}

    # Resolve user
    resolved_uuid = user_uuid
    morpho_user = None

    if email and not resolved_uuid:
        morpho_user = await morpho.find_user_by_email(email)
        if morpho_user:
            resolved_uuid = morpho_user.get("uuid")

    if resolved_uuid and not morpho_user:
        raw = await morpho.get_user(resolved_uuid)
        if raw and "data" in raw:
            morpho_user = raw["data"]

    if not resolved_uuid:
        return {"configured": True, "data": None, "message": "User not found in Morpho"}

    # Fetch accounts and transactions in parallel concept (sequential here for simplicity)
    accounts = await morpho.get_user_accounts(resolved_uuid)
    deposits = await morpho.get_user_deposits(resolved_uuid, limit=10)
    withdrawals = await morpho.get_user_withdrawals(resolved_uuid, limit=10)

    # Build aggregated response
    account_summary = (
        MorphoClient.aggregate_account_balance(accounts) if accounts else None
    )

    recent_transactions = []
    if deposits:
        for d in deposits[:5]:
            recent_transactions.append(MorphoClient.map_deposit_to_transaction(d))
    if withdrawals:
        for w in withdrawals[:5]:
            recent_transactions.append(MorphoClient.map_withdrawal_to_transaction(w))
    recent_transactions.sort(key=lambda t: t.get("created_at", ""), reverse=True)

    return {
        "configured": True,
        "data": {
            "user": MorphoClient.map_user_to_fidus(morpho_user) if morpho_user else None,
            "accounts": account_summary,
            "recent_transactions": recent_transactions[:10],
        },
        "user_uuid": resolved_uuid,
    }
