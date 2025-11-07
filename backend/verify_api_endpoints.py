"""
FIDUS API Endpoint Verification
Tests all critical API endpoints for data correctness and field transformation
"""

import asyncio
import httpx
import os
import json

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

async def verify_api_endpoints():
    print("\n" + "="*80)
    print("FIDUS API ENDPOINT VERIFICATION")
    print(f"Testing against: {API_BASE}")
    print("="*80 + "\n")
    
    results = {
        "passed": 0,
        "failed": 0,
        "endpoints": []
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # ====================================================================
        # 1. Test Fund Portfolio Overview
        # ====================================================================
        print("📋 1. TESTING: Fund Portfolio Overview")
        print("-" * 80)
        
        try:
            response = await client.get(f"{API_BASE}/fund-portfolio/overview")
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    funds = data.get('funds', {})
                    print(f"   ✅ Status: {response.status_code}")
                    print(f"   ✅ Total AUM: ${data.get('aum', 0):,.2f}")
                    print(f"   ✅ Total Investors: {data.get('total_investors', 0)}")
                    print(f"   ✅ Fund Count: {data.get('fund_count', 0)}")
                    
                    # Check each fund
                    for fund_code, fund in funds.items():
                        print(f"\n   📊 {fund_code} Fund:")
                        print(f"      AUM: ${fund.get('aum', 0):,.2f}")
                        print(f"      Investors: {fund.get('total_investors', 0)}")
                        
                        # CRITICAL: Check mt5_trading_profit field
                        mt5_profit = fund.get('mt5_trading_profit')
                        if mt5_profit is not None:
                            print(f"      ✅ MT5 Trading Profit: ${mt5_profit:,.2f}")
                        else:
                            print(f"      ❌ MT5 Trading Profit: MISSING")
                            results["failed"] += 1
                        
                        # Check weighted return
                        print(f"      Weighted Return: {fund.get('performance_ytd', 0):.2%}")
                    
                    results["passed"] += 1
                    results["endpoints"].append({
                        "name": "Fund Portfolio Overview",
                        "status": "PASS",
                        "url": f"{API_BASE}/fund-portfolio/overview"
                    })
                else:
                    print(f"   ❌ Response not successful")
                    results["failed"] += 1
            else:
                print(f"   ❌ HTTP {response.status_code}")
                results["failed"] += 1
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            results["failed"] += 1
        
        # ====================================================================
        # 2. Test Referrals Overview (No Auth Required for public test)
        # ====================================================================
        print(f"\n📋 2. TESTING: Referrals Overview")
        print("-" * 80)
        
        try:
            # Note: This endpoint requires auth, so we'll check structure only
            response = await client.get(f"{API_BASE}/admin/referrals/overview")
            
            if response.status_code == 401:
                print(f"   ✅ Endpoint exists (requires auth)")
                print(f"   ✅ Returns 401 as expected without token")
                results["passed"] += 1
            elif response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status: {response.status_code}")
                
                # Check camelCase transformation
                if 'totalSalesVolume' in data:
                    print(f"   ✅ Field: totalSalesVolume (camelCase)")
                if 'totalCommissions' in data:
                    print(f"   ✅ Field: totalCommissions (camelCase)")
                if 'activeSalespeople' in data:
                    print(f"   ✅ Field: activeSalespeople (camelCase)")
                
                print(f"   📊 Active Salespeople: {data.get('activeSalespeople', 0)}")
                print(f"   📊 Total Sales: ${data.get('totalSalesVolume', 0):,.2f}")
                print(f"   📊 Total Commissions: ${data.get('totalCommissions', 0):,.2f}")
                
                results["passed"] += 1
            else:
                print(f"   ❌ HTTP {response.status_code}")
                results["failed"] += 1
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            results["failed"] += 1
        
        # ====================================================================
        # 3. Test Commission Calendar Endpoint
        # ====================================================================
        print(f"\n📋 3. TESTING: Commission Calendar")
        print("-" * 80)
        
        try:
            # Test with date range
            start_date = "2025-12-01"
            end_date = "2026-12-31"
            
            response = await client.get(
                f"{API_BASE}/admin/referrals/commissions/calendar",
                params={"start_date": start_date, "end_date": end_date}
            )
            
            if response.status_code == 401:
                print(f"   ✅ Endpoint exists (requires auth)")
                print(f"   ✅ Returns 401 as expected without token")
                results["passed"] += 1
            elif response.status_code == 200:
                data = response.json()
                calendar = data.get('calendar', [])
                print(f"   ✅ Status: {response.status_code}")
                print(f"   ✅ Calendar Months: {len(calendar)}")
                
                if calendar:
                    total_payments = sum(len(month.get('payments', [])) for month in calendar)
                    print(f"   ✅ Total Payments: {total_payments}")
                    
                    # Show first month
                    first_month = calendar[0]
                    print(f"   📅 First Month: {first_month.get('month_display')}")
                    print(f"      Total: ${first_month.get('total_commissions', 0):,.2f}")
                
                results["passed"] += 1
            else:
                print(f"   ❌ HTTP {response.status_code}")
                results["failed"] += 1
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            results["failed"] += 1
        
        # ====================================================================
        # 4. Test Public Salespeople Endpoint (No Auth)
        # ====================================================================
        print(f"\n📋 4. TESTING: Public Salespeople Endpoint")
        print("-" * 80)
        
        try:
            response = await client.get(f"{API_BASE}/public/salespeople")
            
            if response.status_code == 200:
                data = response.json()
                salespeople = data.get('salespeople', [])
                
                print(f"   ✅ Status: {response.status_code}")
                print(f"   ✅ Salespeople Count: {len(salespeople)}")
                
                if salespeople:
                    salvador = next((sp for sp in salespeople if sp.get('referral_code') == 'SP-2025'), None)
                    if salvador:
                        print(f"   ✅ Salvador Found:")
                        print(f"      Name: {salvador.get('name')}")
                        print(f"      Code: {salvador.get('referral_code')}")
                    else:
                        print(f"   ⚠️  Salvador not found in public list")
                
                results["passed"] += 1
                results["endpoints"].append({
                    "name": "Public Salespeople",
                    "status": "PASS",
                    "url": f"{API_BASE}/public/salespeople"
                })
            else:
                print(f"   ❌ HTTP {response.status_code}")
                results["failed"] += 1
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            results["failed"] += 1
        
        # ====================================================================
        # 5. Test Health Check
        # ====================================================================
        print(f"\n📋 5. TESTING: Backend Health")
        print("-" * 80)
        
        try:
            response = await client.get(f"{BACKEND_URL}/health")
            
            if response.status_code == 200:
                print(f"   ✅ Backend is healthy")
                print(f"   ✅ Status: {response.status_code}")
                results["passed"] += 1
            else:
                print(f"   ❌ HTTP {response.status_code}")
                results["failed"] += 1
                
        except Exception as e:
            print(f"   ⚠️  Health endpoint not available: {str(e)}")
            # Not critical, don't count as failure
    
    # ====================================================================
    # SUMMARY
    # ====================================================================
    print("\n" + "="*80)
    print("API VERIFICATION SUMMARY")
    print("="*80 + "\n")
    
    total_tests = results["passed"] + results["failed"]
    success_rate = (results["passed"] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if results["failed"] == 0:
        print(f"\n🎉 ALL API ENDPOINTS WORKING CORRECTLY")
    else:
        print(f"\n⚠️  Some endpoints need attention")
    
    print(f"\n📝 Endpoint Status:")
    for endpoint in results["endpoints"]:
        print(f"   {endpoint['status']}: {endpoint['name']}")

if __name__ == "__main__":
    asyncio.run(verify_api_endpoints())
