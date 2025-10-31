#!/usr/bin/env python3
"""
Test MT5 API connectivity for all Alejandro's accounts
Critical for business flow validation
"""
import requests
import json

BASE_URL = "https://fidus-invest.emergent.host"

def get_admin_token():
    login_data = {"username": "admin", "password": "password123", "user_type": "admin"}
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json().get("token")
    return None

def test_mt5_connection(token, mt5_login, server="MEXAtlantic-Real"):
    """Test MT5 API connection for a specific account"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test MT5 API endpoints
    endpoints_to_test = [
        f"/api/mt5/account/{mt5_login}/info",
        f"/api/mt5/account/{mt5_login}/balance", 
        f"/api/mt5/account/{mt5_login}/positions",
        f"/api/mt5/account/{mt5_login}/orders",
        f"/api/mt5/real-time-data/{mt5_login}"
    ]
    
    print(f"\n🔌 Testing MT5 Account: {mt5_login} (Server: {server})")
    print("-" * 50)
    
    connection_results = {"account": mt5_login, "tests": []}
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=10)
            
            test_result = {
                "endpoint": endpoint,
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "error": None if response.status_code == 200 else response.text[:200]
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    test_result["data_preview"] = str(data)[:100] + "..." if len(str(data)) > 100 else str(data)
                    print(f"  ✅ {endpoint.split('/')[-1]}: {test_result['data_preview']}")
                except:
                    test_result["data_preview"] = "Non-JSON response"
                    print(f"  ✅ {endpoint.split('/')[-1]}: Connected (non-JSON)")
            else:
                print(f"  ❌ {endpoint.split('/')[-1]}: {response.status_code} - {response.text[:50]}...")
                
            connection_results["tests"].append(test_result)
            
        except Exception as e:
            error_result = {
                "endpoint": endpoint,
                "status_code": None,
                "success": False,
                "error": str(e)
            }
            connection_results["tests"].append(error_result)
            print(f"  ⚠️ {endpoint.split('/')[-1]}: Connection error - {str(e)}")
    
    # Calculate success rate
    successful_tests = sum(1 for test in connection_results["tests"] if test["success"])
    success_rate = (successful_tests / len(connection_results["tests"])) * 100
    
    print(f"\n📊 MT5 Account {mt5_login} Results:")
    print(f"   Success Rate: {success_rate:.1f}% ({successful_tests}/{len(connection_results['tests'])} tests)")
    
    return connection_results, success_rate >= 80  # Consider 80%+ success rate as "working"

def main():
    print("⚡ MT5 API CONNECTIVITY TEST FOR ALEJANDRO'S INVESTMENTS")
    print("=" * 60)
    print("Testing real-time API data retrieval for business flow validation")
    
    token = get_admin_token()
    if not token:
        print("❌ Could not authenticate - cannot test MT5 connectivity")
        return
    
    print("✅ Authenticated successfully")
    
    # Alejandro's MT5 accounts as specified
    mt5_accounts = [
        {"login": "886557", "investment": "Investment 1", "amount": "$80,000", "fund": "BALANCE"},
        {"login": "886602", "investment": "Investment 2", "amount": "$10,000", "fund": "BALANCE"},
        {"login": "886066", "investment": "Investment 3", "amount": "$10,000", "fund": "BALANCE"},
        {"login": "885822", "investment": "Investment 4", "amount": "$18,151.41", "fund": "CORE"}
    ]
    
    print(f"\n🎯 Testing {len(mt5_accounts)} MT5 accounts:")
    for acc in mt5_accounts:
        print(f"   - {acc['investment']}: MT5 {acc['login']} → {acc['fund']} Fund ({acc['amount']})")
    
    overall_results = []
    working_accounts = 0
    
    for account_info in mt5_accounts:
        mt5_login = account_info["login"]
        connection_result, is_working = test_mt5_connection(token, mt5_login)
        
        overall_results.append({
            "investment": account_info["investment"],
            "mt5_login": mt5_login,
            "fund": account_info["fund"],
            "amount": account_info["amount"],
            "is_working": is_working,
            "connection_details": connection_result
        })
        
        if is_working:
            working_accounts += 1
            print(f"✅ {account_info['investment']} MT5 API: WORKING")
        else:
            print(f"❌ {account_info['investment']} MT5 API: ISSUES DETECTED")
    
    print(f"\n🏆 FINAL MT5 API CONNECTIVITY REPORT:")
    print("=" * 50)
    print(f"Working MT5 Accounts: {working_accounts}/{len(mt5_accounts)}")
    print(f"Business Flow Status: {'✅ OPERATIONAL' if working_accounts >= 3 else '⚠️ NEEDS ATTENTION'}")
    
    if working_accounts == len(mt5_accounts):
        print("\n🎉 ALL MT5 ACCOUNTS OPERATIONAL!")
        print("✅ Real-time API data retrieval: WORKING")
        print("✅ Business flow: FULLY FUNCTIONAL")
    elif working_accounts >= 3:
        print("\n⚠️ MOST MT5 ACCOUNTS WORKING")
        print("✅ Core business flow: OPERATIONAL")
        print("🔧 Some accounts may need attention")
    else:
        print("\n🚨 CRITICAL: MULTIPLE MT5 CONNECTION ISSUES")
        print("❌ Business flow: IMPACTED") 
        print("🔧 Immediate MT5 API troubleshooting required")
    
    print(f"\n📋 Server Details:")
    print(f"   Server: MEXAtlantic-Real")
    print(f"   Password: Fidus13@ (for all accounts)")
    print(f"   Total Investment Value: $118,151.41")

if __name__ == "__main__":
    main()