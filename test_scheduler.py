"""
Test script to verify scheduler jobs are configured correctly
"""

import asyncio
import sys

sys.path.insert(0, '/app/backend')

async def check_scheduler_jobs():
    """Check what jobs are scheduled"""
    
    print("=" * 60)
    print("CHECKING APSCHEDULER JOBS")
    print("=" * 60)
    print()
    
    from server import scheduler
    
    jobs = scheduler.get_jobs()
    
    if not jobs:
        print("❌ NO JOBS SCHEDULED!")
        print()
        return False
    
    print(f"✅ Found {len(jobs)} scheduled job(s):")
    print()
    
    for job in jobs:
        print(f"Job ID: {job.id}")
        print(f"   Function: {job.func.__name__ if hasattr(job, 'func') else 'Unknown'}")
        print(f"   Trigger: {job.trigger}")
        print(f"   Next run: {job.next_run_time}")
        print()
    
    # Check for specific jobs
    health_job = scheduler.get_job('auto_health_check')
    sync_job = scheduler.get_job('auto_vps_sync')
    
    if health_job:
        print("✅ Health monitoring job is configured")
    else:
        print("❌ Health monitoring job NOT found")
    
    if sync_job:
        print("✅ VPS sync job is configured")
    else:
        print("❌ VPS sync job NOT found")
    
    print()
    return True


if __name__ == "__main__":
    success = asyncio.run(check_scheduler_jobs())
    sys.exit(0 if success else 1)
