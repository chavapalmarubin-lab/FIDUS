@echo off
REM MT5 Bridge Service Enhanced - Startup Script
REM Windows Batch File with UTF-8 encoding support
REM Location: C:\mt5_bridge_service\start_enhanced_service.bat

REM Set UTF-8 encoding to prevent Unicode errors
set PYTHONIOENCODING=utf-8

REM Change to service directory
cd /d C:\mt5_bridge_service

REM Create logs directory if it doesn't exist
if not exist logs mkdir logs

REM Display startup message
echo [START] MT5 Bridge Service Enhanced starting...
echo [TIME] %date% %time%

REM Run Python script with logging
python mt5_bridge_service_enhanced.py >> logs\service.log 2>&1

REM If script exits, log it
echo [EXIT] Service stopped at %date% %time% >> logs\service.log
