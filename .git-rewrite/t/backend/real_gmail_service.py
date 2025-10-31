"""
Real Gmail API integration using Google Service Account
"""
import os
import json
import logging
from datetime import datetime, timezone
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
import base64
import email

class RealGmailService:
    def __init__(self):
        self.credentials = None
        self.service = None
        self.user_email = None
        
    def authenticate(self, user_email=None):
        """Authenticate using service account with domain-wide delegation"""
        try:
            # Load service account credentials
            from path_utils import get_credentials_path
            credentials_path = get_credentials_path('google_credentials.json')
            
            if not os.path.exists(credentials_path):
                raise Exception("Google credentials file not found")
                
            # Define the scopes
            SCOPES = [
                'https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.send',
                'https://www.googleapis.com/auth/gmail.modify'
            ]
            
            # Load and create credentials
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path, scopes=SCOPES
            )
            
            # If user_email is provided, delegate to that user
            if user_email:
                credentials = credentials.with_subject(user_email)
                self.user_email = user_email
                logging.info(f"Delegating to user: {user_email}")
            
            self.credentials = credentials
            self.service = build('gmail', 'v1', credentials=credentials)
            
            logging.info("Gmail service authenticated successfully")
            return True
            
        except Exception as e:
            logging.error(f"Gmail authentication failed: {str(e)}")
            return False
    
    def get_messages(self, max_results=10):
        """Get Gmail messages"""
        try:
            if not self.service:
                raise Exception("Gmail service not authenticated")
            
            # Get message list
            results = self.service.users().messages().list(
                userId='me', 
                maxResults=max_results,
                q='in:inbox'  # Only inbox messages
            ).execute()
            
            messages = results.get('messages', [])
            
            formatted_messages = []
            for msg in messages:
                # Get full message details
                message = self.service.users().messages().get(
                    userId='me', 
                    id=msg['id'],
                    format='full'
                ).execute()
                
                # Extract message details
                headers = message['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                
                # Get message snippet
                snippet = message.get('snippet', '')
                
                # Check if unread
                labels = message.get('labelIds', [])
                unread = 'UNREAD' in labels
                
                formatted_messages.append({
                    'id': message['id'],
                    'subject': subject,
                    'sender': sender,
                    'preview': snippet,
                    'date': date,
                    'unread': unread
                })
            
            logging.info(f"Retrieved {len(formatted_messages)} Gmail messages")
            return formatted_messages
            
        except Exception as e:
            logging.error(f"Failed to get Gmail messages: {str(e)}")
            raise e
    
    def send_message(self, to, subject, body):
        """Send Gmail message"""
        try:
            if not self.service:
                raise Exception("Gmail service not authenticated")
            
            # Create message
            message = email.mime.text.MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send message
            send_result = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            logging.info(f"Gmail message sent successfully: {send_result['id']}")
            return send_result['id']
            
        except Exception as e:
            logging.error(f"Failed to send Gmail message: {str(e)}")
            raise e

# Global instance
gmail_service = RealGmailService()