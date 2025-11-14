"""
Authentication module for FIDUS Referral Agent Portal
Provides JWT token handling and authentication dependencies
"""

from .jwt_handler import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    get_token_expiration
)

from .dependencies import (
    get_current_agent,
    get_current_agent_optional
)

__all__ = [
    'verify_password',
    'get_password_hash',
    'create_access_token',
    'verify_token',
    'get_token_expiration',
    'get_current_agent',
    'get_current_agent_optional'
]