"""
Personal Gmail OAuth integration for individual Gmail accounts
"""
import os
import json
import logging
from datetime import datetime, timezone
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64
import email

class PersonalGmailService:
    def __init__(self):
        self.credentials = None
        self.service = None
        
    def get_oauth_url(self, redirect_uri):
        """Generate OAuth URL for personal Gmail access"""
        try:
            client_id = "909926639154-r3v0ka94cbu4uo0sn8g4jvtiulf4i9qs.apps.googleusercontent.com"
            
            # Scopes for Gmail access
            scopes = [
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/gmail.send",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile"
            ]
            
            # Generate OAuth URL
            auth_url = "https://accounts.google.com/o/oauth2/auth?" + "&".join([
                f"client_id={client_id}",
                f"redirect_uri={redirect_uri}",
                f"scope={'+'.join(scopes)}",
                "response_type=code",
                "access_type=offline",
                "prompt=consent"
            ])
            
            return auth_url
            
        except Exception as e:
            logging.error(f"Failed to generate OAuth URL: {str(e)}")
            raise e
    
    def exchange_code_for_tokens(self, code, redirect_uri):
        """Exchange authorization code for access tokens"""
        try:
            client_id = "909926639154-r3v0ka94cbu4uo0sn8g4jvtiulf4i9qs.apps.googleusercontent.com"
            client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
            
            if not client_secret:
                raise Exception("Google client secret not configured")
            
            # Exchange code for tokens
            token_url = "https://oauth2.googleapis.com/token"
            token_data = {
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code"
            }
            
            response = requests.post(token_url, data=token_data, timeout=10)
            
            if response.status_code != 200:
                raise Exception(f"Token exchange failed: {response.text}")
            
            tokens = response.json()
            return tokens
            
        except Exception as e:
            logging.error(f"Token exchange failed: {str(e)}")
            raise e
    
    def authenticate_with_tokens(self, access_token, refresh_token=None):
        """Authenticate Gmail service with access tokens"""
        try:
            # Create credentials object
            credentials = Credentials(
                token=access_token,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id="909926639154-r3v0ka94cbu4uo0sn8g4jvtiulf4i9qs.apps.googleusercontent.com",
                client_secret=os.environ.get('GOOGLE_CLIENT_SECRET')
            )
            
            self.credentials = credentials
            self.service = build('gmail', 'v1', credentials=credentials)
            
            logging.info("Personal Gmail service authenticated successfully")
            return True
            
        except Exception as e:
            logging.error(f"Gmail authentication failed: {str(e)}")
            return False
    
    def get_messages(self, max_results=10):
        """Get Gmail messages from personal account"""
        try:
            if not self.service:
                raise Exception("Gmail service not authenticated")
            
            # Get message list
            results = self.service.users().messages().list(
                userId='me', 
                maxResults=max_results,
                q='in:inbox'
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
                date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                
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
                    'date': date_str,
                    'unread': unread
                })
            
            logging.info(f"Retrieved {len(formatted_messages)} personal Gmail messages")
            return formatted_messages
            
        except Exception as e:
            logging.error(f"Failed to get personal Gmail messages: {str(e)}")
            raise e
    
    def send_message(self, to, subject, body):
        """Send Gmail message from personal account"""
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
            
            logging.info(f"Personal Gmail message sent successfully: {send_result['id']}")
            return send_result['id']
            
        except Exception as e:
            logging.error(f"Failed to send personal Gmail message: {str(e)}")
            raise e

# Global instance
personal_gmail_service = PersonalGmailService()