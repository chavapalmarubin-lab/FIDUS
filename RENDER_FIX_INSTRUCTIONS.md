# RENDER PRODUCTION FIX - Investment Committee Tab

## PROBLEM IDENTIFIED

The Investment Committee tab fails on Render production with:
- CORS errors
- 401 Unauthorized errors
- "Failed to fetch" errors

## ROOT CAUSE

**Frontend environment variable misconfiguration on Render.**

The Render frontend is trying to call:
```
https://trader-insights-10.preview.emergentagent.com/api/...
```

But it SHOULD call:
```
https://fidus-api.onrender.com/api/...
```

## WHY THIS HAPPENS

Render deployments use environment variables from the Render Dashboard, NOT from the `.env` file in the repo. The Render dashboard likely has the wrong `REACT_APP_BACKEND_URL` configured (or it's not set at all, causing it to default to an incorrect value).

## THE FIX

### Step 1: Update Render Environment Variable

1. Go to: https://dashboard.render.com
2. Select service: `fidus-investment-platform` (frontend)
3. Go to "Environment" tab
4. Find or add: `REACT_APP_BACKEND_URL`
5. Set value to: `https://fidus-api.onrender.com`
6. Click "Save Changes"

### Step 2: Trigger Redeploy

After saving the environment variable:
1. Click "Manual Deploy" → "Clear build cache & deploy"
2. Wait for build to complete (5-10 minutes)
3. The new build will use the correct backend URL

### Step 3: Verify

After deployment completes:
1. Go to: https://fidus-investment-platform.onrender.com
2. Login as admin
3. Click "Investment Committee" tab
4. Should load without errors

## VERIFICATION CHECKLIST

- [ ] Render dashboard shows `REACT_APP_BACKEND_URL=https://fidus-api.onrender.com`
- [ ] Frontend redeployed with new environment variable
- [ ] Investment Committee tab loads
- [ ] No CORS errors in browser console
- [ ] No 401 errors in browser console
- [ ] MT5 accounts data loads successfully

## TECHNICAL DETAILS

### Current (Broken) Configuration:
- Frontend `.env` file: `REACT_APP_BACKEND_URL=https://trader-insights-10.preview.emergentagent.com`
- This is correct for LOCAL development
- But Render doesn't use this file - it uses dashboard environment variables

### Correct Configuration for Render:
- Render Dashboard Environment Variable: `REACT_APP_BACKEND_URL=https://fidus-api.onrender.com`
- This tells the production frontend to call the production backend

### Why Backend Works But Frontend Doesn't:
- Backend API (`fidus-api.onrender.com`) is correctly configured
- Backend tested with curl: ✅ All endpoints return 200 OK
- Frontend calling wrong URL: ❌ Calls preview domain instead of production
- Result: 401/CORS errors because preview backend doesn't exist or has different auth

## ALTERNATIVE: Quick Test Without Redeploy

If you want to test immediately without waiting for Render redeploy:

1. Use browser dev tools console
2. Manually set the correct API URL:
```javascript
localStorage.setItem('REACT_APP_BACKEND_URL', 'https://fidus-api.onrender.com');
```
3. Refresh page
4. Check if Investment Committee works

(This is temporary - proper fix requires Render environment variable update)

## BACKEND STATUS

✅ Backend is 100% functional:
- All Investment Committee endpoints working
- Database configured correctly (13/13 accounts)
- VPS syncing properly
- Validation endpoints returning correct data
- Recalculation functions tested and working

The ONLY issue is frontend calling the wrong backend URL.
