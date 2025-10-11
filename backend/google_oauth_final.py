"""
Google OAuth Service - Complete Token Management
Handles OAuth flow, token storage, and automatic refresh
CRITICAL: Uses credentials provided by user
"""

import os
import logging
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode
from motor.motor_asyncio import AsyncIOMotorDatabase
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import aiohttp

logger = logging.getLogger(__name__)

class GoogleOAuthService:
    """
    Complete Google OAuth implementation with:
    - OAuth URL generation
    - Token exchange and callback handling
    - Token storage in MongoDB with auto-refresh
    - API service builders for Gmail, Calendar, Drive, Sheets
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
        # OAuth credentials - using exact credentials provided by user
        self.client_config = {
            "web": {
                "client_id": "909926639154-r3v0ka94cbu4uo0sn8g4jvtiulf4i9qs.apps.googleusercontent.com",
                "client_secret": "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",
                "redirect_uris": ["https://fidus-invest.emergent.host/api/auth/google/callback"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }
        
        self.client_id = self.client_config["web"]["client_id"]
        self.client_secret = self.client_config["web"]["client_secret"]
        self.redirect_uri = self.client_config["web"]["redirect_uris"][0]
        
        # OAuth scopes for Google Workspace integration
        self.scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
    
    def get_oauth_url(self, admin_user_id: str) -> str:
        """
        Generate Google OAuth authorization URL
        
        Args:
            admin_user_id: Admin user ID to include in state parameter
            
        Returns:
            OAuth authorization URL
        """
        try:
            # State parameter includes admin_user_id for callback processing
            state = f"{admin_user_id}:fidus_oauth_state"
            
            params = {
                'client_id': self.client_id,
                'redirect_uri': self.redirect_uri,
                'response_type': 'code',
                'scope': ' '.join(self.scopes),
                'state': state,
                'access_type': 'offline',      # REQUIRED for refresh token
                'prompt': 'consent',           # REQUIRED to get refresh token
                'include_granted_scopes': 'true'
            }
            
            oauth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
            
            logger.info(f"✅ Generated OAuth URL for admin user {admin_user_id}")
            return oauth_url
            
        except Exception as e:
            logger.error(f"❌ Failed to generate OAuth URL: {str(e)}")
            raise
    
    async def handle_oauth_callback(self, code: str, state: str) -> bool:
        """
        Handle OAuth callback and save tokens to database
        
        Args:
            code: Authorization code from OAuth callback
            state: State parameter from OAuth callback
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract admin_user_id from state
            if ':' not in state:
                raise Exception("Invalid state parameter format")
            
            admin_user_id = state.split(':')[0]
            logger.info(f"🔄 Processing OAuth callback for admin user {admin_user_id}")
            
            # Exchange authorization code for tokens
            token_data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://oauth2.googleapis.com/token',
                    data=token_data,
                    timeout=10
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"❌ Token exchange failed: {error_text}")
                        return False
                    
                    tokens = await response.json()
            
            # Calculate expiry time
            expires_in = tokens.get('expires_in', 3600)
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
            
            # Store tokens in database
            token_doc = {
                'admin_user_id': admin_user_id,
                'access_token': tokens['access_token'],
                'refresh_token': tokens.get('refresh_token'),  # Critical for persistent access
                'token_uri': self.client_config["web"]["token_uri"],
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scopes': self.scopes,
                'expiry': expires_at.isoformat(),
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Upsert to handle re-authorization
            await self.db.google_tokens.update_one(
                {'admin_user_id': admin_user_id},
                {'$set': token_doc},
                upsert=True
            )
            
            logger.info(f"✅ OAuth tokens saved for admin user {admin_user_id}")
            logger.info(f"   - Access token: {tokens['access_token'][:20]}...")
            logger.info(f"   - Refresh token: {'Available' if tokens.get('refresh_token') else 'Not available'}")
            logger.info(f"   - Expires at: {expires_at.isoformat()}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to handle OAuth callback: {str(e)}")
            return False
    
    async def get_credentials(self, admin_user_id: str) -> Credentials:
        """
        Get valid credentials, refreshing if needed
        
        Args:
            admin_user_id: Admin user ID
            
        Returns:
            Valid Google credentials
            
        Raises:
            Exception if no tokens found or refresh fails
        """
        try:
            # Get tokens from database
            token_doc = await self.db.google_tokens.find_one({'admin_user_id': admin_user_id})
            
            if not token_doc:
                raise Exception("Google authentication required. Please connect your Google account first.")
            
            # Parse expiry time
            expiry_str = token_doc.get('expiry')
            if expiry_str:
                expiry_time = datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
            else:
                # If no expiry, assume expired
                expiry_time = datetime.now(timezone.utc) - timedelta(minutes=1)
            
            # Create credentials object
            credentials = Credentials(
                token=token_doc['access_token'],
                refresh_token=token_doc.get('refresh_token'),
                token_uri=token_doc['token_uri'],
                client_id=token_doc['client_id'],
                client_secret=token_doc['client_secret'],
                scopes=token_doc['scopes'],
                expiry=expiry_time
            )
            
            # Check if token is expired or will expire soon
            now = datetime.now(timezone.utc)
            if credentials.expired and credentials.refresh_token:
                logger.info(f"🔄 Token expired for admin {admin_user_id}, refreshing...")
                
                # Refresh the token
                from google.auth.transport.requests import Request
                credentials.refresh(Request())
                
                # Update database with new access token
                new_expiry = credentials.expiry.isoformat() if credentials.expiry else None
                await self.db.google_tokens.update_one(
                    {'admin_user_id': admin_user_id},
                    {'$set': {
                        'access_token': credentials.token,
                        'expiry': new_expiry,
                        'updated_at': datetime.now(timezone.utc).isoformat()
                    }}
                )
                
                logger.info(f"✅ Token refreshed successfully for admin {admin_user_id}")
            
            return credentials
            
        except Exception as e:
            logger.error(f"❌ Failed to get valid credentials for admin {admin_user_id}: {str(e)}")
            raise
    
    async def get_connection_status(self, admin_user_id: str) -> Dict[str, Any]:
        """
        Check connection status for admin user
        
        Args:
            admin_user_id: Admin user ID
            
        Returns:
            Connection status details
        """
        try:
            token_doc = await self.db.google_tokens.find_one({'admin_user_id': admin_user_id})
            
            if not token_doc:
                return {
                    'connected': False,
                    'is_expired': True,
                    'message': 'Not connected to Google'
                }
            
            # Parse expiry
            expiry_str = token_doc.get('expiry')
            is_expired = True
            if expiry_str:
                try:
                    expiry_time = datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
                    is_expired = expiry_time <= datetime.now(timezone.utc)
                except:
                    is_expired = True
            
            return {
                'connected': True,
                'is_expired': is_expired,
                'has_refresh_token': bool(token_doc.get('refresh_token')),
                'scopes': token_doc.get('scopes', []),
                'created_at': token_doc.get('created_at'),
                'updated_at': token_doc.get('updated_at'),
                'expiry': expiry_str
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get connection status: {str(e)}")
            return {
                'connected': False,
                'is_expired': True,
                'error': str(e)
            }
    
    async def disconnect(self, admin_user_id: str) -> bool:
        """
        Disconnect Google account by deleting tokens
        
        Args:
            admin_user_id: Admin user ID
            
        Returns:
            True if successful
        """
        try:
            result = await self.db.google_tokens.delete_one({'admin_user_id': admin_user_id})
            logger.info(f"✅ Disconnected Google for admin {admin_user_id} (deleted {result.deleted_count} documents)")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to disconnect Google: {str(e)}")
            return False
    
    # API Service Builders
    async def get_gmail_service(self, admin_user_id: str):
        """Get authenticated Gmail API service"""
        credentials = await self.get_credentials(admin_user_id)
        return build('gmail', 'v1', credentials=credentials)
    
    async def get_calendar_service(self, admin_user_id: str):
        """Get authenticated Calendar API service"""
        credentials = await self.get_credentials(admin_user_id)
        return build('calendar', 'v3', credentials=credentials)
    
    async def get_drive_service(self, admin_user_id: str):
        """Get authenticated Drive API service"""
        credentials = await self.get_credentials(admin_user_id)
        return build('drive', 'v3', credentials=credentials)
    
    async def get_sheets_service(self, admin_user_id: str):
        """Get authenticated Sheets API service"""
        credentials = await self.get_credentials(admin_user_id)
        return build('sheets', 'v4', credentials=credentials)


# Global instance - initialized in server.py
google_oauth_service: Optional[GoogleOAuthService] = None


def get_google_oauth_service(db: AsyncIOMotorDatabase) -> GoogleOAuthService:
    """Get or create Google OAuth service instance"""
    global google_oauth_service
    if google_oauth_service is None:
        google_oauth_service = GoogleOAuthService(db)
    return google_oauth_service


# Helper functions for Gmail API operations
async def list_gmail_messages(admin_user_id: str, db: AsyncIOMotorDatabase, max_results: int = 10) -> List[Dict]:
    """List Gmail messages using OAuth"""
    try:
        service_instance = get_google_oauth_service(db)
        gmail_service = await service_instance.get_gmail_service(admin_user_id)
        
        # Get message list
        results = gmail_service.users().messages().list(
            userId='me',
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        
        # Get detailed message info
        detailed_messages = []
        for msg in messages:
            try:
                message = gmail_service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                # Parse message for frontend
                headers = {h['name']: h['value'] for h in message['payload'].get('headers', [])}
                
                detailed_messages.append({
                    'id': message['id'],
                    'threadId': message['threadId'],
                    'subject': headers.get('Subject', ''),
                    'sender': headers.get('From', ''),
                    'date': headers.get('Date', ''),
                    'snippet': message.get('snippet', ''),
                    'labels': message.get('labelIds', [])
                })
                
            except Exception as e:
                logger.error(f"Failed to fetch message {msg['id']}: {e}")
        
        logger.info(f"✅ Retrieved {len(detailed_messages)} Gmail messages via OAuth")
        return detailed_messages
        
    except Exception as e:
        logger.error(f"❌ Failed to list Gmail messages: {str(e)}")
        return []


async def list_calendar_events(admin_user_id: str, db: AsyncIOMotorDatabase, max_results: int = 10) -> List[Dict]:
    """List Calendar events using OAuth"""
    try:
        service_instance = get_google_oauth_service(db)
        calendar_service = await service_instance.get_calendar_service(admin_user_id)
        
        # Get events from primary calendar
        now = datetime.utcnow().isoformat() + 'Z'
        
        events_result = calendar_service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        logger.info(f"✅ Retrieved {len(events)} calendar events via OAuth")
        return events
        
    except Exception as e:
        logger.error(f"❌ Failed to list calendar events: {str(e)}")
        return []


async def list_drive_files(admin_user_id: str, db: AsyncIOMotorDatabase, folder_id: str = None, max_results: int = 20) -> List[Dict]:
    """List Drive files using OAuth"""
    try:
        service_instance = get_google_oauth_service(db)
        drive_service = await service_instance.get_drive_service(admin_user_id)
        
        # Build query
        query = "trashed=false"
        if folder_id:
            query += f" and '{folder_id}' in parents"
        
        results = drive_service.files().list(
            q=query,
            pageSize=max_results,
            fields="files(id, name, mimeType, modifiedTime, size, webViewLink)"
        ).execute()
        
        files = results.get('files', [])
        
        logger.info(f"✅ Retrieved {len(files)} drive files via OAuth")
        return files
        
    except Exception as e:
        logger.error(f"❌ Failed to list drive files: {str(e)}")
        return []


async def send_gmail_message(admin_user_id: str, db: AsyncIOMotorDatabase, to: str, subject: str, body: str) -> Dict[str, Any]:
    """Send Gmail message using OAuth"""
    try:
        service_instance = get_google_oauth_service(db)
        gmail_service = await service_instance.get_gmail_service(admin_user_id)
        
        # Create message
        from email.mime.text import MIMEText
        import base64
        
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        # Send message
        result = gmail_service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        logger.info(f"✅ Sent Gmail message via OAuth to {to}")
        return {'success': True, 'message_id': result['id']}
        
    except Exception as e:
        logger.error(f"❌ Failed to send Gmail message: {str(e)}")
        return {'success': False, 'error': str(e)}