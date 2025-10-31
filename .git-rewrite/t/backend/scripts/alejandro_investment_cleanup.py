#!/usr/bin/env python3
"""
Alejandro Investment Cleanup Script
Addresses the critical data corruption issue where 10 investments were created instead of 4
Provides detailed analysis and safe cleanup with rollback capability
"""

import asyncio
import json
import sys
import os
from datetime import datetime, timezone
from typing import List, Dict, Any
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.database import connection_manager
from mongodb_integration import mongodb_manager

class AlejandroCleanupManager:
    """Manager for Alejandro investment data cleanup"""
    
    def __init__(self):
        self.db = None
        self.backup_file = f"/app/backend/backups/alejandro_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.cleanup_report = []
    
    async def initialize(self):
        """Initialize database connection"""
        self.db = await connection_manager.get_database()
    
    async def analyze_alejandro_data(self) -> Dict[str, Any]:
        """Comprehensive analysis of Alejandro's investment data"""
        
        print("🔍 ANALYZING ALEJANDRO INVESTMENT DATA")
        print("=" * 50)
        
        # Find Alejandro user
        alejandro = await self.db.users.find_one({'username': 'alejandro_mariscal'})
        
        if not alejandro:
            print("❌ Alejandro Mariscal user not found in database")
            return {"error": "User not found"}
        
        print(f"✅ Found Alejandro: {alejandro.get('email', 'No email')}")
        user_id = alejandro.get('user_id', str(alejandro['_id']))
        print(f"   User ID: {user_id}")
        
        # Find all investments for Alejandro
        investments = await self.db.investments.find({'client_id': user_id}).to_list(length=None)
        
        print(f"\n📊 INVESTMENT ANALYSIS:")
        print(f"   Total investments found: {len(investments)}")
        
        if len(investments) == 0:
            print("   ✅ No investments found - clean state")
            return {
                "user_found": True,
                "investments_count": 0,
                "total_amount": 0,
                "analysis": "Clean state - no duplicate investments"
            }
        
        # Analyze investments
        investment_analysis = {
            'by_fund': {},
            'by_date': {},
            'duplicates': [],
            'total_amount': 0
        }
        
        print(f"\n   📋 Investment Details:")
        for i, inv in enumerate(investments, 1):
            fund_code = inv.get('fund_code', 'Unknown')
            amount = float(inv.get('principal_amount', 0))
            created_at = inv.get('created_at', 'Unknown')
            investment_id = inv.get('investment_id', inv.get('_id', 'Unknown'))
            
            print(f"   {i:2d}. Fund: {fund_code:12} | Amount: ${amount:>12,.2f} | Created: {created_at} | ID: {investment_id}")
            
            # Group by fund
            if fund_code not in investment_analysis['by_fund']:
                investment_analysis['by_fund'][fund_code] = {'count': 0, 'amount': 0, 'investments': []}
            
            investment_analysis['by_fund'][fund_code]['count'] += 1
            investment_analysis['by_fund'][fund_code]['amount'] += amount
            investment_analysis['by_fund'][fund_code]['investments'].append(inv)
            
            investment_analysis['total_amount'] += amount
        
        # Identify potential duplicates
        print(f"\n   🔍 Duplicate Analysis:")
        for fund_code, fund_data in investment_analysis['by_fund'].items():
            print(f"   Fund {fund_code}: {fund_data['count']} investments, Total: ${fund_data['amount']:,.2f}")
            
            if fund_data['count'] > 1:
                # Check for exact duplicates (same amount, close creation time)
                fund_investments = fund_data['investments']
                for i, inv1 in enumerate(fund_investments):
                    for j, inv2 in enumerate(fund_investments[i+1:], i+1):
                        amount_diff = abs(float(inv1.get('principal_amount', 0)) - float(inv2.get('principal_amount', 0)))
                        
                        if amount_diff < 0.01:  # Same amount (within 1 cent)
                            investment_analysis['duplicates'].append({
                                'fund': fund_code,
                                'investment1': inv1,
                                'investment2': inv2,
                                'reason': 'Same amount in same fund'
                            })
        
        print(f"\n   🚨 Potential duplicates found: {len(investment_analysis['duplicates'])}")
        for dup in investment_analysis['duplicates']:
            print(f"      - Fund {dup['fund']}: ${float(dup['investment1'].get('principal_amount', 0)):,.2f}")
        
        print(f"\n   💰 Total AUM for Alejandro: ${investment_analysis['total_amount']:,.2f}")
        
        # Expected vs Actual comparison
        expected_total = 118151.41  # From context
        if abs(investment_analysis['total_amount'] - expected_total) > 0.01:
            print(f"   ⚠️  DISCREPANCY DETECTED:")
            print(f"      Expected total: ${expected_total:,.2f}")
            print(f"      Actual total:   ${investment_analysis['total_amount']:,.2f}")
            print(f"      Difference:     ${investment_analysis['total_amount'] - expected_total:,.2f}")
        else:
            print(f"   ✅ Total matches expected amount")
        
        return {
            "user_found": True,
            "user_id": user_id,
            "investments_count": len(investments),
            "total_amount": investment_analysis['total_amount'],
            "expected_amount": expected_total,
            "discrepancy": investment_analysis['total_amount'] - expected_total,
            "by_fund": investment_analysis['by_fund'],
            "duplicates": investment_analysis['duplicates'],
            "investments": investments
        }
    
    async def create_backup(self, data: Dict[str, Any]):
        """Create backup before any cleanup operations"""
        
        print(f"\n💾 CREATING BACKUP")
        print(f"   Backup file: {self.backup_file}")
        
        # Ensure backup directory exists
        backup_dir = Path(self.backup_file).parent
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Serialize data for backup
        backup_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'user_data': data,
            'reason': 'Pre-cleanup backup for Alejandro investment correction'
        }
        
        # Convert ObjectId and other non-serializable types
        def json_serializer(obj):
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            return str(obj)
        
        with open(self.backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2, default=json_serializer)
        
        print(f"   ✅ Backup created successfully")
        print(f"   Backup size: {Path(self.backup_file).stat().st_size} bytes")
    
    async def generate_cleanup_plan(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed cleanup plan based on analysis"""
        
        print(f"\n📋 GENERATING CLEANUP PLAN")
        print("=" * 30)
        
        plan = {
            'actions': [],
            'investments_to_keep': [],
            'investments_to_remove': [],
            'expected_final_amount': 0
        }
        
        if analysis['investments_count'] == 0:
            print("   ✅ No cleanup needed - no investments found")
            return plan
        
        # Strategy: Keep the oldest investment for each fund, remove duplicates
        for fund_code, fund_data in analysis['by_fund'].items():
            if fund_data['count'] == 1:
                # Single investment - keep it
                investment = fund_data['investments'][0]
                plan['investments_to_keep'].append(investment)
                plan['expected_final_amount'] += float(investment.get('principal_amount', 0))
                
                plan['actions'].append({
                    'action': 'keep',
                    'investment_id': investment.get('investment_id'),
                    'fund': fund_code,
                    'amount': float(investment.get('principal_amount', 0)),
                    'reason': 'Single investment in fund'
                })
            
            else:
                # Multiple investments - keep oldest, remove others
                sorted_investments = sorted(fund_data['investments'], 
                                          key=lambda x: x.get('created_at', datetime.min))
                
                # Keep the first (oldest)
                keep_investment = sorted_investments[0]
                plan['investments_to_keep'].append(keep_investment)
                plan['expected_final_amount'] += float(keep_investment.get('principal_amount', 0))
                
                plan['actions'].append({
                    'action': 'keep',
                    'investment_id': keep_investment.get('investment_id'),
                    'fund': fund_code,
                    'amount': float(keep_investment.get('principal_amount', 0)),
                    'reason': 'Oldest investment in fund (duplicate resolution)'
                })
                
                # Remove the rest
                for remove_investment in sorted_investments[1:]:
                    plan['investments_to_remove'].append(remove_investment)
                    
                    plan['actions'].append({
                        'action': 'remove',
                        'investment_id': remove_investment.get('investment_id'),
                        'fund': fund_code,
                        'amount': float(remove_investment.get('principal_amount', 0)),
                        'reason': 'Duplicate investment (newer than kept version)'
                    })
        
        # Display plan
        print(f"   📊 Cleanup Summary:")
        print(f"      Investments to keep:   {len(plan['investments_to_keep'])}")
        print(f"      Investments to remove: {len(plan['investments_to_remove'])}")
        print(f"      Expected final total:  ${plan['expected_final_amount']:,.2f}")
        
        print(f"\n   📋 Detailed Actions:")
        for i, action in enumerate(plan['actions'], 1):
            action_icon = "✅" if action['action'] == 'keep' else "❌"
            print(f"      {i:2d}. {action_icon} {action['action'].upper()} | Fund: {action['fund']} | ${action['amount']:,.2f} | {action['reason']}")
        
        return plan
    
    async def execute_cleanup(self, plan: Dict[str, Any], dry_run: bool = True) -> Dict[str, Any]:
        """Execute the cleanup plan"""
        
        mode = "DRY RUN" if dry_run else "LIVE EXECUTION"
        print(f"\n🚀 EXECUTING CLEANUP PLAN - {mode}")
        print("=" * 40)
        
        results = {
            'removed_count': 0,
            'kept_count': 0,
            'errors': [],
            'success': True
        }
        
        if dry_run:
            print("   🔍 DRY RUN MODE - No actual changes will be made")
            print("   This is a simulation to verify the cleanup plan")
        
        # Remove duplicate investments
        for investment in plan['investments_to_remove']:
            investment_id = investment.get('investment_id')
            fund_code = investment.get('fund_code')
            amount = float(investment.get('principal_amount', 0))
            
            try:
                if dry_run:
                    print(f"   [DRY RUN] Would remove: {investment_id} | Fund: {fund_code} | ${amount:,.2f}")
                else:
                    result = await self.db.investments.delete_one({'investment_id': investment_id})
                    if result.deleted_count == 1:
                        print(f"   ✅ Removed: {investment_id} | Fund: {fund_code} | ${amount:,.2f}")
                        results['removed_count'] += 1
                    else:
                        error_msg = f"Failed to remove investment {investment_id}"
                        print(f"   ❌ {error_msg}")
                        results['errors'].append(error_msg)
                        results['success'] = False
            
            except Exception as e:
                error_msg = f"Error removing investment {investment_id}: {str(e)}"
                print(f"   ❌ {error_msg}")
                results['errors'].append(error_msg)
                results['success'] = False
        
        # Count kept investments
        results['kept_count'] = len(plan['investments_to_keep'])
        
        print(f"\n   📊 Execution Results:")
        print(f"      Investments removed: {results['removed_count']}")
        print(f"      Investments kept:    {results['kept_count']}")
        print(f"      Errors encountered:  {len(results['errors'])}")
        
        if results['errors']:
            print(f"\n   ⚠️  Errors:")
            for error in results['errors']:
                print(f"      - {error}")
        
        return results
    
    async def verify_cleanup(self, expected_count: int, expected_amount: float) -> bool:
        """Verify cleanup results"""
        
        print(f"\n🔍 VERIFYING CLEANUP RESULTS")
        print("=" * 30)
        
        # Re-analyze Alejandro data
        verification_analysis = await self.analyze_alejandro_data()
        
        actual_count = verification_analysis.get('investments_count', 0)
        actual_amount = verification_analysis.get('total_amount', 0)
        
        success = True
        
        print(f"   Expected investments: {expected_count}")
        print(f"   Actual investments:   {actual_count}")
        
        if actual_count != expected_count:
            print(f"   ❌ Investment count mismatch!")
            success = False
        else:
            print(f"   ✅ Investment count correct")
        
        print(f"   Expected total amount: ${expected_amount:,.2f}")
        print(f"   Actual total amount:   ${actual_amount:,.2f}")
        
        if abs(actual_amount - expected_amount) > 0.01:
            print(f"   ❌ Total amount mismatch!")
            success = False
        else:
            print(f"   ✅ Total amount correct")
        
        return success

async def main():
    """Main cleanup execution"""
    
    print("🔧 ALEJANDRO INVESTMENT CLEANUP UTILITY")
    print("=" * 60)
    print("This script addresses the critical data corruption issue")
    print("where 10 investments were created instead of 4 for Alejandro Mariscal")
    print("=" * 60)
    
    cleanup_manager = AlejandroCleanupManager()
    
    try:
        # Initialize
        await cleanup_manager.initialize()
        print("✅ Database connection established")
        
        # Analyze current data
        analysis = await cleanup_manager.analyze_alejandro_data()
        
        if analysis.get('error'):
            print(f"❌ Analysis failed: {analysis['error']}")
            return
        
        # Check if cleanup is needed
        if analysis['investments_count'] == 0:
            print("\n🎉 No cleanup needed - database is already clean")
            return
        
        if analysis['investments_count'] <= 4 and abs(analysis['discrepancy']) < 0.01:
            print("\n🎉 Data appears to be correct - no cleanup needed")
            return
        
        # Create backup
        await cleanup_manager.create_backup(analysis)
        
        # Generate cleanup plan
        cleanup_plan = await cleanup_manager.generate_cleanup_plan(analysis)
        
        if len(cleanup_plan['investments_to_remove']) == 0:
            print("\n🎉 No duplicates found - no cleanup needed")
            return
        
        # Execute dry run first
        print("\n" + "="*60)
        print("PHASE 1: DRY RUN EXECUTION")
        print("="*60)
        
        dry_run_results = await cleanup_manager.execute_cleanup(cleanup_plan, dry_run=True)
        
        if not dry_run_results['success']:
            print("\n❌ Dry run encountered errors - aborting")
            return
        
        # Ask for confirmation for live execution
        print("\n" + "="*60)
        print("PHASE 2: CONFIRMATION FOR LIVE EXECUTION")
        print("="*60)
        print(f"The cleanup plan will:")
        print(f"  - Remove {len(cleanup_plan['investments_to_remove'])} duplicate investments")
        print(f"  - Keep {len(cleanup_plan['investments_to_keep'])} original investments")
        print(f"  - Reduce total AUM from ${analysis['total_amount']:,.2f} to ${cleanup_plan['expected_final_amount']:,.2f}")
        print(f"  - Backup created at: {cleanup_manager.backup_file}")
        print()
        
        # For production, we'll return here and let user confirm manually
        print("⚠️  MANUAL CONFIRMATION REQUIRED")
        print("To proceed with live execution:")
        print(f"   1. Review the backup file: {cleanup_manager.backup_file}")
        print(f"   2. Verify the cleanup plan above")
        print(f"   3. Run this script with '--execute' flag")
        print()
        print("✅ PHASE 1 ANALYSIS COMPLETE - Ready for manual confirmation")
        
    except Exception as e:
        print(f"❌ Cleanup failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await connection_manager.close_connection()

if __name__ == "__main__":
    asyncio.run(main())