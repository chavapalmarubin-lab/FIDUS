"""
Emergent Google Auth Integration for FIDUS
Using Emergent's managed Google OAuth service for Gmail, Calendar, Drive access
"""

import aiohttp
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, List
from fastapi import HTTPException
import json

logger = logging.getLogger(__name__)

class EmergentGoogleAuth:
    """
    Emergent managed Google OAuth service
    Handles authentication via Emergent's auth infrastructure
    """
    
    def __init__(self, db):
        self.db = db
        self.auth_base_url = "https://auth.emergentagent.com"
        self.session_api_url = "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data"
        
    def get_auth_url(self, redirect_url: str) -> str:
        """
        Generate Emergent Auth URL for Google OAuth
        
        Args:
            redirect_url: Where user lands after auth (main app route)
            
        Returns:
            Emergent auth URL that redirects to Google OAuth
        """
        import urllib.parse
        encoded_redirect = urllib.parse.quote(redirect_url, safe='')
        auth_url = f"{self.auth_base_url}/?redirect={encoded_redirect}"
        
        logger.info(f"Generated Emergent Google Auth URL: {auth_url}")
        return auth_url
    
    async def exchange_session_id(self, session_id: str) -> Dict:
        """
        Exchange session_id for user data and session_token
        
        Args:
            session_id: Temporary session ID from URL fragment
            
        Returns:
            Dictionary with user data and session_token
        """
        try:
            headers = {
                'X-Session-ID': session_id,
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.session_api_url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Expected response: {"id": "string", "email": "string", "name": "string", "picture": "string", "session_token": "string"}
                        required_fields = ['id', 'email', 'name', 'session_token']
                        if all(field in data for field in required_fields):
                            logger.info(f"✅ Successfully exchanged session_id for user: {data.get('email')}")
                            return {
                                'success': True,
                                'user_data': data,
                                'session_token': data['session_token']
                            }
                        else:
                            missing_fields = [f for f in required_fields if f not in data]
                            logger.error(f"Missing required fields in session data: {missing_fields}")
                            return {
                                'success': False,
                                'error': f'Incomplete session data - missing: {missing_fields}'
                            }
                    else:
                        error_text = await response.text()
                        logger.error(f"Session exchange failed with status {response.status}: {error_text}")
                        return {
                            'success': False,
                            'error': f'Session API error: {response.status}'
                        }
                        
        except Exception as e:
            logger.error(f"Error exchanging session_id: {str(e)}")
            return {
                'success': False,
                'error': f'Exchange failed: {str(e)}'
            }
    
    async def store_session_token(self, admin_user_id: str, user_data: Dict, session_token: str) -> bool:
        """
        Store session token in database with 7-day expiry
        
        Args:
            admin_user_id: FIDUS admin user ID
            user_data: User data from Emergent
            session_token: Persistent auth token (7 days)
            
        Returns:
            True if stored successfully
        """
        try:
            # Calculate timezone-aware expiry (7 days)
            expiry_date = datetime.now(timezone.utc) + timedelta(days=7)
            
            # Store session in database
            session_data = {
                'admin_user_id': admin_user_id,
                'google_user_id': user_data.get('id'),
                'google_email': user_data.get('email'),
                'google_name': user_data.get('name'),
                'google_picture': user_data.get('picture'),
                'session_token': session_token,
                'expires_at': expiry_date,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc),
                'connection_status': 'active'
            }
            
            # Upsert session data
            result = await self.db.emergent_google_sessions.update_one(
                {'admin_user_id': admin_user_id},
                {'$set': session_data},
                upsert=True
            )
            
            logger.info(f"✅ Stored Emergent Google session for admin {admin_user_id} ({user_data.get('email')})")
            return result.acknowledged
            
        except Exception as e:
            logger.error(f"Error storing session token for admin {admin_user_id}: {str(e)}")
            return False
    
    async def get_session_token(self, admin_user_id: str) -> Optional[str]:
        """
        Get valid session token for admin user
        
        Args:
            admin_user_id: FIDUS admin user ID
            
        Returns:
            Valid session token or None if expired/not found
        """
        try:
            session_doc = await self.db.emergent_google_sessions.find_one({
                'admin_user_id': admin_user_id
            })
            
            if not session_doc:
                logger.info(f"No session found for admin {admin_user_id}")
                return None
                
            # Check if session is expired
            expires_at = session_doc.get('expires_at')
            if expires_at and expires_at < datetime.now(timezone.utc):
                logger.info(f"Session expired for admin {admin_user_id}")
                # Clean up expired session
                await self.db.emergent_google_sessions.delete_one({'admin_user_id': admin_user_id})
                return None
                
            return session_doc.get('session_token')
            
        except Exception as e:
            logger.error(f"Error getting session token for admin {admin_user_id}: {str(e)}")
            return None
    
    async def get_user_info(self, admin_user_id: str) -> Optional[Dict]:
        """
        Get stored user info for admin
        
        Args:
            admin_user_id: FIDUS admin user ID
            
        Returns:
            User info dictionary or None
        """
        try:
            session_doc = await self.db.emergent_google_sessions.find_one({
                'admin_user_id': admin_user_id
            })
            
            if session_doc:
                return {
                    'google_email': session_doc.get('google_email'),
                    'google_name': session_doc.get('google_name'), 
                    'google_picture': session_doc.get('google_picture'),
                    'connected': True,
                    'expires_at': session_doc.get('expires_at'),
                    'connection_status': session_doc.get('connection_status', 'active')
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user info for admin {admin_user_id}: {str(e)}")
            return None
    
    async def logout_user(self, admin_user_id: str) -> bool:
        """
        Logout user by deleting session from database
        
        Args:
            admin_user_id: FIDUS admin user ID
            
        Returns:
            True if logout successful
        """
        try:
            result = await self.db.emergent_google_sessions.delete_one({
                'admin_user_id': admin_user_id
            })
            
            logger.info(f"✅ Logged out admin {admin_user_id} from Emergent Google Auth")
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error logging out admin {admin_user_id}: {str(e)}")
            return False

# Global instance
emergent_google_auth = None

def initialize_emergent_google_auth(db):
    """Initialize the global Emergent Google Auth instance"""
    global emergent_google_auth
    emergent_google_auth = EmergentGoogleAuth(db)
    return emergent_google_auth