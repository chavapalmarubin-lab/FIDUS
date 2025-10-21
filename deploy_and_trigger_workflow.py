#!/usr/bin/env python3
"""
Deploy workflow to GitHub and trigger autonomous VPS deployment
"""
import requests
import base64
import time
import sys

GITHUB_TOKEN = "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"
REPO_OWNER = "chavapalmarubin-lab"
REPO_NAME = "FIDUS"
WORKFLOW_FILE = "autonomous-vps-deployment.yml"
WORKFLOW_PATH = f".github/workflows/{WORKFLOW_FILE}"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def upload_workflow():
    """Upload workflow file to GitHub"""
    print("📤 Uploading workflow to GitHub...")
    
    # Read workflow content
    with open(f"/app/{WORKFLOW_PATH}", "r") as f:
        content = f.read()
    
    # Check if file exists
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{WORKFLOW_PATH}"
    response = requests.get(url, headers=headers, params={"ref": "main"})
    
    # Encode content
    encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    
    # Prepare data
    data = {
        "message": "feat: add autonomous VPS deployment workflow",
        "content": encoded_content,
        "branch": "main"
    }
    
    # If file exists, include SHA
    if response.status_code == 200:
        data["sha"] = response.json()["sha"]
        print("   Updating existing workflow...")
    else:
        print("   Creating new workflow...")
    
    # Upload
    response = requests.put(url, headers=headers, json=data)
    
    if response.status_code in [200, 201]:
        print("✅ Workflow uploaded successfully!")
        return True
    else:
        print(f"❌ Failed to upload workflow: {response.status_code}")
        print(response.text)
        return False

def trigger_workflow():
    """Trigger the workflow"""
    print("\n🚀 Triggering workflow...")
    
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/{WORKFLOW_FILE}/dispatches"
    data = {"ref": "main"}
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 204:
        print("✅ Workflow triggered successfully!")
        return True
    else:
        print(f"❌ Failed to trigger workflow: {response.status_code}")
        print(response.text)
        return False

def get_latest_run():
    """Get latest workflow run"""
    print("\n⏳ Waiting for workflow to start...")
    time.sleep(5)
    
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/{WORKFLOW_FILE}/runs"
    
    for attempt in range(5):
        response = requests.get(url, headers=headers, params={"per_page": 1})
        
        if response.status_code == 200:
            data = response.json()
            if data["total_count"] > 0:
                run = data["workflow_runs"][0]
                return run
        
        time.sleep(3)
    
    return None

def monitor_run(run_id, run_url):
    """Monitor workflow run"""
    print(f"\n📊 Monitoring workflow run: {run_id}")
    print(f"🔗 View live: {run_url}")
    print()
    
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}"
    
    last_status = None
    check_count = 0
    max_checks = 60  # 10 minutes
    
    while check_count < max_checks:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            status = data["status"]
            conclusion = data.get("conclusion")
            
            if status != last_status:
                print(f"📍 Status: {status}")
                last_status = status
            
            if status == "completed":
                print(f"\n✅ Workflow completed!")
                print(f"📝 Result: {conclusion}")
                
                if conclusion == "success":
                    print("\n🎉 DEPLOYMENT SUCCESSFUL!")
                    print("\n📋 Next steps:")
                    print("1. Test service: curl http://92.118.45.135:8000/api/mt5/bridge/health")
                    print("2. Check backend proxy")
                    print("3. Verify MT5 accounts syncing")
                    return True
                else:
                    print(f"\n⚠️ Deployment finished with status: {conclusion}")
                    print(f"🔗 Check logs: {run_url}")
                    return False
            
            if check_count % 6 == 0 and check_count > 0:
                print(f"⏳ Still {status}... ({check_count * 10}s elapsed)")
            
            time.sleep(10)
            check_count += 1
        else:
            print(f"❌ Error checking status: {response.status_code}")
            return False
    
    print("\n⏱️ Monitoring timeout (10 minutes)")
    print(f"🔗 Check manually: {run_url}")
    return False

def main():
    """Main execution"""
    print("=" * 70)
    print("🚀 AUTONOMOUS VPS DEPLOYMENT VIA GITHUB ACTIONS")
    print("=" * 70)
    print()
    
    # Step 1: Upload workflow
    if not upload_workflow():
        sys.exit(1)
    
    # Step 2: Wait for GitHub to process
    print("\n⏳ Waiting 5 seconds for GitHub to process...")
    time.sleep(5)
    
    # Step 3: Trigger workflow
    if not trigger_workflow():
        sys.exit(1)
    
    # Step 4: Get latest run
    run = get_latest_run()
    
    if not run:
        print("\n⚠️ Could not find workflow run")
        print(f"💡 Check manually: https://github.com/{REPO_OWNER}/{REPO_NAME}/actions")
        sys.exit(1)
    
    # Step 5: Monitor run
    success = monitor_run(run["id"], run["html_url"])
    
    if success:
        print("\n" + "=" * 70)
        print("🎉 AUTONOMOUS DEPLOYMENT COMPLETE!")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("⚠️ DEPLOYMENT NEEDS ATTENTION")
        print("=" * 70)

if __name__ == "__main__":
    main()
