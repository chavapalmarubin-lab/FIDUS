@echo off
echo ========================================
echo MT5 Bridge Service - Task Scheduler Setup
echo ========================================

REM Create the scheduled task
schtasks /Create /TN "MT5BridgeService" /SC ONSTART /TR "C:\mt5_bridge_service\start_mt5_bridge.bat" /RL HIGHEST /F /RU "trader" /RP "%1"

IF %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Task Scheduler configured
    echo Starting service...
    schtasks /Run /TN "MT5BridgeService"
    timeout /t 10 /nobreak
    echo Service started!
) ELSE (
    echo [ERROR] Failed to create scheduled task
    exit /b 1
)
