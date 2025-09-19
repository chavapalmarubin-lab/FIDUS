import os
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, List
import requests
from fastapi import HTTPException
import json

logger = logging.getLogger(__name__)

class GoogleAdminService:
    """Service for managing Google authentication and API access for admin users"""
    
    def __init__(self):
        self.auth_base_url = "https://auth.emergentagent.com"
        self.session_api_url = "https://auth.emergentagent.com/auth/v1/env/oauth/session-data"
        
    def get_google_login_url(self, redirect_url: str) -> str:
        """Generate Google OAuth login URL for admin users"""
        try:
            # Use Emergent auth service for Google OAuth
            login_url = f"{self.auth_base_url}/?redirect={requests.utils.quote(redirect_url)}"
            return login_url
            
        except Exception as e:
            logger.error(f"Error generating Google login URL: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to generate login URL")
    
    async def process_session_id(self, session_id: str) -> Dict[str, any]:
        """Process session ID from OAuth callback and get user data"""
        try:
            headers = {
                'X-Session-ID': session_id,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(self.session_api_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            user_data = response.json()
            
            # Validate required fields
            required_fields = ['id', 'email', 'name', 'session_token']
            for field in required_fields:
                if field not in user_data:
                    raise ValueError(f"Missing required field: {field}")
            
            return user_data
            
        except requests.RequestException as e:
            logger.error(f"Error processing session ID: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid or expired session ID")
        except Exception as e:
            logger.error(f"Unexpected error processing session: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to process authentication")
    
    def create_admin_session(self, user_data: Dict[str, any]) -> Dict[str, any]:
        """Create admin session with Google account data"""
        try:
            session_data = {
                'google_id': user_data['id'],
                'email': user_data['email'],
                'name': user_data['name'],
                'picture': user_data.get('picture', ''),
                'session_token': user_data['session_token'],
                'created_at': datetime.now(timezone.utc),
                'expires_at': datetime.now(timezone.utc) + timedelta(days=7),
                'google_scopes': [
                    'https://www.googleapis.com/auth/gmail.send',
                    'https://www.googleapis.com/auth/gmail.readonly',
                    'https://www.googleapis.com/auth/calendar',
                    'https://www.googleapis.com/auth/drive.file'
                ],
                'is_admin': True,
                'login_type': 'google_oauth'
            }
            
            return session_data
            
        except Exception as e:
            logger.error(f"Error creating admin session: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create session")
    
    def validate_admin_email(self, email: str) -> bool:
        """Validate if email is authorized for admin access"""
        # For now, we'll allow the specific admin email provided
        authorized_emails = [
            'chavapalmarubin@gmail.com',
            # Add more authorized admin emails as needed
        ]
        
        return email.lower() in [e.lower() for e in authorized_emails]
    
    def get_google_api_scopes(self) -> List[str]:
        """Get required Google API scopes for admin functionality"""
        return [
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.readonly', 
            'https://www.googleapis.com/auth/gmail.compose',
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.events',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/documents',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
    
    def format_admin_profile(self, session_data: Dict[str, any]) -> Dict[str, any]:
        """Format admin profile data for frontend"""
        return {
            'id': session_data.get('google_id'),
            'email': session_data.get('email'),
            'name': session_data.get('name'),
            'picture': session_data.get('picture'),
            'is_google_connected': True,
            'google_scopes': session_data.get('google_scopes', []),
            'login_type': session_data.get('login_type', 'google_oauth'),
            'connected_at': session_data.get('created_at', datetime.now(timezone.utc)).isoformat()
        }
    
    async def send_email_via_google(self, session_token: str, to_email: str, subject: str, body: str, attachments: Optional[List] = None) -> bool:
        """Send email using admin's Google account (placeholder for future implementation)"""
        try:
            # This would integrate with Gmail API using the admin's session_token
            # For now, return success to indicate the service is ready
            logger.info(f"Email sending prepared for {to_email} with subject: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    async def create_calendar_event(self, session_token: str, event_data: Dict[str, any]) -> Optional[str]:
        """Create calendar event using admin's Google account (placeholder for future implementation)"""
        try:
            # This would integrate with Google Calendar API
            logger.info(f"Calendar event creation prepared: {event_data.get('summary', 'No title')}")
            return "placeholder_event_id"
            
        except Exception as e:
            logger.error(f"Error creating calendar event: {str(e)}")
            return None
    
    async def share_document(self, session_token: str, document_id: str, email: str, permission: str = 'view') -> bool:
        """Share Google Drive document with client (placeholder for future implementation)"""
        try:
            # This would integrate with Google Drive API
            logger.info(f"Document sharing prepared: {document_id} with {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sharing document: {str(e)}")
            return False

# Global Google admin service instance
google_admin_service = GoogleAdminService()