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
                    'name': profile_data.get('name', user['username']),
                    'email': profile_data.get('email', user['email']),
                    'type': user['user_type'],
                    'status': user['status'],
                    'profile_picture': '/app/static/default_profile.jpg',  # Default profile picture
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
            
            # Convert dates to datetime objects if they're strings
            deposit_date = investment_data.get('deposit_date', datetime.now(timezone.utc))
            if isinstance(deposit_date, str):
                try:
                    deposit_date = datetime.fromisoformat(deposit_date.replace('Z', '+00:00')).replace(tzinfo=timezone.utc)
                except:
                    deposit_date = datetime.strptime(deposit_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            
            incubation_end_date = investment_data['incubation_end_date']
            if isinstance(incubation_end_date, str):
                try:
                    incubation_end_date = datetime.fromisoformat(incubation_end_date.replace('Z', '+00:00')).replace(tzinfo=timezone.utc)
                except:
                    incubation_end_date = datetime.strptime(incubation_end_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            
            interest_start_date = investment_data['interest_start_date']
            if isinstance(interest_start_date, str):
                try:
                    interest_start_date = datetime.fromisoformat(interest_start_date.replace('Z', '+00:00')).replace(tzinfo=timezone.utc)
                except:
                    interest_start_date = datetime.strptime(interest_start_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            
            minimum_hold_end_date = investment_data['minimum_hold_end_date']
            if isinstance(minimum_hold_end_date, str):
                try:
                    minimum_hold_end_date = datetime.fromisoformat(minimum_hold_end_date.replace('Z', '+00:00')).replace(tzinfo=timezone.utc)
                except:
                    minimum_hold_end_date = datetime.strptime(minimum_hold_end_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            
            # Prepare investment document
            investment_doc = {
                'investment_id': investment_id,
                'client_id': investment_data['client_id'],
                'fund_code': investment_data['fund_code'],
                'principal_amount': investment_data['amount'],
                'deposit_date': deposit_date,
                'incubation_end_date': incubation_end_date,
                'interest_start_date': interest_start_date,
                'minimum_hold_end_date': minimum_hold_end_date,
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
                
                # Ensure interest_start_date is timezone-aware
                if interest_start_date.tzinfo is None:
                    interest_start_date = interest_start_date.replace(tzinfo=timezone.utc)
                
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
                    'status': 'active' if current_date > (inv['interest_start_date'].replace(tzinfo=timezone.utc) if inv['interest_start_date'].tzinfo is None else inv['interest_start_date']) else 'incubating',
                    'monthly_interest_rate': monthly_rate,
                    'can_redeem_interest': current_date > (inv['interest_start_date'].replace(tzinfo=timezone.utc) if inv['interest_start_date'].tzinfo is None else inv['interest_start_date']),
                    'can_redeem_principal': current_date > (inv['minimum_hold_end_date'].replace(tzinfo=timezone.utc) if inv['minimum_hold_end_date'].tzinfo is None else inv['minimum_hold_end_date']),
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
    
    def get_client(self, client_id: str) -> Dict[str, Any]:
        """Get client by ID"""
        try:
            # Look in users collection with user_id field for clients
            client = self.db.users.find_one({"user_id": client_id, "user_type": "client"})
            if client:
                # Remove MongoDB _id for JSON serialization
                client.pop('_id', None)
                return client
            return {}
                
        except Exception as e:
            print(f"❌ Error getting client: {str(e)}")
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
    # MT5 ACCOUNT MANAGEMENT
    # ===============================================================================
    
    def create_mt5_account(self, mt5_account_data: Dict[str, Any]) -> Optional[str]:
        """Create a new MT5 account mapping"""
        try:
            account_doc = {
                'account_id': mt5_account_data['account_id'],
                'client_id': mt5_account_data['client_id'],
                'fund_code': mt5_account_data['fund_code'],
                'broker_code': mt5_account_data.get('broker_code'),  # NEW: Store broker code
                'broker_name': mt5_account_data.get('broker_name'),  # NEW: Store broker name
                'mt5_login': mt5_account_data['mt5_login'],
                'mt5_server': mt5_account_data['mt5_server'],
                'total_allocated': mt5_account_data['total_allocated'],
                'current_equity': mt5_account_data.get('current_equity', mt5_account_data['total_allocated']),
                'profit_loss': mt5_account_data.get('profit_loss', 0.0),
                'investment_ids': mt5_account_data.get('investment_ids', []),
                'status': mt5_account_data.get('status', 'active'),
                'manual_entry': mt5_account_data.get('manual_entry', False),  # NEW: Store manual entry flag
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            }
            
            result = self.db.mt5_accounts.insert_one(account_doc)
            
            if result.inserted_id:
                return mt5_account_data['account_id']
            
            return None
            
        except Exception as e:
            print(f"❌ Error creating MT5 account: {str(e)}")
            return None
    
    def get_client_mt5_accounts(self, client_id: str) -> List[Dict[str, Any]]:
        """Get all MT5 accounts for a specific client"""
        try:
            accounts = []
            
            account_docs = self.db.mt5_accounts.find({'client_id': client_id, 'status': 'active'})
            
            for acc in account_docs:
                account_data = {
                    'account_id': acc['account_id'],
                    'client_id': acc['client_id'],
                    'fund_code': acc['fund_code'],
                    'fund_name': f"FIDUS {acc['fund_code'].title()} Fund",
                    'mt5_login': acc['mt5_login'],
                    'mt5_server': acc['mt5_server'],
                    'total_allocated': acc['total_allocated'],
                    'current_equity': acc['current_equity'],
                    'profit_loss': acc['profit_loss'],
                    'profit_loss_percentage': (acc['profit_loss'] / acc['total_allocated'] * 100) if acc['total_allocated'] > 0 else 0,
                    'investment_count': len(acc.get('investment_ids', [])),
                    'status': acc['status'],
                    'created_at': acc['created_at'].isoformat() if hasattr(acc['created_at'], 'isoformat') else str(acc['created_at']),
                    'updated_at': acc['updated_at'].isoformat() if hasattr(acc['updated_at'], 'isoformat') else str(acc['updated_at'])
                }
                
                accounts.append(account_data)
            
            # Sort by creation date (newest first)
            accounts.sort(key=lambda x: x['created_at'], reverse=True)
            
            return accounts
            
        except Exception as e:
            print(f"❌ Error getting client MT5 accounts: {str(e)}")
            return []
    
    def update_mt5_account_allocation(self, account_id: str, additional_amount: float, investment_id: str) -> bool:
        """Add allocation to existing MT5 account"""
        try:
            result = self.db.mt5_accounts.update_one(
                {'account_id': account_id},
                {
                    '$inc': {'total_allocated': additional_amount, 'current_equity': additional_amount},
                    '$push': {'investment_ids': investment_id},
                    '$set': {'updated_at': datetime.now(timezone.utc)}
                }
            )
            
            return result.acknowledged
            
        except Exception as e:
            print(f"❌ Error updating MT5 account allocation: {str(e)}")
            return False
    
    def update_mt5_account_performance(self, account_id: str, current_equity: float) -> bool:
        """Update MT5 account performance data"""
        try:
            # Get current allocation to calculate P&L
            account = self.db.mt5_accounts.find_one({'account_id': account_id})
            if not account:
                return False
            
            profit_loss = current_equity - account['total_allocated']
            
            result = self.db.mt5_accounts.update_one(
                {'account_id': account_id},
                {
                    '$set': {
                        'current_equity': current_equity,
                        'profit_loss': profit_loss,
                        'updated_at': datetime.now(timezone.utc)
                    }
                }
            )
            
            return result.acknowledged
            
        except Exception as e:
            print(f"❌ Error updating MT5 account performance: {str(e)}")
            return False
    
    def get_all_mt5_accounts(self) -> List[Dict[str, Any]]:
        """Get all MT5 accounts for admin overview"""
        try:
            accounts = []
            
            account_docs = self.db.mt5_accounts.find({'status': 'active'})
            
            for acc in account_docs:
                # Get client name
                client = self.db.users.find_one({'user_id': acc['client_id']})
                client_profile = self.db.client_profiles.find_one({'client_id': acc['client_id']})
                
                client_name = client_profile.get('name', client['username']) if client_profile and client else acc['client_id']
                
                account_data = {
                    'account_id': acc['account_id'],
                    'client_id': acc['client_id'],
                    'client_name': client_name,
                    'fund_code': acc['fund_code'],
                    'fund_name': f"FIDUS {acc['fund_code'].title()} Fund",
                    'broker_code': acc.get('broker_code', 'unknown'),
                    'broker_name': acc.get('broker_name', 'Unknown Broker'),
                    'mt5_login': acc['mt5_login'],
                    'mt5_server': acc['mt5_server'],
                    'total_allocated': acc['total_allocated'],
                    'current_equity': acc['current_equity'],
                    'profit_loss': acc['profit_loss'],
                    'profit_loss_percentage': (acc['profit_loss'] / acc['total_allocated'] * 100) if acc['total_allocated'] > 0 else 0,
                    'investment_count': len(acc.get('investment_ids', [])),
                    'status': acc['status'],
                    'created_at': acc['created_at'].isoformat() if hasattr(acc['created_at'], 'isoformat') else str(acc['created_at']),
                    'updated_at': acc['updated_at'].isoformat() if hasattr(acc['updated_at'], 'isoformat') else str(acc['updated_at'])
                }
                
                accounts.append(account_data)
            
            return accounts
            
        except Exception as e:
            print(f"❌ Error getting all MT5 accounts: {str(e)}")
            return []
    
    def store_mt5_credentials(self, account_id: str, encrypted_password: str) -> bool:
        """Store encrypted MT5 credentials"""
        try:
            # Store encrypted password in separate collection for security
            credentials_doc = {
                'account_id': account_id,
                'encrypted_password': encrypted_password,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            }
            
            result = self.db.mt5_credentials.update_one(
                {'account_id': account_id},
                {'$set': credentials_doc},
                upsert=True
            )
            
            return result.acknowledged
            
        except Exception as e:
            print(f"❌ Error storing MT5 credentials: {str(e)}")
            return False
    
    def get_mt5_credentials(self, account_id: str) -> Optional[str]:
        """Get encrypted MT5 credentials"""
        try:
            credentials = self.db.mt5_credentials.find_one({'account_id': account_id})
            
            if credentials:
                return credentials['encrypted_password']
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting MT5 credentials: {str(e)}")
            return None

    def get_mt5_account_by_login(self, mt5_login: int) -> Optional[Dict[str, Any]]:
        """Get MT5 account by login ID to prevent duplicates"""
        try:
            account = self.db.mt5_accounts.find_one({'mt5_login': mt5_login})
            
            if account:
                # Convert ObjectId to string for JSON serialization
                account['_id'] = str(account['_id'])
                return account
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting MT5 account by login: {str(e)}")
            return None
    
    def get_mt5_account(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Get MT5 account by account ID"""
        try:
            account = self.db.mt5_accounts.find_one({'account_id': account_id})
            
            if account:
                # Convert ObjectId to string for JSON serialization
                account['_id'] = str(account['_id'])
                return account
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting MT5 account: {str(e)}")
            return None
    # ===============================================================================
    # DATABASE UTILITIES
    # ===============================================================================
    
    # ===============================================================================
    # DOCUMENT MANAGEMENT
    # ===============================================================================
    
    def create_document(self, document_data: Dict[str, Any]) -> Optional[str]:
        """Create a new document record"""
        try:
            document_doc = {
                'document_id': document_data['document_id'],
                'name': document_data['name'],
                'category': document_data['category'],
                'document_type': document_data.get('document_type', 'shared'),  # 'shared' or 'admin_only'
                'uploader_id': document_data['uploader_id'],
                'uploader_type': document_data.get('uploader_type', 'admin'),  # 'admin' or 'client'
                'client_id': document_data.get('client_id'),  # For client-specific documents
                'file_path': document_data['file_path'],
                'file_size': document_data['file_size'],
                'content_type': document_data.get('content_type'),
                'status': document_data.get('status', 'uploaded'),
                'recipient_emails': document_data.get('recipient_emails', []),
                'signature_required': document_data.get('signature_required', False),
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            }
            
            result = self.db.documents.insert_one(document_doc)
            
            if result.inserted_id:
                return document_data['document_id']
            
            return None
            
        except Exception as e:
            print(f"❌ Error creating document: {str(e)}")
            return None
    
    def get_client_documents(self, client_id: str, include_admin_shared: bool = True) -> List[Dict[str, Any]]:
        """Get documents for a specific client"""
        try:
            documents = []
            query = {'$or': []}
            
            # Include documents uploaded by the client
            query['$or'].append({'uploader_id': client_id})
            
            # Include documents assigned to this client
            query['$or'].append({'client_id': client_id})
            
            if include_admin_shared:
                # Include shared documents (not admin_only)
                query['$or'].append({
                    'document_type': 'shared',
                    'client_id': {'$in': [None, client_id]}
                })
            
            document_docs = self.db.documents.find(query)
            
            for doc in document_docs:
                document_data = {
                    'id': doc['document_id'],
                    'name': doc['name'],
                    'category': doc['category'],
                    'document_type': doc.get('document_type', 'shared'),
                    'uploader_id': doc['uploader_id'],
                    'uploader_type': doc.get('uploader_type', 'admin'),
                    'client_id': doc.get('client_id'),
                    'file_path': doc['file_path'],
                    'file_size': doc['file_size'],
                    'content_type': doc.get('content_type'),
                    'status': doc.get('status', 'uploaded'),
                    'recipient_emails': doc.get('recipient_emails', []),
                    'signature_required': doc.get('signature_required', False),
                    'created_at': doc['created_at'].isoformat(),
                    'updated_at': doc['updated_at'].isoformat()
                }
                documents.append(document_data)
            
            # Sort by creation date (newest first)
            documents.sort(key=lambda x: x['created_at'], reverse=True)
            
            return documents
            
        except Exception as e:
            print(f"❌ Error getting client documents: {str(e)}")
            return []
    
    def get_all_documents(self, include_admin_only: bool = False) -> List[Dict[str, Any]]:
        """Get all documents for admin view"""
        try:
            documents = []
            query = {}
            
            if not include_admin_only:
                # Exclude admin-only documents
                query['document_type'] = {'$ne': 'admin_only'}
            
            document_docs = self.db.documents.find(query)
            
            for doc in document_docs:
                document_data = {
                    'id': doc['document_id'],
                    'name': doc['name'],
                    'category': doc['category'],
                    'document_type': doc.get('document_type', 'shared'),
                    'uploader_id': doc['uploader_id'],
                    'uploader_type': doc.get('uploader_type', 'admin'),
                    'client_id': doc.get('client_id'),
                    'file_path': doc['file_path'],
                    'file_size': doc['file_size'],
                    'content_type': doc.get('content_type'),
                    'status': doc.get('status', 'uploaded'),
                    'recipient_emails': doc.get('recipient_emails', []),
                    'signature_required': doc.get('signature_required', False),
                    'created_at': doc['created_at'].isoformat(),
                    'updated_at': doc['updated_at'].isoformat()
                }
                documents.append(document_data)
            
            # Sort by creation date (newest first)
            documents.sort(key=lambda x: x['created_at'], reverse=True)
            
            return documents
            
        except Exception as e:
            print(f"❌ Error getting all documents: {str(e)}")
            return []
    
    def get_admin_only_documents(self) -> List[Dict[str, Any]]:
        """Get admin-only documents (compliance, internal, etc.)"""
        try:
            documents = []
            
            document_docs = self.db.documents.find({'document_type': 'admin_only'})
            
            for doc in document_docs:
                document_data = {
                    'id': doc['document_id'],
                    'name': doc['name'],
                    'category': doc['category'],
                    'document_type': doc.get('document_type', 'admin_only'),
                    'uploader_id': doc['uploader_id'],
                    'uploader_type': doc.get('uploader_type', 'admin'),
                    'client_id': doc.get('client_id'),
                    'file_path': doc['file_path'],
                    'file_size': doc['file_size'],
                    'content_type': doc.get('content_type'),
                    'status': doc.get('status', 'uploaded'),
                    'recipient_emails': doc.get('recipient_emails', []),
                    'signature_required': doc.get('signature_required', False),
                    'created_at': doc['created_at'].isoformat(),
                    'updated_at': doc['updated_at'].isoformat()
                }
                documents.append(document_data)
            
            # Sort by creation date (newest first)
            documents.sort(key=lambda x: x['created_at'], reverse=True)
            
            return documents
            
        except Exception as e:
            print(f"❌ Error getting admin-only documents: {str(e)}")
            return []

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
                          'payment_confirmations', 'crm_prospects', 'fund_rebates',
                          'mt5_accounts', 'mt5_credentials', 'documents']
            
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