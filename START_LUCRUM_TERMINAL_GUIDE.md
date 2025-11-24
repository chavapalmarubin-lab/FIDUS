# LUCRUM Capital MT5 Terminal - Launch Guide

**Date:** November 24, 2025  
**Terminal Location:** Start Menu > Programs > Lucrum Capital MT5 Terminal  
**Status:** ✅ Terminal Found - Ready to Launch  

---

## 📍 Terminal Location (Confirmed)

**Start Menu Path:**
```
Microsoft > Windows > Start Menu > Programs > Lucrum Capital MT5 Terminal
```

**Available Shortcuts:**
1. ✅ **Lucrum Capital MT5** ← Use this to launch terminal
2. MetaEditor (for MQL5 programming - not needed)
3. Uninstall (do not use)

---

## 🚀 Step-by-Step Launch Instructions

### Step 1: Launch LUCRUM MT5 Terminal

**Method A: Via Start Menu (Recommended)**
1. Click Windows Start button
2. Navigate to: `Programs > Lucrum Capital MT5 Terminal`
3. Click **"Lucrum Capital MT5"** shortcut
4. Terminal window should open

**Method B: Direct Run**
1. Press `Windows + R` to open Run dialog
2. Type: `terminal64.exe` (if LUCRUM is default MT5)
3. Click OK

**Method C: Desktop Shortcut**
- Look for "Lucrum Capital MT5" icon on desktop
- Double-click to launch

---

### Step 2: Login to Account 2198

Once the terminal opens, you'll see a login dialog:

**Login Credentials:**
```
Login: 2198
Password: ***SANITIZED***
Server: Lucrumcapital-Live
```

**Steps:**
1. **Login field:** Enter `2198`
2. **Password field:** Enter `***SANITIZED***`
3. **Server dropdown:** Select `Lucrumcapital-Live`
4. **Save password checkbox:** ✅ Check this box (so it stays logged in)
5. Click **"Login"** button

---

### Step 3: Verify Successful Login

**What to Check:**

1. **Terminal Title Bar:**
   - Should show: `Lucrum Capital MT5 Terminal - 2198 @ Lucrumcapital-Live`
   - Account number `2198` should be visible

2. **Navigator Window (left side):**
   - Should show account `2198` with green connection icon
   - Status: "Connected"

3. **Terminal Window (bottom):**
   - Check "Trade" tab
   - Should show balance (e.g., $10,000.00)
   - Should show equity

4. **Connection Status (bottom-right corner):**
   - Should show green indicator
   - Shows ping time (e.g., "10ms")
   - NOT showing red "No connection"

**Example of Successful Login:**
```
Account: 2198
Balance: $10,000.00
Equity: $10,000.00
Free Margin: $10,000.00
Margin Level: 0.00%
Server: Lucrumcapital-Live
Status: Connected ✅
```

---

### Step 4: Keep Terminal Running

**CRITICAL:** The terminal must stay running for sync to work!

**Do:**
- ✅ Minimize the terminal window (click minimize button `-`)
- ✅ Leave terminal running in background
- ✅ Let it stay logged in 24/7

**Do NOT:**
- ❌ Close the terminal window (X button)
- ❌ Log out of account 2198
- ❌ Disconnect from server

**Why:** The VPS sync script connects to this running terminal to read account data. If the terminal is closed, sync cannot work.

---

## 🔧 Troubleshooting Login Issues

### Issue 1: "Invalid Account" Error

**Cause:** Account number is incorrect

**Solution:**
- Double-check: Login is `2198` (not 02198 or 2,198)
- Make sure no extra spaces

---

### Issue 2: "Authorization Failed" Error

**Cause:** Wrong password or server

**Solution:**
- Password is case-sensitive: `***SANITIZED***`
  - Capital F
  - Number 1 (not lowercase L)
  - Exclamation mark at end
- Server must be exactly: `Lucrumcapital-Live`

---

### Issue 3: "No Connection" Error

**Cause:** Network issue or server name wrong

**Solution:**
- Check VPS internet connection
- Verify server name: `Lucrumcapital-Live` (capital L in Lucrum and Live)
- Try pinging broker server
- Check firewall settings

---

### Issue 4: Server Not in List

**Cause:** Server needs to be added manually

**Solution:**
1. In login dialog, click **"+"** button next to server dropdown
2. Enter server name: `Lucrumcapital-Live`
3. Click "Scan" to find server
4. Select server from results
5. Click OK
6. Try logging in again

---

## ✅ Verification Checklist

After launching terminal, verify:

- [ ] Terminal window is open
- [ ] Login dialog appeared or auto-logged in
- [ ] Account 2198 is logged in
- [ ] Server shows "Lucrumcapital-Live"
- [ ] Connection status is green (connected)
- [ ] Balance shows in terminal (e.g., $10,000.00)
- [ ] Terminal title bar shows "2198"
- [ ] Terminal is minimized (not closed)

---

## 🎯 What Happens Next

**After terminal is running:**

1. **Immediate:** Terminal is ready for sync
2. **Within 1 minute:** VPS sync script should detect the terminal
3. **Within 2-3 minutes:** Account data will sync to MongoDB
4. **Within 5 minutes:** Account 2198 will appear in dashboard

