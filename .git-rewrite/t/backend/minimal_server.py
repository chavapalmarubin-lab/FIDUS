"""
MINIMAL BACKEND WITH WORKING GOOGLE INTEGRATION
Clean implementation without complex dependencies
"""
import os
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uuid
from simple_google_api import simple_google_api

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="FIDUS Google Integration API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class EmailRequest(BaseModel):
    to_email: str
    subject: str
    body: str
    from_email: Optional[str] = None

class MeetingRequest(BaseModel):
    title: str
    description: str
    attendee_emails: List[str]
    start_time: str
    end_time: str

# Test endpoint
@app.get("/")
async def root():
    return {"message": "FIDUS Google Integration API is running", "status": "active"}

# ==================== GOOGLE API ENDPOINTS ====================

@app.get("/api/google/test-connection")
async def test_google_connection():
    """Test Google API connectivity"""
    try:
        logger.info("🧪 Testing Google API connection...")
        result = simple_google_api.test_connection()
        return result
    except Exception as e:
        logger.error(f"❌ Google connection test failed: {str(e)}")
        return {"success": False, "error": str(e)}

@app.post("/api/google/send-email")
async def send_google_email(request: EmailRequest):
    """Send email via Google Gmail API"""
    try:
        logger.info(f"📧 Sending email to {request.to_email}")
        result = simple_google_api.send_email(
            to_email=request.to_email,
            subject=request.subject,
            body=request.body,
            from_email=request.from_email
        )
        return result
    except Exception as e:
        logger.error(f"❌ Send email failed: {str(e)}")
        return {"success": False, "error": str(e)}

@app.get("/api/google/emails")
async def get_google_emails(max_results: int = 10):
    """Get emails from Gmail"""
    try:
        logger.info(f"📬 Fetching {max_results} emails...")
        result = simple_google_api.get_emails(max_results=max_results)
        return result
    except Exception as e:
        logger.error(f"❌ Get emails failed: {str(e)}")
        return {"success": False, "error": str(e)}

@app.post("/api/google/create-meeting")
async def create_google_meeting(request: MeetingRequest):
    """Create Google Calendar meeting"""
    try:
        logger.info(f"📅 Creating meeting: {request.title}")
        result = simple_google_api.create_meeting(
            title=request.title,
            description=request.description,
            attendee_emails=request.attendee_emails,
            start_time=request.start_time,
            end_time=request.end_time
        )
        return result
    except Exception as e:
        logger.error(f"❌ Create meeting failed: {str(e)}")
        return {"success": False, "error": str(e)}

@app.get("/api/google/drive-files")
async def get_drive_files(max_results: int = 10):
    """Get files from Google Drive"""
    try:
        logger.info(f"📂 Fetching {max_results} Drive files...")
        result = simple_google_api.list_files(max_results=max_results)
        return result
    except Exception as e:
        logger.error(f"❌ Get Drive files failed: {str(e)}")
        return {"success": False, "error": str(e)}

# ==================== CRM INTEGRATION ENDPOINTS ====================

@app.post("/api/crm/send-prospect-email")
async def send_prospect_email(request: dict):
    """Send email to CRM prospect using Google Gmail"""
    try:
        # Extract prospect data
        prospect_email = request.get('prospect_email')
        email_type = request.get('email_type', 'general')
        custom_subject = request.get('subject')
        custom_body = request.get('body')
        
        if not prospect_email:
            raise HTTPException(status_code=400, detail="Prospect email is required")
        
        # Generate email content based on type
        if email_type == 'welcome':
            subject = custom_subject or "Welcome to FIDUS Investment Management"
            body = custom_body or f"""
            <html>
            <body>
            <h2>Welcome to FIDUS Investment Management</h2>
            <p>Thank you for your interest in our investment services.</p>
            <p>We look forward to helping you achieve your financial goals.</p>
            <br>
            <p>Best regards,<br>FIDUS Team</p>
            </body>
            </html>
            """
        elif email_type == 'document_request':
            subject = custom_subject or "Document Request - FIDUS Investment"
            body = custom_body or f"""
            <html>
            <body>
            <h2>Document Request</h2>
            <p>We need some additional documents to proceed with your application.</p>
            <p>Please provide the requested documents at your earliest convenience.</p>
            <br>
            <p>Best regards,<br>FIDUS Team</p>
            </body>
            </html>
            """
        else:
            subject = custom_subject or "FIDUS Investment Communication"
            body = custom_body or "Thank you for your interest in FIDUS Investment Management."
        
        # Send email via Google API
        result = simple_google_api.send_email(
            to_email=prospect_email,
            subject=subject,
            body=body,
            from_email="noreply@fidus.com"
        )
        
        logger.info(f"✅ Prospect email sent to {prospect_email}")
        return {
            "success": True,
            "message": f"Email sent successfully to {prospect_email}",
            "email_type": email_type,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to send prospect email: {str(e)}")
        return {"success": False, "error": str(e)}

@app.post("/api/crm/schedule-prospect-meeting")
async def schedule_prospect_meeting(request: dict):
    """Schedule meeting with CRM prospect using Google Calendar"""
    try:
        # Extract meeting data
        prospect_email = request.get('prospect_email')
        prospect_name = request.get('prospect_name', 'Prospect')
        meeting_title = request.get('title', f'FIDUS Meeting with {prospect_name}')
        meeting_description = request.get('description', 'Investment consultation meeting')
        start_time = request.get('start_time')
        end_time = request.get('end_time')
        
        if not prospect_email:
            raise HTTPException(status_code=400, detail="Prospect email is required")
        if not start_time or not end_time:
            raise HTTPException(status_code=400, detail="Start time and end time are required")
        
        # Create meeting via Google API
        result = simple_google_api.create_meeting(
            title=meeting_title,
            description=meeting_description,
            attendee_emails=[prospect_email],
            start_time=start_time,
            end_time=end_time
        )
        
        logger.info(f"✅ Meeting scheduled with {prospect_email}")
        return {
            "success": True,
            "message": f"Meeting scheduled successfully with {prospect_email}",
            "meeting_details": result
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to schedule prospect meeting: {str(e)}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)