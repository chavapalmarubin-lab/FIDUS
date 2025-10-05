#!/usr/bin/env python3
"""
Test FIDUS Backend → MT5 Bridge Integration
Test the complete flow once ForexVPS opens port 8000
"""

import asyncio
import sys
import os
sys.path.append('/app/backend')

async def test_fidus_mt5_integration():
    """Test FIDUS backend integration with MT5 Bridge"""
    
    print("🔗 Testing FIDUS Backend → MT5 Bridge Integration")
    print("=" * 60)
    
    try:
        # Import MT5 Bridge Client
        from mt5_bridge_client import MT5BridgeClient
        
        # Initialize client
        bridge_client = MT5BridgeClient()
        
        print("✅ MT5BridgeClient imported successfully")
        print(f"   Bridge URL: {bridge_client.bridge_url}")
        print(f"   API Key: {bridge_client.api_key[:20]}...")
        print(f"   Timeout: {bridge_client.timeout}s")
        print()
        
        # Test 1: Health Check
        print("1. Testing Health Check...")
        try:
            health = await bridge_client.health_check()
            print(f"   Result: {health}")
            
            if health.get('status') == 'healthy':
                print("   ✅ Bridge service is healthy")
            else:
                print("   ⚠️  Bridge service reports issues")
        except Exception as e:
            print(f"   ❌ Health check failed: {e}")
        
        print()
        
        # Test 2: MT5 Status
        print("2. Testing MT5 Status...")
        try:
            status = await bridge_client.get_mt5_status()
            print(f"   Result: {status}")
            
            if status.get('mt5_available'):
                print("   ✅ MT5 is available and connected")
            else:
                print("   ❌ MT5 is not available")
        except Exception as e:
            print(f"   ❌ MT5 status check failed: {e}")
        
        print()
        
        # Test 3: Account Information (if available)
        print("3. Testing Account Information...")
        try:
            account_info = await bridge_client.get_account_info()
            print(f"   Result: {account_info}")
            
            if not account_info.get('error'):
                print("   ✅ Account info retrieved successfully")
                if 'balance' in account_info:
                    print(f"   💰 Balance: {account_info.get('balance')}")
                if 'equity' in account_info:
                    print(f"   📈 Equity: {account_info.get('equity')}")
            else:
                print(f"   ⚠️  Account info error: {account_info['error']}")
        except Exception as e:
            print(f"   ❌ Account info failed: {e}")
        
        print()
        
        # Test 4: Positions (if available)
        print("4. Testing Positions Data...")
        try:
            positions = await bridge_client.get_positions()
            print(f"   Result: {positions}")
            
            if positions.get('success'):
                pos_count = positions.get('count', 0)
                print(f"   ✅ Positions retrieved: {pos_count} open positions")
            else:
                print(f"   ⚠️  Positions error: {positions.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"   ❌ Positions failed: {e}")
        
        print()
        
        # Cleanup
        await bridge_client.close()
        print("✅ MT5BridgeClient session closed")
        
    except ImportError as e:
        print(f"❌ Failed to import MT5BridgeClient: {e}")
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_mt5_service_integration():
    """Test MT5 Service layer integration"""
    
    print("\n🔧 Testing MT5 Service Layer Integration")
    print("=" * 60)
    
    try:
        from services.mt5_service import mt5_service
        
        print("✅ MT5 Service imported successfully")
        
        # Initialize service
        await mt5_service.initialize()
        print("✅ MT5 Service initialized")
        
        # Test repository access
        if mt5_service.mt5_repo:
            print("✅ MT5 Repository is available")
            
            # Test account retrieval
            accounts = await mt5_service.mt5_repo.find_active_accounts()
            print(f"✅ Active accounts in database: {len(accounts)}")
            
        else:
            print("❌ MT5 Repository not initialized")
            
    except Exception as e:
        print(f"❌ MT5 Service test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fidus_mt5_integration())
    asyncio.run(test_mt5_service_integration())