"""
Authentication utilities for FIDUS Investment Management Platform
Extracted from server.py for reuse across modules
"""

from fastapi import HTTPException, Request
import jwt
import os
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'fidus-production-secret-2025-secure-key-9X2Y5Z8B1E4F7G0I3J6K9L2M5N8O1P4Q7R0S3T6U9V2W5X8Y1Z4A7C0D3F6H9I2K5M8N0P2R5S8T1U4W7X0Y3Z6A9B2C5D8E1F4G7H0I3J6K9L2M5N8O1P4Q7R0S3T6U9V2W5X8Y1Z4')
JWT_ALGORITHM = 'HS256'

def verify_jwt_token(token: str) -> dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Check if token has expired
        if payload.get('exp') and payload['exp'] < datetime.now(timezone.utc).timestamp():
            raise HTTPException(status_code=401, detail="Token has expired")
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        logger.error(f"JWT verification error: {e}")
        raise HTTPException(status_code=401, detail="Token verification failed")

def get_current_admin_user(request: Request) -> dict:
    """Get current admin user from JWT token"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No token provided")
    
    token = auth_header.split(" ")[1]
    payload = verify_jwt_token(token)
    
    # Check if user is admin
    if payload.get("type") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return payload

def get_current_user(request: Request) -> dict:
    """Get current authenticated user (admin or client) from JWT token"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No token provided")
    
    token = auth_header.split(" ")[1]
    payload = verify_jwt_token(token)
    
    return payload

def generate_jwt_token(user_data: dict, expires_in_hours: int = 24) -> str:
    """Generate JWT token for user"""
    try:
        payload = {
            'user_id': user_data.get('user_id') or user_data.get('id'),
            'username': user_data.get('username'),
            'type': user_data.get('type'),
            'exp': datetime.now(timezone.utc).timestamp() + (expires_in_hours * 3600),
            'iat': datetime.now(timezone.utc).timestamp()
        }
        
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token
        
    except Exception as e:
        logger.error(f"JWT generation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate token")

def check_user_permissions(user: dict, required_permissions: list = None) -> bool:
    """Check if user has required permissions"""
    if not required_permissions:
        return True
    
    user_type = user.get('type')
    
    # Admin has all permissions
    if user_type == 'admin':
        return True
    
    # Add more permission logic as needed
    user_permissions = user.get('permissions', [])
    
    return any(perm in user_permissions for perm in required_permissions)

def require_admin_access(user: dict) -> None:
    """Raise exception if user is not admin"""
    if user.get('type') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")

def require_permissions(user: dict, permissions: list) -> None:
    """Raise exception if user doesn't have required permissions"""
    if not check_user_permissions(user, permissions):
        raise HTTPException(status_code=403, detail=f"Required permissions: {', '.join(permissions)}")