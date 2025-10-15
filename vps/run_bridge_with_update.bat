@echo off
REM FIDUS MT5 Bridge Service - Enhanced Run Script
REM Location: C:\mt5_bridge_service\run_bridge_with_update.bat
REM
REM This script:
REM 1. Pulls latest code from GitHub (auto-update)
REM 2. Runs the MT5 bridge service
REM 3. Logs all output
REM
REM Scheduled via Windows Task Scheduler every 5 minutes

echo ================================================
echo FIDUS MT5 Bridge Service - Starting
echo Time: %date% %time%
echo ================================================

cd /d C:\mt5_bridge_service

REM Create logs directory if it doesn't exist
if not exist logs mkdir logs

REM Step 1: Auto-update from GitHub
echo.
echo [1/2] Checking for code updates from GitHub...
powershell.exe -ExecutionPolicy Bypass -File auto_update.ps1

REM Step 2: Run the bridge service
echo.
echo [2/2] Starting MT5 bridge service...
SET PYTHON_PATH=C:\Users\Administrator\AppData\Local\Programs\Python\Python312

REM Check if Python exists
if not exist "%PYTHON_PATH%\python.exe" (
    echo ERROR: Python not found at %PYTHON_PATH%
    echo Please update PYTHON_PATH in this script
    pause
    exit /b 1
)

REM Run the bridge with logging
"%PYTHON_PATH%\python.exe" mt5_bridge_service_production.py >> logs\service_output.log 2>> logs\service_error.log

REM Capture exit code
set EXITCODE=%ERRORLEVEL%

echo.
echo ================================================
echo Bridge service completed with code: %EXITCODE%
echo Time: %date% %time%
echo ================================================
echo.

exit /b %EXITCODE%
