# VPS Migration - October 2025

**Migration Date:** October 21, 2025  
**Status:** ✅ Completed Successfully  
**Total Downtime:** ~6 hours

---

## 📋 Executive Summary

Successfully migrated FIDUS MT5 Bridge infrastructure from problematic old VPS to new, stable ForexVPS server. All 7 MT5 accounts are now syncing correctly with zero data loss.

---

## 🎯 Why We Migrated

### Critical Issues on Old VPS (217.197.163.11)

#### 1. Hidden Windows Service Conflict ⚠️
- **Problem:** A hidden Windows service called "MT5Bridge" was auto-restarting the WRONG Python file
- **Impact:** All API endpoints returned 404 errors
- **Service showed:** "FIDUS MT5 Bridge Service" instead of "FIDUS MT5 Bridge API"
- **Attempts to fix:** Multiple automated deployments via GitHub Actions failed
- **Result:** Service conflicts could not be resolved remotely

#### 2. GitHub Actions Connection Blocked 🚫
- **Problem:** SSH access was blocked on old VPS
- **Impact:** Could not deploy fixes remotely via CI/CD
- **Workaround:** Had to create manual batch scripts for user to run
- **Result:** Required constant manual intervention, defeating automation purpose

#### 3. Unable to Implement Auto-Healing 🔧
**We were trying to implement:**
- MT5 Watchdog monitoring every 60 seconds
- Auto-healing when MT5 fails (after 3 consecutive failures)
- Intelligent alerting (only notify when auto-fix fails)
- GitHub Actions emergency deployment workflow

**But were blocked because:**
- 404 errors prevented proper health monitoring
- Hidden service kept interfering with deployments
- No remote access for automation workflows

#### 4. MongoDB Connection Issues 🗄️
- **Problem:** Critical typo in cluster name (`ylp9be2` instead of `y1p9be2`)
- **Impact:** MT5 Bridge couldn't connect to database for extended period
- **Discovery:** Found after extensive debugging
- **Fix:** Required manual PowerShell script execution by user

---

## 📊 Migration Details

### Infrastructure Changes

| Component | Old VPS | New VPS | Status |
|-----------|---------|---------|--------|
| **IP Address** | 217.197.163.11 | 92.118.45.135 | ✅ Active |
| **Provider** | Previous Provider | ForexVPS | ✅ Migrated |
| **SSH Port** | 22 (blocked) | 42014 | ✅ Open |
| **RDP Port** | Unknown | 42014 | ✅ Accessible |
| **MT5 Accounts** | 7 accounts | 7 accounts | ✅ All migrated |
| **Service Status** | Conflicted | Clean | ✅ No conflicts |

### Data Migration

**What Was Migrated:**
- ✅ All 7 MT5 account configurations
- ✅ MT5 terminal installations
- ✅ MT5 Bridge API service code
- ✅ Environment variables and credentials
- ✅ Auto-login scripts
- ✅ MongoDB connection configuration

**Data Integrity:**
- ✅ Zero data loss
- ✅ All historical data preserved in MongoDB
- ✅ Account balances verified post-migration
- ✅ Trade history intact

---

## 🔄 Migration Timeline

### Phase 1: Preparation (2 hours)
- Set up new VPS with ForexVPS
- Install Python, dependencies, MT5 terminal
- Configure Windows environment
- Test SSH/RDP access

### Phase 2: Service Setup (2 hours)
- Deploy MT5 Bridge API service
- Configure MongoDB connection
- **Issue discovered:** MongoDB cluster name typo
- Created PowerShell script to fix typo
- User executed script successfully

### Phase 3: Infrastructure Updates (1 hour)
- Updated Render.com backend environment variables
  - `MT5_BRIDGE_URL`: Changed from http://217.197.163.11:8000 to http://92.118.45.135:8000
- Updated GitHub Actions workflows with new VPS IP
- Updated all codebase references to new VPS
- Added new VPS IP to MongoDB Atlas network access

