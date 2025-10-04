"""
User Repository for FIDUS Investment Management Platform
Specialized repository for user operations with authentication support
"""

import bcrypt
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from .base_repository import BaseRepository
from models.user import User, UserCreate, UserUpdate, UserRole, KYCStatus, AMLStatus, UserStats, UserSearch

logger = logging.getLogger(__name__)

class UserRepository(BaseRepository[User]):
    """Repository for user operations"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "users", User)
    
    async def create_user(self, user_data: UserCreate) -> Optional[User]:
        """Create a new user with password hashing"""
        try:
            # Hash the password
            password_hash = self._hash_password(user_data.password)
            
            # Prepare user data
            user_dict = user_data.dict(exclude={'password'})
            user_dict['password_hash'] = password_hash
            user_dict['user_id'] = user_dict.get('user_id', str(user_dict.get('_id', '')))
            user_dict['login_attempts'] = 0
            user_dict['is_active'] = True
            user_dict['is_verified'] = False
            
            return await self.create(user_dict)
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user by username/email and password"""
        try:
            # Find user by username or email
            user = await self.collection.find_one({
                '$or': [
                    {'username': username.lower()},
                    {'email': username.lower()}
                ]
            })
            
            if not user:
                return None
            
            # Check if account is active
            if not user.get('is_active', False):
                return None
            
            # Check password
            if not self._verify_password(password, user.get('password_hash', '')):
                # Increment login attempts
                await self.collection.update_one(
                    {'_id': user['_id']},
                    {'$inc': {'login_attempts': 1}}
                )
                return None
            
            # Successful authentication - reset login attempts and update last login
            await self.collection.update_one(
                {'_id': user['_id']},
                {
                    '$set': {
                        'last_login': datetime.now(timezone.utc),
                        'login_attempts': 0
                    }
                }
            )
            
            return self._parse_from_mongo(user)
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            raise
    
    async def update_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Update user password with verification"""
        try:
            # Get current user
            user = await self.find_by_id(user_id)
            if not user:
                return False
            
            # Get user document for password hash
            user_doc = await self.collection.find_one({'$or': [
                {'_id': user_id},
                {'user_id': user_id}
            ]})
            
            if not user_doc:
                return False
            
            # Verify current password
            if not self._verify_password(current_password, user_doc.get('password_hash', '')):
                return False
            
            # Hash new password
            new_password_hash = self._hash_password(new_password)
            
            # Update password
            result = await self.collection.update_one(
                {'_id': user_doc['_id']},
                {
                    '$set': {
                        'password_hash': new_password_hash,
                        'updated_at': datetime.now(timezone.utc)
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating password for user {user_id}: {e}")
            raise
    
    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        return await self.find_one({'email': email.lower()})
    
    async def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username"""
        return await self.find_one({'username': username.lower()})
    
    async def get_users_by_role(self, role: UserRole) -> List[User]:
        """Get all users with specific role"""
        return await self.find_many({'user_type': role.value})
    
    async def get_active_users(self) -> List[User]:
        """Get all active users"""
        return await self.find_many({'is_active': True})
    
    async def search_users(self, search_params: UserSearch) -> Dict[str, Any]:
        """Advanced user search with pagination"""
        try:
            # Build filter
            filter_dict = {}
            
            if search_params.query:
                filter_dict['$or'] = [
                    {'username': {'$regex': search_params.query, '$options': 'i'}},
                    {'email': {'$regex': search_params.query, '$options': 'i'}},
                    {'full_name': {'$regex': search_params.query, '$options': 'i'}}
                ]
            
            if search_params.user_type:
                filter_dict['user_type'] = search_params.user_type.value
            
            if search_params.is_active is not None:
                filter_dict['is_active'] = search_params.is_active
            
            if search_params.is_verified is not None:
                filter_dict['is_verified'] = search_params.is_verified
            
            if search_params.kyc_status:
                filter_dict['kyc_status'] = search_params.kyc_status.value
            
            if search_params.aml_status:
                filter_dict['aml_status'] = search_params.aml_status.value
            
            if search_params.created_after:
                filter_dict.setdefault('created_at', {})['$gte'] = search_params.created_after
            
            if search_params.created_before:
                filter_dict.setdefault('created_at', {})['$lte'] = search_params.created_before
            
            # Build sort
            sort = [(search_params.sort_by, search_params.sort_order)]
            
            # Get total count
            total_count = await self.count(filter_dict)
            
            # Get users
            users = await self.find_many(
                filter_dict=filter_dict,
                limit=search_params.limit,
                skip=search_params.skip,
                sort=sort
            )
            
            return {
                'users': users,
                'total_count': total_count,
                'page': (search_params.skip // search_params.limit) + 1,
                'total_pages': (total_count + search_params.limit - 1) // search_params.limit,
                'has_next': search_params.skip + search_params.limit < total_count,
                'has_prev': search_params.skip > 0
            }
            
        except Exception as e:
            logger.error(f"Error searching users: {e}")
            raise
    
    async def get_user_stats(self) -> UserStats:
        """Get comprehensive user statistics"""
        try:
            # Aggregation pipeline for stats
            pipeline = [
                {
                    '$group': {
                        '_id': None,
                        'total_users': {'$sum': 1},
                        'active_users': {
                            '$sum': {'$cond': [{'$eq': ['$is_active', True]}, 1, 0]}
                        },
                        'verified_users': {
                            '$sum': {'$cond': [{'$eq': ['$is_verified', True]}, 1, 0]}
                        }
                    }
                }
            ]
            
            stats_result = await self.aggregate(pipeline)
            base_stats = stats_result[0] if stats_result else {
                'total_users': 0,
                'active_users': 0,
                'verified_users': 0
            }
            
            # Get role distribution
            role_pipeline = [
                {'$group': {'_id': '$user_type', 'count': {'$sum': 1}}}
            ]
            role_stats = await self.aggregate(role_pipeline)
            by_role = {item['_id']: item['count'] for item in role_stats}
            
            # Get KYC status distribution
            kyc_pipeline = [
                {'$group': {'_id': '$kyc_status', 'count': {'$sum': 1}}}
            ]
            kyc_stats = await self.aggregate(kyc_pipeline)
            by_kyc_status = {item['_id']: item['count'] for item in kyc_stats}
            
            # Get AML status distribution
            aml_pipeline = [
                {'$group': {'_id': '$aml_status', 'count': {'$sum': 1}}}
            ]
            aml_stats = await self.aggregate(aml_pipeline)
            by_aml_status = {item['_id']: item['count'] for item in aml_stats}
            
            # Get recent registrations (last 30 days)
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            recent_registrations = await self.count({'created_at': {'$gte': thirty_days_ago}})
            
            return UserStats(
                total_users=base_stats['total_users'],
                active_users=base_stats['active_users'],
                verified_users=base_stats['verified_users'],
                by_role=by_role,
                by_kyc_status=by_kyc_status,
                by_aml_status=by_aml_status,
                recent_registrations=recent_registrations
            )
            
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            raise
    
    async def update_kyc_status(self, user_id: str, kyc_status: KYCStatus) -> bool:
        """Update user KYC status"""
        try:
            result = await self.update_by_id(user_id, {'kyc_status': kyc_status.value})
            return result is not None
            
        except Exception as e:
            logger.error(f"Error updating KYC status for user {user_id}: {e}")
            raise
    
    async def update_aml_status(self, user_id: str, aml_status: AMLStatus) -> bool:
        """Update user AML status"""
        try:
            result = await self.update_by_id(user_id, {'aml_status': aml_status.value})
            return result is not None
            
        except Exception as e:
            logger.error(f"Error updating AML status for user {user_id}: {e}")
            raise
    
    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account"""
        try:
            result = await self.update_by_id(user_id, {'is_active': False})
            return result is not None
            
        except Exception as e:
            logger.error(f"Error deactivating user {user_id}: {e}")
            raise
    
    async def activate_user(self, user_id: str) -> bool:
        """Activate user account"""
        try:
            result = await self.update_by_id(user_id, {'is_active': True})
            return result is not None
            
        except Exception as e:
            logger.error(f"Error activating user {user_id}: {e}")
            raise
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        return password_hash.decode('utf-8')
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception:
            return False