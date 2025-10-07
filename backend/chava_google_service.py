"""
Chava Palma Google OAuth Service - Persistent Authentication
Manages Google OAuth for chavapalmarubin@gmail.com with proper token persistence
"""

import os
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
import io

logger = logging.getLogger(__name__)

class ChavaGoogleService:
    """
    Google OAuth service specifically for chavapalmarubin@gmail.com
    Handles persistent authentication with proper refresh token management
    """
    
    def __init__(self, mongodb_instance=None):
        self.db = mongodb_instance
        self.client_id = os.environ.get('GOOGLE_CLIENT_ID')
        self.client_secret = os.environ.get('GOOGLE_CLIENT_SECRET') 
        self.redirect_uri = os.environ.get('GOOGLE_OAUTH_REDIRECT_URI')
        
        # Chava's email
        self.chava_email = "chavapalmarubin@gmail.com"
        
        # Scopes needed for Drive, Gmail, Calendar
        self.scopes = [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.events',
            'openid',
            'https://www.googleapis.com/auth/userinfo.profile', 
            'https://www.googleapis.com/auth/userinfo.email'
        ]
        
        logger.info(f"ChavaGoogleService initialized for {self.chava_email}")
    
    async def get_oauth_url(self) -> str:
        """Generate OAuth URL for Chava to authenticate"""
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "redirect_uris": [self.redirect_uri],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token"
                    }
                },
                scopes=self.scopes
            )
            flow.redirect_uri = self.redirect_uri
            
            auth_url, _ = flow.authorization_url(
                access_type='offline',  # Critical for refresh token
                include_granted_scopes='true',
                prompt='consent'  # Force consent to get refresh token
            )
            
            logger.info(f"Generated OAuth URL for {self.chava_email}")
            return auth_url
            
        except Exception as e:
            logger.error(f"Failed to generate OAuth URL: {str(e)}")
            raise
    
    async def exchange_code_for_tokens(self, code: str) -> Dict:
        """Exchange authorization code for tokens and store them"""
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "redirect_uris": [self.redirect_uri],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token"
                    }
                },
                scopes=self.scopes
            )
            flow.redirect_uri = self.redirect_uri
            
            # Exchange code for tokens
            flow.fetch_token(code=code)
            
            credentials = flow.credentials
            
            # Store tokens in database
            token_data = {
                "email": self.chava_email,
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_expiry": credentials.expiry.isoformat() if credentials.expiry else None,
                "scopes": credentials.scopes,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Save to MongoDB
            if self.db:
                await self.db.google_tokens.update_one(
                    {"email": self.chava_email},
                    {"$set": token_data},
                    upsert=True
                )
            
            logger.info(f"✅ Stored Google tokens for {self.chava_email}")
            
            return {
                "success": True,
                "email": self.chava_email,
                "access_token": credentials.token,
                "has_refresh_token": bool(credentials.refresh_token),
                "expiry": credentials.expiry.isoformat() if credentials.expiry else None
            }
            
        except Exception as e:
            logger.error(f"Failed to exchange code for tokens: {str(e)}")
            raise
    
    async def get_valid_credentials(self) -> Optional[Credentials]:
        """Get valid credentials, refreshing if needed"""
        try:
            if not self.db:
                logger.error("Database not available")
                return None
            
            # Get stored tokens
            token_doc = await self.db.google_tokens.find_one({"email": self.chava_email})
            if not token_doc:
                logger.error(f"No stored tokens for {self.chava_email}")
                return None
            
            # Create credentials object
            credentials = Credentials(
                token=token_doc['access_token'],
                refresh_token=token_doc.get('refresh_token'),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=token_doc.get('scopes', self.scopes)
            )
            
            # Check if token needs refresh
            if credentials.expired and credentials.refresh_token:
                logger.info(f"Refreshing expired token for {self.chava_email}")
                
                request = Request()
                credentials.refresh(request)
                
                # Update database with new token
                await self.db.google_tokens.update_one(
                    {"email": self.chava_email},
                    {"$set": {
                        "access_token": credentials.token,
                        "token_expiry": credentials.expiry.isoformat() if credentials.expiry else None,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
                
                logger.info(f"✅ Refreshed token for {self.chava_email}")
            
            return credentials
            
        except Exception as e:
            logger.error(f"Failed to get valid credentials: {str(e)}")
            return None
    
    async def upload_document_to_drive(self, file_content: bytes, filename: str, folder_id: str, mime_type: str = None) -> Dict:
        """Upload document to specific Google Drive folder"""
        try:
            credentials = await self.get_valid_credentials()
            if not credentials:
                raise Exception("No valid Google credentials available")
            
            drive_service = build('drive', 'v3', credentials=credentials)
            
            # Prepare file metadata
            file_metadata = {
                'name': filename,
                'parents': [folder_id] if folder_id else []
            }
            
            # Create media from file content
            media = MediaIoBaseUpload(
                io.BytesIO(file_content),
                mimetype=mime_type or 'application/octet-stream'
            )
            
            # Upload file
            file_result = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink,parents'
            ).execute()
            
            logger.info(f"✅ Uploaded {filename} to Drive folder {folder_id}")
            
            return {
                "success": True,
                "file_id": file_result.get('id'),
                "filename": file_result.get('name'),
                "web_view_link": file_result.get('webViewLink'),
                "folder_id": folder_id
            }
            
        except Exception as e:
            logger.error(f"Failed to upload to Drive: {str(e)}")
            raise
    
    async def get_connection_status(self) -> Dict:
        """Check if Chava's Google account is connected"""
        try:
            if self.db is None:
                return {"connected": False, "error": "Database not available"}
            
            token_doc = await self.db.google_tokens.find_one({"email": self.chava_email})
            
            if not token_doc:
                return {"connected": False, "email": self.chava_email}
            
            # Test if credentials are working
            credentials = await self.get_valid_credentials()
            if credentials:
                # Test with a simple API call
                drive_service = build('drive', 'v3', credentials=credentials)
                about = drive_service.about().get(fields="user").execute()
                
                return {
                    "connected": True,
                    "email": about['user']['emailAddress'],
                    "display_name": about['user'].get('displayName', ''),
                    "last_updated": token_doc.get('updated_at')
                }
            else:
                return {"connected": False, "error": "Invalid credentials"}
                
        except Exception as e:
            logger.error(f"Failed to check connection status: {str(e)}")
            return {"connected": False, "error": str(e)}
    
    async def create_client_folder(self, client_name: str) -> Dict:
        """Create a folder for a client in Chava's Drive"""
        try:
            credentials = await self.get_valid_credentials()
            if not credentials:
                raise Exception("No valid Google credentials available")
            
            drive_service = build('drive', 'v3', credentials=credentials)
            
            folder_name = f"{client_name} - FIDUS Documents"
            
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            folder = drive_service.files().create(
                body=folder_metadata,
                fields='id,name,webViewLink'
            ).execute()
            
            logger.info(f"✅ Created folder '{folder_name}' with ID: {folder['id']}")
            
            return {
                "success": True,
                "folder_id": folder['id'],
                "folder_name": folder['name'],
                "web_view_link": folder['webViewLink']
            }
            
        except Exception as e:
            logger.error(f"Failed to create client folder: {str(e)}")
            raise

# Global instance
chava_google_service = None

def get_chava_google_service(db_instance=None):
    """Get or create the Chava Google service instance"""
    global chava_google_service
    if chava_google_service is None or (db_instance and not chava_google_service.db):
        chava_google_service = ChavaGoogleService(db_instance)
    return chava_google_service