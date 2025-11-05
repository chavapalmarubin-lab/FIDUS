#!/usr/bin/env python3
"""
Phase 2: Database Migration Script
Safely execute all priority migrations with verification

Usage:
    python run_phase2_migration.py --dry-run    # Show what would be done
    python run_phase2_migration.py --execute    # Execute migrations
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

# Load environment variables
backend_env = Path(__file__).parent / "backend" / ".env"
if backend_env.exists():
    load_dotenv(backend_env)

class MigrationRunner:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.mongo_url = os.environ.get('MONGO_URL')
        self.client = None
        self.db = None
        self.migration_log = []
        
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.mongo_url, serverSelectionTimeoutMS=5000)
            self.db = self.client.get_default_database()
            self.client.admin.command('ping')
            self.log(f"✅ Connected to MongoDB: {self.db.name}")
            return True
        except Exception as e:
            self.log(f"❌ Connection failed: {str(e)}")
            return False
    
    def log(self, message):
        """Log message to console and internal log"""
        print(message)
        self.migration_log.append(f"[{datetime.now().isoformat()}] {message}")
    
    def save_backup_metadata(self):
        """Save backup metadata for rollback"""
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "database": self.db.name,
            "collections": {
                "mt5_accounts": self.db.mt5_accounts.count_documents({}),
                "money_managers": self.db.money_managers.count_documents({}),
                "investments": self.db.investments.count_documents({}),
                "clients": self.db.clients.count_documents({}),
                "salespeople": self.db.salespeople.count_documents({}),
                "referral_commissions": self.db.referral_commissions.count_documents({})
            }
        }
        self.log(f"📊 Pre-migration counts: {metadata['collections']}")
        return metadata
    
    def verify_no_data_loss(self, pre_counts):
        """Verify document counts match pre-migration"""
        self.log("\n🔍 Verifying no data loss...")
        
        collections = ["mt5_accounts", "money_managers", "investments", "clients", "salespeople", "referral_commissions"]
        all_good = True
        
        for collection in collections:
            pre = pre_counts[collection]
            post = self.db[collection].count_documents({})
            
            if pre == post:
                self.log(f"  ✅ {collection}: {post} docs (no loss)")
            else:
                self.log(f"  ❌ {collection}: {pre} → {post} docs (MISMATCH!)")
                all_good = False
        
        return all_good
    
    def migration_1_remove_manager_name_fields(self):
        """Priority 1: Remove duplicate manager_name fields"""
        self.log("\n" + "="*60)
        self.log("MIGRATION 1: Remove duplicate manager_name fields")
        self.log("="*60)
        
        # Check mt5_accounts
        mt5_count = self.db.mt5_accounts.count_documents({"manager_name": {"$exists": True}})
        self.log(f"📊 Found {mt5_count} mt5_accounts with manager_name field")
        
        # Check money_managers
        mm_count = self.db.money_managers.count_documents({"manager_name": {"$exists": True}})
        self.log(f"📊 Found {mm_count} money_managers with manager_name field")
        
        if mt5_count == 0 and mm_count == 0:
            self.log("✅ No manager_name fields found - migration not needed")
            return True
        
        if self.dry_run:
            self.log("🔍 DRY RUN - Would remove manager_name fields")
            return True
        
        # Execute migration
        try:
            # Remove from mt5_accounts
            if mt5_count > 0:
                result = self.db.mt5_accounts.update_many(
                    {},
                    {"$unset": {"manager_name": ""}}
                )
                self.log(f"✅ Removed manager_name from {result.modified_count} mt5_accounts")
            
            # Remove from money_managers
            if mm_count > 0:
                result = self.db.money_managers.update_many(
                    {},
                    {"$unset": {"manager_name": ""}}
                )
                self.log(f"✅ Removed manager_name from {result.modified_count} money_managers")
            
            # Verify
            mt5_remaining = self.db.mt5_accounts.count_documents({"manager_name": {"$exists": True}})
            mm_remaining = self.db.money_managers.count_documents({"manager_name": {"$exists": True}})
            
            if mt5_remaining == 0 and mm_remaining == 0:
                self.log("✅ Migration 1 completed successfully")
                return True
            else:
                self.log(f"❌ Migration 1 incomplete: {mt5_remaining + mm_remaining} fields remain")
                return False
                
        except Exception as e:
            self.log(f"❌ Migration 1 failed: {str(e)}")
            return False
    
    def migration_2_remove_investment_amount_fields(self):
        """Priority 2: Remove duplicate amount fields from investments"""
        self.log("\n" + "="*60)
        self.log("MIGRATION 2: Remove duplicate amount, investment_date, referred_by fields")
        self.log("="*60)
        
        # Check counts
        amount_count = self.db.investments.count_documents({"amount": {"$exists": True}})
        investment_date_count = self.db.investments.count_documents({"investment_date": {"$exists": True}})
        referred_by_count = self.db.investments.count_documents({"referred_by": {"$exists": True}})
        
        self.log(f"📊 Found {amount_count} investments with 'amount' field")
        self.log(f"📊 Found {investment_date_count} investments with 'investment_date' field")
        self.log(f"📊 Found {referred_by_count} investments with 'referred_by' field")
        
        if amount_count == 0 and investment_date_count == 0 and referred_by_count == 0:
            self.log("✅ No deprecated fields found - migration not needed")
            return True
        
        if self.dry_run:
            self.log("🔍 DRY RUN - Would remove deprecated fields")
            return True
        
        # Execute migration
        try:
            # First, ensure principal_amount exists for all records with amount
            if amount_count > 0:
                # Copy amount to principal_amount if missing
                result = self.db.investments.update_many(
                    {
                        "principal_amount": {"$exists": False},
                        "amount": {"$exists": True}
                    },
                    [{"$set": {"principal_amount": "$amount"}}]
                )
                if result.modified_count > 0:
                    self.log(f"✅ Copied amount to principal_amount for {result.modified_count} investments")
            
            # Now remove deprecated fields
            result = self.db.investments.update_many(
                {},
                {
                    "$unset": {
                        "amount": "",
                        "investment_date": "",
                        "referred_by": ""
                    }
                }
            )
            self.log(f"✅ Removed deprecated fields from {result.modified_count} investments")
            
            # Verify
            remaining = self.db.investments.count_documents({
                "$or": [
                    {"amount": {"$exists": True}},
                    {"investment_date": {"$exists": True}},
                    {"referred_by": {"$exists": True}}
                ]
            })
            
            if remaining == 0:
                self.log("✅ Migration 2 completed successfully")
                return True
            else:
                self.log(f"❌ Migration 2 incomplete: {remaining} fields remain")
                return False
                
        except Exception as e:
            self.log(f"❌ Migration 2 failed: {str(e)}")
            return False
    
    def migration_3_remove_last_sync_fields(self):
        """Priority 3: Remove deprecated last_sync fields"""
        self.log("\n" + "="*60)
        self.log("MIGRATION 3: Remove deprecated last_sync field")
        self.log("="*60)
        
        # Check count
        count = self.db.mt5_accounts.count_documents({"last_sync": {"$exists": True}})
        self.log(f"📊 Found {count} mt5_accounts with 'last_sync' field")
        
        if count == 0:
            self.log("✅ No last_sync fields found - migration not needed")
            return True
        
        if self.dry_run:
            self.log("🔍 DRY RUN - Would remove last_sync fields")
            return True
        
        # Execute migration
        try:
            result = self.db.mt5_accounts.update_many(
                {},
                {"$unset": {"last_sync": ""}}
            )
            self.log(f"✅ Removed last_sync from {result.modified_count} mt5_accounts")
            
            # Verify
            remaining = self.db.mt5_accounts.count_documents({"last_sync": {"$exists": True}})
            
            if remaining == 0:
                self.log("✅ Migration 3 completed successfully")
                return True
            else:
                self.log(f"❌ Migration 3 incomplete: {remaining} fields remain")
                return False
                
        except Exception as e:
            self.log(f"❌ Migration 3 failed: {str(e)}")
            return False
    
    def run_all_migrations(self):
        """Run all migrations in sequence"""
        self.log("\n" + "="*60)
        self.log("PHASE 2: DATABASE MIGRATION")
        self.log("="*60)
        self.log(f"Mode: {'DRY RUN' if self.dry_run else 'EXECUTE'}")
        self.log(f"Database: {self.db.name}")
        
        # Save pre-migration state
        pre_counts = self.save_backup_metadata()
        
        # Run migrations
        migrations = [
            ("Migration 1", self.migration_1_remove_manager_name_fields),
            ("Migration 2", self.migration_2_remove_investment_amount_fields),
            ("Migration 3", self.migration_3_remove_last_sync_fields)
        ]
        
        results = []
        for name, migration_func in migrations:
            success = migration_func()
            results.append((name, success))
            
            if not success and not self.dry_run:
                self.log(f"\n❌ {name} failed - stopping migrations")
                break
        
        # Verify no data loss
        if not self.dry_run:
            data_safe = self.verify_no_data_loss(pre_counts["collections"])
            if not data_safe:
                self.log("\n❌ DATA LOSS DETECTED - ROLLBACK REQUIRED")
                return False
        
        # Summary
        self.log("\n" + "="*60)
        self.log("MIGRATION SUMMARY")
        self.log("="*60)
        
        for name, success in results:
            status = "✅" if success else "❌"
            self.log(f"{status} {name}")
        
        all_success = all(success for _, success in results)
        
        if all_success:
            if self.dry_run:
                self.log("\n✅ DRY RUN COMPLETE - All migrations validated")
                self.log("   Run with --execute to apply changes")
            else:
                self.log("\n✅ ALL MIGRATIONS COMPLETED SUCCESSFULLY")
        else:
            self.log("\n❌ SOME MIGRATIONS FAILED")
        
        return all_success
    
    def save_log(self):
        """Save migration log to file"""
        log_file = Path(__file__).parent / f"migration_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(log_file, 'w') as f:
            f.write('\n'.join(self.migration_log))
        self.log(f"\n📝 Log saved to: {log_file}")

def main():
    parser = argparse.ArgumentParser(description='Run Phase 2 database migrations')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--execute', action='store_true', help='Execute migrations')
    args = parser.parse_args()
    
    if not args.dry_run and not args.execute:
        print("Error: Must specify either --dry-run or --execute")
        parser.print_help()
        return 1
    
    runner = MigrationRunner(dry_run=args.dry_run)
    
    if not runner.connect():
        return 1
    
    success = runner.run_all_migrations()
    runner.save_log()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
