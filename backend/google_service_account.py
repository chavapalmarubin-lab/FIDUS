"""
Google Service Account Integration
Provides persistent Google API access without user OAuth
Service Account Email: fidus-gmail-service@shaped-canyon-470822-b3.iam.gserviceaccount.com
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# Define scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets'
]

# Path to service account JSON
SERVICE_ACCOUNT_FILE = Path(__file__).parent / 'config' / 'google-service-account.json'

def get_google_credentials():
    """Get Google service account credentials - never expire!"""
    try:
        if not SERVICE_ACCOUNT_FILE.exists():
            raise FileNotFoundError(f"Service account file not found: {SERVICE_ACCOUNT_FILE}")
        
        credentials = service_account.Credentials.from_service_account_file(
            str(SERVICE_ACCOUNT_FILE),
            scopes=SCOPES
        )
        
        logger.info("✅ Service account credentials loaded successfully")
        return credentials
        
    except Exception as e:
        logger.error(f"❌ Failed to load service account credentials: {e}")
        raise

def get_gmail_service():
    """Get authenticated Gmail API service"""
    credentials = get_google_credentials()
    return build('gmail', 'v1', credentials=credentials)

def get_calendar_service():
    """Get authenticated Calendar API service"""
    credentials = get_google_credentials()
    return build('calendar', 'v3', credentials=credentials)

def get_drive_service():
    """Get authenticated Drive API service"""
    credentials = get_google_credentials()
    return build('drive', 'v3', credentials=credentials)

def get_sheets_service():
    """Get authenticated Sheets API service"""
    credentials = get_google_credentials()
    return build('sheets', 'v4', credentials=credentials)


# ==================== GMAIL ====================

async def list_gmail_messages(max_results: int = 10, query: str = None) -> List[Dict]:
    """List Gmail messages"""
    try:
        service = get_gmail_service()
        
        params = {'userId': 'me', 'maxResults': max_results}
        if query:
            params['q'] = query
            
        results = service.users().messages().list(**params).execute()
        messages = results.get('messages', [])
        
        # Fetch full details
        detailed_messages = []
        for msg in messages[:max_results]:
            try:
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                detailed_messages.append(message)
            except Exception as e:
                logger.error(f"Failed to fetch message {msg['id']}: {e}")
        
        logger.info(f"✅ Fetched {len(detailed_messages)} Gmail messages")
        return detailed_messages
        
    except Exception as e:
        logger.error(f"❌ Failed to list Gmail messages: {e}")
        return []


# ==================== CALENDAR ====================

async def list_calendar_events(max_results: int = 10) -> List[Dict]:
    """List Calendar events"""
    try:
        from datetime import datetime
        
        service = get_calendar_service()
        
        now = datetime.utcnow().isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        logger.info(f"✅ Fetched {len(events)} calendar events")
        return events
        
    except Exception as e:
        logger.error(f"❌ Failed to list calendar events: {e}")
        return []


# ==================== DRIVE ====================

async def list_drive_files(folder_id: str, max_results: int = 20) -> List[Dict]:
    """List files in Drive folder"""
    try:
        service = get_drive_service()
        
        query = f"'{folder_id}' in parents and trashed=false"
        
        results = service.files().list(
            q=query,
            pageSize=max_results,
            fields="files(id, name, mimeType, modifiedTime, size, webViewLink)"
        ).execute()
        
        files = results.get('files', [])
        
        logger.info(f"✅ Fetched {len(files)} files from Drive folder {folder_id}")
        return files
        
    except Exception as e:
        logger.error(f"❌ Failed to list Drive files: {e}")
        return []


# ==================== SHEETS ====================

async def list_spreadsheets_in_folder(folder_id: str) -> List[Dict]:
    """List all spreadsheets in a Drive folder"""
    try:
        service = get_drive_service()
        
        query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false"
        
        results = service.files().list(
            q=query,
            pageSize=20,
            fields="files(id, name, modifiedTime, webViewLink)"
        ).execute()
        
        spreadsheets = results.get('files', [])
        
        logger.info(f"✅ Fetched {len(spreadsheets)} spreadsheets from folder {folder_id}")
        return spreadsheets
        
    except Exception as e:
        logger.error(f"❌ Failed to list spreadsheets: {e}")
        return []
