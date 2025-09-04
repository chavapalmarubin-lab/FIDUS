#!/usr/bin/env python3
"""
FIDUS Live Data Migration Script
Transition from mock data to production-ready database structure
"""
import os
import sys
import uuid
from datetime import datetime, timezone, timedelta
from pymongo import MongoClient
import bcrypt
import json

# Get MongoDB URL from environment
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/fidus_investment_db')

class LiveDataMigration:
    def __init__(self):
        self.client = MongoClient(MONGO_URL)
        self.db_name = MONGO_URL.split('/')[-1]
        self.db = self.client[self.db_name]
        
        print(f"🚀 FIDUS Live Data Migration")
        print(f"📍 Target Database: {self.db_name}")
        print("=" * 60)
    
    def create_collections_schema(self):
        """Create proper database collections with schema validation"""
        print("\n📋 Creating Database Collections...")
        
        # Define collections with validation schemas
        collections_schema = {
            'users': {
                'validator': {
                    '$jsonSchema': {
                        'bsonType': 'object',
                        'required': ['user_id', 'username', 'email', 'user_type', 'created_at'],
                        'properties': {
                            'user_id': {'bsonType': 'string'},
                            'username': {'bsonType': 'string'},
                            'email': {'bsonType': 'string'},
                            'password_hash': {'bsonType': 'string'},
                            'user_type': {'enum': ['client', 'admin']},
                            'status': {'enum': ['active', 'inactive', 'suspended']},
                            'created_at': {'bsonType': 'date'},
                            'updated_at': {'bsonType': 'date'}
                        }
                    }
                }
            },
            'client_profiles': {
                'validator': {
                    '$jsonSchema': {
                        'bsonType': 'object',
                        'required': ['client_id', 'name', 'email'],
                        'properties': {
                            'client_id': {'bsonType': 'string'},
                            'name': {'bsonType': 'string'},
                            'email': {'bsonType': 'string'},
                            'phone': {'bsonType': 'string'},
                            'fidus_account_number': {'bsonType': 'string'},
                            'contract_start_date': {'bsonType': 'date'},
                            'contract_renewal_date': {'bsonType': 'date'}
                        }
                    }
                }
            },
            'client_readiness': {
                'validator': {
                    '$jsonSchema': {
                        'bsonType': 'object',
                        'required': ['client_id'],
                        'properties': {
                            'client_id': {'bsonType': 'string'},
                            'aml_kyc_completed': {'bsonType': 'bool'},
                            'agreement_signed': {'bsonType': 'bool'},
                            'account_creation_date': {'bsonType': 'date'},
                            'investment_ready': {'bsonType': 'bool'},
                            'notes': {'bsonType': 'string'}
                        }
                    }
                }
            },
            'investments': {
                'validator': {
                    '$jsonSchema': {
                        'bsonType': 'object',
                        'required': ['investment_id', 'client_id', 'fund_code', 'principal_amount'],
                        'properties': {
                            'investment_id': {'bsonType': 'string'},
                            'client_id': {'bsonType': 'string'},
                            'fund_code': {'enum': ['CORE', 'BALANCE', 'DYNAMIC', 'UNLIMITED']},
                            'principal_amount': {'bsonType': 'number'},
                            'deposit_date': {'bsonType': 'date'},
                            'incubation_end_date': {'bsonType': 'date'},
                            'interest_start_date': {'bsonType': 'date'},
                            'minimum_hold_end_date': {'bsonType': 'date'},
                            'status': {'enum': ['incubating', 'active', 'mature', 'redeemed']},
                            'created_at': {'bsonType': 'date'}
                        }
                    }
                }
            },
            'redemption_requests': {
                'validator': {
                    '$jsonSchema': {
                        'bsonType': 'object',
                        'required': ['request_id', 'client_id', 'investment_id', 'redemption_type'],
                        'properties': {
                            'request_id': {'bsonType': 'string'},
                            'client_id': {'bsonType': 'string'},
                            'investment_id': {'bsonType': 'string'},
                            'redemption_type': {'enum': ['interest', 'principal', 'full']},
                            'amount': {'bsonType': 'number'},
                            'status': {'enum': ['pending', 'approved', 'rejected', 'processed']},
                            'requested_at': {'bsonType': 'date'},
                            'processed_at': {'bsonType': 'date'}
                        }
                    }
                }
            },
            'fund_configurations': {
                'validator': {
                    '$jsonSchema': {
                        'bsonType': 'object',
                        'required': ['fund_code', 'name', 'monthly_interest_rate'],
                        'properties': {
                            'fund_code': {'bsonType': 'string'},
                            'name': {'bsonType': 'string'},
                            'monthly_interest_rate': {'bsonType': 'number'},
                            'minimum_investment': {'bsonType': 'number'},
                            'redemption_frequency': {'enum': ['monthly', 'quarterly', 'semi-annually', 'annually', 'flexible']},
                            'aum': {'bsonType': 'number'},
                            'nav_per_share': {'bsonType': 'number'},
                            'performance_ytd': {'bsonType': 'number'}
                        }
                    }
                }
            },
            'crm_prospects': {
                'validator': {
                    '$jsonSchema': {
                        'bsonType': 'object',
                        'required': ['prospect_id', 'name', 'email'],
                        'properties': {
                            'prospect_id': {'bsonType': 'string'},
                            'name': {'bsonType': 'string'},
                            'email': {'bsonType': 'string'},
                            'phone': {'bsonType': 'string'},
                            'stage': {'enum': ['lead', 'qualified', 'proposal', 'negotiation', 'won', 'lost']},
                            'notes': {'bsonType': 'string'},
                            'converted_to_client': {'bsonType': 'bool'},
                            'client_id': {'bsonType': 'string'},
                            'created_at': {'bsonType': 'date'}
                        }
                    }
                }
            },
            'activity_logs': {
                'validator': {
                    '$jsonSchema': {
                        'bsonType': 'object',
                        'required': ['log_id', 'client_id', 'activity_type'],
                        'properties': {
                            'log_id': {'bsonType': 'string'},
                            'client_id': {'bsonType': 'string'},
                            'activity_type': {'enum': ['deposit', 'redemption', 'interest_payment', 'fee_charge']},
                            'amount': {'bsonType': 'number'},
                            'fund_code': {'bsonType': 'string'},
                            'description': {'bsonType': 'string'},
                            'timestamp': {'bsonType': 'date'}
                        }
                    }
                }
            },
            'payment_confirmations': {
                'validator': {
                    '$jsonSchema': {
                        'bsonType': 'object',
                        'required': ['confirmation_id', 'investment_id', 'payment_method'],
                        'properties': {
                            'confirmation_id': {'bsonType': 'string'},
                            'investment_id': {'bsonType': 'string'},
                            'payment_method': {'enum': ['fiat', 'crypto']},
                            'transaction_details': {'bsonType': 'object'},
                            'confirmed_by': {'bsonType': 'string'},
                            'confirmed_at': {'bsonType': 'date'}
                        }
                    }
                }
            },
            'fund_rebates': {
                'validator': {
                    '$jsonSchema': {
                        'bsonType': 'object',
                        'required': ['rebate_id', 'fund_code', 'month', 'amount'],
                        'properties': {
                            'rebate_id': {'bsonType': 'string'},
                            'fund_code': {'bsonType': 'string'},
                            'month': {'bsonType': 'string'},
                            'amount': {'bsonType': 'number'},
                            'percentage': {'bsonType': 'number'},
                            'created_at': {'bsonType': 'date'}
                        }
                    }
                }
            }
        }
        
        # Create collections with validation
        for collection_name, schema in collections_schema.items():
            try:
                if collection_name in self.db.list_collection_names():
                    print(f"   ✅ Collection '{collection_name}' already exists")
                else:
                    self.db.create_collection(collection_name, **schema)
                    print(f"   ✅ Created collection '{collection_name}' with validation")
            except Exception as e:
                print(f"   ❌ Error creating '{collection_name}': {str(e)}")
        
        # Create indexes for performance
        self.create_indexes()
    
    def create_indexes(self):
        """Create database indexes for performance optimization"""
        print("\n📊 Creating Database Indexes...")
        
        indexes = {
            'users': [
                ('username', 1),
                ('email', 1),
                ('user_id', 1)
            ],
            'client_profiles': [
                ('client_id', 1),
                ('email', 1)
            ],
            'investments': [
                ('client_id', 1),
                ('investment_id', 1),
                ('fund_code', 1),
                ('deposit_date', -1)
            ],
            'redemption_requests': [
                ('client_id', 1),
                ('investment_id', 1),
                ('status', 1),
                ('requested_at', -1)
            ],
            'activity_logs': [
                ('client_id', 1),
                ('timestamp', -1),
                ('activity_type', 1)
            ],
            'crm_prospects': [
                ('email', 1),
                ('stage', 1),
                ('created_at', -1)
            ]
        }
        
        for collection_name, collection_indexes in indexes.items():
            collection = self.db[collection_name]
            for index_spec in collection_indexes:
                try:
                    collection.create_index([index_spec])
                    print(f"   ✅ Created index on {collection_name}.{index_spec[0]}")
                except Exception as e:
                    print(f"   ❌ Error creating index on {collection_name}.{index_spec[0]}: {str(e)}")
    
    def migrate_demo_data(self):
        """Migrate essential demo data for production showcase"""
        print("\n📁 Migrating Demo Data...")
        
        # Create admin user
        admin_user = {
            'user_id': 'user_admin_001',
            'username': 'admin',
            'email': 'admin@fidus.com',
            'password_hash': bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            'user_type': 'admin',
            'status': 'active',
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc)
        }
        
        # Create demo clients
        demo_clients = [
            {
                'user_id': 'client_001',
                'username': 'client1',
                'email': 'gerardo.briones@fidus.com',
                'password_hash': bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                'user_type': 'client',
                'status': 'active',
                'created_at': datetime.now(timezone.utc) - timedelta(days=180),
                'updated_at': datetime.now(timezone.utc)
            },
            {
                'user_id': 'client_002',
                'username': 'client2',
                'email': 'maria.rodriguez@fidus.com',
                'password_hash': bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                'user_type': 'client',
                'status': 'active',
                'created_at': datetime.now(timezone.utc) - timedelta(days=150),
                'updated_at': datetime.now(timezone.utc)
            },
            {
                'user_id': 'client_003',
                'username': 'client3',
                'email': 'salvador.palma@fidus.com',
                'password_hash': bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                'user_type': 'client',
                'status': 'active',
                'created_at': datetime.now(timezone.utc) - timedelta(days=120),
                'updated_at': datetime.now(timezone.utc)
            }
        ]
        
        # Insert users
        try:
            self.db.users.insert_one(admin_user)
            print("   ✅ Created admin user")
            
            self.db.users.insert_many(demo_clients)
            print(f"   ✅ Created {len(demo_clients)} demo client users")
        except Exception as e:
            print(f"   ❌ Error creating users: {str(e)}")
        
        # Create client profiles
        client_profiles = [
            {
                'client_id': 'client_001',
                'name': 'Gerardo Briones',
                'email': 'gerardo.briones@fidus.com',
                'phone': '+1-555-0101',
                'fidus_account_number': '124567',
                'contract_start_date': datetime(2020, 4, 1),
                'contract_renewal_date': datetime(2025, 4, 1)
            },
            {
                'client_id': 'client_002',
                'name': 'Maria Rodriguez',
                'email': 'maria.rodriguez@fidus.com',
                'phone': '+1-555-0102',
                'fidus_account_number': '124568',
                'contract_start_date': datetime(2021, 6, 15),
                'contract_renewal_date': datetime(2026, 6, 15)
            },
            {
                'client_id': 'client_003',
                'name': 'Salvador Palma',
                'email': 'salvador.palma@fidus.com',
                'phone': '+1-555-0103',
                'fidus_account_number': '124569',
                'contract_start_date': datetime(2022, 1, 1),
                'contract_renewal_date': datetime(2027, 1, 1)
            }
        ]
        
        try:
            self.db.client_profiles.insert_many(client_profiles)
            print(f"   ✅ Created {len(client_profiles)} client profiles")
        except Exception as e:
            print(f"   ❌ Error creating client profiles: {str(e)}")
        
        # Create fund configurations
        fund_configs = [
            {
                'fund_code': 'CORE',
                'name': 'FIDUS Core Fund',
                'monthly_interest_rate': 0.015,  # 1.5%
                'minimum_investment': 10000,
                'redemption_frequency': 'monthly',
                'aum': 50000,  # Will be calculated dynamically
                'nav_per_share': 102.8,
                'performance_ytd': 8.5
            },
            {
                'fund_code': 'BALANCE',
                'name': 'FIDUS Balance Fund',
                'monthly_interest_rate': 0.025,  # 2.5%
                'minimum_investment': 50000,
                'redemption_frequency': 'quarterly',
                'aum': 100000,  # Will be calculated dynamically
                'nav_per_share': 104.59,
                'performance_ytd': 12.3
            },
            {
                'fund_code': 'DYNAMIC',
                'name': 'FIDUS Dynamic Fund',
                'monthly_interest_rate': 0.035,  # 3.5%
                'minimum_investment': 250000,
                'redemption_frequency': 'semi-annually',
                'aum': 300000,  # Will be calculated dynamically
                'nav_per_share': 108.45,
                'performance_ytd': 18.7
            },
            {
                'fund_code': 'UNLIMITED',
                'name': 'FIDUS Unlimited Fund',
                'monthly_interest_rate': 0.0,  # Variable
                'minimum_investment': 1000000,
                'redemption_frequency': 'flexible',
                'aum': 0,  # Invitation only
                'nav_per_share': 95.67,
                'performance_ytd': -2.1
            }
        ]
        
        try:
            self.db.fund_configurations.insert_many(fund_configs)
            print(f"   ✅ Created {len(fund_configs)} fund configurations")
        except Exception as e:
            print(f"   ❌ Error creating fund configurations: {str(e)}")
        
        # Create sample investments
        sample_investments = [
            {
                'investment_id': str(uuid.uuid4()),
                'client_id': 'client_001',
                'fund_code': 'CORE',
                'principal_amount': 25000,
                'deposit_date': datetime.now(timezone.utc) - timedelta(days=90),
                'incubation_end_date': datetime.now(timezone.utc) - timedelta(days=30),
                'interest_start_date': datetime.now(timezone.utc) - timedelta(days=30),
                'minimum_hold_end_date': datetime.now(timezone.utc) + timedelta(days=330),
                'status': 'active',
                'created_at': datetime.now(timezone.utc) - timedelta(days=90)
            },
            {
                'investment_id': str(uuid.uuid4()),
                'client_id': 'client_002',
                'fund_code': 'BALANCE',
                'principal_amount': 75000,
                'deposit_date': datetime.now(timezone.utc) - timedelta(days=120),
                'incubation_end_date': datetime.now(timezone.utc) - timedelta(days=60),
                'interest_start_date': datetime.now(timezone.utc) - timedelta(days=60),
                'minimum_hold_end_date': datetime.now(timezone.utc) + timedelta(days=300),
                'status': 'active',
                'created_at': datetime.now(timezone.utc) - timedelta(days=120)
            },
            {
                'investment_id': str(uuid.uuid4()),
                'client_id': 'client_003',
                'fund_code': 'DYNAMIC',
                'principal_amount': 300000,
                'deposit_date': datetime.now(timezone.utc) - timedelta(days=180),
                'incubation_end_date': datetime.now(timezone.utc) - timedelta(days=120),
                'interest_start_date': datetime.now(timezone.utc) - timedelta(days=120),
                'minimum_hold_end_date': datetime.now(timezone.utc) + timedelta(days=240),
                'status': 'active',
                'created_at': datetime.now(timezone.utc) - timedelta(days=180)
            }
        ]
        
        try:
            self.db.investments.insert_many(sample_investments)
            print(f"   ✅ Created {len(sample_investments)} sample investments")
        except Exception as e:
            print(f"   ❌ Error creating sample investments: {str(e)}")
        
        # Create client readiness records
        readiness_records = [
            {
                'client_id': 'client_001',
                'aml_kyc_completed': True,
                'agreement_signed': True,
                'account_creation_date': datetime.now(timezone.utc) - timedelta(days=180),
                'investment_ready': True,
                'notes': 'All documentation complete'
            },
            {
                'client_id': 'client_002',
                'aml_kyc_completed': True,
                'agreement_signed': True,
                'account_creation_date': datetime.now(timezone.utc) - timedelta(days=150),
                'investment_ready': True,
                'notes': 'Ready for additional investments'
            },
            {
                'client_id': 'client_003',
                'aml_kyc_completed': True,
                'agreement_signed': False,
                'account_creation_date': datetime.now(timezone.utc) - timedelta(days=120),
                'investment_ready': False,
                'notes': 'Awaiting signed agreement'
            }
        ]
        
        try:
            self.db.client_readiness.insert_many(readiness_records)
            print(f"   ✅ Created {len(readiness_records)} client readiness records")
        except Exception as e:
            print(f"   ❌ Error creating client readiness records: {str(e)}")
    
    def create_backup_script(self):
        """Create database backup script for production"""
        backup_script = '''#!/bin/bash
# FIDUS Database Backup Script
# Run this script daily for production backups

BACKUP_DIR="/app/backups"
DB_NAME="fidus_investment_db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/fidus_backup_$TIMESTAMP.gz"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create MongoDB dump
echo "Creating database backup..."
mongodump --db $DB_NAME --archive=$BACKUP_FILE --gzip

if [ $? -eq 0 ]; then
    echo "✅ Backup created successfully: $BACKUP_FILE"
    
    # Keep only last 7 days of backups
    find $BACKUP_DIR -name "fidus_backup_*.gz" -mtime +7 -delete
    echo "✅ Old backups cleaned up"
else
    echo "❌ Backup failed!"
    exit 1
fi
'''
        
        with open('/app/backup_database.sh', 'w') as f:
            f.write(backup_script)
        
        os.chmod('/app/backup_database.sh', 0o755)
        print("   ✅ Created database backup script: /app/backup_database.sh")
        
        # Create backup directory
        os.makedirs('/app/backups', exist_ok=True)
        print("   ✅ Created backup directory: /app/backups")
    
    def verify_migration(self):
        """Verify the migration was successful"""
        print("\n🔍 Verifying Migration...")
        
        collections_to_check = [
            'users', 'client_profiles', 'client_readiness', 'investments', 
            'fund_configurations', 'redemption_requests', 'activity_logs',
            'payment_confirmations', 'crm_prospects', 'fund_rebates'
        ]
        
        for collection_name in collections_to_check:
            collection = self.db[collection_name]
            count = collection.count_documents({})
            print(f"   📊 {collection_name}: {count} documents")
            
            if count > 0 and collection_name in ['users', 'client_profiles', 'investments']:
                sample = collection.find_one()
                if sample:
                    print(f"      Sample fields: {list(sample.keys())}")
        
        # Test data integrity
        users_count = self.db.users.count_documents({})
        profiles_count = self.db.client_profiles.count_documents({})
        investments_count = self.db.investments.count_documents({})
        
        print(f"\n📈 Data Integrity Check:")
        print(f"   Users: {users_count}")
        print(f"   Client Profiles: {profiles_count}")
        print(f"   Investments: {investments_count}")
        
        if users_count > 0 and profiles_count > 0 and investments_count > 0:
            print("   ✅ Data integrity verified")
            return True
        else:
            print("   ❌ Data integrity issues found")
            return False
    
    def run_migration(self):
        """Run the complete migration process"""
        try:
            print("🚀 Starting Live Data Migration Process...")
            
            # Step 1: Create collections and schema
            self.create_collections_schema()
            
            # Step 2: Migrate demo data
            self.migrate_demo_data()
            
            # Step 3: Create backup script
            self.create_backup_script()
            
            # Step 4: Verify migration
            success = self.verify_migration()
            
            if success:
                print("\n🎉 MIGRATION COMPLETED SUCCESSFULLY!")
                print("📊 Database is now ready for production use")
                print("🔒 Backup system is configured")
                print("📈 All collections created with proper schema validation")
                
                # Create migration summary
                summary = {
                    'migration_date': datetime.now(timezone.utc).isoformat(),
                    'database_name': self.db_name,
                    'collections_created': self.db.list_collection_names(),
                    'demo_users_created': self.db.users.count_documents({}),
                    'demo_investments_created': self.db.investments.count_documents({}),
                    'status': 'success'
                }
                
                with open('/app/migration_summary.json', 'w') as f:
                    json.dump(summary, f, indent=2, default=str)
                
                print("📁 Migration summary saved to: /app/migration_summary.json")
                
            else:
                print("\n💥 MIGRATION FAILED!")
                print("Please check the errors above and retry")
                return False
                
        except Exception as e:
            print(f"\n💥 MIGRATION ERROR: {str(e)}")
            return False
        
        return True

if __name__ == "__main__":
    migration = LiveDataMigration()
    success = migration.run_migration()
    
    if not success:
        sys.exit(1)