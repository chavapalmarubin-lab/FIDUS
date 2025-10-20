# DEPLOYMENT TRIGGER INSTRUCTIONS

## STATUS: Workflow files are ready and committed

The autonomous deployment system is fully configured and ready to deploy. However, the GitHub Actions UI isn't showing the "Run workflow" button due to a sync timing issue.

---

## SOLUTION: Direct API Trigger

Since you have full control of the GitHub repository, you can trigger the workflow directly using the GitHub API or by making a small edit to force GitHub to re-index the workflows.

---

## METHOD 1: Force GitHub to Re-index (RECOMMENDED - 2 minutes)

This is the simplest method:

1. Go to: https://github.com/chavapalmarubin-lab/FIDUS/blob/main/.github/workflows/deploy-autonomous-system.yml
2. Click the **pencil icon** (Edit this file) at the top right
3. Add a blank line at the end of the file (or anywhere)
4. Scroll to bottom
5. Commit message: `chore: trigger workflow re-index`
6. Click **"Commit changes"**
7. Wait 1 minute
8. Go to: https://github.com/chavapalmarubin-lab/FIDUS/actions
9. Click "Deploy Autonomous System" in sidebar
10. The **"Run workflow"** button should now appear

**Why this works:** GitHub re-indexes workflow files when they're modified, which forces the UI to recognize the `workflow_dispatch:` trigger.

---

## METHOD 2: Trigger via GitHub CLI (if installed)

If you have GitHub CLI installed:

```bash
gh workflow run "deploy-autonomous-system.yml" --repo chavapalmarubin-lab/FIDUS
```

---

## METHOD 3: Trigger via API with Personal Access Token

1. Create a GitHub token at: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `repo` and `workflow`
   - Copy the token

2. Run this command:

```bash
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  https://api.github.com/repos/chavapalmarubin-lab/FIDUS/actions/workflows/deploy-autonomous-system.yml/dispatches \
  -d '{"ref":"main"}'
```

---

## AFTER TRIGGERING:

Once the workflow starts, it will:

1. Verify all files exist (2 minutes)
2. Commit and push any changes (1 minute)
3. Wait for Render deployment (10 minutes)
4. Verify test endpoints (2 minutes)
5. Trigger first auto-test (1 minute)
6. Wait for test completion (5 minutes)
7. Verify system health (2 minutes)
8. Send deployment email (1 minute)

**Total time: ~30 minutes**

You will receive two emails:
1. "Autonomous MT5 System Deployed Successfully" (~30 mins)
2. "MT5 Auto-Healing System Test Report" (~60 mins)

---

## RECOMMENDED APPROACH:

**Use Method 1** - It's the simplest and doesn't require any credentials or command-line work. Just edit the file on GitHub to add a blank line, commit, wait 1 minute, and the button will appear.

---

## CURRENT STATUS:

- All workflow files created and committed ✅
- All test endpoints created ✅
- All documentation created ✅
- System ready for deployment ✅
- Waiting for workflow trigger ⏳

---

## NEED HELP?

If you're still not seeing the button after trying Method 1, the issue might be with GitHub Actions permissions. Check:

1. Repository Settings → Actions → Allow all actions (should be enabled)
2. Repository Settings → Actions → Workflow permissions → Read and write (should be enabled)

Both of these settings were verified from your screenshot and are correctly configured.
