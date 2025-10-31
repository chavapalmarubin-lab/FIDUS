"""
REAL Google API Service using actual Google service account credentials
No more mock data - this uses your actual Google APIs
"""
import os
import json
import base64
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Import actual Google API libraries
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.auth.exceptions

logger = logging.getLogger(__name__)

class RealGoogleAPIService:
    """REAL Google API integration using your service account credentials"""
    
    def __init__(self):
        self.credentials = None
        self.gmail_service = None
        self.calendar_service = None
        self.drive_service = None
        self.authenticated = False
        self._initialize_credentials()
    
    def _initialize_credentials(self):
        """Initialize with your actual Google service account credentials"""
        try:
            credentials_path = '/app/backend/google-credentials.json'
            
            if not os.path.exists(credentials_path):
                logger.error("❌ Google credentials file not found")
                return
            
            # Define required scopes for full Google Workspace access
            scopes = [
                'https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.send',
                'https://www.googleapis.com/auth/gmail.compose',
                'https://www.googleapis.com/auth/gmail.modify',
                'https://www.googleapis.com/auth/drive',
                'https://www.googleapis.com/auth/drive.file',
                'https://www.googleapis.com/auth/calendar',
                'https://www.googleapis.com/auth/calendar.events',
            ]
            
            # Load service account credentials
            self.credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=scopes
            )
            
            # Build actual Google API services
            self.gmail_service = build('gmail', 'v1', credentials=self.credentials)
            self.calendar_service = build('calendar', 'v3', credentials=self.credentials)
            self.drive_service = build('drive', 'v3', credentials=self.credentials)
            
            self.authenticated = True
            logger.info("✅ REAL Google API services initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Google API services: {str(e)}")
            self.authenticated = False
    
    def test_connection(self) -> Dict[str, Any]:
        """Test actual Google API connections"""
        if not self.authenticated:
            return {
                "success": False,
                "error": "Google APIs not authenticated",
                "services": {
                    "gmail": {"status": "failed"},
                    "calendar": {"status": "failed"},
                    "drive": {"status": "failed"}
                }
            }
        
        results = {"gmail": {}, "calendar": {}, "drive": {}}
        
        # Test Gmail
        try:
            profile = self.gmail_service.users().getProfile(userId='me').execute()
            results["gmail"] = {
                "status": "connected",
                "email": profile.get('emailAddress'),
                "messages_total": profile.get('messagesTotal', 0)
            }
            logger.info(f"✅ Gmail connected: {profile.get('emailAddress')}")
        except Exception as e:
            results["gmail"] = {"status": "failed", "error": str(e)}
            logger.error(f"❌ Gmail connection failed: {str(e)}")
        
        # Test Calendar
        try:
            calendar_list = self.calendar_service.calendarList().list().execute()
            primary_calendar = None
            for cal in calendar_list.get('items', []):
                if cal.get('primary'):
                    primary_calendar = cal
                    break
                    
            results["calendar"] = {
                "status": "connected",
                "primary_calendar": primary_calendar.get('summary') if primary_calendar else 'Primary',
                "calendars_count": len(calendar_list.get('items', []))
            }
            logger.info(f"✅ Calendar connected: {len(calendar_list.get('items', []))} calendars")
        except Exception as e:
            results["calendar"] = {"status": "failed", "error": str(e)}
            logger.error(f"❌ Calendar connection failed: {str(e)}")
        
        # Test Drive
        try:
            about = self.drive_service.about().get(fields='user,storageQuota').execute()
            user_info = about.get('user', {})
            storage = about.get('storageQuota', {})
            
            results["drive"] = {
                "status": "connected",
                "user_email": user_info.get('emailAddress'),
                "display_name": user_info.get('displayName'),
                "storage_used": storage.get('usage', '0'),
                "storage_limit": storage.get('limit', '0')
            }
            logger.info(f"✅ Drive connected: {user_info.get('emailAddress')}")
        except Exception as e:
            results["drive"] = {"status": "failed", "error": str(e)}
            logger.error(f"❌ Drive connection failed: {str(e)}")
        
        # Overall success
        all_connected = all(service.get("status") == "connected" for service in results.values())
        
        return {
            "success": all_connected,
            "services": results,
            "message": "All Google APIs connected successfully" if all_connected else "Some Google APIs failed"
        }
    
    def get_real_emails(self, max_results: int = 50) -> Dict[str, Any]:
        """Get REAL emails from Gmail API"""
        if not self.authenticated:
            return {"success": False, "error": "Not authenticated", "emails": []}
        
        try:
            # Get message IDs
            results = self.gmail_service.users().messages().list(
                userId='me',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            # Get full message details
            for msg in messages[:10]:  # Limit to 10 for performance
                message = self.gmail_service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                # Extract headers
                headers = message['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'No Date')
                to = next((h['value'] for h in headers if h['name'] == 'To'), 'Unknown Recipient')
                
                # Get body
                body = self._extract_message_body(message['payload'])
                
                emails.append({
                    'id': msg['id'],
                    'threadId': message.get('threadId'),
                    'subject': subject,
                    'sender': sender,
                    'recipient': to,
                    'date': date,
                    'snippet': message.get('snippet', ''),
                    'body': body,
                    'read': 'UNREAD' not in message.get('labelIds', []),
                    'starred': 'STARRED' in message.get('labelIds', [])
                })
            
            logger.info(f"✅ Retrieved {len(emails)} real emails from Gmail")
            return {
                "success": True,
                "emails": emails,
                "total": len(messages)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get real emails: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "emails": []
            }
    
    def _extract_message_body(self, payload):
        """Extract email body from Gmail API payload"""
        body = ""
        
        if 'body' in payload and payload['body'].get('data'):
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        elif 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
                elif part['mimeType'] == 'text/html' and 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
        
        return body
    
    def send_real_email(self, to_email: str, subject: str, body: str, from_email: str = None) -> Dict[str, Any]:
        """Send REAL email via Gmail API"""
        if not self.authenticated:
            return {"success": False, "error": "Not authenticated"}
        
        try:
            # Create message
            message = MIMEMultipart()
            message['to'] = to_email
            message['from'] = from_email or 'fidus-gmail-service@shaped-canyon-470822-b3.iam.gserviceaccount.com'
            message['subject'] = subject
            
            # Add body
            if body.startswith('<'):
                message.attach(MIMEText(body, 'html'))
            else:
                message.attach(MIMEText(body, 'plain'))
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send via Gmail API
            send_message = self.gmail_service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            logger.info(f"✅ REAL email sent to {to_email}, Message ID: {send_message['id']}")
            return {
                "success": True,
                "message_id": send_message['id'],
                "to": to_email,
                "subject": subject
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to send real email: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

# Create global instance
real_google_api = RealGoogleAPIService()