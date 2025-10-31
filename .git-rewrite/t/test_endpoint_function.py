#!/usr/bin/env python3
"""
Test the MT5 Bridge Health endpoint function directly
"""

import asyncio
import sys
import os
sys.path.append('/app/backend')

async def test_endpoint_function():
    """Test the endpoint function directly"""
    
    # Mock current_user
    class MockUser:
        def get(self, key):
            if key == "type":
                return "admin"
            return None
    
    current_user = MockUser()
    
    try:
        # Import the function
        from server import check_mt5_bridge_health
        
        print("✅ Successfully imported check_mt5_bridge_health function")
        
        # Test the function
        result = await check_mt5_bridge_health(current_user)
        print(f"✅ Function executed successfully")
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"❌ Function test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_endpoint_function())