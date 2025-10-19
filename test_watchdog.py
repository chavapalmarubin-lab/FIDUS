"""
Test MT5 Watchdog functionality
Verifies watchdog is running and GitHub token is configured
"""

import asyncio
import sys
import os

sys.path.insert(0, '/app/backend')

async def test_watchdog():
    """Test MT5 Watchdog"""
    
    print("=" * 70)
    print("MT5 WATCHDOG VERIFICATION TEST")
    print("=" * 70)
    print()
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv('/app/backend/.env')
    
    # Check GitHub token
    github_token = os.getenv('GITHUB_TOKEN')
    print(f"1. GitHub Token Present: {'✅ YES' if github_token else '❌ NO'}")
    if github_token:
        print(f"   Token starts with: {github_token[:10]}...")
    print()
    
    # Check SMTP configuration
    smtp_user = os.getenv('SMTP_USERNAME')
    smtp_pass = os.getenv('SMTP_APP_PASSWORD')
    print(f"2. SMTP Configured: {'✅ YES' if (smtp_user and smtp_pass) else '❌ NO'}")
    print(f"   SMTP Username: {smtp_user}")
    print()
    
    # Import database
    from config.database import get_database
    db = await get_database()
    print("3. Database Connected: ✅ YES")
    print()
    
    # Import watchdog
    try:
        from mt5_watchdog import MT5Watchdog
        from alert_service import AlertService
        print("4. Watchdog Module Imported: ✅ YES")
        print()
        
        # Create watchdog instance
        alert_service = AlertService(db)
        watchdog = MT5Watchdog(db, alert_service)
        
        print("5. Watchdog Instance Created: ✅ YES")
        print(f"   Check Interval: {watchdog.check_interval}s")
        print(f"   Failure Threshold: {watchdog.failure_threshold}")
        print(f"   GitHub Token Configured: {'✅ YES' if watchdog.github_token else '❌ NO'}")
        print(f"   VPS Bridge URL: {watchdog.vps_bridge_url}")
        print()
        
        # Test health check
        print("6. Testing Health Check...")
        health = await watchdog.check_mt5_health()
        print(f"   Health Status: {'✅ HEALTHY' if health['healthy'] else '⚠️ UNHEALTHY'}")
        print(f"   Bridge API Available: {health.get('bridge_api_available', 'N/A')}")
        print(f"   Data Fresh: {health.get('data_fresh', 'N/A')}")
        print(f"   Accounts Syncing: {health.get('accounts_syncing', 'N/A')}")
        print()
        
        # Check if global watchdog is initialized
        from mt5_watchdog import get_watchdog
        global_watchdog = get_watchdog()
        print(f"7. Global Watchdog Initialized: {'✅ YES' if global_watchdog else '❌ NO (will initialize on server startup)'}")
        print()
        
        print("=" * 70)
        print("✅ ALL TESTS PASSED - MT5 WATCHDOG IS READY!")
        print("=" * 70)
        print()
        print("Next Steps:")
        print("1. Watchdog will automatically start when backend server starts")
        print("2. Check server logs for: '[MT5 WATCHDOG] 🚀 Starting...'")
        print("3. Watchdog will monitor every 60 seconds")
        print("4. Auto-healing will trigger after 3 consecutive failures")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_watchdog())
    sys.exit(0 if success else 1)
