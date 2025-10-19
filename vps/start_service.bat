@echo off
REM MT5 Bridge API Service Startup Script
REM This script starts the MT5 Bridge API service with proper logging

echo ========================================
echo FIDUS MT5 Bridge API Service
echo ========================================
echo Starting service on port 8000...
echo.

REM Create logs directory if it doesn't exist
if not exist logs mkdir logs

REM Start the Python service
python mt5_bridge_api_service.py

REM If we reach here, the service has stopped
echo.
echo Service has stopped. Check logs\api_service.log for details.
pause
