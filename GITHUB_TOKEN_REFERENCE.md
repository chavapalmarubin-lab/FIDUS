# GITHUB_TOKEN Quick Reference Card

**Token:** `[REVOKED_TOKEN]`

**Purpose:** Enables automatic MT5 Terminal restart via GitHub Actions

**Where to Use:**
- Render Dashboard → Backend Service → Environment Variables
- Key: `GITHUB_TOKEN`
- Value: (paste token above)

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
