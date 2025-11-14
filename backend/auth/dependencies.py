"""
Authentication Dependencies for FastAPI
Provides middleware for protected routes
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bson import ObjectId
from typing import Dict, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import os

from .jwt_handler import verify_token

# Security scheme for Swagger UI
security = HTTPBearer()

# Database connection
async def get_database():
    """Get database connection"""
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    return client.fidus_production


async def get_current_agent(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """
    Dependency to get the current authenticated referral agent.
    
    This dependency:
    1. Extracts JWT token from Authorization header
    2. Verifies token is valid and not expired
    3. Retrieves agent from database
    4. Validates agent account is active
    
    Use this as a dependency in protected routes:
    
    Example:
        @router.get("/api/referral-agent/dashboard")
        async def get_dashboard(agent: Dict = Depends(get_current_agent)):
            # agent is now authenticated and verified
            return {"message": f"Welcome {agent['name']}"}
    
    Args:
        credentials: HTTP Bearer token from request header
        
    Returns:
        Dict: Full salesperson document from database
        
    Raises:
        HTTPException 401: If token is invalid or expired
        HTTPException 401: If agent not found in database
        HTTPException 403: If agent account is not active
    """
    token = credentials.credentials
    
    # Verify and decode token
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Extract salesperson ID from token
    salesperson_id_str = payload.get("sub")
    
    if salesperson_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Get database connection
    db = await get_database()
    
    # Retrieve salesperson from database
    try:
        salesperson_id = ObjectId(salesperson_id_str)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid salesperson ID in token"
        )
    
    salesperson = await db.salespeople.find_one({"_id": salesperson_id})
    
    if salesperson is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Salesperson not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Check if account is active
    if salesperson.get("status") != "active" and salesperson.get("active") != True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please contact administrator."
        )
    
    return salesperson


async def get_current_agent_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[Dict]:
    """
    Optional authentication dependency.
    Returns agent if authenticated, None if not.
    
    Use this for routes that work differently for authenticated vs anonymous users.
    
    Example:
        @router.get("/api/public-data")
        async def get_data(agent: Optional[Dict] = Depends(get_current_agent_optional)):
            if agent:
                return {"data": "authenticated_version"}
            return {"data": "public_version"}
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_agent(credentials)
    except HTTPException:
        return None
