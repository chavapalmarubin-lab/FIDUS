@echo off
echo FIDUS MT5 Bridge Service - Windows VPS Setup
echo ============================================

REM Create service directory
mkdir C:\mt5_bridge_service
cd C:\mt5_bridge_service

REM Check Python installation
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not installed or not in PATH
    echo Please install Python 3.11+ from python.org
    pause
    exit /b 1
)

REM Install dependencies
echo Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt

REM Copy environment file
copy .env.template .env
echo.
echo IMPORTANT: Edit .env file with proper configuration:
echo - Generate secure API key
echo - Set ENVIRONMENT=prod
echo.

REM Create Windows service script
echo Creating service scripts...

REM Start service script
echo @echo off > start_service.bat
echo echo Starting FIDUS MT5 Bridge Service... >> start_service.bat
echo cd C:\mt5_bridge_service >> start_service.bat
echo python main_production.py >> start_service.bat
echo pause >> start_service.bat

REM Stop service script  
echo @echo off > stop_service.bat
echo echo Stopping FIDUS MT5 Bridge Service... >> stop_service.bat
echo taskkill /f /im python.exe >> stop_service.bat
echo echo Service stopped >> stop_service.bat
echo pause >> stop_service.bat

REM Install as Windows service (optional)
echo @echo off > install_service.bat
echo echo Installing as Windows service... >> install_service.bat
echo pip install pywin32 >> install_service.bat
echo echo Service installation requires admin privileges >> install_service.bat
echo pause >> install_service.bat

echo.
echo ============================================
echo Setup completed successfully!
echo.
echo Next steps:
echo 1. Edit .env file with your configuration
echo 2. Install MetaTrader 5 terminal
echo 3. Configure Windows Firewall (port 8000)
echo 4. Run start_service.bat to start the service
echo.
echo For help, see setup_instructions.md
echo ============================================
pause
