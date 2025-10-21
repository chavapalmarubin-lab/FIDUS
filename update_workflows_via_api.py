#!/usr/bin/env python3
"""
Update GitHub Workflow Files via API
Bypasses local git history issues by committing directly to GitHub
"""
import requests
import base64
import json
import time

GITHUB_TOKEN = "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"
REPO_OWNER = "chavapalmarubin-lab"
REPO_NAME = "FIDUS"
BRANCH = "main"

# Old and new VPS IPs
OLD_VPS_IP = "217.197.163.11"
NEW_VPS_IP = "92.118.45.135"

# Workflow files to update
WORKFLOW_FILES = [
    "deploy-fresh-vps.yml",
    "deploy-vps.yml",
    "deploy-autonomous-system.yml",
    "diagnose-vps.yml",
    "deploy-mt5-bridge-emergency-ps.yml",
    "nuclear-reset-mt5-bridge.yml",
    "direct-file-deploy-mt5-bridge.yml",
    "final-fix-mt5-bridge.yml",
    "complete-diagnostic-fix.yml",
    "auto-test-healing-system.yml",
    "fresh-install-mt5-bridge.yml",
    "deploy-mt5-bridge-emergency.yml",
    "diagnose-mt5-bridge.yml",
    "setup-mt5-auto-login.yml",
    "monitor-render-health.yml",
    "diagnose-vps-auto-restart.yml",
    "deploy-backend.yml"
]

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_file_content(file_path):
    """Get file content from GitHub"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}"
    params = {"ref": BRANCH}
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    data = response.json()
    content = base64.b64decode(data["content"]).decode("utf-8")
    sha = data["sha"]
    
    return content, sha

def update_file_content(file_path, new_content, sha, commit_message):
    """Update file content on GitHub"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}"
    
    # Encode content to base64
    encoded_content = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")
    
    data = {
        "message": commit_message,
        "content": encoded_content,
        "sha": sha,
        "branch": BRANCH
    }
    
    response = requests.put(url, headers=headers, json=data)
    response.raise_for_status()
    
    return response.json()

def main():
    """Main execution"""
    print("🚀 Starting GitHub Workflow Files Update via API")
    print("=" * 70)
    print(f"Repository: {REPO_OWNER}/{REPO_NAME}")
    print(f"Branch: {BRANCH}")
    print(f"Old VPS IP: {OLD_VPS_IP}")
    print(f"New VPS IP: {NEW_VPS_IP}")
    print(f"Files to update: {len(WORKFLOW_FILES)}")
    print("=" * 70)
    print()
    
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    for workflow_file in WORKFLOW_FILES:
        file_path = f".github/workflows/{workflow_file}"
        print(f"📄 Processing: {workflow_file}")
        
        try:
            # Get current file content
            content, sha = get_file_content(file_path)
            
            # Check if old VPS IP exists
            if OLD_VPS_IP not in content:
                print(f"   ⏭️  Skipped - No old VPS IP found")
                skipped_count += 1
                continue
            
            # Replace old VPS IP with new VPS IP
            new_content = content.replace(OLD_VPS_IP, NEW_VPS_IP)
            
            # Count replacements
            replacements = content.count(OLD_VPS_IP)
            
            # Update file on GitHub
            commit_message = f"chore: update {workflow_file} to new VPS ({NEW_VPS_IP})"
            result = update_file_content(file_path, new_content, sha, commit_message)
            
            print(f"   ✅ Updated - {replacements} replacement(s)")
            print(f"   📝 Commit: {result['commit']['sha'][:8]}")
            updated_count += 1
            
            # Rate limiting - wait 1 second between requests
            time.sleep(1)
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"   ⚠️  Not found - File may not exist")
            else:
                print(f"   ❌ Error: {e.response.status_code} - {e.response.text}")
            error_count += 1
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            error_count += 1
        
        print()
    
    # Summary
    print("=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print(f"✅ Updated: {updated_count}")
    print(f"⏭️  Skipped: {skipped_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📝 Total: {len(WORKFLOW_FILES)}")
    print("=" * 70)
    
    if updated_count > 0:
        print()
        print("✅ SUCCESS! Workflow files updated on GitHub")
        print(f"🔗 View changes: https://github.com/{REPO_OWNER}/{REPO_NAME}/commits/{BRANCH}")
        print()
        print("🎯 Next Steps:")
        print("1. Verify commits on GitHub")
        print("2. Test new VPS: curl http://92.118.45.135:8000/api/mt5/bridge/health")
        print("3. Run Phase 5 verification tests")
    else:
        print()
        print("⚠️ No files were updated. Please check the output above.")

if __name__ == "__main__":
    main()
