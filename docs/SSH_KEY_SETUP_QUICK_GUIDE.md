# SSH Key Setup - 2 Minute Guide

## Step 1: Run Setup Script on VPS (1 minute)

**RDP to VPS (92.118.45.135)**

**Open PowerShell as Administrator**

**Run this ONE command:**

```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/chavalitpro/fidus-autofix/main/vps-scripts/setup-ssh-key-for-github.ps1" -OutFile "$env:TEMP\setup-ssh.ps1"; PowerShell -ExecutionPolicy Bypass -File "$env:TEMP\setup-ssh.ps1"
```

**Or if offline, paste and run the script from `/vps-scripts/setup-ssh-key-for-github.ps1`**

## Step 2: Copy Private Key (30 seconds)

The script will output:
```
============================================
[Private key content here]
============================================
```

**Copy EVERYTHING** from `-----BEGIN OPENSSH PRIVATE KEY-----` to `-----END OPENSSH PRIVATE KEY-----`

## Step 3: Add to GitHub Secrets (30 seconds)

1. Go to: `https://github.com/YOUR_ORG/YOUR_REPO/settings/secrets/actions`
2. Click: **"New repository secret"**
3. Name: `VPS_SSH_KEY`
4. Value: **Paste the private key**
5. Click: **"Add secret"**

**Done!**

## Step 4: Test It Works

1. Go to: GitHub Actions → "Emergency - Restart MT5 Bridge (Diagnostic + Fix)"
2. Click: "Run workflow"
3. Should complete successfully with green checkmark

---

## What This Enables

**Before**: GitHub Actions couldn't connect to VPS (password auth failed)

**After**: GitHub Actions can:
- Restart Bridge remotely when it crashes
- Run diagnostics to find root cause
- Verify MT5 Terminal is running
- Check health and report status

**Result**: True zero-touch auto-healing

---

## Troubleshooting

### If workflow still fails after setup:

**Check**:
1. VPS_SSH_KEY secret contains the full private key (including BEGIN/END lines)
2. No extra spaces or line breaks were added when pasting
3. SSH service is running on VPS: `Get-Service sshd`

**Test manually**:
```bash
# On your local machine
ssh -i path/to/private/key Administrator@92.118.45.135
```

Should connect without password prompt.

---

**Time**: 2 minutes total  
**Complexity**: Copy/paste  
**Benefit**: Remote emergency restarts work forever
