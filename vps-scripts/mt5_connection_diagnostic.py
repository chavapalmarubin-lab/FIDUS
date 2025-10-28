# MT5 Bridge IPC Timeout Fix
# This script fixes the MetaTrader5 Python library connection issue

import MetaTrader5 as mt5
import time
import sys
import os
from pathlib import Path

print("=" * 70)
print("MT5 CONNECTION DIAGNOSTIC & FIX")
print("=" * 70)
print()

# Common MT5 installation paths
MT5_PATHS = [
    r"C:\Program Files\MetaTrader 5\terminal64.exe",
    r"C:\Program Files (x86)\MetaTrader 5\terminal64.exe",
    r"C:\MetaTrader 5\terminal64.exe",
    r"D:\MetaTrader 5\terminal64.exe",
    # Add more paths if needed
]

def find_mt5_terminal():
    """Find the MT5 terminal executable"""
    print("🔍 Searching for MT5 Terminal...")
    
    for path in MT5_PATHS:
        if Path(path).exists():
            print(f"   ✅ Found: {path}")
            return path
    
    print("   ❌ MT5 Terminal not found in common locations")
    return None

def test_mt5_connection_basic():
    """Test basic MT5 connection without path"""
    print("\n📡 Test 1: Basic Connection (no path)")
    print("-" * 70)
    
    result = mt5.initialize()
    
    if result:
        print("   ✅ SUCCESS: MT5 connected!")
        info = mt5.terminal_info()
        if info:
            print(f"   Terminal: {info.name}")
            print(f"   Company: {info.company}")
            print(f"   Build: {info.build}")
        mt5.shutdown()
        return True
    else:
        error = mt5.last_error()
        print(f"   ❌ FAILED: Error {error}")
        return False

def test_mt5_connection_with_path(path):
    """Test MT5 connection with explicit path"""
    print(f"\n📡 Test 2: Connection with Path")
    print("-" * 70)
    print(f"   Path: {path}")
    
    result = mt5.initialize(path=path)
    
    if result:
        print("   ✅ SUCCESS: MT5 connected with path!")
        info = mt5.terminal_info()
        if info:
            print(f"   Terminal: {info.name}")
            print(f"   Company: {info.company}")
            print(f"   Build: {info.build}")
        mt5.shutdown()
        return True
    else:
        error = mt5.last_error()
        print(f"   ❌ FAILED: Error {error}")
        return False

def test_mt5_connection_with_retries(path=None, max_retries=3, delay=5):
    """Test MT5 connection with retry logic"""
    print(f"\n📡 Test 3: Connection with Retries ({max_retries} attempts)")
    print("-" * 70)
    
    for attempt in range(1, max_retries + 1):
        print(f"   Attempt {attempt}/{max_retries}...")
        
        if path:
            result = mt5.initialize(path=path)
        else:
            result = mt5.initialize()
        
        if result:
            print(f"   ✅ SUCCESS on attempt {attempt}!")
            info = mt5.terminal_info()
            if info:
                print(f"   Terminal: {info.name}")
                print(f"   Connected: {info.connected}")
            
            # Test account access
            account_info = mt5.account_info()
            if account_info:
                print(f"   Account: {account_info.login}")
                print(f"   Balance: ${account_info.balance:,.2f}")
                print(f"   Server: {account_info.server}")
            
            mt5.shutdown()
            return True
        else:
            error = mt5.last_error()
            print(f"   ❌ Attempt {attempt} failed: {error}")
            
            if attempt < max_retries:
                print(f"   ⏳ Waiting {delay} seconds before retry...")
                time.sleep(delay)
    
    print(f"   ❌ All {max_retries} attempts failed")
    return False

def check_mt5_settings():
    """Check if MT5 terminal has correct settings"""
    print("\n⚙️  MT5 Settings Check")
    print("-" * 70)
    print("   Please verify in MT5 Terminal:")
    print("   1. Tools → Options → Expert Advisors")
    print("   2. Enable: 'Allow automated trading'")
    print("   3. Enable: 'Allow DLL imports'")
    print("   4. Restart MT5 after changing settings")
    print()

def check_permissions():
    """Check if script is running with proper permissions"""
    print("\n🔐 Permissions Check")
    print("-" * 70)
    
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        if is_admin:
            print("   ✅ Running as Administrator")
        else:
            print("   ⚠️  NOT running as Administrator")
            print("   Consider running this script as Administrator")
    except:
        print("   ⚠️  Could not determine Administrator status")

