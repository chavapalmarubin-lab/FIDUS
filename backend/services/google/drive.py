"""
Google Drive API Service
Manage files and folders in Google Drive
"""

import logging
from typing import List, Optional, Dict
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload
import io

logger = logging.getLogger(__name__)

class DriveService:
    """Google Drive operations for FIDUS"""
    
    def __init__(self, token_manager):
        self.token_manager = token_manager
        logger.info("✅ Drive Service initialized")
    
    async def _get_service(self, user_id: str):
        """Get authenticated Drive service"""
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
        
        return build('drive', 'v3', credentials=credentials)
    
    async def create_folder(
        self,
        user_id: str,
        name: str,
        parent_folder_id: Optional[str] = None
    ) -> Dict:
        """
        Create folder in Google Drive
        
        Args:
            user_id: Admin user ID
            name: Folder name
            parent_folder_id: Parent folder ID (optional)
            
        Returns:
            Folder info
        """
        try:
            logger.info(f"📁 Creating folder: {name}")
            
            service = await self._get_service(user_id)
            
            # Build folder metadata
            folder_metadata = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                folder_metadata['parents'] = [parent_folder_id]
            
            # Create folder
            folder = service.files().create(
                body=folder_metadata,
                fields='id, name, webViewLink'
            ).execute()
            
            logger.info(f"✅ Folder created: {folder['id']}")
            
            return {
                "success": True,
                "folder_id": folder['id'],
                "name": folder['name'],
                "web_link": folder['webViewLink']
            }
            
        except HttpError as e:
            logger.error(f"❌ Drive API error: {str(e)}")
            raise ValueError(f"Failed to create folder: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Create folder failed: {str(e)}")
            raise ValueError(f"Failed to create folder: {str(e)}")
    
    async def upload_file(
        self,
        user_id: str,
        file_name: str,
        file_content: bytes,
        mime_type: str,
        folder_id: Optional[str] = None
    ) -> Dict:
        """
        Upload file to Google Drive
        
        Args:
            user_id: Admin user ID
            file_name: Name for the file
            file_content: File content as bytes
            mime_type: MIME type of file
            folder_id: Destination folder ID (optional)
            
        Returns:
            File info
        """
        try:
            logger.info(f"📤 Uploading file: {file_name}")
            
            service = await self._get_service(user_id)
            
            # Build file metadata
            file_metadata = {'name': file_name}
            
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Create media upload
            media = MediaIoBaseUpload(
                io.BytesIO(file_content),
                mimetype=mime_type,
                resumable=True
            )
            
            # Upload file
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink, webContentLink'
            ).execute()
            
            logger.info(f"✅ File uploaded: {file['id']}")
            
            return {
                "success": True,
                "file_id": file['id'],
                "name": file['name'],
                "web_link": file['webViewLink'],
                "download_link": file.get('webContentLink')
            }
            
        except HttpError as e:
            logger.error(f"❌ Drive API error: {str(e)}")
            raise ValueError(f"Failed to upload file: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Upload file failed: {str(e)}")
            raise ValueError(f"Failed to upload file: {str(e)}")
    
    async def list_files(
        self,
        user_id: str,
        folder_id: Optional[str] = None,
        max_results: int = 20
    ) -> List[Dict]:
        """
        List files in Drive
        
        Args:
            user_id: Admin user ID
            folder_id: Folder to list files from (optional)
            max_results: Max files to return
            
        Returns:
            List of files
        """
        try:
            logger.info(f"📂 Listing files for user {user_id}")
            
            service = await self._get_service(user_id)
            
            # Build query
            query = "trashed = false"
            if folder_id:
                query += f" and '{folder_id}' in parents"
            
            # List files
            results = service.files().list(
                q=query,
                pageSize=max_results,
                fields="files(id, name, mimeType, webViewLink, createdTime, modifiedTime)"
            ).execute()
            
            files = results.get('files', [])
            
            logger.info(f"✅ Found {len(files)} files")
            
            return [
                {
                    "id": f['id'],
                    "name": f['name'],
                    "mime_type": f['mimeType'],
                    "web_link": f['webViewLink'],
                    "created_time": f['createdTime'],
                    "modified_time": f['modifiedTime']
                }
                for f in files
            ]
            
        except HttpError as e:
            logger.error(f"❌ Drive API error: {str(e)}")
            raise ValueError(f"Failed to list files: {str(e)}")
        except Exception as e:
            logger.error(f"❌ List files failed: {str(e)}")
            raise ValueError(f"Failed to list files: {str(e)}")
