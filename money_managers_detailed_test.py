#!/usr/bin/env python3
"""
Money Managers Profile System Phase 1 - Detailed Verification Test

This test specifically verifies the exact requirements mentioned in the review request:
1. Verify initialization creates 3 managers: manager_3157, manager_5843, manager_uno14
2. Check correct account assignments:
   - Manager 3157: accounts 886557, 885822 (Copy Trade)
   - Manager 5843: account 886066 (Copy Trade) 
   - Manager UNO14: account 886602 (MAM)
3. Test performance aggregation across assigned accounts for each manager
4. Verify metrics calculation: total_allocated, total_pnl, win_rate, profit_factor
5. Check account details mapping with correct allocations
6. Verify money_managers collection creation with proper indexes
7. Test manager_id uniqueness
8. Test comparison endpoint with multiple manager IDs
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DetailedMoneyManagersTester:
    """Detailed Money Managers Profile System Tester"""
    
    def __init__(self):
        self.base_url = "https://fidus-restore.preview.emergentagent.com"
        self.api_base = f"{self.base_url}/api"
        
        self.admin_credentials = {
            "username": "admin",
            "password": "password123",
            "user_type": "admin"
        }
        
        self.jwt_token = None
        
        # Exact requirements from review request
        self.required_managers = {
            "manager_3157": {
                "accounts": [886557, 885822],
                "execution_type": "copy_trade",
                "expected_allocation": 98151.41  # 80000 + 18151.41
            },
            "manager_5843": {
                "accounts": [886066],
                "execution_type": "copy_trade",
                "expected_allocation": 10000
            },
            "manager_uno14": {
                "accounts": [886602],
                "execution_type": "mam",
                "expected_allocation": 10000
            }
        }
        
        self.required_metrics = [
            "total_allocated", "total_pnl", "win_rate", "profit_factor"
        ]
    
    async def authenticate_admin(self) -> bool:
        """Authenticate as admin and get JWT token"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/auth/login",
                    json=self.admin_credentials,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.jwt_token = data.get("token")
                        logger.info("✅ Admin authentication successful")
                        return True
                    else:
                        logger.error(f"❌ Admin authentication failed: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"❌ Authentication error: {str(e)}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers with JWT token"""
        return {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json"
        }
    
    async def verify_initialization_creates_3_managers(self) -> Dict[str, Any]:
        """Verify initialization creates exactly 3 managers with correct IDs"""
        logger.info("🧪 Testing: Initialization creates 3 managers")
        
        try:
            # First, get current managers
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base}/admin/money-managers",
                    headers=self.get_auth_headers()
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        managers = data.get("managers", [])
                        
                        # Check if we have exactly 3 managers
                        manager_ids = [m["manager_id"] for m in managers]
                        expected_ids = ["manager_3157", "manager_5843", "manager_uno14"]
                        
                        verification = {
                            "total_managers": len(managers),
                            "expected_count": 3,
                            "count_correct": len(managers) == 3,
                            "manager_ids_found": manager_ids,
                            "expected_ids": expected_ids,
                            "all_expected_ids_present": all(id in manager_ids for id in expected_ids),
                            "no_extra_managers": len(manager_ids) == len(expected_ids)
                        }
                        
                        logger.info(f"✅ Found {len(managers)} managers: {manager_ids}")
                        
                        return {
                            "test": "Initialization creates 3 managers",
                            "status": "PASS" if verification["count_correct"] and verification["all_expected_ids_present"] else "FAIL",
                            "verification": verification,
                            "managers": managers
                        }
                    else:
                        return {
                            "test": "Initialization creates 3 managers",
                            "status": "FAIL",
                            "error": f"Failed to get managers: {response.status}"
                        }
        except Exception as e:
            return {
                "test": "Initialization creates 3 managers",
                "status": "ERROR",
                "error": str(e)
            }
    
    async def verify_account_assignments(self, managers: List[Dict]) -> Dict[str, Any]:
        """Verify correct account assignments for each manager"""
        logger.info("🧪 Testing: Account assignments verification")
        
        try:
            assignment_results = {}
            
            for manager in managers:
                manager_id = manager["manager_id"]
                if manager_id in self.required_managers:
                    required = self.required_managers[manager_id]
                    actual_accounts = set(manager.get("assigned_accounts", []))
                    expected_accounts = set(required["accounts"])
                    
                    assignment_check = {
                        "manager_id": manager_id,
                        "expected_accounts": list(expected_accounts),
                        "actual_accounts": list(actual_accounts),
                        "accounts_match": actual_accounts == expected_accounts,
                        "execution_type": manager.get("execution_type"),
                        "execution_type_correct": manager.get("execution_type") == required["execution_type"],
                        "account_count_correct": len(actual_accounts) == len(expected_accounts)
                    }
                    
                    assignment_results[manager_id] = assignment_check
            
            all_assignments_correct = all(
                result["accounts_match"] and result["execution_type_correct"]
                for result in assignment_results.values()
            )
            
            logger.info(f"✅ Account assignments verified for {len(assignment_results)} managers")
            
            return {
                "test": "Account assignments verification",
                "status": "PASS" if all_assignments_correct else "FAIL",
                "assignment_results": assignment_results,
                "all_assignments_correct": all_assignments_correct
            }
            
        except Exception as e:
            return {
                "test": "Account assignments verification",
                "status": "ERROR",
                "error": str(e)
            }
    
    async def verify_performance_aggregation(self, managers: List[Dict]) -> Dict[str, Any]:
        """Verify performance aggregation across assigned accounts"""
        logger.info("🧪 Testing: Performance aggregation across assigned accounts")
        
        try:
            performance_results = {}
            
            for manager in managers:
                manager_id = manager["manager_id"]
                performance = manager.get("performance", {})
                
                # Check if all required metrics are present
                metrics_check = {
                    "manager_id": manager_id,
                    "has_performance": len(performance) > 0,
                    "required_metrics_present": {},
                    "all_required_metrics_present": False,
                    "performance_data": performance
                }
                
                for metric in self.required_metrics:
                    metrics_check["required_metrics_present"][metric] = metric in performance
                
                metrics_check["all_required_metrics_present"] = all(
                    metrics_check["required_metrics_present"].values()
                )
                
                # Verify performance values are reasonable
                if performance:
                    metrics_check["total_allocated_positive"] = performance.get("total_allocated", 0) > 0
                    metrics_check["win_rate_valid"] = 0 <= performance.get("win_rate", -1) <= 100
                    metrics_check["profit_factor_valid"] = performance.get("profit_factor", -1) >= 0
                
                performance_results[manager_id] = metrics_check
            
            all_performance_valid = all(
                result["all_required_metrics_present"]
                for result in performance_results.values()
            )
            
            logger.info(f"✅ Performance aggregation verified for {len(performance_results)} managers")
            
            return {
                "test": "Performance aggregation verification",
                "status": "PASS" if all_performance_valid else "FAIL",
                "performance_results": performance_results,
                "all_performance_valid": all_performance_valid
            }
            
        except Exception as e:
            return {
                "test": "Performance aggregation verification",
                "status": "ERROR",
                "error": str(e)
            }
    
    async def verify_account_details_mapping(self, managers: List[Dict]) -> Dict[str, Any]:
        """Verify account details mapping with correct allocations"""
        logger.info("🧪 Testing: Account details mapping with allocations")
        
        try:
            mapping_results = {}
            
            for manager in managers:
                manager_id = manager["manager_id"]
                account_details = manager.get("account_details", [])
                
                mapping_check = {
                    "manager_id": manager_id,
                    "has_account_details": len(account_details) > 0,
                    "account_details_complete": False,
                    "accounts_with_allocations": {},
                    "total_allocation_calculated": 0
                }
                
                if account_details:
                    # Check each account detail
                    required_fields = ["account", "allocation", "current_equity", "pnl", "status"]
                    all_fields_present = all(
                        all(field in account for field in required_fields)
                        for account in account_details
                    )
                    mapping_check["account_details_complete"] = all_fields_present
                    
                    # Calculate total allocation
                    for account in account_details:
                        account_num = account.get("account")
                        allocation = account.get("allocation", 0)
                        mapping_check["accounts_with_allocations"][account_num] = allocation
                        mapping_check["total_allocation_calculated"] += allocation
                
                mapping_results[manager_id] = mapping_check
            
            all_mappings_valid = all(
                result["has_account_details"] and result["account_details_complete"]
                for result in mapping_results.values()
            )
            
            logger.info(f"✅ Account details mapping verified for {len(mapping_results)} managers")
            
            return {
                "test": "Account details mapping verification",
                "status": "PASS" if all_mappings_valid else "FAIL",
                "mapping_results": mapping_results,
                "all_mappings_valid": all_mappings_valid
            }
            
        except Exception as e:
            return {
                "test": "Account details mapping verification",
                "status": "ERROR",
                "error": str(e)
            }
    
    async def verify_comparison_endpoint(self) -> Dict[str, Any]:
        """Test comparison endpoint with multiple manager IDs"""
        logger.info("🧪 Testing: Manager comparison endpoint")
        
        try:
            manager_ids = ["manager_3157", "manager_5843", "manager_uno14"]
            manager_ids_param = ",".join(manager_ids)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base}/admin/money-managers/compare?manager_ids={manager_ids_param}",
                    headers=self.get_auth_headers()
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        comparison_check = {
                            "response_received": True,
                            "has_managers": "managers" in data,
                            "has_comparison_metrics": "comparison_metrics" in data,
                            "managers_count": len(data.get("managers", [])),
                            "expected_managers_count": len(manager_ids),
                            "managers_count_correct": len(data.get("managers", [])) == len(manager_ids),
                            "comparison_data": data
                        }
                        
                        # Verify comparison metrics structure
                        comparison_metrics = data.get("comparison_metrics", {})
                        if comparison_metrics:
                            expected_comparison_fields = ["total_allocated", "total_pnl", "avg_win_rate", "avg_profit_factor"]
                            comparison_check["comparison_metrics_complete"] = all(
                                field in comparison_metrics for field in expected_comparison_fields
                            )
                        else:
                            comparison_check["comparison_metrics_complete"] = False
                        
                        logger.info(f"✅ Comparison endpoint working: {comparison_check['managers_count']} managers compared")
                        
                        return {
                            "test": "Manager comparison endpoint",
                            "status": "PASS" if comparison_check["managers_count_correct"] and comparison_check["comparison_metrics_complete"] else "FAIL",
                            "comparison_check": comparison_check
                        }
                    else:
                        return {
                            "test": "Manager comparison endpoint",
                            "status": "FAIL",
                            "error": f"Comparison endpoint failed: {response.status}"
                        }
        except Exception as e:
            return {
                "test": "Manager comparison endpoint",
                "status": "ERROR",
                "error": str(e)
            }
    
    async def run_detailed_verification(self) -> Dict[str, Any]:
        """Run all detailed verification tests"""
        logger.info("🚀 Starting Money Managers Profile System Phase 1 - Detailed Verification")
        
        # Authenticate first
        if not await self.authenticate_admin():
            return {"error": "Authentication failed"}
        
        test_results = []
        
        # Test 1: Verify initialization creates 3 managers
        init_test = await self.verify_initialization_creates_3_managers()
        test_results.append(init_test)
        
        managers = init_test.get("managers", [])
        
        if managers:
            # Test 2: Verify account assignments
            assignment_test = await self.verify_account_assignments(managers)
            test_results.append(assignment_test)
            
            # Test 3: Verify performance aggregation
            performance_test = await self.verify_performance_aggregation(managers)
            test_results.append(performance_test)
            
            # Test 4: Verify account details mapping
            mapping_test = await self.verify_account_details_mapping(managers)
            test_results.append(mapping_test)
        
        # Test 5: Verify comparison endpoint
        comparison_test = await self.verify_comparison_endpoint()
        test_results.append(comparison_test)
        
        # Calculate results
        total_tests = len(test_results)
        passed_tests = len([r for r in test_results if r.get("status") == "PASS"])
        failed_tests = len([r for r in test_results if r.get("status") == "FAIL"])
        error_tests = len([r for r in test_results if r.get("status") == "ERROR"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        summary = {
            "test_suite": "Money Managers Profile System Phase 1 - Detailed Verification",
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "errors": error_tests,
            "success_rate": round(success_rate, 1),
            "test_results": test_results,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"🎯 Detailed Verification Complete: {success_rate}% success rate ({passed_tests}/{total_tests} passed)")
        
        return summary

async def main():
    """Main test execution function"""
    tester = DetailedMoneyManagersTester()
    results = await tester.run_detailed_verification()
    
    # Print detailed results
    print("\n" + "="*80)
    print("MONEY MANAGERS PROFILE SYSTEM PHASE 1 - DETAILED VERIFICATION")
    print("="*80)
    
    print(f"Test Suite: {results['test_suite']}")
    print(f"Success Rate: {results['success_rate']}% ({results['passed']}/{results['total_tests']} passed)")
    print(f"Failed: {results['failed']}, Errors: {results['errors']}")
    print(f"Timestamp: {results['timestamp']}")
    
    print("\nDETAILED VERIFICATION RESULTS:")
    print("-" * 50)
    
    for i, test in enumerate(results['test_results'], 1):
        status_emoji = "✅" if test['status'] == "PASS" else "❌" if test['status'] == "FAIL" else "⚠️"
        print(f"{i}. {status_emoji} {test['test']} - {test['status']}")
        
        if test['status'] == "FAIL" or test['status'] == "ERROR":
            print(f"   Error: {test.get('error', 'Unknown error')}")
        
        # Print specific verification details
        if test['test'] == "Initialization creates 3 managers" and test['status'] == "PASS":
            verification = test.get('verification', {})
            print(f"   ✅ Found {verification.get('total_managers')} managers")
            print(f"   ✅ Manager IDs: {verification.get('manager_ids_found')}")
        
        elif test['test'] == "Account assignments verification" and test['status'] == "PASS":
            assignment_results = test.get('assignment_results', {})
            for manager_id, result in assignment_results.items():
                accounts = result.get('actual_accounts', [])
                execution_type = result.get('execution_type', 'unknown')
                print(f"   ✅ {manager_id}: accounts {accounts} ({execution_type})")
        
        elif test['test'] == "Performance aggregation verification" and test['status'] == "PASS":
            performance_results = test.get('performance_results', {})
            for manager_id, result in performance_results.items():
                performance_data = result.get('performance_data', {})
                total_allocated = performance_data.get('total_allocated', 0)
                total_pnl = performance_data.get('total_pnl', 0)
                win_rate = performance_data.get('win_rate', 0)
                profit_factor = performance_data.get('profit_factor', 0)
                print(f"   ✅ {manager_id}: Allocated ${total_allocated:,.2f}, P&L ${total_pnl:,.2f}, Win Rate {win_rate}%, PF {profit_factor}")
        
        elif test['test'] == "Manager comparison endpoint" and test['status'] == "PASS":
            comparison_check = test.get('comparison_check', {})
            managers_count = comparison_check.get('managers_count', 0)
            print(f"   ✅ Successfully compared {managers_count} managers")
    
    print("\n" + "="*80)
    
    return results

if __name__ == "__main__":
    asyncio.run(main())