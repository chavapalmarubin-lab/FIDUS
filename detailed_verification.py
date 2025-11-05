#!/usr/bin/env python3
"""
Detailed verification of the Money Managers Critical Data Integrity Fix
"""

import asyncio
import aiohttp
import json

async def detailed_verification():
    # Authenticate
    async with aiohttp.ClientSession() as session:
        # Login
        async with session.post(
            "https://fidus-integration-1.preview.emergentagent.com/api/auth/login",
            json={"username": "admin", "password": "password123", "user_type": "admin"}
        ) as response:
            if response.status == 200:
                data = await response.json()
                token = data.get("token")
                
                # Get managers
                headers = {"Authorization": f"Bearer {token}"}
                async with session.get(
                    "https://fidus-integration-1.preview.emergentagent.com/api/admin/money-managers",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        managers = data.get("managers", [])
                        
                        print("🎯 CRITICAL DATA INTEGRITY FIX VERIFICATION RESULTS")
                        print("="*60)
                        
                        # Requirement 1: Exactly 4 managers
                        manager_count_ok = len(managers) == 4
                        status1 = "✅" if manager_count_ok else "❌"
                        print(f"1. Manager Count: {len(managers)} (Expected: 4) {status1}")
                        
                        # Requirement 2: 1:1 mapping verification
                        print("\n2. 1:1 Account Mapping Verification:")
                        all_1to1 = True
                        for manager in managers:
                            name = manager.get("name", "Unknown")
                            accounts = manager.get("assigned_accounts", [])
                            count = len(accounts)
                            status = "✅" if count == 1 else "❌"
                            if count != 1:
                                all_1to1 = False
                            print(f"   {name}: {count} account(s) {accounts} {status}")
                        
                        status2 = "✅ PASS" if all_1to1 else "❌ FAIL"
                        print(f"   Overall 1:1 Mapping: {status2}")
                        
                        # Requirement 3: Specific mappings
                        expected_mappings = {
                            "CP Strategy": [885822],
                            "TradingHub Gold": [886557], 
                            "GoldenTrade": [886066],
                            "UNO14": [886602]
                        }
                        
                        print("\n3. Specific Manager-Account Mappings:")
                        all_mappings_correct = True
                        for manager in managers:
                            name = manager.get("name", "Unknown")
                            accounts = manager.get("assigned_accounts", [])
                            expected = expected_mappings.get(name, [])
                            correct = accounts == expected
                            if not correct:
                                all_mappings_correct = False
                            status = "✅" if correct else "❌"
                            print(f"   {name} → {accounts} (Expected: {expected}) {status}")
                        
                        status3 = "✅ PASS" if all_mappings_correct else "❌ FAIL"
                        print(f"   Overall Mappings: {status3}")
                        
                        # Requirement 4: Profile URLs
                        expected_profiles = {
                            "CP Strategy": "https://ratings.mexatlantic.com/widgets/ratings/3157?widgetKey=social_platform_ratings",
                            "TradingHub Gold": None,
                            "GoldenTrade": "https://ratings.mexatlantic.com/widgets/ratings/5843?widgetKey=social_platform_ratings",
                            "UNO14": None
                        }
                        
                        print("\n4. Profile URL Verification:")
                        all_profiles_correct = True
                        for manager in managers:
                            name = manager.get("name", "Unknown")
                            profile_url = manager.get("profile_url")
                            expected = expected_profiles.get(name)
                            correct = profile_url == expected
                            if not correct:
                                all_profiles_correct = False
                            status = "✅" if correct else "❌"
                            profile_display = "null" if profile_url is None else "MexAtlantic URL"
                            expected_display = "null (pending)" if expected is None else "MexAtlantic URL"
                            print(f"   {name}: {profile_display} (Expected: {expected_display}) {status}")
                        
                        status4 = "✅ PASS" if all_profiles_correct else "❌ FAIL"
                        print(f"   Overall Profile URLs: {status4}")
                        
                        # Requirement 5: Account allocations
                        expected_allocations = {
                            885822: 18151.41,  # CORE Fund
                            886557: 80000.00,  # BALANCE Fund
                            886066: 10000.00,  # BALANCE Fund
                            886602: 10000.00   # BALANCE Fund
                        }
                        
                        print("\n5. Account Allocation Verification:")
                        all_allocations_correct = True
                        for manager in managers:
                            name = manager.get("name", "Unknown")
                            account_details = manager.get("account_details", [])
                            for account in account_details:
                                acc_num = account.get("account")
                                allocation = account.get("allocation", 0)
                                expected = expected_allocations.get(acc_num, 0)
                                correct = abs(allocation - expected) < 0.01
                                if not correct:
                                    all_allocations_correct = False
                                status = "✅" if correct else "❌"
                                fund_type = "CORE" if acc_num == 885822 else "BALANCE"
                                print(f"   Account {acc_num}: ${allocation:,.2f} ({fund_type} Fund) (Expected: ${expected:,.2f}) {status}")
                        
                        status5 = "✅ PASS" if all_allocations_correct else "❌ FAIL"
                        print(f"   Overall Allocations: {status5}")
                        
                        # Final result
                        overall_success = all([
                            manager_count_ok,
                            all_1to1,
                            all_mappings_correct,
                            all_profiles_correct,
                            all_allocations_correct
                        ])
                        
                        print("\n" + "="*60)
                        final_status = "✅ 100% SUCCESS - CRITICAL FIX VERIFIED" if overall_success else "❌ FAILED - ISSUES FOUND"
                        print(f"🎯 OVERALL RESULT: {final_status}")
                        print("="*60)
                        
                    else:
                        print(f"Failed to get managers: {response.status}")
            else:
                print(f"Failed to login: {response.status}")

if __name__ == "__main__":
    asyncio.run(detailed_verification())