def generate_fixed_code(working_path=None):
    """Generate fixed initialization code"""
    print("\n📝 FIXED INITIALIZATION CODE")
    print("=" * 70)
    
    code = '''
import MetaTrader5 as mt5
import time
import logging

logger = logging.getLogger(__name__)

def initialize_mt5_with_retry(max_retries=3, delay=5):
    """
    Initialize MT5 with retry logic and proper error handling
    
    Args:
        max_retries: Maximum number of connection attempts
        delay: Delay in seconds between retries
    
    Returns:
        bool: True if connected, False otherwise
    """
'''
    
    if working_path:
        code += f'''
    # Path that worked in diagnostics
    mt5_path = r"{working_path}"
'''
    else:
        code += '''
    # Try common MT5 paths
    mt5_paths = [
        r"C:\\Program Files\\MetaTrader 5\\terminal64.exe",
        r"C:\\Program Files (x86)\\MetaTrader 5\\terminal64.exe",
    ]
    
    mt5_path = None
    for path in mt5_paths:
        if Path(path).exists():
            mt5_path = path
            break
'''
    
    code += '''
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"MT5 connection attempt {attempt}/{max_retries}")
            
            # Initialize with or without path
            if mt5_path:
                result = mt5.initialize(path=mt5_path)
            else:
                result = mt5.initialize()
            
            if result:
                # Verify connection
                terminal_info = mt5.terminal_info()
                if terminal_info and terminal_info.connected:
                    logger.info(f"✅ MT5 connected: {terminal_info.name}")
                    return True
                else:
                    logger.warning("MT5 initialized but not connected")
                    mt5.shutdown()
            else:
                error = mt5.last_error()
                logger.error(f"MT5 initialize failed: {error}")
            
            if attempt < max_retries:
                logger.info(f"Waiting {delay}s before retry...")
                time.sleep(delay)
        
        except Exception as e:
            logger.error(f"Exception during MT5 init: {e}")
            if attempt < max_retries:
                time.sleep(delay)
    
    logger.error("❌ All MT5 connection attempts failed")
    return False

# Usage in your Bridge service:
if initialize_mt5_with_retry():
    print("MT5 Ready!")
else:
    print("MT5 Connection Failed")
    sys.exit(1)
'''
    
    print(code)
    
    # Save to file
    output_file = "fixed_mt5_init.py"
    with open(output_file, 'w') as f:
        f.write(code)
    print(f"\n💾 Saved to: {output_file}")

def main():
    """Run all diagnostics"""
    print("Starting MT5 Connection Diagnostics...\n")
    
    # Check permissions
    check_permissions()
    
    # Check MT5 settings
    check_mt5_settings()
    
    # Find MT5 terminal
    mt5_path = find_mt5_terminal()
    
    # Test 1: Basic connection
    test1_success = test_mt5_connection_basic()
    
    # Test 2: Connection with path
    test2_success = False
    if mt5_path:
        test2_success = test_mt5_connection_with_path(mt5_path)
    
    # Test 3: Connection with retries
    test3_success = test_mt5_connection_with_retries(
        path=mt5_path if mt5_path else None,
        max_retries=3,
        delay=5
    )
    
    # Summary
    print("\n" + "=" * 70)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 70)
    print(f"Test 1 (Basic):         {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"Test 2 (With Path):     {'✅ PASS' if test2_success else '❌ FAIL' if mt5_path else '⏭️  SKIP'}")
    print(f"Test 3 (With Retries):  {'✅ PASS' if test3_success else '❌ FAIL'}")
    
    if test1_success or test2_success or test3_success:
        print("\n🎉 SUCCESS! MT5 connection is possible")
        working_path = mt5_path if (test2_success or test3_success) else None
        generate_fixed_code(working_path)
        
        print("\n📋 NEXT STEPS:")
        print("1. Copy the fixed code above into your MT5 Bridge service")
        print("2. Replace the current mt5.initialize() call")
        print("3. Restart the Bridge service")
        print("4. Test with: curl http://localhost:8000/api/mt5/bridge/health")
    else:
        print("\n❌ ALL TESTS FAILED")
        print("\n📋 TROUBLESHOOTING:")
        print("1. Ensure MT5 Terminal is running and logged in")
        print("2. Check MT5 settings: Tools → Options → Expert Advisors")
        print("3. Enable 'Allow automated trading' in MT5")
        print("4. Run this script as Administrator")
        print("5. Restart MT5 Terminal")
        print("6. Try running this diagnostic again")

if __name__ == "__main__":
    main()
