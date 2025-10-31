#!/usr/bin/env python3
"""
Data Validation and Migration Script
Validates and cleans existing FIDUS database data to match new schemas
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.database import connection_manager
from repositories.user_repository import UserRepository
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataValidator:
    """Validates and migrates existing database data"""
    
    def __init__(self):
        self.db = None
        self.migration_report = {
            'users': {'validated': 0, 'migrated': 0, 'errors': []},
            'investments': {'validated': 0, 'migrated': 0, 'errors': []},
            'crm_prospects': {'validated': 0, 'migrated': 0, 'errors': []},
            'summary': {'total_issues': 0, 'total_fixes': 0}
        }
    
    async def initialize(self):
        """Initialize database connection"""
        self.db = await connection_manager.get_database()
    
    async def validate_users_collection(self):
        """Validate and migrate users collection"""
        
        print("👥 VALIDATING USERS COLLECTION")
        print("=" * 40)
        
        try:
            users = await self.db.users.find({}).to_list(length=None)
            print(f"Found {len(users)} users to validate")
            
            for user in users:
                user_id = str(user.get('_id', 'unknown'))
                issues = []
                fixes = {}
                
                # Check required fields
                if not user.get('username'):
                    issues.append("Missing username")
                elif not isinstance(user['username'], str):
                    issues.append("Invalid username type")
                
                if not user.get('email'):
                    issues.append("Missing email")
                elif not isinstance(user['email'], str) or '@' not in user['email']:
                    issues.append("Invalid email format")
                
                # Fix legacy field mapping
                if 'type' in user and 'user_type' not in user:
                    fixes['user_type'] = user['type']
                    issues.append("Legacy 'type' field needs migration to 'user_type'")
                
                # Add missing fields with defaults
                if 'is_active' not in user:
                    fixes['is_active'] = True
                    issues.append("Missing 'is_active' field")
                
                if 'is_verified' not in user:
                    fixes['is_verified'] = False
                    issues.append("Missing 'is_verified' field")
                
                if 'kyc_status' not in user:
                    fixes['kyc_status'] = 'pending'
                    issues.append("Missing 'kyc_status' field")
                
                if 'aml_status' not in user:
                    fixes['aml_status'] = 'pending'
                    issues.append("Missing 'aml_status' field")
                
                if 'login_attempts' not in user:
                    fixes['login_attempts'] = 0
                    issues.append("Missing 'login_attempts' field")
                
                if 'created_at' not in user:
                    fixes['created_at'] = datetime.now(timezone.utc)
                    issues.append("Missing 'created_at' field")
                
                if 'updated_at' not in user:
                    fixes['updated_at'] = datetime.now(timezone.utc)
                    issues.append("Missing 'updated_at' field")
                
                # Report findings
                username = user.get('username', 'unknown')
                self.migration_report['users']['validated'] += 1
                
                if issues:
                    print(f"   🔧 User {username} ({user_id}): {len(issues)} issues")
                    for issue in issues:
                        print(f"      - {issue}")
                    
                    # Apply fixes
                    if fixes:
                        try:
                            await self.db.users.update_one(
                                {'_id': user['_id']},
                                {'$set': fixes}
                            )
                            self.migration_report['users']['migrated'] += 1
                            print(f"      ✅ Applied {len(fixes)} fixes")
                        except Exception as e:
                            error_msg = f"Failed to update user {username}: {e}"
                            self.migration_report['users']['errors'].append(error_msg)
                            print(f"      ❌ {error_msg}")
                else:
                    print(f"   ✅ User {username}: No issues found")
            
            print(f"\n📊 Users validation summary:")
            print(f"   Validated: {self.migration_report['users']['validated']}")
            print(f"   Migrated: {self.migration_report['users']['migrated']}")
            print(f"   Errors: {len(self.migration_report['users']['errors'])}")
            
        except Exception as e:
            logger.error(f"Error validating users collection: {e}")
    
    async def validate_investments_collection(self):
        """Validate investments collection"""
        
        print(f"\n💼 VALIDATING INVESTMENTS COLLECTION")
        print("=" * 40)
        
        try:
            investments = await self.db.investments.find({}).to_list(length=None)
            print(f"Found {len(investments)} investments to validate")
            
            if len(investments) == 0:
                print("   ✅ No investments found - clean state")
                return
            
            for investment in investments:
                investment_id = investment.get('investment_id', str(investment.get('_id', 'unknown')))
                issues = []
                fixes = {}
                
                # Check required fields
                if not investment.get('client_id'):
                    issues.append("Missing client_id")
                
                if not investment.get('fund_code'):
                    issues.append("Missing fund_code")
                elif investment['fund_code'] not in ['CORE', 'BALANCE', 'DYNAMIC', 'UNLIMITED']:
                    issues.append(f"Invalid fund_code: {investment['fund_code']}")
                
                if not investment.get('principal_amount'):
                    issues.append("Missing principal_amount")
                elif not isinstance(investment['principal_amount'], (int, float)) or investment['principal_amount'] <= 0:
                    issues.append("Invalid principal_amount")
                
                # Add missing fields
                if 'currency' not in investment:
                    fixes['currency'] = 'USD'
                    issues.append("Missing 'currency' field")
                
                if 'status' not in investment:
                    fixes['status'] = 'active'
                    issues.append("Missing 'status' field")
                
                if 'created_at' not in investment:
                    fixes['created_at'] = datetime.now(timezone.utc)
                    issues.append("Missing 'created_at' field")
                
                if 'updated_at' not in investment:
                    fixes['updated_at'] = datetime.now(timezone.utc)
                    issues.append("Missing 'updated_at' field")
                
                # Report findings
                self.migration_report['investments']['validated'] += 1
                
                if issues:
                    print(f"   🔧 Investment {investment_id}: {len(issues)} issues")
                    for issue in issues:
                        print(f"      - {issue}")
                    
                    # Apply fixes
                    if fixes:
                        try:
                            await self.db.investments.update_one(
                                {'_id': investment['_id']},
                                {'$set': fixes}
                            )
                            self.migration_report['investments']['migrated'] += 1
                            print(f"      ✅ Applied {len(fixes)} fixes")
                        except Exception as e:
                            error_msg = f"Failed to update investment {investment_id}: {e}"
                            self.migration_report['investments']['errors'].append(error_msg)
                            print(f"      ❌ {error_msg}")
                else:
                    print(f"   ✅ Investment {investment_id}: No issues found")
            
            print(f"\n📊 Investments validation summary:")
            print(f"   Validated: {self.migration_report['investments']['validated']}")
            print(f"   Migrated: {self.migration_report['investments']['migrated']}")
            print(f"   Errors: {len(self.migration_report['investments']['errors'])}")
            
        except Exception as e:
            logger.error(f"Error validating investments collection: {e}")
    
    async def validate_crm_prospects_collection(self):
        """Validate CRM prospects collection"""
        
        print(f"\n🎯 VALIDATING CRM PROSPECTS COLLECTION")
        print("=" * 40)
        
        try:
            prospects = await self.db.crm_prospects.find({}).to_list(length=None)
            print(f"Found {len(prospects)} CRM prospects to validate")
            
            if len(prospects) == 0:
                print("   ✅ No CRM prospects found")
                return
            
            for prospect in prospects:
                prospect_id = str(prospect.get('_id', 'unknown'))
                issues = []
                fixes = {}
                
                # Check required fields
                if not prospect.get('name'):
                    issues.append("Missing name")
                
                if not prospect.get('email'):
                    issues.append("Missing email")
                elif '@' not in prospect['email']:
                    issues.append("Invalid email format")
                
                # Add missing fields
                if 'stage' not in prospect:
                    fixes['stage'] = 'lead'
                    issues.append("Missing 'stage' field")
                
                if 'created_at' not in prospect:
                    fixes['created_at'] = datetime.now(timezone.utc)
                    issues.append("Missing 'created_at' field")
                
                if 'updated_at' not in prospect:
                    fixes['updated_at'] = datetime.now(timezone.utc)
                    issues.append("Missing 'updated_at' field")
                
                # Report findings
                name = prospect.get('name', 'unknown')
                self.migration_report['crm_prospects']['validated'] += 1
                
                if issues:
                    print(f"   🔧 Prospect {name} ({prospect_id}): {len(issues)} issues")
                    for issue in issues:
                        print(f"      - {issue}")
                    
                    # Apply fixes
                    if fixes:
                        try:
                            await self.db.crm_prospects.update_one(
                                {'_id': prospect['_id']},
                                {'$set': fixes}
                            )
                            self.migration_report['crm_prospects']['migrated'] += 1
                            print(f"      ✅ Applied {len(fixes)} fixes")
                        except Exception as e:
                            error_msg = f"Failed to update prospect {name}: {e}"
                            self.migration_report['crm_prospects']['errors'].append(error_msg)
                            print(f"      ❌ {error_msg}")
                else:
                    print(f"   ✅ Prospect {name}: No issues found")
            
            print(f"\n📊 CRM prospects validation summary:")
            print(f"   Validated: {self.migration_report['crm_prospects']['validated']}")
            print(f"   Migrated: {self.migration_report['crm_prospects']['migrated']}")
            print(f"   Errors: {len(self.migration_report['crm_prospects']['errors'])}")
            
        except Exception as e:
            logger.error(f"Error validating crm_prospects collection: {e}")
    
    async def check_data_integrity(self):
        """Check data integrity and relationships"""
        
        print(f"\n🔍 DATA INTEGRITY CHECKS")
        print("=" * 30)
        
        try:
            # Check for duplicate users
            duplicate_emails = await self.db.users.aggregate([
                {'$group': {'_id': '$email', 'count': {'$sum': 1}}},
                {'$match': {'count': {'$gt': 1}}}
            ]).to_list(length=None)
            
            if duplicate_emails:
                print(f"   ⚠️  Found {len(duplicate_emails)} duplicate email addresses:")
                for dup in duplicate_emails:
                    print(f"      - {dup['_id']}: {dup['count']} users")
            else:
                print(f"   ✅ No duplicate email addresses found")
            
            # Check for duplicate usernames
            duplicate_usernames = await self.db.users.aggregate([
                {'$group': {'_id': '$username', 'count': {'$sum': 1}}},
                {'$match': {'count': {'$gt': 1}}}
            ]).to_list(length=None)
            
            if duplicate_usernames:
                print(f"   ⚠️  Found {len(duplicate_usernames)} duplicate usernames:")
                for dup in duplicate_usernames:
                    print(f"      - {dup['_id']}: {dup['count']} users")
            else:
                print(f"   ✅ No duplicate usernames found")
            
            # Check investment-user relationships
            investments = await self.db.investments.find({}).to_list(length=None)
            if investments:
                orphaned_investments = 0
                for investment in investments:
                    client_id = investment.get('client_id')
                    if client_id:
                        user_exists = await self.db.users.count_documents({'$or': [
                            {'_id': client_id},
                            {'user_id': client_id}
                        ]})
                        if not user_exists:
                            orphaned_investments += 1
                
                if orphaned_investments > 0:
                    print(f"   ⚠️  Found {orphaned_investments} orphaned investments (no matching user)")
                else:
                    print(f"   ✅ All investments have valid user references")
            
        except Exception as e:
            logger.error(f"Error checking data integrity: {e}")
    
    async def generate_final_report(self):
        """Generate final migration report"""
        
        print(f"\n📋 FINAL VALIDATION REPORT")
        print("=" * 40)
        
        total_validated = sum(collection['validated'] for collection in self.migration_report.values() if isinstance(collection, dict) and 'validated' in collection)
        total_migrated = sum(collection['migrated'] for collection in self.migration_report.values() if isinstance(collection, dict) and 'migrated' in collection)
        total_errors = sum(len(collection['errors']) for collection in self.migration_report.values() if isinstance(collection, dict) and 'errors' in collection)
        
        print(f"📊 Overall Statistics:")
        print(f"   Total documents validated: {total_validated}")
        print(f"   Total documents migrated: {total_migrated}")
        print(f"   Total errors: {total_errors}")
        
        print(f"\n📋 By Collection:")
        for collection_name, stats in self.migration_report.items():
            if isinstance(stats, dict) and 'validated' in stats:
                print(f"   {collection_name}:")
                print(f"     Validated: {stats['validated']}")
                print(f"     Migrated: {stats['migrated']}")
                print(f"     Errors: {len(stats['errors'])}")
                
                if stats['errors']:
                    print(f"     Error details:")
                    for error in stats['errors'][:3]:  # Show first 3 errors
                        print(f"       - {error}")
                    if len(stats['errors']) > 3:
                        print(f"       ... and {len(stats['errors']) - 3} more errors")
        
        if total_errors == 0:
            print(f"\n🎉 DATA VALIDATION SUCCESSFUL!")
            print(f"✅ All data is now compatible with new schema")
            print(f"✅ Database is ready for production use")
        else:
            print(f"\n⚠️  DATA VALIDATION COMPLETED WITH ERRORS")
            print(f"📝 Review error details above")
            print(f"🔧 Manual intervention may be required")

async def main():
    """Main validation execution"""
    
    print("🔍 FIDUS DATABASE DATA VALIDATION")
    print("=" * 60)
    print("Validating existing data against new Phase 2 schemas")
    print("Migrating legacy field names and adding missing fields")
    print("=" * 60)
    
    validator = DataValidator()
    
    try:
        await validator.initialize()
        print("✅ Database connection established")
        
        # Validate all collections
        await validator.validate_users_collection()
        await validator.validate_investments_collection()
        await validator.validate_crm_prospects_collection()
        
        # Check data integrity
        await validator.check_data_integrity()
        
        # Generate final report
        await validator.generate_final_report()
        
    except Exception as e:
        logger.error(f"Data validation failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await connection_manager.close_connection()

if __name__ == "__main__":
    asyncio.run(main())