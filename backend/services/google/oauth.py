"""
Google OAuth 2.0 Service
Handles OAuth flow for Google Workspace integration
"""

import os
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from urllib.parse import urlencode
import requests
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class GoogleOAuthService:
    """
    Handles Google OAuth 2.0 authentication flow
    
    Features:
    - Force account picker
    - Pre-select business account
    - Secure state management
    - Token exchange and storage
    """
    
    def __init__(self, token_manager):
        """Initialize OAuth service with configuration"""
        # OAuth Configuration
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
        
        # Validate required config
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            raise ValueError(
                "Missing required Google OAuth configuration. "
                "Set GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and GOOGLE_REDIRECT_URI"
            )
        
        # Token manager for storage
        self.token_manager = token_manager
        
        # OAuth endpoints
        self.auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        
        # Required scopes for FIDUS features
        self.scopes = [
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.modify",
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/calendar.events",
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/drive.file",
        ]
        
        logger.info("✅ Google OAuth Service initialized")
        logger.info(f"📍 Redirect URI: {self.redirect_uri}")
    
    async def generate_auth_url(self, user_id: str) -> str:
        """
        Generate OAuth authorization URL
        
        Args:
            user_id: Admin user ID initiating OAuth
            
        Returns:
            Authorization URL to redirect user to
        """
        # Generate secure state token
        state = f"{user_id}:{secrets.token_urlsafe(32)}"
        
        # Store state for validation (expires in 10 minutes)
        await self.token_manager.store_state(user_id, state, expires_minutes=10)
        
        # Build OAuth parameters
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "state": state,
            "access_type": "offline",  # Request refresh token
            "prompt": "select_account consent",  # CRITICAL: Force account picker
            "login_hint": "chavapalmarubin@gmail.com"  # CRITICAL: Pre-select business account
        }
        
        auth_url = f"{self.auth_url}?{urlencode(params)}"
        
        logger.info(f"🔐 Generated OAuth URL for user {user_id}")
        logger.debug(f"📝 OAuth URL: {auth_url}")
        
        return auth_url
    
    async def handle_callback(
        self, 
        code: str, 
        state: str, 
        error: Optional[str] = None
    ) -> Dict:
        """
        Handle OAuth callback from Google
        
        Args:
            code: Authorization code from Google
            state: State parameter for CSRF protection
            error: Error code if OAuth failed
            
        Returns:
            Dictionary with user info and success status
            
        Raises:
            HTTPException: If callback processing fails
        """
        logger.info("📨 Received OAuth callback")
        
        # Handle OAuth errors
        if error:
            logger.error(f"❌ OAuth error: {error}")
            raise HTTPException(
                status_code=400,
                detail=f"OAuth error: {error}"
            )
        
        # Validate required parameters
        if not code or not state:
            logger.error("❌ Missing code or state in callback")
            raise HTTPException(
                status_code=400,
                detail="Missing required OAuth parameters"
            )
        
        # Parse state to get user_id
        try:
            user_id, state_token = state.split(':', 1)
            logger.info(f"🔍 Extracted user_id from state: {user_id}")
        except ValueError:
            logger.error(f"❌ Invalid state format: {state}")
            logger.error(f"❌ State value: {state}")
            raise HTTPException(
                status_code=400,
                detail="Invalid state parameter"
            )
        except Exception as e:
            logger.error(f"❌ Error parsing state: {str(e)}")
            logger.error(f"❌ State value: {state}")
            raise HTTPException(
                status_code=400,
                detail=f"State parsing failed: {str(e)}"
            )
        
        # Verify state (CSRF protection)
        if not self.token_manager.verify_state(user_id, state):
            logger.error(f"❌ State verification failed for user {user_id}")
            raise HTTPException(
                status_code=400,
                detail="State verification failed - possible CSRF attack"
            )
        
        # Defensive check: Ensure user_id is valid
        if not user_id or user_id == "":
            logger.error(f"❌ Empty user_id after state parsing")
            raise HTTPException(
                status_code=400,
                detail="Invalid user_id in OAuth state"
            )
        
        logger.info(f"✅ State verified for user: {user_id}")
        
        # Exchange authorization code for tokens
        try:
            logger.info(f"🔄 Exchanging code for tokens (user: {user_id})")
            
            token_data = {
                "code": code,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri,
                "grant_type": "authorization_code"
            }
            
            response = requests.post(
                self.token_url,
                data=token_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Token exchange failed: {response.text}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Token exchange failed: {response.text}"
                )
            
            tokens = response.json()
            logger.info("✅ Successfully exchanged code for tokens")
            
        except requests.RequestException as e:
            logger.error(f"❌ Token exchange request failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Token exchange failed: {str(e)}"
            )
        
        # Get user info from Google
        try:
            logger.info("👤 Fetching user info from Google")
            
            userinfo_response = requests.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            )
            
            if userinfo_response.status_code == 200:
                user_info = userinfo_response.json()
                logger.info(f"✅ Got user info: {user_info.get('email')}")
            else:
                logger.warning("⚠️ Could not fetch user info")
                user_info = {}
                
        except Exception as e:
            logger.warning(f"⚠️ User info fetch failed: {str(e)}")
            user_info = {}
        
        # Store tokens
        try:
            logger.info(f"💾 Storing tokens for user {user_id}")
            
            await self.token_manager.store_tokens(
                user_id=user_id,
                access_token=tokens['access_token'],
                refresh_token=tokens.get('refresh_token'),
                expires_in=tokens['expires_in'],
                token_type=tokens['token_type'],
                scope=tokens['scope']
            )
            
            logger.info("✅ Tokens stored successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to store tokens: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to store tokens: {str(e)}"
            )
        
        # Clear state (one-time use)
        await self.token_manager.clear_state(user_id)
        
        logger.info(f"🎉 OAuth flow completed successfully for user {user_id}")
        
        return {
            "success": True,
            "user_id": user_id,
            "email": user_info.get('email'),
            "name": user_info.get('name'),
            "picture": user_info.get('picture')
        }
    
    async def disconnect(self, user_id: str) -> bool:
        """
        Disconnect Google account for user
        
        Args:
            user_id: Admin user ID
            
        Returns:
            True if successful
        """
        logger.info(f"🔌 Disconnecting Google account for user {user_id}")
        
        # Revoke tokens with Google
        tokens = await self.token_manager.get_tokens(user_id)
        
        if tokens and tokens.get('access_token'):
            try:
                revoke_url = "https://oauth2.googleapis.com/revoke"
                requests.post(
                    revoke_url,
                    data={"token": tokens['access_token']},
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                logger.info("✅ Tokens revoked with Google")
            except Exception as e:
                logger.warning(f"⚠️ Could not revoke tokens: {str(e)}")
        
        # Delete tokens from storage
        await self.token_manager.delete_tokens(user_id)
        
        logger.info(f"✅ Google account disconnected for user {user_id}")
        
        return True
