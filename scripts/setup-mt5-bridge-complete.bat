@echo off
echo ========================================
echo MT5 Bridge Service - Complete Setup
echo NEW VPS: 92.118.45.135
echo ========================================
echo.

REM Step 1: Create directory structure
echo [1/8] Creating directory structure...
if not exist "C:\mt5_bridge_service" mkdir "C:\mt5_bridge_service"
if not exist "C:\mt5_bridge_service\logs" mkdir "C:\mt5_bridge_service\logs"
cd /d C:\mt5_bridge_service
echo     SUCCESS
echo.

REM Step 2: Download mt5_bridge_api_service.py
echo [2/8] Downloading MT5 Bridge service file...
curl -L -o mt5_bridge_api_service.py https://raw.githubusercontent.com/chavapalmarubin-lab/FIDUS/main/vps/mt5_bridge_api_service.py
if %ERRORLEVEL% EQU 0 (
    echo     SUCCESS
) else (
    echo     ERROR: Failed to download service file
    pause
    exit /b 1
)
echo.

REM Step 3: Create .env file with CORRECT cluster name
echo [3/8] Creating .env file with correct MongoDB credentials...
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

REM Step 4: Create requirements.txt
echo [4/8] Creating requirements.txt...
(
echo fastapi==0.115.0
echo uvicorn==0.30.6
echo pydantic==2.9.0
echo MetaTrader5==5.0.4508
echo pymongo==4.8.0
echo python-dotenv==1.0.1
echo cryptography==43.0.1
echo httpx==0.27.0
echo python-dateutil==2.8.2
) > requirements.txt
echo     SUCCESS
echo.

REM Step 5: Install Python dependencies
echo [5/8] Installing Python dependencies (this may take 2-3 minutes)...
C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe -m pip install --upgrade pip --quiet
C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe -m pip install -r requirements.txt --quiet
if %ERRORLEVEL% EQU 0 (
    echo     SUCCESS
) else (
    echo     WARNING: Some packages may have failed
)
echo.

REM Step 6: Create startup batch file
echo [6/8] Creating startup batch file...
(
echo @echo off
echo cd /d C:\mt5_bridge_service
echo SET PYTHON_PATH=C:\Users\Administrator\AppData\Local\Programs\Python\Python312
echo "%%PYTHON_PATH%%\python.exe" mt5_bridge_api_service.py ^>^> logs\service_output.log 2^>^>^ logs\service_error.log
echo exit /b %%ERRORLEVEL%%
) > start_mt5_bridge.bat
echo     SUCCESS
echo.

REM Step 7: Create scheduled task
echo [7/8] Creating scheduled task "MT5BridgeService"...
schtasks /Delete /TN "MT5BridgeService" /F >nul 2>&1
schtasks /Create /TN "MT5BridgeService" /SC ONSTART /TR "C:\mt5_bridge_service\start_mt5_bridge.bat" /RL HIGHEST /RU SYSTEM /F
if %ERRORLEVEL% EQU 0 (
    echo     SUCCESS
) else (
    echo     ERROR: Failed to create scheduled task
    pause
    exit /b 1
)
echo.

REM Step 8: Start the service
echo [8/8] Starting MT5 Bridge Service...
schtasks /Run /TN "MT5BridgeService"
echo     Service start command sent
echo     Waiting 25 seconds for initialization...
timeout /t 25 /nobreak >nul
echo.

REM Test the service
echo ========================================
echo Testing Service...
echo ========================================
echo.
curl -s http://localhost:8000/api/mt5/bridge/health
echo.
echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Check above for "mongodb":{"connected":true}
echo.
echo If MongoDB shows connected:false, check logs:
echo - C:\mt5_bridge_service\logs\service_error.log
echo - C:\mt5_bridge_service\logs\service_output.log
echo.
echo Test externally:
echo curl http://92.118.45.135:8000/api/mt5/bridge/health
echo.
pause
