@echo off
cd /d C:\mt5_bridge_service
SET PYTHON_PATH=C:\Users\Administrator\AppData\Local\Programs\Python\Python312
"%PYTHON_PATH%\python.exe" mt5_bridge_api_service.py >> logs\service_output.log 2>> logs\service_error.log
exit /b %ERRORLEVEL%
