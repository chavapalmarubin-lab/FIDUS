"""
Emergent Google Social Login Implementation
Provides Google OAuth authentication for user signup and login
"""

import logging
import requests
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmergentGoogleAuth:
    """
    Emergent Google Social Login Service
    Handles Google OAuth authentication through Emergent's service
    """
    
    def __init__(self):
        self.emergent_oauth_url = "https://auth.emergentagent.com"
        self.session_data_url = "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data"
    
    def generate_login_url(self, redirect_url: str) -> str:
        """
        Generate Google login URL using Emergent OAuth
        
        Args:
            redirect_url: Where user should be redirected after authentication
            
        Returns:
            Google OAuth URL for user authentication
        """
        try:
            # Use Emergent OAuth service for Google authentication
            oauth_url = f"{self.emergent_oauth_url}/?redirect={requests.utils.quote(redirect_url, safe='')}"
            
            logger.info(f"Generated Google login URL for redirect: {redirect_url}")
            return oauth_url
            
        except Exception as e:
            logger.error(f"Failed to generate login URL: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to generate login URL")
    
    async def process_session_id(self, session_id: str) -> Dict[str, Any]:
        """
        Process session ID from Emergent OAuth callback
        
        Args:
            session_id: Session ID from URL fragment
            
        Returns:
            User data and session information
        """
        try:
            logger.info(f"Processing session ID: {session_id}")
            logger.info(f"Session data URL: {self.session_data_url}")
            
            # Call Emergent backend to get session data
            response = requests.get(
                self.session_data_url,
                headers={'X-Session-ID': session_id},
                timeout=10
            )
            
            logger.info(f"Emergent service response status: {response.status_code}")
            logger.info(f"Emergent service response text: {response.text}")
            
            if response.status_code != 200:
                logger.error(f"Emergent session data request failed: {response.status_code}, Response: {response.text}")
                raise HTTPException(status_code=400, detail=f"Invalid session ID - Service responded with {response.status_code}")
            
            session_data = response.json()
            logger.info(f"Session data received: {session_data}")
            
            # Extract user information
            user_data = {
                'google_id': session_data.get('id'),
                'email': session_data.get('email'),
                'name': session_data.get('name'),
                'picture': session_data.get('picture', ''),
                'emergent_session_token': session_data.get('session_token')
            }
            
            logger.info(f"Extracted user data: {user_data}")
            
            # Validate required fields
            if not user_data['email'] or not user_data['emergent_session_token']:
                logger.error(f"Incomplete OAuth data - email: {user_data.get('email')}, token: {user_data.get('emergent_session_token')}")
                raise HTTPException(status_code=400, detail="Incomplete OAuth data")
            
            logger.info(f"Successfully processed session for: {user_data['email']}")
            return user_data
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Session processing error: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to process session")
    
    def create_local_session(self, user_data: Dict[str, Any]) -> str:
        """
        Create local session token for authenticated user
        
        Args:
            user_data: User information from Google OAuth
            
        Returns:
            Local session token
        """
        try:
            # Generate unique local session token
            local_session_token = str(uuid.uuid4())
            
            logger.info(f"Created local session token for: {user_data['email']}")
            return local_session_token
            
        except Exception as e:
            logger.error(f"Session creation error: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create session")

# Global instance
google_social_auth = EmergentGoogleAuth()