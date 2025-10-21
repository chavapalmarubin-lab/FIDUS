@echo off
echo ========================================
echo MT5 Bridge Service - Log Viewer
echo ========================================
echo.

cd /d C:\mt5_bridge_service

echo [1] SERVICE ERROR LOG
echo ========================================
if exist logs\service_error.log (
    type logs\service_error.log
) else (
    echo No service_error.log found
)

echo.
echo.
echo [2] SERVICE OUTPUT LOG
echo ========================================
if exist logs\service_output.log (
    type logs\service_output.log
) else (
    echo No service_output.log found
)

echo.
echo.
echo [3] DIRECT PYTHON MONGODB TEST
echo ========================================
C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe -c "import sys; import traceback; from pymongo import MongoClient; import os; from dotenv import load_dotenv; load_dotenv(); uri=os.getenv('MONGODB_URI'); print(f'Connection String: {uri}'); print('Attempting connection...'); client=MongoClient(uri, serverSelectionTimeoutMS=10000); result=client.admin.command('ping'); print('SUCCESS: Connected!'); print(result)" 2>&1

echo.
echo.
echo [4] CHECKING PYTHON PACKAGES
echo ========================================
C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe -m pip list | findstr /I "pymongo fastapi uvicorn dotenv"

echo.
echo.
echo ========================================
echo End of Logs
echo ========================================
pause
