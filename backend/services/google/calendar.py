"""
Google Calendar API Service
Manage calendar events and create Google Meet links
"""

import logging
from typing import List, Optional, Dict
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

class CalendarService:
    """Google Calendar operations for FIDUS"""
    
    def __init__(self, token_manager):
        self.token_manager = token_manager
        logger.info("✅ Calendar Service initialized")
    
    async def _get_service(self, user_id: str):
        """Get authenticated Calendar service"""
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
        
        return build('calendar', 'v3', credentials=credentials)
    
    async def create_event(
        self,
        user_id: str,
        summary: str,
        start_time: str,
        end_time: str,
        description: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        create_meet_link: bool = True
    ) -> Dict:
        """
        Create calendar event with optional Google Meet link
        
        Args:
            user_id: Admin user ID
            summary: Event title
            start_time: Start time (ISO format)
            end_time: End time (ISO format)
            description: Event description
            attendees: List of attendee emails
            create_meet_link: Whether to create Google Meet link
            
        Returns:
            Event info including Meet link if created
        """
        try:
            logger.info(f"📅 Creating calendar event: {summary}")
            
            service = await self._get_service(user_id)
            
            # Build event
            event = {
                'summary': summary,
                'description': description or '',
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'America/New_York',
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'America/New_York',
                }
            }
            
            # Add attendees
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            # Add Google Meet link
            if create_meet_link:
                event['conferenceData'] = {
                    'createRequest': {
                        'requestId': f"fidus-{datetime.utcnow().timestamp()}",
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                    }
                }
            
            # Create event
            result = service.events().insert(
                calendarId='primary',
                body=event,
                conferenceDataVersion=1 if create_meet_link else 0,
                sendUpdates='all'
            ).execute()
            
            meet_link = None
            if 'conferenceData' in result and 'entryPoints' in result['conferenceData']:
                for entry in result['conferenceData']['entryPoints']:
                    if entry['entryPointType'] == 'video':
                        meet_link = entry['uri']
                        break
            
            logger.info(f"✅ Event created: {result['id']}")
            if meet_link:
                logger.info(f"🔗 Meet link: {meet_link}")
            
            return {
                "success": True,
                "event_id": result['id'],
                "html_link": result['htmlLink'],
                "meet_link": meet_link,
                "summary": summary,
                "start_time": start_time,
                "end_time": end_time
            }
            
        except HttpError as e:
            logger.error(f"❌ Calendar API error: {str(e)}")
            raise ValueError(f"Failed to create event: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Create event failed: {str(e)}")
            raise ValueError(f"Failed to create event: {str(e)}")
    
    async def list_events(
        self,
        user_id: str,
        max_results: int = 20,
        time_min: Optional[str] = None
    ) -> List[Dict]:
        """
        List calendar events
        
        Args:
            user_id: Admin user ID
            max_results: Max events to return
            time_min: Minimum time (ISO format)
            
        Returns:
            List of events
        """
        try:
            logger.info(f"📆 Listing calendar events for user {user_id}")
            
            service = await self._get_service(user_id)
            
            # Default to current time
            if not time_min:
                time_min = datetime.utcnow().isoformat() + 'Z'
            
            # List events
            results = service.events().list(
                calendarId='primary',
                timeMin=time_min,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = results.get('items', [])
            
            logger.info(f"✅ Found {len(events)} events")
            
            # Format events
            formatted_events = []
            for event in events:
                meet_link = None
                if 'conferenceData' in event and 'entryPoints' in event['conferenceData']:
                    for entry in event['conferenceData']['entryPoints']:
                        if entry['entryPointType'] == 'video':
                            meet_link = entry['uri']
                            break
                
                formatted_events.append({
                    "id": event['id'],
                    "summary": event.get('summary', 'No Title'),
                    "start": event['start'].get('dateTime', event['start'].get('date')),
                    "end": event['end'].get('dateTime', event['end'].get('date')),
                    "html_link": event['htmlLink'],
                    "meet_link": meet_link
                })
            
            return formatted_events
            
        except HttpError as e:
            logger.error(f"❌ Calendar API error: {str(e)}")
            raise ValueError(f"Failed to list events: {str(e)}")
        except Exception as e:
            logger.error(f"❌ List events failed: {str(e)}")
            raise ValueError(f"Failed to list events: {str(e)}")
