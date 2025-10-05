# 📈 FIDUS MT5 Integration - User Guide

## 🎯 **What is MT5 Integration?**

The FIDUS platform connects directly to MetaTrader 5 (MT5) trading accounts to provide real-time trading data, account balances, and position monitoring. This integration gives you live visibility into client trading performance without manual data entry.

---

## 🔌 **How to Connect an MT5 Account**

### **For Admin Users:**

**Step 1: Access MT5 Management**
1. Log into FIDUS as an admin user
2. Navigate to **Dashboard** → **MetaTrader Data** section
3. Click **"Manage MT5 Accounts"**

**Step 2: Add New MT5 Account**
1. Click **"+ Add MT5 Account"** 
2. Fill in the required information:
   - **Client Name**: Select from existing FIDUS clients
   - **MT5 Login**: The MT5 account number (e.g., 885822)
   - **Broker**: Select broker from dropdown (e.g., MEXAtlantic)
   - **Server**: MT5 server name (e.g., MEXAtlantic-Real-Hedge)
   - **Fund Code**: Investment fund designation

**Step 3: Verify Connection**
1. Click **"Test Connection"** to verify MT5 account access
2. System will show ✅ **Connected** or ❌ **Connection Failed**
3. If connected, live data will start flowing within 2-3 minutes

### **For Client Users:**

**What You'll See:**
- **Account Balance**: Real-time MT5 account balance
- **Equity**: Current account value including open positions
- **Open Positions**: Active trades with profit/loss
- **Trading History**: Recent trading activity and performance

**Data Updates:**
- Account balances update every **5 minutes**
- Position data updates in **real-time**
- History syncs **daily** at midnight

---

## 📊 **MT5 Data in Your Dashboard**

### **Admin Dashboard View:**

**MT5 Account Mappings Table:**
```
Client Name    | MT5 Login | Broker      | Server           | Status
Salvador Palma | 885822    | MEXAtlantic | MEXAtlantic-Real | 🟢 Active
John Smith     | 123456    | DooTech     | DooTech-Live     | 🟢 Active
```

**Performance Overview:**
- Total Assets Under Management (AUM)
- Combined account equity across all clients
- Top performing accounts
- Recent trading activity summary

### **Client Dashboard View:**

**Account Summary Card:**
```
MT5 Account: 885822 (MEXAtlantic)
┌─────────────────────────────────────┐
│ Balance:    $50,000.00             │
│ Equity:     $52,150.75             │
│ P&L Today:  +$1,250.30 (+2.4%)    │ 
│ Positions:  3 Open                 │
└─────────────────────────────────────┘
Last Updated: 2 minutes ago
```

**Open Positions Table:**
```
Symbol | Type | Size  | Entry    | Current  | P&L
EURUSD | BUY  | 1.0   | 1.0850   | 1.0875   | +$250
GBPJPY | SELL | 0.5   | 185.50   | 185.25   | +$125
GOLD   | BUY  | 0.1   | 2650.00  | 2665.00  | +$150
```

---

## 🔧 **Troubleshooting Common Issues**

### **Issue: "MT5 Account Not Connecting"**

**Possible Causes & Solutions:**

1. **Incorrect MT5 Credentials**
   - ✅ **Solution**: Verify MT5 login, password, and server name
   - ✅ **Test**: Try logging into MT5 terminal manually first

2. **MT5 Terminal Not Running**
   - ✅ **Solution**: Ensure MT5 terminal is open and logged in
   - ✅ **Test**: Check if MT5 shows "Connected" in bottom-right corner

3. **Expert Advisor Settings**
   - ✅ **Solution**: In MT5, go to Tools → Options → Expert Advisors
   - ✅ **Enable**: "Allow algorithmic trading" and "Allow DLL imports"
   - ✅ **Disable**: "Disable algorithmic trading via external Python API"

4. **Firewall/Network Issues**
   - ✅ **Solution**: Check if VPS/server firewall allows MT5 API access
   - ✅ **Test**: Contact system administrator for network configuration

### **Issue: "Data Not Updating"**

**Check These Items:**

1. **Connection Status**
   - Look for 🟢 **Active** status next to MT5 account
   - If 🔴 **Disconnected**, click "Reconnect" button

2. **Last Updated Time**
   - Normal: Updates every 2-5 minutes
   - If over 10 minutes old, check MT5 terminal connection

3. **System Status**
   - Admin users: Check **System Status** page for service health
   - Look for any 🔴 **Critical** or 🟡 **Warning** alerts

### **Issue: "Position Data Missing"**

**Troubleshooting Steps:**

1. **Verify MT5 Terminal**
   - Ensure positions are visible in MT5 terminal
   - Check if account has any open trades

2. **Account Permissions** 
   - Verify FIDUS account is linked to correct MT5 login
   - Check if client has proper access permissions

3. **Data Sync Status**
   - Admin users can trigger manual sync from MT5 management page
   - Allow 2-3 minutes for data to appear after sync

---

## ⚠️ **Important Notes**

### **Security & Access:**
- Only **admin users** can configure MT5 connections
- **Client users** can only view their own MT5 data
- All MT5 credentials are encrypted and stored securely
- API connections use secure authentication tokens

### **Data Accuracy:**
- MT5 data reflects real-time trading account status
- Minor delays (1-2 minutes) are normal for data updates  
- Historical data syncs once daily for performance
- Always verify critical data directly in MT5 terminal when needed

### **Trading Operations:**
- FIDUS platform is **read-only** - no trading operations allowed
- Actual trading must be performed directly in MT5 terminal
- Platform shows performance data only, not trading controls

### **Support:**
- For MT5 connection issues: Contact your system administrator
- For FIDUS platform issues: Use in-platform support chat
- For MT5 terminal issues: Contact your broker support

---

## 📞 **Getting Help**

### **Admin Support:**
- **System Status**: Dashboard → System Status → MT5 Service Health
- **Connection Logs**: Available in admin MT5 management section
- **Manual Sync**: Use "Sync All Accounts" button for immediate data refresh

### **Client Support:**
- **Account Status**: Visible on dashboard with connection indicator
- **Data Questions**: Contact your account manager
- **Technical Issues**: Use platform support chat feature

### **Emergency Contacts:**
- **Platform Down**: Check system status page first
- **Data Discrepancies**: Compare with MT5 terminal directly
- **Access Issues**: Contact admin users for account verification

---

**🎯 The MT5 integration is designed to provide seamless, real-time visibility into trading performance while maintaining the security and accuracy of your financial data.**