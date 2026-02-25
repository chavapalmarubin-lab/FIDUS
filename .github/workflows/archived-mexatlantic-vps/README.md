# Archived MEXAtlantic VPS Workflows

## Archive Date: February 24, 2026

## Reason for Archive
These workflows were created to manage the MEXAtlantic MT5 Bridge VPS (92.118.45.135).
FIDUS has transitioned to **LUCRUM-ONLY mode** and the MEXAtlantic VPS is no longer in use.

## What's in this Archive
- MT5 Bridge deployment workflows
- VPS auto-healing and monitoring workflows
- MT4 EA deployment workflows
- Emergency restart workflows
- Diagnostic and troubleshooting workflows

## How to Reuse for Another Broker
1. Copy the relevant workflow file back to `/app/.github/workflows/`
2. Update the VPS IP address and credentials in GitHub Secrets:
   - `VPS_HOST` - New broker's VPS IP
   - `VPS_USERNAME` - SSH username
   - `VPS_PASSWORD` - SSH password
   - `VPS_PORT` - SSH port (usually 22)
3. Update any hardcoded references to `92.118.45.135`
4. Test the workflow with `workflow_dispatch` trigger

## Key Workflows to Consider Reusing
- `deploy-mt5-bridge-emergency.yml` - Emergency restart via SSH
- `monitor-bridge-health.yml` - Health monitoring with auto-healing
- `auto-healing-monitor.yml` - Automatic bridge restart on failure
- `diagnose-vps.yml` - VPS diagnostics

## Current Active LUCRUM Workflows
The following workflows remain active for LUCRUM:
- `sync-lucrum-accounts-to-mongodb.yml` - Main LUCRUM data sync
- `restart-mt5-sync-lucrum.yml` - Restart LUCRUM sync
- `verify-lucrum-sync.yml` - Verify LUCRUM sync status

## Contact
For questions about reactivating these workflows, refer to SYSTEM_MASTER.md
