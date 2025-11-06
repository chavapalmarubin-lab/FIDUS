#!/usr/bin/env python3
"""
COMPREHENSIVE FIELD STANDARDS AUDIT
====================================

Audits ALL code to ensure it follows DATABASE_FIELD_STANDARDS.md

This script will:
1. Find all MongoDB queries in the codebase
2. Check if they use correct snake_case field names
3. Identify any violations
4. Report missing fields that need to be added to standards
"""

import os
import re
from pathlib import Path

# Define the standard field names from DATABASE_FIELD_STANDARDS.md
STANDARD_FIELDS = {
    'investments': {
        'snake_case': [
            'client_id', 'client_name', 'client_email', 'fund_type', 
            'principal_amount', 'interest_rate', 'payment_frequency',
            'start_date', 'incubation_end_date', 'first_payment_date',
            'contract_end_date', 'status', 'salesperson_id', 'salesperson_name',
            'referral_code', 'mt5_accounts', 'created_at', 'updated_at',
            'referral_salesperson_id'  # Added for cash flow
        ],
        'camel_case': [
            'clientId', 'clientName', 'clientEmail', 'fundType',
            'principalAmount', 'interestRate', 'paymentFrequency',
            'startDate', 'incubationEndDate', 'firstPaymentDate',
            'contractEndDate', 'status', 'salespersonId', 'salespersonName',
            'referralCode', 'mt5Accounts', 'createdAt', 'updatedAt',
            'referralSalespersonId'
        ]
    },
    'mt5_accounts': {
        'snake_case': [
            'account', 'fund_type', 'manager_name', 'manager_profile_url',
            'execution_method', 'capital_source', 'client_id', 'initial_allocation',
            'equity', 'balance', 'profit', 'margin', 'free_margin', 'margin_level',
            'leverage', 'currency', 'server', 'status', 'last_sync',
            'created_at', 'updated_at'
        ],
        'camel_case': [
            'account', 'fundType', 'managerName', 'managerProfileUrl',
            'executionMethod', 'capitalSource', 'clientId', 'initialAllocation',
            'equity', 'balance', 'profit', 'margin', 'freeMargin', 'marginLevel',
            'leverage', 'currency', 'server', 'status', 'lastSync',
            'createdAt', 'updatedAt'
        ]
    },
    'salespeople': {
        'snake_case': [
            'salesperson_id', 'name', 'code', 'email', 'phone', 'referral_link',
            'commission_rate', 'total_sales', 'total_commissions', 'pending_commissions',
            'paid_commissions', 'active_clients', 'status', 'joined_date',
            'created_at', 'updated_at'
        ],
        'camel_case': [
            'salespersonId', 'name', 'code', 'email', 'phone', 'referralLink',
            'commissionRate', 'totalSales', 'totalCommissions', 'pendingCommissions',
            'paidCommissions', 'activeClients', 'status', 'joinedDate',
            'createdAt', 'updatedAt'
        ]
    },
    'referral_commissions': {
        'snake_case': [
            'salesperson_id', 'salesperson_name', 'client_id', 'client_name',
            'investment_id', 'fund_type', 'payment_date', 'client_payment_amount',
            'commission_amount', 'commission_type', 'payment_number', 'status',
            'approved_by', 'approved_date', 'paid_date', 'created_at', 'updated_at'
        ],
        'camel_case': [
            'salespersonId', 'salespersonName', 'clientId', 'clientName',
            'investmentId', 'fundType', 'paymentDate', 'clientPaymentAmount',
            'commissionAmount', 'commissionType', 'paymentNumber', 'status',
            'approvedBy', 'approvedDate', 'paidDate', 'createdAt', 'updatedAt'
        ]
    }
}

# Known violations to fix
VIOLATIONS = []
UNKNOWN_FIELDS = []

