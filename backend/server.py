# Replace the existing Google OAuth endpoints with proper Emergent implementation

# Add this after the existing imports
import requests
from datetime import datetime, timezone, timedelta

# Replace Google OAuth endpoints with Emergent OAuth implementation
@api_router.get("/admin/google/auth-url")
async def get_google_auth_url():
    """Get Emergent OAuth authorization URL for Google authentication"""
    try:
        # Use Emergent OAuth service - redirect to admin dashboard after auth
        redirect_url = f"{os.environ.get('FRONTEND_URL', 'https://wealth-portal-17.preview.emergentagent.com')}/admin/google-callback"
        auth_url = f"https://auth.emergentagent.com/?redirect={redirect_url}"
        
        logging.info(f"Generated Emergent OAuth URL: {auth_url}")
        
        return {
            "success": True,
            "auth_url": auth_url,
            "redirect_url": redirect_url
        }
        
    except Exception as e:
        logging.error(f"Get Google auth URL error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get auth URL")

@api_router.post("/admin/google/process-session")
async def process_emergent_google_session(request: dict):
    """Process Emergent OAuth session ID for Google authentication"""
    try:
        logging.info("Processing Emergent Google OAuth session")
        
        session_id = request.get('session_id')
        if not session_id:
            raise HTTPException(status_code=400, detail="Missing session_id")
        
        # Call Emergent OAuth service to get user data
        emergent_url = "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data"
        headers = {"X-Session-ID": session_id}
        
        response = requests.get(emergent_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            logging.error(f"Emergent OAuth error: {response.status_code} - {response.text}")
            raise HTTPException(status_code=400, detail="Invalid session_id")
        
        user_data = response.json()
        
        # Store session in database with httpOnly cookie
        session_token = user_data.get('session_token')
        
        session_data = {
            "session_token": session_token,
            "user_info": {
                "id": user_data.get('id'),
                "email": user_data.get('email'),
                "name": user_data.get('name'),
                "picture": user_data.get('picture')
            },
            "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
            "created_at": datetime.now(timezone.utc),
            "auth_type": "emergent_google"
        }
        
        # Store in MongoDB
        await client[os.environ.get('DB_NAME', 'fidus_investment_db')].admin_sessions.insert_one(session_data)
        
        logging.info(f"Created Emergent Google session for: {user_data.get('email')}")
        
        return {
            "success": True,
            "profile": session_data["user_info"],
            "session_token": session_token,
            "message": "Google authentication successful"
        }
        
    except Exception as e:
        logging.error(f"Process Emergent session error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process session")

@api_router.get("/admin/google/profile")  
async def get_admin_google_profile(request: Request):
    """Get current admin's Google profile using session token from cookies"""
    try:
        # Get session token from cookies first (preferred for Emergent OAuth)
        session_token = None
        
        if 'session_token' in request.cookies:
            session_token = request.cookies['session_token']
        
        # Fallback to Authorization header
        if not session_token:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                session_token = auth_header.split(' ')[1]
        
        if not session_token:
            raise HTTPException(status_code=401, detail="No session token provided")
        
        # Find session in database
        session_doc = await client[os.environ.get('DB_NAME', 'fidus_investment_db')].admin_sessions.find_one({"session_token": session_token})
        
        if not session_doc:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        # Check expiry with timezone-aware comparison
        expires_at = session_doc['expires_at']
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        elif expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
            
        if expires_at < datetime.now(timezone.utc):
            await client[os.environ.get('DB_NAME', 'fidus_investment_db')].admin_sessions.delete_one({"session_token": session_token})
            raise HTTPException(status_code=401, detail="Session expired")
        
        # Return profile
        user_info = session_doc.get('user_info', {})
        
        return {
            "success": True,
            "profile": {
                "id": user_info.get('id', 'unknown'),
                "email": user_info.get('email', ''),
                "name": user_info.get('name', ''),
                "picture": user_info.get('picture', ''),
                "is_google_connected": True,
                "auth_type": session_doc.get('auth_type', 'emergent_google'),
                "connected_at": session_doc['created_at'].isoformat()
            },
            "is_authenticated": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Get Google profile error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get profile")

@api_router.post("/admin/google/logout")
async def logout_google_admin(request: Request, response: Response):
    """Logout Google admin user"""
    try:
        # Get session token
        session_token = None
        if 'session_token' in request.cookies:
            session_token = request.cookies['session_token']
        
        if session_token:
            # Delete from database
            await client[os.environ.get('DB_NAME', 'fidus_investment_db')].admin_sessions.delete_one({"session_token": session_token})
            
            # Clear cookie
            response.delete_cookie("session_token", path="/", secure=True, samesite="none")
        
        return {"success": True, "message": "Logged out successfully"}
        
    except Exception as e:
        logging.error(f"Logout error: {str(e)}")
        raise HTTPException(status_code=500, detail="Logout failed")