@echo off
echo ========================================
echo Fix API Routes - Add /api/mt5/accounts
echo ========================================
echo.

cd /d C:\mt5_bridge_service

echo [1/5] Downloading updated service file...
curl -L -o mt5_bridge_api_service.py.new https://raw.githubusercontent.com/chavapalmarubin-lab/FIDUS/main/vps/mt5_bridge_api_service.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to download file
    pause
    exit /b 1
)
echo     SUCCESS
echo.

echo [2/5] Backing up current file...
if exist mt5_bridge_api_service.py (
    copy mt5_bridge_api_service.py mt5_bridge_api_service.py.backup.%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
    echo     SUCCESS
) else (
    echo     No existing file to backup
)
echo.

echo [3/5] Replacing service file...
move /Y mt5_bridge_api_service.py.new mt5_bridge_api_service.py
echo     SUCCESS
echo.

echo [4/5] Restarting service...
schtasks /End /TN "MT5BridgeService" >nul 2>&1
timeout /t 5 /nobreak >nul
taskkill /F /IM python.exe >nul 2>&1
timeout /t 3 /nobreak >nul
schtasks /Run /TN "MT5BridgeService" >nul 2>&1
echo     Service restarted
echo     Waiting 25 seconds...
timeout /t 25 /nobreak >nul
echo     SUCCESS
echo.

echo [5/5] Testing endpoints...
echo.
echo Test 1: Health endpoint
curl -s http://localhost:8000/api/mt5/bridge/health | findstr "healthy"
echo.
echo Test 2: NEW /api/mt5/accounts endpoint
curl -s http://localhost:8000/api/mt5/accounts
echo.
echo.
echo ========================================
echo Fix Complete!
echo ========================================
echo.
echo Endpoints now available:
echo - /api/mt5/bridge/health
echo - /api/mt5/accounts (NEW)
echo - /api/mt5/accounts/summary
echo - /api/mt5/account/{id}/info
echo - /api/mt5/account/{id}/balance
echo - /api/mt5/account/{id}/trades
echo.
pause
