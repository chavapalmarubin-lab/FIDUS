# Archived MEXAtlantic VPS Workflows

## Archive Date: February 24, 2026

## Reason for Archive
These workflows were created to manage the MEXAtlantic MT5 Bridge VPS (92.118.45.135).
FIDUS has transitioned to **LUCRUM-ONLY mode** and the MEXAtlantic VPS is no longer in use.

## Status: DISABLED
All workflow files have been renamed to `.yml.disabled` so GitHub Actions will not execute them.

## To Stop Email Notifications
If you're still receiving failure emails from old workflow runs:

1. **Go to GitHub Repository** → Settings → Notifications
2. **Or** Go to your GitHub profile → Settings → Notifications → Actions
3. Uncheck "Send notifications for failed workflows only" or adjust as needed

Alternatively, the old runs will stop appearing after 90 days (GitHub's retention period).

## What's in this Archive
- MT5 Bridge deployment workflows
- VPS auto-healing and monitoring workflows
- MT4 EA deployment workflows
- Emergency restart workflows
- Diagnostic and troubleshooting workflows

## How to Reuse for Another Broker
1. Rename the workflow file from `.yml.disabled` back to `.yml`
2. Move it to `/app/.github/workflows/`
3. Update the VPS IP address and credentials in GitHub Secrets:
   - `VPS_HOST` - New broker's VPS IP
   - `VPS_USERNAME` - SSH username
   - `VPS_PASSWORD` - SSH password
   - `VPS_PORT` - SSH port (usually 22)
4. Update any hardcoded references to `92.118.45.135`
5. Test the workflow with `workflow_dispatch` trigger

## Key Workflows to Consider Reusing
- `deploy-mt5-bridge-emergency.yml.disabled` - Emergency restart via SSH
- `monitor-bridge-health.yml.disabled` - Health monitoring with auto-healing
- `auto-healing-monitor.yml.disabled` - Automatic bridge restart on failure
- `diagnose-vps.yml.disabled` - VPS diagnostics

## Current Active LUCRUM Workflows
The following workflows remain active for LUCRUM:
- `sync-lucrum-accounts-to-mongodb.yml` - Main LUCRUM data sync
- `restart-mt5-sync-lucrum.yml` - Restart LUCRUM sync
- `verify-lucrum-sync.yml` - Verify LUCRUM sync status

## Contact
For questions about reactivating these workflows, refer to SYSTEM_MASTER.md
