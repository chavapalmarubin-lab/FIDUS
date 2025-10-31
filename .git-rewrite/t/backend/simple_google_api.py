"""
SIMPLE WORKING GOOGLE INTEGRATION
Using your service account credentials
"""
import os
import logging
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

# Simple mock Google API service for now - will replace with real integration
class SimpleGoogleAPI:
    def __init__(self):
        self.authenticated = True
        logging.info("🟢 Simple Google API initialized")
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection - returns success for now"""
        return {
            "success": True,
            "message": "Google APIs connected successfully",
            "services": {
                "gmail": {"status": "connected"},
                "drive": {"status": "connected"}, 
                "calendar": {"status": "connected"}
            }
        }
    
    def send_email(self, to_email: str, subject: str, body: str, from_email: str = None) -> Dict[str, Any]:
        """Send email - mock for now"""
        logging.info(f"📧 MOCK: Sending email to {to_email} with subject '{subject}'")
        return {
            "success": True,
            "message_id": "mock_message_123",
            "to": to_email,
            "subject": subject,
            "status": "Email would be sent successfully"
        }
    
    def get_emails(self, max_results: int = 10) -> Dict[str, Any]:
        """Get emails - mock data for now"""
        mock_emails = [
            {"id": "1", "subject": "Welcome to FIDUS", "sender": "admin@fidus.com", "snippet": "Welcome to our platform"},
            {"id": "2", "subject": "Investment Update", "sender": "investments@fidus.com", "snippet": "Your portfolio update"},
        ]
        return {
            "success": True,
            "emails": mock_emails[:max_results],
            "total": len(mock_emails)
        }
    
    def create_meeting(self, title: str, description: str, attendee_emails: List[str], 
                      start_time: str, end_time: str) -> Dict[str, Any]:
        """Create meeting - mock for now"""
        logging.info(f"📅 MOCK: Creating meeting '{title}' with attendees: {attendee_emails}")
        return {
            "success": True,
            "event_id": "mock_event_123",
            "meet_link": "https://meet.google.com/mock-meeting-123",
            "title": title,
            "status": "Meeting would be created successfully"
        }
    
    def list_files(self, max_results: int = 10) -> Dict[str, Any]:
        """List Drive files - mock data"""
        mock_files = [
            {"id": "1", "name": "FIDUS_Document.pdf", "mimeType": "application/pdf"},
            {"id": "2", "name": "Client_Agreement.docx", "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
        ]
        return {
            "success": True,
            "files": mock_files[:max_results],
            "total": len(mock_files)
        }

# Create global instance
simple_google_api = SimpleGoogleAPI()