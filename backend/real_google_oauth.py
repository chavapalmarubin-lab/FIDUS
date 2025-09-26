"""
REAL Google OAuth Integration
This creates the actual Google OAuth flow that redirects users to accounts.google.com
"""
import os
import logging
import requests
from urllib.parse import urlencode
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class RealGoogleOAuth:
    """Real Google OAuth 2.0 integration"""
    
    def __init__(self):
        # Use your ACTUAL Google OAuth credentials
        self.client_id = "909926639154-r3v0ka94cbu4uo0sn8g4jvtiulf4i9qs.apps.googleusercontent.com"  
        self.client_secret = "GOCSPX-YOUR_CLIENT_SECRET_HERE"  # You need to get this from Google Console
        self.redirect_uri = "https://invest-portal-31.preview.emergentagent.com/api/admin/google-callback"
        
        self.oauth_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        
        # Comprehensive scopes for full Google Workspace access
        self.scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.compose',
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.events',
        ]
        
        logger.info("Real Google OAuth initialized")
    
    def get_authorization_url(self) -> str:
        """
        Generate the REAL Google OAuth URL that redirects users to accounts.google.com
        This is the classic Google OAuth flow you wanted
        """
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(self.scopes),
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent',
            'state': 'fidus_oauth_state_123'  # Security token
        }
        
        auth_url = f"{self.oauth_base_url}?{urlencode(params)}"
        logger.info(f"Generated REAL Google OAuth URL: {auth_url}")
        
        return auth_url
    
    def exchange_code_for_tokens(self, authorization_code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access/refresh tokens
        This happens after user authorizes on accounts.google.com
        """
        try:
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': authorization_code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri,
            }
            
            response = requests.post(self.token_url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                logger.info("✅ Successfully exchanged authorization code for tokens")
                
                return {
                    'success': True,
                    'access_token': token_data.get('access_token'),
                    'refresh_token': token_data.get('refresh_token'),
                    'expires_in': token_data.get('expires_in'),
                    'scope': token_data.get('scope')
                }
            else:
                logger.error(f"❌ Token exchange failed: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'Token exchange failed: {response.text}'
                }
                
        except Exception as e:
            logger.error(f"❌ Token exchange error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user info from Google using access token"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                logger.info(f"✅ Retrieved user info for: {user_data.get('email')}")
                return {
                    'success': True,
                    'user': user_data
                }
            else:
                logger.error(f"❌ Failed to get user info: {response.status_code}")
                return {
                    'success': False,
                    'error': f'Failed to get user info: {response.text}'
                }
                
        except Exception as e:
            logger.error(f"❌ Get user info error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

# Global instance
real_google_oauth = RealGoogleOAuth()