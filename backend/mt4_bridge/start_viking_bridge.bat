@echo off
REM ============================================================
REM VIKING MT4 Bridge Service Startup Script
REM ============================================================
REM This script starts the VIKING MT4 bridge service on port 8001
REM Completely separate from FIDUS MT5 bridge (port 8000)
REM ============================================================

echo.
echo ============================================================
echo    VIKING MT4 Bridge Service
echo    Port: 8001
echo    Account: 33627673 (MEXAtlantic)
echo ============================================================
echo.

REM Set working directory to script location
cd /d "%~dp0"

REM Check if Python is available
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python not found in PATH
    echo Please install Python 3.8+ and add to PATH
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found
    echo Creating template .env file...
    echo MONGO_URL=your_mongodb_connection_string_here > .env
    echo DB_NAME=fidus_production >> .env
    echo VIKING_BRIDGE_PORT=8001 >> .env
    echo.
    echo Please edit .env file with your MongoDB connection string
    pause
    exit /b 1
)

REM Install dependencies if needed
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -q fastapi uvicorn motor python-dotenv pydantic

REM Start the service
echo.
echo Starting VIKING MT4 Bridge Service...
echo.
python viking_mt4_bridge_service.py

REM Keep window open on error
if %ERRORLEVEL% neq 0 (
    echo.
    echo Service exited with error code %ERRORLEVEL%
    pause
)
