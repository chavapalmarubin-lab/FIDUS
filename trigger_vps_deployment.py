#!/usr/bin/env python3
"""
Trigger GitHub Actions Workflow to Deploy MT5 Bridge on New VPS
"""
import requests
import time
import json

GITHUB_TOKEN = "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"
REPO_OWNER = "chavapalmarubin-lab"
REPO_NAME = "FIDUS"
WORKFLOW_FILE = "deploy-fresh-vps.yml"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def trigger_workflow():
    """Trigger the deployment workflow"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/{WORKFLOW_FILE}/dispatches"
    
    data = {
        "ref": "main"
    }
    
    print(f"🚀 Triggering workflow: {WORKFLOW_FILE}")
    print(f"📍 Repository: {REPO_OWNER}/{REPO_NAME}")
    print(f"🌿 Branch: main")
    print()
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 204:
        print("✅ Workflow triggered successfully!")
        return True
    else:
        print(f"❌ Failed to trigger workflow: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def get_latest_workflow_run():
    """Get the latest workflow run"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/{WORKFLOW_FILE}/runs"
    
    response = requests.get(url, headers=headers, params={"per_page": 1})
    
    if response.status_code == 200:
        data = response.json()
        if data["total_count"] > 0:
            return data["workflow_runs"][0]
    return None

def monitor_workflow_run(run_id):
    """Monitor workflow run status"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}"
    
    print(f"\n📊 Monitoring workflow run: {run_id}")
    print(f"🔗 View live: https://github.com/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}")
    print()
    
    max_checks = 60  # Monitor for up to 10 minutes
    check_count = 0
    
    while check_count < max_checks:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            status = data["status"]
            conclusion = data.get("conclusion")
            
            if status == "completed":
                print(f"\n✅ Workflow completed!")
                print(f"📝 Conclusion: {conclusion}")
                
                if conclusion == "success":
                    print("🎉 Deployment successful!")
                    return True
                else:
                    print(f"⚠️ Deployment finished with status: {conclusion}")
                    return False
            
            if check_count % 6 == 0:  # Print status every minute
                print(f"⏳ Status: {status}... (checking again in 10s)")
            
            time.sleep(10)
            check_count += 1
        else:
            print(f"❌ Error checking workflow status: {response.status_code}")
            return False
    
    print("\n⏱️ Monitoring timeout reached (10 minutes)")
    print("💡 Workflow may still be running. Check GitHub Actions page.")
    return False

def main():
    """Main execution"""
    print("=" * 70)
    print("🚀 NEW VPS MT5 BRIDGE DEPLOYMENT")
    print("=" * 70)
    print()
    
    # Trigger workflow
    if not trigger_workflow():
        print("\n❌ Failed to trigger deployment")
        return
    
    print("\n⏳ Waiting 5 seconds for workflow to start...")
    time.sleep(5)
    
    # Get latest run
    latest_run = get_latest_workflow_run()
    
    if latest_run:
        run_id = latest_run["id"]
        run_url = latest_run["html_url"]
        
        print(f"\n✅ Found workflow run:")
        print(f"   ID: {run_id}")
        print(f"   URL: {run_url}")
        
        # Monitor the run
        success = monitor_workflow_run(run_id)
        
        if success:
            print("\n" + "=" * 70)
            print("🎉 DEPLOYMENT COMPLETE!")
            print("=" * 70)
            print()
            print("🔍 Next steps:")
            print("1. Test MT5 Bridge: curl http://92.118.45.135:8000/api/mt5/bridge/health")
            print("2. Verify service status on VPS")
            print("3. Check Task Scheduler is running")
        else:
            print("\n" + "=" * 70)
            print("⚠️ DEPLOYMENT NEEDS ATTENTION")
            print("=" * 70)
            print()
            print(f"🔗 Check logs: {run_url}")
    else:
        print("\n⚠️ Could not find workflow run")
        print("💡 Check manually: https://github.com/{REPO_OWNER}/{REPO_NAME}/actions")

if __name__ == "__main__":
    main()
