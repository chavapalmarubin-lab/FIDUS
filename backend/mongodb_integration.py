"""
MongoDB Integration for FIDUS Investment Management System
Provides database operations for production-ready data management
"""
import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import bcrypt

# Get MongoDB URL from environment
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/fidus_investment_db')

class MongoDBManager:
    def __init__(self):
        try:
            self.client = MongoClient(MONGO_URL)
            self.db_name = MONGO_URL.split('/')[-1]
            self.db = self.client[self.db_name]
            
            # Test connection
            self.client.admin.command('ping')
            print(f"✅ MongoDB connected to: {self.db_name}")
            
        except Exception as e:
            print(f"❌ MongoDB connection failed: {str(e)}")
            raise
    
    # ===============================================================================
    # USER MANAGEMENT
    # ===============================================================================
    
    def authenticate_user(self, username: str, password: str, user_type: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with MongoDB credentials"""
        try:
            # Find user by username and type
            user = self.db.users.find_one({
                'username': username,
                'user_type': user_type,
                'status': 'active'
            })
            
            if not user:
                return None
            
            # Verify password
            if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                # Get additional profile information for clients
                profile_data = {}
                if user_type == 'client':
                    profile = self.db.client_profiles.find_one({'client_id': user['user_id']})
                    if profile:
                        profile_data = {
                            'name': profile.get('name', username),
                            'email': profile.get('email', user['email']),
                            'phone': profile.get('phone', ''),
                            'fidus_account_number': profile.get('fidus_account_number', '')
                        }
                
                return {
                    'id': user['user_id'],
                    'username': user['username'],
                    'email': user['email'],
                    'type': user['user_type'],
                    'status': user['status'],
                    **profile_data
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return None
    
    def get_all_clients(self) -> List[Dict[str, Any]]:
        """Get all client users with their profiles and readiness status"""
        try:
            clients = []
            
            # Get all client users
            client_users = self.db.users.find({'user_type': 'client', 'status': 'active'})
            
            for user in client_users:
                client_id = user['user_id']
                
                # Get client profile
                profile = self.db.client_profiles.find_one({'client_id': client_id})
                
                # Get readiness status
                readiness = self.db.client_readiness.find_one({'client_id': client_id})
                
                # Get investment count
                investment_count = self.db.investments.count_documents({'client_id': client_id})
                
                # Calculate total invested amount
                total_invested = 0
                investments = self.db.investments.find({'client_id': client_id})
                for inv in investments:
                    total_invested += inv.get('principal_amount', 0)
                
                # Format readiness status properly (remove ObjectId)
                readiness_data = {}
                if readiness:
                    readiness_data = {
                        'client_id': readiness.get('client_id'),
                        'aml_kyc_completed': readiness.get('aml_kyc_completed', False),
                        'agreement_signed': readiness.get('agreement_signed', False),
                        'account_creation_date': readiness.get('account_creation_date').isoformat() if readiness.get('account_creation_date') else None,
                        'investment_ready': readiness.get('investment_ready', False),
                        'notes': readiness.get('notes', '')
                    }
                else:
                    readiness_data = {
                        'client_id': client_id,
                        'aml_kyc_completed': False,
                        'agreement_signed': False,
                        'account_creation_date': None,
                        'investment_ready': False,
                        'notes': ''
                    }
                
                client_data = {
                    'id': client_id,
                    'username': user['username'],
                    'name': profile.get('name', user['username']) if profile else user['username'],
                    'email': profile.get('email', user['email']) if profile else user['email'],
                    'phone': profile.get('phone', '') if profile else '',
                    'type': user['user_type'],
                    'status': user['status'],
                    'fidus_account_number': profile.get('fidus_account_number', '') if profile else '',
                    'total_investments': investment_count,
                    'total_invested': total_invested,
                    'readiness_status': readiness_data,
                    'investment_ready': readiness_data.get('investment_ready', False),
                    'created_at': user.get('created_at', datetime.now(timezone.utc)).isoformat()
                }
                
                clients.append(client_data)
            
            # Sort by creation date (newest first)
            clients.sort(key=lambda x: x['created_at'], reverse=True)
            
            return clients
            
        except Exception as e:
            print(f"❌ Error getting clients: {str(e)}")
            return []
    
    # ===============================================================================
    # INVESTMENT MANAGEMENT
    # ===============================================================================
    
    def create_investment(self, investment_data: Dict[str, Any]) -> Optional[str]:
        """Create a new investment in the database"""
        try:
            # Generate investment ID
            investment_id = str(uuid.uuid4())
            
            # Prepare investment document
            investment_doc = {
                'investment_id': investment_id,
                'client_id': investment_data['client_id'],
                'fund_code': investment_data['fund_code'],
                'principal_amount': investment_data['amount'],
                'deposit_date': investment_data.get('deposit_date', datetime.now(timezone.utc)),
                'incubation_end_date': investment_data['incubation_end_date'],
                'interest_start_date': investment_data['interest_start_date'],
                'minimum_hold_end_date': investment_data['minimum_hold_end_date'],
                'status': 'incubating',
                'created_at': datetime.now(timezone.utc)
            }
            
            # Insert investment
            result = self.db.investments.insert_one(investment_doc)
            
            if result.inserted_id:
                # Create activity log
                self.log_activity({
                    'client_id': investment_data['client_id'],
                    'activity_type': 'deposit',
                    'amount': investment_data['amount'],
                    'fund_code': investment_data['fund_code'],
                    'description': f"Investment created in {investment_data['fund_code']} fund"
                })
                
                return investment_id
            
            return None
            
        except Exception as e:
            print(f"❌ Error creating investment: {str(e)}")
            return None
    
    def get_client_investments(self, client_id: str) -> List[Dict[str, Any]]:
        """Get all investments for a specific client"""
        try:
            investments = []
            
            investment_docs = self.db.investments.find({'client_id': client_id})
            
            for inv in investment_docs:
                # Calculate current value (simple interest)
                principal = inv['principal_amount']
                deposit_date = inv['deposit_date']
                interest_start_date = inv['interest_start_date']
                
                # Get fund config for interest rate
                fund_config = self.db.fund_configurations.find_one({'fund_code': inv['fund_code']})
                monthly_rate = fund_config.get('monthly_interest_rate', 0) if fund_config else 0
                
                # Calculate interest earned
                current_date = datetime.now(timezone.utc)
                interest_earned = 0
                
                if current_date > interest_start_date:
                    months_earning = max(0, (current_date.year - interest_start_date.year) * 12 + 
                                          (current_date.month - interest_start_date.month))
                    interest_earned = principal * monthly_rate * months_earning
                
                current_value = principal + interest_earned
                
                investment_data = {
                    'investment_id': inv['investment_id'],
                    'fund_code': inv['fund_code'],
                    'fund_name': f"FIDUS {inv['fund_code'].title()} Fund",
                    'principal_amount': principal,
                    'current_value': current_value,
                    'interest_earned': interest_earned,
                    'deposit_date': inv['deposit_date'].isoformat(),
                    'incubation_end_date': inv['incubation_end_date'].isoformat(),
                    'interest_start_date': inv['interest_start_date'].isoformat(),
                    'minimum_hold_end_date': inv['minimum_hold_end_date'].isoformat(),
                    'status': inv['status'],
                    'monthly_interest_rate': monthly_rate,
                    'can_redeem_interest': current_date > inv['interest_start_date'],
                    'can_redeem_principal': current_date > inv['minimum_hold_end_date'],
                    'created_at': inv.get('created_at', datetime.now(timezone.utc)).isoformat()
                }
                
                investments.append(investment_data)
            
            # Sort by creation date (newest first)
            investments.sort(key=lambda x: x['created_at'], reverse=True)
            
            return investments
            
        except Exception as e:
            print(f"❌ Error getting client investments: {str(e)}")
            return []
    
    def get_fund_configurations(self) -> List[Dict[str, Any]]:
        """Get all fund configurations"""
        try:
            funds = []
            fund_docs = self.db.fund_configurations.find({})
            
            for fund in fund_docs:
                # Calculate AUM from actual investments
                pipeline = [
                    {'$match': {'fund_code': fund['fund_code']}},
                    {'$group': {'_id': None, 'total_aum': {'$sum': '$principal_amount'}}}
                ]
                
                aum_result = list(self.db.investments.aggregate(pipeline))
                actual_aum = aum_result[0]['total_aum'] if aum_result else 0
                
                # Count investors
                investor_count = len(self.db.investments.distinct('client_id', {'fund_code': fund['fund_code']}))
                
                fund_data = {
                    'fund_code': fund['fund_code'],
                    'name': fund['name'],
                    'monthly_interest_rate': fund['monthly_interest_rate'],
                    'annual_interest_rate': fund['monthly_interest_rate'] * 12,
                    'minimum_investment': fund['minimum_investment'],
                    'redemption_frequency': fund['redemption_frequency'],
                    'aum': actual_aum,
                    'nav_per_share': fund.get('nav_per_share', 100.0),
                    'performance_ytd': fund.get('performance_ytd', 0.0),
                    'total_investors': investor_count,
                    'incubation_period_months': 2,
                    'minimum_hold_period_months': 14
                }
                
                funds.append(fund_data)
            
            return funds
            
        except Exception as e:
            print(f"❌ Error getting fund configurations: {str(e)}")
            return []
    
    # ===============================================================================
    # CLIENT READINESS MANAGEMENT
    # ===============================================================================
    
    def get_client_readiness(self, client_id: str) -> Dict[str, Any]:
        """Get client readiness status"""
        try:
            readiness = self.db.client_readiness.find_one({'client_id': client_id})
            
            if readiness:
                return {
                    'client_id': client_id,
                    'aml_kyc_completed': readiness.get('aml_kyc_completed', False),
                    'agreement_signed': readiness.get('agreement_signed', False),
                    'account_creation_date': readiness.get('account_creation_date'),
                    'investment_ready': readiness.get('investment_ready', False),
                    'notes': readiness.get('notes', '')
                }
            else:
                # Return default readiness status
                return {
                    'client_id': client_id,
                    'aml_kyc_completed': False,
                    'agreement_signed': False,
                    'account_creation_date': None,
                    'investment_ready': False,
                    'notes': ''
                }
                
        except Exception as e:
            print(f"❌ Error getting client readiness: {str(e)}")
            return {}
    
    def update_client_readiness(self, client_id: str, readiness_data: Dict[str, Any]) -> bool:
        """Update client readiness status"""
        try:
            # Calculate investment_ready status
            investment_ready = (
                readiness_data.get('aml_kyc_completed', False) and
                readiness_data.get('agreement_signed', False) and
                readiness_data.get('account_creation_date') is not None
            )
            
            update_data = {
                'client_id': client_id,
                'aml_kyc_completed': readiness_data.get('aml_kyc_completed', False),
                'agreement_signed': readiness_data.get('agreement_signed', False),
                'account_creation_date': readiness_data.get('account_creation_date'),
                'investment_ready': investment_ready,
                'notes': readiness_data.get('notes', ''),
                'updated_at': datetime.now(timezone.utc)
            }
            
            # Use upsert to create or update
            result = self.db.client_readiness.update_one(
                {'client_id': client_id},
                {'$set': update_data},
                upsert=True
            )
            
            return result.acknowledged
            
        except Exception as e:
            print(f"❌ Error updating client readiness: {str(e)}")
            return False
    
    # ===============================================================================
    # ACTIVITY LOGGING
    # ===============================================================================
    
    def log_activity(self, activity_data: Dict[str, Any]) -> bool:
        """Log client activity"""
        try:
            log_entry = {
                'log_id': str(uuid.uuid4()),
                'client_id': activity_data['client_id'],
                'activity_type': activity_data['activity_type'],
                'amount': activity_data.get('amount', 0),
                'fund_code': activity_data.get('fund_code', ''),
                'description': activity_data.get('description', ''),
                'timestamp': datetime.now(timezone.utc)
            }
            
            result = self.db.activity_logs.insert_one(log_entry)
            return result.acknowledged
            
        except Exception as e:
            print(f"❌ Error logging activity: {str(e)}")
            return False
    
    def get_client_activity_logs(self, client_id: str) -> List[Dict[str, Any]]:
        """Get activity logs for a client"""
        try:
            logs = []
            
            log_docs = self.db.activity_logs.find({'client_id': client_id}).sort('timestamp', -1)
            
            for log in log_docs:
                log_data = {
                    'id': log['log_id'],
                    'client_id': log['client_id'],
                    'activity_type': log['activity_type'],
                    'amount': log.get('amount', 0),
                    'fund_code': log.get('fund_code', ''),
                    'description': log.get('description', ''),
                    'timestamp': log['timestamp'].isoformat()
                }
                logs.append(log_data)
            
            return logs
            
        except Exception as e:
            print(f"❌ Error getting activity logs: {str(e)}")
            return []
    
    # ===============================================================================
    # FUND PORTFOLIO MANAGEMENT
    # ===============================================================================
    
    def get_fund_overview(self) -> Dict[str, Any]:
        """Get comprehensive fund overview for admin dashboard"""
        try:
            # Get all fund configurations
            funds = self.get_fund_configurations()
            
            total_aum = sum(fund['aum'] for fund in funds)
            total_investors = len(self.db.investments.distinct('client_id'))
            active_funds = len([f for f in funds if f['aum'] > 0])
            
            # Calculate weighted average return
            total_weighted_return = sum(fund['aum'] * fund['performance_ytd'] for fund in funds if fund['aum'] > 0)
            avg_return = total_weighted_return / total_aum if total_aum > 0 else 0
            
            overview = {
                'total_aum': total_aum,
                'total_investors': total_investors,
                'active_funds': active_funds,
                'average_return': avg_return,
                'funds': funds
            }
            
            return overview
            
        except Exception as e:
            print(f"❌ Error getting fund overview: {str(e)}")
            return {}
    
    # ===============================================================================
    # DATABASE UTILITIES
    # ===============================================================================
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics for monitoring"""
        try:
            stats = {
                'database_name': self.db_name,
                'collections': {},
                'total_documents': 0
            }
            
            collections = ['users', 'client_profiles', 'investments', 'client_readiness', 
                          'fund_configurations', 'activity_logs', 'redemption_requests',
                          'payment_confirmations', 'crm_prospects', 'fund_rebates']
            
            for collection_name in collections:
                count = self.db[collection_name].count_documents({})
                stats['collections'][collection_name] = count
                stats['total_documents'] += count
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting database stats: {str(e)}")
            return {}

# Global MongoDB manager instance
mongodb_manager = MongoDBManager()