**Timeline:**
```
Terminal Launch (0 min)
    ↓
VPS Sync Service Restart (2 min) ← Run GitHub workflow
    ↓
First Sync Cycle (3 min) ← Wait
    ↓
Verify Sync (5 min) ← Run verify workflow
    ↓
Check Dashboard (6 min) ← View Investment Committee
```

---

## 🚨 Next Steps After Launch

Once LUCRUM terminal is running and logged in:

### Step 1: Run "Find MT5 Sync Script Location" Workflow
- Go to GitHub Actions
- Run workflow: "Find MT5 Sync Script Location"
- Check output for actual script path
- This helps us verify sync service configuration

### Step 2: Run "Restart MT5 Sync Service" Workflow
- Go to GitHub Actions
- Run workflow: "Restart MT5 Sync Service (Include LUCRUM)"
- This starts the Python sync service
- Service will connect to the LUCRUM terminal you just started

### Step 3: Wait 3 Minutes
- Let sync service initialize
- Let first sync cycle complete
- Python service queries all terminals every ~2 minutes

### Step 4: Run "Verify LUCRUM Account Sync" Workflow
- Go to GitHub Actions
- Run workflow: "Verify LUCRUM Account Sync"
- Check output for "🎉 LUCRUM Account 2198 IS SYNCING!"
- Verify account appears in API response

### Step 5: Check Investment Committee Dashboard
- Open FIDUS platform
- Go to Investment Committee page
- Look for total accounts = 12 (was 11)
- Look for account 2198 with LUCRUM broker
- Verify JOSE manager appears
- Check BALANCE fund increased by ~$10,000

---

## 📊 Expected Results

**When Everything Works:**

**MT5 Terminal:**
```
Lucrum Capital MT5 Terminal - 2198 @ Lucrumcapital-Live
Status: Connected ✅
Balance: $10,000.00
Equity: $10,000.00
```

**Verify Workflow Output:**
```
=== Testing MT5 Bridge API ===
✅ API Response: 14 accounts found
🎉 LUCRUM Account 2198 IS SYNCING!
   Balance: $10,000.00
   Equity: $10,000.00
   Server: Lucrumcapital-Live
```

**Investment Committee Dashboard:**
```
Total Accounts: 12 (was 11)
Total AUM: $128,151.41 (increased)
Active Managers: 6 (includes JOSE)
Account 2198 visible in BALANCE fund list
```

---

## 🔄 Keeping Terminal Running Long-Term

**Best Practices:**

1. **Auto-Start on Boot:**
   - Add LUCRUM MT5 to Windows Startup folder
   - Path: `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\`
   - Create shortcut to LUCRUM terminal in Startup folder

2. **Auto-Login Script:**
   - Configure MT5 to save login credentials
   - Check "Save password" when logging in
   - Terminal will auto-reconnect if disconnected

3. **Windows Task Scheduler:**
   - Create task to launch terminal on system startup
   - Run as user: `trader`
   - Trigger: At system startup

4. **Monitor Terminal:**
   - Check daily that terminal is still running
   - Verify connection status is green
   - Watch for balance updates

---

## 🐛 Common Issues & Fixes

### Terminal Closes Unexpectedly

**Symptom:** Terminal window disappears

**Causes:**
- User accidentally closed it
- Windows Update restarted VPS
- Memory issue crashed terminal

**Solution:**
- Re-launch terminal from Start Menu
- Log back into account 2198
- Run "Restart MT5 Sync Service" workflow

---

### Terminal Shows "No Connection"

**Symptom:** Red "No connection" in bottom-right corner

**Causes:**
- Internet connectivity issue
- Broker server maintenance
- Firewall blocking connection

**Solution:**
- Check VPS internet connection
- Right-click account in Navigator → "Reconnect"
- Wait 30 seconds for auto-reconnect
- If persists, check broker's status page

---

### Sync Works Then Stops

**Symptom:** Account 2198 syncs initially, then data becomes stale

**Causes:**
- Terminal disconnected
- Sync service crashed
- Terminal closed

**Solution:**
1. Check terminal is still running and connected
2. Run "Verify LUCRUM Account Sync" workflow
3. If needed, run "Restart MT5 Sync Service" workflow

---

## 📞 Quick Reference

**Launch Command:**
- Start Menu → Lucrum Capital MT5 Terminal → Lucrum Capital MT5

**Login:**
- Account: `2198`
- Password: `***SANITIZED***`
- Server: `Lucrumcapital-Live`

**Verification:**
- Title bar shows: "2198 @ Lucrumcapital-Live"
- Connection: Green indicator ✅
- Balance: Visible in Terminal tab

**Keep Running:**
- Minimize (don't close)
- Stay logged in
- Leave connected 24/7

---

## ✅ Success Confirmation

**You'll know it's working when:**

1. ✅ LUCRUM terminal shows connected status
2. ✅ Account 2198 balance visible in terminal
3. ✅ "Verify" workflow shows account 2198 in API
4. ✅ Dashboard shows 12 total accounts
5. ✅ JOSE manager appears in Money Managers
6. ✅ Sync logs show recent activity with 2198

**Current Status:** Terminal location confirmed ✅  
**Next Action:** Launch terminal and log into account 2198  
**Time Required:** 5 minutes  

---

**Guide Created:** November 24, 2025  
**Terminal Location:** Confirmed in Start Menu  
**Ready to Launch:** YES ✅
