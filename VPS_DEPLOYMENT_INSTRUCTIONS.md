# VPS Deployment Instructions - MT5 Bridge Auto-Healing

## Step 1: Copy the Updated File to VPS

1. Open the file: `/app/CLEAN_VPS_FILE_TO_COPY.py` (this is the clean version without syntax errors)

2. **Copy ALL content** from the file (Ctrl+A, Ctrl+C)

3. On your Windows VPS (92.118.45.135):
   - Navigate to: `C:\mt5_bridge_service\`
   - Open `mt5_bridge_api_service.py` in Notepad or your preferred editor
   - **Select all existing content** (Ctrl+A) and **delete it**
   - **Paste** the new content (Ctrl+V)
   - **Save** the file (Ctrl+S)

## Step 2: Restart the MT5 Bridge Service

Open PowerShell or Command Prompt as Administrator and run:

```powershell
# Stop the service
taskkill /F /IM python.exe

# Wait 3 seconds
timeout /t 3

# Start the service again
cd C:\mt5_bridge_service
python mt5_bridge_api_service.py
```

OR if you're using Task Scheduler:
- Open Task Scheduler
- Find "MT5 Bridge API Service"
- Right-click → End (to stop)
- Right-click → Run (to start)

## Step 3: Verify the New Endpoints

After restarting, test the new endpoints from your local machine or Render backend:

### Test Health Endpoint (should now work):
```bash
curl http://92.118.45.135:8000/api/mt5/bridge/health
```

Expected: JSON response with status, MT5 info, and MongoDB info

### Test Emergency Restart Endpoint (without token - should fail with 401):
```bash
curl -X POST http://92.118.45.135:8000/api/admin/emergency-restart
```

Expected: `{"detail":"Unauthorized"}` (this is correct - means endpoint exists)

### Test One-Time Setup Endpoint:
```bash
curl -X POST "http://92.118.45.135:8000/api/admin/one-time-setup?setup_key=FIDUS_SETUP_2025_ONE_TIME_USE_KEY_XYZ" \
  -H "Content-Type: application/json" \
  -d '{"admin_token":"test-token-123456789012345678901234567890"}'
```

Expected: Success response (if token doesn't exist yet)

## Step 4: What's Next?

Once you confirm the new endpoints are working:

1. **Configure ADMIN_SECRET_TOKEN**: Run the GitHub Actions workflow "Configure VPS Auto-Healing" to securely add the admin token to VPS .env

2. **Test Emergency Restart**: Trigger the "Emergency Restart Hybrid" workflow to verify auto-healing works

3. **Monitor MT5 Watchdog**: Check backend logs to see the watchdog monitoring MT5 Bridge health every 60 seconds

4. **Security Cleanup**: After successful setup, remove the `/api/admin/one-time-setup` endpoint from the code

## Troubleshooting

### Service won't start after update:
- Check logs: `C:\mt5_bridge_service\logs\api_service.log`
- Verify Python version: `python --version` (should be 3.12+)
- Check .env file exists: `C:\mt5_bridge_service\.env`

### Endpoints return 404:
- Service is running old code
- Repeat Step 1 and Step 2 carefully
- Verify the file was actually saved

### "ADMIN_SECRET_TOKEN not configured" error:
- This is expected before running the setup workflow
- The one-time-setup endpoint will add it to .env
- After adding, restart the service

## Need Help?

If you encounter issues:
1. Share the screenshot of the service startup logs
2. Share the output from the curl commands
3. Check if the file content matches exactly (no extra characters)
