"""
Google Sheets API Service
Manage spreadsheets in Google Sheets
"""

import logging
from typing import List, Optional, Dict
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

class SheetsService:
    """Google Sheets operations for FIDUS"""
    
    def __init__(self, token_manager):
        self.token_manager = token_manager
        logger.info("✅ Sheets Service initialized")
    
    async def _get_service(self, user_id: str):
        """Get authenticated Sheets service"""
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
        
        return build('sheets', 'v4', credentials=credentials)
    
    async def list_spreadsheets(
        self,
        user_id: str,
        max_results: int = 20
    ) -> List[Dict]:
        """
        List spreadsheets from Drive (Sheets are stored in Drive)
        
        Args:
            user_id: Admin user ID
            max_results: Max spreadsheets to return
            
        Returns:
            List of spreadsheets
        """
        try:
            logger.info(f"📊 Listing spreadsheets for user {user_id}")
            
            # We need to use Drive API to list Sheets files
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
            
            # Use Drive API to find Sheets
            drive_service = build('drive', 'v3', credentials=credentials)
            
            # Query for Google Sheets files
            results = drive_service.files().list(
                q="mimeType='application/vnd.google-apps.spreadsheet' and trashed = false",
                pageSize=max_results,
                fields="files(id, name, createdTime, modifiedTime, webViewLink)"
            ).execute()
            
            sheets = results.get('files', [])
            
            logger.info(f"✅ Found {len(sheets)} spreadsheets")
            
            return [
                {
                    "spreadsheetId": s['id'],
                    "name": s['name'],
                    "web_link": s['webViewLink'],
                    "created_time": s['createdTime'],
                    "modified_time": s['modifiedTime']
                }
                for s in sheets
            ]
            
        except HttpError as e:
            logger.error(f"❌ Sheets API error: {str(e)}")
            raise ValueError(f"Failed to list spreadsheets: {str(e)}")
        except Exception as e:
            logger.error(f"❌ List spreadsheets failed: {str(e)}")
            raise ValueError(f"Failed to list spreadsheets: {str(e)}")
    
    async def get_spreadsheet(
        self,
        user_id: str,
        spreadsheet_id: str
    ) -> Dict:
        """
        Get spreadsheet details
        
        Args:
            user_id: Admin user ID
            spreadsheet_id: Spreadsheet ID
            
        Returns:
            Spreadsheet details
        """
        try:
            logger.info(f"📄 Getting spreadsheet {spreadsheet_id}")
            
            service = await self._get_service(user_id)
            
            # Get spreadsheet
            spreadsheet = service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            logger.info(f"✅ Got spreadsheet: {spreadsheet.get('properties', {}).get('title', 'Unknown')}")
            
            return {
                "spreadsheetId": spreadsheet['spreadsheetId'],
                "title": spreadsheet['properties']['title'],
                "sheets": [
                    {
                        "sheetId": sheet['properties']['sheetId'],
                        "title": sheet['properties']['title']
                    }
                    for sheet in spreadsheet.get('sheets', [])
                ],
                "web_link": spreadsheet['spreadsheetUrl']
            }
            
        except HttpError as e:
            logger.error(f"❌ Sheets API error: {str(e)}")
            raise ValueError(f"Failed to get spreadsheet: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Get spreadsheet failed: {str(e)}")
            raise ValueError(f"Failed to get spreadsheet: {str(e)}")
    
    async def create_spreadsheet(
        self,
        user_id: str,
        title: str,
        sheet_titles: Optional[List[str]] = None
    ) -> Dict:
        """
        Create a new spreadsheet
        
        Args:
            user_id: Admin user ID
            title: Spreadsheet title
            sheet_titles: List of sheet names to create
            
        Returns:
            Spreadsheet info
        """
        try:
            logger.info(f"📝 Creating spreadsheet: {title}")
            
            service = await self._get_service(user_id)
            
            # Build spreadsheet body
            spreadsheet = {
                'properties': {
                    'title': title
                }
            }
            
            # Add sheets if specified
            if sheet_titles:
                spreadsheet['sheets'] = [
                    {'properties': {'title': sheet_title}}
                    for sheet_title in sheet_titles
                ]
            
            # Create spreadsheet
            result = service.spreadsheets().create(
                body=spreadsheet,
                fields='spreadsheetId,spreadsheetUrl,properties'
            ).execute()
            
            logger.info(f"✅ Spreadsheet created: {result['spreadsheetId']}")
            
            return {
                "success": True,
                "spreadsheetId": result['spreadsheetId'],
                "title": result['properties']['title'],
                "web_link": result['spreadsheetUrl']
            }
            
        except HttpError as e:
            logger.error(f"❌ Sheets API error: {str(e)}")
            raise ValueError(f"Failed to create spreadsheet: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Create spreadsheet failed: {str(e)}")
            raise ValueError(f"Failed to create spreadsheet: {str(e)}")
