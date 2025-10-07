#!/usr/bin/env python3
"""
Test script to check if Chava endpoints are registered
"""

import sys
import os
sys.path.append('/app/backend')

# Import the FastAPI app
from server import app

def list_routes():
    """List all registered routes"""
    print("🔍 Registered routes:")
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            print(f"  {route.methods} {route.path}")
    
    print("\n🔍 Looking for Chava routes:")
    chava_routes = [route for route in app.routes if hasattr(route, 'path') and 'chava' in route.path.lower()]
    if chava_routes:
        for route in chava_routes:
            print(f"  ✅ Found: {route.methods} {route.path}")
    else:
        print("  ❌ No Chava routes found")

if __name__ == "__main__":
    list_routes()