#!/usr/bin/env python3
"""
MT5 Sync Monitoring Script
Tracks sync performance, success rate, and data freshness
Run: python3 monitor_mt5_sync.py
"""

import asyncio
import sys
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os

# MongoDB connection
MONGO_URL = "mongodb+srv://chavapalmarubin_db_user:2170Tenoch!@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority"

async def check_sync_status():
    """Check current MT5 sync status"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.fidus_production
    
    print("=" * 80)
    print(f"MT5 SYNC STATUS - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("=" * 80)
    
    # Get all accounts
    accounts = await db.mt5_accounts.find().sort('account', 1).to_list(length=None)
    
    if not accounts:
        print("❌ No accounts found in database!")
        return
    
    # Calculate metrics
    now = datetime.now(timezone.utc)
    total_accounts = len(accounts)
    fresh_accounts = 0
    stale_accounts = 0
    oldest_update = None
    newest_update = None
    total_balance = 0
    
    print(f"\n📊 ACCOUNT STATUS ({total_accounts} accounts):")
    print(f"{'Account':<10} {'Balance':<15} {'Age':<20} {'Data Source':<20}")
    print("-" * 80)
    
    for acc in accounts:
        account_id = acc.get('account', 'N/A')
        balance = acc.get('balance', 0)
        updated_at = acc.get('updated_at')
        data_source = acc.get('data_source', 'unknown')
        
        # Calculate age
        if updated_at:
            if isinstance(updated_at, str):
                updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            age_seconds = (now - updated_at).total_seconds()
            age_minutes = age_seconds / 60
            
            if age_minutes < 10:
                age_str = f"{age_minutes:.1f} min (FRESH)"
                fresh_accounts += 1
            elif age_minutes < 30:
                age_str = f"{age_minutes:.1f} min (OK)"
            else:
                age_str = f"{age_minutes:.1f} min (STALE)"
                stale_accounts += 1
            
            # Track oldest/newest
            if oldest_update is None or updated_at < oldest_update:
                oldest_update = updated_at
            if newest_update is None or updated_at > newest_update:
                newest_update = updated_at
        else:
            age_str = "NO TIMESTAMP"
            stale_accounts += 1
        
        # Add to total
        total_balance += balance
        
        # Print row
        print(f"{account_id:<10} ${balance:<14,.2f} {age_str:<20} {data_source:<20}")
    
    print("-" * 80)
    print(f"{'TOTAL':<10} ${total_balance:<14,.2f}")
    print()
    
    # Summary metrics
    print("📈 METRICS:")
    print(f"   Fresh accounts (<10 min): {fresh_accounts}/{total_accounts} ({fresh_accounts/total_accounts*100:.1f}%)")
    print(f"   Stale accounts (>10 min):  {stale_accounts}/{total_accounts}")
    
    if oldest_update and newest_update:
        oldest_age = (now - oldest_update).total_seconds() / 60
        newest_age = (now - newest_update).total_seconds() / 60
        print(f"   Oldest update: {oldest_age:.1f} minutes ago")
        print(f"   Newest update: {newest_age:.1f} minutes ago")
        print(f"   Sync spread: {(oldest_age - newest_age):.1f} minutes")
    
    # Health assessment
    print()
    print("🏥 HEALTH ASSESSMENT:")
    if fresh_accounts == total_accounts:
        print("   ✅ EXCELLENT - All accounts fresh (<10 min)")
    elif fresh_accounts >= total_accounts * 0.8:
        print("   ✅ GOOD - Most accounts fresh (>80%)")
    elif fresh_accounts >= total_accounts * 0.5:
        print("   ⚠️  DEGRADED - Some accounts stale (<80%)")
    else:
        print("   ❌ CRITICAL - Many accounts stale (<50%)")
    
    # Expected next sync
    if newest_update:
        next_sync = newest_update + timedelta(minutes=5)
        time_until = (next_sync - now).total_seconds() / 60
        if time_until > 0:
            print(f"   Next sync expected in: {time_until:.1f} minutes")
        else:
            print(f"   ⚠️  Sync overdue by: {abs(time_until):.1f} minutes")
    
    print("=" * 80)
    print()

async def continuous_monitor(interval_seconds=300):
    """Monitor continuously every N seconds"""
    print("🔄 Starting continuous monitoring...")
    print(f"   Checking every {interval_seconds} seconds ({interval_seconds/60:.1f} minutes)")
    print(f"   Press Ctrl+C to stop")
    print()
    
    try:
        while True:
            await check_sync_status()
            print(f"⏳ Waiting {interval_seconds} seconds until next check...")
            print()
            await asyncio.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor MT5 sync status')
    parser.add_argument('--continuous', action='store_true', help='Run continuous monitoring')
    parser.add_argument('--interval', type=int, default=300, help='Check interval in seconds (default: 300)')
    
    args = parser.parse_args()
    
    if args.continuous:
        asyncio.run(continuous_monitor(args.interval))
    else:
        asyncio.run(check_sync_status())
