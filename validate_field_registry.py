#!/usr/bin/env python3
"""
Field Registry Validation Script
Run to verify all field standards are documented and implemented correctly

Usage:
    python validate_field_registry.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
backend_env = Path(__file__).parent / "backend" / ".env"
if backend_env.exists():
    load_dotenv(backend_env)
from backend.validation.field_registry import (
    validate_manager_name,
    validate_fund_type,
    validate_mongodb_document,
    validate_api_response,
    get_deprecated_fields,
    ALLOWED_MANAGER_NAMES,
    ALLOWED_FUND_TYPES,
    MONGODB_SCHEMAS
)

def test_connection():
    """Test MongoDB connection"""
    print("\n" + "="*60)
    print("1. TESTING MONGODB CONNECTION")
    print("="*60)
    
    mongo_url = os.environ.get('MONGO_URL')
    if not mongo_url:
        print("❌ MONGO_URL environment variable not set")
        return None
    
    try:
        client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        db = client.get_default_database()
        client.admin.command('ping')
        print(f"✅ Connected to MongoDB: {db.name}")
        return db
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return None

def check_duplicate_fields(db):
    """Check for duplicate/deprecated fields"""
    print("\n" + "="*60)
    print("2. CHECKING FOR DUPLICATE/DEPRECATED FIELDS")
    print("="*60)
    
    errors = []
    warnings = []
    
    # Check mt5_accounts
    print("\n📊 Checking mt5_accounts...")
    mt5_with_manager_name = db.mt5_accounts.count_documents({"manager_name": {"$exists": True}})
    if mt5_with_manager_name > 0:
        warnings.append(f"⚠️  Found {mt5_with_manager_name} mt5_accounts with deprecated 'manager_name' field")
    else:
        print("  ✅ No deprecated 'manager_name' field")
    
    mt5_with_last_sync = db.mt5_accounts.count_documents({"last_sync": {"$exists": True}})
    if mt5_with_last_sync > 0:
        warnings.append(f"⚠️  Found {mt5_with_last_sync} mt5_accounts with deprecated 'last_sync' field")
    else:
        print("  ✅ No deprecated 'last_sync' field")
    
    # Check money_managers
    print("\n📊 Checking money_managers...")
    mm_with_manager_name = db.money_managers.count_documents({"manager_name": {"$exists": True}})
    if mm_with_manager_name > 0:
        warnings.append(f"⚠️  Found {mm_with_manager_name} money_managers with deprecated 'manager_name' field")
    else:
        print("  ✅ No deprecated 'manager_name' field")
    
    # Check investments
    print("\n📊 Checking investments...")
    inv_with_amount = db.investments.count_documents({"amount": {"$exists": True}})
    if inv_with_amount > 0:
        warnings.append(f"⚠️  Found {inv_with_amount} investments with deprecated 'amount' field")
    else:
        print("  ✅ No deprecated 'amount' field")
    
    inv_with_referred_by = db.investments.count_documents({"referred_by": {"$exists": True}})
    if inv_with_referred_by > 0:
        warnings.append(f"⚠️  Found {inv_with_referred_by} investments with deprecated 'referred_by' field")
    else:
        print("  ✅ No deprecated 'referred_by' field")
    
    return errors, warnings

def check_manager_names(db):
    """Check all manager names are valid"""
    print("\n" + "="*60)
    print("3. VALIDATING MANAGER NAMES")
    print("="*60)
    
    errors = []
    
    print("\n📊 Checking mt5_accounts manager names...")
    for account in db.mt5_accounts.find():
        if "manager" in account:
            if not validate_manager_name(account["manager"]):
                errors.append(f"❌ Invalid manager name in account {account.get('account', 'unknown')}: '{account['manager']}'")
    
    print("\n📊 Checking money_managers names...")
    for manager in db.money_managers.find():
        if "name" in manager:
            if not validate_manager_name(manager["name"]):
                errors.append(f"❌ Invalid manager name in money_managers: '{manager['name']}'")
    
    if not errors:
        print("  ✅ All manager names are valid")
    
    return errors

def check_fund_types(db):
    """Check all fund types are valid"""
    print("\n" + "="*60)
    print("4. VALIDATING FUND TYPES")
    print("="*60)
    
    errors = []
    
    print("\n📊 Checking mt5_accounts fund types...")
    for account in db.mt5_accounts.find():
        if "fund_type" in account:
            if not validate_fund_type(account["fund_type"]):
                errors.append(f"❌ Invalid fund type in account {account.get('account', 'unknown')}: '{account['fund_type']}'")
    
    print("\n📊 Checking investments fund types...")
    for investment in db.investments.find():
        if "fund_type" in investment:
            if not validate_fund_type(investment["fund_type"]):
                errors.append(f"❌ Invalid fund type in investment {investment.get('investment_id', 'unknown')}: '{investment['fund_type']}'")
    
    if not errors:
        print("  ✅ All fund types are valid")
    
    return errors

def check_timestamps(db):
    """Check all timestamps are DateTime objects"""
    print("\n" + "="*60)
    print("5. VALIDATING TIMESTAMP TYPES")
    print("="*60)
    
    warnings = []
    
    # Check salespeople
    print("\n📊 Checking salespeople timestamps...")
    string_timestamps = db.salespeople.count_documents({"created_at": {"$type": "string"}})
    if string_timestamps > 0:
        warnings.append(f"⚠️  Found {string_timestamps} salespeople with string 'created_at' (should be DateTime)")
    else:
        print("  ✅ All salespeople timestamps are DateTime")
    
    # Check referral_commissions
    print("\n📊 Checking referral_commissions timestamps...")
    string_payment_dates = db.referral_commissions.count_documents({"payment_date": {"$type": "string"}})
    if string_payment_dates > 0:
        warnings.append(f"⚠️  Found {string_payment_dates} commissions with string 'payment_date' (should be DateTime)")
    else:
        print("  ✅ All commission payment dates are DateTime")
    
    return warnings

def check_referral_system(db):
    """Check referral system data integrity"""
    print("\n" + "="*60)
    print("6. VALIDATING REFERRAL SYSTEM DATA")
    print("="*60)
    
    errors = []
    
    # Check Salvador Palma
    print("\n📊 Checking Salvador Palma record...")
    salvador = db.salespeople.find_one({"name": "Salvador Palma"})
    if not salvador:
        errors.append("❌ Salvador Palma not found in salespeople collection")
    else:
        print(f"  ✅ Salvador Palma found: {salvador['salesperson_id']}")
        
        # Convert Decimal128 to float
        from bson import Decimal128
        def to_float(val):
            if isinstance(val, Decimal128):
                return float(val.to_decimal())
            return float(val) if val else 0.0
        
        print(f"     Total Sales: ${to_float(salvador.get('total_sales_volume', 0)):,.2f}")
        print(f"     Commissions: ${to_float(salvador.get('total_commissions_earned', 0)):,.2f}")
        print(f"     Clients: {salvador.get('total_clients_referred', 0)}")
        
        # Verify expected values
        expected_sales = 118151.41
        expected_commissions = 3272.27
        expected_clients = 1
        
        actual_sales = to_float(salvador.get('total_sales_volume', 0))
        actual_commissions = to_float(salvador.get('total_commissions_earned', 0))
        actual_clients = salvador.get('total_clients_referred', 0)
        
        if abs(actual_sales - expected_sales) > 0.01:
            errors.append(f"❌ Salvador sales mismatch: expected ${expected_sales:,.2f}, got ${actual_sales:,.2f}")
        
        if abs(actual_commissions - expected_commissions) > 0.01:
            errors.append(f"❌ Salvador commissions mismatch: expected ${expected_commissions:,.2f}, got ${actual_commissions:,.2f}")
        
        if actual_clients != expected_clients:
            errors.append(f"❌ Salvador clients mismatch: expected {expected_clients}, got {actual_clients}")
    
    # Check Alejandro's investments
    print("\n📊 Checking Alejandro's investments...")
    alejandro_investments = list(db.investments.find({
        "referral_salesperson_id": salvador.get('salesperson_id') if salvador else None
    }))
    
    if len(alejandro_investments) != 2:
        errors.append(f"❌ Expected 2 investments for Alejandro, found {len(alejandro_investments)}")
    else:
        print(f"  ✅ Found {len(alejandro_investments)} investments for Alejandro")
        for inv in alejandro_investments:
            print(f"     {inv.get('fund_type')}: ${float(inv.get('principal_amount', 0)):,.2f}")
    
    # Check commissions
    print("\n📊 Checking referral commissions...")
    commissions = db.referral_commissions.count_documents({
        "salesperson_id": salvador.get('salesperson_id') if salvador else None
    })
    
    if commissions != 16:
        errors.append(f"❌ Expected 16 commissions for Salvador, found {commissions}")
    else:
        print(f"  ✅ Found {commissions} commissions for Salvador")
    
    return errors

def check_document_counts(db):
    """Check expected document counts"""
    print("\n" + "="*60)
    print("7. CHECKING DOCUMENT COUNTS")
    print("="*60)
    
    expected_counts = {
        "mt5_accounts": 11,
        "money_managers": 7,
        "salespeople": 3,
        "referral_commissions": 16,
        "investments": 3,
        "clients": 1
    }
    
    errors = []
    
    for collection, expected in expected_counts.items():
        actual = db[collection].count_documents({})
        status = "✅" if actual == expected else "⚠️"
        print(f"  {status} {collection}: {actual} docs (expected {expected})")
        
        if actual != expected:
            errors.append(f"⚠️  {collection} count mismatch: expected {expected}, got {actual}")
    
    return errors

def main():
    """Run all validation checks"""
    print("\n" + "="*60)
    print("FIDUS FIELD REGISTRY VALIDATION")
    print("="*60)
    
    # Test connection
    db = test_connection()
    if db is None:
        print("\n❌ VALIDATION FAILED: Cannot connect to database")
        return 1
    
    all_errors = []
    all_warnings = []
    
    # Run checks
    errors, warnings = check_duplicate_fields(db)
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    
    errors = check_manager_names(db)
    all_errors.extend(errors)
    
    errors = check_fund_types(db)
    all_errors.extend(errors)
    
    warnings = check_timestamps(db)
    all_warnings.extend(warnings)
    
    errors = check_referral_system(db)
    all_errors.extend(errors)
    
    errors = check_document_counts(db)
    all_warnings.extend(errors)  # Counts are warnings, not errors
    
    # Print summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    if all_errors:
        print(f"\n❌ CRITICAL ERRORS: {len(all_errors)}")
        for error in all_errors:
            print(f"  {error}")
    
    if all_warnings:
        print(f"\n⚠️  WARNINGS: {len(all_warnings)}")
        for warning in all_warnings:
            print(f"  {warning}")
    
    if not all_errors and not all_warnings:
        print("\n✅ ALL VALIDATION CHECKS PASSED")
        print("\nField Registry is complete and database is consistent!")
        return 0
    elif not all_errors:
        print("\n✅ NO CRITICAL ERRORS")
        print("⚠️  Some warnings found - migration recommended")
        return 0
    else:
        print("\n❌ VALIDATION FAILED")
        print(f"\nFound {len(all_errors)} critical errors and {len(all_warnings)} warnings")
        print("Please review and fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
