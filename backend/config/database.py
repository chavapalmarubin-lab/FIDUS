"""
Database Configuration for FIDUS Investment Management Platform
Environment-aware MongoDB Atlas configuration with connection pooling
"""

import os
import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration manager with environment awareness"""
    
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "production")
        self._load_config()
        
    def _load_config(self):
        """Load database configuration based on environment"""
        
        if self.environment == "production":
            self.connection_string = os.getenv("MONGO_URL")
            self.database_name = os.getenv("DB_NAME", "fidus_production")
        elif self.environment == "test":
            self.connection_string = os.getenv("MONGO_URL_TEST")
            self.database_name = os.getenv("DB_NAME_TEST", "fidus_test")
        elif self.environment == "development":
            self.connection_string = os.getenv("MONGO_URL_DEV", os.getenv("MONGO_URL"))
            self.database_name = os.getenv("DB_NAME_DEV", "fidus_development")
        else:
            raise ValueError(f"Unknown environment: {self.environment}")
        
        if not self.connection_string:
            raise ValueError(f"MONGO_URL not configured for environment: {self.environment}")
        
        # Connection pool settings
        self.min_pool_size = int(os.getenv("MONGO_MIN_POOL_SIZE", "10"))
        self.max_pool_size = int(os.getenv("MONGO_MAX_POOL_SIZE", "50"))
        self.connect_timeout_ms = int(os.getenv("MONGO_CONNECT_TIMEOUT_MS", "5000"))
        self.server_selection_timeout_ms = int(os.getenv("MONGO_SERVER_SELECTION_TIMEOUT_MS", "5000"))
        self.socket_timeout_ms = int(os.getenv("MONGO_SOCKET_TIMEOUT_MS", "10000"))
        self.max_idle_time_ms = int(os.getenv("MONGO_MAX_IDLE_TIME_MS", "60000"))
        
        # Retry settings
        self.max_retry_attempts = int(os.getenv("MONGO_MAX_RETRY_ATTEMPTS", "3"))
        self.retry_delay_ms = int(os.getenv("MONGO_RETRY_DELAY_MS", "1000"))
        
        logger.info(f"Database config loaded for environment: {self.environment}")
        logger.info(f"Database: {self.database_name}")
        logger.info(f"Connection pool: {self.min_pool_size}-{self.max_pool_size}")

class ConnectionManager:
    """Singleton MongoDB connection manager with connection pooling and error handling"""
    
    _instance = None
    _client: Optional[AsyncIOMotorClient] = None
    _database = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConnectionManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._config = DatabaseConfig()
            
    async def get_client(self) -> AsyncIOMotorClient:
        """Get or create MongoDB client with connection pooling"""
        if self._client is None:
            await self._create_connection()
        
        return self._client
    
    async def get_database(self):
        """Get database instance"""
        if self._database is None:
            client = await self.get_client()
            self._database = client[self._config.database_name]
        
        return self._database
    
    async def _create_connection(self):
        """Create MongoDB connection with retry logic"""
        for attempt in range(self._config.max_retry_attempts):
            try:
                logger.info(f"Creating MongoDB connection (attempt {attempt + 1}/{self._config.max_retry_attempts})")
                
                self._client = AsyncIOMotorClient(
                    self._config.connection_string,
                    minPoolSize=self._config.min_pool_size,
                    maxPoolSize=self._config.max_pool_size,
                    connectTimeoutMS=self._config.connect_timeout_ms,
                    serverSelectionTimeoutMS=self._config.server_selection_timeout_ms,
                    socketTimeoutMS=self._config.socket_timeout_ms,
                    maxIdleTimeMS=self._config.max_idle_time_ms,
                    retryWrites=True,
                    w="majority"
                )
                
                # Test connection
                await self._client.admin.command('ping')
                logger.info("✅ MongoDB connection established successfully")
                
                # Get database instance
                self._database = self._client[self._config.database_name]
                
                return
                
            except (ServerSelectionTimeoutError, ConnectionFailure) as e:
                logger.error(f"❌ MongoDB connection attempt {attempt + 1} failed: {e}")
                
                if attempt < self._config.max_retry_attempts - 1:
                    await asyncio.sleep(self._config.retry_delay_ms / 1000 * (2 ** attempt))  # Exponential backoff
                else:
                    raise ConnectionError(f"Failed to connect to MongoDB after {self._config.max_retry_attempts} attempts: {e}")
            
            except Exception as e:
                logger.error(f"❌ Unexpected error during MongoDB connection: {e}")
                raise
    
    async def health_check(self) -> dict:
        """Perform database health check"""
        try:
            client = await self.get_client()
            
            # Test ping
            start_time = asyncio.get_event_loop().time()
            await client.admin.command('ping')
            ping_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            # Get server status
            server_status = await client.admin.command('serverStatus')
            
            # Get database stats
            db = await self.get_database()
            db_stats = await db.command('dbStats')
            
            return {
                'status': 'healthy',
                'ping_time_ms': round(ping_time, 2),
                'server_version': server_status.get('version'),
                'database': self._config.database_name,
                'environment': self._config.environment,
                'collections_count': db_stats.get('collections', 0),
                'objects_count': db_stats.get('objects', 0),
                'data_size_mb': round(db_stats.get('dataSize', 0) / 1024 / 1024, 2),
                'storage_size_mb': round(db_stats.get('storageSize', 0) / 1024 / 1024, 2),
                'connection_pool': {
                    'min_size': self._config.min_pool_size,
                    'max_size': self._config.max_pool_size,
                    'current_size': len(self._client.nodes) if self._client else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'database': self._config.database_name,
                'environment': self._config.environment
            }
    
    async def close_connection(self):
        """Close database connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            logger.info("MongoDB connection closed")

# Global connection manager instance
connection_manager = ConnectionManager()

# Convenience functions for backward compatibility
async def get_database():
    """Get database instance"""
    return await connection_manager.get_database()

async def get_client():
    """Get MongoDB client"""
    return await connection_manager.get_client()

async def health_check():
    """Perform database health check"""
    return await connection_manager.health_check()