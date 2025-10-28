"""
Gmail API Service
Send and receive emails through Google Gmail API
"""

import logging
from typing import List, Optional, Dict
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class GmailService:
    """Gmail API operations for FIDUS"""
    
    def __init__(self, token_manager):
        self.token_manager = token_manager
        logger.info("✅ Gmail Service initialized")
    
    async def _get_service(self, user_id: str):
        """Get authenticated Gmail service"""
        tokens = await self.token_manager.get_tokens(user_id)
        
        if not tokens:
            raise ValueError("No Google account connected")
        
        credentials = Credentials(
            token=tokens['access_token'],
            refresh_token=tokens.get('refresh_token'),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.token_manager.client_id,
            client_secret=self.token_manager.client_secret
        )
        
        return build('gmail', 'v1', credentials=credentials)
    
    async def send_email(
        self,
        user_id: str,
        to: str,
        subject: str,
        body: str,
        body_html: Optional[str] = None
    ) -> Dict:
        """
        Send email via Gmail
        
        Args:
            user_id: Admin user ID
            to: Recipient email
            subject: Email subject
            body: Plain text body
            body_html: HTML body (optional)
            
        Returns:
            Message info
        """
        try:
            logger.info(f"📧 Sending email to {to}")
            
            service = await self._get_service(user_id)
            
            # Create message
            message = MIMEMultipart('alternative')
            message['To'] = to
            message['Subject'] = subject
            
            # Add plain text
            message.attach(MIMEText(body, 'plain'))
            
            # Add HTML if provided
            if body_html:
                message.attach(MIMEText(body_html, 'html'))
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode('utf-8')
            
            # Send
            result = service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            logger.info(f"✅ Email sent: {result['id']}")
            
            return {
                "success": True,
                "message_id": result['id'],
                "to": to,
                "subject": subject
            }
            
        except HttpError as e:
            logger.error(f"❌ Gmail API error: {str(e)}")
            raise ValueError(f"Failed to send email: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Send email failed: {str(e)}")
            raise ValueError(f"Failed to send email: {str(e)}")
    
    async def list_messages(
        self,
        user_id: str,
        max_results: int = 20,
        query: Optional[str] = None
    ) -> List[Dict]:
        """
        List Gmail messages
        
        Args:
            user_id: Admin user ID
            max_results: Max messages to return
            query: Gmail search query
            
        Returns:
            List of messages
        """
        try:
            logger.info(f"📬 Listing messages for user {user_id}")
            
            service = await self._get_service(user_id)
            
            # List messages
            results = service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=query
            ).execute()
            
            messages = results.get('messages', [])
            
            logger.info(f"✅ Found {len(messages)} messages")
            
            # Get full message details
            full_messages = []
            for msg in messages:
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'  # ✅ Changed from 'metadata' to 'full' to get body content
                ).execute()
                
                # Extract headers
                headers = message['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
                
                # Extract message body
                body = ""
                if 'parts' in message['payload']:
                    # Multipart message
                    for part in message['payload']['parts']:
                        if part['mimeType'] == 'text/plain' or part['mimeType'] == 'text/html':
                            if 'data' in part['body']:
                                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                                break
                elif 'body' in message['payload'] and 'data' in message['payload']['body']:
                    # Simple message
                    body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
                
                full_messages.append({
                    "id": message['id'],
                    "thread_id": message['threadId'],
                    "subject": subject,
                    "from": from_email,
                    "date": date,
                    "snippet": message['snippet'],
                    "body": body  # ✅ Now includes full body content
                })
            
            return full_messages
            
        except HttpError as e:
            logger.error(f"❌ Gmail API error: {str(e)}")
            raise ValueError(f"Failed to list messages: {str(e)}")
        except Exception as e:
            logger.error(f"❌ List messages failed: {str(e)}")
            raise ValueError(f"Failed to list messages: {str(e)}")
