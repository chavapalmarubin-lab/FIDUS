"""
JWT Token Handler for Referral Agent Authentication
Handles token generation, verification, and validation
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "temp_dev_secret_change_in_production_1234567890")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The bcrypt hashed password
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Bcrypt hashed password
    """
    return pwd_context.hash(password)


def create_access_token(
    data: Dict[str, str],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary of data to encode in token (must include 'sub' with user ID)
        expires_delta: Optional custom expiration time
        
    Returns:
        str: Encoded JWT token
        
    Example:
        >>> token = create_access_token({"sub": "user_id_123"})
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc)  # Issued at
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Optional[Dict]: Decoded token payload if valid, None if invalid
        
    Example:
        >>> payload = verify_token(token)
        >>> if payload:
        >>>     user_id = payload.get("sub")
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def decode_token(token: str) -> Dict:
    """
    Decode a JWT token without verification (for debugging).
    
    Args:
        token: JWT token string
        
    Returns:
        Dict: Decoded token payload
        
    Raises:
        JWTError: If token cannot be decoded
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def get_token_expiration(token: str) -> Optional[datetime]:
    """
    Get the expiration time from a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Optional[datetime]: Expiration datetime if token is valid, None otherwise
    """
    payload = verify_token(token)
    if payload and "exp" in payload:
        return datetime.fromtimestamp(payload["exp"])
    return None
