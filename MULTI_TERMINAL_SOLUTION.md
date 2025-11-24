# Multi-Terminal MT5 Bridge Solution - LUCRUM Integration

**Date:** November 24, 2025  
**Issue:** Need to sync accounts from multiple brokers (MEXAtlantic + LUCRUM)  
**Challenge:** Each MT5 terminal can only connect to ONE broker at a time  
**Status:** Solution designed, ready to implement  

---

## 🔍 Current Situation Analysis

### What's Working ✅
- **MEXAtlantic Terminal:** Syncing 13 accounts every 120 seconds
- **VPS Location:** 217.197.163.11
- **Bridge Script:** `C:\mt5_bridge_service\mt5_bridge_api_service.py`
- **MongoDB:** Connected and configured
- **Account 2198:** Already in `mt5_account_config` with `is_active: true`

### The Challenge 🎯
**MT5 Terminal Limitation:** Each terminal instance can only connect to accounts from ONE broker server.

**Current Setup:**
```
MEXAtlantic Terminal
├── Connected to: MEXAtlantic-Real server
└── Handles: 13 accounts (all MEXAtlantic)
```

**What We Need:**
```
System with 2 Terminals
├── MEXAtlantic Terminal → 13 MEXAtlantic accounts
└── LUCRUM Terminal → 1 LUCRUM account (2198)
```

---

## ✅ What's Already Configured

### 1. MongoDB - mt5_account_config ✅
```javascript
{
  _id: ObjectId('6920b31d07f4b0d609b1ddf4'),
  account: 2198,
  password: 'Fidus13!',
  name: 'BALANCE - JOSE (LUCRUM)',
  server: 'Lucrumcapital-Live',
  is_active: true,
  broker: 'Lucrum Capital',
  phase: 'Phase 2'
}
```
**Status:** ✅ Ready

### 2. MongoDB - mt5_accounts ✅
```javascript
{
  _id: 'MT5_LUCRUM_2198',
  account: 2198,
  broker: 'Lucrum Capital',
  server: 'Lucrumcapital-Live',
  manager_name: 'JOSE',
  connection_status: 'ready_for_sync',
  data_source: 'VPS_LIVE_MT5',
  phase: 'Phase 2'
}
```
**Status:** ✅ Ready

### 3. LUCRUM Terminal Installed ✅
**Location:** Start Menu > Programs > Lucrum Capital MT5 Terminal  
**Status:** ✅ Installed, not yet started

### 4. Backend Configuration ✅
**File:** `/app/backend/mt5_integration.py`  
**LUCRUM Config:**
```python
"lucrum": {
    "name": "Lucrum Capital",
    "servers": ["Lucrumcapital-Live", "Lucrumcapital-Demo"]
}
```
**Status:** ✅ Ready

---

## 🔧 Solution Options

### Option 1: Dual-Terminal Bridge (Recommended)

**Architecture:**
```
Python Bridge Service (mt5_bridge_api_service.py)
│
├─→ MT5 Terminal 1 (MEXAtlantic)
│   ├── Connects to: MEXAtlantic-Real
│   ├── Port: Default (via MetaTrader API)
│   └── Handles: Accounts from mt5_account_config where server = "MEXAtlantic-Real"
│
└─→ MT5 Terminal 2 (LUCRUM)
    ├── Connects to: Lucrumcapital-Live  
    ├── Port: Default (via MetaTrader API)
    └── Handles: Accounts from mt5_account_config where server = "Lucrumcapital-Live"
```

**How It Works:**
1. Python bridge queries MongoDB for all accounts with `is_active: true`
2. Groups accounts by broker/server
3. For each unique server:
   - Finds corresponding MT5 terminal
   - Initializes connection
   - Retrieves account data
4. Updates MongoDB with fresh data

**Implementation Steps:**

**Step 1: Update Bridge Script**

Modify `mt5_bridge_api_service.py` to support multiple terminals:

```python
import MetaTrader5 as mt5

# Terminal paths
TERMINALS = {
    "MEXAtlantic-Real": {
        "path": r"C:\Program Files\MEXAtlantic MetaTrader 5\terminal64.exe",
        "instance": None
    },
    "Lucrumcapital-Live": {
        "path": r"C:\Program Files\Lucrum Capital MetaTrader 5\terminal64.exe",
        "instance": None
    }
}

def initialize_terminals():
    """Initialize all MT5 terminals"""
    for server, config in TERMINALS.items():
        print(f"Initializing terminal for {server}...")
        # Each terminal is a separate process
        # MT5 Python API can handle multiple terminal connections
        
def sync_account(account_config):
    """Sync single account based on its server"""
    server = account_config['server']
    terminal_path = TERMINALS.get(server, {}).get('path')
    
    if not terminal_path:
        print(f"No terminal configured for server: {server}")
        return
    
    # Initialize connection to appropriate terminal
    if not mt5.initialize(terminal_path):
        print(f"Failed to initialize {terminal_path}")
        return
    
    # Login to account
    if not mt5.login(account_config['account'], 
                     password=account_config['password'], 
                     server=server):
        print(f"Failed to login to {account_config['account']}")
        mt5.shutdown()
        return
    
    # Get account info
    account_info = mt5.account_info()
    balance = account_info.balance
    equity = account_info.equity
    # ... more fields
    
    # Update MongoDB
    db.mt5_accounts.update_one(
        {"account": account_config['account']},
        {"$set": {
            "balance": balance,
            "equity": equity,
            "last_sync_timestamp": datetime.now(),
            "synced_from_vps": True
        }}
    )
    
    # Shutdown terminal connection
    mt5.shutdown()
    print(f"Synced account {account_config['account']}: ${balance}")

def sync_all_accounts():
    """Main sync loop"""
    accounts = list(db.mt5_account_config.find({"is_active": True}))
    
    for account in accounts:
        try:
            sync_account(account)
        except Exception as e:
            print(f"Error syncing {account['account']}: {e}")
    
    print(f"Sync complete: {len(accounts)} accounts")

# Run sync every 120 seconds
while True:
    sync_all_accounts()
    time.sleep(120)
```

**Step 2: Launch LUCRUM Terminal**

On VPS:
1. Open: Start Menu > Lucrum Capital MT5 Terminal
2. Login:
   - Account: 2198
   - Password: Fidus13!
   - Server: Lucrumcapital-Live
3. Keep terminal running (minimized)

**Step 3: Restart Bridge Service**

```powershell
# Stop current service
schtasks /End /TN "MT5BridgeService"

# Restart with updated script
schtasks /Run /TN "MT5BridgeService"
```

**Step 4: Verify Both Terminals Syncing**

Check logs for both broker names:
```
Synced account 886557: $10054.27 (MEXAtlantic)
Synced account 886602: $15924.72 (MEXAtlantic)
...
Synced account 2198: $10000.00 (LUCRUM) ✅
```

---

### Option 2: Separate Bridge Instances (Alternative)

**Architecture:**
```
Bridge 1: MEXAtlantic Bridge
├── Script: mt5_bridge_mexatlantic.py
├── Terminal: MEXAtlantic Terminal
└── Accounts: All MEXAtlantic accounts

Bridge 2: LUCRUM Bridge  
├── Script: mt5_bridge_lucrum.py
├── Terminal: LUCRUM Terminal
└── Accounts: Account 2198
```

**Pros:**
- Complete isolation between brokers
- Easier to debug individual broker issues
- Can run on different schedules

**Cons:**
- More complex to maintain
- Two separate services
- Two sets of logs

---

## 🚀 Recommended Implementation Path

### Phase 1: Launch LUCRUM Terminal (Manual - 2 min)

**Action:** You do this via RDP

1. RDP into VPS: `217.197.163.11`
2. Open: Start Menu > Lucrum Capital MT5 Terminal
3. Login with credentials (account 2198, password Fidus13!, server Lucrumcapital-Live)
4. Minimize terminal (keep running)

---

### Phase 2: Update Bridge Script (Agent/Dev - 30 min)

**Files to Modify:**
- `C:\mt5_bridge_service\mt5_bridge_api_service.py`

**Changes Needed:**
1. Add LUCRUM terminal path to configuration
2. Update sync logic to handle multiple servers
3. Group accounts by server before syncing
4. Initialize appropriate terminal for each account group

**Deployment:**
- Via GitHub Actions OR
- Manual file update on VPS

---

### Phase 3: Test & Verify (5 min)

**Test Steps:**
1. Restart bridge service
2. Wait 2 minutes for sync cycle
3. Check logs for account 2198 entries
4. Query MongoDB to verify `last_sync_timestamp` updated
5. Check dashboard for account 2198

---

## 📋 Current Status Summary