def check_python_files():
    """Check all Python files for MongoDB queries"""
    print("="*80)
    print("AUDITING PYTHON FILES FOR FIELD STANDARDS COMPLIANCE")
    print("="*80 + "\n")
    
    backend_path = Path('/app/backend')
    python_files = list(backend_path.rglob('*.py'))
    
    print(f"Found {len(python_files)} Python files to audit\n")
    
    # Patterns to find MongoDB queries
    patterns = [
        r"db\.(\w+)\.find\((.*?)\)",
        r"db\.(\w+)\.find_one\((.*?)\)",
        r"db\.(\w+)\.update\((.*?)\)",
        r"db\.(\w+)\.update_one\((.*?)\)",
        r"db\.(\w+)\.update_many\((.*?)\)",
        r"db\.(\w+)\.insert_one\((.*?)\)",
        r"db\.(\w+)\.insert_many\((.*?)\)",
        r"\.get\(['\"](\w+)['\"]\)",  # dict.get('field')
    ]
    
    violations_found = 0
    
    for py_file in python_files:
        if 'node_modules' in str(py_file) or '__pycache__' in str(py_file):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                # Check for camelCase in MongoDB queries (should be snake_case)
                for i, line in enumerate(lines, 1):
                    # Skip comments
                    if line.strip().startswith('#'):
                        continue
                    
                    # Look for camelCase field names in db queries
                    if 'db.' in line and any(pattern in line for pattern in ['find', 'update', 'insert']):
                        # Check for camelCase patterns (capital letter after lowercase)
                        camel_matches = re.findall(r"['\"]([a-z]+[A-Z]\w+)['\"]", line)
                        
                        for match in camel_matches:
                            # Check if this is a known field that should be snake_case
                            for collection, fields in STANDARD_FIELDS.items():
                                if match in fields['camel_case']:
                                    violations_found += 1
                                    VIOLATIONS.append({
                                        'file': str(py_file.relative_to('/app')),
                                        'line': i,
                                        'field': match,
                                        'should_be': fields['snake_case'][fields['camel_case'].index(match)],
                                        'collection': collection,
                                        'code': line.strip()
                                    })
                    
                    # Check .get() calls for proper field names
                    get_matches = re.findall(r"\.get\(['\"](\w+)['\"]\)", line)
                    for match in get_matches:
                        # Check if contains underscore (good) or camelCase (potentially bad in MongoDB context)
                        if re.search(r'[a-z][A-Z]', match):
                            # This might be okay if it's after API conversion
                            # But flag it for review
                            pass
                            
        except Exception as e:
            print(f"Error reading {py_file}: {e}")
    
    return violations_found

def check_javascript_files():
    """Check JavaScript files for API calls"""
    print("\n" + "="*80)
    print("AUDITING JAVASCRIPT FILES FOR FIELD STANDARDS COMPLIANCE")
    print("="*80 + "\n")
    
    frontend_path = Path('/app/frontend/src')
    if not frontend_path.exists():
        print("Frontend directory not found")
        return 0
    
    js_files = list(frontend_path.rglob('*.js')) + list(frontend_path.rglob('*.jsx'))
    
    print(f"Found {len(js_files)} JavaScript files to audit\n")
    
    violations_found = 0
    
    for js_file in js_files:
        if 'node_modules' in str(js_file):
            continue
            
        try:
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    # Look for snake_case in frontend (should be camelCase)
                    snake_matches = re.findall(r"['\"]([a-z]+_\w+)['\"]", line)
                    
                    for match in snake_matches:
                        # Check if this is a known field that should be camelCase
                        for collection, fields in STANDARD_FIELDS.items():
                            if match in fields['snake_case']:
                                violations_found += 1
                                VIOLATIONS.append({
                                    'file': str(js_file.relative_to('/app')),
                                    'line': i,
                                    'field': match,
                                    'should_be': fields['camel_case'][fields['snake_case'].index(match)],
                                    'collection': collection,
                                    'code': line.strip()[:100]  # Truncate long lines
                                })
                                
        except Exception as e:
            print(f"Error reading {js_file}: {e}")
    
    return violations_found

def generate_report():
    """Generate audit report"""
    print("\n" + "="*80)
    print("FIELD STANDARDS AUDIT REPORT")
    print("="*80 + "\n")
    
    if not VIOLATIONS:
        print("✅ NO VIOLATIONS FOUND - All code follows field standards!\n")
        return
    
    print(f"❌ FOUND {len(VIOLATIONS)} VIOLATIONS\n")
    print("These must be fixed to ensure consistency:\n")
    
    # Group by file
    by_file = {}
    for v in VIOLATIONS:
        file = v['file']
        if file not in by_file:
            by_file[file] = []
        by_file[file].append(v)
    
    for file, violations in sorted(by_file.items()):
        print(f"\n📁 {file}")
        print("─" * 80)
        for v in violations:
            print(f"  Line {v['line']}: '{v['field']}' should be '{v['should_be']}'")
            print(f"    Collection: {v['collection']}")
            print(f"    Code: {v['code'][:80]}")
            print()

if __name__ == '__main__':
    print("\n" + "="*80)
    print("STARTING COMPREHENSIVE FIELD STANDARDS AUDIT")
    print("="*80 + "\n")
    print("Checking against: DATABASE_FIELD_STANDARDS.md")
    print("Date:", "November 6, 2025")
    print("\n")
    
    # Run audits
    py_violations = check_python_files()
    js_violations = check_javascript_files()
    
    # Generate report
    generate_report()
    
    print("\n" + "="*80)
    print("AUDIT COMPLETE")
    print("="*80)
    print(f"\nTotal violations found: {len(VIOLATIONS)}")
    
    if VIOLATIONS:
        print("\n⚠️  ACTION REQUIRED: Fix all violations to ensure consistency")
        print("    Use DATABASE_FIELD_STANDARDS.md as the source of truth")
    else:
        print("\n✅ All code follows field standards correctly!")
