#!/usr/bin/env python3
"""
SHARE: Test MT5 Bridge Service End-to-End Connectivity
Run this immediately once ForexVPS opens port 8000 external access
"""

import requests
import json
from datetime import datetime, timezone

def test_mt5_bridge_connectivity():
    """Test direct connectivity to MT5 Bridge service"""
    
    bridge_url = "http://217.197.163.11:8000"
    api_key = "fidus-mt5-bridge-key-2025-secure"
    headers = {"X-API-Key": api_key}
    
    print("🚀 FIDUS MT5 Bridge Service - End-to-End Connectivity Test")
    print("=" * 70)
    print(f"Bridge URL: {bridge_url}")
    print(f"Test Time: {datetime.now(timezone.utc).isoformat()}")
    print()
    
    # Test endpoints in order of importance
    test_endpoints = [
        ("/", "Root Service Info"),
        ("/health", "Service Health Check"), 
        ("/api/mt5/status", "MT5 Status Check"),
        ("/api/mt5/terminal/info", "MT5 Terminal Information"),
        ("/api/mt5/positions", "MT5 Positions Data"),
        ("/api/mt5/symbols", "MT5 Trading Symbols")
    ]
    
    results = []
    
    for endpoint, description in test_endpoints:
        print(f"Testing {endpoint} ({description})...")
        
        try:
            response = requests.get(f"{bridge_url}{endpoint}", headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract key information based on endpoint
                if endpoint == "/":
                    service_name = data.get("service", "Unknown")
                    mt5_available = data.get("mt5_available", False)
                    print(f"  ✅ SUCCESS: {service_name}")
                    print(f"     MT5 Available: {'✅' if mt5_available else '❌'}")
                    
                elif endpoint == "/health":
                    status = data.get("status", "unknown")
                    mt5_connected = data.get("mt5_connected", False)
                    print(f"  ✅ SUCCESS: Health Status = {status}")
                    print(f"     MT5 Connected: {'✅' if mt5_connected else '❌'}")
                    
                elif endpoint == "/api/mt5/status":
                    mt5_available = data.get("mt5_available", False) 
                    mt5_initialized = data.get("mt5_initialized", False)
                    print(f"  ✅ SUCCESS: MT5 Status Retrieved")
                    print(f"     MT5 Available: {'✅' if mt5_available else '❌'}")
                    print(f"     MT5 Initialized: {'✅' if mt5_initialized else '❌'}")
                    
                elif endpoint == "/api/mt5/terminal/info":
                    if "error" not in data:
                        terminal_name = data.get("name", "Unknown")
                        connected = data.get("connected", False)
                        print(f"  ✅ SUCCESS: Terminal = {terminal_name}")
                        print(f"     Connected: {'✅' if connected else '❌'}")
                    else:
                        print(f"  ⚠️  Terminal Error: {data['error']}")
                        
                elif endpoint == "/api/mt5/positions":
                    positions = data.get("positions", [])
                    count = data.get("count", 0)
                    print(f"  ✅ SUCCESS: {count} positions retrieved")
                    
                elif endpoint == "/api/mt5/symbols":
                    symbols = data.get("symbols", [])
                    count = data.get("count", 0)
                    print(f"  ✅ SUCCESS: {count} trading symbols available")
                
                results.append({"endpoint": endpoint, "status": "success", "data": data})
                
            else:
                print(f"  ❌ HTTP {response.status_code}: {response.text[:100]}")
                results.append({"endpoint": endpoint, "status": "error", "code": response.status_code})
                
        except requests.exceptions.ConnectTimeout:
            print(f"  ❌ CONNECTION TIMEOUT: Bridge service unreachable")
            results.append({"endpoint": endpoint, "status": "timeout"})
            
        except requests.exceptions.ConnectionError:
            print(f"  ❌ CONNECTION ERROR: Port likely blocked by ForexVPS")
            results.append({"endpoint": endpoint, "status": "blocked"})
            
        except Exception as e:
            print(f"  ❌ ERROR: {str(e)}")
            results.append({"endpoint": endpoint, "status": "error", "message": str(e)})
        
        print()
    
    # Summary
    successful_tests = len([r for r in results if r["status"] == "success"])
    total_tests = len(results)
    success_rate = (successful_tests / total_tests) * 100
    
    print("=" * 70)
    print("📊 TEST RESULTS SUMMARY:")
    print(f"   Successful Tests: {successful_tests}/{total_tests}")
    print(f"   Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("   Status: 🎉 PERFECT - MT5 Bridge fully operational!")
    elif success_rate >= 80:
        print("   Status: ✅ EXCELLENT - Core functionality working")
    elif success_rate >= 60:
        print("   Status: ⚠️  GOOD - Most features working")
    elif success_rate >= 40:
        print("   Status: ⚠️  LIMITED - Basic connectivity only")
    else:
        print("   Status: ❌ FAILED - Service unreachable or broken")
    
    print()
    print("🎯 NEXT STEPS:")
    if successful_tests == 0:
        print("   1. Check ForexVPS port 8000 is open externally")
        print("   2. Verify MT5 Bridge service is running on VPS") 
        print("   3. Test direct VPS localhost access")
    elif success_rate < 100:
        print("   1. ✅ Connectivity established!")
        print("   2. Address any failing endpoints")
        print("   3. Test FIDUS Backend → Bridge integration")
    else:
        print("   1. ✅ MT5 Bridge service fully operational!")
        print("   2. ✅ Test FIDUS Backend integration")
        print("   3. ✅ Deploy to production!")
    
    # Save detailed results
    with open('mt5_bridge_test_results.json', 'w') as f:
        json.dump({
            "test_time": datetime.now(timezone.utc).isoformat(),
            "bridge_url": bridge_url,
            "summary": {
                "successful_tests": successful_tests,
                "total_tests": total_tests,
                "success_rate": success_rate
            },
            "detailed_results": results
        }, f, indent=2)
    
    print(f"📁 Detailed results saved to: mt5_bridge_test_results.json")
    return results

if __name__ == "__main__":
    test_mt5_bridge_connectivity()