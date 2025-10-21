@echo off
echo ========================================
echo MongoDB Connection Diagnostic Test
echo ========================================
echo.

cd /d C:\mt5_bridge_service

echo [TEST 1] Checking .env file...
if exist .env (
    echo .env file exists
    echo.
    echo Content (passwords hidden):
    type .env | findstr /V "PASSWORD"
    echo.
) else (
    echo ERROR: .env file missing!
    pause
    exit /b 1
)

echo.
echo [TEST 2] Direct Python MongoDB Connection Test...
echo.
C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe -c "import sys; from pymongo import MongoClient; import os; from dotenv import load_dotenv; load_dotenv(); uri=os.getenv('MONGODB_URI'); print('Testing MongoDB connection...'); print(f'URI: {uri[:60]}...'); client=MongoClient(uri, serverSelectionTimeoutMS=10000); result=client.admin.command('ping'); print('\nSUCCESS: MongoDB Connected!'); print(f'Result: {result}'); db=client.get_database(); collections=db.list_collection_names(); print(f'\nCollections found: {len(collections)}'); print(f'Sample collections: {collections[:5]}'); sys.exit(0)" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Python MongoDB connection failed!
    echo This indicates a problem with credentials, network, or Python packages.
    echo.
)

echo.
echo [TEST 3] Checking service error logs...
if exist logs\service_error.log (
    echo Last 50 lines of service_error.log:
    echo ----------------------------------------
    powershell -Command "Get-Content logs\service_error.log -Tail 50 | Out-String"
    echo ----------------------------------------
) else (
    echo No service_error.log found
)

echo.
echo [TEST 4] Checking API service logs...
if exist logs\api_service.log (
    echo Last 50 lines of api_service.log:
    echo ----------------------------------------
    powershell -Command "Get-Content logs\api_service.log -Tail 50 | Out-String"
    echo ----------------------------------------
) else (
    echo No api_service.log found
)

echo.
echo [TEST 5] Testing health endpoint...
curl -s http://localhost:8000/api/mt5/bridge/health
echo.

echo.
echo [TEST 6] Checking Python packages...
C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe -m pip list | findstr /I "pymongo fastapi uvicorn dotenv"

echo.
echo ========================================
echo Diagnostic Complete
echo ========================================
echo.
echo If TEST 2 shows "SUCCESS", but TEST 5 shows connected:false,
echo then the service is not loading the .env file correctly.
echo.
echo If TEST 2 fails, check the error message for details.
echo ========================================
pause
