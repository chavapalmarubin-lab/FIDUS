"""
Google OAuth Token Manager
Handles secure storage and refresh of OAuth tokens
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
import requests

logger = logging.getLogger(__name__)

class GoogleTokenManager:
    """
    Manages Google OAuth tokens with automatic refresh
    """
    
    def __init__(self, mongodb_client, client_id: str, client_secret: str):
        """Initialize token manager"""
        self.db = mongodb_client['fidus_production']
        self.tokens_collection = self.db['google_oauth_tokens']
        self.state_collection = self.db['oauth_states']
        self.client_id = client_id
        self.client_secret = client_secret
        
        logger.info("✅ Token Manager initialized")
    
    async def store_tokens(
        self,
        user_id: str,
        access_token: str,
        refresh_token: Optional[str],
        expires_in: int,
        token_type: str,
        scope: str
    ):
        """Store OAuth tokens for user"""
        logger.info(f"💾 Storing tokens for user {user_id}")
        
        token_doc = {
            "user_id": user_id,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": token_type,
            "scope": scope,
            "expires_at": datetime.utcnow() + timedelta(seconds=expires_in),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await self.tokens_collection.update_one(
            {"user_id": user_id},
            {"$set": token_doc},
            upsert=True
        )
        
        logger.info(f"✅ Tokens stored for user {user_id}")
    
    async def get_tokens(self, user_id: str) -> Optional[Dict]:
        """
        Get valid tokens for user, refreshing if necessary
        """
        logger.debug(f"🔍 Getting tokens for user {user_id}")
        
        token_doc = await self.tokens_collection.find_one({"user_id": user_id})
        
        if not token_doc:
            logger.warning(f"⚠️ No tokens found for user {user_id}")
            return None
        
        # Check if token is expired
        if token_doc['expires_at'] < datetime.utcnow():
            logger.info(f"🔄 Token expired, refreshing for user {user_id}")
            
            # Refresh token
            new_tokens = await self._refresh_token(token_doc['refresh_token'])
            
            if new_tokens:
                # Update stored tokens
                await self.store_tokens(
                    user_id=user_id,
                    access_token=new_tokens['access_token'],
                    refresh_token=token_doc['refresh_token'],  # Keep same refresh token
                    expires_in=new_tokens['expires_in'],
                    token_type=new_tokens['token_type'],
                    scope=token_doc['scope']
                )
                
                # Return fresh tokens
                token_doc = await self.tokens_collection.find_one({"user_id": user_id})
                logger.info(f"✅ Token refreshed for user {user_id}")
            else:
                logger.error(f"❌ Token refresh failed for user {user_id}")
                return None
        
        return token_doc
    
    async def _refresh_token(self, refresh_token: str) -> Optional[Dict]:
        """Refresh expired access token"""
        if not refresh_token:
            logger.error("❌ No refresh token available")
            return None
        
        try:
            logger.info("🔄 Refreshing access token")
            
            response = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                logger.info("✅ Token refresh successful")
                return response.json()
            else:
                logger.error(f"❌ Token refresh failed: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Token refresh exception: {str(e)}")
            return None
    
    async def delete_tokens(self, user_id: str):
        """Delete tokens for user"""
        logger.info(f"🗑️ Deleting tokens for user {user_id}")
        
        await self.tokens_collection.delete_one({"user_id": user_id})
        
        logger.info(f"✅ Tokens deleted for user {user_id}")
    
    def store_state(self, user_id: str, state: str, expires_minutes: int = 10):
        """Store OAuth state for CSRF protection"""
        logger.debug(f"💾 Storing state for user {user_id}")
        
        state_doc = {
            "user_id": user_id,
            "state": state,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=expires_minutes)
        }
        
        self.state_collection.update_one(
            {"user_id": user_id},
            {"$set": state_doc},
            upsert=True
        )
    
    def verify_state(self, user_id: str, state: str) -> bool:
        """Verify OAuth state"""
        logger.info(f"🔍 Verifying state for user {user_id}")
        logger.info(f"🔍 State to verify: {state[:50]}...")
        
        state_doc = self.state_collection.find_one({"user_id": user_id})
        
        if not state_doc:
            logger.warning(f"⚠️ No state found for user {user_id} in MongoDB")
            return False
        
        logger.info(f"🔍 Found state doc: user_id={state_doc.get('user_id')}, state={state_doc.get('state', '')[:50]}...")
        
        # Check expiration
        if state_doc['expires_at'] < datetime.utcnow():
            logger.warning(f"⚠️ State expired for user {user_id}")
            logger.warning(f"   Expired at: {state_doc['expires_at']}, Now: {datetime.utcnow()}")
            return False
        
        # Verify match
        if state_doc['state'] != state:
            logger.warning(f"⚠️ State mismatch for user {user_id}")
            logger.warning(f"   Expected: {state_doc['state'][:50]}...")
            logger.warning(f"   Received: {state[:50]}...")
            return False
        
        logger.info(f"✅ State verified for user {user_id}")
        return True
    
    def clear_state(self, user_id: str):
        """Clear OAuth state after use"""
        logger.debug(f"🗑️ Clearing state for user {user_id}")
        
        self.state_collection.delete_one({"user_id": user_id})