| Component | Status | Notes |
|-----------|--------|-------|
| MongoDB Config | ✅ READY | Account 2198 configured |
| Backend Code | ✅ READY | LUCRUM broker recognized |
| LUCRUM Terminal | 🟡 INSTALLED | Not yet started |
| Bridge Script | 🔴 NEEDS UPDATE | Multi-terminal support needed |
| Documentation | ✅ COMPLETE | All docs updated |

---

## 🎯 What You Can Do vs What Needs Dev Work

### ✅ You Can Do (No Code Changes)

1. **Launch LUCRUM Terminal** (RDP to VPS)
2. **Run "Find Sync Script" workflow** (verify current script)
3. **Verify MongoDB has account 2198** (already confirmed ✅)

### 🔴 Needs Code Changes (Agent/Dev/Emergent)

1. **Update bridge script** for multi-terminal support
2. **Add terminal path configuration** for LUCRUM
3. **Modify sync logic** to route accounts to correct terminal
4. **Test sync** for both brokers
5. **Deploy updated script** to VPS

---

## 💡 Quick Win: File-Based Bridge (Alternative)

If modifying the main bridge is complex, we could use the file-based approach we designed earlier:

**How it works:**
1. LUCRUM terminal writes data to local file (via EA)
2. Separate Python service reads file and updates MongoDB
3. No modification to main bridge needed
4. Isolated from MEXAtlantic sync

**Files:**
- EA: `/app/vps-scripts/MT4_Python_Bridge_FileBased.mq4` (adapt for MT5)
- Monitor: `/app/vps-scripts/mt4_file_monitor.py`

**Pros:**
- No changes to working MEXAtlantic bridge
- Complete isolation
- EA handles terminal connection

**Cons:**
- Requires compiling and installing EA in LUCRUM terminal
- Additional service to manage

---

## 🎯 Recommended Next Steps

### Immediate (You):
1. ✅ RDP into VPS: `217.197.163.11`
2. ✅ Launch LUCRUM terminal
3. ✅ Login to account 2198
4. ✅ Keep terminal running

### Short-term (Emergent/Agent):
1. Assess current bridge script architecture
2. Implement multi-terminal support
3. Deploy updated script
4. Test sync for account 2198
5. Verify dashboard shows 14 total accounts

### Long-term (Nice to Have):
1. Add broker-based routing logic
2. Create unified multi-broker sync architecture
3. Add monitoring for each terminal
4. Auto-restart terminals if they crash

---

## 📞 Technical Details for Emergent

**VPS Details:**
- IP: `217.197.163.11`
- User: (trader or admin user)
- OS: Windows Server

**Current Bridge:**
- Location: `C:\mt5_bridge_service\`
- Main script: `mt5_bridge_api_service.py`
- Sync interval: 120 seconds
- Current accounts: 13 (all MEXAtlantic)

**MongoDB:**
- Connection: `mongodb+srv://chavapalmarubin_db_user:2170Tenoch!@fidus.y1p9be2.mongodb.net/fidus_production`
- Config collection: `mt5_account_config`
- Accounts collection: `mt5_accounts`

**New Account (Already in MongoDB):**
- Account: 2198
- Broker: Lucrum Capital
- Server: Lucrumcapital-Live
- Status: `is_active: true`

**Terminal Paths (Likely):**
- MEXAtlantic: `C:\Program Files\MEXAtlantic MetaTrader 5\terminal64.exe`
- LUCRUM: `C:\Program Files\Lucrum Capital MetaTrader 5\terminal64.exe`

**What's Needed:**
- Update `mt5_bridge_api_service.py` to handle multiple terminals
- Add terminal path mapping by server name
- Group accounts by server before syncing
- Route each account to its broker's terminal

---

## ✅ Success Criteria

**Integration complete when:**

1. ✅ LUCRUM terminal running on VPS
2. ✅ Bridge script handles both MEXAtlantic and LUCRUM
3. ✅ Account 2198 syncs every 120 seconds
4. ✅ MongoDB shows updated `last_sync_timestamp` for 2198
5. ✅ Dashboard displays 14 total accounts (13 MEX + 1 LUCRUM)
6. ✅ JOSE manager visible in Money Managers page
7. ✅ Investment Committee shows 12 MT5 accounts

---

**Document Created:** November 24, 2025  
**Issue:** Multi-terminal support needed  
**Solution:** Update bridge to handle multiple broker terminals  
**Status:** Terminal ready to launch, bridge needs code update
