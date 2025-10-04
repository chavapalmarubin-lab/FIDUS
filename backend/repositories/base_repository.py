"""
Base Repository for FIDUS Investment Management Platform
Generic CRUD operations for MongoDB collections
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Type, TypeVar, Generic
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
import logging
from bson import ObjectId
from pymongo.errors import DuplicateKeyError, PyMongoError
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

logger = logging.getLogger(__name__)

class BaseRepository(ABC, Generic[T]):
    """Abstract base repository with common CRUD operations"""
    
    def __init__(self, database: AsyncIOMotorDatabase, collection_name: str, model_class: Type[T]):
        self.db = database
        self.collection: AsyncIOMotorCollection = database[collection_name]
        self.collection_name = collection_name
        self.model_class = model_class
        
    async def create(self, data: Dict[str, Any]) -> Optional[T]:
        """Create a new document"""
        try:
            # Add timestamps
            now = datetime.now(timezone.utc)
            data.setdefault('created_at', now)
            data.setdefault('updated_at', now)
            
            # Prepare data for MongoDB
            prepared_data = self._prepare_for_mongo(data)
            
            result = await self.collection.insert_one(prepared_data)
            
            if result.inserted_id:
                created_doc = await self.collection.find_one({'_id': result.inserted_id})
                return self._parse_from_mongo(created_doc)
            
            return None
            
        except DuplicateKeyError as e:
            logger.error(f"Duplicate key error in {self.collection_name}: {e}")
            raise ValueError(f"Document with unique field already exists")
        
        except PyMongoError as e:
            logger.error(f"Database error in {self.collection_name}.create: {e}")
            raise
        
        except Exception as e:
            logger.error(f"Unexpected error in {self.collection_name}.create: {e}")
            raise
    
    async def find_by_id(self, doc_id: str) -> Optional[T]:
        """Find document by ID"""
        try:
            # Try both _id and custom ID fields
            query = {'_id': doc_id}
            
            # If it's not a valid ObjectId, try as string
            try:
                query['_id'] = ObjectId(doc_id)
            except:
                # Also search by common ID fields
                query = {'$or': [
                    {'_id': doc_id},
                    {'user_id': doc_id},
                    {'investment_id': doc_id},
                    {'account_id': doc_id}
                ]}
            
            document = await self.collection.find_one(query)
            
            if document:
                return self._parse_from_mongo(document)
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding document by ID in {self.collection_name}: {e}")
            raise
    
    async def find_one(self, filter_dict: Dict[str, Any]) -> Optional[T]:
        """Find single document by filter"""
        try:
            document = await self.collection.find_one(filter_dict)
            
            if document:
                return self._parse_from_mongo(document)
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding document in {self.collection_name}: {e}")
            raise
    
    async def find_many(self, 
                       filter_dict: Dict[str, Any] = None, 
                       limit: int = 50, 
                       skip: int = 0,
                       sort: List[tuple] = None) -> List[T]:
        """Find multiple documents"""
        try:
            filter_dict = filter_dict or {}
            
            cursor = self.collection.find(filter_dict)
            
            if sort:
                cursor = cursor.sort(sort)
            
            cursor = cursor.skip(skip).limit(limit)
            
            documents = await cursor.to_list(length=limit)
            
            return [self._parse_from_mongo(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error finding documents in {self.collection_name}: {e}")
            raise
    
    async def update_by_id(self, doc_id: str, update_data: Dict[str, Any]) -> Optional[T]:
        """Update document by ID"""
        try:
            # Add update timestamp
            update_data['updated_at'] = datetime.now(timezone.utc)
            
            # Prepare data for MongoDB
            prepared_data = self._prepare_for_mongo(update_data)
            
            # Try both _id and custom ID fields
            query = {'_id': doc_id}
            
            try:
                query['_id'] = ObjectId(doc_id)
            except:
                query = {'$or': [
                    {'_id': doc_id},
                    {'user_id': doc_id},
                    {'investment_id': doc_id},
                    {'account_id': doc_id}
                ]}
            
            result = await self.collection.find_one_and_update(
                query,
                {'$set': prepared_data},
                return_document=True
            )
            
            if result:
                return self._parse_from_mongo(result)
            
            return None
            
        except Exception as e:
            logger.error(f"Error updating document in {self.collection_name}: {e}")
            raise
    
    async def delete_by_id(self, doc_id: str) -> bool:
        """Delete document by ID"""
        try:
            # Try both _id and custom ID fields
            query = {'_id': doc_id}
            
            try:
                query['_id'] = ObjectId(doc_id)
            except:
                query = {'$or': [
                    {'_id': doc_id},
                    {'user_id': doc_id},
                    {'investment_id': doc_id},
                    {'account_id': doc_id}
                ]}
            
            result = await self.collection.delete_one(query)
            
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting document in {self.collection_name}: {e}")
            raise
    
    async def count(self, filter_dict: Dict[str, Any] = None) -> int:
        """Count documents matching filter"""
        try:
            filter_dict = filter_dict or {}
            return await self.collection.count_documents(filter_dict)
            
        except Exception as e:
            logger.error(f"Error counting documents in {self.collection_name}: {e}")
            raise
    
    async def exists(self, filter_dict: Dict[str, Any]) -> bool:
        """Check if document exists"""
        try:
            count = await self.collection.count_documents(filter_dict, limit=1)
            return count > 0
            
        except Exception as e:
            logger.error(f"Error checking document existence in {self.collection_name}: {e}")
            raise
    
    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute aggregation pipeline"""
        try:
            cursor = self.collection.aggregate(pipeline)
            return await cursor.to_list(length=None)
            
        except Exception as e:
            logger.error(f"Error executing aggregation in {self.collection_name}: {e}")
            raise
    
    def _prepare_for_mongo(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for MongoDB storage"""
        prepared = {}
        
        for key, value in data.items():
            if value is None:
                continue
                
            # Handle datetime objects
            if hasattr(value, 'isoformat'):
                prepared[key] = value
            # Handle Decimal objects
            elif hasattr(value, '__float__'):
                prepared[key] = float(value)
            # Handle Enum objects
            elif hasattr(value, 'value'):
                prepared[key] = value.value
            else:
                prepared[key] = value
        
        return prepared
    
    def _parse_from_mongo(self, document: Dict[str, Any]) -> T:
        """Parse MongoDB document to Pydantic model"""
        if not document:
            return None
        
        # Convert ObjectId to string
        if '_id' in document and isinstance(document['_id'], ObjectId):
            document['_id'] = str(document['_id'])
        
        # Handle datetime strings
        for key, value in document.items():
            if isinstance(value, str) and key.endswith('_at'):
                try:
                    document[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except:
                    pass
        
        return self.model_class(**document)
    
    async def create_index(self, keys: Dict[str, int], **kwargs):
        """Create index on collection"""
        try:
            await self.collection.create_index(list(keys.items()), **kwargs)
            logger.info(f"Index created on {self.collection_name}: {keys}")
            
        except Exception as e:
            logger.error(f"Error creating index on {self.collection_name}: {e}")
            raise
    
    async def create_indexes(self, indexes: List[Dict[str, Any]]):
        """Create multiple indexes"""
        try:
            for index_spec in indexes:
                keys = index_spec['keys']
                options = index_spec.get('options', {})
                await self.create_index(keys, **options)
            
            logger.info(f"All indexes created for {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Error creating indexes for {self.collection_name}: {e}")
            raise
    
    async def drop_indexes(self):
        """Drop all indexes except _id"""
        try:
            await self.collection.drop_indexes()
            logger.info(f"Indexes dropped for {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Error dropping indexes for {self.collection_name}: {e}")
            raise
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            stats = await self.db.command("collStats", self.collection_name)
            
            return {
                'collection': self.collection_name,
                'count': stats.get('count', 0),
                'size': stats.get('size', 0),
                'storage_size': stats.get('storageSize', 0),
                'avg_obj_size': stats.get('avgObjSize', 0),
                'indexes': stats.get('nindexes', 0),
                'total_index_size': stats.get('totalIndexSize', 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting stats for {self.collection_name}: {e}")
            return {
                'collection': self.collection_name,
                'count': await self.count(),
                'error': str(e)
            }