@echo off
REM FIDUS MT5 Bridge - Enhanced Run Script with Auto-Update
REM Location: C:\mt5_bridge_service\run_mt5_bridge.bat
REM
REM This script:
REM 1. Pulls latest code from GitHub (quiet mode)
REM 2. Runs the MT5 bridge service
REM 3. Logs all output

cd /d C:\mt5_bridge_service

REM Pull latest code from GitHub (quiet mode, don't fail if no changes)
git pull origin main --quiet 2>nul

REM Set Python path
SET PYTHON_PATH=C:\Users\Administrator\AppData\Local\Programs\Python\Python312

REM Check if Python exists
if not exist "%PYTHON_PATH%\python.exe" (
    echo ERROR: Python not found at %PYTHON_PATH%
    echo Please update PYTHON_PATH in this script
    exit /b 1
)

REM Run the bridge with logging
"%PYTHON_PATH%\python.exe" mt5_bridge_service_production.py >> logs\service_output.log 2>> logs\service_error.log

exit /b %ERRORLEVEL%