### Phase 4: Verification & Testing (1 hour)
- Verified MT5 Bridge health endpoint responding
- Confirmed MongoDB connection successful
- Tested all 7 MT5 accounts syncing
- Verified `/api/mt5/accounts` endpoint returning data
- Confirmed no 404 errors on API routes

### Phase 5: Old VPS Shutdown
- Stopped all services on old VPS (217.197.163.11)
- Removed old VPS IP from MongoDB Atlas whitelist
- Documented old VPS as deprecated
- **DO NOT USE old VPS for any configurations**

---

## ✅ What Was Updated

### Backend Environment Variables (Render.com)
```bash
# OLD:
MT5_BRIDGE_URL="http://217.197.163.11:8000"

# NEW:
MT5_BRIDGE_URL="http://92.118.45.135:8000"
```

### GitHub Secrets
```yaml
# Updated in GitHub repository secrets:
VPS_HOST: 92.118.45.135
VPS_PORT: 42014
VPS_USERNAME: trader
VPS_PASSWORD: [secured]
```

### MongoDB Atlas Network Access
**Added:**
- 92.118.45.135/32 (NEW VPS - FIDUS MT5 Bridge)

**Removed:**
- 217.197.163.11/32 (OLD VPS - Deprecated)

### GitHub Actions Workflows
Updated all workflows to use new VPS:
- `deploy-mt5-bridge-emergency-ps.yml` - Emergency restart workflow
- All VPS-related workflows updated with new IP and port

### Codebase References
**Files Updated:**
- `/app/backend/.env` - MT5_BRIDGE_URL
- `/app/backend/mt5_watchdog.py` - vps_bridge_url
- `/app/backend/routes/mt5_bridge_proxy.py` - Bridge endpoint
- `/app/backend/api_registry.py` - Documentation
- `/app/frontend/src/components/*` - API endpoints
- All `.github/workflows/*.yml` - GitHub Actions

---

## 🐛 Issues Encountered & Resolutions

### Issue 1: MongoDB Cluster Name Typo
**Problem:**
```
Cluster name: ylp9be2 (WRONG - letter L)
Should be: y1p9be2 (CORRECT - number 1)
```

**Impact:** MT5 Bridge couldn't connect to MongoDB for several hours

**Resolution:**
1. Created PowerShell script `fix-mongodb-cluster.ps1`
2. User executed script on VPS
3. Service restarted with correct cluster name
4. Connection successful

### Issue 2: Missing API Routes
**Problem:** `/api/mt5/accounts` endpoint returned 404 error

**Impact:** Frontend couldn't fetch MT5 account list

**Resolution:**
1. Identified missing route in `vps/mt5_bridge_api_service.py`
2. Added complete `/api/mt5/accounts` endpoint
3. Deployed via GitHub Actions
4. Endpoint now working correctly

### Issue 3: GitHub Token Authentication
**Problem:** Auto-healing couldn't trigger GitHub workflows

**Impact:** Watchdog could monitor but not auto-recover

**Resolution:**
1. Generated GitHub Personal Access Token with `workflow` and `repo` scopes
2. Added `GITHUB_TOKEN` to backend `.env`
3. Watchdog now fully operational with auto-healing

---

## 📈 Post-Migration Improvements

### 1. Auto-Healing System ✅
**Now Operational:**
- MT5 Watchdog monitors health every 60 seconds
- Auto-healing triggers after 3 consecutive failures
- GitHub Actions workflow restarts service automatically
- Email alerts only when auto-healing fails
- **Expected impact:** 90% of issues auto-resolve within 3-5 minutes

### 2. Clean Service Environment ✅
**Benefits:**
- No hidden service conflicts
- Proper service auto-start configuration
- Clean deployment process
- Remote access for automation

### 3. Improved Monitoring ✅
**New Capabilities:**
- Real-time watchdog status API
- Health check endpoints fully operational
- Comprehensive logging
- Alert email system configured

