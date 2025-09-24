import os
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional
import uuid
import requests
import urllib.parse
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class GoogleAdminService:
    """Direct Google OAuth 2.0 service for admin users"""
    
    def __init__(self):
        self.client_id = os.environ.get('GOOGLE_CLIENT_ID')
        self.client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
        self.redirect_uri = os.environ.get('GOOGLE_REDIRECT_URI')
        self.google_oauth_url = "https://accounts.google.com/o/oauth2/auth"
        self.google_token_url = "https://oauth2.googleapis.com/token"
        self.google_userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        
        if not self.client_id or not self.client_secret or not self.redirect_uri:
            raise ValueError("Missing GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET or GOOGLE_REDIRECT_URI environment variables")
        
    def get_google_login_url(self, state: str = None) -> str:
        """Generate direct Google OAuth login URL"""
        try:
            # Standard Google OAuth parameters
            params = {
                'client_id': self.client_id,
                'redirect_uri': self.redirect_uri,
                'scope': 'openid email profile https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/calendar.readonly https://www.googleapis.com/auth/calendar.events https://www.googleapis.com/auth/drive.readonly https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/spreadsheets.readonly https://www.googleapis.com/auth/spreadsheets',
                'response_type': 'code',
                'access_type': 'offline',
                'prompt': 'consent'
            }
            
            if state:
                params['state'] = state
                
            query_string = urllib.parse.urlencode(params)
            login_url = f"{self.google_oauth_url}?{query_string}"
            
            logger.info(f"Generated Google OAuth URL: {login_url}")
            return login_url
            
        except Exception as e:
            logger.error(f"Error generating Google login URL: {str(e)}")
    async def test_gmail_connection(self) -> Dict:
        """Test Gmail API connectivity to verify OAuth is working"""
        try:
            # Use stored access token to test Gmail API
            access_token = self.get_stored_access_token()
            if not access_token:
                return {"success": False, "error": "No access token available"}
            
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(
                "https://gmail.googleapis.com/gmail/v1/users/me/profile",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                profile_data = response.json()
                return {
                    "success": True,
                    "email": profile_data.get("emailAddress"),
                    "messages_total": profile_data.get("messagesTotal", 0)
                }
            else:
                return {"success": False, "error": f"Gmail API error: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Gmail connection test failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_calendar_connection(self) -> Dict:
        """Test Calendar API connectivity to verify OAuth is working"""
        try:
            access_token = self.get_stored_access_token()
            if not access_token:
                return {"success": False, "error": "No access token available"}
            
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(
                "https://www.googleapis.com/calendar/v3/calendars/primary",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                calendar_data = response.json()
                return {
                    "success": True,
                    "calendar_id": calendar_data.get("id"),
                    "summary": calendar_data.get("summary")
                }
            else:
                return {"success": False, "error": f"Calendar API error: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Calendar connection test failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_drive_connection(self) -> Dict:
        """Test Drive API connectivity to verify OAuth is working"""
        try:
            access_token = self.get_stored_access_token()
            if not access_token:
                return {"success": False, "error": "No access token available"}
            
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(
                "https://www.googleapis.com/drive/v3/about?fields=user",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                drive_data = response.json()
                user_info = drive_data.get("user", {})
                return {
                    "success": True,
                    "user_email": user_info.get("emailAddress"),
                    "display_name": user_info.get("displayName")
                }
            else:
                return {"success": False, "error": f"Drive API error: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Drive connection test failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_stored_access_token(self) -> str:
        """Get stored access token from session/database"""
        # For now, return None - this needs to be implemented based on your token storage
        # This is where you'd retrieve the actual Google access token for the current user
        return None
    
    async def exchange_code_for_tokens(self, code: str) -> Dict[str, any]:
        """Exchange authorization code for access tokens using Google API"""
        try:
            # Real Google OAuth token exchange
            token_data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri
            }
            
            logger.info(f"Exchanging authorization code for tokens...")
            
            # Make request to Google token endpoint
            response = requests.post(
                self.google_token_url,
                data=token_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            if response.status_code == 200:
                tokens = response.json()
                logger.info("Successfully exchanged code for tokens")
                return tokens
            else:
                logger.error(f"Token exchange failed: HTTP {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Token exchange failed: {response.text}"
                )
            
        except requests.RequestException as e:
            logger.error(f"Request error during token exchange: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to exchange authorization code")
        except Exception as e:
            logger.error(f"Error exchanging code for tokens: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to exchange authorization code")
    
    async def get_user_info(self, access_token: str) -> Dict[str, any]:
        """Get user info from Google using access token"""
        try:
            logger.info("Retrieving user info from Google API...")
            
            # Make request to Google userinfo endpoint
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(
                self.google_userinfo_url,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                user_info = response.json()
                logger.info(f"Successfully retrieved user info for: {user_info.get('email')}")
                return user_info
            else:
                logger.error(f"Failed to get user info: HTTP {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to get user information: {response.text}"
                )
            
        except requests.RequestException as e:
            logger.error(f"Request error getting user info: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to get user information")
        except Exception as e:
            logger.error(f"Error getting user info: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to get user information")
    
    async def create_admin_session(self, user_info: Dict[str, any], tokens: Dict[str, any]) -> Dict[str, any]:
        """Create admin session with Google user info and tokens"""
        try:
            session_token = str(uuid.uuid4())
            expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
            
            session_data = {
                'session_token': session_token,
                'google_user_id': user_info['id'],
                'email': user_info['email'],
                'name': user_info['name'],
                'picture': user_info.get('picture'),
                'access_token': tokens['access_token'],
                'refresh_token': tokens.get('refresh_token'),
                'token_expires_at': datetime.now(timezone.utc) + timedelta(seconds=tokens['expires_in']),
                'created_at': datetime.now(timezone.utc),
                'expires_at': expires_at,
                'last_accessed': datetime.now(timezone.utc),
                'scopes': tokens.get('scope', '').split(' ')
            }
            
            logger.info(f"Created admin session for {user_info['email']}")
            return session_data
            
        except Exception as e:
            logger.error(f"Error creating admin session: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create session")

# Global service instance - lazy initialization to avoid environment variable issues
_google_admin_service = None

def get_google_admin_service():
    """Get or create Google admin service instance"""
    global _google_admin_service
    if _google_admin_service is None:
        _google_admin_service = GoogleAdminService()
    return _google_admin_service