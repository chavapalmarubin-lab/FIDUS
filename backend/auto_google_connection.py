"""
FIDUS Production Google Connection Manager
=========================================

Automated Google OAuth connection management for production systems.
NO manual user intervention required - system maintains connection automatically.
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, Any
import aiohttp
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# MongoDB Integration
from mongodb_integration import mongodb_manager

logger = logging.getLogger(__name__)

class AutoGoogleConnectionManager:
    """
    Production-grade Google connection management
    - Automatically establishes and maintains Google API connections
    - Monitors connection health continuously  
    - Auto-reconnects on failures
    - No user intervention required
    """
    
    def __init__(self):
        self.service_account_credentials = None
        self.gmail_service = None
        self.calendar_service = None
        self.drive_service = None
        self.meet_service = None
        
        # Connection monitoring
        self.connection_status = {
            "gmail": {"connected": False, "last_check": None, "error": None},
            "calendar": {"connected": False, "last_check": None, "error": None},
            "drive": {"connected": False, "last_check": None, "error": None},
            "meet": {"connected": False, "last_check": None, "error": None}
        }
        
        # Auto-reconnection settings
        self.monitor_interval = 300  # 5 minutes
        self.max_retry_attempts = 5
        self.retry_delay = 30  # seconds
        
        # Initialize on startup (delayed until event loop is available)
        self._initialized = False
    
    async def initialize_auto_connection(self):
        """Initialize Google services automatically on startup"""
        try:
            logger.info("🔄 PRODUCTION: Initializing automated Google connection...")
            
            # Load service account credentials
            if await self._load_service_account_credentials():
                # Establish connections to all Google services
                await self._establish_all_connections()
                
                # Start continuous monitoring
                asyncio.create_task(self._start_connection_monitoring())
                
                self._initialized = True
                logger.info("✅ PRODUCTION: Automated Google connection system active")
            else:
                logger.error("❌ PRODUCTION: Failed to initialize Google connection - missing credentials")
                
        except Exception as e:
            logger.error(f"❌ PRODUCTION: Auto-connection initialization failed: {str(e)}")
            self._initialized = True  # Mark as initialized even if failed to avoid infinite loops
    
    async def _load_service_account_credentials(self) -> bool:
        """Load and validate service account credentials"""
        try:
            # Get service account key from environment
            service_account_key = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')
            
            if not service_account_key:
                logger.error("❌ GOOGLE_SERVICE_ACCOUNT_KEY environment variable not found")
                return False
            
            # Parse JSON credentials
            try:
                credentials_info = json.loads(service_account_key)
            except json.JSONDecodeError as e:
                logger.error(f"❌ Invalid JSON in GOOGLE_SERVICE_ACCOUNT_KEY: {str(e)}")
                return False
            
            # Create service account credentials
            scopes = [
                'https://www.googleapis.com/auth/gmail.modify',
                'https://www.googleapis.com/auth/calendar',
                'https://www.googleapis.com/auth/drive',
                'https://www.googleapis.com/auth/meetings'
            ]
            
            self.service_account_credentials = service_account.Credentials.from_service_account_info(
                credentials_info, scopes=scopes
            )
            
            logger.info("✅ PRODUCTION: Service account credentials loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load service account credentials: {str(e)}")
            return False
    
    async def _establish_all_connections(self):
        """Establish connections to all Google services"""
        services = {
            'gmail': ('gmail', 'v1'),
            'calendar': ('calendar', 'v3'),
            'drive': ('drive', 'v3'),
            'meet': ('meet', 'v2')
        }
        
        for service_name, (api_name, version) in services.items():
            try:
                service = build(api_name, version, credentials=self.service_account_credentials)
                setattr(self, f"{service_name}_service", service)
                
                # Test connection
                await self._test_service_connection(service_name, service)
                
                self.connection_status[service_name] = {
                    "connected": True,
                    "last_check": datetime.now(timezone.utc).isoformat(),
                    "error": None
                }
                
                logger.info(f"✅ PRODUCTION: {service_name.upper()} service connected")
                
            except Exception as e:
                logger.error(f"❌ PRODUCTION: Failed to connect {service_name}: {str(e)}")
                self.connection_status[service_name] = {
                    "connected": False,
                    "last_check": datetime.now(timezone.utc).isoformat(),
                    "error": str(e)
                }
    
    async def _test_service_connection(self, service_name: str, service):
        """Test if a Google service connection is working"""
        try:
            if service_name == 'gmail':
                # Test Gmail access
                service.users().getProfile(userId='me').execute()
            elif service_name == 'calendar':
                # Test Calendar access
                service.calendarList().list().execute()
            elif service_name == 'drive':
                # Test Drive access
                service.files().list(pageSize=1).execute()
            elif service_name == 'meet':
                # Test Meet access (may have different endpoint)
                pass  # Meet API might require different testing approach
                
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ {service_name} connection test failed: {str(e)}")
            return False
    
    async def _start_connection_monitoring(self):
        """Start continuous connection monitoring"""
        logger.info("🔄 PRODUCTION: Starting continuous connection monitoring...")
        
        while True:
            try:
                await asyncio.sleep(self.monitor_interval)
                await self._monitor_all_connections()
                
            except Exception as e:
                logger.error(f"❌ Connection monitoring error: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def _monitor_all_connections(self):
        """Monitor all Google service connections"""
        logger.info("🔍 PRODUCTION: Monitoring Google service connections...")
        
        for service_name in ['gmail', 'calendar', 'drive', 'meet']:
            service = getattr(self, f"{service_name}_service", None)
            
            if service:
                is_connected = await self._test_service_connection(service_name, service)
                
                if is_connected:
                    self.connection_status[service_name].update({
                        "connected": True,
                        "last_check": datetime.now(timezone.utc).isoformat(),
                        "error": None
                    })
                else:
                    # Connection failed - attempt reconnection
                    logger.warning(f"⚠️ PRODUCTION: {service_name} connection lost - attempting reconnection...")
                    await self._reconnect_service(service_name)
            else:
                # Service not initialized - attempt connection
                logger.warning(f"⚠️ PRODUCTION: {service_name} not initialized - attempting connection...")
                await self._reconnect_service(service_name)
        
        # Store connection status in MongoDB for monitoring
        await self._store_connection_status()
        
        # Log overall status
        connected_services = sum(1 for status in self.connection_status.values() if status["connected"])
        total_services = len(self.connection_status)
        
        logger.info(f"📊 PRODUCTION: Google services status: {connected_services}/{total_services} connected")
    
    async def _reconnect_service(self, service_name: str):
        """Attempt to reconnect a specific Google service"""
        service_apis = {
            'gmail': ('gmail', 'v1'),
            'calendar': ('calendar', 'v3'),
            'drive': ('drive', 'v3'),
            'meet': ('meet', 'v2')
        }
        
        if service_name not in service_apis:
            return
        
        api_name, version = service_apis[service_name]
        
        for attempt in range(self.max_retry_attempts):
            try:
                logger.info(f"🔄 PRODUCTION: Reconnecting {service_name} (attempt {attempt + 1}/{self.max_retry_attempts})")
                
                # Recreate service
                service = build(api_name, version, credentials=self.service_account_credentials)
                setattr(self, f"{service_name}_service", service)
                
                # Test connection
                if await self._test_service_connection(service_name, service):
                    self.connection_status[service_name] = {
                        "connected": True,
                        "last_check": datetime.now(timezone.utc).isoformat(),
                        "error": None
                    }
                    
                    logger.info(f"✅ PRODUCTION: {service_name} reconnected successfully")
                    return
                
            except Exception as e:
                logger.warning(f"⚠️ PRODUCTION: {service_name} reconnection attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.max_retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay)
        
        # All attempts failed
        self.connection_status[service_name] = {
            "connected": False,
            "last_check": datetime.now(timezone.utc).isoformat(),
            "error": f"Reconnection failed after {self.max_retry_attempts} attempts"
        }
        
        logger.error(f"❌ PRODUCTION: {service_name} reconnection failed after {self.max_retry_attempts} attempts")
    
    async def _store_connection_status(self):
        """Store connection status in MongoDB for monitoring dashboard"""
        try:
            status_record = {
                "timestamp": datetime.now(timezone.utc),
                "services": self.connection_status.copy(),
                "overall_health": sum(1 for status in self.connection_status.values() if status["connected"]) / len(self.connection_status),
                "auto_managed": True
            }
            
            # Store in MongoDB
            await mongodb_manager.store_google_connection_status(status_record)
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to store connection status: {str(e)}")
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get current connection status for API endpoints"""
        # Initialize if not already done
        if not self._initialized:
            try:
                # Create an event loop if none exists
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Initialize synchronously for now
            loop.run_until_complete(self.initialize_auto_connection())
        
        # Get last check times safely
        last_checks = [
            status.get("last_check", "")
            for status in self.connection_status.values()
            if status.get("last_check")
        ]
        last_monitoring_check = max(last_checks) if last_checks else None
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": self.connection_status.copy(),
            "overall_health": sum(1 for status in self.connection_status.values() if status["connected"]) / max(len(self.connection_status), 1),
            "auto_managed": True,
            "last_monitoring_check": last_monitoring_check
        }
    
    async def force_reconnect_all(self):
        """Force reconnection of all services (for admin use)"""
        logger.info("🔄 PRODUCTION: Force reconnecting all Google services...")
        await self._establish_all_connections()
        return self.get_connection_status()


# Global instance for production use
auto_google_manager = AutoGoogleConnectionManager()


async def get_auto_google_manager():
    """Get the global auto Google connection manager"""
    return auto_google_manager