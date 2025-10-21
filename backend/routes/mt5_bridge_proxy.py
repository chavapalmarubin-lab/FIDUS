"""
MT5 Bridge Proxy Routes
Proxies requests from the FIDUS backend to the MT5 Bridge API service on VPS
"""

from fastapi import APIRouter, HTTPException
import httpx
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

router = APIRouter()

# MT5 Bridge configuration
MT5_BRIDGE_URL = os.getenv('MT5_BRIDGE_URL', 'http://92.118.45.135:8000')
REQUEST_TIMEOUT = 30.0

# ============================================
# HEALTH CHECK
# ============================================
@router.get("/api/mt5/bridge/health")
async def bridge_health():
    """Proxy to MT5 Bridge health check"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{MT5_BRIDGE_URL}/api/mt5/bridge/health")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ MT5 Bridge health check failed: {e.response.status_code}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"MT5 Bridge health check failed: {e.response.text}"
        )
    except httpx.RequestError as e:
        logger.error(f"❌ MT5 Bridge unavailable: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"MT5 Bridge service unavailable: {str(e)}"
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error in health check: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Health check error: {str(e)}"
        )


# ============================================
# MT5 STATUS
# ============================================
@router.get("/api/mt5/status")
async def mt5_status():
    """Proxy to MT5 status endpoint"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{MT5_BRIDGE_URL}/api/mt5/status")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ MT5 status request failed: {e.response.status_code}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"MT5 status request failed: {e.response.text}"
        )
    except httpx.RequestError as e:
        logger.error(f"❌ MT5 Bridge unavailable: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"MT5 Bridge service unavailable: {str(e)}"
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error getting MT5 status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"MT5 status error: {str(e)}"
        )


# ============================================
# ACCOUNT INFO
# ============================================
@router.get("/api/mt5/account/{account_id}/info")
async def get_account_info(account_id: int):
    """Proxy to MT5 account info endpoint"""
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.get(f"{MT5_BRIDGE_URL}/api/mt5/account/{account_id}/info")
            
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"Account {account_id} not found")
            
            response.raise_for_status()
            return response.json()
            
    except HTTPException:
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ Account info request failed: {e.response.status_code}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Account info request failed: {e.response.text}"
        )
    except httpx.RequestError as e:
        logger.error(f"❌ MT5 Bridge unavailable: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"MT5 Bridge service unavailable: {str(e)}"
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error getting account info: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Account info error: {str(e)}"
        )


# ============================================
# ACCOUNT BALANCE
# ============================================
@router.get("/api/mt5/account/{account_id}/balance")
async def get_account_balance(account_id: int):
    """Proxy to MT5 account balance endpoint"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{MT5_BRIDGE_URL}/api/mt5/account/{account_id}/balance")
            
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"Account {account_id} not found")
            
            response.raise_for_status()
            return response.json()
            
    except HTTPException:
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ Account balance request failed: {e.response.status_code}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Account balance request failed: {e.response.text}"
        )
    except httpx.RequestError as e:
        logger.error(f"❌ MT5 Bridge unavailable: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"MT5 Bridge service unavailable: {str(e)}"
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error getting account balance: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Account balance error: {str(e)}"
        )


# ============================================
# ACCOUNT TRADES
# ============================================
@router.get("/api/mt5/account/{account_id}/trades")
async def get_account_trades(account_id: int, limit: int = 100):
    """Proxy to MT5 account trades endpoint"""
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.get(
                f"{MT5_BRIDGE_URL}/api/mt5/account/{account_id}/trades",
                params={"limit": limit}
            )
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ Account trades request failed: {e.response.status_code}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Account trades request failed: {e.response.text}"
        )
    except httpx.RequestError as e:
        logger.error(f"❌ MT5 Bridge unavailable: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"MT5 Bridge service unavailable: {str(e)}"
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error getting account trades: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Account trades error: {str(e)}"
        )


# ============================================
# ACCOUNTS SUMMARY
# ============================================
@router.get("/api/mt5/accounts/summary")
async def get_accounts_summary():
    """Proxy to MT5 accounts summary endpoint"""
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.get(f"{MT5_BRIDGE_URL}/api/mt5/accounts/summary")
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ Accounts summary request failed: {e.response.status_code}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Accounts summary request failed: {e.response.text}"
        )
    except httpx.RequestError as e:
        logger.error(f"❌ MT5 Bridge unavailable: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"MT5 Bridge service unavailable: {str(e)}"
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error getting accounts summary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Accounts summary error: {str(e)}"
        )


# ============================================
# SYSTEM STATUS (ADMIN)
# ============================================
@router.get("/api/mt5/admin/system-status")
async def get_system_status():
    """Proxy to MT5 Bridge system status endpoint (admin)"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{MT5_BRIDGE_URL}/api/mt5/admin/system-status")
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ System status request failed: {e.response.status_code}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"System status request failed: {e.response.text}"
        )
    except httpx.RequestError as e:
        logger.error(f"❌ MT5 Bridge unavailable: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"MT5 Bridge service unavailable: {str(e)}"
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error getting system status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"System status error: {str(e)}"
        )
