# 🚀 MT5 Integration Troubleshooting Guide
**Comprehensive Documentation for Monday CTO Session**

## 📊 Current System Status (as of Oct 4, 2025)

### ✅ **What's Working**
- **MT5 Bridge Service**: Running on Windows VPS (217.197.163.11:8000) localhost ✅
- **FIDUS Backend Integration**: 71.4% success rate (5/7 MT5 endpoints working) ✅
- **Service Architecture**: FastAPI bridge service with all dependencies installed ✅
- **Automatic Startup**: Configured via Windows Startup folder ✅
- **Authentication**: API key security implemented ✅

### ❌ **Primary Issues to Resolve**

#### 1. **MT5 Python Connection Issue** (CRITICAL)
```json
{
  "mt5_available": false,
  "mt5_initialized": false
}
```

#### 2. **External VPS Access** (BLOCKED)
- ForexVPS firewall blocking port 8000
- Support ticket submitted - awaiting response

---

## 🔧 **Detailed Troubleshooting Plan**

### **Phase 1: MT5 Python Package Diagnostics**

#### **Step 1.1: Basic Connection Test**
On VPS, open Command Prompt and run:
```cmd
cd C:\fidus_mt5_bridge
python
```

Then execute these commands:
```python
import MetaTrader5 as mt5
print(f"MT5 Package Version: {mt5.__version__ if hasattr(mt5, '__version__') else 'Unknown'}")

# Test initialization
result = mt5.initialize()
print(f"Initialize Result: {result}")

if result:
    print("✅ MT5 Connection Successful!")
    
    # Get terminal info
    terminal_info = mt5.terminal_info()
    if terminal_info:
        print(f"Terminal Name: {terminal_info.name}")
        print(f"Terminal Build: {terminal_info.build}")
        print(f"Terminal Connected: {terminal_info.connected}")
        print(f"Terminal Path: {terminal_info.path}")
        print(f"Trade Allowed: {terminal_info.trade_allowed}")
    
    # Get account info
    account_info = mt5.account_info()
    if account_info:
        print(f"Account Login: {account_info.login}")
        print(f"Account Server: {account_info.server}")
        print(f"Account Balance: {account_info.balance}")
        print(f"Account Currency: {account_info.currency}")
    
    mt5.shutdown()
else:
    error = mt5.last_error()
    print(f"❌ MT5 Connection Failed: {error}")
    print(f"Error Code: {error[0] if error else 'No error code'}")
    print(f"Error Description: {error[1] if len(error) > 1 else 'No description'}")

exit()
```

#### **Step 1.2: Administrator Rights Check**
If Step 1.1 fails:
1. Close MT5 terminal completely
2. Right-click MT5 shortcut → "Run as Administrator"
3. Log into account 885822
4. Repeat Step 1.1

#### **Step 1.3: MT5 Terminal Configuration Verification**
In MT5 Terminal:
1. **Tools → Options → Expert Advisors**
2. Verify these settings:
   - ✅ "Allow algorithmic trading" 
   - ✅ "Allow DLL imports"
   - ✅ "Allow imports of external experts"
   - ❌ "Disable algorithmic trading via external Python API" (must be UNCHECKED)
3. **Click OK** and restart MT5 terminal
4. Repeat Step 1.1

### **Phase 2: Python Environment Diagnostics**

#### **Step 2.1: Package Version Check**
```cmd
pip show MetaTrader5
pip list | find "MetaTrader5"
```

#### **Step 2.2: Reinstall MT5 Package** (if needed)
```cmd
pip uninstall MetaTrader5
pip install MetaTrader5==5.0.47
```

#### **Step 2.3: Python Path Check**
```cmd
python -c "import sys; print('\n'.join(sys.path))"
where python
```

### **Phase 3: Advanced Diagnostics**

