@echo off
echo ========================================
echo MongoDB Connection Diagnostics
echo ========================================
echo.

cd /d C:\mt5_bridge_service

echo [1] Checking .env file exists...
if exist .env (
    echo     YES - .env exists
    echo.
    echo [2] Showing .env content (hiding password):
    type .env | findstr /V "PASSWORD"
) else (
    echo     ERROR: .env file missing!
    pause
    exit /b 1
)

echo.
echo [3] Checking Python dependencies...
C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe -m pip list | findstr "pymongo"
C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe -m pip list | findstr "motor"
C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe -m pip list | findstr "fastapi"

echo.
echo [4] Testing MongoDB connection with Python...
C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe -c "from pymongo import MongoClient; import os; from dotenv import load_dotenv; load_dotenv(); uri=os.getenv('MONGODB_URI'); print(f'URI: {uri[:50]}...'); client=MongoClient(uri, serverSelectionTimeoutMS=5000); client.admin.command('ping'); print('SUCCESS: MongoDB connected!')"

echo.
echo [5] Checking service error logs...
if exist logs\service_error.log (
    echo Last 30 lines of error log:
    powershell -Command "Get-Content logs\service_error.log -Tail 30"
) else (
    echo No error log found
)

echo.
echo [6] Checking API service logs...
if exist logs\api_service.log (
    echo Last 30 lines of API log:
    powershell -Command "Get-Content logs\api_service.log -Tail 30"
) else (
    echo No API log found
)

echo.
echo ========================================
echo Diagnostics Complete
echo ========================================
pause
