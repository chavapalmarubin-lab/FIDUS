@echo off
echo ========================================
echo MongoDB Connection Fix
echo ========================================
echo.

cd /d C:\mt5_bridge_service

echo [1/5] Backing up .env...
if exist .env (
    copy .env .env.backup.%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
    echo     SUCCESS
) else (
    echo     No existing .env
)

echo.
echo [2/5] Creating new .env with correct MongoDB credentials...
(
echo MONGODB_URI=mongodb+srv://chavapalmarubin_db_user:2170Tenoch%%21@fidus.ylp9be2.mongodb.net/fidus_production?retryWrites=true^&w=majority^&appName=FIDUS
echo MONGODB_DATABASE=fidus_production
echo MT5_PATH=C:\Program Files\MEX Atlantic MT5 Terminal\terminal64.exe
echo MT5_SERVER=MEXAtlantic-Real
echo MT5_PASSWORD=Fidus13!
echo MT5_ACCOUNTS=886557,886066,886602,885822,886528,891215,891234
echo SYNC_INTERVAL=300
echo LOG_LEVEL=INFO
echo API_PORT=8000
) > .env
echo     SUCCESS

echo.
echo [3/5] Stopping service...
schtasks /End /TN "MT5BridgeService" >nul 2>&1
timeout /t 5 /nobreak >nul
taskkill /F /IM python.exe >nul 2>&1
timeout /t 3 /nobreak >nul
echo     SUCCESS

echo.
echo [4/5] Starting service...
schtasks /Run /TN "MT5BridgeService" >nul 2>&1
echo     Waiting 20 seconds...
timeout /t 20 /nobreak >nul
echo     SUCCESS

echo.
echo [5/5] Testing MongoDB connection...
curl -s http://localhost:8000/api/mt5/bridge/health
echo.
echo.
echo ========================================
echo Check above for "connected":true
echo ========================================
pause