#### **Step 3.1: MT5 Terminal Logs Analysis**
Check MT5 logs for Python API attempts:
- **Location**: `C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\<Terminal_ID>\Logs\`
- **Look for**: API connection attempts, Python-related errors

#### **Step 3.2: Windows Compatibility Check**
```cmd
python -c "
import platform
print(f'Python Version: {platform.python_version()}')
print(f'Architecture: {platform.architecture()}')
print(f'Windows Version: {platform.platform()}')
"
```

#### **Step 3.3: Process Interaction Test**
```cmd
tasklist | find "terminal64.exe"
tasklist | find "python.exe"
```

---

## 🎯 **Expected Outcomes & Solutions**

### **Scenario A: Permission/Rights Issue**
- **Symptoms**: MT5 works manually but Python can't connect
- **Solution**: Run both MT5 and Python bridge service as Administrator
- **Implementation**: Update startup script to run as Administrator

### **Scenario B: Package Version Mismatch**
- **Symptoms**: Import works but `mt5.initialize()` returns False
- **Solution**: Reinstall compatible MetaTrader5 package version
- **Implementation**: Use specific version that matches MT5 terminal build

### **Scenario C: Terminal Configuration Issue**
- **Symptoms**: Connection works sometimes but not consistently  
- **Solution**: Correct Expert Advisor settings and restart terminal
- **Implementation**: Document exact configuration steps

### **Scenario D: Account/Server Issue**
- **Symptoms**: Terminal connects but Python sees no account
- **Solution**: Use different trading account or server
- **Implementation**: Test with demo account first

---

## 📁 **Critical Files & Locations**

### **On Windows VPS (217.197.163.11):**
```
C:\fidus_mt5_bridge\
├── main_production.py          # Main bridge service
├── requirements.txt            # Python dependencies  
├── .env                       # Configuration file
├── start_mt5_bridge.bat       # Startup script
└── logs\                      # Service logs
    └── mt5_bridge_YYYYMMDD.log
```

### **MT5 Terminal Locations:**
```
C:\Program Files\MetaTrader 5\  # MT5 installation
C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\  # MT5 data
```

### **Startup Configuration:**
```
C:\Users\Administrator\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\
└── start_mt5_bridge.bat       # Auto-start script
```

---

## 🚨 **Backup Plans**

### **Plan A: Alternative MT5 Package**
If current MetaTrader5 package fails:
- Try older version: `pip install MetaTrader5==5.0.45`
- Try development version from source

### **Plan B: Manual Trading Account**  
If Python API fails completely:
- Implement manual account data entry system
- Create scheduled synchronization process
- Use MT5 export/import functionality

### **Plan C: Alternative Trading Platform**
If MT5 integration is impossible:
- Evaluate cTrader API integration
- Consider TradingView API for data feeds
- Implement CSV import system for trading data

---

## 🔍 **Post-Resolution Validation**

Once MT5 connection is working:

### **Step 1: Service Validation**
```bash
# Test bridge service endpoint
curl http://localhost:8000
# Should show: "mt5_available": true
```

### **Step 2: FIDUS Integration Test**  
```bash
# Test from FIDUS backend
curl -X GET "https://fidus-invest.emergent.host/api/mt5/brokers" \
  -H "Authorization: Bearer <admin_token>"
```

### **Step 3: End-to-End Workflow**
1. Create test MT5 account in FIDUS
2. Verify position data flows correctly  
3. Test account balance synchronization
4. Validate trading history import

---

## 📞 **Support Contacts & Resources**

### **ForexVPS Support**
- **Issue**: Port 8000 external access blocked
- **Status**: Support ticket submitted
- **Follow-up**: Check email for response

### **MT5 Documentation**
- **Python API**: [MQL5 Documentation](https://www.mql5.com/en/docs/integration/python_metatrader5)
- **Package Issues**: MetaTrader5 Python package GitHub issues

### **Emergency Contacts**
- **Emergent Platform**: Integration support available
- **FIDUS Backend**: All endpoints configured and ready

---

## ✅ **Success Criteria**

By end of Monday session:
1. ✅ **MT5 Python Connection**: `"mt5_available": true` in service response
2. ✅ **Account Data Access**: Ability to fetch account info, positions, history
3. ✅ **Service Reliability**: Bridge service runs continuously without errors  
4. ✅ **FIDUS Integration**: All MT5 endpoints return real data instead of mocks

**Target: 100% MT5 integration success rate (currently at 71.4%)**