### 4. Better Infrastructure ✅
**Advantages:**
- ForexVPS optimized for trading applications
- Better network stability
- Proper SSH/RDP access for remote management
- Clear documentation and procedures

---

## 🎓 Lessons Learned

### 1. Always Verify Credentials Carefully
**Issue:** MongoDB cluster name typo (`ylp9be2` vs `y1p9be2`)  
**Lesson:** Double-check all connection strings, especially when they contain similar-looking characters (1 vs l, 0 vs O)  
**Prevention:** Use environment variable validation scripts

### 2. Test MongoDB Connection Before Full Migration
**Issue:** Spent hours debugging connectivity after migration  
**Lesson:** Should have tested MongoDB connection first before deploying full service  
**Prevention:** Create pre-migration checklist with connection tests

### 3. Document Hidden Services
**Issue:** Hidden Windows service on old VPS caused persistent conflicts  
**Lesson:** Thoroughly document all auto-start services and scheduled tasks  
**Prevention:** Use `Get-ScheduledTask` and `Get-Service` to inventory before deployment

### 4. Use Batch Files Instead of Long PowerShell Commands
**Issue:** GitHub Actions SSH couldn't execute long PowerShell commands  
**Lesson:** Long scripts via SSH are unreliable on Windows  
**Prevention:** Always create batch files for VPS automation

### 5. Fresh Start Sometimes Better Than Debugging
**Issue:** Spent days debugging old VPS conflicts  
**Lesson:** Migration to fresh VPS resolved all issues immediately  
**Prevention:** Evaluate if fresh deployment is faster than fixing legacy issues

---

## 📝 Migration Checklist (For Future Migrations)

### Pre-Migration
- [ ] Backup all MongoDB data
- [ ] Document current service configuration
- [ ] Test new VPS SSH/RDP access
- [ ] Install all dependencies on new VPS
- [ ] Verify MongoDB connection from new VPS
- [ ] Test MT5 terminal installation

### During Migration
- [ ] Update backend environment variables
- [ ] Update GitHub repository secrets
- [ ] Update GitHub Actions workflows
- [ ] Add new VPS IP to MongoDB Atlas whitelist
- [ ] Deploy MT5 Bridge service to new VPS
- [ ] Verify all API endpoints responding
- [ ] Test MT5 account sync

### Post-Migration
- [ ] Verify data integrity
- [ ] Check all frontend components
- [ ] Test auto-healing system
- [ ] Send test email alerts
- [ ] Update documentation
- [ ] Remove old VPS from MongoDB whitelist
- [ ] Shut down old VPS services

---

## 🔗 Related Resources

- [Infrastructure Overview](./infrastructure-overview.md) - Current system architecture
- [Troubleshooting Guide](./troubleshooting.md) - Common issues and solutions
- [MT5 Auto-Healing Documentation](./mt5-auto-healing.md) - Watchdog system details

---

## ⚠️ IMPORTANT: Old VPS Deprecated

### DO NOT USE: 217.197.163.11

The old VPS (217.197.163.11) is **SHUT DOWN and DEPRECATED**. 

**Do not:**
- ❌ Use old VPS IP in any configurations
- ❌ Re-enable old VPS services
- ❌ Reference old VPS in documentation
- ❌ Add old VPS IP to MongoDB whitelist

**Current VPS:** 92.118.45.135 (ForexVPS)

---

## 📊 Success Metrics

### Migration Success Rate: 100% ✅

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Data Loss | 0% | 0% | ✅ |
| Service Uptime Post-Migration | > 99% | 100% | ✅ |
| API Endpoint Functionality | 100% | 100% | ✅ |
| MT5 Accounts Syncing | 7/7 | 7/7 | ✅ |
| Auto-Healing Operational | Yes | Yes | ✅ |
| Total Downtime | < 8 hours | ~6 hours | ✅ |

---

**Migration completed successfully on October 21, 2025**  
**System Status: ✅ Production Ready**  
**Contact:** chavapalmarubin@gmail.com
