@echo off
echo ==========================================
echo VIKING PRO File Monitor Service
echo Account: 1309411 (Traders Trust)
echo Strategy: PRO
echo ==========================================
echo.
echo Starting file monitor...
echo JSON File: viking_account_1309411_data.json
echo MongoDB Doc: VIKING_1309411
echo.
cd /d C:\viking_bridge
python viking_pro_file_monitor.py
pause
