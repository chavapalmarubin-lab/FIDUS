#!/usr/bin/env python3
"""
Money Managers Profile System Phase 1 Backend Testing

Tests the complete Money Managers Profile System implementation including:
- Money Managers API endpoints
- Manager configuration and initialization
- Performance calculation across assigned accounts
- Database collections and indexes
- Manager comparison functionality

Test Coverage:
1. GET /api/admin/money-managers - Get all managers with performance
2. GET /api/admin/money-managers/{manager_id} - Get specific manager details
3. GET /api/admin/money-managers/compare - Compare multiple managers
4. POST /api/admin/money-managers/initialize - Initialize default managers
5. Manager Configuration Testing (3 managers with correct account assignments)
6. Performance Calculation Testing
7. Database Collections Testing
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

class MoneyManagersBackendTester:
    """Comprehensive Money Managers Profile System Backend Tester"""
    
    def __init__(self):
        # Use the correct backend URL from frontend/.env
        self.base_url = "https://referral-tracker-9.preview.emergentagent.com"
        self.api_base = f"{self.base_url}/api"
        
        # Test credentials
        self.admin_credentials = {
            "username": "admin",
            "password": "password123",
            "user_type": "admin"
        }
        
        self.jwt_token = None
        self.test_results = []
        
        # Expected manager configurations after CRITICAL DATA INTEGRITY FIX
        # NOW: 4 managers with 1:1 account mapping (not 1:N)
        self.expected_managers = {
            "manager_cp_strategy": {
                "name": "CP Strategy",
                "assigned_accounts": [885822],  # ONLY 1 account (1:1 mapping)
                "profile_url": "https://ratings.mexatlantic.com/widgets/ratings/3157?widgetKey=social_platform_ratings",  # Has profile URL
                "fund": "CORE"
            },
            "manager_tradinghub_gold": {
                "name": "TradingHub Gold", 
                "assigned_accounts": [886557],  # ONLY 1 account (1:1 mapping)
                "profile_url": None,  # Should be null (pending)
                "fund": "BALANCE"
            },
            "manager_goldentrade": {
                "name": "GoldenTrade",
                "assigned_accounts": [886066],  # ONLY 1 account (1:1 mapping)
                "profile_url": "https://ratings.mexatlantic.com/widgets/ratings/5843?widgetKey=social_platform_ratings",  # Has profile URL
                "fund": "BALANCE"
            },
            "manager_uno14": {
                "name": "UNO14",
                "assigned_accounts": [886602],  # ONLY 1 account (1:1 mapping)
                "profile_url": None,  # Should be null (pending)
                "fund": "BALANCE"
            }
        }
        
        # Expected account allocations after fix
        self.expected_allocations = {
            885822: {"fund": "CORE", "allocation": 18151.41},
            886557: {"fund": "BALANCE", "allocation": 80000},
            886066: {"fund": "BALANCE", "allocation": 10000},
            886602: {"fund": "BALANCE", "allocation": 10000}
        }
    
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
                        error_text = await response.text()
                        logger.error(f"❌ Admin authentication failed: {response.status} - {error_text}")
                        return False
        except Exception as e:
            logger.error(f"❌ Authentication error: {str(e)}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers with JWT token"""
        if not self.jwt_token:
            raise ValueError("No JWT token available. Please authenticate first.")
        return {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json"
        }
    
    async def test_initialize_money_managers(self) -> Dict[str, Any]:
        """Test POST /api/admin/money-managers/initialize endpoint"""
        test_name = "Initialize Money Managers"
        logger.info(f"🧪 Testing: {test_name}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/admin/money-managers/initialize",
                    headers=self.get_auth_headers()
                ) as response:
                    status = response.status
                    data = await response.json()
                    
                    if status == 200:
                        success = data.get("success", False)
                        managers_created = data.get("managers_created", 0)
                        action = data.get("action", "unknown")
                        
                        logger.info(f"✅ Initialize endpoint working: {action}, created: {managers_created}")
                        
                        return {
                            "test": test_name,
                            "status": "PASS",
                            "response_code": status,
                            "success": success,
                            "managers_created": managers_created,
                            "action": action,
                            "details": data
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Initialize failed: {status} - {error_text}")
                        
                        return {
                            "test": test_name,
                            "status": "FAIL",
                            "response_code": status,
                            "error": error_text
                        }
                        
        except Exception as e:
            logger.error(f"❌ Initialize test error: {str(e)}")
            return {
                "test": test_name,
                "status": "ERROR",
                "error": str(e)
            }
    
    async def test_get_all_money_managers(self) -> Dict[str, Any]:
        """Test GET /api/admin/money-managers endpoint"""
        test_name = "Get All Money Managers"
        logger.info(f"🧪 Testing: {test_name}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base}/admin/money-managers",
                    headers=self.get_auth_headers()
                ) as response:
                    status = response.status
                    data = await response.json()
                    
                    if status == 200:
                        managers = data.get("managers", [])
                        total_count = len(managers)
                        
                        logger.info(f"✅ Get all managers working: {total_count} managers found")
                        
                        # Verify expected managers exist
                        found_managers = {m["manager_id"]: m for m in managers}
                        verification_results = {}
                        
                        for expected_id, expected_config in self.expected_managers.items():
                            if expected_id in found_managers:
                                manager = found_managers[expected_id]
                                verification_results[expected_id] = {
                                    "found": True,
                                    "name_match": manager.get("name") == expected_config["name"],
                                    "accounts_match": set(manager.get("assigned_accounts", [])) == set(expected_config["assigned_accounts"]),
                                    "has_performance": "performance" in manager,
                                    "has_account_details": "account_details" in manager
                                }
                            else:
                                verification_results[expected_id] = {"found": False}
                        
                        return {
                            "test": test_name,
                            "status": "PASS",
                            "response_code": status,
                            "total_managers": total_count,
                            "managers": managers,
                            "verification": verification_results
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Get all managers failed: {status} - {error_text}")
                        
                        return {
                            "test": test_name,
                            "status": "FAIL",
                            "response_code": status,
                            "error": error_text
                        }
                        
        except Exception as e:
            logger.error(f"❌ Get all managers test error: {str(e)}")
            return {
                "test": test_name,
                "status": "ERROR",
                "error": str(e)
            }
    
    async def test_get_specific_manager(self, manager_id: str) -> Dict[str, Any]:
        """Test GET /api/admin/money-managers/{manager_id} endpoint"""
        test_name = f"Get Specific Manager ({manager_id})"
        logger.info(f"🧪 Testing: {test_name}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base}/admin/money-managers/{manager_id}",
                    headers=self.get_auth_headers()
                ) as response:
                    status = response.status
                    data = await response.json()
                    
                    if status == 200:
                        manager = data.get("manager")
                        
                        if manager:
                            logger.info(f"✅ Get specific manager working: {manager.get('name', 'Unknown')}")
                            
                            # Verify manager details
                            verification = {
                                "has_manager_id": "manager_id" in manager,
                                "has_performance": "performance" in manager,
                                "has_account_details": "account_details" in manager,
                                "has_recent_trades": "recent_trades" in manager,
                                "performance_metrics_complete": False
                            }
                            
                            if "performance" in manager:
                                perf = manager["performance"]
                                required_metrics = [
                                    "total_allocated", "total_pnl", "win_rate", 
                                    "profit_factor", "total_trades"
                                ]
                                verification["performance_metrics_complete"] = all(
                                    metric in perf for metric in required_metrics
                                )
                            
                            return {
                                "test": test_name,
                                "status": "PASS",
                                "response_code": status,
                                "manager": manager,
                                "verification": verification
                            }
                        else:
                            logger.error(f"❌ Manager not found: {manager_id}")
                            return {
                                "test": test_name,
                                "status": "FAIL",
                                "response_code": status,
                                "error": "Manager not found in response"
                            }
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Get specific manager failed: {status} - {error_text}")
                        
                        return {
                            "test": test_name,
                            "status": "FAIL",
                            "response_code": status,
                            "error": error_text
                        }
                        
        except Exception as e:
            logger.error(f"❌ Get specific manager test error: {str(e)}")
            return {
                "test": test_name,
                "status": "ERROR",
                "error": str(e)
            }
    
    async def test_compare_managers(self, manager_ids: List[str]) -> Dict[str, Any]:
        """Test GET /api/admin/money-managers/compare endpoint"""
        test_name = "Compare Money Managers"
        logger.info(f"🧪 Testing: {test_name}")
        
        try:
            manager_ids_param = ",".join(manager_ids)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base}/admin/money-managers/compare?manager_ids={manager_ids_param}",
                    headers=self.get_auth_headers()
                ) as response:
                    status = response.status
                    data = await response.json()
                    
                    if status == 200:
                        managers = data.get("managers", [])
                        comparison_metrics = data.get("comparison_metrics", {})
                        
                        logger.info(f"✅ Compare managers working: {len(managers)} managers compared")
                        
                        # Verify comparison structure
                        verification = {
                            "has_managers": len(managers) > 0,
                            "has_comparison_metrics": len(comparison_metrics) > 0,
                            "managers_count_match": len(managers) == len(manager_ids),
                            "has_aggregated_metrics": False
                        }
                        
                        if comparison_metrics:
                            required_comparison_metrics = [
                                "total_allocated", "total_pnl", "avg_win_rate", "avg_profit_factor"
                            ]
                            verification["has_aggregated_metrics"] = all(
                                metric in comparison_metrics for metric in required_comparison_metrics
                            )
                        
                        return {
                            "test": test_name,
                            "status": "PASS",
                            "response_code": status,
                            "managers_compared": len(managers),
                            "comparison_metrics": comparison_metrics,
                            "verification": verification
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Compare managers failed: {status} - {error_text}")
                        
                        return {
                            "test": test_name,
                            "status": "FAIL",
                            "response_code": status,
                            "error": error_text
                        }
                        
        except Exception as e:
            logger.error(f"❌ Compare managers test error: {str(e)}")
            return {
                "test": test_name,
                "status": "ERROR",
                "error": str(e)
            }
    
    async def test_manager_configuration(self, managers_data: List[Dict]) -> Dict[str, Any]:
        """Test manager configuration against Phase 1 requirements"""
        test_name = "Manager Configuration Verification"
        logger.info(f"🧪 Testing: {test_name}")
        
        try:
            configuration_results = {}
            
            for manager in managers_data:
                manager_id = manager.get("manager_id")
                if manager_id in self.expected_managers:
                    expected = self.expected_managers[manager_id]
                    
                    config_check = {
                        "manager_exists": True,
                        "name_correct": manager.get("name") == expected["name"],
                        "accounts_correct": set(manager.get("assigned_accounts", [])) == set(expected["assigned_accounts"]),
                        "has_strategy_info": any(key in manager for key in ["strategy_name", "strategy_description", "risk_profile"]),
                        "status_active": manager.get("status", "active") == "active"
                    }
                    
                    configuration_results[manager_id] = config_check
            
            # Check if all expected managers are configured
            all_managers_found = all(
                manager_id in configuration_results 
                for manager_id in self.expected_managers.keys()
            )
            
            # Check account assignments
            account_assignment_check = {}
            for manager in managers_data:
                for account in manager.get("assigned_accounts", []):
                    if account in self.expected_allocations:
                        account_assignment_check[account] = {
                            "assigned_to": manager.get("manager_id"),
                            "expected_fund": self.expected_allocations[account]["fund"],
                            "expected_allocation": self.expected_allocations[account]["allocation"]
                        }
            
            logger.info(f"✅ Manager configuration check completed")
            
            return {
                "test": test_name,
                "status": "PASS",
                "all_managers_found": all_managers_found,
                "configuration_results": configuration_results,
                "account_assignments": account_assignment_check,
                "total_managers_configured": len(configuration_results)
            }
            
        except Exception as e:
            logger.error(f"❌ Manager configuration test error: {str(e)}")
            return {
                "test": test_name,
                "status": "ERROR",
                "error": str(e)
            }
    
    async def test_critical_data_integrity_fix(self, managers_data: List[Dict]) -> Dict[str, Any]:
        """Test CRITICAL DATA INTEGRITY FIX: 4 managers with 1:1 account mapping"""
        test_name = "CRITICAL Data Integrity Fix Verification"
        logger.info(f"🧪 Testing: {test_name}")
        
        try:
            # CRITICAL REQUIREMENT 1: Exactly 4 managers
            manager_count = len(managers_data)
            exactly_4_managers = manager_count == 4
            
            # CRITICAL REQUIREMENT 2: Each manager has ONLY 1 assigned account (1:1 mapping)
            one_to_one_mapping = True
            mapping_violations = []
            
            for manager in managers_data:
                manager_name = manager.get("name", "Unknown")
                assigned_accounts = manager.get("assigned_accounts", [])
                account_count = len(assigned_accounts)
                
                if account_count != 1:
                    one_to_one_mapping = False
                    mapping_violations.append({
                        "manager": manager_name,
                        "account_count": account_count,
                        "accounts": assigned_accounts,
                        "violation": f"Has {account_count} accounts instead of 1"
                    })
            
            # CRITICAL REQUIREMENT 3: Verify specific manager-account mappings
            manager_account_verification = {}
            for manager in managers_data:
                manager_id = manager.get("manager_id", "Unknown")
                manager_name = manager.get("name", "Unknown")
                assigned_accounts = manager.get("assigned_accounts", [])
                
                if manager_id in self.expected_managers:
                    expected_accounts = self.expected_managers[manager_id]["assigned_accounts"]
                    accounts_match = set(assigned_accounts) == set(expected_accounts)
                    
                    manager_account_verification[manager_name] = {
                        "found": True,
                        "manager_id": manager_id,
                        "expected_accounts": expected_accounts,
                        "actual_accounts": assigned_accounts,
                        "accounts_match": accounts_match,
                        "account_count": len(assigned_accounts)
                    }
                else:
                    manager_account_verification[manager_name] = {
                        "found": False,
                        "manager_id": manager_id,
                        "unexpected_manager": True
                    }
            
            # CRITICAL REQUIREMENT 4: Verify profile URLs
            profile_url_verification = {}
            for manager in managers_data:
                manager_id = manager.get("manager_id", "Unknown")
                manager_name = manager.get("name", "Unknown")
                profile_url = manager.get("profile_url")
                
                if manager_id in self.expected_managers:
                    expected_profile = self.expected_managers[manager_id]["profile_url"]
                    profile_matches = profile_url == expected_profile
                    
                    profile_url_verification[manager_name] = {
                        "expected": expected_profile,
                        "actual": profile_url,
                        "matches": profile_matches
                    }
            
            # CRITICAL REQUIREMENT 5: Verify account allocation amounts
            allocation_verification = {}
            for manager in managers_data:
                manager_name = manager.get("name", "Unknown")
                account_details = manager.get("account_details", [])
                
                for account_detail in account_details:
                    account_number = account_detail.get("account")
                    allocation = account_detail.get("allocation")
                    
                    if account_number in self.expected_allocations:
                        expected_allocation = self.expected_allocations[account_number]["allocation"]
                        allocation_matches = abs(allocation - expected_allocation) < 0.01  # Allow small floating point differences
                        
                        allocation_verification[account_number] = {
                            "manager": manager_name,
                            "expected_allocation": expected_allocation,
                            "actual_allocation": allocation,
                            "matches": allocation_matches,
                            "fund": self.expected_allocations[account_number]["fund"]
                        }
            
            # Calculate overall success
            all_requirements_met = (
                exactly_4_managers and 
                one_to_one_mapping and
                all(v["accounts_match"] for v in manager_account_verification.values() if v.get("found")) and
                all(v["matches"] for v in profile_url_verification.values()) and
                all(v["matches"] for v in allocation_verification.values())
            )
            
            logger.info(f"✅ Critical data integrity fix verification completed")
            
            return {
                "test": test_name,
                "status": "PASS" if all_requirements_met else "FAIL",
                "critical_requirements": {
                    "exactly_4_managers": exactly_4_managers,
                    "one_to_one_mapping": one_to_one_mapping,
                    "all_mappings_correct": all(v["accounts_match"] for v in manager_account_verification.values() if v.get("found")),
                    "all_profiles_correct": all(v["matches"] for v in profile_url_verification.values()),
                    "all_allocations_correct": all(v["matches"] for v in allocation_verification.values())
                },
                "manager_count": manager_count,
                "mapping_violations": mapping_violations,
                "manager_account_verification": manager_account_verification,
                "profile_url_verification": profile_url_verification,
                "allocation_verification": allocation_verification,
                "overall_success": all_requirements_met
            }
            
        except Exception as e:
            logger.error(f"❌ Critical data integrity test error: {str(e)}")
            return {
                "test": test_name,
                "status": "ERROR",
                "error": str(e)
            }

    async def test_performance_calculation(self, managers_data: List[Dict]) -> Dict[str, Any]:
        """Test performance calculation across assigned accounts"""
        test_name = "Performance Calculation Testing"
        logger.info(f"🧪 Testing: {test_name}")
        
        try:
            performance_results = {}
            
            for manager in managers_data:
                manager_id = manager.get("manager_id")
                performance = manager.get("performance", {})
                account_details = manager.get("account_details", [])
                
                perf_check = {
                    "has_performance_data": len(performance) > 0,
                    "has_total_allocated": "total_allocated" in performance,
                    "has_total_pnl": "total_pnl" in performance,
                    "has_win_rate": "win_rate" in performance,
                    "has_profit_factor": "profit_factor" in performance,
                    "has_account_details": len(account_details) > 0,
                    "performance_metrics_valid": False,
                    "account_details_complete": False
                }
                
                # Validate performance metrics
                if performance:
                    required_metrics = [
                        "total_allocated", "total_pnl", "win_rate", "profit_factor",
                        "total_trades", "winning_trades", "losing_trades"
                    ]
                    perf_check["performance_metrics_valid"] = all(
                        metric in performance for metric in required_metrics
                    )
                
                # Validate account details
                if account_details:
                    account_fields_complete = all(
                        all(field in account for field in ["account", "allocation", "current_equity", "pnl"])
                        for account in account_details
                    )
                    perf_check["account_details_complete"] = account_fields_complete
                
                performance_results[manager_id] = perf_check
            
            logger.info(f"✅ Performance calculation check completed")
            
            return {
                "test": test_name,
                "status": "PASS",
                "performance_results": performance_results,
                "managers_with_performance": len([r for r in performance_results.values() if r["has_performance_data"]]),
                "managers_with_valid_metrics": len([r for r in performance_results.values() if r["performance_metrics_valid"]])
            }
            
        except Exception as e:
            logger.error(f"❌ Performance calculation test error: {str(e)}")
            return {
                "test": test_name,
                "status": "ERROR",
                "error": str(e)
            }
    
    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all Money Managers Profile System tests"""
        logger.info("🚀 Starting Money Managers Profile System Phase 1 Testing")
        
        # Authenticate first
        if not await self.authenticate_admin():
            return {"error": "Authentication failed"}
        
        test_results = []
        
        # Test 1: Initialize Money Managers
        init_result = await self.test_initialize_money_managers()
        test_results.append(init_result)
        
        # Test 2: Get All Money Managers
        all_managers_result = await self.test_get_all_money_managers()
        test_results.append(all_managers_result)
        
        managers_data = all_managers_result.get("managers", [])
        
        # Test 3: Get Specific Managers
        for manager_id in self.expected_managers.keys():
            specific_result = await self.test_get_specific_manager(manager_id)
            test_results.append(specific_result)
        
        # Test 4: Compare Managers
        manager_ids_list = list(self.expected_managers.keys())
        compare_result = await self.test_compare_managers(manager_ids_list)
        test_results.append(compare_result)
        
        # Test 5: CRITICAL Data Integrity Fix Verification
        if managers_data:
            critical_result = await self.test_critical_data_integrity_fix(managers_data)
            test_results.append(critical_result)
        
        # Test 6: Manager Configuration Verification
        if managers_data:
            config_result = await self.test_manager_configuration(managers_data)
            test_results.append(config_result)
        
        # Test 7: Performance Calculation Testing
        if managers_data:
            perf_result = await self.test_performance_calculation(managers_data)
            test_results.append(perf_result)
        
        # Calculate overall results
        total_tests = len(test_results)
        passed_tests = len([r for r in test_results if r.get("status") == "PASS"])
        failed_tests = len([r for r in test_results if r.get("status") == "FAIL"])
        error_tests = len([r for r in test_results if r.get("status") == "ERROR"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        summary = {
            "test_suite": "Money Managers Profile System Phase 1",
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "errors": error_tests,
            "success_rate": round(success_rate, 1),
            "test_results": test_results,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"🎯 Money Managers Testing Complete: {success_rate}% success rate ({passed_tests}/{total_tests} passed)")
        
        return summary

async def main():
    """Main test execution function"""
    tester = MoneyManagersBackendTester()
    results = await tester.run_comprehensive_tests()
    
    # Print detailed results
    print("\n" + "="*80)
    print("MONEY MANAGERS PROFILE SYSTEM PHASE 1 - TEST RESULTS")
    print("="*80)
    
    print(f"Test Suite: {results['test_suite']}")
    print(f"Success Rate: {results['success_rate']}% ({results['passed']}/{results['total_tests']} passed)")
    print(f"Failed: {results['failed']}, Errors: {results['errors']}")
    print(f"Timestamp: {results['timestamp']}")
    
    print("\nDETAILED TEST RESULTS:")
    print("-" * 50)
    
    for i, test in enumerate(results['test_results'], 1):
        status_emoji = "✅" if test['status'] == "PASS" else "❌" if test['status'] == "FAIL" else "⚠️"
        print(f"{i}. {status_emoji} {test['test']} - {test['status']}")
        
        if test['status'] == "FAIL" or test['status'] == "ERROR":
            print(f"   Error: {test.get('error', 'Unknown error')}")
        elif test['test'] == "Get All Money Managers" and test['status'] == "PASS":
            print(f"   Found {test.get('total_managers', 0)} managers")
            verification = test.get('verification', {})
            for manager_id, verify_data in verification.items():
                if verify_data.get('found'):
                    print(f"   - {manager_id}: ✅ Found with performance data")
                else:
                    print(f"   - {manager_id}: ❌ Not found")
        elif test['test'] == "Compare Money Managers" and test['status'] == "PASS":
            print(f"   Compared {test.get('managers_compared', 0)} managers")
            metrics = test.get('comparison_metrics', {})
            if metrics:
                print(f"   Total Allocated: ${metrics.get('total_allocated', 0):,.2f}")
                print(f"   Total P&L: ${metrics.get('total_pnl', 0):,.2f}")
    
    print("\n" + "="*80)
    
    return results

if __name__ == "__main__":
    asyncio.run(main())