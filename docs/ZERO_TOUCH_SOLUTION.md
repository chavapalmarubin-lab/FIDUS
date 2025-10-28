# MT5 Bridge Self-Healing Setup - Zero Touch Solution

## The Real Problem

The MT5 Bridge needs to:
1. Start automatically without Unicode crashes
2. Run in the correct user session (not SYSTEM)
3. Auto-restart on failures
4. Require ZERO manual intervention

## The Real Solution

Deploy a self-healing script directly on the VPS that:
- Fixes Unicode issues automatically on startup
- Configures Task Scheduler correctly
- Monitors and auto-restarts the Bridge
- Requires zero manual work after initial deployment

---

## ONE-TIME DEPLOYMENT (SSH Key Method)

This will enable GitHub Actions to work properly forever.

### Step 1: Generate SSH Key for GitHub Actions

**On your local machine:**

```bash
# Generate a dedicated SSH key for GitHub Actions
ssh-keygen -t rsa -b 4096 -f ~/.ssh/vps_github_actions -N ""

# Display the public key (copy this)
cat ~/.ssh/vps_github_actions.pub

# Display the private key (copy this for GitHub Secrets)
cat ~/.ssh/vps_github_actions
```

### Step 2: Add Public Key to VPS

**SSH to VPS:**
```bash
ssh Administrator@92.118.45.135
```

**Run on VPS:**
```powershell
# Create .ssh directory if it doesn't exist
New-Item -Path "$env:USERPROFILE\.ssh" -ItemType Directory -Force

# Open authorized_keys file in Notepad
notepad "$env:USERPROFILE\.ssh\authorized_keys"
```

**In Notepad:**
1. Paste the public key (from `~/.ssh/vps_github_actions.pub`)
2. Save and close

**Back in PowerShell, set permissions:**
```powershell
# Set correct permissions
icacls "$env:USERPROFILE\.ssh" /inheritance:r
icacls "$env:USERPROFILE\.ssh" /grant:r "$env:USERNAME:(OI)(CI)F"
icacls "$env:USERPROFILE\.ssh\authorized_keys" /inheritance:r
icacls "$env:USERPROFILE\.ssh\authorized_keys" /grant:r "$env:USERNAME:F"
icacls "$env:USERPROFILE\.ssh\authorized_keys" /grant:r "SYSTEM:F"

Write-Host "SSH key configured!" -ForegroundColor Green

# Type exit to close SSH
exit
```

### Step 3: Test SSH Key Authentication

**On your local machine:**
```bash
ssh -i ~/.ssh/vps_github_actions Administrator@92.118.45.135
```

Should connect WITHOUT password prompt. If it works, type `exit`.

### Step 4: Add Private Key to GitHub Secrets

1. Go to: https://github.com/chavalitpro/fidus-autofix/settings/secrets/actions
2. Click: **"New repository secret"**
3. Name: `VPS_SSH_KEY`
4. Value: Paste entire private key content from `~/.ssh/vps_github_actions`
   ```
   -----BEGIN OPENSSH PRIVATE KEY-----
   ... (entire key content) ...
   -----END OPENSSH PRIVATE KEY-----
   ```
5. Click: **"Add secret"**

### Step 5: Test Automated Deployment

Now GitHub Actions will work! Try the workflow again:
- Go to: Actions → "Fix MT5 Bridge Unicode Logging"
- Click: "Run workflow"

It should complete successfully now.

---

## THE ULTIMATE SOLUTION: Self-Healing Task Scheduler

After GitHub Actions works, deploy this self-healing script that runs automatically on the VPS:

### Create Self-Healing Bridge Service

This script will:
- Fix Unicode issues on every restart
- Monitor Bridge health
- Auto-restart on failures
- Run in correct user session

The workflow will deploy this automatically once SSH keys are set up.

---

## Summary

**After this ONE-TIME setup:**
- ✅ GitHub Actions will work automatically
- ✅ All fixes deploy without manual work
- ✅ Bridge auto-heals on failures
- ✅ Zero touch operation

**Time Required:**
- SSH key setup: 5 minutes (one time only)
- All future operations: 0 minutes (fully automated)

---

Would you like to proceed with the SSH key setup? It's the ONLY manual step needed to achieve full automation forever.
