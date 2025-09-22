"""
Real Google APIs Integration Service
Provides Gmail, Calendar, Drive, and Meet API functionality with OAuth 2.0
"""

import os
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Any
import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.auth.exceptions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleAPIsService:
    """
    Comprehensive Google APIs service for FIDUS investment management platform
    Handles Gmail, Calendar, Drive, and Meet integrations
    """
    
    def __init__(self):
        self.client_id = os.environ.get('GOOGLE_CLIENT_ID')
        self.client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
        self.redirect_uri = os.environ.get('GOOGLE_OAUTH_REDIRECT_URI')
        
        # Debug logging
        logger.info(f"GoogleAPIsService init - client_id: {self.client_id is not None}")
        logger.info(f"GoogleAPIsService init - client_secret: {self.client_secret is not None}")
        logger.info(f"GoogleAPIsService init - redirect_uri: {self.redirect_uri}")
        
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            logger.error(f"Missing Google OAuth credentials: client_id={self.client_id is not None}, client_secret={self.client_secret is not None}, redirect_uri={self.redirect_uri}")
        
        # Required scopes for all Google services
        self.scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send', 
            'https://www.googleapis.com/auth/gmail.compose',
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.events',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive.metadata.readonly',
            'https://www.googleapis.com/auth/meetings.space.created',
            'https://www.googleapis.com/auth/meetings.space.readonly'
        ]
        
        logger.info("Google APIs Service initialized with comprehensive scopes")
    
    def reinitialize_with_env(self):
        """Reinitialize the service with environment variables after they are loaded"""
        self.client_id = os.environ.get('GOOGLE_CLIENT_ID')
        self.client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
        self.redirect_uri = os.environ.get('GOOGLE_OAUTH_REDIRECT_URI')
        
        logger.info(f"GoogleAPIsService reinit - client_id: {self.client_id is not None}")
        logger.info(f"GoogleAPIsService reinit - client_secret: {self.client_secret is not None}")
        logger.info(f"GoogleAPIsService reinit - redirect_uri: {self.redirect_uri}")
        
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            logger.error(f"Missing Google OAuth credentials after reinit: client_id={self.client_id is not None}, client_secret={self.client_secret is not None}, redirect_uri={self.redirect_uri}")
        else:
            logger.info("Google APIs Service reinitialized successfully with environment variables")
    
    def generate_oauth_url(self, state: str = None) -> str:
        """
        Generate Google OAuth URL for user authentication
        
        Args:
            state: Optional state parameter for security
            
        Returns:
            OAuth authorization URL
        """
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri]
                    }
                },
                scopes=self.scopes
            )
            
            flow.redirect_uri = self.redirect_uri
            
            authorization_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent',
                state=state
            )
            
            logger.info(f"Generated OAuth URL for Google APIs integration")
            return authorization_url
            
        except Exception as e:
            logger.error(f"Failed to generate OAuth URL: {str(e)}")
            raise Exception(f"OAuth URL generation failed: {str(e)}")
    
    def exchange_code_for_tokens(self, authorization_code: str) -> Dict[str, str]:
        """
        Exchange authorization code for access and refresh tokens
        
        Args:
            authorization_code: Authorization code from OAuth callback
            
        Returns:
            Dictionary containing tokens and user info
        """
        try:
            # Create flow without fixed scopes to allow Google to return whatever scopes were granted
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri]
                    }
                },
                scopes=None  # Don't enforce scopes during token exchange
            )
            
            flow.redirect_uri = self.redirect_uri
            
            # Fetch token without scope validation
            flow.fetch_token(code=authorization_code)
            
            credentials = flow.credentials
            
            # Get user info
            user_info = self._get_user_info(credentials)
            
            # Log the actual scopes returned by Google
            actual_scopes = credentials.scopes or []
            logger.info(f"Google returned scopes: {actual_scopes}")
            
            token_data = {
                'access_token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': actual_scopes,  # Use actual scopes returned by Google
                'expiry': credentials.expiry.isoformat() if credentials.expiry else None,
                'user_info': user_info
            }
            
            logger.info(f"Successfully exchanged code for tokens: {user_info.get('email')}")
            return token_data
            
        except Exception as e:
            logger.error(f"Token exchange failed: {str(e)}")
            raise Exception(f"Failed to exchange authorization code: {str(e)}")
    
    def _get_user_info(self, credentials: Credentials) -> Dict[str, Any]:
        """Get user information from Google OAuth"""
        try:
            oauth_service = build('oauth2', 'v2', credentials=credentials)
            user_info = oauth_service.userinfo().get().execute()
            
            return {
                'id': user_info.get('id'),
                'email': user_info.get('email'),
                'name': user_info.get('name'),
                'picture': user_info.get('picture'),
                'verified_email': user_info.get('verified_email')
            }
            
        except Exception as e:
            logger.error(f"Failed to get user info: {str(e)}")
            return {}
    
    def _get_credentials(self, token_data: Dict[str, str]) -> Credentials:
        """
        Create credentials object from stored token data
        
        Args:
            token_data: Dictionary containing token information
            
        Returns:
            Google credentials object
        """
        try:
            expiry = None
            if token_data.get('expiry'):
                expiry = datetime.fromisoformat(token_data['expiry'].replace('Z', '+00:00'))
            
            credentials = Credentials(
                token=token_data['access_token'],
                refresh_token=token_data.get('refresh_token'),
                token_uri=token_data.get('token_uri'),
                client_id=token_data.get('client_id'),
                client_secret=token_data.get('client_secret'),
                scopes=token_data.get('scopes'),
                expiry=expiry
            )
            
            # Refresh token if expired
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            
            return credentials
            
        except Exception as e:
            logger.error(f"Failed to create credentials: {str(e)}")
            raise Exception(f"Invalid credentials: {str(e)}")
    
    # ==================== GMAIL API METHODS ====================
    
    async def get_gmail_messages(self, token_data: Dict[str, str], max_results: int = 20) -> List[Dict]:
        """
        Get Gmail messages using real Gmail API
        
        Args:
            token_data: OAuth token data
            max_results: Maximum number of messages to retrieve
            
        Returns:
            List of Gmail messages
        """
        try:
            credentials = self._get_credentials(token_data)
            gmail_service = build('gmail', 'v1', credentials=credentials)
            
            # Get message list
            results = gmail_service.users().messages().list(
                userId='me',
                maxResults=max_results,
                labelIds=['INBOX']
            ).execute()
            
            messages = results.get('messages', [])
            
            detailed_messages = []
            for message in messages:
                # Get detailed message info
                msg_detail = gmail_service.users().messages().get(
                    userId='me',
                    id=message['id']
                ).execute()
                
                # Extract headers
                headers = {}
                for header in msg_detail['payload'].get('headers', []):
                    headers[header['name']] = header['value']
                
                # Extract body
                body = self._extract_message_body(msg_detail['payload'])
                
                detailed_messages.append({
                    'id': msg_detail['id'],
                    'thread_id': msg_detail['threadId'],
                    'subject': headers.get('Subject', 'No Subject'),
                    'sender': headers.get('From', 'Unknown Sender'),
                    'to': headers.get('To', ''),
                    'date': headers.get('Date', ''),
                    'snippet': msg_detail.get('snippet', ''),
                    'body': body,
                    'unread': 'UNREAD' in msg_detail.get('labelIds', []),
                    'labels': msg_detail.get('labelIds', []),
                    'internal_date': msg_detail.get('internalDate'),
                    'real_gmail_api': True
                })
            
            logger.info(f"Retrieved {len(detailed_messages)} real Gmail messages")
            return detailed_messages
            
        except HttpError as e:
            logger.error(f"Gmail API error: {str(e)}")
            return [{
                'id': 'error_gmail',
                'subject': '⚠️ Gmail API Error',
                'sender': 'FIDUS System <system@fidus.com>',
                'snippet': f'Gmail API error: {str(e)}',
                'body': f'Error accessing Gmail: {str(e)}',
                'error': True
            }]
        except Exception as e:
            logger.error(f"Gmail integration error: {str(e)}")
            return [{
                'id': 'error_gmail',
                'subject': '⚠️ Gmail Integration Error',
                'sender': 'FIDUS System <system@fidus.com>',
                'snippet': f'Gmail error: {str(e)}',
                'body': f'Gmail integration error: {str(e)}',
                'error': True
            }]
    
    def _extract_message_body(self, payload: Dict) -> str:
        """Extract message body from Gmail payload"""
        try:
            # Try to get body from the main payload
            if payload.get('body', {}).get('data'):
                return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
            
            # Try to get from parts
            parts = payload.get('parts', [])
            for part in parts:
                if part.get('mimeType') == 'text/plain' and part.get('body', {}).get('data'):
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif part.get('mimeType') == 'text/html' and part.get('body', {}).get('data'):
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            
            return "Message body could not be decoded"
            
        except Exception as e:
            logger.error(f"Failed to extract message body: {str(e)}")
            return f"Error extracting message body: {str(e)}"
    
    async def send_gmail_message(self, token_data: Dict[str, str], to: str, subject: str, body: str, html_body: str = None) -> Dict:
        """
        Send email via Gmail API
        
        Args:
            token_data: OAuth token data
            to: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
            
        Returns:
            Send result dictionary
        """
        try:
            credentials = self._get_credentials(token_data)
            gmail_service = build('gmail', 'v1', credentials=credentials)
            
            # Create message
            if html_body:
                message = MIMEMultipart('alternative')
                message.attach(MIMEText(body, 'plain'))
                message.attach(MIMEText(html_body, 'html'))
            else:
                message = MIMEText(body)
            
            message['to'] = to
            message['subject'] = subject
            
            # Get sender email from user info
            user_info = token_data.get('user_info', {})
            sender_email = user_info.get('email', 'noreply@fidus.com')
            message['from'] = f"FIDUS Investment Management <{sender_email}>"
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send message
            send_result = gmail_service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            logger.info(f"Email sent successfully via Gmail API: {send_result['id']}")
            
            return {
                'success': True,
                'message_id': send_result['id'],
                'message': 'Email sent successfully via Gmail API',
                'api_used': 'gmail_api'
            }
            
        except Exception as e:
            logger.error(f"Gmail send error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'api_used': 'gmail_api'
            }
    
    # ==================== CALENDAR API METHODS ====================
    
    async def get_calendar_events(self, token_data: Dict[str, str], max_results: int = 20) -> List[Dict]:
        """
        Get Calendar events using real Calendar API
        
        Args:
            token_data: OAuth token data
            max_results: Maximum number of events to retrieve
            
        Returns:
            List of calendar events
        """
        try:
            credentials = self._get_credentials(token_data)
            calendar_service = build('calendar', 'v3', credentials=credentials)
            
            # Get events from primary calendar
            now = datetime.now(timezone.utc).isoformat()
            events_result = calendar_service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No Title'),
                    'description': event.get('description', ''),
                    'start': start,
                    'end': end,
                    'location': event.get('location', ''),
                    'attendees': [
                        {
                            'email': attendee.get('email'),
                            'displayName': attendee.get('displayName'),
                            'responseStatus': attendee.get('responseStatus')
                        }
                        for attendee in event.get('attendees', [])
                    ],
                    'status': event.get('status'),
                    'html_link': event.get('htmlLink'),
                    'real_calendar_api': True
                })
            
            logger.info(f"Retrieved {len(formatted_events)} calendar events")
            return formatted_events
            
        except Exception as e:
            logger.error(f"Calendar API error: {str(e)}")
            return [{
                'id': 'error_calendar',
                'summary': '⚠️ Calendar API Error',
                'description': f'Calendar API error: {str(e)}',
                'start': datetime.now(timezone.utc).isoformat(),
                'end': (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
                'error': True
            }]
    
    async def create_calendar_event(self, token_data: Dict[str, str], event_data: Dict) -> Dict:
        """
        Create a new calendar event
        
        Args:
            token_data: OAuth token data
            event_data: Event details
            
        Returns:
            Created event information
        """
        try:
            credentials = self._get_credentials(token_data)
            calendar_service = build('calendar', 'v3', credentials=credentials)
            
            event = calendar_service.events().insert(
                calendarId='primary',
                body=event_data
            ).execute()
            
            logger.info(f"Created calendar event: {event['id']}")
            
            return {
                'success': True,
                'event_id': event['id'],
                'html_link': event.get('htmlLink'),
                'message': 'Calendar event created successfully'
            }
            
        except Exception as e:
            logger.error(f"Calendar event creation error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # ==================== DRIVE API METHODS ====================
    
    async def get_drive_files(self, token_data: Dict[str, str], max_results: int = 20) -> List[Dict]:
        """
        Get Drive files using real Drive API
        
        Args:
            token_data: OAuth token data
            max_results: Maximum number of files to retrieve
            
        Returns:
            List of Drive files
        """
        try:
            credentials = self._get_credentials(token_data)
            drive_service = build('drive', 'v3', credentials=credentials)
            
            # Get files from Drive
            results = drive_service.files().list(
                pageSize=max_results,
                fields="nextPageToken, files(id, name, mimeType, size, modifiedTime, webViewLink, owners)"
            ).execute()
            
            files = results.get('files', [])
            
            formatted_files = []
            for file in files:
                formatted_files.append({
                    'id': file['id'],
                    'name': file['name'],
                    'mimeType': file.get('mimeType'),
                    'size': file.get('size'),
                    'modifiedTime': file.get('modifiedTime'),
                    'webViewLink': file.get('webViewLink'),
                    'owners': [
                        {
                            'displayName': owner.get('displayName'),
                            'emailAddress': owner.get('emailAddress')
                        }
                        for owner in file.get('owners', [])
                    ],
                    'real_drive_api': True
                })
            
            logger.info(f"Retrieved {len(formatted_files)} Drive files")
            return formatted_files
            
        except Exception as e:
            logger.error(f"Drive API error: {str(e)}")
            return [{
                'id': 'error_drive',
                'name': '⚠️ Drive API Error',
                'mimeType': 'application/error',
                'size': '0',
                'modifiedTime': datetime.now(timezone.utc).isoformat(),
                'error': True
            }]
    
    async def upload_drive_file(self, token_data: Dict[str, str], file_data: bytes, filename: str, mime_type: str) -> Dict:
        """
        Upload file to Google Drive
        
        Args:
            token_data: OAuth token data
            file_data: File content as bytes
            filename: Name of the file
            mime_type: MIME type of the file
            
        Returns:
            Upload result
        """
        try:
            credentials = self._get_credentials(token_data)
            drive_service = build('drive', 'v3', credentials=credentials)
            
            file_metadata = {'name': filename}
            
            from googleapiclient.http import MediaIoBaseUpload
            import io
            
            file_io = io.BytesIO(file_data)
            media = MediaIoBaseUpload(file_io, mimetype=mime_type)
            
            file_result = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            logger.info(f"Uploaded file to Drive: {file_result['id']}")
            
            return {
                'success': True,
                'file_id': file_result['id'],
                'web_view_link': file_result.get('webViewLink'),
                'message': 'File uploaded successfully to Google Drive'
            }
            
        except Exception as e:
            logger.error(f"Drive upload error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

# Global instance - lazy initialization to avoid environment variable issues
_google_apis_service = None

def get_google_apis_service():
    """Get or create Google APIs service instance"""
    global _google_apis_service
    if _google_apis_service is None:
        _google_apis_service = GoogleAPIsService()
    return _google_apis_service

# For backward compatibility - lazy initialization
def get_google_apis_service_instance():
    """Get Google APIs service instance for module-level access"""
    return get_google_apis_service()

# Use property-based access to ensure lazy initialization
class GoogleAPIsServiceModule:
    @property
    def google_apis_service(self):
        return get_google_apis_service()

# Create module-level accessor
_module = GoogleAPIsServiceModule()
google_apis_service = _module.google_apis_service