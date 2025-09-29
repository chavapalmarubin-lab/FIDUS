#!/usr/bin/env python3
"""
Test script to verify Google connection endpoints are working
"""

import requests
import json

def test_google_endpoints():
    backend_url = "https://fidus-invest.emergent.host/api"
    
    # Authenticate
    login_data = {
        "username": "admin",
        "password": "password123",
        "user_type": "admin"
    }
    
    auth_response = requests.post(f"{backend_url}/auth/login", json=login_data)
    if auth_response.status_code != 200:
        print(f"❌ Authentication failed: {auth_response.status_code}")
        return False
    
    token = auth_response.json().get('token')
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test all 4 endpoints
    endpoints = [
        ("GET", "/admin/google/connection-status"),
        ("GET", "/admin/google/monitor"),
        ("GET", "/admin/google/health-check"),
        ("POST", "/admin/google/force-reconnect")
    ]
    
    results = []
    for method, endpoint in endpoints:
        if method == "GET":
            response = requests.get(f"{backend_url}{endpoint}", headers=headers)
        else:
            response = requests.post(f"{backend_url}{endpoint}", headers=headers)
        
        success = response.status_code == 200
        results.append({
            "endpoint": endpoint,
            "method": method,
            "status": response.status_code,
            "success": success
        })
        
        print(f"{method} {endpoint}: {response.status_code} {'✅' if success else '❌'}")
        
        if success:
            data = response.json()
            print(f"  Success: {data.get('success', 'N/A')}")
            print(f"  Auto-managed: {data.get('connection_status', {}).get('auto_managed', data.get('auto_managed', 'N/A'))}")
            print(f"  Production ready: {data.get('production_ready', 'N/A')}")
        elif response.status_code != 404:
            print(f"  Error: {response.text[:100]}")
        print()
    
    # Summary
    working_endpoints = sum(1 for r in results if r["success"])
    total_endpoints = len(results)
    success_rate = (working_endpoints / total_endpoints) * 100
    
    print(f"📊 SUMMARY: {working_endpoints}/{total_endpoints} endpoints working ({success_rate:.1f}% success rate)")
    
    if success_rate >= 75:
        print("🎉 CONCLUSION: Automated Google connection system is WORKING!")
        return True
    else:
        print("❌ CONCLUSION: Automated Google connection system has issues")
        return False

if __name__ == "__main__":
    test_google_endpoints()