"""
Clean Google OAuth Service - Complete Token Management
Handles OAuth flow, token storage, and automatic refresh
"""
import os
import logging
import requests
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from urllib.parse import urlencode
from motor.motor_asyncio import AsyncIOMotorDatabase
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

class GoogleOAuthService:
    """
    Complete Google OAuth implementation with:
    - OAuth URL generation
    - Token exchange
    - Token storage in MongoDB
    - Automatic token refresh
    - API client initialization
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
        # OAuth credentials from environment
        self.client_id = os.environ.get('GOOGLE_CLIENT_ID')
        self.client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
        self.redirect_uri = os.environ.get('GOOGLE_REDIRECT_URI')
        
        # Validate credentials
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            logger.warning("⚠️  Google OAuth credentials not fully configured in environment")
        
        # OAuth scopes
        self.scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.events',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
    
    def generate_oauth_url(self, user_id: str) -> str:
        """
        Generate Google OAuth authorization URL
        
        Args:
            user_id: User ID to include in state parameter
            
        Returns:
            OAuth authorization URL
        """
        try:
            # State parameter includes user_id for callback processing
            state = f"{user_id}:fidus_oauth"
            
            params = {
                'client_id': self.client_id,
                'redirect_uri': self.redirect_uri,
                'response_type': 'code',
                'scope': ' '.join(self.scopes),
                'state': state,
                'access_type': 'offline',  # Request refresh token
                'prompt': 'consent'  # Force consent to get refresh token
            }
            
            oauth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
            
            logger.info(f"✅ Generated OAuth URL for user {user_id}")
            return oauth_url
            
        except Exception as e:
            logger.error(f"❌ Failed to generate OAuth URL: {str(e)}")
            raise
    
    async def exchange_code_for_tokens(self, code: str, user_id: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens
        
        Args:
            code: Authorization code from OAuth callback
            user_id: User ID to associate tokens with
            
        Returns:
            Token data including access_token, refresh_token, expires_at
        """
        try:
            logger.info(f"🔄 Exchanging authorization code for tokens (user: {user_id})")
            
            # Exchange code for tokens
            token_response = requests.post(
                'https://oauth2.googleapis.com/token',
                data={
                    'code': code,
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'redirect_uri': self.redirect_uri,
                    'grant_type': 'authorization_code'
                },
                timeout=10
            )
            
            if token_response.status_code != 200:
                error_msg = f"Token exchange failed: {token_response.text}"
                logger.error(f"❌ {error_msg}")
                raise Exception(error_msg)
            
            tokens = token_response.json()
            
            # Calculate expiry time
            expires_in = tokens.get('expires_in', 3600)
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
            
            # Prepare token document
            token_doc = {
                'user_id': user_id,
                'access_token': tokens['access_token'],
                'refresh_token': tokens.get('refresh_token'),  # May not be present on refresh
                'token_type': tokens.get('token_type', 'Bearer'),
                'expires_at': expires_at,
                'scopes': tokens.get('scope', '').split(' ') if tokens.get('scope') else self.scopes,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            }
            
            # Store tokens in database
            await self.db.google_tokens.update_one(
                {'user_id': user_id},
                {'$set': token_doc},
                upsert=True
            )
            
            logger.info(f"✅ Tokens saved to database for user {user_id}")
            logger.info(f"   - Access token: {tokens['access_token'][:20]}...")
            logger.info(f"   - Refresh token: {'Yes' if tokens.get('refresh_token') else 'No'}")
            logger.info(f"   - Expires at: {expires_at.isoformat()}")
            
            return token_doc
            
        except Exception as e:
            logger.error(f"❌ Failed to exchange code for tokens: {str(e)}")
            raise
    
    async def get_valid_access_token(self, user_id: str) -> str:
        """
        Get a valid access token, refreshing if necessary
        
        Args:
            user_id: User ID to get token for
            
        Returns:
            Valid access token
            
        Raises:
            Exception if no tokens found or refresh fails
        """
        try:
            # Get tokens from database
            token_doc = await self.db.google_tokens.find_one({'user_id': user_id})
            
            if not token_doc:
                raise Exception("No Google tokens found - user needs to authenticate")
            
            # Check if token is expired or will expire in next 5 minutes
            now = datetime.now(timezone.utc)
            expires_at = token_doc['expires_at']
            
            # Make expires_at timezone-aware if it isn't
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            
            time_until_expiry = (expires_at - now).total_seconds()
            
            if time_until_expiry < 300:  # Less than 5 minutes
                logger.info(f"🔄 Token expired or expiring soon for user {user_id}, refreshing...")
                
                if not token_doc.get('refresh_token'):
                    raise Exception("No refresh token available - user needs to re-authenticate")
                
                # Refresh the token
                new_token = await self._refresh_access_token(user_id, token_doc['refresh_token'])
                return new_token
            
            logger.info(f"✅ Using existing valid token for user {user_id} (expires in {int(time_until_expiry)}s)")
            return token_doc['access_token']
            
        except Exception as e:
            logger.error(f"❌ Failed to get valid access token: {str(e)}")
            raise
    
    async def _refresh_access_token(self, user_id: str, refresh_token: str) -> str:
        """
        Refresh access token using refresh token
        
        Args:
            user_id: User ID
            refresh_token: Refresh token
            
        Returns:
            New access token
        """
        try:
            logger.info(f"🔄 Refreshing access token for user {user_id}")
            
            refresh_response = requests.post(
                'https://oauth2.googleapis.com/token',
                data={
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'refresh_token': refresh_token,
                    'grant_type': 'refresh_token'
                },
                timeout=10
            )
            
            if refresh_response.status_code != 200:
                error_msg = f"Token refresh failed: {refresh_response.text}"
                logger.error(f"❌ {error_msg}")
                raise Exception(error_msg)
            
            new_tokens = refresh_response.json()
            new_expires_at = datetime.now(timezone.utc) + timedelta(seconds=new_tokens.get('expires_in', 3600))
            
            # Update database with new access token
            update_data = {
                'access_token': new_tokens['access_token'],
                'expires_at': new_expires_at,
                'updated_at': datetime.now(timezone.utc)
            }
            
            # If a new refresh token is provided, update it too
            if new_tokens.get('refresh_token'):
                update_data['refresh_token'] = new_tokens['refresh_token']
            
            await self.db.google_tokens.update_one(
                {'user_id': user_id},
                {'$set': update_data}
            )
            
            logger.info(f"✅ Token refreshed successfully for user {user_id}")
            logger.info(f"   - New expiry: {new_expires_at.isoformat()}")
            
            return new_tokens['access_token']
            
        except Exception as e:
            logger.error(f"❌ Failed to refresh access token: {str(e)}")
            raise
    
    async def check_connection_status(self, user_id: str) -> Dict[str, Any]:
        """
        Check if user has valid Google connection
        
        Args:
            user_id: User ID to check
            
        Returns:
            Connection status with details
        """
        try:
            token_doc = await self.db.google_tokens.find_one({'user_id': user_id})
            
            if not token_doc:
                return {
                    'connected': False,
                    'message': 'Not connected to Google'
                }
            
            # Check if token is expired
            now = datetime.now(timezone.utc)
            expires_at = token_doc['expires_at']
            
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            
            is_expired = now >= expires_at
            
            return {
                'connected': True,
                'has_refresh_token': bool(token_doc.get('refresh_token')),
                'expires_at': expires_at.isoformat(),
                'is_expired': is_expired,
                'scopes': token_doc.get('scopes', [])
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to check connection status: {str(e)}")
            return {
                'connected': False,
                'error': str(e)
            }
    
    async def get_gmail_service(self, user_id: str):
        """Get authenticated Gmail API service"""
        access_token = await self.get_valid_access_token(user_id)
        credentials = Credentials(token=access_token)
        return build('gmail', 'v1', credentials=credentials)
    
    async def get_calendar_service(self, user_id: str):
        """Get authenticated Calendar API service"""
        access_token = await self.get_valid_access_token(user_id)
        credentials = Credentials(token=access_token)
        return build('calendar', 'v3', credentials=credentials)
    
    async def get_drive_service(self, user_id: str):
        """Get authenticated Drive API service"""
        access_token = await self.get_valid_access_token(user_id)
        credentials = Credentials(token=access_token)
        return build('drive', 'v3', credentials=credentials)
    
    async def get_sheets_service(self, user_id: str):
        """Get authenticated Sheets API service"""
        access_token = await self.get_valid_access_token(user_id)
        credentials = Credentials(token=access_token)
        return build('sheets', 'v4', credentials=credentials)
    
    async def disconnect(self, user_id: str) -> bool:
        """
        Disconnect Google account by deleting tokens
        
        Args:
            user_id: User ID to disconnect
            
        Returns:
            True if successful
        """
        try:
            result = await self.db.google_tokens.delete_one({'user_id': user_id})
            logger.info(f"✅ Disconnected Google for user {user_id} (deleted {result.deleted_count} token documents)")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to disconnect Google: {str(e)}")
            return False


# Global instance - will be initialized in server.py
google_oauth_service: Optional[GoogleOAuthService] = None


def get_google_oauth_service(db: AsyncIOMotorDatabase) -> GoogleOAuthService:
    """Get or create Google OAuth service instance"""
    global google_oauth_service
    if google_oauth_service is None:
        google_oauth_service = GoogleOAuthService(db)
    return google_oauth_service
