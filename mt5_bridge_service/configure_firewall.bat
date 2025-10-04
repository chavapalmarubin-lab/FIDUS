@echo off
echo Configuring Windows Firewall for MT5 Bridge Service
echo ====================================================

REM Enable firewall rule for MT5 Bridge Service
netsh advfirewall firewall add rule name="FIDUS MT5 Bridge Service" dir=in action=allow protocol=TCP localport=8000

echo.
if %ERRORLEVEL% EQU 0 (
    echo ✅ Firewall rule added successfully
    echo Port 8000 is now open for incoming connections
) else (
    echo ❌ Failed to add firewall rule
    echo Please run as Administrator or configure manually:
    echo 1. Open Windows Defender Firewall
    echo 2. Click "Advanced settings"
    echo 3. Click "Inbound Rules" 
    echo 4. Click "New Rule..."
    echo 5. Select "Port" and click Next
    echo 6. Select "TCP" and enter "8000" 
    echo 7. Select "Allow the connection"
    echo 8. Apply to all profiles
    echo 9. Name: "FIDUS MT5 Bridge Service"
)

echo.
echo Testing port accessibility...
netstat -an | find ":8000"

echo.
echo ====================================================
echo Firewall configuration completed
echo ====================================================
pause
