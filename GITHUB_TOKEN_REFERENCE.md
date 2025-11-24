# GITHUB_TOKEN Quick Reference Card

**⚠️ SECURITY WARNING: TOKEN REMOVED FROM DOCUMENTATION**

**Token:** `[SECURED - Only visible in GitHub when first created]`
**Token Format:** `[REMOVED_GITHUB_TOKEN]****...****` (44 characters total)

**Purpose:** Enables automatic MT5 Terminal restart via GitHub Actions

**Where to Use:**
- Render Dashboard → Backend Service → Environment Variables
- Key: `GITHUB_TOKEN`
- Value: `[Must be retrieved from GitHub Personal Access Tokens]`

**🔐 SECURITY REQUIREMENTS:**
- **NEVER** store token in code or documentation
- **ONLY** store in Render environment variables (encrypted)
- Token should only be visible when initially created in GitHub

**How to Verify It's Working:**
1. Check Render deployment completed: "Deploy live"
2. Check backend logs: "✅ GITHUB_TOKEN configured"
3. Check email: Should receive alerts at chavapalmarubin@gmail.com
4. Check GitHub Actions: https://github.com/chavapalmarubin-lab/FIDUS/actions

**When to Rotate:**
- Every 90 days (recommended)
- If compromised
- When changing ownership

**Emergency Contact:**
- Email: chavapalmarubin@gmail.com
- See `/app/docs/AUTO_HEALING_SYSTEM.md` for full documentation
