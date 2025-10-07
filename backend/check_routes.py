#!/usr/bin/env python3
"""
Check all registered FastAPI routes
"""

import sys
import os
sys.path.append('/app/backend')

# Import the FastAPI app
from server import app

def list_all_routes():
    """List all registered routes in the FastAPI app"""
    print("🔍 ALL REGISTERED ROUTES:")
    print("=" * 50)
    
    route_count = 0
    chava_routes = []
    
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods_str = ', '.join(route.methods) if route.methods else 'N/A'
            print(f"{methods_str:<15} {route.path}")
            route_count += 1
            
            # Check for Chava routes
            if 'chava' in route.path.lower():
                chava_routes.append(f"{methods_str} {route.path}")
    
    print(f"\n📊 Total routes: {route_count}")
    
    print("\n🔍 CHAVA-SPECIFIC ROUTES:")
    print("=" * 30)
    if chava_routes:
        for route in chava_routes:
            print(f"✅ {route}")
    else:
        print("❌ No Chava routes found!")
    
    print("\n🔍 GOOGLE-RELATED ROUTES:")
    print("=" * 30)
    google_routes = []
    for route in app.routes:
        if hasattr(route, 'path') and 'google' in route.path.lower():
            methods_str = ', '.join(route.methods) if route.methods else 'N/A'
            google_routes.append(f"{methods_str:<15} {route.path}")
    
    if google_routes:
        for route in google_routes[:10]:  # Show first 10
            print(f"  {route}")
        if len(google_routes) > 10:
            print(f"  ... and {len(google_routes) - 10} more")
    else:
        print("❌ No Google routes found!")

if __name__ == "__main__":
    list_all_routes()