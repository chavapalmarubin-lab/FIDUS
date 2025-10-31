"""
Gmail API Service using Emergent Google Authentication
Provides Gmail functionality using Emergent's managed Google OAuth
"""

import aiohttp
import logging
from typing import Dict, List, Optional
import json
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class EmergentGmailService:
    """
    Gmail API service using Emergent authentication
    """
    
    def __init__(self):
        self.gmail_api_base = "https://gmail.googleapis.com/gmail/v1"
        
    async def get_gmail_messages(self, session_token: str, max_results: int = 20) -> List[Dict]:
        """
        Get Gmail messages using Emergent session token
        
        Args:
            session_token: Emergent session token
            max_results: Maximum number of messages to retrieve
            
        Returns:
            List of Gmail messages
        """
        try:
            # Use session token to make authenticated Gmail API calls
            headers = {
                'Authorization': f'Bearer {session_token}',
                'Content-Type': 'application/json'
            }
            
            # Get message list from Gmail API
            messages_url = f"{self.gmail_api_base}/users/me/messages"
            params = {
                'maxResults': max_results,
                'labelIds': 'INBOX'
            }
            
            async with aiohttp.ClientSession() as session:
                # Get message IDs
                async with session.get(messages_url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        messages = data.get('messages', [])
                        
                        # Get detailed message data for each message
                        detailed_messages = []
                        for msg in messages[:max_results]:  # Limit to max_results
                            try:
                                msg_url = f"{self.gmail_api_base}/users/me/messages/{msg['id']}"
                                async with session.get(msg_url, headers=headers) as msg_response:
                                    if msg_response.status == 200:
                                        msg_data = await msg_response.json()
                                        
                                        # Extract message details
                                        headers_data = {}
                                        for header in msg_data.get('payload', {}).get('headers', []):
                                            headers_data[header['name']] = header['value']
                                        
                                        # Extract body
                                        body = self._extract_message_body(msg_data.get('payload', {}))
                                        
                                        detailed_messages.append({
                                            'id': msg_data.get('id'),
                                            'thread_id': msg_data.get('threadId'),
                                            'subject': headers_data.get('Subject', 'No Subject'),
                                            'sender': headers_data.get('From', 'Unknown Sender'),
                                            'to': headers_data.get('To', ''),
                                            'date': headers_data.get('Date', ''),
                                            'snippet': msg_data.get('snippet', ''),
                                            'body': body,
                                            'unread': 'UNREAD' in msg_data.get('labelIds', []),
                                            'labels': msg_data.get('labelIds', []),
                                            'internal_date': msg_data.get('internalDate'),
                                            'source': 'emergent_gmail_api'
                                        })
                                        
                            except Exception as e:
                                logger.error(f"Error getting message {msg['id']}: {str(e)}")
                                continue
                        
                        logger.info(f"✅ Retrieved {len(detailed_messages)} Gmail messages via Emergent Auth")
                        return detailed_messages
                        
                    elif response.status == 401:
                        logger.error("Gmail API authentication failed - session token invalid")
                        return [{
                            'id': 'auth_error',
                            'subject': '🔐 Authentication Required',
                            'sender': 'FIDUS System <system@fidus.com>',
                            'snippet': 'Please reconnect your Google account to access Gmail.',
                            'body': 'Google authentication has expired. Click "Connect Google Workspace" to reconnect.',
                            'date': datetime.now(timezone.utc).isoformat(),
                            'unread': True,
                            'source': 'auth_error'
                        }]
                    else:
                        error_text = await response.text()
                        logger.error(f"Gmail API error: Status {response.status}, Response: {error_text}")
                        return [{
                            'id': 'api_error',
                            'subject': '⚠️ Gmail API Error',
                            'sender': 'FIDUS System <system@fidus.com>',
                            'snippet': f'Gmail API error: {response.status}',
                            'body': f'Error accessing Gmail: {error_text[:200]}',
                            'date': datetime.now(timezone.utc).isoformat(),
                            'unread': True,
                            'source': 'api_error'
                        }]
                        
        except Exception as e:
            logger.error(f"Error getting Gmail messages: {str(e)}")
            return [{
                'id': 'service_error',
                'subject': '❌ Gmail Service Error',
                'sender': 'FIDUS System <system@fidus.com>',
                'snippet': f'Service error: {str(e)}',
                'body': f'Gmail service encountered an error: {str(e)}',
                'date': datetime.now(timezone.utc).isoformat(),
                'unread': True,
                'source': 'service_error'
            }]
    
    def _extract_message_body(self, payload: Dict) -> str:
        """
        Extract message body from Gmail API payload
        
        Args:
            payload: Gmail message payload
            
        Returns:
            Message body as string
        """
        try:
            # Try to get plain text body
            if payload.get('body', {}).get('data'):
                import base64
                body_data = payload['body']['data']
                # Gmail API returns base64url-encoded data
                body_data = body_data.replace('-', '+').replace('_', '/')
                # Add padding if needed
                while len(body_data) % 4:
                    body_data += '='
                decoded_body = base64.b64decode(body_data).decode('utf-8', errors='ignore')
                return decoded_body
            
            # Try multipart
            if payload.get('parts'):
                for part in payload['parts']:
                    if part.get('mimeType') == 'text/plain' and part.get('body', {}).get('data'):
                        import base64
                        body_data = part['body']['data']
                        body_data = body_data.replace('-', '+').replace('_', '/')
                        while len(body_data) % 4:
                            body_data += '='
                        decoded_body = base64.b64decode(body_data).decode('utf-8', errors='ignore')
                        return decoded_body
            
            # Fallback to snippet
            return payload.get('snippet', 'Message body not available')
            
        except Exception as e:
            logger.error(f"Error extracting message body: {str(e)}")
            return 'Error extracting message body'
    
    async def send_gmail_message(self, session_token: str, to: str, subject: str, body: str) -> Dict:
        """
        Send Gmail message using Emergent session token
        
        Args:
            session_token: Emergent session token
            to: Recipient email
            subject: Email subject
            body: Email body
            
        Returns:
            Send result dictionary
        """
        try:
            import base64
            import email.mime.text
            import email.mime.multipart
            
            # Create email message
            msg = email.mime.multipart.MIMEMultipart()
            msg['to'] = to
            msg['subject'] = subject
            
            # Add body
            msg.attach(email.mime.text.MIMEText(body, 'plain'))
            
            # Convert to raw format for Gmail API
            raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
            
            headers = {
                'Authorization': f'Bearer {session_token}',
                'Content-Type': 'application/json'
            }
            
            send_data = {
                'raw': raw_message
            }
            
            send_url = f"{self.gmail_api_base}/users/me/messages/send"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(send_url, headers=headers, json=send_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"✅ Email sent successfully via Emergent Gmail API: {result.get('id')}")
                        return {
                            'success': True,
                            'message_id': result.get('id'),
                            'message': 'Email sent successfully via Emergent Gmail API'
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Gmail send error: Status {response.status}, Response: {error_text}")
                        return {
                            'success': False,
                            'error': f'Gmail send error: {response.status}',
                            'details': error_text
                        }
                        
        except Exception as e:
            logger.error(f"Error sending Gmail message: {str(e)}")
            return {
                'success': False,
                'error': f'Send error: {str(e)}'
            }

# Global instance
emergent_gmail_service = EmergentGmailService()