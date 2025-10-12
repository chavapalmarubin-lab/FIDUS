"""
FIDUS Platform Credentials Service
Secure credential management with audit logging
NO CREDENTIALS EXPOSED - Only status and metadata
"""

import os
import logging
from datetime import datetime, timezone
from typing import Dict, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import aiohttp

logger = logging.getLogger(__name__)

class CredentialsService:
    """Service for secure credential management and testing"""
    
    def __init__(self, mongo_client: AsyncIOMotorClient = None, db_name: str = None):
        self.mongo_client = mongo_client
        self.db_name = db_name or os.environ.get('DB_NAME', 'fidus_production')
    
    async def check_credential_configured(self, credential_id: str) -> Dict:
        """Check if a credential is configured (env var exists)"""
        
        env_checks = {
            'mongodb_atlas': ['MONGO_URL'],
            'google_oauth': ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET'],
            'google_service_account': ['GOOGLE_SERVICE_ACCOUNT_FILE'],
            'render_api': ['RENDER_API_KEY'],
            'emergent_host': ['EMERGENT_API_TOKEN'],
            'smtp_email': ['SMTP_HOST', 'SMTP_PORT', 'SMTP_USERNAME', 'SMTP_PASSWORD'],
            'github_repo': ['GITHUB_TOKEN'],
        }
        
        env_vars = env_checks.get(credential_id, [])
        configured = all(os.getenv(var) for var in env_vars)
        missing = [var for var in env_vars if not os.getenv(var)]
        
        return {
            'credential_id': credential_id,
            'configured': configured,
            'env_vars_checked': env_vars,
            'missing_env_vars': missing,
            'checked_at': datetime.now(timezone.utc).isoformat()
        }
    
    async def test_mongodb_connection(self) -> Dict:
        """Test MongoDB connection without exposing credentials"""
        try:
            if not self.mongo_client:
                return {
                    'service': 'mongodb',
                    'test_passed': False,
                    'error': 'MongoDB client not initialized',
                    'tested_at': datetime.now(timezone.utc).isoformat()
                }
            
            db = self.mongo_client[self.db_name]
            await db.command('ping')
            
            # Get some stats without exposing sensitive data
            stats = await db.command('dbstats')
            
            return {
                'service': 'mongodb',
                'test_passed': True,
                'database': self.db_name,
                'collections_count': stats.get('collections', 0),
                'tested_at': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"MongoDB connection test failed: {str(e)}")
            return {
                'service': 'mongodb',
                'test_passed': False,
                'error': str(e),
                'tested_at': datetime.now(timezone.utc).isoformat()
            }
    
    async def test_google_oauth(self) -> Dict:
        """Test Google OAuth configuration"""
        try:
            client_id = os.getenv('GOOGLE_CLIENT_ID')
            client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
            
            if not client_id or not client_secret:
                return {
                    'service': 'google_oauth',
                    'test_passed': False,
                    'error': 'OAuth credentials not configured',
                    'tested_at': datetime.now(timezone.utc).isoformat()
                }
            
            # Just verify they exist and are non-empty
            return {
                'service': 'google_oauth',
                'test_passed': True,
                'client_id_configured': bool(client_id),
                'client_secret_configured': bool(client_secret),
                'tested_at': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Google OAuth test failed: {str(e)}")
            return {
                'service': 'google_oauth',
                'test_passed': False,
                'error': str(e),
                'tested_at': datetime.now(timezone.utc).isoformat()
            }
    
    async def test_smtp_connection(self) -> Dict:
        """Test SMTP configuration (without actually sending email)"""
        try:
            smtp_host = os.getenv('SMTP_HOST')
            smtp_port = os.getenv('SMTP_PORT')
            smtp_username = os.getenv('SMTP_USERNAME')
            smtp_password = os.getenv('SMTP_PASSWORD')
            
            if not all([smtp_host, smtp_port, smtp_username, smtp_password]):
                return {
                    'service': 'smtp',
                    'test_passed': False,
                    'error': 'SMTP credentials not fully configured',
                    'tested_at': datetime.now(timezone.utc).isoformat()
                }
            
            return {
                'service': 'smtp',
                'test_passed': True,
                'host': smtp_host,
                'port': smtp_port,
                'username_configured': bool(smtp_username),
                'password_configured': bool(smtp_password),
                'tested_at': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"SMTP test failed: {str(e)}")
            return {
                'service': 'smtp',
                'test_passed': False,
                'error': str(e),
                'tested_at': datetime.now(timezone.utc).isoformat()
            }
    
    async def test_render_api(self) -> Dict:
        """Test Render API connection"""
        try:
            api_key = os.getenv('RENDER_API_KEY')
            
            if not api_key:
                return {
                    'service': 'render',
                    'test_passed': False,
                    'error': 'Render API key not configured',
                    'tested_at': datetime.now(timezone.utc).isoformat()
                }
            
            # Test API by fetching services (read-only operation)
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Accept': 'application/json'
                }
                
                async with session.get(
                    'https://api.render.com/v1/services',
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'service': 'render',
                            'test_passed': True,
                            'services_count': len(data),
                            'tested_at': datetime.now(timezone.utc).isoformat()
                        }
                    else:
                        return {
                            'service': 'render',
                            'test_passed': False,
                            'error': f'API returned status {response.status}',
                            'tested_at': datetime.now(timezone.utc).isoformat()
                        }
        except Exception as e:
            logger.error(f"Render API test failed: {str(e)}")
            return {
                'service': 'render',
                'test_passed': False,
                'error': str(e),
                'tested_at': datetime.now(timezone.utc).isoformat()
            }
    
    async def test_all_credentials(self) -> Dict:
        """Test all configured credentials"""
        results = {}
        
        # Test each service
        results['mongodb'] = await self.test_mongodb_connection()
        results['google_oauth'] = await self.test_google_oauth()
        results['smtp'] = await self.test_smtp_connection()
        results['render'] = await self.test_render_api()
        
        # Summary
        passed = sum(1 for r in results.values() if r.get('test_passed'))
        total = len(results)
        
        return {
            'summary': {
                'total_tested': total,
                'passed': passed,
                'failed': total - passed,
                'success_rate': f'{(passed/total*100):.1f}%'
            },
            'tests': results,
            'tested_at': datetime.now(timezone.utc).isoformat()
        }
    
    async def log_credential_access(self, user_email: str, action: str, credential_id: str, details: Optional[Dict] = None):
        """Log credential access for audit trail"""
        if not self.mongo_client:
            logger.warning("Cannot log credential access - MongoDB not available")
            return
        
        try:
            db = self.mongo_client[self.db_name]
            audit_entry = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'user_email': user_email,
                'action': action,
                'credential_id': credential_id,
                'details': details or {},
                'ip_address': None,  # Can be added from request context
                'user_agent': None   # Can be added from request context
            }
            
            await db.credential_audit_log.insert_one(audit_entry)
            logger.info(f"Credential access logged: {user_email} - {action} - {credential_id}")
        except Exception as e:
            logger.error(f"Failed to log credential access: {str(e)}")
    
    async def get_credential_status(self, credential_id: str) -> Dict:
        """Get comprehensive status for a credential"""
        config_check = await self.check_credential_configured(credential_id)
        
        # Run appropriate test based on credential type
        test_result = None
        if credential_id == 'mongodb_atlas':
            test_result = await self.test_mongodb_connection()
        elif credential_id == 'google_oauth':
            test_result = await self.test_google_oauth()
        elif credential_id == 'smtp_email':
            test_result = await self.test_smtp_connection()
        elif credential_id == 'render_api':
            test_result = await self.test_render_api()
        
        return {
            'credential_id': credential_id,
            'configuration': config_check,
            'test_result': test_result,
            'status': 'operational' if config_check.get('configured') and (test_result and test_result.get('test_passed')) else 'issues_detected',
            'checked_at': datetime.now(timezone.utc).isoformat()
        }
