@echo off
REM FIDUS MT5 Bridge API Service Startup Script
REM Run this script to start the FastAPI REST API service on port 8000

echo ========================================
echo FIDUS MT5 Bridge API Service
echo ========================================

cd /d C:\mt5_bridge_service

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo Installing dependencies...
pip install -q --upgrade pip
pip install -q -r requirements.txt

REM Start the FastAPI service
echo Starting MT5 Bridge API Service on port 8000...
python mt5_bridge_api_service.py

pause
