"""
FIDUS Google API Service
Handles Gmail, Drive, Calendar, and Meet integration
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

logger = logging.getLogger(__name__)

class GoogleAPIService:
    """Complete Google API integration for FIDUS CRM"""
    
    def __init__(self):
        """Initialize Google API service with service account credentials"""
        self.credentials_path = "/app/backend/google-credentials.json"
        self.scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.events'
        ]
        
        # Initialize services
        self.credentials = None
        self.gmail_service = None
        self.drive_service = None
        self.calendar_service = None
        
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google APIs using service account"""
        try:
            logger.info("🔐 Authenticating with Google APIs...")
            
            # Load service account credentials
            self.credentials = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=self.scopes
            )
            
            # Build API services
            self.gmail_service = build('gmail', 'v1', credentials=self.credentials)
            self.drive_service = build('drive', 'v3', credentials=self.credentials)
            self.calendar_service = build('calendar', 'v3', credentials=self.credentials)
            
            logger.info("✅ Google APIs authenticated successfully")
            
        except Exception as e:
            logger.error(f"❌ Google API authentication failed: {str(e)}")
            raise Exception(f"Failed to authenticate with Google APIs: {str(e)}")
    
    # ==================== GMAIL API METHODS ====================
    
    def send_email(self, to_email: str, subject: str, body: str, from_email: str = None) -> Dict[str, Any]:
        """Send email via Gmail API"""
        try:
            logger.info(f"📧 Sending email to {to_email}")
            
            # Create message
            message = MIMEMultipart()
            message['to'] = to_email
            message['from'] = from_email or "fidus-gmail-service@shaped-canyon-470822-b3.iam.gserviceaccount.com"
            message['subject'] = subject
            
            # Attach body
            message.attach(MIMEText(body, 'html'))
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send email
            send_message = self.gmail_service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            logger.info(f"✅ Email sent successfully. Message ID: {send_message['id']}")
            return {
                "success": True,
                "message_id": send_message['id'],
                "to": to_email,
                "subject": subject
            }
            
        except HttpError as e:
            logger.error(f"❌ Gmail API error: {str(e)}")
            return {
                "success": False,
                "error": f"Gmail API error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"❌ Email sending failed: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to send email: {str(e)}"
            }
    
    def get_emails(self, max_results: int = 10) -> Dict[str, Any]:
        """Fetch recent emails from Gmail"""
        try:
            logger.info(f"📬 Fetching {max_results} recent emails...")
            
            # Get message list
            results = self.gmail_service.users().messages().list(
                userId='me',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            email_list = []
            
            # Get email details
            for message in messages:
                msg = self.gmail_service.users().messages().get(
                    userId='me', 
                    id=message['id']
                ).execute()
                
                # Extract email details
                payload = msg['payload']
                headers = payload.get('headers', [])
                
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'No Date')
                
                # Get snippet
                snippet = msg.get('snippet', '')
                
                email_list.append({
                    'id': message['id'],
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'snippet': snippet
                })
            
            logger.info(f"✅ Retrieved {len(email_list)} emails")
            return {
                "success": True,
                "emails": email_list,
                "total": len(email_list)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch emails: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to fetch emails: {str(e)}"
            }
    
    # ==================== GOOGLE DRIVE API METHODS ====================
    
    def upload_file(self, file_name: str, file_content: bytes, mime_type: str = 'application/pdf') -> Dict[str, Any]:
        """Upload file to Google Drive"""
        try:
            logger.info(f"📁 Uploading file: {file_name}")
            
            file_metadata = {'name': file_name}
            
            # Upload file
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=file_content,
                fields='id'
            ).execute()
            
            logger.info(f"✅ File uploaded successfully. File ID: {file.get('id')}")
            return {
                "success": True,
                "file_id": file.get('id'),
                "file_name": file_name
            }
            
        except Exception as e:
            logger.error(f"❌ File upload failed: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to upload file: {str(e)}"
            }
    
    def list_files(self, max_results: int = 10) -> Dict[str, Any]:
        """List files from Google Drive"""
        try:
            logger.info(f"📂 Listing {max_results} files from Google Drive...")
            
            results = self.drive_service.files().list(
                pageSize=max_results,
                fields="nextPageToken, files(id, name, mimeType, createdTime, size)"
            ).execute()
            
            files = results.get('files', [])
            
            logger.info(f"✅ Retrieved {len(files)} files")
            return {
                "success": True,
                "files": files,
                "total": len(files)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to list files: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to list files: {str(e)}"
            }
    
    # ==================== GOOGLE CALENDAR API METHODS ====================
    
    def create_meeting(self, title: str, description: str, attendee_emails: List[str], 
                      start_time: str, end_time: str) -> Dict[str, Any]:
        """Create Google Calendar event with Meet link"""
        try:
            logger.info(f"📅 Creating calendar event: {title}")
            
            # Create event
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'UTC'
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'UTC'
                },
                'attendees': [{'email': email} for email in attendee_emails],
                'conferenceData': {
                    'createRequest': {
                        'requestId': f"meet-{datetime.now().isoformat()}"
                    }
                }
            }
            
            # Create the event
            event = self.calendar_service.events().insert(
                calendarId='primary',
                body=event,
                conferenceDataVersion=1
            ).execute()
            
            # Get Meet link
            meet_link = None
            if 'conferenceData' in event and 'entryPoints' in event['conferenceData']:
                for entry in event['conferenceData']['entryPoints']:
                    if entry['entryPointType'] == 'video':
                        meet_link = entry['uri']
                        break
            
            logger.info(f"✅ Calendar event created successfully. Event ID: {event['id']}")
            return {
                "success": True,
                "event_id": event['id'],
                "event_link": event.get('htmlLink'),
                "meet_link": meet_link,
                "title": title
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create calendar event: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to create calendar event: {str(e)}"
            }
    
    def get_calendar_events(self, max_results: int = 10) -> Dict[str, Any]:
        """Get upcoming calendar events"""
        try:
            logger.info(f"📅 Fetching {max_results} upcoming events...")
            
            # Get current time
            now = datetime.utcnow().isoformat() + 'Z'
            
            # Fetch events
            events_result = self.calendar_service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            event_list = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                event_list.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No Title'),
                    'start': start,
                    'description': event.get('description', ''),
                    'attendees': event.get('attendees', [])
                })
            
            logger.info(f"✅ Retrieved {len(event_list)} calendar events")
            return {
                "success": True,
                "events": event_list,
                "total": len(event_list)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch calendar events: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to fetch calendar events: {str(e)}"
            }
    
    # ==================== TEST METHODS ====================
    
    def test_connection(self) -> Dict[str, Any]:
        """Test all Google API connections"""
        try:
            logger.info("🧪 Testing Google API connections...")
            
            results = {}
            
            # Test Gmail
            try:
                profile = self.gmail_service.users().getProfile(userId='me').execute()
                results['gmail'] = {
                    "status": "connected",
                    "email": profile.get('emailAddress'),
                    "messages_total": profile.get('messagesTotal', 0)
                }
            except Exception as e:
                results['gmail'] = {"status": "failed", "error": str(e)}
            
            # Test Drive
            try:
                drive_info = self.drive_service.about().get(fields='user').execute()
                results['drive'] = {
                    "status": "connected",
                    "user": drive_info.get('user', {}).get('emailAddress')
                }
            except Exception as e:
                results['drive'] = {"status": "failed", "error": str(e)}
            
            # Test Calendar
            try:
                calendar_list = self.calendar_service.calendarList().list().execute()
                results['calendar'] = {
                    "status": "connected",
                    "calendars": len(calendar_list.get('items', []))
                }
            except Exception as e:
                results['calendar'] = {"status": "failed", "error": str(e)}
            
            # Overall status
            all_connected = all(service.get("status") == "connected" for service in results.values())
            
            logger.info(f"🧪 Connection test completed. All services connected: {all_connected}")
            
            return {
                "success": all_connected,
                "services": results,
                "message": "All Google APIs connected successfully" if all_connected else "Some Google APIs failed to connect"
            }
            
        except Exception as e:
            logger.error(f"❌ Connection test failed: {str(e)}")
            return {
                "success": False,
                "error": f"Connection test failed: {str(e)}"
            }

# Global instance
google_api = GoogleAPIService()