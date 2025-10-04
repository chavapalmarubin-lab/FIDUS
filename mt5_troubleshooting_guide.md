# MT5 Connection Troubleshooting Guide
**For Monday Session with CTO**

## Current Status
- ✅ MT5 Bridge Service: Running on VPS localhost:8000
- ✅ MetaTrader5 Package: Installed successfully 
- ✅ MT5 Terminal: Installed and running (Account: 885822)
- ❌ Python-MT5 Connection: Not detecting MT5 terminal

## Issue Description
Service response shows:
```json
{
  "mt5_available": false,
  "mt5_initialized": false
}
```

## MT5 Terminal Configuration
- **Account**: 885822 (switched from 8966602)
- **Status**: Connected and showing live prices
- **Expert Advisors Settings**:
  - ✅ "Allow algorithmic trading" enabled
  - ✅ "Allow DLL imports" enabled 
  - ✅ "Disable algorithmic trading via external Python API" disabled

## Troubleshooting Steps to Try
1. **Verify MT5 Terminal is fully logged in**
2. **Check if MT5 terminal needs to be run as Administrator**
3. **Test direct Python MT5 connection**:
   ```python
   import MetaTrader5 as mt5
   result = mt5.initialize()
   print(f"Initialize result: {result}")
   if result:
       terminal_info = mt5.terminal_info()
       print(f"Connected: {terminal_info.connected}")
   ```
4. **Check MT5 terminal logs for API access attempts**
5. **Verify MetaTrader5 Python package version compatibility**

## Expected Resolution
Once Python can connect to MT5 terminal:
- Service should show `"mt5_available": true`
- Service should show `"mt5_initialized": true`
- All MT5 API endpoints will become functional

## Files Location on VPS
- Bridge Service: `C:\fidus_mt5_bridge\main_production.py`
- Configuration: `C:\fidus_mt5_bridge\.env`
- Logs: `C:\fidus_mt5_bridge\logs\`